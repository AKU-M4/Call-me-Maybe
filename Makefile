venv:
	python3 -m venv venv

activate:
	source venv/bin/activate

all: venv

lint-strict:
	flake8 . && mypy . --strict