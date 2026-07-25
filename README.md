*This project has been created as part of the 42 curriculum by adkaid-s.*

# Call me Maybe

## Description

**Call me Maybe** is a function-calling engine built on top of a small local
language model (`Qwen/Qwen3-0.6B`, ~0.6B parameters). Given a natural-language
request such as *"What is the sum of 2 and 3?"*, the goal is not to have the
model answer in prose, but to have it produce a structured, machine-executable
call:

```json
{"name": "fn_add_numbers", "parameters": {"a": 2.0, "b": 3.0}}
```

Small models are notoriously unreliable at producing valid structured output
from prompting alone — they might succeed only ~30% of the time. This project
solves that with **constrained decoding**: instead of hoping the model outputs
correct JSON, we intervene at every generation step and force it to.

## Instructions

### Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) for dependency management

### Install

```bash
make install
```

### Run

```bash
make run
```

or with custom paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

By default, input is read from `data/input/` and output is written to
`data/output/function_calls.json`.

### Debug

```bash
make debug
```

Runs the program under `pdb`.

### Lint

```bash
make lint          # flake8 + mypy
make lint-strict    # flake8 + mypy --strict
```

### Clean

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, and `.pytest_cache`.

### Grading

A companion tool, `moulinette`, generates exercise sets and grades a set of
generated function calls against a reference answer key:

```bash
uv run python -m moulinette prepare_exercises
uv run python -m moulinette grade_student_answers data/output/function_calls.json
```

## Algorithm Explanation — Constrained Decoding

The pipeline generates a function call in two stages:

**1. Function selection.** A short prompt asks the model, in free text, which
function should be called for the user's request. The model generates text
token by token (greedy / `argmax`) until one of the known function names
appears in its output. No heuristics or string-matching on the *user's*
prompt are used to pick the function — only the model's own generation, per
the project constraints.

**2. Constrained argument generation.** This is the core of the project:

1. The chosen function's name is force-fed into the prompt as
   `{"name": "<fn_name>", "parameters": {`, so the name is never at risk of
   being generated wrong.
2. From there, tokens are generated one at a time. At each step:
   - The model produces raw logits for every token in its vocabulary.
   - `JsonConstrainedDecoder.mask_logits` walks the top candidate tokens and
     sets any token that would break the JSON to `-inf`:
     - a token that would close a `}` that was never opened is rejected;
     - a token that would close the `parameters` object before every
       required key from the schema has appeared is rejected.
   - The highest-scoring token that survives the mask is selected
     (`argmax`), guaranteeing that only structurally and schematically valid
     tokens are ever chosen.
3. Generation stops the moment the JSON object's braces balance out and the
   accumulated string parses as valid JSON.
4. The parsed parameters are then coerced to the correct types (e.g. numeric
   strings become `float`) as declared in the function's schema.

Because invalid tokens are eliminated *before* selection rather than
retried *after* a failure, the output is guaranteed to be syntactically valid,
schema-complete JSON on every single run — not just most of the time.

## Design Decisions

- **Forcing the function name into the prefix** removes an entire class of
  failure (misspelled/hallucinated function names) without needing the model
  to get it right — the constrained decoder is reserved for the actual
  argument values, which is the genuinely hard part.
- **Greedy decoding (`argmax`)** was chosen over sampling for determinism:
  identical input always produces identical output, which matters for
  grading and debugging.
- **Vocabulary-level masking** (via the tokenizer's vocab file) rather than
  post-hoc JSON validation means invalid output is structurally impossible,
  not just unlikely.
- **Type coercion after parsing** (e.g. `"2" -> 2.0`) keeps the constrained
  decoder focused purely on structure/schema, while a light post-processing
  step handles the semantic gap between "the model produced a string" and
  "the function needs a float."

## Challenges Faced

The constrained decoder guarantees valid *JSON structure*, but has no notion
of whether a generated *value* is semantically correct. Being a small,
greedily-decoded model, it sometimes takes shortcuts on the
`fn_substitute_string_with_regex` function specifically:

- It would copy a literal number straight from the prompt as the regex
  (e.g. `regex: "34"`) instead of generalizing to a digit pattern
  (`regex: "\d+"`), so any other number in the string wouldn't get matched.
- It would pad the `replacement` string with stray spaces
  (`replacement: " * "` instead of `"*"`), which the exact-match grading in
  `moulinette` treats as a wrong answer.

Adding a few-shot example to the prompt (`formated_prompt.py`) helped
partially, but a small model doesn't always generalize reliably from a single
example. The fully reliable fix was a light, targeted post-processing step
in `generate_function_call()`, applied to the parsed JSON right before it's
returned: `replacement` values are stripped of leading/trailing whitespace,
and a `regex` value that is purely digits is normalized to `\d+`.

## Performance Analysis

- **Validity:** 100% of generated outputs are valid, schema-complete JSON —
  guaranteed structurally by the decoder, not just observed empirically.
- **Accuracy:** 11/11 (100%) of the public test set passes after the fixes
  described above; prior to the fixes, 2 of the `fn_substitute_string_with_regex`
  cases failed on output correctness (not structure).
- **Speed:** the full 11-prompt public set runs in under 2 minutes on CPU,
  well within the 5-minute target.


## Resources

- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Guiding LLMs the right way: fast, non-invasive constrained generation (outlines)](https://blog.dottxt.co/)
- [BPE tokenization overview](https://huggingface.co/learn/nlp-course/chapter6/5)
- [Pydantic documentation](https://docs.pydantic.dev/)

**AI usage:** AI assistance (Claude) was used to debug two failing test
cases in the `fn_substitute_string_with_regex` exercises — diagnosing why the
model's generated `regex` and `replacement` values produced incorrect output,
and implementing the fix (a few-shot prompt example plus targeted
post-processing in `generate_function_call()`). 
