# src/__main__.py

import sys
import argparse
from pathlib import Path
from llm_sdk import Small_LLM_Model
from src.loader import load_function_definitions, load_prompts
from src.generator import generate_function_call
from src.decoder import JsonConstrainedDecoder
from src.writer import write_results


DEFAULT_FUNCTIONS = Path("data/input/functions_definition.json")
DEFAULT_INPUT = Path("data/input/function_calling_tests.json")
DEFAULT_OUTPUT = Path("data/output/function_calls.json")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="LLM function calling tool")
    parser.add_argument("--functions_definition", type=Path, default=DEFAULT_FUNCTIONS)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    """Main entry point for the function calling pipeline."""
    args = parse_args()

    try:
        functions = load_function_definitions(args.functions_definition)
        prompts = load_prompts(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Load model and vocabulary once
    model = Small_LLM_Model()
    vocab_path = model.get_path_to_vocab_file()

    import json
    with open(vocab_path) as f:
        vocabulary = json.load(f)

    decoder = JsonConstrainedDecoder(vocabulary)
    results = []

    for i, prompt in enumerate(prompts):
        print(f"[{i+1}/{len(prompts)}] Processing: {prompt.prompt}")
        try:
            result = generate_function_call(
                prompt.prompt, functions, model, decoder
            )
            results.append(result)
            print(f"  → {result.name}({result.parameters})")
        except Exception as e:
            print(f"  [ERROR] {e}", file=sys.stderr)

    write_results(results, args.output)
    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()