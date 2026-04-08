# Development Process

Detailed development workflow for this repository. Referenced from `CLAUDE.md`.

---

## Context Recovery Rule -- CRITICAL

**After auto-compact or session continuation, ALWAYS read the relevant documentation files before continuing work:**

1. Read `docs/IMPLEMENTATION_PLAN.md` for current progress
2. Read `docs/CHANGELOG.md` for recent changes
3. Read any package-specific documentation relevant to the task

This ensures continuity and prevents duplicated or missed work.

---

## Task Classification

Scope (Q/S/P) is **auto-detected** by `/done` based on branch, diff size, and plan state. Do not classify manually upfront.

| Scope | When detected | Examples |
|-------|---------------|---------|
| **Q** (Quick) | On main/master, <=3 files, <100 lines | Typo fix, config tweak, one-liner bug fix |
| **S** (Standard) | On feature branch, no active plan phases | New feature, multi-file refactor, bug requiring investigation |
| **P** (Project) | IMPLEMENTATION_PLAN.md has unchecked phases | Multi-phase feature, architectural change, large migration |

---

## Pre-flight

Run `/sync` before starting any work. It fetches remote refs, reports branch state, dirty files, ahead/behind counts, and recent commits.

---

## Q. Quick Path

1. **Fix it** -- make the change
2. **Validate** -- run `uv run ruff check . && uv run ruff format --check . && uv run pytest`
3. **Commit and push** -- push directly to the base branch (`main`/`master`)
4. **Verify CI** -- run `gh run watch` to confirm the triggered run passes

If branch protection is enabled: after step 2, push to a short-lived branch, run `gh pr create --fill && gh pr checks --watch`, merge, and delete the branch.

If the fix fails twice, reveals unexpected complexity, or CI fails, promote to **S**.

---

## S. Standard Path

**S.1 Explore** -- Read relevant code and tests. Identify patterns/utilities to reuse. Understand scope.

**S.2 Plan** -- Read `docs/DECISIONS.md`. Check for conflicts with prior decisions; if a conflict is found, present the contradiction to the user before proceeding. Design approach. Identify files to modify. Log the feature request and any user decisions.

**S.3 Setup** -- Create feature branch from the base branch (`fix/...`, `feat/...`, `refactor/...`).

**S.4 Build (TDD cycle)**
1. Create code structure (interfaces, types)
2. Write tests
3. Write implementation
4. Write docstrings for public APIs; record non-trivial decisions in `docs/IMPLEMENTATION_PLAN.md`
5. Iterate (back to step 2 if needed)

**S.5 Validate** -- run both in parallel via agents:

| Agent | File | What it does |
|-------|------|-------------|
| Code Quality | `.claude/agents/code-quality-validator.md` | Lint, format, type check (auto-fixes) |
| Test Coverage | `.claude/agents/test-coverage-validator.md` | Run tests, check coverage |

Pre-commit hygiene (before agents): no leftover `TODO`/`FIXME`/`HACK`, no debug prints, no hardcoded secrets.

All agents use `subagent_type: "general-purpose"`. Do NOT use `feature-dev:code-reviewer`.

**S.6 Ship**
1. Commit and push
2. Create PR (use `.claude/agents/pr-writer.md` agent to generate description)
3. Verify CI with `gh pr checks`
4. Wait for automated reviewer (e.g., CodeRabbit). When comments arrive, use `.claude/agents/review-responder.md` to triage and fix. Push fixes before proceeding.
5. Code review: use `.claude/agents/code-reviewer.md` agent. Fix Critical issues before merge.
6. **Update the PR test plan** -- check off completed items, add results for any manual verification steps. Do this after every push to the PR branch, not just at the end.

**S.7 Document** -- Update `docs/CHANGELOG.md` with user-facing changes and `docs/DECISIONS.md` with decisions made. Use `.claude/agents/docs-updater.md` to verify.

**On failure:** fix the issue, amend or re-commit, re-run from the failed step. If multiple steps fail repeatedly, reassess scope.

---

## Failure Protocol

