import json
from src.models import FunctionDefinition


def build_prompt(user_prompt: str, functions: list[FunctionDefinition]) -> str:
    """Building prompt

    Keyword arguments:
    argument -- user_prompt: the natural language request
    argument -- functions: list of all the function defintions

    Return: returns well formated prompt ready for tokenization 
    """

    fn_descriptions: str = ""
    for fn in functions:
        parameters = ""
        for k, v in functions.parameters.items():
            parameters = f"{k}: {v.type}"

        fn_descriptions = "\n".join(f"{fn.name}: {fn.desctiption}"
                                    f"(parameters: {parameters}")
    return (
        f"You are a function calling assistant.\n"
        f"Available functions:\n{fn_descriptions}\n\n"
        f"User request: {user_prompt}\n\n"
        f"Respond with a JSON object with keys 'name' and 'parameters':\n"
    )
