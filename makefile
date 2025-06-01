all: format lint test

test:
	python -m pytest --disable-warnings

lint:
	pylint src

black:
	black src --config pyproject.toml

isort:
	isort src

format: isort black

clean:
	rm -rf __pycache__ .pytest_cache

.PHONY: test lint format isort black all clean