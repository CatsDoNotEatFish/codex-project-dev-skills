---
name: project-dev
description: Initialize, adopt, resume, and deliver software projects across disposable Codex sessions using adaptive workflow rigor, repository state, safe Git checkpoints, and risk-based testing. Use for ongoing project development or recovery, including empty projects and undocumented codebases. Do not use for one-off coding questions outside a maintained project.
---

# Project Dev

Keep conversations disposable and the repository durable without turning every change into a ceremony. Recover from repository evidence, choose rigor proportional to risk, deliver one clear outcome, and leave only the state needed by the next session.

## Sources Of Truth

Use these sources in order:

1. Applicable `AGENTS.md` files define project-local rules and permissions.
2. `docs/ai/PROJECT.md` identifies the design baseline, protected paths, workflow policy, testing policy, and delivery conventions.
3. The configured design document records durable architecture and product decisions.
4. `docs/ai/STATE.md` records current coordination state.
5. An active task card, when required, defines the delivery contract.
6. Git state and executed checks are implementation evidence.

Conversation history is not project state. Preserve unrelated user changes and reconcile contradictions from repository evidence.

## Start With Minimum Context

1. Find the project root and read applicable `AGENTS.md` instructions.
2. Inspect the current Git branch and worktree.
3. Read `docs/ai/PROJECT.md` and `docs/ai/STATE.md`.
4. If coordination files are missing, classify the project and read [references/initialization.md](references/initialization.md).
5. If state points to `inline`, recover from its outcome, handoff, branch, and worktree diff. If it points to a task ID, read only that card, its design references, and relevant implementation files.
6. Run the state checker immediately only during initialization, recovery, strict work, or when evidence disagrees. Routine clean work does not need a ceremonial pre-check.

Do not read all design history, completed cards, raw data, or unrelated modules by default.

## Choose Workflow Rigor

Read [references/workflow-modes.md](references/workflow-modes.md) once when classifying a new outcome. Use the lightest safe mode and escalate when scope or risk grows.

- **Fast**: a low-risk, narrow change expected to finish in one session. Record it inline in `STATE.md`; do not create a task card or task branch.
- **Standard**: the default for ordinary features and fixes. Use one compact card, one short branch, focused checks, and one completion update.
- **Strict**: data migrations, security/privacy/auth, money, destructive or irreversible behavior, breaking contracts, releases/deployments, or broad cross-cutting changes. Use full gates.

Project policy or explicit user direction may require stricter handling. Never use `fast` merely because the user values speed when a failure could lose data, expose information, or break a published contract.

## Work Efficiently

Before editing, confirm the requested outcome and protected boundaries. Then follow the selected mode:

- write coordination state once before implementation and once at completion; do not cycle through administrative statuses;
- group routine commands and checks instead of narrating every internal gate;
- ask the user only for product decisions, missing external authorization, destructive choices, or semantic conflicts;
- run focused checks after relevant changes and broader checks once at completion when the blast radius justifies them;
- do not rerun an unchanged check merely to produce another receipt;
- create checkpoints only when work will cross sessions, a coherent partial slice exists, or recovery risk materially increases;
- update the design document only when architecture, contracts, durable workflows, project rules, roadmap, or milestone status actually changes.

For standard or strict work, create a card from [assets/task-template.md](assets/task-template.md). Record `workflow_mode`, test mode, a concrete test reason, and an explicit `design_sync_required` decision with its reason. Keep future cards `planned` and only one active delivery task.

Read [references/testing-strategy.md](references/testing-strategy.md) when executable behavior changes. Use `$tdd-workflow` only for `tdd` or the test-first portion of `mixed`; ordinary work does not gain value from performative Red-Green-Refactor.

Read [references/git-workflow.md](references/git-workflow.md) only before initialization, branch or commit decisions, synchronization, integration, conflict recovery, or cleanup.

## Preserve Cross-Session Recovery

For fast work, set `active_task: inline`, `workflow_mode: fast`, an active status, a concrete Current Outcome, and a useful Handoff before editing. The Git diff plus this short state is sufficient for another session. Complete the change with a focused check, one local commit, and reset state to idle.

For standard or strict work, the task card, branch, commits, and evidence carry progress. If the user says “save progress” or a session must end mid-task, create one coherent checkpoint when possible and update the handoff with completed work, remaining work, and the last trusted check.

If fast work expands, becomes risky, or will span multiple sessions, convert `inline` state into a standard or strict task card before continuing. Never discard or rewrite the existing diff during conversion.

## Complete

A change is complete when observable acceptance passes, required checks pass, required design synchronization is done, and no blocker remains.

- Fast: reset state to `active_task: none`, `status: idle`, `workflow_mode: none`; commit the intentional change on the permitted current branch.
- Standard: update card and state once, run the checker, commit the verified task, merge the short branch, and follow push policy.
- Strict: run all declared gates and integration checks before completion or external delivery.

Do not start the next task automatically. Report the workflow mode, outcome, branch/commit, checks, design sync decision, remote status, residual risk, and next safe action in a concise handoff.

## Recover

Freeze new edits when state, cards, worktree, branches, or design facts conflict. Preserve all evidence; do not auto-stash, hard-reset, discard changes, rewrite history, or choose one side of a semantic conflict. Repair only facts supported by the repository, then resume with the appropriate mode.
