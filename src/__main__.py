from loader import load_function_definition
from pathlib import Path

# 1. Get the absolute path of the directory containing __main__.py (the 'src' folder)
CURRENT_DIR = Path(__file__).resolve().parent

# 2. Go up one level to the project root, then down into data/input/
PROJECT_ROOT = CURRENT_DIR.parent
DEFAULT_FUNCTIONS = PROJECT_ROOT / "data" / "input" / "functions_definition.json"

def main():
    loaded_json = load_function_definition(DEFAULT_FUNCTIONS)
    print(loaded_json)

if __name__ == "__main__":
    main()