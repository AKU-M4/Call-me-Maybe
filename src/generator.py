import json
import numpy as np
from src.formated_prompt import build_prompt
from src.decoder import JsonConstrainedDecoder
from llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition, FunctionCall

MAX_NEW_TOKENS = 200


def generate_function_call(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model,
    decoder: JsonConstrainedDecoder,
    ) -> FunctionCall:
    
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    chosen_fn = _select_function(user_prompt, functions, model)

    schema = {
        "name": chosen_fn.name,
        "parameters": {k: v.type for k, v in chosen_fn.parameters.items()}
    }

    prompt_to_feed = build_prompt(user_prompt, functions)
    input_ids = model.encode(prompt_to_feed)

    generated_ids: list[int] = []
    generated_str = ""

    for _ in range(MAX_NEW_TOKENS):
        import torch
        tensor = torch.tensor([input_ids + generated_ids])
        logits = model.get_logits_from_input_ids(tensor)[0, -1].np()

        masked = decoder.mask_logits(logits, generated_str, schema)
        next_id = int(np.argmax(masked))
        next_token = decoder.id_to_token[next_id]

        generated_ids.append(next_id)
        generated_str += next_token

        try:
            parsed = json.loads(genetaed_str)
            return FunctionCall(
                prompt=user_prompt,
                name=parsed["name"],
                parameters=parsed["parameters"] 
            )
        except json.JSONDecodeError:
            continue
    raise ValueError(f"Failed to generated valid JSON for prompt: {user_prompt}!")

def _select_function(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model
    ) -> FunctionDefinition:
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    fn_list = "\n".join(f"{fn.name}: {fn.description}" for fn in functions)
    prompt = (
        f"Given this request: {user_prompt}"
        f"Which function should be called?\n {fn_list}"
        f"Answer with only the function name:"
    )
    
    input_ids = model.encode(prompt)
    import torch
    generated = ""

    for _ in range(50):
        tensor = torch.tensor([input_ids]).tolist[0]
        logits = model.get_logits_from_input_ids(tensor)[0, -1].np()
        next_id = int(np.argmax(logits))
        token = model.decode([next_id])
        generated += token
        input_ids = input_ids + [next_id]

        for fn in functions:
            if fn.name in generated:
                return fn
        
    return functions[0]
