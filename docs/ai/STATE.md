---
schema_version: project-dev-state/v1
project: codex-project-dev-skills
stage: public-release
active_task: none
status: idle
workflow_mode: none
last_completed: OPT-004
git_branch: main
git_remote: origin
push_policy: manual
updated_at: 2026-10-05
---

# Current Project State

## Current Outcome

The `v1.2.0` line is merged to `main`: per-task instruction footprint reduced, coordination records reconciled with the repository, and verification cost scoped to what actually changed. Not yet released.

## Blockers

- None.

## Next Tasks

- Cut `RELEASE-003` from committed source: regenerate `dist/` archives, verify contents and `SHA256SUMS.txt`, tag, publish, then update version references.
- Do not re-run the unit suite for the packaging step: use `test_mode: none`, verify artifacts only, and cite the verified run below.

## Verification Baseline

- Tests: 34 project state, adaptive workflow, Git lifecycle, repository-reality gate, and test-mode selection tests passed on `main`.
- State checker: strict validation passed with zero errors and zero warnings on `main`.
- Merged: `merge(OPT-004)` at `3e7c028` brings `aca0a40`, `86c593a`, and `d23eeb1`.
- Release: `v1.1.0` remains the published release; `dist/` still holds only the v1.0.0 and v1.1.0 archives and must be regenerated for `v1.2.0`.

## Handoff

`main` carries the `v1.2.0` work and is pushed to `origin/main`. The task branches `task/opt-002-token-footprint`, `task/opt-003-reality-gates`, and `task/opt-004-test-scope` remain local only, matching the repository convention that `origin` tracks `main` alone. `docs/PROJECT.md` records `v1.2.0` as implemented but unreleased, so the next delivery is a release task rather than a feature task. `dist/` is a protected path: regenerate it from committed source instead of editing it.
