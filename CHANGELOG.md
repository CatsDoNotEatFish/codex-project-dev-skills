# Changelog

All notable changes to this repository are recorded here.

## Unreleased

### Changed

- Added adaptive `fast`, `standard`, and `strict` project delivery modes.
- Fast work can use recoverable inline state without a task card or dedicated branch.
- Design synchronization is now an explicit task decision; ordinary implementation no longer churns the design document by default.
- Reduced repeated state transitions, full-context reads, test runs, checkpoints, and progress narration.
- Standard work now uses focused tests and one completion update; full gates are reserved for strict risk.
- TDD guidance now uses compact cycles and runs broader regression checks once after a coherent implementation.

### Compatibility

- Existing `project-dev` v1 project, state, and task files remain valid.
- New adaptive fields are optional and default legacy tasks to standard behavior.

## 1.0.0 - 2026-08-28

First public release.

### Added

- `project-dev` for greenfield bootstrap, existing-project adoption, cross-session state, bounded task delivery, safe Git operations, design synchronization, and recovery.
- `tdd-workflow` for verified test-first Red → Green → Refactor cycles.
- Risk-based routing across `tdd`, `mixed`, `test-after`, `exploratory`, and `none` modes.
- Configurable project-local design documents, protected paths, test commands, default branches, and push policies.
- Standard templates for project contracts, state, task cards, design baselines, Git ignore rules, and repository instructions.
- A standard-library project state checker and 14 unit/integration tests.
- GitHub Actions validation and downloadable release archives.
