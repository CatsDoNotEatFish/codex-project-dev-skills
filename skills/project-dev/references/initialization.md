# Project Initialization

Read this reference only when `docs/ai/PROJECT.md` or `docs/ai/STATE.md` is missing, or when the user asks to initialize or adopt a project.

## Classify The Starting Point

Use a read-only inventory before creating files.

### Greenfield

The root is empty or contains only notes without meaningful implementation.

1. Convert the user's product brief into users, first useful outcome, scope, non-goals, core workflows, data sensitivity, platform constraints, and acceptance signals.
2. Ask only for decisions that materially change product direction or create expensive rework. Record reversible choices as explicit assumptions.
3. Create or carefully extend `AGENTS.md` from the template. Project invariants belong there; generic engineering advice does not.
4. Create the configured design document from `assets/design-template.md`. Keep it proportional to the product and label unconfirmed assumptions.
5. Create `docs/ai/PROJECT.md`, `STATE.md`, and `tasks/INIT-001.md` from their templates.
6. Make `INIT-001` a design-confirmation task. Do not implement broad product features until pivotal assumptions are resolved.
7. Initialize Git and create the safe baseline described in the Git workflow.

Replace every template identifier, path, heading, and date with observed project facts before validation. Never leave template sentinel values in an initialized repository.

The initial design is a decision aid, not a claim that the system exists. Prefer a small vertical first release over a complete speculative architecture.

### Existing Code Without A Trustworthy Baseline

1. Inventory source, tests, manifests, migrations, entry points, runtime configuration, scripts, and existing Git history.
2. Run only safe discovery commands and existing non-destructive checks. Do not start services that mutate external systems merely to inspect the project.
3. Describe the current implementation as-is. Separate observed facts from inferred intent and future proposals.
4. Identify sensitive paths, generated artifacts, databases, credentials, deployment targets, and irreversible operations.
5. Generate the project contract, design baseline, state, and a bounded reconciliation task.
6. Preserve existing branch, commit, formatting, testing, and documentation conventions unless they are unsafe or internally inconsistent.
7. Do not label roadmap items complete because adjacent scaffolding exists.

### Existing Governed Project

Read and preserve its local conventions. Add only the missing coordination files or fields. Configure `design_document`, headings, protected paths, default branch, and test commands to match the repository instead of renaming established artifacts.

## Project Contract Fields

`docs/ai/PROJECT.md` uses flat YAML-like frontmatter with one-line JSON arrays.

- `project`: stable project identifier, shared with `STATE.md`.
- `project_type`: `greenfield`, `existing`, or `governed`.
- `design_document`: relative path to the durable design baseline.
- `design_sync`: `always`, `when_affected`, or `disabled`.
- `status_heading`: heading text that records current implementation status.
- `changelog_heading`: heading text that records design changes.
- `protected_paths`: project-relative files or glob patterns that Git must not track.
- `test_commands`: trusted default verification commands; tasks may add narrower checks.
- `tdd_policy`: normally `risk-based`; `required` or `disabled` only when the project explicitly chooses it.
- `default_branch`: actual integration branch, usually `main`.

If design sync is disabled, record why in the contract body. The status and change-log headings may be `none`, but the configured design document must still exist as a minimal durable baseline.

## Baseline Quality Gate

Before the first commit:

- project identity matches between contract and state;
- design path and configured headings exist;
- protected and generated files are ignored and untracked;
- initial task scope, test mode, and acceptance are explicit;
- the state checker passes;
- the staged file list and diff contain only intentional non-sensitive content.