| Failure | Action |
|---|---|
| Validation (S.5) fails on current code | Fix, amend commit, re-run from S.5 |
| CI (S.6.3) fails on current code | Fix, push, re-run from S.6.3 |
| CI fails on pre-existing issue | Document separately, do not block current work |
| Code review flags architectural concern | Pause. Evaluate rework (back to S.4) vs. follow-up issue |
| Multiple steps fail repeatedly | Stop. Reassess scope -- may need to split into smaller increments |

---

## Post-merge

Run `/landed` after a PR is merged. It verifies merge CI, optionally checks
deployments (via `.claude/deploy.json`), cleans up branches, and identifies the
next phase for P-scope work.

---

## P. Project Path

**P.1 Analyze**
- Explore codebase architecture and boundaries
- Read `docs/IMPLEMENTATION_PLAN.md`, `docs/CHANGELOG.md`, and `docs/DECISIONS.md` for prior decisions
- **Consistency check**: scan `docs/DECISIONS.md` for conflicts or obsolete entries. Prune stale decisions. If conflicts found, present the contradiction to the user before proceeding.

**P.2 Plan**
- Design approach and write implementation plan in `docs/IMPLEMENTATION_PLAN.md`
- Define phases with acceptance criteria

**P.3 Execute** (repeat per phase)
1. Run Standard Path (S.1 through S.7) for the phase
2. Update `docs/IMPLEMENTATION_PLAN.md`
3. Write phase handoff note (2-5 sentences: what completed, deviations, risks, dependencies, intentional debt)

**P.4 Finalize** -- Merge. Version bump and changelog consolidation if applicable.

---

## Agent Reference

All custom agents are in `.claude/agents/` and use `subagent_type: "general-purpose"`.

| Step | Agent File | Purpose |
|------|-----------|---------|
| S.5 | `code-quality-validator.md` | Lint, format, type check |
| S.5 | `test-coverage-validator.md` | Tests and coverage |
| S.6.2 | `pr-writer.md` | Generate PR description |
| S.6.4 | `review-responder.md` | Handle automated reviewer comments |
| S.6.5 | `code-reviewer.md` | Independent code review |
| S.7 | `docs-updater.md` | Verify and update documentation |

---

## Hooks

1 hook script in `.claude/hooks/` runs automatically via settings.json:

| Hook | Event | Matcher | Behavior |
|------|-------|---------|----------|
| `auto-format.sh` | PostToolUse | Edit\|Write | Runs `uv run ruff format` and `uv run ruff check --fix` on edited .py files. Synchronous. |

All hooks require `jq` for JSON parsing and degrade gracefully if jq is missing.

---

## Skills

4 skills in `.claude/skills/`:

| Skill | Purpose |
|-------|---------|
| `/sync` | Pre-flight workspace sync. Fetches remote, reports branch state, dirty files, ahead/behind, recent commits. |
| `/design` | Crystallize brainstorming into a structured plan. Reads DECISIONS.md for conflicts, auto-classifies scope, outputs actionable plan. |
| `/done` | Universal completion. Auto-detects scope (Q/S/P), validates (3-tier checklist), ships/lands/delivers, updates docs. |
| `/landed` | Post-merge lifecycle. Verifies merge CI, optional deployment checks, cleans up branches, prepares next phase. |

---

## Rules

4 review rules in `.claude/rules/` auto-loaded as project context:

| Rule | Focus |
|------|-------|
| `architecture-review.md` | System design, dependencies, data flow, security boundaries |
| `code-quality-review.md` | DRY, error handling, type annotations, complexity |
| `performance-review.md` | N+1 queries, memory, caching, algorithmic complexity |
| `test-review.md` | Coverage gaps, test quality, edge cases, assertion quality |

These cover what linters cannot: architecture, design, and logic-level concerns.

---

## Changelog Format

Use [Keep a Changelog](https://keepachangelog.com/) format. Sections: Added, Changed, Deprecated, Removed, Fixed, Migration.

Entries must describe **user impact**, not just name the change:
- **Good**: "Users can now filter results by date range using `--since` and `--until` flags"
- **Bad**: "Added date filter"

Update changelog for every MINOR or MAJOR version bump. Patch updates are optional.

---

## PCC Shorthand

When the user says **"PCC"** or **"PCC now"**, run `/done` (which executes Validate, Ship/Land/Deliver, and Document).
