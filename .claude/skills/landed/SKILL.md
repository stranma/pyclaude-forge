---
name: landed
description: Post-merge lifecycle. Verifies merge CI, optional deployment checks, cleans up branches, and prepares next phase.
allowed-tools: Bash, Read, Grep, Glob
disable-model-invocation: true
---

# Landed

Post-merge lifecycle command. Run this after a PR is merged to verify CI, check deployments, clean up branches, and identify next steps.

## Step 1: Detect Merged PR

Identify the PR that was just merged.

1. Run `git branch --show-current` to get the current branch
2. If already on master:
   - Check `git reflog --oneline -20` for the previous branch name
   - If no branch found, ask the user for the PR number or branch name
3. Look up the merged PR:

   ```bash
   gh pr list --state merged --head <branch> --json number,title,mergeCommit -L 1
   ```

4. If no PR found: ask the user for the PR number directly
5. Display: PR number, title, merge commit SHA

**Pre-check**: Run `gh auth status` early. If not authenticated, stop and instruct the user to run `gh auth login`.

## Step 2: Verify Merge CI

Check that CI passed on the merge commit.

1. List recent runs on master:

   ```bash
   gh run list --branch master -L 20 --json status,conclusion,databaseId,name,headSha
   ```

2. Filter to runs whose `headSha` matches the merge commit SHA
3. Evaluate all matched runs:
   - **in_progress**: watch still-running run(s) with `gh run watch <id>`
   - **success**: all matched runs must be `completed` with `conclusion=success` to proceed
   - **failure**: show details via `gh run view <id> --log-failed` for each failing run
     - Ask: "Is this a recurring issue or specific to this PR?"
     - If recurring: suggest adding to `/done` validation or pre-merge CI
     - If specific: diagnose inline from the failed log output

## Step 3: Deployment Verification (Configurable)

Check for deployment status if configured.

1. Check if `.claude/deploy.json` exists
2. If it exists:
   - Read the file and iterate over configured environments
   - For each environment:
     - Watch the deployment workflow: `gh run list --workflow <workflow> --commit <merge-commit-sha> --json status,conclusion,databaseId`
     - If `health_check` URL is configured, fetch it and verify a 200 response
   - Report per-environment status (success/failure/in_progress)
3. If no config file:
   - Ask the user: "Is there a deployment to verify? (skip if none)"
   - If user says no or skips: mark as "skipped"

## Step 4: Branch Cleanup

Switch to master and clean up the feature branch.

1. `git checkout master && git pull --rebase`
2. Delete local branch: `git branch -d <branch>` (safe delete, will fail if unmerged)
3. Check if remote branch still exists: `git ls-remote --heads origin <branch>`
4. If remote branch exists:
   - Ask the user before deleting: "Delete remote branch origin/<branch>?"
   - If approved: `git push origin --delete <branch>`
   - If denied: note "kept" in summary
5. If remote branch already deleted (e.g., GitHub auto-delete): note "already deleted by GitHub" in summary

**Edge case**: If already on master and the branch was already deleted locally, skip local deletion gracefully.

## Step 5: Next Phase (P-scope Only)

Check if there is more planned work.

1. Read `docs/IMPLEMENTATION_PLAN.md`
2. If the file exists, check the "Quick Status Summary" table near the top for any phase whose status is not "Complete":
   - Identify the next incomplete phase
   - Summarize what it covers and any noted dependencies
3. If all phases show "Complete" or no plan file exists: skip this step

## Step 6: Summary Report

Output a summary of everything that happened:

```text
# Landed

PR: #N "<title>" merged into master
CI: PASS (run #ID) | FAIL (run #ID) | WATCHING
Deploy: verified / skipped / failed

## Cleanup
- Deleted local branch: <branch>
- Deleted remote branch: <branch> [or "kept" or "already deleted by GitHub"]
- Now on: master (up to date)

## Next Steps
- [next phase summary / "Ready for new work" / "Project complete"]
```

## Edge Cases

- **Already on master**: check `git reflog` for previous branch, or ask the user
- **PR not found via branch name**: ask the user for the PR number
- **Remote branch already deleted**: GitHub auto-delete is common; handle gracefully
- **gh not authenticated**: check `gh auth status` early and stop with instructions
- **No CI runs found**: report "no CI runs found for merge commit" and proceed
