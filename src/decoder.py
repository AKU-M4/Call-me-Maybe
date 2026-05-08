import json
import numpy as np
from typing import Any


class JsonConstrainedDecoder:
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    def __init__(self, vocabulary: dict[str, int]) -> None:
        """Initialize the decoder with model vocabulary 
        """
        self.id_to_token: dict[int, str] = {
            v: k for k, v in vocabulary.items()}
        self.token_to_id: dict[str, int] = vocabulary
        self.vocab_size: int = len(vocabulary)

    def get_valid_token_ids(
            self,
            generated_so_far: str,
            schema: dict[str: int]) -> list[int]:
        """sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        valid_ids = []
        for token_id, token_str in self.id_to_token.items():
            candidate = generated_so_far + token_str
            if self._is_valid_prefix(candidate, schema):
                valid_ids.append(token_id)
        return valid_ids

    def mask_logits(
            self,
            logits: np.ndarray,
            generated_so_far: str,
            schema: dict[str, Any]) -> np.ndarray:
        """"sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        masked = np.full_like(logits, -np.inf)
        valid_ids = self.get_valid_token_ids(generated_so_far, schema)
        for token_id in valid_ids:
            masked[token_id] = logits[token_id]
        return masked

    def _is_valid_prefix(self, text: str, schema: dict[str, Any]) -> bool:
        """sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        try:
            parsed = json.loads(text)
            return self._matches_schema(parsed, schema)
        except json.JSONDecodeError:
            pass

        return self._is_json_prefix(text)

    def _is_json_prefix(self, text: str) -> bool:
        """sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        stripped = text.strip()

        if not stripped:
            return True
        if not stripped.startswith("{"):
            return False

        depth = 0
        in_string = False
        escape = False

        for c in stripped:
            if escape:
                escape = False
                continue
            if c == "\\" and in_string:
                escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
            if depth < 0:
                return False
        return True

    def _matches_schema(self, parsed: dict[str, Any], schema: dict[str, Any]
                        ) -> bool:
        """"sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        if "name" not in parsed or "parameters" not in parsed:
            return False
        if parsed["name"] != schema.get("name"):
            return False
        expected_params = schema.get("parameters", {})
        for key, expected_type in expected_params.items():
            if key not in parsed["parameters"]:
                return False
            val = parsed["parameters"][key]
            if not self.check_type(val, expected_type):
                return False
        return True

    def check_type(self, value: Any, expected_type: str) -> bool:
        """sumary_line

        Keyword arguments:
        argument -- description
        Return: return_description
        """
        type_map: dict[str, type] = {
            "number": (int, float),
            "string": str,
            "boolean": bool,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        return isinstance(value, expected)
