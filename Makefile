venv:
	python3 -m venv venv

activate:
	uv venv

all: venv activate

lint-strict:
	flake8 . && mypy . --strict