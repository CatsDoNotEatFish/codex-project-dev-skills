---
schema_version: project-dev-task/v2
task_id: INIT-001
stage: discovery
title: Confirm the first observable project outcome
status: ready
workflow_mode: standard
branch: task/init-001-confirm-baseline
base_branch: main
depends_on: []
design_refs: ["Project Goal", "Implementation Status"]
allowed_paths: ["AGENTS.md", "docs/"]
forbidden_paths: []
impacts: ["documentation", "delivery_status"]
test_mode: none
test_reason: Documentation-only bootstrap task with no executable behavior
tdd_red_verified: false
design_sync_required: true
design_sync_reason: Initial project design and delivery status are the task outcome
acceptance_complete: false
checks_complete: false
design_sync_complete: false
design_version: pending
created_at: replace-with-current-date
updated_at: replace-with-current-date
---

# INIT-001 - Confirm The First Observable Project Outcome

## Goal

Describe one result a reviewer or user can observe.

## Context Budget

Required:

- Applicable `AGENTS.md`
- `docs/ai/PROJECT.md`
- `docs/ai/STATE.md`
- This task card
- Sections listed in `design_refs`

Read if needed:

- Nearby implementation and tests required to resolve a concrete uncertainty

Do not read by default:

- All historical task cards
- Raw or protected data
- Unrelated modules

## Scope

Allowed:

- List behavior and paths this task may change.

Forbidden:

- List protected behavior, data, and paths.

## Acceptance Criteria

- [ ] State the observable success behavior.
- [ ] State at least one relevant failure or boundary case.
- [ ] Preserve applicable project invariants.

## Required Checks

- Add exact trusted commands or narrowly defined manual inspections.
- `python <skill-dir>/scripts/check_project_state.py --project <repo> --strict`

## Red Evidence

- Required when `tdd_red_verified` is true: record the focused command and the failing result observed before implementation.
- A claim that it failed is not evidence. Show the command and what it reported.

## Delivery Evidence

- Pending. Show the commands that were run, not only the conclusion they reached.

## Remaining Risks

- Pending.

## Next Safe Action

- Implement only after scope, dependencies, and test mode are confirmed.
