---
name: sync
description: Pre-flight workspace sync. Run before starting any work to check branch state, remote tracking, dirty files, and recent commits.
allowed-tools: Read, Bash, Grep
disable-model-invocation: true
---

# Sync

Pre-flight workspace sync. Run this before starting any work.

## Steps

1. **Fetch remote refs**
   - Run `git fetch origin`

2. **Check workspace state**
   - Run `git status` to see dirty files, staged changes, untracked files
   - Run `git branch -vv` to see current branch, tracking info, ahead/behind counts

3. **Auto-reset to master if nothing is blocking**

   If ALL of the following are true, automatically run `git checkout master && git pull --rebase` without asking:
   - Working tree is clean (no staged, unstaged, or untracked changes that matter)
   - Current branch is NOT master (already on a feature branch that can be left)
   - The feature branch has no unpushed commits (ahead 0, or branch was already merged)

   If any blocker exists, do NOT auto-reset. Instead report the blocker and ask what to do:
   - **Dirty working tree**: list the files and ask whether to stash, commit, or discard
   - **Unpushed commits on current branch**: warn and ask whether to push first or switch anyway
   - **Already on master**: just `git pull --rebase` to update

4. **Show recent context**
   - Run `git log --oneline -3` to show the last 3 commits (after any branch switch)

5. **Output structured report**

```
# Workspace Sync

Branch: <name> (tracking: <remote>/<branch>)
Status: <clean | N dirty files | N staged, M unstaged>
Remote: <up to date | N ahead, M behind>

## Actions Taken
- <e.g. "Switched to master and pulled 5 new commits", or "None -- already on clean master">

## Blockers (if any)
- <e.g. "Unstaged changes in .claude/settings.json -- stash, commit, or discard?">

## Recent Commits
- <hash> <message>
- <hash> <message>
- <hash> <message>
```
