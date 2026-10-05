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

Verification cost follows what actually changed, not the mode name. A `strict` task that changes
no executable behavior does not earn a test run by being strict.

- Fast: run one focused check or direct inspection. Use a regression test for a bug when cheap; do not load the full TDD workflow for trivial presentation changes.
- Standard: run focused tests during implementation and one broader affected suite at completion when shared behavior changed.
- Strict: run the checks the task declares, at the depth the actual risk justifies — focused, integration, migration/rollback, or security. A release or deployment that publishes already-verified sources verifies its artifacts, provenance, and authorization rather than the unit suites again.

## Do Not Re-run Unchanged Checks

- Do not re-run the same passing command when its relevant inputs have not changed. Same inputs, same commit, same green result: a re-run cannot fail differently, so it adds cost and nothing else.
- When no executable behavior changed — documentation, version metadata, release notes, packaging, CI or release configuration, task and state files — use `test_mode: none`. Verify what did change (artifact contents and exclusions, checksums, tag provenance, links, rendering) and cite the last verified run instead of repeating it.
- For a release, the checks that can still fail after the code was verified are the artifact ones: archive contents, `SHA256SUMS.txt`, the commit a tag resolves to, and the CI status of that commit.
- Do not execute the full suite after every Red-Green cycle; run it once after the coherent implementation or refactor is complete.

## AI-Specific Evidence

An AI-generated test and implementation can agree while both misunderstand the requirement. Derive examples from project rules and user outcomes. For TDD, observe failure for the intended missing behavior rather than syntax or setup, never weaken assertions to pass, and use independent acceptance evidence for high-risk behavior.

Set `tdd_red_verified: true` only after observing the intended Red result. For `mixed`, it applies only to the test-first portion.
