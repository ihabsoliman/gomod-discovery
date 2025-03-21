.PHONY: all sync dev test format lint

all: test format lint

sync:
	npm install
	uv sync
	uv pip install --upgrade pip black flake8 pytest

dev:
	npx wrangler dev

dev-ssl:
	npx wrangler dev --local-protocol https --port 8443 --minify

test:
	PYTHONPATH=src pytest tests

format:
	black .

lint:
	black . --check
