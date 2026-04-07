# CLAUDE.md

## Development Process

Use `/sync` before starting work, `/design` to formalize a plan, `/done` when finished, and `/landed` after the PR merges. Before creating any plan, read `docs/DEVELOPMENT_PROCESS.md` first.

## Development Commands

- Install dependencies: `uv sync --group dev`
- Run tests: `uv run pytest -v`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII
- Use types everywhere possible
- Do not add comments that state the obvious
