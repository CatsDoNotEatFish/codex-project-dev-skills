# Risk-Based Testing Strategy

Read this reference when executable behavior changes. Choose the smallest test approach that can credibly detect the relevant failure.

## Select `test_mode`

- `tdd`: stable deterministic rules, reproducible defects, authorization/privacy/financial/data-integrity invariants, or known API contracts with a fast reliable harness.
- `mixed`: a testable core plus browser, visual, database, performance, device, or external-system verification.
- `test-after`: behavior is understood but meaningful verification requires an assembled system or real framework lifecycle.
- `exploratory`: a time-bounded feasibility or interface question is genuinely unknown. A spike is not production completion.
- `none`: no executable behavior changed. Still use relevant linting, rendering, link checks, or inspection.

Prefer `tdd` or `mixed` only when the behavior can be expressed as an observable example, the test can fail for that behavior, the harness is deterministic, the requirement is stable, and regression cost justifies maintaining the test.

## Match Cost To Workflow

- Fast: run one focused check or direct inspection. Use a regression test for a bug when cheap; do not load the full TDD workflow for trivial presentation changes.
- Standard: run focused tests during implementation and one broader affected suite at completion when shared behavior changed.
- Strict: run focused, integration, migration/rollback, security, or full-suite checks proportional to the actual risk.

Do not rerun the same passing command when relevant inputs have not changed. Do not execute the full suite after every Red-Green cycle; run it once after the coherent implementation or refactor is complete.

## AI-Specific Evidence

An AI-generated test and implementation can agree while both misunderstand the requirement. Derive examples from project rules and user outcomes. For TDD, observe failure for the intended missing behavior rather than syntax or setup, never weaken assertions to pass, and use independent acceptance evidence for high-risk behavior.

Set `tdd_red_verified: true` only after observing the intended Red result. For `mixed`, it applies only to the test-first portion.
