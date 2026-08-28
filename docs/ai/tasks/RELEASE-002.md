---
schema_version: project-dev-task/v1
task_id: RELEASE-002
stage: public-release
title: Publish adaptive workflow release v1.1.0
status: done
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
acceptance_complete: true
checks_complete: true
design_sync_complete: true
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

- [x] Repository documentation identifies `v1.1.0` as the current stable release.
- [x] Both Skills pass official structure validation and all 20 project tests pass.
- [x] Release archives contain only committed intended files and match their checksums.
- [x] The authorized repository, tag, release title, notes, and asset set are fixed before remote mutation.

## Required Checks

- `python -B -m unittest discover -s skills/project-dev/tests -p "test_*.py" -v`
- Official `skill-creator` quick validation for both Skill directories.
- `python skills/project-dev/scripts/check_project_state.py --project . --strict`
- Inspect archive file lists and verify `SHA256SUMS.txt` before and after upload.

## Delivery Evidence

- All 20 project state and workflow tests passed.
- Both Skill directories passed the official `skill-creator` quick validator.
- Strict project state validation passed after finalizing version references.
- Three `v1.1.0` archives matched their committed Git trees and `SHA256SUMS.txt` values.
- Remote destination is `CatsDoNotEatFish/codex-project-dev-skills`; the user explicitly authorized publication.
- Tag `v1.1.0` resolves to merge commit `2ebcd0f76f7e61b4829c2df6caca234225c35aa6`.
- GitHub release https://github.com/CatsDoNotEatFish/codex-project-dev-skills/releases/tag/v1.1.0 is public with all four assets uploaded and matching local digests.
- GitHub Actions `Validate Skills` run `33171027728` completed successfully for the tagged commit.

## Remaining Risks

- Real usage may reveal additional opportunities to reduce coordination cost without weakening recovery.

## Next Safe Action

- Collect observed usage failures before planning the next version.
