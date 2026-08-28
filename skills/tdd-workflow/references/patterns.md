# TDD Patterns

Read only the section matching the current work.

## New Behavior

Start from a caller-visible example. Prefer the public API or narrowest stable boundary. Add one behavior per cycle and let repeated examples reveal the implementation structure.

## Defect Repair

Write the smallest regression test that reproduces the reported failure. Verify that it fails on the current code for the expected reason, then fix the root cause. Add adjacent boundary cases only when they represent credible recurrence risks.

## Legacy Or Untested Code

Add characterization tests around behavior that must not change before refactoring. A characterization test may initially pass; it establishes the current baseline and is not red-step evidence for new behavior. Once the baseline is protected, add a failing test for the intended change.

If code cannot be tested without a large rewrite, introduce the smallest stable boundary under characterization coverage. Do not redesign the subsystem merely to satisfy a preferred testing style.

## External Adapter

Separate owned mapping, validation, retries, and error translation from the external client. Test owned deterministic logic first. Use contract fixtures or an approved sandbox for provider behavior; mocks must not invent an API contract.

## Database Or Migration

Use an isolated disposable database representative of production semantics. Write a test for data shape, constraints, compatibility, idempotency, or rollback behavior before the migration when the harness permits it. Do not substitute an in-memory database when its behavior materially differs.

## UI Behavior

Use TDD for deterministic state transitions, validation, formatting, and component behavior when stable. Use browser or visual verification for layout, responsive behavior, focus flow, and real interaction. A snapshot alone is weak evidence for user behavior.

## Common Failure Modes

- A red test fails because setup is broken rather than behavior is missing.
- The test passes immediately and is still reported as test-first evidence.
- Assertions mirror the implementation instead of the requirement.
- Excessive mocks freeze private structure and make refactoring costly.
- Production code contains branches used only by tests.
- The test is weakened after implementation fails.
- Only the focused test runs, hiding broader regression failures.
- TDD is forced onto exploratory or visual work where it adds no design signal.
