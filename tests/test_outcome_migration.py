from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
import uuid
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
        "progress": None,
        "artifact": [],
        "completed": [],
        "replace": False,
        "workflow": None,
        "expect_revision": None,
        "direct_lock": False,
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


def schema_2_state(
    *,
    status: str = "active",
    phase: str = "execute",
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "created_by": "littlepowers",
        "workflow_id": str(uuid.uuid4()),
        "revision": 4,
        "status": status,
        "objective": "Continue the complete approved product outcome",
        "phase": phase,
        "artifacts": {
            "brainstorm": "docs/littlepowers/brainstorms/legacy.md",
            "spec": None,
            "design": None,
            "plan": "docs/littlepowers/plans/legacy.md",
            "shape": None,
        },
        "current_task": "Legacy task",
        "progress": "Legacy progress",
        "handoff": None,
        "next_action": "Reconcile before continuing",
        "completed": ["Legacy planning"],
        "created_at": "2026-07-20T08:00:00Z",
        "updated_at": "2026-07-20T09:00:00Z",
    }


class OutcomeMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_legacy(self, value: dict[str, object]) -> Path:
        directory = self.root / ".littlepowers"
        directory.mkdir()
        (directory / ".gitignore").write_text("*\n", encoding="utf-8")
        path = directory / "state.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def start(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "objective": "Build the complete Outcome Lock",
            "phase": "brainstorm",
            "next_action": "Approve the contract",
            "artifact": [],
            "replace": False,
            "direct_lock": False,
        }
        values.update(overrides)
        return state_module.command_start(namespace(**values), self.root)

    def writer(
        self, state: dict[str, object], **values: object
    ) -> argparse.Namespace:
        return namespace(
            workflow=state["workflow_id"],
            expect_revision=state["revision"],
            **values,
        )

    def test_new_state_is_schema_4_protocol_1_3_and_unbound(self) -> None:
        created = self.start()

        self.assertEqual(created["schema_version"], 4)
        self.assertEqual(created["protocol_version"], "1.3")
        self.assertEqual(created["review"]["policy"]["mode"], "blocking")
        self.assertIsNone(created["review"]["gate"])
        self.assertEqual(
            set(created["artifacts"]),
            {
                "brainstorm",
                "spec",
                "design",
                "plan",
                "shape",
                "contract",
                "evidence",
            },
        )
        lock = created["outcome_lock"]
        self.assertEqual(lock["mode"], "unbound")
        self.assertEqual(lock["status"], "unbound")
        self.assertEqual(lock["scope_delta"]["status"], "reconcile_required")
        self.assertEqual(lock["plan"]["coverage"]["status"], "pending")

    def test_tracked_direct_state_has_one_inline_outcome_and_no_plan_artifact(
        self,
    ) -> None:
        created = self.start(
            phase="execute",
            direct_lock=True,
            next_action="Make the tiny change",
        )

        lock = created["outcome_lock"]
        self.assertEqual(lock["mode"], "direct")
        self.assertEqual(lock["status"], "bound")
        self.assertEqual(set(lock["contract"]["outcomes"]), {"OUT-001"})
        self.assertIsNone(lock["contract"]["artifact"])
        self.assertIsNone(lock["plan"]["artifact"])
        self.assertEqual(lock["plan"]["coverage"]["status"], "pass")
        self.assertEqual(lock["plan"]["coverage"]["mapped_active"], 1)
        self.assertEqual(lock["baseline"]["status"], "not_applicable")

    def test_direct_lock_rejects_planning_phase_or_artifacts_atomically(self) -> None:
        with self.assertRaisesRegex(state_module.StateError, "phase=execute"):
            self.start(direct_lock=True)
        self.assertFalse((self.root / ".littlepowers" / "state.json").exists())

        with self.assertRaisesRegex(state_module.StateError, "planning artifacts"):
            self.start(
                phase="execute",
                direct_lock=True,
                artifact=["plan=docs/littlepowers/plans/tiny.md"],
            )
        self.assertFalse((self.root / ".littlepowers" / "state.json").exists())

    def test_active_and_paused_schema_2_get_read_only_reconciliation_view(
        self,
    ) -> None:
        for status in ("active", "paused"):
            with self.subTest(status=status):
                legacy = schema_2_state(status=status)
                path = self.write_legacy(legacy)

                loaded = state_module.load_state(self.root)

                assert loaded is not None
                self.assertEqual(loaded["schema_version"], 4)
                self.assertEqual(loaded["protocol_version"], "1.3")
                self.assertEqual(loaded["review"]["policy"]["mode"], "blocking")
                self.assertEqual(loaded["status"], status)
                self.assertEqual(loaded["revision"], legacy["revision"])
                self.assertEqual(
                    loaded["outcome_lock"]["status"], "reconcile_required"
                )
                self.assertEqual(
                    loaded["outcome_lock"]["baseline"]["status"],
                    "reconcile_required",
                )
                self.assertEqual(json.loads(path.read_text()), legacy)

                path.parent.joinpath("state.json").unlink()
                path.parent.joinpath(".gitignore").unlink()
                path.parent.rmdir()

    def test_terminal_schema_2_remains_terminal_and_not_required(self) -> None:
        for status in ("complete", "cancelled"):
            with self.subTest(status=status):
                legacy = schema_2_state(status=status, phase="verify")
                path = self.write_legacy(legacy)

                loaded = state_module.load_state(self.root)

                assert loaded is not None
                self.assertEqual(loaded["status"], status)
                self.assertEqual(
                    loaded["outcome_lock"]["mode"], "legacy_terminal"
                )
                self.assertEqual(
                    loaded["outcome_lock"]["status"], "not_required"
                )
                self.assertEqual(json.loads(path.read_text()), legacy)

                path.parent.joinpath("state.json").unlink()
                path.parent.joinpath(".gitignore").unlink()
                path.parent.rmdir()

    def test_first_successful_mutation_archives_exact_schema_2_once(self) -> None:
        legacy = schema_2_state()
        path = self.write_legacy(legacy)
        loaded = state_module.load_state(self.root)
        assert loaded is not None

        migrated = state_module.command_checkpoint(
            self.writer(
                loaded,
                next_action="Create the Outcome Contract",
            ),
            self.root,
        )

        self.assertEqual(migrated["schema_version"], 4)
        self.assertEqual(migrated["revision"], legacy["revision"] + 1)
        self.assertEqual(json.loads(path.read_text())["schema_version"], 4)
        archives = list(
            (self.root / ".littlepowers" / "archive").glob(
                "*-pre-schema4-v2.json"
            )
        )
        self.assertEqual(len(archives), 1)
        self.assertEqual(json.loads(archives[0].read_text()), legacy)

        state_module.command_checkpoint(
            self.writer(migrated, next_action="Continue reconciliation"),
            self.root,
        )
        self.assertEqual(
            len(
                list(
                    (self.root / ".littlepowers" / "archive").glob(
                        "*-pre-schema4-v2.json"
                    )
                )
            ),
            1,
        )

    def test_rejected_legacy_mutation_writes_no_archive_or_revision(self) -> None:
        legacy = schema_2_state()
        path = self.write_legacy(legacy)
        loaded = state_module.load_state(self.root)
        assert loaded is not None

        with self.assertRaises(state_module.StateConflict):
            state_module.command_checkpoint(
                namespace(
                    workflow=loaded["workflow_id"],
                    expect_revision=999,
                    next_action="Unsafe stale write",
                ),
                self.root,
            )

        self.assertEqual(json.loads(path.read_text()), legacy)
        self.assertFalse((self.root / ".littlepowers" / "archive").exists())

    def test_schema_1_view_and_archive_are_deterministic(self) -> None:
        legacy = {
            "schema_version": 1,
            "status": "active",
            "objective": "Legacy objective",
            "phase": "execute",
            "artifacts": {
                "brainstorm": None,
                "spec": None,
                "design": None,
                "plan": "docs/littlepowers/plans/legacy.md",
            },
            "current_task": "Task 2",
            "next_action": "Continue Task 2",
            "completed": ["Task 1"],
            "updated_at": "2026-07-17T08:00:00Z",
        }
        self.write_legacy(legacy)

        first = state_module.load_state(self.root)
        second = state_module.load_state(self.root)
        assert first is not None and second is not None
        self.assertEqual(first["workflow_id"], second["workflow_id"])
        self.assertEqual(first["schema_version"], 4)
        self.assertEqual(first["outcome_lock"]["status"], "reconcile_required")

        migrated = state_module.command_checkpoint(
            self.writer(first, next_action="Reconcile the legacy outcome"),
            self.root,
        )
        self.assertEqual(migrated["revision"], 1)
        archives = list(
            (self.root / ".littlepowers" / "archive").glob(
                "*-pre-schema4-v1.json"
            )
        )
        self.assertEqual(len(archives), 1)
        self.assertEqual(json.loads(archives[0].read_text()), legacy)

    def test_unknown_future_schema_and_protocol_fail_closed(self) -> None:
        future = schema_2_state()
        future["schema_version"] = 99
        self.write_legacy(future)
        with self.assertRaisesRegex(state_module.StateError, "unsupported schema"):
            state_module.load_state(self.root)

        self.temporary_directory.cleanup()
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        state = self.start()
        path = self.root / ".littlepowers" / "state.json"
        state["protocol_version"] = "9.9"
        path.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(state_module.StateError, "protocol_version"):
            state_module.load_state(self.root)


if __name__ == "__main__":
    unittest.main()
