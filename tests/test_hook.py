from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import littlepowers_state as state_module  # noqa: E402


class SessionStartHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary_directory.name)
        self.hook = ROOT / "hooks" / "session-start.py"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_hook(self, payload: str | None = None) -> subprocess.CompletedProcess[str]:
        event = payload or json.dumps(
            {
                "cwd": str(self.workspace),
                "hook_event_name": "SessionStart",
                "source": "resume",
            }
        )
        environment = os.environ.copy()
        environment["PLUGIN_ROOT"] = str(ROOT)
        return subprocess.run(
            [sys.executable, str(self.hook)],
            input=event,
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

    def start_state(self) -> None:
        args = argparse.Namespace(
            objective="Finish the interrupted change",
            phase="execute",
            next_action="Run Task 3",
            artifact=["plan=docs/littlepowers/plans/example.md"],
            replace=False,
        )
        state_module.command_start(args, self.workspace)

    def test_hook_is_silent_without_unfinished_state(self) -> None:
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_hook_injects_valid_additional_context_for_active_state(self) -> None:
        self.start_state()

        result = self.run_hook()
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Finish the interrupted change", context)
        self.assertIn("Run Task 3", context)
        self.assertIn("docs/littlepowers/plans/example.md", context)

    def test_hook_is_silent_for_completed_state(self) -> None:
        self.start_state()
        state_module.command_finish(
            argparse.Namespace(next_action=None), self.workspace, "complete"
        )

        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_hook_fails_open_for_bad_input_or_state(self) -> None:
        bad_input = self.run_hook("not json")
        self.assertEqual(bad_input.returncode, 0)
        self.assertEqual(bad_input.stdout, "")
        self.assertIn("hook skipped", bad_input.stderr)

        state_dir = self.workspace / ".littlepowers"
        state_dir.mkdir()
        (state_dir / "state.json").write_text("{", encoding="utf-8")
        bad_state = self.run_hook()
        self.assertEqual(bad_state.returncode, 0)
        self.assertEqual(bad_state.stdout, "")
        self.assertIn("hook skipped", bad_state.stderr)

    def test_hook_refuses_a_state_file_tracked_by_git(self) -> None:
        self.start_state()
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(self.workspace)], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.workspace),
                "add",
                "-f",
                ".littlepowers/state.json",
            ],
            check=True,
        )

        result = self.run_hook()

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("refusing tracked state file", result.stderr)


if __name__ == "__main__":
    unittest.main()
