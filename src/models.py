from typing import Any
from pydantic import BaseModel, Field

class FunctionReturn(BaseModel):
    type: str


class FunctionParameter(BaseModel):
    type: str


class FunctionDefintion(BaseModel):
    name: str
    description: str
    parameters: dict[str, FunctionParameter]
    returns: FunctionReturn


class Prompt(BaseModel):
    prompt: str


class FunctionCall(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, Any]
