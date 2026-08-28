---
schema_version: project-dev-task/v1
task_id: RELEASE-001
stage: public-release
title: Publish the first reusable Skill release
status: done
branch: task/release-001-first-public-release
base_branch: main
depends_on: []
design_refs: ["Implementation Status", "Change Log"]
allowed_paths: ["skills/", "README.md", "LICENSE", "CHANGELOG.md", ".github/", "docs/"]
forbidden_paths: ["dist/", ".env", "*.pem", "*.key"]
impacts: ["documentation", "operations", "delivery_status"]
test_mode: test-after
test_reason: Release packaging is verified after assembling both independently tested Skills
tdd_red_verified: false
acceptance_complete: true
checks_complete: true
design_sync_complete: true
design_version: 1.0.0
created_at: 2026-08-28
updated_at: 2026-08-28
---

# RELEASE-001 - Publish The First Reusable Skill Release

## Goal

Publish one public repository and a `v1.0.0` release containing independently installable `project-dev` and `tdd-workflow` Skills.

## Scope

Allowed:

- Package the two verified Skill sources.
- Document purpose, installation, usage, testing modes, Git behavior, and validation.
- Add CI validation and release archives.

Forbidden:

- Product-specific customer data or rules.
- Credentials, local runtime files, generated archives in Git history, or unverified release claims.

## Acceptance Criteria

- [x] A public GitHub repository contains both standard Skill directories.
- [x] README explains purpose, installation, normal use, and TDD selection.
- [x] Both Skills pass official structure validation.
- [x] The 14-test state and Git lifecycle suite passes.
- [x] `v1.0.0` archives and checksums are generated from committed source.

## Required Checks

- `python -B -m unittest discover -s skills/project-dev/tests -p "test_*.py" -v`
- Official `skill-creator` quick validation for both Skill directories.
- `python skills/project-dev/scripts/check_project_state.py --project . --strict`
- Compare source and packaged archive contents; calculate SHA-256 checksums.

## Delivery Evidence

- Both official Skill validations passed.
- All 14 unit/integration tests passed.
- Project state validation passed in strict mode.
- Release archives were generated from committed source and verified with SHA-256 checksums.

## Remaining Risks

- Real-world usage may reveal project conventions not represented by the initial generic schema.
- GitHub authentication and remote policies still vary across consuming environments.

## Next Safe Action

- Collect observed usage failures before planning the next version.
