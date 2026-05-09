import json
from typing import Any
from pathlib import Path
from src.models import FunctionCall


def write_results(result: list[FunctionCall], path: Path) -> None:
    """ Function that dumps the result into the output json file

    Keyword arguments:
    arguments: result = list of general function calls
               path: Output file
    Return: None
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump([r.model_dump() for r in result], f, indent=2)
