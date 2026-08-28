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
) -> str:
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
) -> str:
    return textwrap.dedent(
        f"""\
        ---
        schema_version: project-dev-state/v1
        project: sample-project
        stage: foundation
        active_task: {active_task}
        status: {status}
        last_completed: none
        git_branch: {git_branch}
        git_remote: {git_remote}
        push_policy: {push_policy}
        updated_at: 2026-08-28
        ---

        # Current Project State
        """
    )


def task(
    task_id: str = "APP-001",
    status: str = "ready",
    impacts: str = '["domain"]',
    test_mode: str = "tdd",
    complete: bool = False,
    red_verified: bool = False,
    design_version: str = "pending",
) -> str:
    flag = "true" if complete else "false"
    red = "true" if red_verified else "false"
    evidence = "- Focused and regression checks passed." if complete else "- Pending."
    risks = "- No known residual risk." if complete else "- Pending."
    return textwrap.dedent(
        f"""\
        ---
        schema_version: project-dev-task/v1
        task_id: {task_id}
        stage: foundation
        title: Test task
        status: {status}
        branch: task/{task_id.lower()}-test-task
        base_branch: main
        depends_on: []
        design_refs: ["Implementation Status"]
        allowed_paths: ["src/", "tests/"]
        forbidden_paths: ["private/"]
        impacts: {impacts}
        test_mode: {test_mode}
        test_reason: Stable observable domain behavior
        tdd_red_verified: {red}
        acceptance_complete: {flag}
        checks_complete: {flag}
        design_sync_complete: {flag}
        design_version: {design_version}
        created_at: 2026-08-28
        updated_at: 2026-08-28
        ---

        # {task_id} - Test Task

        ## Delivery Evidence

        {evidence}

        ## Remaining Risks

        {risks}
        """
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
