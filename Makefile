.PHONY: install test lint run

install:
	uv sync --all-extras

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run mypy src/pokemon_battle_engine/domain

run:
	uv run uvicorn pokemon_battle_engine.main:app --reload