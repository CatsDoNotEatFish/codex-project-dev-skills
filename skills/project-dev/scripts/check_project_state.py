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
EXECUTABLE_IMPACTS = IMPACTS - {"documentation", "delivery_status", "none"}
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


def matches_protected_pattern(path: str, pattern: str) -> bool:
    normalized = normalize_repo_path(path)
    if normalized.lower() == ".env.example":
        return False
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

    if data["schema_version"] != "project-dev-task/v1":
        findings.error(f"{label}: unsupported schema_version {data['schema_version']!r}")

    task_id = str(data["task_id"])
    if path.stem != task_id:
        findings.error(f"{label}: filename must be {task_id}.md")

    status = str(data["status"])
    if status not in TASK_STATUSES:
        findings.error(f"{label}: invalid status {status!r}")

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

        governed = bool(impacts) and impacts != ["none"]
        sync_needed = config["design_sync"] == "always" or (
            config["design_sync"] == "when_affected" and governed
        )
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
        state, _ = read_frontmatter(state_path)
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

    active_task = str(state["active_task"])
    if active_task == "none":
        if state_status != "idle":
            findings.error("docs/ai/STATE.md: active_task none requires status idle")
        if active_cards:
            findings.error(
                "docs/ai/STATE.md: active_task none conflicts with active cards: "
                + ", ".join(active_cards)
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

    if not task_paths:
        findings.warn("no task cards found under docs/ai/tasks")

    return findings


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
    args = parser.parse_args()

    project = args.project.resolve()
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
