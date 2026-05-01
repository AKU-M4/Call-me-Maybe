import json
import numpy as np
from typing import Any


class JsonConstrainedDecoding:
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
        self.vocab_size: int = len(vocab)

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
        for token_id, token_str in self.id_to_toekn.items():
            candidate = generated_so_far + token_str
            if self._is_valid_prefix(candidate, schema):
                valid_ids.append(token_id)
        return valid_ids

    def mask_logits(
        self,
        logits: np.ndarray,
        generated_so_far: str,
        schema: dict[str, Any]) -> np.ndarray:
        