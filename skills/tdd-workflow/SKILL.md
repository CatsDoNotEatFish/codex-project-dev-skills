---
name: tdd-workflow
description: Implement or repair stable, observable software behavior through a verified test-first red-green-refactor loop. Use when the user requests TDD, a project task selects TDD or mixed mode, or a deterministic high-risk rule benefits from executable examples. Do not use for documentation-only work, open-ended product discovery, purely visual styling, or exploratory spikes without a feasible test harness.
---

# TDD Workflow

Use tests to shape one behavior at a time and preserve evidence that the test could detect its absence. TDD is a development technique, not a requirement to unit-test every line or mock every dependency.

## Confirm The Contract

Before editing, identify:

- the observable behavior and user or caller;
- one success example and relevant boundary or failure case;
- project invariants that must remain true;
- the narrowest reliable test level: unit, integration, contract, component, or end-to-end;
- the existing command that runs the focused test.

If the requirement is materially ambiguous, resolve the product decision before encoding it in a test. If the environment or interface is unknown, use a bounded exploratory task first rather than pretending to follow TDD.

For legacy code, defects, external adapters, or database behavior, read [references/patterns.md](references/patterns.md) before choosing the first test.

## Red

1. Add one smallest test that describes the next observable behavior through a stable interface.
2. Run that test before production implementation.
3. Confirm it fails because the behavior is missing or wrong, not because of syntax, imports, fixtures, unavailable infrastructure, or a broken harness.
4. Record the command and expected failure summary in task evidence when a task system exists.

If the test passes immediately, determine whether behavior already exists, the assertion is ineffective, or the test reaches the wrong path. Do not claim red-step evidence until the test demonstrates the intended gap.

## Green

Implement the smallest coherent production change that satisfies the behavior. Do not add test-only branches, weaken assertions, or broaden scope. Run the focused test until it passes, then run nearby regression tests.

## Refactor

Improve names, structure, duplication, and boundaries only while tests remain green. Refactoring must preserve observable behavior. Run the focused test after meaningful changes and the broader required suite before completion.

Repeat Red, Green, and Refactor for the next behavior. Keep cycles small enough that a failure has an obvious cause.

## Test Quality

- Prefer observable behavior over private implementation details.
- Use real collaborators when they are fast and deterministic; use fakes at owned boundaries and mocks only for meaningful interaction contracts.
- Include failure and boundary behavior proportional to risk.
- Keep tests deterministic, isolated from production systems, and understandable as examples.
- Never delete or loosen a valid regression test merely to make new code pass.
- Do not chase a coverage percentage without behavioral value.

An AI can write a test and implementation that agree but are both wrong. Validate acceptance independently for high-risk behavior through broader integration, fixtures from approved sources, manual review, or another project-specific check.

## Mixed Tasks

When the parent task uses `mixed`, apply this loop only to the stable testable core. Verify visual layout, external-system behavior, performance, accessibility, deployment, or other environment-dependent outcomes with the appropriate non-TDD checks. Do not force them into brittle unit tests.

## Completion Evidence

Report:

- behavior and test level;
- red command and why it failed;
- green command and result;
- refactoring performed;
- broader regression checks;
- untested risks or environmental gaps.

Set any project `tdd_red_verified` flag only after observing the intended red result.
