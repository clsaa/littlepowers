from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import littlepowers_review_runner as runner  # noqa: E402
import littlepowers_state as state_module  # noqa: E402


def namespace(**values: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "objective": None,
        "phase": None,
        "next_action": None,
        "current_task": None,
        "progress": None,
        "artifact": [],
        "completed": [],
        "replace": False,
        "workflow": None,
        "expect_revision": None,
        "direct_lock": False,
        "review_policy": "blocking",
        "review_through": None,
        "review_wait_seconds": None,
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


class ImmediateProcess:
    def __init__(self, returncode: int = 0, *, timeout: bool = False) -> None:
        self.returncode = returncode
        self.timeout = timeout
        self.killed = False

    def wait(self, timeout: int | None = None) -> int:
        if self.timeout and not self.killed:
            raise subprocess.TimeoutExpired("claude", timeout)
        return self.returncode

    def kill(self) -> None:
        self.killed = True


class ReviewRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name).resolve()
        self.session = str(uuid.uuid4())
        self.argv_log = self.root / "claude-argv.json"
        self.fake_claude = self.root / "fake-claude"
        self.fake_claude.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['LP_ARGV_LOG'], 'w', encoding='utf-8') as f:\n"
            "    json.dump(sys.argv[1:], f)\n",
            encoding="utf-8",
        )
        self.fake_claude.chmod(0o700)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def writer(state: dict[str, object], **values: object) -> argparse.Namespace:
        return namespace(
            workflow=state["workflow_id"],
            expect_revision=state["revision"],
            **values,
        )

    def create_window(self) -> dict[str, object]:
        state = state_module.command_start(
            namespace(
                objective="Review then continue the exact outcome",
                phase="brainstorm",
                next_action="Write the artifact",
                review_policy="windowed",
                review_through="execute",
                review_wait_seconds=60,
            ),
            self.root,
        )
        artifact = self.root / "docs" / "littlepowers" / "brainstorms" / "gate.md"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("# Gate\n", encoding="utf-8")
        state = state_module.command_checkpoint(
            self.writer(
                state,
                phase="spec",
                artifact=["brainstorm=docs/littlepowers/brainstorms/gate.md"],
                completed=["brainstorm"],
                next_action="Review the artifact",
            ),
            self.root,
        )
        return state_module.command_park_review(
            self.writer(
                state,
                artifact_key="brainstorm",
                scope_delta="none",
                unresolved_questions=0,
                replace=False,
            ),
            self.root,
        )

    def schedule(
        self,
        state: dict[str, object],
        *,
        spawn: object | None = None,
        session: str | None = None,
    ) -> dict[str, object]:
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        callback = spawn or (lambda _root, _workflow, _revision: 4321)
        with mock.patch.object(
            runner.shutil, "which", return_value=str(self.fake_claude)
        ):
            return runner.schedule_job(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
                session_id=session or self.session,
                spawn_child=callback,
            )

    @staticmethod
    def eligible_status(
        _root: Path, state: dict[str, object], *, gate_revision: int
    ) -> dict[str, object]:
        return {
            "workflow_id": state["workflow_id"],
            "gate_revision": gate_revision,
            "status": "eligible",
            "mode": "windowed",
            "artifact_key": "brainstorm",
            "not_before": state["review"]["gate"]["not_before"],
            "reasons": [],
        }

    def test_schedule_writes_private_content_free_metadata_and_is_idempotent(self) -> None:
        state = self.create_window()
        calls: list[tuple[Path, str, int]] = []

        def spawn(root: Path, workflow: str, revision: int) -> int:
            calls.append((root, workflow, revision))
            return 4321

        first = self.schedule(state, spawn=spawn)
        second = self.schedule(state, spawn=spawn)

        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1)
        self.assertEqual(first["status"], "armed")
        self.assertIsNone(first["pid"])
        path = (
            self.root
            / ".littlepowers"
            / "review-jobs"
            / f"{state['workflow_id']}-r{state['revision']}.json"
        )
        self.assertTrue(path.is_file())
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("# Gate", text)
        self.assertNotIn("Review then continue", text)
        self.assertNotIn("prompt", text.lower())

    def test_child_invokes_exact_session_once_without_forbidden_flags(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        commands: list[list[str]] = []

        def host_call(command: list[str], **_kwargs: object) -> ImmediateProcess:
            commands.append(command)
            return ImmediateProcess()

        with mock.patch.object(
            runner.state_module,
            "review_gate_status",
            side_effect=self.eligible_status,
        ):
            result = runner.run_job(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
                sleep=lambda _seconds: None,
                popen=host_call,
            )

        self.assertEqual(result, 0)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][0], str(self.fake_claude))
        argv = commands[0][1:]
        self.assertEqual(argv[:3], ["-p", "--resume", self.session])
        self.assertEqual(len(argv), 4)
        prompt = argv[3]
        self.assertIn(str(self.root), prompt)
        self.assertIn(str(state["workflow_id"]), prompt)
        self.assertIn(str(gate["opened_revision"]), prompt)
        joined = " ".join(argv)
        for forbidden in (
            "--continue",
            "--dangerously-skip-permissions",
            "--model",
            "--effort",
            "transcript",
        ):
            self.assertNotIn(forbidden, joined)
        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["exit_code"], 0)

    def test_concurrent_replayed_children_claim_exactly_one_host_call(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        calls: list[list[str]] = []
        calls_lock = threading.Lock()

        def host_call(
            command: list[str], **_kwargs: object
        ) -> ImmediateProcess:
            with calls_lock:
                calls.append(command)
            return ImmediateProcess()

        def replay() -> int:
            return runner.run_job(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
                sleep=lambda _seconds: None,
                popen=host_call,
            )

        with mock.patch.object(
            runner.state_module,
            "review_gate_status",
            side_effect=self.eligible_status,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _index: replay(), range(2)))

        self.assertEqual(results, [0, 0])
        self.assertEqual(len(calls), 1)
        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        self.assertEqual(status["status"], "completed")

    def test_cancelled_or_replaced_gate_exits_without_host_call(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        state_module.command_cancel_review(
            self.writer(state, reason="intervention"), self.root
        )

        result = runner.run_job(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
            sleep=lambda _seconds: None,
        )

        self.assertEqual(result, 0)
        self.assertFalse(self.argv_log.exists())
        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        self.assertEqual(status["status"], "stale")
        self.assertEqual(status["error"], "gate_no_gate")

    def test_timeout_records_bounded_failure_without_retry(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        calls = 0

        def timeout(*_args: object, **_kwargs: object) -> ImmediateProcess:
            nonlocal calls
            calls += 1
            return ImmediateProcess(timeout=True)

        with mock.patch.object(
            runner.state_module,
            "review_gate_status",
            side_effect=self.eligible_status,
        ):
            runner.run_job(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
                sleep=lambda _seconds: None,
                popen=timeout,
            )

        self.assertEqual(calls, 1)
        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["error"], "timeout")
        self.assertIsNone(status["exit_code"])
        current = state_module.load_state(self.root)
        assert current is not None
        self.assertIsNotNone(current["review"]["gate"])

    def test_cancellation_during_wait_wins_before_host_invocation(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        calls = 0

        def cancel_before_claim(_seconds: float) -> None:
            state_module.command_cancel_review(
                self.writer(state, reason="intervention"), self.root
            )

        def host_call(*_args: object, **_kwargs: object) -> ImmediateProcess:
            nonlocal calls
            calls += 1
            return ImmediateProcess()

        runner.run_job(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
            sleep=cancel_before_claim,
            popen=host_call,
        )

        self.assertEqual(calls, 0)
        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        self.assertEqual(status["status"], "stale")
        self.assertEqual(status["error"], "gate_no_gate")

    def test_initial_job_write_failure_is_atomic_and_retryable(self) -> None:
        state = self.create_window()
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        path = (
            self.root
            / ".littlepowers"
            / "review-jobs"
            / f"{state['workflow_id']}-r{gate['opened_revision']}.json"
        )

        with mock.patch.object(
            runner.state_module,
            "_write_bytes_atomic",
            side_effect=state_module.StateError("injected write failure"),
        ):
            with self.assertRaisesRegex(runner.RunnerError, "injected"):
                self.schedule(state)

        self.assertFalse(path.exists())
        scheduled = self.schedule(state)
        self.assertEqual(scheduled["status"], "armed")
        self.assertTrue(path.is_file())

    def test_job_json_rejects_duplicate_keys(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        path = (
            self.root
            / ".littlepowers"
            / "review-jobs"
            / f"{state['workflow_id']}-r{gate['opened_revision']}.json"
        )
        payload = path.read_text(encoding="utf-8").replace(
            '  "job_version": 1,',
            '  "job_version": 1,\n  "job_version": 1,',
            1,
        )
        path.write_text(payload, encoding="utf-8")
        path.chmod(0o600)

        with self.assertRaisesRegex(runner.RunnerError, "duplicate JSON key"):
            runner.job_status(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
            )

    def test_read_accepts_equivalent_path_and_handle_stat_views(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        path = (
            self.root
            / ".littlepowers"
            / "review-jobs"
            / f"{state['workflow_id']}-r{gate['opened_revision']}.json"
        )
        original_lstat = runner.state_module._entry_lstat

        def platform_path_stat(
            directory: Path, name: str, directory_fd: int | None
        ) -> os.stat_result | SimpleNamespace:
            details = original_lstat(directory, name, directory_fd)
            if directory == path.parent and name == path.name:
                values = {
                    field: getattr(details, field)
                    for field in dir(details)
                    if field.startswith("st_")
                }
                values["st_ctime_ns"] = details.st_ctime_ns + 1
                return SimpleNamespace(**values)
            return details

        with mock.patch.object(
            runner.state_module, "_entry_lstat", side_effect=platform_path_stat
        ):
            status = runner.job_status(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
            )

        self.assertEqual(status["status"], "armed")

    def test_lost_sleeper_leaves_durable_gate_and_armed_status(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)

        status = runner.job_status(
            root_text=str(self.root),
            workflow=str(state["workflow_id"]),
            gate_revision=gate["opened_revision"],
        )
        current = state_module.load_state(self.root)

        self.assertEqual(status["status"], "armed")
        assert current is not None
        self.assertEqual(
            current["review"]["gate"]["opened_revision"],
            gate["opened_revision"],
        )

    def test_read_rejects_link_and_path_replacement(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        path = (
            self.root
            / ".littlepowers"
            / "review-jobs"
            / f"{state['workflow_id']}-r{gate['opened_revision']}.json"
        )
        replacement = path.with_suffix(".replacement")
        replacement.write_bytes(path.read_bytes())
        replacement.chmod(0o600)
        original_open = os.open
        replaced = False

        def replace_after_open(
            target: object, flags: int, *args: object, **kwargs: object
        ) -> int:
            nonlocal replaced
            descriptor = original_open(target, flags, *args, **kwargs)
            if (
                (Path(target) == path or str(target) == path.name)
                and not replaced
                and not flags & getattr(os, "O_DIRECTORY", 0)
            ):
                replaced = True
                try:
                    os.replace(replacement, path)
                except OSError:
                    os.close(descriptor)
                    raise
            return descriptor

        with mock.patch.object(runner.os, "open", side_effect=replace_after_open):
            with self.assertRaisesRegex(
                runner.RunnerError, "path changed|cannot safely open"
            ):
                runner.job_status(
                    root_text=str(self.root),
                    workflow=str(state["workflow_id"]),
                    gate_revision=gate["opened_revision"],
                )

        path.unlink()
        target = path.with_suffix(".target")
        target.write_text("{}\n", encoding="utf-8")
        path.symlink_to(target.name)
        with self.assertRaisesRegex(runner.RunnerError, "regular file"):
            runner.job_status(
                root_text=str(self.root),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
            )

    @unittest.skipIf(os.name == "nt", "descriptor-relative race check is POSIX-only")
    def test_job_store_replacement_is_pinned_and_rejected(self) -> None:
        state = self.create_window()
        self.schedule(state)
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        jobs = self.root / ".littlepowers" / "review-jobs"
        moved = self.root / ".littlepowers" / "review-jobs-original"
        original_exists = runner.state_module._entry_exists
        replaced = False

        def replace_store(
            directory: Path, name: str, directory_fd: int | None
        ) -> bool:
            nonlocal replaced
            if directory == jobs and not replaced:
                replaced = True
                jobs.rename(moved)
                jobs.mkdir(mode=0o700)
            return original_exists(directory, name, directory_fd)

        with mock.patch.object(
            runner.state_module, "_entry_exists", side_effect=replace_store
        ):
            with self.assertRaisesRegex(runner.RunnerError, "store changed"):
                runner.job_status(
                    root_text=str(self.root),
                    workflow=str(state["workflow_id"]),
                    gate_revision=gate["opened_revision"],
                )

    def test_schedule_rejects_noncanonical_or_wrong_session_and_policy(self) -> None:
        state = self.create_window()
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        with self.assertRaisesRegex(runner.RunnerError, "session ID"):
            self.schedule(state, session="not-a-uuid")
        with self.assertRaisesRegex(runner.RunnerError, "canonical"):
            runner.schedule_job(
                root_text=str(self.root / ".."),
                workflow=str(state["workflow_id"]),
                gate_revision=gate["opened_revision"],
                session_id=self.session,
            )

        other_root = self.root / "other"
        other_root.mkdir()
        other = state_module.command_start(
            namespace(
                objective="Unattended work",
                phase="brainstorm",
                next_action="Write",
                review_policy="unattended",
            ),
            other_root,
        )
        artifact = other_root / "docs" / "littlepowers" / "brainstorms" / "gate.md"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("# Gate\n", encoding="utf-8")
        other = state_module.command_checkpoint(
            self.writer(
                other,
                phase="spec",
                artifact=["brainstorm=docs/littlepowers/brainstorms/gate.md"],
                completed=["brainstorm"],
            ),
            other_root,
        )
        other = state_module.command_park_review(
            self.writer(
                other,
                artifact_key="brainstorm",
                scope_delta="none",
                unresolved_questions=0,
                replace=False,
            ),
            other_root,
        )
        with self.assertRaisesRegex(runner.RunnerError, "windowed"):
            with mock.patch.object(
                runner.shutil, "which", return_value=str(self.fake_claude)
            ):
                runner.schedule_job(
                    root_text=str(other_root.resolve()),
                    workflow=str(other["workflow_id"]),
                    gate_revision=other["revision"],
                    session_id=self.session,
                )

    def test_status_without_job_is_read_only(self) -> None:
        workflow = str(uuid.uuid4())
        before = set(self.root.iterdir())

        status = runner.job_status(
            root_text=str(self.root), workflow=workflow, gate_revision=1
        )

        self.assertEqual(status["status"], "no_job")
        self.assertEqual(set(self.root.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
