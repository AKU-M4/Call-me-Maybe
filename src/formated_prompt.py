from src.models import FunctionDefinition


def build_prompt(user_prompt: str, functions: list[FunctionDefinition]) -> str:
    """Build the free-text prompt fed to the model for argument generation.

    Lists every available function with its parameters and description,
    then appends the user's request. The model's completion is later
    constrained token-by-token, so this prompt only needs to give the
    model enough context to guess reasonable values, not to guarantee
    a valid response on its own.

    Args:
        user_prompt: The natural-language request to fulfill.
        functions: All function definitions the model can choose from.

    Returns:
        The full prompt string to feed to the model.
    """
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
