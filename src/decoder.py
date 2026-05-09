import numpy as np
from typing import Any


class JsonConstrainedDecoder:
    def __init__(self, vocabulary: dict[str, int]) -> None:
        # Clean tokenizer artifacts to prevent parsing errors
        self.id_to_token: dict[int, str] = {
            v: k.replace("Ġ", " ").replace("Ċ", "\n") for k, v in vocabulary.items()
        }

    def mask_logits(
            self,
            logits: np.ndarray,
            generated_so_far: str,
            schema: dict[str, Any]) -> np.ndarray:

        masked = np.full_like(logits, -np.inf)
        sorted_indices = np.argsort(logits)[::-1]

        # Track our JSON state
        depth = generated_so_far.count('{') - generated_so_far.count('}')

        # Strict whitelist: Only allow characters that belong in a JSON payload
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFG'
                            'HIJKLMNOPQRSTUVWXYZ0123456789_:,."{} \n-+[]')

        for token_id in sorted_indices[:150]:
            token_str = self.id_to_token.get(token_id, "")

            # Rule 1: No invalid characters (prevents the model from writing random text)
            if not all(c in allowed_chars for c in token_str):
                continue

            # Rule 2: Prevent syntax errors (never close a brace that isn't open)
            new_open = token_str.count('{')
            new_close = token_str.count('}')
            if depth + new_open - new_close < 0:
                continue

            # Rule 3: Schema Enforcement Gatekeeper
            # If the model tries to close the parameters dictionary, check if all keys exist!
            if '}' in token_str and depth == 2:
                candidate = generated_so_far + token_str
                missing_key = False

                for req_key in schema.get("parameters", {}).keys():
                    if f'"{req_key}"' not in candidate:
                        missing_key = True
                        break

                # Reject the closing bracket if parameters are missing, forcing it to generate the key
                if missing_key:
                    continue

            masked[token_id] = logits[token_id]

        # Failsafe: if the model backs itself into a corner, pick the safest token to avoid crashing
        if np.max(masked) == -np.inf:
            masked[sorted_indices[0]] = logits[sorted_indices[0]]

        return masked
