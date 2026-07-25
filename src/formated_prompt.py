from src.models import FunctionDefinition


def build_prompt(user_prompt: str, functions: list[FunctionDefinition]) -> str:
    fn_descriptions_list = []

    for fn in functions:
        params = ", ".join(
            f"{k}: {v.type}" for k, v in fn.parameters.items()
        )
        fn_descriptions_list.append(
            f"- {fn.name}({params}): {fn.description}"
        )

    fn_descriptions = "\n".join(fn_descriptions_list)

    return (
        "You are an AI assistant that calls functions.\n"
        f"Available functions:\n{fn_descriptions}\n\n"
        f"User request: {user_prompt}\n\n"
        "Generate a valid JSON tool call matching the required parameters.\n"
    )
