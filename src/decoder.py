import numpy as np
import numpy.typing as npt
from typing import Any


class JsonConstrainedDecoder:
    def __init__(self, vocabulary: dict[str, int]) -> None:
        # Clean tokenizer artifacts to prevent parsing errors
        self.id_to_token: dict[int, str] = {
            v: k.replace("Ġ", " ").replace("Ċ", "\n")
            for k, v in vocabulary.items()
        }

    def mask_logits(
        self,
        logits: npt.NDArray[np.float64],
        generated_so_far: str,
        schema: dict[str, Any]
    ) -> npt.NDArray[np.float64]:

        masked = np.full_like(logits, -np.inf)
        sorted_indices = np.argsort(logits)[::-1]

        # Track our JSON state
        depth = generated_so_far.count('{') - generated_so_far.count('}')

        for token_id in sorted_indices[:150]:
            token_str = self.id_to_token.get(token_id, "")

            # Rule 2: Prevent syntax errors (never close a brace if not open)
            new_open = token_str.count('{')
            new_close = token_str.count('}')
            if depth + new_open - new_close < 0:
                continue

            # Rule 3: Schema Enforcement Gatekeeper
            # If the model tries to close the dictionary, check if keys exist
            if '}' in token_str and depth == 2:
                candidate = generated_so_far + token_str
                missing_key = False

                if '"parameters"' in candidate:
                        params_part = candidate.split('"parameters"')[-1]
                        for req_key in schema.get("parameters", {}).keys():
                            if f'"{req_key}"' not in params_part:
                                missing_key = True
                                break
                else:
                    missing_key = True
                # Reject the closing bracket if parameters are missing,
                # forcing it to generate the key
                if missing_key:
                    continue

            masked[token_id] = logits[token_id]

        # Failsafe: if the model backs itself into a corner, pick the safest
        # token to avoid crashing
        if np.max(masked) == -np.inf:
            masked[sorted_indices[0]] = logits[sorted_indices[0]]
        return masked
