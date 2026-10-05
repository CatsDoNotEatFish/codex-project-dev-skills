---
schema_version: project-dev-state/v1
project: codex-project-dev-skills
stage: public-release
active_task: none
status: idle
workflow_mode: none
last_completed: OPT-004
git_branch: task/opt-004-test-scope
git_remote: origin
push_policy: manual
updated_at: 2026-10-05
---

# Current Project State

## Current Outcome

`OPT-004` scopes verification cost to what actually changed: `operations` is no longer an executable impact, so release and packaging tasks may declare `test_mode: none`, and the policy that unchanged inputs must not be re-run is now stated where mode and check selection happen.

## Blockers

- None.

## Next Tasks

- Review and merge `task/opt-004-test-scope`, then cut a release from committed source.
- `task/opt-002-token-footprint`, `task/opt-003-reality-gates`, and `task/opt-004-test-scope` are all local and unpushed; only the last is needed, since it descends from the others.

## Verification Baseline

- Tests: 34 project state, adaptive workflow, Git lifecycle, repository-reality gate, and test-mode selection tests passed.
- State checker: strict validation passed with zero errors and zero warnings on this repository.
- Release: `v1.1.0` remains the published release with verified archives and SHA-256 checksums.
- Branch reality: `main` still matches `origin/main` at `c308537`.

## Handoff

`task/opt-004-test-scope` descends from `task/opt-003-reality-gates` (`86c593a`) and `task/opt-002-token-footprint` (`d23eeb1`); merging it brings all three. `main` is untouched. The design document records the corrected testing policy under `v1.2.0`, still unreleased. A release task must regenerate `dist/` from committed source, and must not re-run the suite for the packaging step itself — that is exactly the waste this change removes.
