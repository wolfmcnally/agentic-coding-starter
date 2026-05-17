# Example

A minimal Python package and CLI that exists so build gates have a real target from the first session. Replace or extend as the project takes shape.

## Quickstart

```bash
uv sync
uv run example --help
uv run example hello
uv run example hello Ada
```

## Build gates

```bash
uv run ruff check example tests
uv run ruff format --check example tests
uv run pytest -q
```
