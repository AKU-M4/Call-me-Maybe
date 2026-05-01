PHONY: install, lint-strict, lint, 

all: venv activate

venv:
	python3 -m venv venv

activate:
	uv venv

install: $(all)
	cd llm_sdk && uv tree


lint-strict:
	flake8 . && mypy . --strict