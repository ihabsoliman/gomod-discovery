# Makefile for building, testing, formatting, and linting the project

.PHONY: all dev test format lint

all: test format lint

sync:
	npm install
	uv sync
	uv pip install --upgrade pip black flake8 pytest

dev:
	npx wrangler dev

test:
	pytest

format:
	black .

lint:
	black . --check
