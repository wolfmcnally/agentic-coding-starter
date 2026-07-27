# Example

A minimal Python package and CLI that exists so build gates have a real target from the first session. Replace or extend as the project takes shape.

## Quickstart

```bash
uv sync --locked --managed-python
uv run --locked --managed-python example --help
uv run --locked --managed-python example hello
uv run --locked --managed-python example hello Ada
```

## Build gates

```bash
uv run --locked --managed-python ruff check example tests
uv run --locked --managed-python ruff format --check example tests
uv run --locked --managed-python python -m pytest -q
```
