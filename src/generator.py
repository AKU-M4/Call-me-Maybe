import json
from src.decoder import JsonConstrainedDecoding
from llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition, FunctionCall

MAX_NEW_TOKENS = 200


def generated_function_call(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model,
    decoder: JsonConstrainedDecoding,
    ) -> FunctionCall:
    
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """

def _select_function(
    user_prompt: str,
    functions: list[FunctionDefinition],
    model: Small_LLM_Model
    ) -> FunctionDefintion:
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

    
