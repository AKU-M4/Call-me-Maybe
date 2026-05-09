PYTHON = uv run python
FLAKE8 = uv run flake8
MYPY = uv run mypy
SRC_DIR = src

install:
	uv sync

run: 
	$(PYTHON) -m $(SRC_DIR)

debug: 
	$(PYTHON) -m pdb -m $(SRC_DIR)
 
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cahce

lint:
	$(FLAKE8) $(SRC_DIR)
	$(MYPY) --warn-return-any --warn-unused-ignores \\
	--ignore-missing-imports --disallow-untyped-defs \\
	--check-untyped-defs $(SRC_DIR)

lint-strict:
	$(FLAKE8) $(SRC)
	$(MYPY) -strict $(SRC_DIR)

PHONY: install, lint-strict, lint, clean, debug, run, install