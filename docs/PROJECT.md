# Codex Project Dev Skills Design

Version: 1.1.0-dev

Last updated: 2026-08-28

## Project Goal

Provide a small, reusable Codex Skill set that keeps long-lived AI-developed software projects coherent across disposable conversations without imposing a heavyweight multi-agent control system.

## Scope And Non-Goals

The repository owns project lifecycle coordination and an optional focused TDD workflow. It does not own a project's product requirements, choose remote repositories without authorization, deploy applications, or replace project-specific review and security policies.

## Core Workflows

- Bootstrap an empty project from a product brief and establish a reviewable design baseline.
- Adopt an existing codebase and document observed implementation before changing it.
- Resume one bounded active task from repository evidence.
- Select fast, standard, or strict workflow rigor from failure impact and recovery needs.
- Select a testing mode based on behavior stability, testability, and regression risk.
- Create safe local Git checkpoints, synchronize conservatively, verify integration, and leave a concise handoff.

## Architecture

`project-dev` is the lifecycle owner. Fast work uses short inline state plus Git differences; standard and strict work use cards and branches. Project-specific facts live in the consuming repository. `tdd-workflow` is loaded only for selected test-first work. Supporting details use progressive disclosure.

## Quality And Security

- Coordination validation uses Python standard library only.
- Protected paths are configured per consuming project with baseline secret patterns.
- Git workflows prohibit force-based recovery and unapproved remote actions.
- TDD completion requires observed Red-step evidence for the intended behavior.
- Existing v1 coordination files remain valid while optional adaptive fields enable lower-overhead work.
- Public releases are verified, checksummed, and produced from committed source.

## Delivery Roadmap

- `v1.0.0`: public baseline with two Skills, project initialization modes, Git lifecycle, risk-based testing, validation, documentation, and release artifacts.
- `v1.1.0`: adaptive workflow rigor, inline fast recovery, explicit design-sync decisions, and reduced repeated checks.
- Later versions will be driven by observed usage failures rather than speculative workflow expansion.

## Implementation Status

- `v1.1.0` adaptive workflow implementation and local validation are in progress.

## Decisions And Assumptions

- Both Skills ship in one repository because they share one project-delivery workflow while remaining independently installable.
- TDD remains a separate Skill to avoid loading specialized instructions into unrelated tasks.
- Project-specific business rules remain outside the generic Skills.
- Low-risk work should pay only the coordination cost required for safe cross-session recovery.

## Change Log

### 1.1.0-dev - 2026-08-28

- Added adaptive fast, standard, and strict workflows while preserving v1 compatibility.
- Added inline fast-state recovery and explicit design synchronization decisions.

### 1.0.0 - 2026-08-28

- Created the first public release baseline.
