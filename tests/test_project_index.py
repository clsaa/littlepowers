from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import littlepowers_state as state_module  # noqa: E402


def namespace(**values: object) -> argparse.Namespace:
    return argparse.Namespace(**values)


@unittest.skipUnless(shutil.which("git"), "Git is required for worktree tests")
class ProjectIndexFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary_directory.name)
        self.manager = self.base / "manager"
        self.member = self.base / "member"
        self._init_repository(self.manager)
        self._git(
            "worktree",
            "add",
            "-q",
            "-b",
            "feature/member",
            str(self.member),
            cwd=self.manager,
        )
        self.manager_state = self._start(self.manager, "Manage parallel work")
        self.member_state = self._start(self.member, "Implement member change")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _git(self, *arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(cwd), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )

    def _init_repository(self, root: Path) -> None:
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(root)],
            check=True,
            capture_output=True,
        )
        (root / "tracked.txt").write_text("base\n", encoding="utf-8")
        self._git("add", "tracked.txt", cwd=root)
        self._git(
            "-c",
            "user.name=Littlepowers Test",
            "-c",
            "user.email=littlepowers@example.invalid",
            "commit",
            "-q",
            "-m",
            "base",
            cwd=root,
        )

    def _start(self, root: Path, objective: str) -> dict[str, object]:
        return state_module.command_start(
            namespace(
                objective=objective,
                phase="execute",
                next_action="Continue",
                artifact=[],
                replace=False,
                workflow=None,
                expect_revision=None,
                direct_lock=True,
                review_policy="blocking",
                review_through=None,
                review_wait_seconds=None,
            ),
            root,
        )

    def register(
        self, member: Path | None = None, *, label: str | None = "member"
    ) -> dict[str, object]:
        return state_module.command_project_register(
            namespace(
                member_root=str(member or self.member),
                label=label,
            ),
            self.manager,
        )

    def unregister(self, member: Path | None = None) -> dict[str, object]:
        return state_module.command_project_unregister(
            namespace(member_root=str(member or self.member)),
            self.manager,
        )

    def checkpoint(
        self,
        root: Path,
        state: dict[str, object],
        *,
        progress: str,
        next_action: str,
    ) -> dict[str, object]:
        return state_module.command_checkpoint(
            namespace(
                workflow=state["workflow_id"],
                expect_revision=state["revision"],
                objective=None,
                phase=None,
                next_action=next_action,
                current_task=None,
                progress=progress,
                artifact=[],
                completed=[],
            ),
            root,
        )


