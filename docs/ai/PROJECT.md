---
schema_version: project-dev-config/v1
project: codex-project-dev-skills
project_type: greenfield
design_document: docs/PROJECT.md
design_sync: when_affected
status_heading: Implementation Status
changelog_heading: Change Log
protected_paths: [".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "dist/**"]
test_commands: ["python -B -m unittest discover -s skills/project-dev/tests -p test_*.py -v"]
tdd_policy: risk-based
workflow_policy: adaptive
default_branch: main
created_at: 2026-08-28
---

# Project Development Contract

## Purpose

Publish a compact, reusable pair of Codex Skills for durable project coordination and selective test-driven development.

## Product Constraints

- Keep `project-dev` independent of any one product domain.
- Keep TDD optional and risk-driven.
- Preserve authorization boundaries for remote Git operations and destructive recovery.
- Keep ordinary user interaction simple even when repository evidence is detailed.
- Apply only the workflow rigor justified by failure impact and recovery needs.

## Data And Safety

- The repository contains no customer or production data.
- Release archives are generated under ignored `dist/` and uploaded only after verification.

## Definition Of Done

- Both Skills pass official structure validation.
- The project state test suite passes.
- README usage matches shipped behavior.
- Release archives match committed source and include SHA-256 checksums.
