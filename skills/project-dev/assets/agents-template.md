# Project Maintenance Rules

## Sources Of Truth

- `docs/ai/PROJECT.md` defines the project development contract.
- The design document named there defines architecture and product behavior.
- `docs/ai/STATE.md` and its active task card define current delivery state.

## Project Invariants

- Record only durable, project-specific rules whose violation would cause data loss, security exposure, compatibility failure, or incorrect business behavior.

## Verification

- Run the checks declared by the active task and project contract.
- Keep design, implementation status, and change history synchronized when affected.
