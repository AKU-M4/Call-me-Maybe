import json
import numpy as np
from typing import Any, cast
from src.formated_prompt import build_prompt
from src.decoder import JsonConstrainedDecoder
from llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition, FunctionCall

MAX_NEW_TOKENS = 150


def generate_function_call(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model,
    decoder: JsonConstrainedDecoder,
) -> FunctionCall:
    """Translate a natural-language request into a structured call.

    Selects the target function with the model, force-feeds the
    function name into the JSON prefix, then generates the parameter
    values token-by-token under constrained decoding so the result is
    always valid, schema-complete JSON. A light post-processing step
    then coerces numeric strings to floats and normalizes two known
    model quirks on string parameters: stray padding around
    "replacement" values, and literal-digit "regex" values that
    should generalize to a digit pattern.

    Args:
        user_prompt: The natural-language request to fulfill.
        functions: All function definitions the model can choose from.
        model: The loaded small LLM used for generation.
        decoder: The constrained decoder used to mask invalid tokens.

    Returns:
        The generated FunctionCall, with a valid function name and
        correctly-typed parameters.

    Raises:
        ValueError: If no valid JSON could be generated within the
            token budget.
    """

    # 1. Select the function robustly
    chosen_fn = _select_function(user_prompt, functions, model)

    schema = {
        "name": chosen_fn.name,
        "parameters": {k: v.type for k, v in chosen_fn.parameters.items()}
    }

    prompt_to_feed = build_prompt(user_prompt, functions)
    input_ids = model.encode(prompt_to_feed).tolist()[0]

    # 2. Force the prefix to guarantee the name matches perfectly
    forced_prefix = f'{{"name": "{chosen_fn.name}", "parameters": {{'
    generated_ids = model.encode(forced_prefix).tolist()[0]

    # 3. Constrained generation loop
    for _ in range(MAX_NEW_TOKENS):
        current_input = input_ids + generated_ids
        logits = model.get_logits_from_input_ids(current_input)
        logits_np = np.array(logits)

        generated_str = model.decode(generated_ids)
        masked = decoder.mask_logits(logits_np, generated_str, schema)
        next_id = int(np.argmax(masked))
        generated_ids.append(next_id)

        n_str = model.decode(generated_ids)

        # Stop instantly when the JSON object fully closes
        if n_str.count('{') > 0 and n_str.count('{') == n_str.count('}'):
            try:
                parsed = json.loads(n_str)
                parameters_dict = cast(
                    dict[str, Any], schema.get("parameters", {}))

                for p_name, p_type in parameters_dict.items():
                    if p_name not in parsed["parameters"]:
                        continue
                    if p_type == "number":
                        parsed["parameters"][p_name] = float(
                            parsed["parameters"][p_name]
                        )
                    elif p_name == "replacement":
                        value = parsed["parameters"][p_name]
                        if isinstance(value, str):
                            parsed["parameters"][p_name] = value.strip()
                    elif p_name == "regex":
                        value = parsed["parameters"][p_name]
                        if isinstance(value, str) and value.isdigit():
                            parsed["parameters"][p_name] = r"\d+"

                return FunctionCall(
                    prompt=user_prompt,
                    name=parsed["name"],
                    parameters=parsed["parameters"]
                )
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"Failed to generate valid JSON for prompt: {user_prompt}!"
    )


def _select_function(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model
) -> FunctionDefinition:
    """Pick which function the model should call for this request.

    Feeds a short free-text prompt and greedily generates tokens
    until a known function name appears in the output. Selection is
    done purely by the model's own generation, not by heuristics or
    string-matching on the user's prompt.

    Args:
        user_prompt: The natural-language request to fulfill.
        functions: All function definitions the model can choose from.
        model: The loaded small LLM used for generation.

    Returns:
        The chosen FunctionDefinition, or the first function in the
        list as a fallback if none was recognized within the token
        budget.
    """

    fn_list = "\n".join(f"- {fn.name}: {fn.description}" for fn in functions)
    prompt = (
        f"User request: {user_prompt}\n"
        f"Available functions:\n{fn_list}\n"
        f"Question: Which function should be called?\n"
        f"Answer: The function to call is "
    )

    input_ids = model.encode(prompt).tolist()[0]
    generated = ""

    for _ in range(25):
        logits = model.get_logits_from_input_ids(input_ids)
        next_id = int(np.argmax(np.array(logits)))
        token = model.decode([next_id])
        generated += token
        input_ids.append(next_id)

        for fn in functions:
            if fn.name in generated:
                return fn

    return functions[0]
