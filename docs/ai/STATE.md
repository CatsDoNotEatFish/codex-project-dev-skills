---
schema_version: project-dev-state/v1
project: codex-project-dev-skills
stage: public-release
active_task: none
status: idle
workflow_mode: none
last_completed: OPT-002
git_branch: task/opt-002-token-footprint
git_remote: origin
push_policy: manual
updated_at: 2026-10-05
---

# Current Project State

## Current Outcome

`OPT-002` reduces the per-task instruction footprint of `project-dev`: the state-checker command is documented at its point of use, and `references/workflow-modes.md` is no longer mandatory for ordinary tasks.

## Blockers

- None.

## Next Tasks

- Review and merge `task/opt-002-token-footprint`, then cut a release from committed source.
- Keep collecting real usage feedback before adding further workflow rules.

## Verification Baseline

- Tests: 20 project state, adaptive workflow, and Git lifecycle tests passed.
- State checker: strict validation passed with zero errors and zero warnings.
- Token effect: `SKILL.md` grows by 382 bytes; `references/workflow-modes.md` (~3.8 KB) stops loading on ordinary tasks, a net saving of roughly 850 tokens per task.
- Release: `v1.1.0` remains the published release with verified archives and SHA-256 checksums.

## Handoff

`task/opt-002-token-footprint` holds the only change to `skills/project-dev/SKILL.md`; `main` still matches `origin/main` at `c308537`. No design synchronization was required: workflow semantics, the coordination file schema, and the published `v1.1.0` contract are unchanged, so this remains an unreleased instruction-routing change until the next release task.
