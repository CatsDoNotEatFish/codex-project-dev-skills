---
name: project-dev
description: Initialize, adopt, resume, and deliver software projects across disposable Codex sessions using repository state, bounded task cards, safe Git checkpoints, configurable design-document gates, and risk-based testing. Use for ongoing project development or recovery, including empty projects and undocumented existing codebases. Do not use for one-off coding questions outside a maintained project.
---

# Project Dev

Keep conversations disposable and the repository durable. Recover current work from project files, execute one bounded outcome, verify it, and leave evidence another session can trust.

## Sources Of Truth

Use these sources in descending scope:

1. Applicable `AGENTS.md` files define project-local rules and permissions.
2. `docs/ai/PROJECT.md` identifies the design baseline, protected paths, testing policy, and delivery conventions.
3. The configured design document records architecture, product decisions, roadmap, and implementation status.
4. `docs/ai/STATE.md` is the sole current coordination state.
5. The active task card is the current delivery contract.
6. Git state and executed checks are implementation evidence.

Conversation history is never project state. When sources disagree, freeze new edits and reconcile the narrowest stale source from repository evidence.

## Select A Mode

- **Bootstrap**: Turn an empty project idea into a reviewed design baseline and first delivery task.
- **Adopt**: Establish an as-is baseline for existing code with missing or incomplete governance.
- **Resume**: Continue the active task from repository evidence.
- **Plan**: Define or revise one observable task without implementing when planning is requested.
- **Implement**: Deliver the active task within its declared scope.
- **Review**: Inspect changes and evidence without fixing unless changes were requested.
- **Recover**: Reconcile interrupted, missing, stale, or conflicting state.

For Bootstrap or Adopt, read [references/initialization.md](references/initialization.md) and [references/git-workflow.md](references/git-workflow.md). Use the templates only while creating the corresponding project files.

## Start Every Project Operation

1. Find the project root and read all applicable `AGENTS.md` instructions.
2. Inspect Git status, branch, worktree, remotes, and upstream before relying on recorded state.
3. Read `docs/ai/PROJECT.md` and `docs/ai/STATE.md`. If either is missing, enter Bootstrap or Adopt rather than guessing progress.
4. Run `python <skill-dir>/scripts/check_project_state.py --project <repo>` after the coordination files exist.
5. Read only the active task card, its `design_refs`, and files needed for the requested outcome.
6. Enter Recover when config, state, task, branch, worktree, or executable evidence disagree.

Do not load the full design history, every completed card, raw data, or unrelated modules by default.

## Initialize Or Adopt

Classify the repository from evidence, not the user's vocabulary:

- empty or nearly empty: Bootstrap from the product brief;
- meaningful source code but no trustworthy design baseline: Adopt and document the current implementation before changing it;
- existing governance: preserve its conventions and add only missing coordination files.

Initialization may create local project files, run `git init`, and create a safe local baseline commit when the user asks this Skill to initialize or take over the project. It does not authorize inventing a remote, pushing, releasing, deploying, or committing secrets and runtime data.

For a blank project, resolve only decisions that materially change product scope, platform, data sensitivity, or architecture. Record reasonable assumptions explicitly. Create a design-confirmation task and do not begin broad feature development while pivotal decisions remain unresolved.

## Plan One Bounded Task

Create `docs/ai/tasks/<task_id>.md` from [assets/task-template.md](assets/task-template.md). Define one observable goal, allowed and forbidden scope, dependencies, acceptance cases, exact checks, documentation impacts, and delivery evidence.

Use only these impact values:

`data`, `api`, `domain`, `security_privacy`, `ui`, `operations`, `dependencies`, `architecture`, `documentation`, `delivery_status`, or `none`.

Do not combine `none` with another impact. Any non-`none` impact follows the design-sync policy in `docs/ai/PROJECT.md`.

Choose `test_mode` by reading [references/testing-strategy.md](references/testing-strategy.md) whenever behavior changes. Allowed modes are `tdd`, `mixed`, `test-after`, `exploratory`, and `none`. Record a concrete `test_reason`; do not select TDD by habit or avoid it merely for speed.

Use `$tdd-workflow` when it is installed and the task mode is `tdd`, or for the test-first slice of `mixed`. Otherwise preserve the same essential evidence: observe the new test fail for the intended reason before implementation, make it pass with the smallest coherent change, then refactor under passing tests.

Keep one active delivery task. Future cards remain `planned`; finishing one task does not authorize starting the next.

## Implement Safely

Before editing, confirm that the user requested a change, the active card matches it, dependencies are complete, and intended paths fit the declared scope. Revise the task contract first when scope genuinely changes.

Read [references/git-workflow.md](references/git-workflow.md) before branch creation, commits, synchronization, integration, conflict recovery, or branch cleanup.

- create or resume the task branch before implementation;
- preserve unrelated user changes and project-specific protected data;
- prefer a small vertical slice that remains runnable and reviewable;
- do not expand into speculative future infrastructure;
- keep project state updates in the main session unless the user explicitly requests parallel agents.

## Verify And Complete

Set the task to `verifying`, then execute every Required Check and test the risk-bearing behavior. File existence alone is not acceptance evidence.

When design sync is required by `docs/ai/PROJECT.md`:

- revise affected design sections to match actual behavior;
- update the configured implementation-status and change-log sections;
- update the document version/date when that document uses them;
- record the resulting identifier in `design_version`.

A task may become `done` only when acceptance and required checks pass, required documentation is synchronized, TDD red-step evidence exists when applicable, and no blocker remains. Otherwise use `blocked` or `needs_review` with the exact next safe action.

After completion, commit verified task state on its task branch, integrate through the Git gate, follow `push_policy`, set `active_task: none`, and leave the project `idle` unless the user explicitly authorized another task.

## Recover And Handoff

Recovery preserves evidence. Do not automatically stash, discard, reset, rewrite, or choose one side of a semantic conflict. Compare config, state, cards, design, branches, history, worktree, remotes, and executable checks; repair only facts supported by evidence.

Report the mode, task and status, branch, local and merge commits, remote synchronization, changed files, check outcomes, design version, blockers, assumptions requiring review, and the next safe action.
