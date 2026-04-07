---
name: design
description: Crystallize brainstorming into a structured implementation plan. Reads DECISIONS.md for conflicts, auto-classifies scope (Q/S/P), and outputs an actionable plan.
argument-hint: "[topic or summary of what to plan]"
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# Design

Crystallize brainstorming into a structured implementation plan. Use at the start or end of brainstorming to formalize an approach.

## Steps

### 1. Check for Conflicts

- Read `docs/DECISIONS.md` -- scan for entries that conflict with or overlap the proposed work
- Read `docs/IMPLEMENTATION_PLAN.md` -- check for active phases or overlapping planned work
- If conflicts found: present the contradiction to the user before proceeding

### 2. Auto-Classify Scope

This is a planning-time estimate based on conversation context. `/done` will later auto-detect actual scope from workspace signals (branch, files changed, diff size, plan state) at completion time.

| Scope | Criteria |
|-------|----------|
| **Q** (Quick) | Trivial, obvious, single-location change (typo, config tweak, one-liner) |
| **S** (Standard) | Fits in one session, clear scope (new feature, multi-file refactor, investigation) |
| **P** (Project) | Needs phased execution across sessions (multi-phase feature, architecture change) |

### 3. Output Structured Plan

The plan format varies by scope:

#### Q (Quick)
```
## Plan (Quick)
**Fix**: <what to change>
**File**: <target file>
**Recommendation**: Proceed directly -- this is a single-location change.
```

#### S (Standard)
```
## Plan (Standard)
**Scope**: <1-2 sentence summary>
**Branch**: `<fix|feat|refactor>/<short-name>`

### Files to Modify
- <file> -- <what changes>

### Approach
<numbered steps>

### Test Strategy
<what to test and how>

### Risks
- <potential issues>
```

#### P (Project)
```
## Plan (Project)
**Scope**: <1-2 sentence summary>

### Phase 1: <name>
**Acceptance Criteria**:
- [ ] <criterion>
**Files**: <list>
**Approach**: <summary>

### Phase 2: <name>
...
```

For P-scoped plans: write the phase breakdown to `docs/IMPLEMENTATION_PLAN.md` using the same structure shown above (phase name, acceptance criteria, files, approach). The `.claude/agents/implementation-tracker.md` agent validates this format.

### 4. Decision Candidates

List any decisions that should be recorded in `docs/DECISIONS.md`:
- Architectural choices made during planning
- Alternatives considered and rejected
- Constraints or assumptions

### 5. User Confirmation

Present the plan and wait for user approval before implementation begins.
