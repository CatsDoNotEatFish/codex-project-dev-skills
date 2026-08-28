# Risk-Based Testing Strategy

Read this reference while planning any task that changes executable behavior or fixes a defect. Choose the smallest test approach that gives credible evidence.

## Select `test_mode`

### `tdd`

Use test-first development when most of the task has stable, observable behavior and a practical automated harness. It is especially valuable for:

- deterministic domain rules, calculations, parsing, validation, state transitions, and algorithms;
- reproducible defects where a regression test can demonstrate the failure;
- authorization, privacy, financial, data-integrity, idempotency, migration, or compatibility invariants;
- API or library contracts whose inputs, outputs, and failure behavior are known;
- refactoring behavior that must remain unchanged, after characterization tests establish the baseline.

TDD may use unit, integration, contract, or component tests. It is not synonymous with mocking every dependency.

### `mixed`

Use this when one task combines a testable core with work better verified another way. Apply TDD to deterministic rules or contracts, then use integration, end-to-end, visual, accessibility, performance, or manual checks for the rest.

Common examples are a UI feature backed by domain logic, an external adapter with a pure mapping core, or a database workflow with both transformation rules and environment-specific migration checks.

### `test-after`

Use this when behavior is understood but meaningful verification requires an assembled system, real framework lifecycle, browser, device, database, or external sandbox. Define acceptance first, implement a bounded slice, then add the closest reliable automated test before completion.

Do not choose this merely because writing a test first feels slower.

### `exploratory`

Use this for time-bounded discovery where the interface, feasibility, or third-party behavior is genuinely unknown. State the question and stopping condition. A spike is not production completion: discard it or convert learned behavior into a normal task with tests and design updates.

### `none`

Use only for non-executable changes such as prose, task metadata, or assets where an automated behavior test adds no signal. Still perform relevant linting, rendering, link checks, or manual inspection.

## TDD Decision Test

Prefer `tdd` or `mixed` when all are true:

1. the next behavior can be expressed as an observable example;
2. a test can fail for the missing or incorrect behavior rather than incidental setup;
3. the harness is fast and deterministic enough for short feedback loops;
4. the requirement is stable enough that the test will guide design rather than freeze speculation;
5. the behavior's regression cost justifies maintaining the test.

Choose another mode when one of these conditions genuinely fails, and record which one in `test_reason`.

## AI-Specific Evidence

An AI-generated test and implementation can agree while both misunderstand the requirement. Therefore:

- derive acceptance examples from project rules and user outcomes before coding;
- observe the red test fail for the expected behavioral reason, not a syntax or setup error;
- do not weaken assertions to make the implementation pass;
- run broader existing tests after the focused loop;
- use independent acceptance, integration, or manual evidence for high-risk behavior.

Set `tdd_red_verified: true` only after the intended red result was actually observed. For `mixed`, this flag applies to the test-first portion.
