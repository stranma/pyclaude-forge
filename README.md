# claude-code-harness

Portable Claude Code workflow for Python projects. Drop this into any Python repo to get structured development skills, automated agents, and review rules.

## What's Included

### Skills (slash commands)
| Skill | Purpose |
|-------|---------|
| `/sync` | Pre-flight workspace sync -- fetches remote, reports branch state, dirty files |
| `/design` | Crystallize brainstorming into a structured plan with Q/S/P scope classification |
| `/done` | Universal completion -- validates, ships/lands/delivers, updates docs |
| `/landed` | Post-merge lifecycle -- verifies CI, cleans branches, identifies next phase |

### Agents
| Agent | Purpose |
|-------|---------|
| `code-quality-validator` | Runs ruff + pyright, auto-fixes what it can |
| `test-coverage-validator` | Runs pytest, checks coverage |
| `code-reviewer` | Independent code review with confidence-based filtering |
| `pr-writer` | Generates structured PR descriptions from diff |
| `review-responder` | Triages and fixes automated reviewer comments |
| `docs-updater` | Verifies and updates changelog and implementation plan |

### Rules (auto-loaded context)
Architecture review, code quality, performance, and test review criteria.

### Hooks
Auto-format hook runs `ruff format` and `ruff check --fix` on every `.py` file edit.

## Usage

### Option 1: Copy into your project

```bash
cp -r .claude/ /path/to/your/project/.claude/
cp docs/DEVELOPMENT_PROCESS.md /path/to/your/project/docs/
```

Then add to your project's `CLAUDE.md`:

```markdown
## Development Process

Use `/sync` before starting work, `/design` to formalize a plan, `/done` when finished, and `/landed` after the PR merges.
Before creating any plan, read `docs/DEVELOPMENT_PROCESS.md` first.
```

### Option 2: Git submodule

```bash
cd /path/to/your/project
git submodule add <repo-url> .claude-harness
# Symlink or copy .claude/ directory
```

## Requirements

- Python project using `uv` package manager
- `ruff` and `pyright` for linting/type checking
- `pytest` for testing
- `gh` CLI for GitHub operations (PR creation, CI checks)
- `jq` for hook JSON parsing

## Configuration

- `settings.json` -- tool permissions and hooks (edit to match your project)
- `settings.local.json` -- machine-specific overrides (gitignored)
- `deploy.json` -- deployment verification config for `/landed` (optional, gitignored)

## Running Tests

```bash
uv sync --group dev
uv run pytest -v
```
