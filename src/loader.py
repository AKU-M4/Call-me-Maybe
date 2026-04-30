import json
from pathlib import Path
from pydantic import ValidationError, model_validate
from .models import Prompt, FunctionDefintion

def load_function_definition(path: Path) -> list[FunctionDefinition]:
    if not path.exists():
        raise FileNotFoundError(f"Function definition not found {path}")
    try:
        with open(path) as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid Json in {path}: {e}!")
    try:
        return [FunctionDefiniton.model_validate(item) for item in json_data]
    except ValidationError as e:
        raise ValidationError(f"Schema error in {path}: {e}")
    
