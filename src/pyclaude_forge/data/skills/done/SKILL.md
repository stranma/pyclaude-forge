---
name: done
description: Universal completion command. Auto-detects scope (Q/S/P), validates code quality, ships/lands/delivers changes, and updates documentation.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
disable-model-invocation: true
---

# Done

Universal completion command. Call this when work is finished to validate, ship, and document.

## Phase 1: Detect Scope

Determine scope from workspace signals:

| Signal | Q (ship) | S (land) | P (deliver) |
|--------|----------|----------|-------------|
| Branch | main/master | feature branch | feature branch |
| Files changed | <=3 | >3 | any |
| IMPLEMENTATION_PLAN.md | no unchecked phases | no unchecked phases | has unchecked phases |
| Diff size | <100 lines | >=100 lines | any |

**Decision logic** (first match wins):
1. If `docs/IMPLEMENTATION_PLAN.md` has unchecked phases -> **P** (deliver)
2. If on a feature branch -> **S** (land)
3. If on main/master AND small scope (<=3 files, <100 lines changed) -> **Q** (ship)
4. If on main/master AND large scope -> warn user, suggest creating a feature branch

**Always report the detected scope and accept user override.**

## Phase 2: Validate

Absorbs the former `/ship` checklist. Three tiers of checks:

### Blockers (must ALL pass -- stop if any fail)

1. **No secrets in codebase**
   - Search for: `sk-`, `AKIA`, `ghp_`, `password=`, `secret=`, `-----BEGIN.*PRIVATE KEY`
   - Zero matches in tracked files (exclude `.env.example`)

2. **No debug code**
   - Search for: `breakpoint()`, `pdb.set_trace()` in non-test source files
   - These are hard blockers -- any match stops the process

3. **Pre-commit hygiene**
   - Search for leftover `TODO`, `FIXME`, `HACK` markers in changed files
   - List all found with file:line for review

### High Priority (run via agents in parallel)

Launch two agents simultaneously:

| Agent | File | What it checks |
|-------|------|---------------|
| Code Quality | `.claude/agents/code-quality-validator.md` | Lint (`ruff check`), format (`ruff format --check`), type check (`pyright`) |
| Test Coverage | `.claude/agents/test-coverage-validator.md` | All tests pass, coverage report |

All agents use `subagent_type: "general-purpose"`.

### Recommended

1. **Git history** -- check for WIP/fixup commits that should be squashed
2. **Branch up to date** -- check if behind base branch

### Skip Conditions

- If no `.py` files are changed: skip Python tooling (lint, format, types, tests)
- Report skipped checks and why

### Blocker Found

If any Blocker fails: **STOP**. Report all findings and do not proceed to Phase 3.

## Phase 3: Ship / Land / Deliver

Actions depend on detected scope:

### Q (Ship)

1. `git add` changed files
2. `git commit` with descriptive message
3. `git push` to main/master
4. `gh run watch` to verify CI passes

Note: If a direct push to main fails due to branch protection, re-detect scope as **S (Land)** and follow the S path instead.

### S (Land)

1. `git add` changed files
2. `git commit` with descriptive message
3. `git push -u origin <branch>`
4. Create PR using `.claude/agents/pr-writer.md` agent for description
5. `gh pr checks --watch` to verify CI
6. When automated reviewer comments arrive, use `.claude/agents/review-responder.md` to triage and fix
7. Run `.claude/agents/code-reviewer.md` for independent code review
8. Fix Critical issues before merge

### P (Deliver)

All of S (Land), plus:

1. Verify acceptance criteria using `.claude/agents/acceptance-criteria-validator.md`
2. Update `docs/IMPLEMENTATION_PLAN.md` using `.claude/agents/implementation-tracker.md`
3. Write phase handoff note (2-5 sentences: what completed, deviations, risks, dependencies, intentional debt)
4. If this is the final phase: version bump and changelog consolidation

## Phase 4: Document

### Q (Ship)
- Update `docs/CHANGELOG.md` only if the change is user-facing

### S (Land) and P (Deliver)
- Always update `docs/CHANGELOG.md` with user-facing changes
- Always update `docs/DECISIONS.md` with decisions made during the work
- Use `.claude/agents/docs-updater.md` to verify documentation is complete

## Failure Protocol

| Failure | Action |
|---------|--------|
| Validation (Phase 2) fails | Fix issues, re-run from Phase 2 |
| CI (Phase 3) fails | Fix, push, re-run from Phase 3 CI step |
| CI fails on pre-existing issue | Document separately, do not block current work |
| Code review flags architectural concern | Pause. Evaluate rework vs. follow-up issue |
| Acceptance criteria (P) reveals regression | File as separate issue. Fix only if direct regression |
| Multiple steps fail repeatedly | Stop. Reassess scope -- may need to split work |
