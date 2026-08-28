# Git Workflow

Read this reference only when Git operations are needed.

## Authorization And Safety

Local initialization, permitted branches, explicit-path staging, local commits, safe fetch, fast-forward pull, and verified local merges are normal project operations after the user asks this Skill to initialize or develop the project.

Creating or choosing a remote, pushing under `manual` or `disabled`, releasing, deploying, deleting remote branches, force-pushing, or rewriting published history needs explicit authority. Never fabricate Git identity or infer a remote from authentication.

Do not use hard reset, clean, forced restore, automatic stash, force-push, or history rewriting as recovery shortcuts.

## Initialize

Resolve the exact root, ensure no parent repository owns it, inventory secrets/runtime/generated data, merge ignore rules, configure protected paths, run `git init -b <default_branch>`, create coordination files, inspect staged paths and diff, validate, then commit `chore(init): establish project development baseline`. Without a configured remote, continue locally.

## Fast Work

Fast work may stay on the permitted current or default branch without a task branch. Begin only from an understood worktree. Stage explicit paths, inspect the staged diff, run the focused check, reset inline state to idle, and create one local commit.

Do not fetch or run broad integration checks repeatedly during several fast edits in the same known session. Fetch before a push or when remote collaboration could have changed the baseline. Escalate to standard before the change spans sessions intentionally, crosses boundaries, or accumulates unrelated scope.

## Standard And Strict Branches

Create `task/<task-id-lowercase>-<short-slug>` from a clean reconciled default branch. Record the branch in state and card. Standard uses one completion commit plus only necessary cross-session checkpoints. Strict may add reviewable commits where rollback or audit value justifies them.

Commit rules:

- stage explicit task paths and inspect staged names, stat, and relevant diff;
- exclude unrelated user changes and protected content;
- run checks proportional to the committed slice;
- never merge an incomplete checkpoint as completed work;
- do not amend pushed commits without explicit authorization.

## Synchronization

Fetch may run automatically when a remote exists. Pull only on a clean configured default branch with an upstream, using `git pull --ff-only`. Divergence requires inspection; never substitute automatic rebase, merge-pull, force, reset, or stash.

On a task branch, fetch remote changes but do not implicitly pull another branch into it. Update the default branch safely, then merge it into the task only when needed.

## Integrate

After standard or strict completion, commit verified task state, update a clean default branch, start `git merge --no-ff --no-commit <task-branch>`, run the required integration checks once, then commit `merge(<task-id>): <observable outcome>`. If conflicts or checks fail, stop and preserve the task branch.

## Push Policy

- `manual`: report local commits; do not push automatically.
- `after_merge`: push the verified default branch to its configured upstream after integration.
- `disabled`: do not push until the user changes policy.

Before pushing, verify destination, branch, ahead/behind counts, and protected paths. A rejected non-fast-forward push is a synchronization conflict, not permission to force-push.

## Conflict Recovery

Preserve base, local, and incoming versions. Resolve code and design from requirements, scope, and tests; never choose all of `ours` or `theirs` as a shortcut. Ask the user only when the conflict is a real product, data, or ownership decision.
