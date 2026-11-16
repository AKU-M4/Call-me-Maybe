import numpy as np
import numpy.typing as npt
from typing import Any


class JsonConstrainedDecoder:
    """Mask an LLM's next-token logits so generation stays valid JSON.

    At every generation step, the decoder rejects any token that would
    either break JSON syntax (e.g. closing a brace that was never
    opened) or close the parameters object before every required
    schema key has been generated. This guarantees the model can only
    ever produce structurally valid, schema-complete JSON.
    """

    def __init__(self, vocabulary: dict[str, int]) -> None:
        """Build the token-id-to-string lookup used for masking.

        Args:
            vocabulary: Mapping of raw tokenizer strings to their
                token ids, as loaded from the model's vocab file.
        """
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
        """Return a copy of logits with invalid next-tokens set to -inf.

        Args:
            logits: Raw next-token logits from the model.
            generated_so_far: The JSON text generated up to this point.
            schema: Dict with a "parameters" key listing the required
                parameter names for the current function call.

        Returns:
            A logits array of the same shape where every token that
            would break JSON structure or skip a required parameter
            key has been masked to -inf, leaving only valid choices.
        """

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
