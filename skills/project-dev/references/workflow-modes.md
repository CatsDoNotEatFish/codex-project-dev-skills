# Adaptive Workflow Modes

Read this reference when a new outcome begins, risk changes, or project policy requires a mode decision. Classification should take seconds, not become a planning exercise.

## Fast

Use `fast` only when all are true:

- the requested result is narrow and clearly understood;
- failure is easy to detect and reverse;
- it does not change database/schema, public API, authorization, privacy, money, destructive behavior, dependencies, deployment, or durable architecture;
- it is expected to finish in the current session;
- a focused check or direct inspection provides credible evidence.

Typical examples: copy, styling, a local configuration default, a small isolated bug, a narrow test adjustment, or documentation that does not change project governance.

Workflow:

1. Ensure the worktree is understood and the current branch is permitted.
2. Set state to `active_task: inline`, `workflow_mode: fast`, and `status: in_progress`; write a one-sentence outcome and handoff.
3. Implement directly without a card, dedicated branch, design update, or state checker preflight.
4. Run the smallest credible check once.
5. Reset state to idle and create one local commit.

If interrupted, leave inline state and the worktree intact. The next session inspects both and continues. If the task grows, convert it to standard or strict before adding unrelated scope.

## Standard

Use `standard` for ordinary product features, multi-file fixes, UI workflows, internal API work, and changes likely to need more than one coherent implementation step.

Workflow:

1. Create one compact task card and short task branch.
2. Set state and card to `in_progress` once; do not add a separate `verifying` transition unless another process requires it.
3. Implement a vertical slice and run focused tests.
4. Run broader regression checks only when shared behavior changed.
5. Set `design_sync_required` from actual durable design impact, not from file count or the mere existence of executable changes.
6. Update card, state, design when required, and evidence once at completion.
7. Run the state checker, commit, integrate, and follow push policy.

Use a checkpoint only for a coherent partial result that must survive a session boundary. Do not create a commit for every small internal step.

## Strict

Use `strict` for:

- database or data migrations and irreversible transformations;
- authentication, authorization, secrets, privacy, regulated or customer data;
- financial calculations, billing, quotas, or entitlement logic;
- destructive operations or external side effects that cannot be cheaply reversed;
- breaking API/schema/compatibility changes;
- releases, deployments, production configuration, or supply-chain changes;
- broad refactors across shared boundaries;
- recovery from conflicting or uncertain repository state.

Strict adds explicit rollback/recovery behavior, complete task scope, state checker preflight and completion checks, broader tests, staged-diff review, design synchronization when durable decisions change, and integration gates. TDD is selected only when the behavior is stable and testable; strict does not automatically mean TDD.

## Escalation

Escalate immediately when new evidence invalidates the current mode. Preserve the current diff and write the smallest additional coordination record needed. Do not downgrade an active strict task just to avoid checks; downgrade only when the original risk classification was demonstrably wrong and record the reason.

## Human Interaction

Routine implementation, tests, local commits, and configured Git operations should proceed autonomously. Pause only for a decision that changes product meaning, requires new external authority, risks destructive loss, or cannot be resolved from trusted project evidence.
