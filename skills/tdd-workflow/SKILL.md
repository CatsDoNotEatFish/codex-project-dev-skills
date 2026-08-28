---
name: tdd-workflow
description: Implement or repair stable, observable software behavior through a compact verified test-first Red-Green-Refactor loop. Use when the user requests TDD, a project task selects TDD or mixed mode, or a deterministic high-risk rule benefits from executable examples. Do not use for documentation, exploratory work, purely visual styling, or behavior without a feasible reliable harness.
---

# TDD Workflow

Use TDD where test-first feedback improves correctness or design. Keep the loop compact; do not turn it into repeated narration, full-suite runs, or tests of private implementation detail.

## Confirm One Behavior

Identify the observable behavior, caller, success example, relevant failure or boundary case, protected invariants, and narrowest reliable test level. Resolve material product ambiguity before encoding it.

For legacy code, defects, adapters, database behavior, or UI behavior, read [references/patterns.md](references/patterns.md) only for the matching section.

## Red

Add the smallest test for the next behavior and run only the focused command. Confirm failure is caused by missing or incorrect behavior, not syntax, imports, fixtures, infrastructure, or a broken harness. If it passes immediately, determine whether behavior already exists or the test is ineffective; do not claim Red evidence.

## Green

Make the smallest coherent production change that satisfies the behavior. Do not add test-only branches, weaken assertions, or broaden scope. Run the focused test until it passes.

## Refactor

Improve structure only when useful while the focused test stays green. Repeat for another behavior only when it represents a distinct required example.

Run nearby or full regression checks once after the coherent implementation/refactor, not after every micro-cycle. Report Red reason, Green result, broader check, and remaining risk at completion rather than narrating every command.

## Test Quality

- Prefer public behavior over private structure.
- Use real fast deterministic collaborators; use fakes at owned boundaries and mocks only for meaningful interaction contracts.
- Add cases proportional to credible regression risk, not coverage targets.
- Keep tests deterministic and isolated from production systems.
- Never delete or loosen a valid regression test merely to pass.

An AI can make a wrong test agree with wrong code. Use project rules and user outcomes as the acceptance source, and independently verify high-risk behavior.

For `mixed`, use this loop only for the stable testable core. Verify layout, accessibility, external systems, performance, deployment, and environment-dependent outcomes with suitable non-TDD checks.

Set `tdd_red_verified` only after observing the intended Red result.
