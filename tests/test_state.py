from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import littlepowers_state as state_module  # noqa: E402


def namespace(**values: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "objective": None,
        "phase": None,
        "next_action": None,
        "current_task": None,
        "artifact": [],
        "completed": [],
        "replace": False,
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


class StateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def start(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "objective": "Ship a recovery workflow",
            "phase": "brainstorm",
            "next_action": "Compare approaches",
            "artifact": [],
            "replace": False,
        }
        values.update(overrides)
        return state_module.command_start(namespace(**values), self.root)

    def test_start_creates_valid_self_ignored_state(self) -> None:
        created = self.start()

        self.assertEqual(created["status"], "active")
        self.assertEqual(created["phase"], "brainstorm")
        self.assertEqual(
            (self.root / ".littlepowers" / ".gitignore").read_text(encoding="utf-8"),
            "*\n",
        )
        persisted = json.loads(
            (self.root / ".littlepowers" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(persisted["schema_version"], 1)
        self.assertFalse(list((self.root / ".littlepowers").glob("*.tmp")))

    def test_start_refuses_to_replace_open_state_without_explicit_flag(self) -> None:
        self.start()

        with self.assertRaisesRegex(state_module.StateError, "--replace"):
            self.start(objective="Different work")

        replaced = self.start(objective="Different work", replace=True)
        self.assertEqual(replaced["objective"], "Different work")

    def test_checkpoint_updates_artifacts_and_deduplicates_completed_items(self) -> None:
        self.start()
        args = namespace(
            phase="spec",
            next_action="Write requirements",
            artifact=["brainstorm=docs/littlepowers/brainstorms/example.md"],
            completed=["brainstorm", "brainstorm"],
        )

        updated = state_module.command_checkpoint(args, self.root)

        self.assertEqual(updated["phase"], "spec")
        self.assertEqual(updated["completed"], ["brainstorm"])
        self.assertEqual(
            updated["artifacts"]["brainstorm"],
            "docs/littlepowers/brainstorms/example.md",
        )

    def test_pause_changes_recovery_policy_and_checkpoint_resumes(self) -> None:
        self.start()
        paused = state_module.command_pause(
            namespace(next_action="Wait for approval"), self.root
        )

        self.assertEqual(paused["status"], "paused")
        self.assertIn("do not resume", state_module.render_context(paused))

        resumed = state_module.command_checkpoint(
            namespace(current_task="Task 1", next_action="Implement Task 1"), self.root
        )
        self.assertEqual(resumed["status"], "active")
        self.assertIn("Preserve this objective", state_module.render_context(resumed))

    def test_complete_and_cancel_suppress_recovery_context(self) -> None:
        self.start()
        completed = state_module.command_finish(namespace(), self.root, "complete")
        self.assertEqual(completed["status"], "complete")
        self.assertEqual(state_module.render_context(completed), "")

        self.start(objective="Replacement after completion")
        cancelled = state_module.command_finish(namespace(), self.root, "cancelled")
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(state_module.render_context(cancelled), "")

    def test_invalid_artifact_and_malformed_state_are_rejected(self) -> None:
        with self.assertRaisesRegex(state_module.StateError, "KEY=PATH"):
            state_module.parse_artifacts(["unknown=somewhere"])

        directory = self.root / ".littlepowers"
        directory.mkdir()
        (directory / "state.json").write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(state_module.StateError, "cannot read"):
            state_module.load_state(self.root)

    def test_discover_root_honors_explicit_root(self) -> None:
        nested = self.root / "nested"
        nested.mkdir()
        self.assertEqual(
            state_module.discover_root(start=nested, explicit=self.root),
            self.root.resolve(),
        )


if __name__ == "__main__":
    unittest.main()

