#!/usr/bin/env python3
"""Validate project-dev coordination state without third-party packages."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ACTIVE_STATUSES = {"ready", "in_progress", "verifying", "blocked", "needs_review"}
TASK_STATUSES = ACTIVE_STATUSES | {"planned", "done", "cancelled"}
PUSH_POLICIES = {"manual", "after_merge", "disabled"}
PROJECT_TYPES = {"greenfield", "existing", "governed"}
DESIGN_SYNC_MODES = {"always", "when_affected", "disabled"}
TDD_POLICIES = {"risk-based", "required", "disabled"}
TEST_MODES = {"tdd", "mixed", "test-after", "exploratory", "none"}
WORKFLOW_MODES = {"fast", "standard", "strict"}
WORKFLOW_POLICIES = {"adaptive", "standard", "strict"}
# `v2` adds evidence binding to completed work. It is opt-in so that v1 cards, which
# predate the requirement and remain valid, keep validating exactly as before.
TASK_SCHEMA_VERSIONS = {"project-dev-task/v1", "project-dev-task/v2"}
EVIDENCE_BOUND_SCHEMA = "project-dev-task/v2"
IMPACTS = {
    "data",
    "api",
    "domain",
    "security_privacy",
    "ui",
    "operations",
    "dependencies",
    "architecture",
    "documentation",
    "delivery_status",
    "none",
}
# Impacts whose verification needs a test harness, because they change behavior.
# `operations` is deliberately excluded: CI, packaging, and release plumbing are
# configuration, verified by a dry run, an artifact inspection, or a config check
# rather than by unit tests. Treating it as executable forced release and packaging
# tasks to declare a test mode, and therefore to re-run suites on unchanged code.
EXECUTABLE_IMPACTS = IMPACTS - {
    "documentation",
    "delivery_status",
    "operations",
    "none",
}
BASE_PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
]
REQUIRED_CONFIG_FIELDS = {
    "schema_version",
    "project",
    "project_type",
    "design_document",
    "design_sync",
    "status_heading",
    "changelog_heading",
    "protected_paths",
    "test_commands",
    "tdd_policy",
    "default_branch",
    "created_at",
}
REQUIRED_STATE_FIELDS = {
    "schema_version",
    "project",
    "stage",
    "active_task",
    "status",
    "last_completed",
    "git_branch",
    "git_remote",
    "push_policy",
    "updated_at",
}
REQUIRED_TASK_FIELDS = {
    "schema_version",
    "task_id",
    "stage",
    "title",
    "status",
    "branch",
    "base_branch",
    "depends_on",
    "design_refs",
    "allowed_paths",
    "forbidden_paths",
    "impacts",
    "test_mode",
    "test_reason",
    "tdd_red_verified",
    "acceptance_complete",
    "checks_complete",
    "design_sync_complete",
    "design_version",
    "created_at",
    "updated_at",
}


@dataclass
class Finding:
    level: str
    message: str


class Findings:
    def __init__(self) -> None:
        self.items: list[Finding] = []

    def error(self, message: str) -> None:
        self.items.append(Finding("ERROR", message))

    def warn(self, message: str) -> None:
        self.items.append(Finding("WARN", message))

    @property
    def errors(self) -> int:
        return sum(item.level == "ERROR" for item in self.items)

    @property
    def warnings(self) -> int:
        return sum(item.level == "WARN" for item in self.items)


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid one-line JSON array: {exc.msg}") from exc
        if not isinstance(parsed, list):
            raise ValueError("expected a JSON array")
        return parsed
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none"}:
        return "none"
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    data: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError(
                f"line {line_number}: use flat key/value fields and one-line JSON arrays"
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValueError(f"line {line_number}: invalid key {key!r}")
        if key in data:
            raise ValueError(f"line {line_number}: duplicate key {key!r}")
        data[key] = parse_scalar(raw_value)
    return data, "\n".join(lines[closing + 1 :]).strip()


def require_fields(
    data: dict[str, Any], required: set[str], label: str, findings: Findings
) -> None:
    missing = sorted(required - data.keys())
    if missing:
        findings.error(f"{label}: missing fields: {', '.join(missing)}")


def validate_date(value: Any, label: str, findings: Findings) -> None:
    try:
        date.fromisoformat(str(value))
    except ValueError:
        findings.error(f"{label}: expected YYYY-MM-DD, got {value!r}")


def section_body(markdown: str, heading: str) -> str | None:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)")
    match = pattern.search(markdown)
    return match.group(1).strip() if match else None


def meaningful_section(markdown: str, heading: str) -> bool:
    body = section_body(markdown, heading)
    if body is None:
        return False
    normalized = body.lower().strip()
    return bool(normalized) and normalized not in {
        "- pending.",
        "pending.",
        "- none.",
        "none.",
    }


def has_heading(markdown: str, heading: str) -> bool:
    return bool(
        re.search(rf"(?m)^#{{1,6}}\s+{re.escape(heading)}\s*$", markdown)
    )


def run_git(project: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(project), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return None


def normalize_repo_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def matches_path_pattern(path: str, pattern: str) -> bool:
    """Match a repo-relative path against a glob, an exact path, or a directory prefix.

    A directory entry keeps its trailing slash (``docs/``) or uses ``docs/**``; a bare
    name matches that exact path only. ``*`` also crosses ``/``, matching the behaviour
    of the protected-path patterns this shares.
    """
    normalized = normalize_repo_path(path)
    candidate = normalized.lower()
    rule = normalize_repo_path(pattern).lower()
    if not rule:
        return False
    if rule.endswith("/**"):
        prefix = rule[:-3].rstrip("/")
        return candidate == prefix or candidate.startswith(prefix + "/")
    if rule.endswith("/"):
        prefix = rule.rstrip("/")
        return candidate == prefix or candidate.startswith(prefix + "/")
    return fnmatch.fnmatchcase(candidate, rule)


def matches_protected_pattern(path: str, pattern: str) -> bool:
    if normalize_repo_path(path).lower() == ".env.example":
        return False
    return matches_path_pattern(path, pattern)


def validate_git(
    project: Path, protected_patterns: list[str], findings: Findings
) -> None:
    root_result = run_git(project, "rev-parse", "--show-toplevel")
    if root_result is None:
        findings.error("Git executable is unavailable")
        return
    if root_result.returncode != 0:
        findings.error("project root is not a Git repository")
        return

    try:
        git_root = Path(root_result.stdout.strip()).resolve()
    except OSError as exc:
        findings.error(f"cannot resolve Git root: {exc}")
        return
    if git_root != project.resolve():
        findings.error(f"project root must equal Git root: {git_root}")

    conflict_result = run_git(project, "diff", "--name-only", "--diff-filter=U")
    if conflict_result and conflict_result.returncode == 0:
        conflicts = [line for line in conflict_result.stdout.splitlines() if line.strip()]
        if conflicts:
            findings.error("unresolved Git conflicts: " + ", ".join(conflicts))

    tracked_result = run_git(project, "ls-files", "-z")
    if tracked_result and tracked_result.returncode == 0:
        patterns = BASE_PROTECTED_PATTERNS + protected_patterns
        protected = sorted(
            path
            for path in tracked_result.stdout.split("\0")
            if path and any(matches_protected_pattern(path, rule) for rule in patterns)
        )
        if protected:
            findings.error("protected paths are tracked by Git: " + ", ".join(protected))


def current_branch(project: Path) -> str | None:
    """The checked-out branch, or None when Git cannot answer or HEAD is detached."""
    result = run_git(project, "rev-parse", "--abbrev-ref", "HEAD")
    if result is None or result.returncode != 0:
        return None
    name = result.stdout.strip()
    return None if not name or name == "HEAD" else name


COORDINATION_PREFIX = "docs/ai/"


def changed_paths(
    project: Path, base_ref: str | None, findings: Findings
) -> list[str] | None:
    """Repo-relative paths changed against ``base_ref``, plus uncommitted and untracked.

    Returns None when there is no resolvable baseline — a fresh repository, or a base
    branch that does not exist yet — because then every file is new and the gate would
    report the whole project as out of scope. The coordination tree is always excluded:
    state, cards, and config must change on every task.
    """
    ref = base_ref or ""
    if ref:
        check = run_git(project, "rev-parse", "--verify", "--quiet", ref)
        if check is None or check.returncode != 0:
            return None
    else:
        ref = "HEAD"

    collected: set[str] = set()
    diff_result = run_git(project, "diff", "--name-only", ref)
    if diff_result is None or diff_result.returncode != 0:
        findings.warn(f"scope check: cannot diff against {ref!r}")
        return None
    collected.update(
        line.strip() for line in diff_result.stdout.splitlines() if line.strip()
    )
    untracked_result = run_git(project, "ls-files", "--others", "--exclude-standard")
    if untracked_result is not None and untracked_result.returncode == 0:
        collected.update(
            line.strip() for line in untracked_result.stdout.splitlines() if line.strip()
        )
    return sorted(
        path
        for path in collected
        if not normalize_repo_path(path).startswith(COORDINATION_PREFIX)
    )


def validate_scope(
    project: Path,
    label: str,
    base_branch: str,
    allowed: list[str],
    forbidden: list[str],
    findings: Findings,
) -> None:
    """Compare the changes actually present against the card's declared scope bounds."""
    if not allowed and not forbidden:
        return
    paths = changed_paths(project, base_branch, findings)
    if paths is None:
        return
    for path in paths:
        if any(matches_path_pattern(path, rule) for rule in forbidden):
            findings.error(f"{label}: change touches forbidden path {path}")
        elif allowed and not any(matches_path_pattern(path, rule) for rule in allowed):
            findings.warn(f"{label}: change outside allowed_paths: {path}")


COMMAND_HINT = re.compile(
    r"```"
    r"|`[^`]*\b(?:python|pytest|unittest|npm|pnpm|yarn|node|npx|git|"
    r"cargo|go|dotnet|make|tox|nox|test)\b[^`]*`",
    re.IGNORECASE,
)
FAILURE_MARKER = re.compile(
    r"\b(?:fail|failed|failing|failure|error|errors|assert|assertion|traceback|"
    r"nonzero|non-zero|exit\s*code|red)\b",
    re.IGNORECASE,
)


def has_recorded_command(text: str) -> bool:
    """True when a section shows a command rather than only a claim about one."""
    return bool(COMMAND_HINT.search(text))


def has_red_evidence(body: str) -> bool:
    """A recorded Red step: the section shows a command and a failing observation."""
    if not meaningful_section(body, "Red Evidence"):
        return False
    section = section_body(body, "Red Evidence") or ""
    return bool(has_recorded_command(section) and FAILURE_MARKER.search(section))


def safe_relative_path(project: Path, value: Any) -> Path | None:
    candidate = Path(str(value))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (project / candidate).resolve()
    try:
        resolved.relative_to(project.resolve())
    except ValueError:
        return None
    return resolved


def validate_config(
    project: Path, path: Path, findings: Findings
) -> tuple[dict[str, Any], str, str] | None:
    try:
        config, _ = read_frontmatter(path)
    except (OSError, UnicodeError, ValueError) as exc:
        findings.error(f"docs/ai/PROJECT.md: {exc}")
        return None

    require_fields(config, REQUIRED_CONFIG_FIELDS, "docs/ai/PROJECT.md", findings)
    if REQUIRED_CONFIG_FIELDS - config.keys():
        return None

    if config["schema_version"] != "project-dev-config/v1":
        findings.error(
            "docs/ai/PROJECT.md: unsupported schema_version "
            f"{config['schema_version']!r}"
        )
    if config["project_type"] not in PROJECT_TYPES:
        findings.error("docs/ai/PROJECT.md: invalid project_type")
    if config["design_sync"] not in DESIGN_SYNC_MODES:
        findings.error("docs/ai/PROJECT.md: invalid design_sync")
    if config["tdd_policy"] not in TDD_POLICIES:
        findings.error("docs/ai/PROJECT.md: invalid tdd_policy")
    workflow_policy = str(config.get("workflow_policy", "adaptive"))
    if workflow_policy not in WORKFLOW_POLICIES:
        findings.error("docs/ai/PROJECT.md: invalid workflow_policy")
    validate_date(config["created_at"], "docs/ai/PROJECT.md: created_at", findings)

    for field in ("protected_paths", "test_commands"):
        if not isinstance(config[field], list) or not all(
            isinstance(item, str) for item in config[field]
        ):
            findings.error(f"docs/ai/PROJECT.md: {field} must be a string array")

    default_branch = str(config["default_branch"])
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", default_branch):
        findings.error("docs/ai/PROJECT.md: invalid default_branch")

    design_path = safe_relative_path(project, config["design_document"])
    if design_path is None:
        findings.error("docs/ai/PROJECT.md: design_document must stay inside project root")
        return config, "", default_branch
    if not design_path.is_file():
        findings.error(f"missing configured design document: {config['design_document']}")
        return config, "", default_branch

    try:
        design_text = design_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        findings.error(f"cannot read configured design document: {exc}")
        return config, "", default_branch

    if config["design_sync"] != "disabled":
        for field in ("status_heading", "changelog_heading"):
            heading = str(config[field])
            if heading == "none" or not has_heading(design_text, heading):
                findings.error(
                    f"configured {field} heading not found in design document: {heading!r}"
                )

    return config, design_text, default_branch


def validate_task(
    path: Path,
    design_text: str,
    config: dict[str, Any],
    default_branch: str,
    findings: Findings,
) -> tuple[dict[str, Any], str] | None:
    label = path.name
    try:
        data, body = read_frontmatter(path)
    except (OSError, UnicodeError, ValueError) as exc:
        findings.error(f"{label}: {exc}")
        return None

    require_fields(data, REQUIRED_TASK_FIELDS, label, findings)
    if REQUIRED_TASK_FIELDS - data.keys():
        return data, body

    if data["schema_version"] not in TASK_SCHEMA_VERSIONS:
        findings.error(f"{label}: unsupported schema_version {data['schema_version']!r}")

    task_id = str(data["task_id"])
    if path.stem != task_id:
        findings.error(f"{label}: filename must be {task_id}.md")

    status = str(data["status"])
    if status not in TASK_STATUSES:
        findings.error(f"{label}: invalid status {status!r}")

    workflow_mode = str(data.get("workflow_mode", "standard"))
    if workflow_mode not in WORKFLOW_MODES:
        findings.error(f"{label}: invalid workflow_mode {workflow_mode!r}")
    workflow_policy = str(config.get("workflow_policy", "adaptive"))
    if workflow_policy == "strict" and workflow_mode != "strict":
        findings.error(f"{label}: project workflow_policy requires strict mode")
    if workflow_policy == "standard" and workflow_mode == "fast":
        findings.error(f"{label}: project workflow_policy forbids fast mode")

    branch = str(data["branch"])
    if not re.fullmatch(r"task/[a-z0-9][a-z0-9._/-]*", branch):
        findings.error(f"{label}: invalid task branch {branch!r}")
    if str(data["base_branch"]) != default_branch:
        findings.error(f"{label}: base_branch must be {default_branch!r}")

    array_fields = (
        "depends_on",
        "design_refs",
        "allowed_paths",
        "forbidden_paths",
        "impacts",
    )
    for field in array_fields:
        if not isinstance(data[field], list):
            findings.error(f"{label}: {field} must be a one-line JSON array")

    impacts = data["impacts"] if isinstance(data["impacts"], list) else []
    invalid_impacts = sorted(set(map(str, impacts)) - IMPACTS)
    if invalid_impacts:
        findings.error(f"{label}: invalid impacts: {', '.join(invalid_impacts)}")
    if not impacts:
        findings.error(f"{label}: impacts cannot be empty")
    if "none" in impacts and len(impacts) > 1:
        findings.error(f"{label}: impact 'none' cannot be combined with another impact")

    test_mode = str(data["test_mode"])
    if test_mode not in TEST_MODES:
        findings.error(f"{label}: invalid test_mode {test_mode!r}")
    if not str(data["test_reason"]).strip():
        findings.error(f"{label}: test_reason cannot be empty")
    if test_mode == "none" and set(map(str, impacts)) & EXECUTABLE_IMPACTS:
        findings.error(f"{label}: executable impacts cannot use test_mode 'none'")
    if config["tdd_policy"] == "disabled" and test_mode in {"tdd", "mixed"}:
        findings.error(f"{label}: project tdd_policy disables TDD")
    if (
        config["tdd_policy"] == "required"
        and set(map(str, impacts)) & EXECUTABLE_IMPACTS
        and test_mode not in {"tdd", "mixed", "exploratory"}
    ):
        findings.error(f"{label}: project tdd_policy requires tdd or mixed mode")

    boolean_fields = (
        "tdd_red_verified",
        "acceptance_complete",
        "checks_complete",
        "design_sync_complete",
    )
    for field in boolean_fields:
        if not isinstance(data[field], bool):
            findings.error(f"{label}: {field} must be true or false")

    if "design_sync_required" in data:
        if not isinstance(data["design_sync_required"], bool):
            findings.error(f"{label}: design_sync_required must be true or false")
        if not str(data.get("design_sync_reason", "")).strip():
            findings.error(
                f"{label}: explicit design_sync_required needs design_sync_reason"
            )

    validate_date(data["created_at"], f"{label}: created_at", findings)
    validate_date(data["updated_at"], f"{label}: updated_at", findings)

    if test_mode not in {"tdd", "mixed"} and data["tdd_red_verified"] is True:
        findings.warn(f"{label}: tdd_red_verified should be false outside tdd or mixed")

    if status == "done":
        if data["acceptance_complete"] is not True:
            findings.error(f"{label}: done task requires acceptance_complete: true")
        if data["checks_complete"] is not True:
            findings.error(f"{label}: done task requires checks_complete: true")
        if test_mode in {"tdd", "mixed"} and data["tdd_red_verified"] is not True:
            findings.error(f"{label}: completed TDD work requires tdd_red_verified: true")
        if not meaningful_section(body, "Delivery Evidence"):
            findings.error(f"{label}: done task requires meaningful Delivery Evidence")
        if not meaningful_section(body, "Remaining Risks"):
            findings.error(f"{label}: done task requires a Remaining Risks assessment")

        # A boolean is a claim; these bind it to something the card actually shows.
        # Only v2 cards opt into this, so historical v1 records keep their original
        # meaning instead of being retroactively judged against a later rule.
        if data["schema_version"] == EVIDENCE_BOUND_SCHEMA:
            if data["checks_complete"] is True and not has_recorded_command(
                section_body(body, "Delivery Evidence") or ""
            ):
                findings.warn(
                    f"{label}: checks_complete is true but Delivery Evidence records "
                    "no command"
                )
            if data["tdd_red_verified"] is True and not has_red_evidence(body):
                findings.warn(
                    f"{label}: tdd_red_verified is true but no Red Evidence section "
                    "records a focused command and its failing result"
                )

        governed = bool(impacts) and impacts != ["none"]
        if config["design_sync"] == "always":
            sync_needed = True
        elif config["design_sync"] == "disabled":
            sync_needed = False
        elif "design_sync_required" in data:
            sync_needed = data["design_sync_required"] is True
        else:
            # Legacy v1 cards keep their original conservative behavior.
            sync_needed = governed
        if sync_needed:
            if data["design_sync_complete"] is not True:
                findings.error(f"{label}: task requires design_sync_complete: true")
            design_version = str(data["design_version"])
            if design_version in {"pending", "none", "not-required"}:
                findings.error(f"{label}: task requires a recorded design_version")
            elif design_version not in design_text:
                findings.error(
                    f"{label}: design_version {design_version!r} not found in design document"
                )
        elif data["design_version"] not in {"none", "not-required"}:
            findings.warn(f"{label}: design sync is not required; use not-required")

    return data, body


def validate_project(project: Path) -> Findings:
    findings = Findings()
    config_path = project / "docs" / "ai" / "PROJECT.md"
    state_path = project / "docs" / "ai" / "STATE.md"

    for label, path in {
        "docs/ai/PROJECT.md": config_path,
        "docs/ai/STATE.md": state_path,
    }.items():
        if not path.is_file():
            findings.error(f"missing required file: {label}")
    if findings.errors:
        validate_git(project, [], findings)
        return findings

    config_result = validate_config(project, config_path, findings)
    if config_result is None:
        validate_git(project, [], findings)
        return findings
    config, design_text, default_branch = config_result
    protected_patterns = (
        config["protected_paths"] if isinstance(config["protected_paths"], list) else []
    )
    validate_git(project, protected_patterns, findings)

    try:
        state, state_body = read_frontmatter(state_path)
    except (OSError, UnicodeError, ValueError) as exc:
        findings.error(f"docs/ai/STATE.md: {exc}")
        return findings

    require_fields(state, REQUIRED_STATE_FIELDS, "docs/ai/STATE.md", findings)
    if REQUIRED_STATE_FIELDS - state.keys():
        return findings

    if state["schema_version"] != "project-dev-state/v1":
        findings.error(
            f"docs/ai/STATE.md: unsupported schema_version {state['schema_version']!r}"
        )
    if str(state["project"]) != str(config["project"]):
        findings.error("project mismatch between PROJECT.md and STATE.md")

    state_status = str(state["status"])
    if state_status not in ACTIVE_STATUSES | {"idle"}:
        findings.error(f"docs/ai/STATE.md: invalid status {state_status!r}")
    validate_date(state["updated_at"], "docs/ai/STATE.md: updated_at", findings)

    active_task = str(state["active_task"])
    default_state_mode = "none" if active_task == "none" else "standard"
    state_workflow_mode = str(state.get("workflow_mode", default_state_mode))
    if state_workflow_mode not in WORKFLOW_MODES | {"none"}:
        findings.error(
            f"docs/ai/STATE.md: invalid workflow_mode {state_workflow_mode!r}"
        )

    git_branch = str(state["git_branch"])
    git_remote = str(state["git_remote"])
    push_policy = str(state["push_policy"])
    if git_branch != default_branch and not re.fullmatch(
        r"task/[a-z0-9][a-z0-9._/-]*", git_branch
    ):
        findings.error(
            f"docs/ai/STATE.md: git_branch must be {default_branch!r} or a task branch"
        )
    if not git_remote:
        findings.error("docs/ai/STATE.md: git_remote cannot be empty")
    if push_policy not in PUSH_POLICIES:
        findings.error("docs/ai/STATE.md: invalid push_policy")

    remote_result = run_git(project, "remote")
    actual_remotes = (
        set(remote_result.stdout.split())
        if remote_result and remote_result.returncode == 0
        else set()
    )
    if git_remote == "none":
        if actual_remotes:
            findings.warn(
                "docs/ai/STATE.md: git_remote is none but remotes exist: "
                + ", ".join(sorted(actual_remotes))
            )
        if push_policy == "after_merge":
            findings.error("docs/ai/STATE.md: after_merge requires a configured remote")
    elif git_remote not in actual_remotes:
        findings.error(
            f"docs/ai/STATE.md: configured remote {git_remote!r} does not exist"
        )

    task_dir = project / "docs" / "ai" / "tasks"
    task_paths = sorted(task_dir.glob("*.md")) if task_dir.is_dir() else []
    tasks: dict[str, dict[str, Any]] = {}
    active_cards: list[str] = []
    for task_path in task_paths:
        result = validate_task(
            task_path, design_text, config, default_branch, findings
        )
        if result is None:
            continue
        task, _ = result
        task_id = str(task.get("task_id", task_path.stem))
        if task_id in tasks:
            findings.error(f"duplicate task_id: {task_id}")
        tasks[task_id] = task
        if task.get("status") in ACTIVE_STATUSES:
            active_cards.append(task_id)

    for task_id, task in tasks.items():
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            continue
        for dependency in map(str, dependencies):
            if dependency not in tasks:
                findings.error(f"{task_id}: missing dependency task {dependency}")
            elif (
                task.get("status") in ACTIVE_STATUSES | {"done"}
                and tasks[dependency].get("status") != "done"
            ):
                findings.error(f"{task_id}: dependency {dependency} is not done")

    if active_task == "none":
        if state_status != "idle":
            findings.error("docs/ai/STATE.md: active_task none requires status idle")
        if state_workflow_mode != "none":
            findings.error(
                "docs/ai/STATE.md: idle state requires workflow_mode none"
            )
        if active_cards:
            findings.error(
                "docs/ai/STATE.md: active_task none conflicts with active cards: "
                + ", ".join(active_cards)
            )
    elif active_task == "inline":
        if state_status not in ACTIVE_STATUSES:
            findings.error("docs/ai/STATE.md: inline work requires an active status")
        if state_workflow_mode != "fast":
            findings.error("docs/ai/STATE.md: inline work requires workflow_mode fast")
        if str(config.get("workflow_policy", "adaptive")) != "adaptive":
            findings.error("docs/ai/STATE.md: project workflow_policy forbids fast mode")
        if active_cards:
            findings.error(
                "docs/ai/STATE.md: inline work conflicts with active cards: "
                + ", ".join(active_cards)
            )
        for heading in ("Current Outcome", "Handoff"):
            if not meaningful_section(state_body, heading):
                findings.error(
                    f"docs/ai/STATE.md: inline work requires meaningful {heading}"
                )
    else:
        if active_task not in tasks:
            findings.error(f"active task card not found: {active_task}.md")
        else:
            task_status = str(tasks[active_task].get("status"))
            if task_status != state_status:
                findings.error(
                    f"status mismatch: STATE.md={state_status}, "
                    f"{active_task}.md={task_status}"
                )
            task_branch = str(tasks[active_task].get("branch"))
            task_workflow_mode = str(
                tasks[active_task].get("workflow_mode", "standard")
            )
            if state_workflow_mode != task_workflow_mode:
                findings.error(
                    "workflow mode mismatch: "
                    f"STATE.md={state_workflow_mode}, "
                    f"{active_task}.md={task_workflow_mode}"
                )
            if state_status != "ready" and git_branch != task_branch:
                findings.error(
                    f"branch mismatch: STATE.md={git_branch}, "
                    f"{active_task}.md={task_branch}"
                )
        if active_cards != [active_task]:
            findings.error(
                "exactly one active card must match active_task; found: "
                + (", ".join(active_cards) if active_cards else "none")
            )

    # Reconcile the recorded branch with the one actually checked out. A card still
    # `ready` may name a branch that does not exist yet, so only its state comparison
    # is relaxed; STATE.md's own branch claim is always a statement of fact. An unborn
    # HEAD (fresh repository) or a detached HEAD has no branch to reconcile against.
    actual_branch = current_branch(project)
    if actual_branch is not None:
        if git_branch != actual_branch:
            message = (
                f"docs/ai/STATE.md: git_branch {git_branch!r} does not match the "
                f"checked-out branch {actual_branch!r}"
            )
            if active_task in {"none", "inline"}:
                findings.warn(message)
            else:
                findings.error(message)
        if active_task not in {"none", "inline"} and active_task in tasks:
            active_card = tasks[active_task]
            card_branch = str(active_card.get("branch"))
            if active_card.get("status") != "ready" and card_branch != actual_branch:
                findings.error(
                    f"{active_task}.md: branch {card_branch!r} does not match the "
                    f"checked-out branch {actual_branch!r}"
                )

    # Compare the changes genuinely present against the active card's declared scope.
    # This runs for a `done` card too: completion is exactly when the declared bounds
    # matter most, and a merged branch simply produces an empty diff.
    if active_task not in {"none", "inline"} and active_task in tasks:
        active_card = tasks[active_task]
        allowed_rules = active_card.get("allowed_paths")
        forbidden_rules = active_card.get("forbidden_paths")
        validate_scope(
            project,
            f"{active_task}.md",
            str(active_card.get("base_branch") or default_branch),
            [str(rule) for rule in allowed_rules]
            if isinstance(allowed_rules, list)
            else [],
            [str(rule) for rule in forbidden_rules]
            if isinstance(forbidden_rules, list)
            else [],
            findings,
        )

    if not task_paths and active_task != "inline":
        findings.warn("no task cards found under docs/ai/tasks")

    return findings


def brief(project: Path) -> str:
    """A compact orientation digest for a session that is starting fresh.

    Reads the same files through the same parsers as validation, so the digest cannot
    disagree with what the checker enforces.
    """
    out: list[str] = []
    config_result = validate_config(
        project, project / "docs" / "ai" / "PROJECT.md", Findings()
    )
    if config_result is None:
        return "cannot build brief: docs/ai/PROJECT.md is missing or invalid"
    config, _design_text, default_branch = config_result
    out.append(f"project    {config['project']}  ({config['project_type']})")
    out.append(f"design     {config['design_document']}")
    out.append(
        "policy     workflow={0} tdd={1} design_sync={2} default_branch={3}".format(
            config.get("workflow_policy", "adaptive"),
            config["tdd_policy"],
            config["design_sync"],
            default_branch,
        )
    )

    try:
        state, state_body = read_frontmatter(project / "docs" / "ai" / "STATE.md")
    except (OSError, UnicodeError, ValueError) as exc:
        out.append(f"state      unreadable: {exc}")
        return "\n".join(out)

    active_task = str(state.get("active_task", "none"))
    out.append(
        f"state      active_task={active_task} status={state.get('status')} "
        f"mode={state.get('workflow_mode', '-')} stage={state.get('stage', '-')}"
    )
    declared = str(state.get("git_branch", "?"))
    actual = current_branch(project)
    flag = "" if actual is None or actual == declared else "   <-- MISMATCH"
    out.append(f"branch     declared={declared} actual={actual or 'unknown'}{flag}")

    if active_task == "inline":
        outcome = section_body(state_body, "Current Outcome")
        if outcome:
            out.append("outcome    " + " ".join(outcome.split())[:280])
    elif active_task != "none":
        card_path = project / "docs" / "ai" / "tasks" / f"{active_task}.md"
        card: dict[str, Any] = {}
        card_body = ""
        if card_path.is_file():
            try:
                card, card_body = read_frontmatter(card_path)
            except (OSError, UnicodeError, ValueError):
                pass
        out.append(
            f"task       {active_task} [{card.get('status', 'missing')}] "
            f"{card.get('title', '')}"
        )
        out.append(
            "  delivery workflow={0} test={1} branch={2} base={3}".format(
                card.get("workflow_mode", "-"),
                card.get("test_mode", "-"),
                card.get("branch", "-"),
                card.get("base_branch", "-"),
            )
        )
        out.append(f"  scope    allowed={card.get('allowed_paths', [])}")
        out.append(f"           forbid={card.get('forbidden_paths', [])}")
        goal = section_body(card_body, "Goal")
        if goal:
            out.append("  goal     " + " ".join(goal.split())[:240])
        next_action = section_body(card_body, "Next Safe Action")
        if next_action:
            out.append("  next     " + " ".join(next_action.split())[:200])

    for heading, tag in (("Blockers", "blockers"), ("Next Tasks", "next")):
        section = section_body(state_body, heading)
        if section:
            flat = "; ".join(
                " ".join(line.split()) for line in section.splitlines() if line.strip()
            )
            out.append(f"{tag:<10} {flat[:260]}")
    baseline = section_body(state_body, "Verification Baseline")
    if baseline:
        flat = "; ".join(
            " ".join(line.split()) for line in baseline.splitlines() if line.strip()
        )
        out.append(f"{'verified':<10} {flat[:260]}")

    recent = run_git(project, "log", "--oneline", "-3")
    if recent is not None and recent.returncode == 0:
        commits = [line for line in recent.stdout.splitlines() if line.strip()]
        if commits:
            out.append("recent     " + " | ".join(commits))
    worktree = run_git(project, "status", "--porcelain")
    if worktree is not None and worktree.returncode == 0:
        dirty = [line for line in worktree.stdout.splitlines() if line.strip()]
        out.append(f"worktree   {len(dirty)} uncommitted change(s)")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate project-dev cross-session coordination state."
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current directory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as validation failures",
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Print a compact orientation digest before the findings",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    if args.brief:
        print(brief(project))
    findings = validate_project(project)
    for item in findings.items:
        print(f"[{item.level}] {item.message}")

    failed = findings.errors > 0 or (args.strict and findings.warnings > 0)
    status = "FAILED" if failed else "OK"
    print(
        f"[{status}] project={project} "
        f"errors={findings.errors} warnings={findings.warnings}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