class ProjectIndexMutationTests(ProjectIndexFixture):
    def test_register_and_unregister_preserve_both_ledgers(self) -> None:
        manager_path = state_module.state_path(self.manager)
        member_path = state_module.state_path(self.member)
        manager_before = manager_path.read_bytes()
        member_before = member_path.read_bytes()

        registered = self.register()

        self.assertEqual(registered["revision"], 1)
        self.assertEqual(
            registered["members"],
            [
                {
                    "root": str(self.member.resolve()),
                    "label": "member",
                    "registered_at": registered["updated_at"],
                }
            ],
        )
        self.assertEqual(manager_path.read_bytes(), manager_before)
        self.assertEqual(member_path.read_bytes(), member_before)
        self.assertEqual(
            state_module.load_state(self.manager)["revision"],
            self.manager_state["revision"],
        )

        unregistered = self.unregister()

        self.assertEqual(unregistered["revision"], 2)
        self.assertEqual(unregistered["members"], [])
        self.assertEqual(manager_path.read_bytes(), manager_before)
        self.assertEqual(member_path.read_bytes(), member_before)

    def test_duplicate_self_and_foreign_roots_fail_without_mutation(self) -> None:
        self.register()
        index_path = state_module.project_index_path(self.manager)
        before = index_path.read_bytes()

        with self.assertRaisesRegex(state_module.StateError, "already registered"):
            self.register()
        with self.assertRaisesRegex(state_module.StateError, "differ from"):
            self.register(self.manager)

        foreign = self.base / "foreign"
        self._init_repository(foreign)
        with self.assertRaisesRegex(state_module.StateError, "manager's Git repository"):
            self.register(foreign)

        self.assertEqual(index_path.read_bytes(), before)

    def test_linked_member_root_is_rejected_without_mutation(self) -> None:
        linked_member = self.base / "linked-member"
        try:
            linked_member.symlink_to(self.member, target_is_directory=True)
        except OSError:
            self.skipTest("directory symlinks are unavailable")

        with self.assertRaisesRegex(state_module.StateError, "non-linked directory"):
            self.register(linked_member)

        self.assertFalse(state_module.project_index_path(self.manager).exists())

    def test_member_limit_is_bounded(self) -> None:
        second = self.base / "second"
        self._git(
            "worktree",
            "add",
            "-q",
            "-b",
            "feature/second",
            str(second),
            cwd=self.manager,
        )
        with mock.patch.object(state_module, "MAX_PROJECT_MEMBERS", 1):
            self.register()
            with self.assertRaisesRegex(state_module.StateError, "already has 1"):
                self.register(second, label="second")

    def test_labels_are_optional_single_line_and_bounded(self) -> None:
        registered = self.register(label=None)
        self.assertIsNone(registered["members"][0]["label"])
        self.unregister()

        with self.assertRaisesRegex(state_module.StateError, "one line"):
            self.register(label="line one\nline two")
        with self.assertRaisesRegex(state_module.StateError, "exceeds"):
            self.register(label="x" * (state_module.MAX_PROJECT_LABEL_LENGTH + 1))

    def test_missing_worktree_can_be_explicitly_unregistered(self) -> None:
        self.register()
        canonical_member = self.member.resolve()
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)

        result = self.unregister(canonical_member)

        self.assertEqual(result["members"], [])
        self.assertEqual(result["revision"], 2)

    def test_replaced_member_symlink_can_be_unregistered_by_stored_path(self) -> None:
        self.register()
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)
        replacement = self.base / "replacement"
        replacement.mkdir()
        try:
            self.member.symlink_to(replacement, target_is_directory=True)
        except OSError:
            self.skipTest("directory symlinks are unavailable")

        result = self.unregister(self.member)

        self.assertEqual(result["members"], [])
        self.assertEqual(result["revision"], 2)

    def test_replaced_member_symlink_does_not_unregister_its_registered_target(
        self,
    ) -> None:
        second = self.base / "second"
        self._git(
            "worktree",
            "add",
            "-q",
            "-b",
            "feature/second",
            str(second),
            cwd=self.manager,
        )
        self.register(second, label="second")
        self.register(self.member, label="stale")
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)
        try:
            self.member.symlink_to(second, target_is_directory=True)
        except OSError:
            self.skipTest("directory symlinks are unavailable")

        result = self.unregister(self.member)

        self.assertEqual(
            [entry["root"] for entry in result["members"]],
            [str(second.resolve())],
        )
        self.assertEqual(result["revision"], 3)

    def test_tracked_index_is_rejected(self) -> None:
        self.register()
        self._git(
            "add",
            "-f",
            ".littlepowers/project-index.json",
            cwd=self.manager,
        )

        with self.assertRaisesRegex(state_module.StateError, "Git-tracked"):
            state_module.load_project_index(self.manager)

    def test_index_validator_rejects_unknown_keys_and_duplicate_roots(self) -> None:
        index = self.register()
        unknown = json.loads(json.dumps(index))
        unknown["unexpected"] = True
        with self.assertRaisesRegex(state_module.StateError, "unknown or missing"):
            state_module.validate_project_index(unknown)

        duplicate = json.loads(json.dumps(index))
        duplicate["members"].append(dict(duplicate["members"][0]))
        with self.assertRaisesRegex(state_module.StateError, "must be unique"):
            state_module.validate_project_index(duplicate)

    def test_parser_exposes_explicit_membership_commands(self) -> None:
        parser = state_module.build_parser()
        registered = parser.parse_args(
            [
                "--root",
                str(self.manager),
                "project-register",
                "--member-root",
                str(self.member),
                "--label",
                "member",
            ]
        )
        unregistered = parser.parse_args(
            [
                "--root",
                str(self.manager),
                "project-unregister",
                "--member-root",
                str(self.member),
            ]
        )

        self.assertEqual(registered.command, "project-register")
        self.assertEqual(unregistered.command, "project-unregister")


