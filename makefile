.PHONY: all test lint format isort black docker-build docker-run clean

all: format lint test

run:
	python src/main.py
test:
	python -m pytest --disable-warnings

lint:
	pylint src

black:
	black src --config pyproject.toml

isort:
	isort src

format: isort black

docker-build:
	docker build -t user_service .

docker-run: docker-build
	docker run --env-file .env --rm -it -p 8000:8000 user_service

docker-run-detached: docker-build
	docker run --env-file .env --rm -d -p 8000:8000 user_service

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache

