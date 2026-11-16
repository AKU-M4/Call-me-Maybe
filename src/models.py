from typing import Any
from pydantic import BaseModel


class FunctionReturn(BaseModel):
    """Return-type declaration for a callable function."""

    type: str


class FunctionParameter(BaseModel):
    """Type declaration for a single function parameter."""

    type: str


class FunctionDefinition(BaseModel):
    """Full schema for a function the model may call.

    Attributes:
        name: The function's identifier, as used in generated calls.
        description: Human-readable summary of what the function does.
        parameters: Mapping of parameter name to its type declaration.
        returns: The function's return type declaration.
    """

    name: str
    description: str
    parameters: dict[str, FunctionParameter]
    returns: FunctionReturn


class Prompt(BaseModel):
    """A single natural-language request to translate into a call."""

    prompt: str


class FunctionCall(BaseModel):
    """A generated function call, ready to be executed or graded.

    Attributes:
        prompt: The original natural-language request.
        name: The name of the function chosen by the model.
        parameters: The generated argument values, keyed by name.
    """

    prompt: str
    name: str
    parameters: dict[str, Any]
