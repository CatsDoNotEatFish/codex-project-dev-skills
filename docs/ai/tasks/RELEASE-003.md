---
schema_version: project-dev-task/v2
task_id: RELEASE-003
stage: public-release
title: Publish v1.2.0 release
status: in_progress
workflow_mode: strict
branch: task/release-003-publish-v1-2-0
base_branch: main
depends_on: ["OPT-004"]
design_refs: ["Implementation Status", "Quality And Security", "Change Log"]
allowed_paths: ["README.md", "CHANGELOG.md", "docs/"]
forbidden_paths: ["dist/", ".env", "*.pem", "*.key"]
impacts: ["documentation", "delivery_status"]
test_mode: none
test_reason: Release packaging changes no executable behavior; the suites' inputs are unchanged since e96ac1c, so verification is archive contents, checksums, tag provenance, and CI status rather than a re-run
tdd_red_verified: false
design_sync_required: true
design_sync_reason: Publishing v1.2.0 changes the durable release and implementation status
acceptance_complete: false
checks_complete: false
design_sync_complete: true
design_version: 1.2.0
created_at: 2026-10-05
updated_at: 2026-10-05
---

# RELEASE-003 - Publish v1.2.0 Release

## Goal

Publish the merged `v1.2.0` work as a GitHub release whose archives byte-match the tagged commit and whose checksums, tag provenance, and CI status are verified before and after upload.

## Context Budget

Required:

- Applicable `AGENTS.md`
- `docs/ai/PROJECT.md`
- `docs/ai/STATE.md`
- This task card
- `docs/ai/tasks/RELEASE-002.md` as the established release precedent

Read if needed:

- `CHANGELOG.md`, `README.md` for the version references being updated

Do not read by default:

- Historical task cards other than `RELEASE-002`
- The generated archives themselves beyond entry-list and checksum inspection

## Scope

Allowed:

- `README.md`, `CHANGELOG.md`, `docs/` — version references and release records.

Forbidden:

- Change shipped Skill behaviour during release packaging; `skills/` must not change in this task.
- Commit generated archives, credentials, or unrelated changes.
- Rewrite published history or force-push.
- Re-run the unit suite: its inputs are unchanged since `e96ac1c`, so a re-run cannot fail differently.

## Acceptance Criteria

- [ ] Version references identify `v1.2.0` as the current stable release in `README.md`, `CHANGELOG.md`, and `docs/PROJECT.md`.
- [ ] All three archives are built from the `v1.2.0` tag with `core.autocrlf=false` and contain zero CRLF bytes, so they byte-match committed source.
- [ ] `SHA256SUMS.txt` matches the built archives, and the uploaded asset digests match the local files.
- [ ] `v1.2.0` is an annotated tag resolving to the release merge commit on `main`.
- [ ] `Validate Skills` passes for the tagged commit.
- [ ] `skills/` is unchanged by this task.

## Required Checks

- `git -c core.autocrlf=false archive --format=zip --prefix=codex-project-dev-skills-v1.2.0/ -o dist/codex-project-dev-skills-v1.2.0.zip v1.2.0`
- `git -c core.autocrlf=false archive --format=zip --prefix=project-dev/ -o dist/project-dev-v1.2.0.zip v1.2.0:skills/project-dev`
- `git -c core.autocrlf=false archive --format=zip --prefix=tdd-workflow/ -o dist/tdd-workflow-v1.2.0.zip v1.2.0:skills/tdd-workflow`
- Inspect each archive's entry list, confirm zero CRLF bytes, and verify `SHA256SUMS.txt`.
- `python <skill-dir>/scripts/check_project_state.py --project <repo> --strict`
- Confirm `git rev-parse v1.2.0^{commit}` equals the release merge commit and `Validate Skills` passed for it.

## Red Evidence

- Not applicable: `tdd_red_verified` is false and `test_mode` is `none`; this task changes no executable behavior.

## Delivery Evidence

- Pending publication.

## Remaining Risks

- `v1.1.0`'s per-skill archives carried CRLF-converted line endings while its notes claimed committed-source provenance. `v1.2.0` builds with `core.autocrlf=false`, so its archives differ in line endings from the previous release's per-skill archives even though the skill content is unchanged.

## Next Safe Action

- Finalise version references, merge, tag, build and verify archives, then publish with explicit authorization.
