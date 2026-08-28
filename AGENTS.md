# Repository Maintenance Rules

## Scope

This repository publishes two reusable Codex Skills under `skills/`. Keep the Skills generic; project-specific product rules belong in each consuming project's `AGENTS.md` and `docs/ai/PROJECT.md`.

## Required Synchronization

When Skill behavior changes, update the affected `SKILL.md`, supporting references or scripts, root `README.md`, `CHANGELOG.md`, `docs/PROJECT.md`, `docs/ai/STATE.md`, and the active task card in the same delivery.

## Verification

- Run `python -B -m unittest discover -s skills/project-dev/tests -p "test_*.py" -v`.
- Validate both Skill folders with the Codex `skill-creator` validator before release.
- Inspect release archives and SHA-256 checksums before uploading them.
- Never commit credentials, customer data, local databases, runtime state, or generated release archives.
