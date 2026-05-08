import json
import numpy as np
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
        
        new_generated_str = model.decode(generated_ids)
        
        # Stop instantly when the JSON object fully closes
        if new_generated_str.count('{') > 0 and new_generated_str.count('{') == new_generated_str.count('}'):
            try:
                parsed = json.loads(new_generated_str)
                return FunctionCall(
                    prompt=user_prompt,
                    name=parsed["name"],
                    parameters=parsed["parameters"] 
                )
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Failed to generate valid JSON for prompt: {user_prompt}!")


def _select_function(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model
    ) -> FunctionDefinition:
    
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
