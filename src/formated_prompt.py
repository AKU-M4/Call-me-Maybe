from src.models import FunctionDefinition


def build_prompt(user_prompt: str, functions: list[FunctionDefinition]) -> str:
    fn_descriptions_list = []

    for fn in functions:
        parameters = ", ".join(
            f'"{k}": {v.type}' for k, v in fn.parameters.items()
        )
        schema_str = f'{{"name": "{fn.name}", "parameters": {{{parameters}}}}}'
        fn_descriptions_list.append(
            f"- {fn.name}: {fn.description}\n (Expected Schema: {schema_str})"
        )

    fn_descriptions = "\n".join(fn_descriptions_list)

    return (
        "You are a strict JSON function calling AI.\n"
        f"Available functions:\n{fn_descriptions}\n\n"
        f"User request: {user_prompt}\n\n"
        "Note: When asked to replace elements with a symbol (even if "
        "pluralized, like 'asterisks'), always use a single symbol "
        "character (e.g., '*') as the replacement string.\n"
        "Note: If a parameter value contains double quotes, you must escape "
        "them with a backslash (e.g., \\\"word\\\").\n\n"
        "Respond with a complete JSON object matching the exact schema.\n"
    )
