# Git Workflow

Read this reference only for repository initialization, branches, commits, synchronization, integration, remotes, cleanup, or conflict recovery.

## Authorization And Safety

Local initialization, task branches, explicit-path staging, local commits, safe fetch, fast-forward pull, and verified local merges are normal project operations after the user asks this Skill to initialize or develop the project.

Separate authorization is required for creating a remote repository, choosing or changing a remote destination, pushing when policy is `manual` or `disabled`, publishing releases, deployments, deleting remote branches, force-pushing, or rewriting published history.

Never fabricate Git identity or infer the intended remote from authentication. If `user.name` or `user.email` is missing, request it before the first commit.

## Initialize

1. Resolve the exact project root and ensure a parent repository does not already own it.
2. Inventory secrets, local configuration, runtime data, databases, user content, generated output, dependencies, and existing ignore rules.
3. Merge `assets/gitignore-template.txt` with project-specific rules; do not overwrite an existing `.gitignore`.
4. Add sensitive project patterns to `protected_paths` in `docs/ai/PROJECT.md`. Preserve useful non-sensitive facts as hashes, counts, or source labels when needed; never duplicate protected content into documentation.
5. Run `git init -b <default_branch>` at the exact root.
6. Create the project contract, design baseline, state, and initial task before staging.
7. Inspect staged path names, stat, and relevant diff. Remove secrets, protected data, runtime files, dependencies, and generated output.
8. Run the state checker and applicable existing checks.
9. Commit the safe baseline as `chore(init): establish project development baseline`.
10. Without a configured remote, continue locally and report that synchronization is not configured.

## Task Branches

Create `task/<task-id-lowercase>-<short-slug>` from a clean, reconciled default branch. Record the exact base and task branch in the card and current branch in state.

When resuming, verify the branch and inspect staged, unstaged, and untracked paths before editing. Continue from commits, state, task evidence, and executable behavior rather than chat memory.

## Commits

Create local commits automatically when a slice is reviewable or a durable checkpoint materially improves cross-session recovery.

- stage explicit task paths; avoid blind repository-wide staging after initialization;
- inspect staged paths, stat, and relevant diff;
- exclude unrelated user changes and protected content;
- run checks proportional to the slice;
- never merge an incomplete checkpoint as completed work;
- do not amend or rewrite pushed commits without explicit authorization.

Use the task ID when applicable:

```text
feat(APP-007): add observable behavior
fix(APP-008): preserve a domain invariant
test(APP-007): cover failure behavior
docs(APP-007): synchronize design baseline
checkpoint(APP-007): save verified implementation slice
```

## Fetch And Pull

Fetching is read-only and may run automatically when a remote exists.

Pull only when the current branch is the configured default branch, worktree and index are clean, upstream exists, and fast-forward is possible. Use `git pull --ff-only`. If histories diverge, stop and inspect both sides; do not substitute automatic rebase, merge-pull, force, reset, or stash.

On an active task branch, fetch remote changes but do not implicitly pull another branch into the task. Checkpoint current work, update the default branch safely, then merge it into the task only when the task needs that baseline.

## Integrate

1. Complete acceptance, tests, documentation sync, evidence, and state on the task branch.
2. Run the state checker and commit the verified task result.
3. Switch to a clean default branch and fast-forward it from upstream when configured.
4. Start `git merge --no-ff --no-commit <task-branch>`.
5. If conflicts appear, stop before committing and follow conflict recovery.
6. Re-run task checks and the state checker against the merge candidate.
7. Commit as `merge(<task-id>): <observable outcome>` only when gates pass.
8. Follow `push_policy`.
9. Delete a local task branch only after the merge and required push are verified. Remote deletion requires explicit authorization.

If merge-candidate checks fail, abort the merge without altering the task branch and return the task to `needs_review` or `blocked`.

## Push Policy

- `manual`: do not push automatically; report exact local commits awaiting synchronization.
- `after_merge`: push the verified default branch to its configured upstream after integration. Do not push task branches unless separately requested.
- `disabled`: do not push; changing policy requires the user.

Before pushing, verify destination, branch, ahead/behind counts, and protected paths. A rejected non-fast-forward push is a synchronization conflict, never permission to force-push.

## Conflict Recovery

List exact conflicted paths and preserve base, local, and incoming versions. Resolve generated files through their source when possible. Resolve code and design from current requirements, task scope, and tests; never select all of `ours` or `theirs` as a shortcut. Ask the user when the conflict represents a real product, data, or ownership decision.

Do not use hard reset, clean, forced restore, automatic stash, force-push, or history rewriting as recovery shortcuts.