class ProjectIndexStatusTests(ProjectIndexFixture):
    def test_status_refreshes_primary_and_registered_workflows(self) -> None:
        self.register(label="search")
        self.member_state = self.checkpoint(
            self.member,
            self.member_state,
            progress="Search contract: 2/3 checks pass",
            next_action="Run the final search check",
        )

        result = state_module.command_project_status(self.manager)

        self.assertEqual(result["index_revision"], 1)
        self.assertEqual(result["registered_members"], 1)
        self.assertEqual(len(result["worktrees"]), 2)
        primary, member = result["worktrees"]
        self.assertEqual(primary["role"], "primary")
        self.assertEqual(primary["branch"], "main")
        self.assertEqual(primary["availability"], "ok")
        self.assertEqual(
            primary["ledger"]["workflow_id"], self.manager_state["workflow_id"]
        )
        self.assertEqual(member["label"], "search")
        self.assertEqual(member["branch"], "feature/member")
        self.assertEqual(member["availability"], "ok")
        self.assertEqual(
            member["ledger"]["progress"], "Search contract: 2/3 checks pass"
        )
        self.assertEqual(member["ledger"]["review"]["state"], "no_gate")

    def test_status_without_index_reads_primary_and_creates_nothing(self) -> None:
        index_path = state_module.project_index_path(self.manager)
        self.assertFalse(index_path.exists())

        result = state_module.command_project_status(self.manager)

        self.assertIsNone(result["index_revision"])
        self.assertEqual(result["registered_members"], 0)
        self.assertEqual(len(result["worktrees"]), 1)
        self.assertEqual(result["worktrees"][0]["availability"], "ok")
        self.assertFalse(index_path.exists())

    def test_member_without_ledger_is_reported_without_error(self) -> None:
        no_ledger = self.base / "no-ledger"
        self._git(
            "worktree",
            "add",
            "-q",
            "-b",
            "feature/no-ledger",
            str(no_ledger),
            cwd=self.manager,
        )
        self.register(no_ledger, label="no-ledger")

        result = state_module.command_project_status(self.manager)
        row = result["worktrees"][1]

        self.assertEqual(row["availability"], "no_ledger")
        self.assertIsNone(row["ledger"])
        self.assertIsNone(row["error"])

    def test_missing_member_error_is_isolated_and_does_not_prune(self) -> None:
        self.register()
        index_path = state_module.project_index_path(self.manager)
        manager_path = state_module.state_path(self.manager)
        index_before = index_path.read_bytes()
        manager_before = manager_path.read_bytes()
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)

        result = state_module.command_project_status(self.manager)

        self.assertEqual(result["worktrees"][0]["availability"], "ok")
        broken = result["worktrees"][1]
        self.assertEqual(broken["availability"], "error")
        self.assertIn("cannot resolve", broken["error"])
        self.assertEqual(result["registered_members"], 1)
        self.assertEqual(index_path.read_bytes(), index_before)
        self.assertEqual(manager_path.read_bytes(), manager_before)

    def test_invalid_member_ledger_is_isolated_and_status_is_read_only(self) -> None:
        self.register()
        index_path = state_module.project_index_path(self.manager)
        manager_path = state_module.state_path(self.manager)
        member_path = state_module.state_path(self.member)
        member_path.write_text("{not-json}\n", encoding="utf-8")
        index_before = index_path.read_bytes()
        manager_before = manager_path.read_bytes()
        member_before = member_path.read_bytes()

        result = state_module.command_project_status(self.manager)

        self.assertEqual(result["worktrees"][0]["availability"], "ok")
        broken = result["worktrees"][1]
        self.assertEqual(broken["availability"], "error")
        self.assertIn("cannot read", broken["error"])
        self.assertEqual(index_path.read_bytes(), index_before)
        self.assertEqual(manager_path.read_bytes(), manager_before)
        self.assertEqual(member_path.read_bytes(), member_before)

    def test_foreign_replacement_is_reported_without_index_mutation(self) -> None:
        self.register()
        canonical_member = self.member.resolve()
        index_path = state_module.project_index_path(self.manager)
        index_before = index_path.read_bytes()
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)
        self._init_repository(canonical_member)

        result = state_module.command_project_status(self.manager)
        broken = result["worktrees"][1]

        self.assertEqual(broken["availability"], "error")
        self.assertIn("no longer a worktree", broken["error"])
        self.assertEqual(index_path.read_bytes(), index_before)

    def test_member_path_inspection_error_is_isolated(self) -> None:
        self.register()
        original_inspection = state_module._is_link_or_reparse

        def inspect(path: Path) -> bool:
            if path == self.member.resolve():
                raise PermissionError("permission denied")
            return original_inspection(path)

        with mock.patch.object(
            state_module, "_is_link_or_reparse", side_effect=inspect
        ):
            result = state_module.command_project_status(self.manager)

        self.assertEqual(result["worktrees"][0]["availability"], "ok")
        broken = result["worktrees"][1]
        self.assertEqual(broken["availability"], "error")
        self.assertIn("cannot inspect member worktree", broken["error"])

    def test_json_and_text_output_are_stable_and_concise(self) -> None:
        self.register(label="search")
        result = state_module.command_project_status(self.manager)

        json_output = io.StringIO()
        with redirect_stdout(json_output):
            state_module.print_project_status(result, as_json=True)
        decoded = json.loads(json_output.getvalue())
        self.assertEqual(decoded["registered_members"], 1)
        self.assertEqual(decoded["worktrees"][1]["label"], "search")

        text_output = io.StringIO()
        with redirect_stdout(text_output):
            state_module.print_project_status(result, as_json=False)
        rendered = text_output.getvalue()
        self.assertIn("project index revision: 1", rendered)
        self.assertIn("[primary] primary", rendered)
        self.assertIn("[member] search", rendered)
        self.assertIn("active/execute", rendered)

    def test_parser_exposes_read_only_status_command(self) -> None:
        args = state_module.build_parser().parse_args(
            ["--root", str(self.manager), "project-status", "--json"]
        )
        self.assertEqual(args.command, "project-status")
        self.assertTrue(args.json)

    def test_doctor_validates_index_without_visiting_members(self) -> None:
        self.register()
        self._git("worktree", "remove", "--force", str(self.member), cwd=self.manager)
        output = io.StringIO()

        with redirect_stdout(output):
            healthy = state_module.command_doctor(self.manager)

        self.assertTrue(healthy)
        self.assertIn("project index: schema 1, revision 1, members 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
