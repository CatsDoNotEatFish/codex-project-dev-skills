---
schema_version: project-dev-config/v1
project: replace-with-project-id
project_type: greenfield
design_document: docs/PROJECT.md
design_sync: when_affected
status_heading: Implementation Status
changelog_heading: Change Log
protected_paths: [".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.db", "*.sqlite", "*.sqlite3", "logs/**", "backups/**"]
test_commands: []
tdd_policy: risk-based
default_branch: main
created_at: replace-with-current-date
---

# Project Development Contract

## Purpose

Record the project identity and the smallest useful product outcome.

## Product Constraints

- Add only rules that materially constrain implementation choices.

## Data And Safety

- Record sensitive data, irreversible operations, and project-specific protected paths.

## Definition Of Done

- Observable acceptance behavior is verified.
- Required automated and manual checks pass.
- Design and status records match the implementation.
- Git history contains only intentional, reviewable project changes.
