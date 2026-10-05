---
schema_version: project-dev-state/v1
project: codex-project-dev-skills
stage: public-release
active_task: RELEASE-003
status: in_progress
workflow_mode: strict
last_completed: OPT-004
git_branch: task/release-003-publish-v1-2-0
git_remote: origin
push_policy: manual
updated_at: 2026-10-05
---

# Current Project State

## Current Outcome

Publish the merged `v1.2.0` work as a GitHub release whose archives byte-match the tagged commit and whose checksums, tag provenance, and CI status are verified before and after upload.

## Blockers

- None.

## Next Tasks

- Finalise version references, merge to `main`, tag `v1.2.0`, build and verify archives, then publish.
- Do not re-run the unit suite: its inputs are unchanged since `e96ac1c`.

## Verification Baseline

- Tests: 34 project state, adaptive workflow, Git lifecycle, repository-reality gate, and test-mode selection tests passed at `e96ac1c`.
- State checker: strict validation passed with zero errors and zero warnings on `main`.
- Release: `v1.1.0` is the current published release; `dist/` holds only the v1.0.0 and v1.1.0 archives.
- Provenance defect found: `v1.1.0`'s per-skill archives were packaged with `core.autocrlf=true`, so they carry CRLF endings and do not byte-match the tag, despite the release notes claiming committed-source provenance.

## Handoff

`RELEASE-003` is the active strict task on `task/release-003-publish-v1-2-0`, which descends from `e96ac1c` on `main`. Only version references and release records change here; `skills/` must stay untouched. Archives are built with `git -c core.autocrlf=false archive` from the tag so they byte-match committed source. Publication requires the user's authorization, which has been given for this release.
