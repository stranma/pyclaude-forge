# CLAUDE.md

## Development Commands

- Install dependencies: `uv sync --group dev`
- Install package (editable): `pip install -e .`
- Run tests: `python -m pytest -v`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII
- Use types everywhere possible
- Do not add comments that state the obvious
