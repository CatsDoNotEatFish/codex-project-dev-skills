---
schema_version: project-dev-task/v1
task_id: RELEASE-002
stage: public-release
title: Publish adaptive workflow release v1.1.0
status: in_progress
workflow_mode: strict
branch: task/release-002-publish-v1-1-0
base_branch: main
depends_on: ["OPT-001"]
design_refs: ["Implementation Status", "Change Log"]
allowed_paths: ["README.md", "CHANGELOG.md", "docs/"]
forbidden_paths: ["dist/", ".env", "*.pem", "*.key"]
impacts: ["documentation", "operations", "delivery_status"]
test_mode: test-after
test_reason: Release metadata and archives must be verified against the already tested Skill sources
tdd_red_verified: false
design_sync_required: true
design_sync_reason: Publishing v1.1.0 changes the durable release and implementation status
acceptance_complete: false
checks_complete: false
design_sync_complete: false
design_version: 1.1.0
created_at: 2026-08-28
updated_at: 2026-08-28
---

# RELEASE-002 - Publish Adaptive Workflow Release v1.1.0

## Goal

Publish the verified adaptive low-overhead workflows as GitHub release `v1.1.0` with independently installable archives and checksums.

## Scope

Allowed:

- Finalize version, changelog, implementation status, and release documentation.
- Verify both Skills, project state, tests, archive contents, and checksums.
- Push the verified default branch and publish the authorized GitHub release.

Forbidden:

- Change shipped Skill behavior during release packaging.
- Commit generated archives, credentials, local runtime files, or unrelated changes.
- Rewrite published history or force-push.

## Acceptance Criteria

- [ ] Repository documentation identifies `v1.1.0` as the current stable release.
- [ ] Both Skills pass official structure validation and all 20 project tests pass.
- [ ] Release archives contain only committed intended files and match their checksums.
- [ ] GitHub `main`, tag `v1.1.0`, release notes, and uploaded assets are verified online.

## Required Checks

- `python -B -m unittest discover -s skills/project-dev/tests -p "test_*.py" -v`
- Official `skill-creator` quick validation for both Skill directories.
- `python skills/project-dev/scripts/check_project_state.py --project . --strict`
- Inspect archive file lists and verify `SHA256SUMS.txt` before and after upload.

## Delivery Evidence

- Pending.

## Remaining Risks

- Pending.

## Next Safe Action

- Finalize release metadata, then run all declared checks.
