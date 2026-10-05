---
schema_version: project-dev-state/v1
project: codex-project-dev-skills
stage: public-release
active_task: none
status: idle
workflow_mode: none
last_completed: RELEASE-003
git_branch: main
git_remote: origin
push_policy: manual
updated_at: 2026-10-05
---

# Current Project State

## Current Outcome

`v1.2.0` is published with archives that byte-match the tagged commit, verified checksums, tag provenance, and a successful CI run.

## Blockers

- None.

## Next Tasks

- Collect observed usage failures before planning another workflow change.
- Keep verification cost proportional to what changes: the packaging step of a release must not re-run suites whose inputs are unchanged.

## Verification Baseline

- Tests: 34 project state, adaptive workflow, Git lifecycle, repository-reality gate, and test-mode selection tests passed at `e96ac1c`; the release itself changed no executable behaviour and did not re-run them.
- State checker: strict validation passed with zero errors and zero warnings.
- Tag: annotated `v1.2.0` resolves to `472c697`, the release merge commit on `main`.
- Archives: built with `git -c core.autocrlf=false archive`; all 50 file entries hash-match their `v1.2.0` blobs, zero CRLF.
- GitHub Actions: `Validate Skills` run `37274284040` (run #5) passed for `472c697`.
- Release: `v1.2.0` is public with four assets whose GitHub digests match the local files.

## Handoff

`v1.2.0` is published at https://github.com/CatsDoNotEatFish/codex-project-dev-skills/releases/tag/v1.2.0. No delivery task is active; collect observed usage failures before planning another workflow change. The task branches `task/opt-002-token-footprint`, `task/opt-003-reality-gates`, `task/opt-004-test-scope`, and `task/release-003-publish-v1-2-0` remain local only, matching the repository convention that `origin` tracks `main` alone. `dist/` is a protected path and holds generated archives for v1.0.0 through v1.2.0; regenerate rather than edit it.
