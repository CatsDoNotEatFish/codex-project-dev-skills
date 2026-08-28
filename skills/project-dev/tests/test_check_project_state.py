from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_project_state.py"
SPEC = importlib.util.spec_from_file_location("check_project_state", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def project_config(
    protected_paths: str = '[".env", "private/**"]',
    design_sync: str = "when_affected",
    tdd_policy: str = "risk-based",
    workflow_policy: str | None = None,
) -> str:
    workflow_line = f"workflow_policy: {workflow_policy}\n" if workflow_policy else ""
    return textwrap.dedent(
        f"""\
        ---
        schema_version: project-dev-config/v1
        project: sample-project
        project_type: greenfield
        design_document: docs/PROJECT.md
        design_sync: {design_sync}
        status_heading: Implementation Status
        changelog_heading: Change Log
        protected_paths: {protected_paths}
        test_commands: ["python -m unittest"]
        tdd_policy: {tdd_policy}
        {workflow_line.rstrip()}
        default_branch: main
        created_at: 2026-08-28
        ---

        # Project Development Contract
        """
    )


def state(
    active_task: str = "APP-001",
    status: str = "ready",
    git_branch: str = "main",
    git_remote: str = "none",
    push_policy: str = "manual",
    workflow_mode: str | None = None,
    body: str = "# Current Project State",
) -> str:
    workflow_line = f"workflow_mode: {workflow_mode}\n" if workflow_mode else ""
    return (
        "---\n"
        "schema_version: project-dev-state/v1\n"
        "project: sample-project\n"
        "stage: foundation\n"
        f"active_task: {active_task}\n"
        f"status: {status}\n"
        f"{workflow_line}"
        "last_completed: none\n"
        f"git_branch: {git_branch}\n"
        f"git_remote: {git_remote}\n"
        f"push_policy: {push_policy}\n"
        "updated_at: 2026-08-28\n"
        "---\n\n"
        f"{body}\n"
    )


def task(
    task_id: str = "APP-001",
    status: str = "ready",
    impacts: str = '["domain"]',
    test_mode: str = "tdd",
    complete: bool = False,
    red_verified: bool = False,
    design_version: str = "pending",
    workflow_mode: str | None = None,
    design_sync_required: bool | None = None,
) -> str:
    flag = "true" if complete else "false"
    red = "true" if red_verified else "false"
    evidence = "- Focused and regression checks passed." if complete else "- Pending."
    risks = "- No known residual risk." if complete else "- Pending."
    workflow_line = f"workflow_mode: {workflow_mode}\n" if workflow_mode else ""
    if design_sync_required is None:
        design_sync_line = ""
    else:
        sync_flag = "true" if design_sync_required else "false"
        design_sync_line = (
            f"design_sync_required: {sync_flag}\n"
            "design_sync_reason: Explicit task-level design impact decision\n"
        )
    return (
        "---\n"
        "schema_version: project-dev-task/v1\n"
        f"task_id: {task_id}\n"
        "stage: foundation\n"
        "title: Test task\n"
        f"status: {status}\n"
        f"{workflow_line}"
        f"branch: task/{task_id.lower()}-test-task\n"
        "base_branch: main\n"
        "depends_on: []\n"
        'design_refs: ["Implementation Status"]\n'
        'allowed_paths: ["src/", "tests/"]\n'
        'forbidden_paths: ["private/"]\n'
        f"impacts: {impacts}\n"
        f"test_mode: {test_mode}\n"
        "test_reason: Stable observable domain behavior\n"
        f"tdd_red_verified: {red}\n"
        f"{design_sync_line}"
        f"acceptance_complete: {flag}\n"
        f"checks_complete: {flag}\n"
        f"design_sync_complete: {flag}\n"
        f"design_version: {design_version}\n"
        "created_at: 2026-08-28\n"
        "updated_at: 2026-08-28\n"
        "---\n\n"
        f"# {task_id} - Test Task\n\n"
        "## Delivery Evidence\n\n"
        f"{evidence}\n\n"
        "## Remaining Risks\n\n"
        f"{risks}\n"
    )


class ProjectFixture:
    def __init__(self, initialize_git: bool = True) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs" / "ai" / "tasks").mkdir(parents=True)
        if initialize_git:
            subprocess.run(
                ["git", "init", "-b", "main", str(self.root)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        (self.root / "docs" / "ai" / "PROJECT.md").write_text(
            project_config(), encoding="utf-8"
        )
        (self.root / "docs" / "PROJECT.md").write_text(
            textwrap.dedent(
                """\
                # Project Design

                ## Implementation Status

                - Foundation in progress.

                ## Change Log
                """
            ),
            encoding="utf-8",
        )

    def write_state(self, content: str) -> None:
        (self.root / "docs" / "ai" / "STATE.md").write_text(
            content, encoding="utf-8"
        )

    def write_task(self, task_id: str, content: str) -> None:
        (self.root / "docs" / "ai" / "tasks" / f"{task_id}.md").write_text(
            content, encoding="utf-8"
        )

    def write_config(self, content: str) -> None:
        (self.root / "docs" / "ai" / "PROJECT.md").write_text(
            content, encoding="utf-8"
        )

    def add_design_record(self, version: str) -> None:
        path = self.root / "docs" / "PROJECT.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + f"\n### {version} - 2026-08-28\n\n- Test delivery.\n",
            encoding="utf-8",
        )

    def close(self) -> None:
        self.temp.cleanup()


class CheckProjectStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectFixture()

    def tearDown(self) -> None:
        self.project.close()

    @staticmethod
    def messages(findings: object) -> str:
        return "\n".join(item.message for item in findings.items)

    def test_ready_task_is_valid(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)
        self.assertEqual(0, findings.warnings)

    def test_fast_inline_work_is_recoverable_without_task_card(self) -> None:
        body = textwrap.dedent(
            """\
            # Current Project State

            ## Current Outcome

            Change the settings button label without altering behavior.

            ## Handoff

            Inspect the uncommitted UI diff and run the focused component check.
            """
        )
        self.project.write_state(
            state(
                active_task="inline",
                status="in_progress",
                workflow_mode="fast",
                body=body,
            )
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)
        self.assertEqual(0, findings.warnings)

    def test_fast_inline_work_requires_recovery_summary(self) -> None:
        self.project.write_state(
            state(
                active_task="inline",
                status="in_progress",
                workflow_mode="fast",
            )
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("Current Outcome", self.messages(findings))
        self.assertIn("Handoff", self.messages(findings))

    def test_inline_work_must_use_fast_mode(self) -> None:
        body = textwrap.dedent(
            """\
            # Current Project State

            ## Current Outcome

            Make one low-risk copy change.

            ## Handoff

            Inspect the current diff.
            """
        )
        self.project.write_state(
            state(
                active_task="inline",
                status="in_progress",
                workflow_mode="standard",
                body=body,
            )
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("inline work requires workflow_mode fast", self.messages(findings))

    def test_project_standard_policy_forbids_fast_inline_work(self) -> None:
        self.project.write_config(project_config(workflow_policy="standard"))
        body = textwrap.dedent(
            """\
            # Current Project State

            ## Current Outcome

            Make one low-risk copy change.

            ## Handoff

            Inspect the current diff.
            """
        )
        self.project.write_state(
            state(
                active_task="inline",
                status="in_progress",
                workflow_mode="fast",
                body=body,
            )
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("workflow_policy forbids fast mode", self.messages(findings))

    def test_state_and_task_status_mismatch_fails(self) -> None:
        self.project.write_state(
            state(status="in_progress", git_branch="task/app-001-test-task")
        )
        self.project.write_task("APP-001", task(status="ready"))

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("status mismatch", self.messages(findings))

    def test_two_active_tasks_fail(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())
        self.project.write_task("APP-002", task(task_id="APP-002"))

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("exactly one active card", self.messages(findings))

    def test_planned_task_may_depend_on_active_task(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())
        future = task(task_id="APP-002", status="planned").replace(
            "depends_on: []", 'depends_on: ["APP-001"]'
        )
        self.project.write_task("APP-002", future)

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)

    def test_done_governed_task_with_tdd_evidence_is_valid(self) -> None:
        self.project.write_state(state(active_task="none", status="idle"))
        self.project.write_task(
            "APP-001",
            task(
                status="done",
                complete=True,
                red_verified=True,
                design_version="0.2.0",
            ),
        )
        self.project.add_design_record("0.2.0")

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)

    def test_explicit_no_design_change_avoids_document_churn(self) -> None:
        self.project.write_state(state(active_task="none", status="idle"))
        self.project.write_task(
            "APP-001",
            task(
                status="done",
                complete=True,
                red_verified=True,
                workflow_mode="standard",
                design_sync_required=False,
                design_version="not-required",
            ),
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)

    def test_state_and_task_workflow_modes_must_match(self) -> None:
        self.project.write_state(
            state(
                status="in_progress",
                git_branch="task/app-001-test-task",
                workflow_mode="strict",
            )
        )
        self.project.write_task(
            "APP-001",
            task(status="in_progress", workflow_mode="standard"),
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("workflow mode mismatch", self.messages(findings))

    def test_done_tdd_task_without_red_evidence_fails(self) -> None:
        self.project.write_state(state(active_task="none", status="idle"))
        self.project.write_task(
            "APP-001",
            task(status="done", complete=True, design_version="0.2.0"),
        )
        self.project.add_design_record("0.2.0")

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("tdd_red_verified", self.messages(findings))

    def test_done_task_without_delivery_evidence_fails(self) -> None:
        self.project.write_state(state(active_task="none", status="idle"))
        self.project.write_task("APP-001", task(status="done"))

        findings = MODULE.validate_project(self.project.root)

        messages = self.messages(findings)
        self.assertIn("acceptance_complete", messages)
        self.assertIn("Delivery Evidence", messages)

    def test_non_git_project_fails(self) -> None:
        self.project.close()
        self.project = ProjectFixture(initialize_git=False)
        self.project.write_state(state())
        self.project.write_task("APP-001", task())

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("not a Git repository", self.messages(findings))

    def test_project_defined_protected_path_fails_when_tracked(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())
        protected = self.project.root / "private" / "customers.json"
        protected.parent.mkdir()
        protected.write_text("sensitive", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(self.project.root), "add", "private/customers.json"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("protected paths are tracked", self.messages(findings))

    def test_env_example_may_be_tracked(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())
        example = self.project.root / ".env.example"
        example.write_text("APP_PORT=8000\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(self.project.root), "add", ".env.example"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertEqual(0, findings.errors)

    def test_after_merge_without_remote_fails(self) -> None:
        self.project.write_state(state(push_policy="after_merge"))
        self.project.write_task("APP-001", task())

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("after_merge requires", self.messages(findings))

    def test_executable_task_cannot_skip_behavior_tests(self) -> None:
        self.project.write_state(state())
        self.project.write_task(
            "APP-001", task(test_mode="none", impacts='["api"]')
        )

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("executable impacts cannot use", self.messages(findings))

    def test_project_can_disable_tdd(self) -> None:
        self.project.write_config(project_config(tdd_policy="disabled"))
        self.project.write_state(state())
        self.project.write_task("APP-001", task(test_mode="tdd"))

        findings = MODULE.validate_project(self.project.root)

        self.assertIn("tdd_policy disables", self.messages(findings))

    def test_greenfield_baseline_can_be_committed_without_secret(self) -> None:
        self.project.write_state(state())
        self.project.write_task("APP-001", task())
        (self.project.root / ".gitignore").write_text(
            ".env\nprivate/\n", encoding="utf-8"
        )
        (self.project.root / ".env").write_text(
            "API_TOKEN=secret\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "-C", str(self.project.root), "add", "."],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        findings = MODULE.validate_project(self.project.root)
        self.assertEqual(0, findings.errors)

        subprocess.run(
            [
                "git",
                "-C",
                str(self.project.root),
                "-c",
                "user.name=Skill Test",
                "-c",
                "user.email=skill-test@example.invalid",
                "commit",
                "-m",
                "chore(init): establish project development baseline",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        tracked = subprocess.run(
            ["git", "-C", str(self.project.root), "ls-files"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()

        self.assertIn("docs/ai/PROJECT.md", tracked)
        self.assertIn("docs/ai/STATE.md", tracked)
        self.assertNotIn(".env", tracked)


if __name__ == "__main__":
    unittest.main()
