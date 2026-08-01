from __future__ import annotations

import argparse
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import littlepowers_state as state_module


def writer(state: dict[str, object], **values: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "workflow": state["workflow_id"],
        "expect_revision": state["revision"],
        "objective": None,
        "phase": None,
        "next_action": None,
        "current_task": None,
        "progress": None,
        "artifact": [],
        "completed": [],
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


class ReviewStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_raw_state(self, payload: bytes) -> Path:
        store = self.root / ".littlepowers"
        store.mkdir()
        (store / ".gitignore").write_text("*\n", encoding="utf-8")
        path = store / "state.json"
        path.write_bytes(payload)
        return path

    def test_default_review_policy_is_blocking_and_exact(self) -> None:
        state = state_module.new_state("Deliver outcome", "brainstorm", "Shape it")

        self.assertEqual(state["schema_version"], 4)
        self.assertEqual(state["protocol_version"], "1.3")
        self.assertEqual(
            state["review"],
            {
                "policy": {
                    "mode": "blocking",
                    "through": "next_phase",
                    "wait_seconds": None,
                    "recorded_at": state["created_at"],
                },
                "gate": None,
                "last_resolution": None,
            },
        )
        self.assertIs(state_module.validate_state(state), state)

    def test_every_supported_policy_combination_validates(self) -> None:
        cases = (
            ("blocking", None, None, "next_phase"),
            ("implementation_mandate", None, None, "execute"),
            ("unattended", None, None, "execute"),
            ("windowed", "next_phase", 60, "next_phase"),
            ("windowed", "execute", 604800, "execute"),
        )
        for mode, through, wait, expected_through in cases:
            with self.subTest(mode=mode, through=through, wait=wait):
                review = state_module.new_review_state(
                    mode=mode,
                    through=through,
                    wait_seconds=wait,
                )
                self.assertEqual(review["policy"]["mode"], mode)
                self.assertEqual(
                    review["policy"]["through"], expected_through
                )
                self.assertEqual(review["policy"]["wait_seconds"], wait)

    def test_contradictory_or_out_of_range_policy_fails(self) -> None:
        invalid = (
            {"mode": "blocking", "through": "execute"},
            {"mode": "unattended", "through": "next_phase"},
            {"mode": "implementation_mandate", "wait_seconds": 60},
            {"mode": "windowed", "wait_seconds": None},
            {"mode": "windowed", "wait_seconds": 60},
            {"mode": "windowed", "wait_seconds": 59},
            {"mode": "windowed", "wait_seconds": 604801},
            {"mode": "windowed", "wait_seconds": True},
            {"mode": "unknown"},
        )
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(state_module.StateError):
                    state_module.new_review_state(**values)

    def test_review_record_rejects_unknown_keys_and_future_policy_time(self) -> None:
        state = state_module.new_state("Deliver outcome", "brainstorm", "Shape it")
        unknown = copy.deepcopy(state)
        unknown["review"]["extra"] = True
        with self.assertRaisesRegex(state_module.StateError, "unknown or missing"):
            state_module.validate_state(unknown)

        future = copy.deepcopy(state)
        future["review"]["policy"]["recorded_at"] = "2999-01-01T00:00:00Z"
        with self.assertRaisesRegex(state_module.StateError, "future"):
            state_module.validate_state(future)

    def test_tracked_direct_stores_policy_but_has_no_gate(self) -> None:
        state = state_module.new_state(
            "Make the fixed edit",
            "execute",
            "Apply it",
            direct_lock=True,
            review_mode="unattended",
        )

        self.assertEqual(state["review"]["policy"]["mode"], "unattended")
        self.assertIsNone(state["review"]["gate"])
        self.assertEqual(state["outcome_lock"]["mode"], "direct")
        state_module.validate_state(state)

    def test_schema_3_view_preserves_state_and_defaults_review_to_blocking(self) -> None:
        current = state_module.new_state("Legacy outcome", "brainstorm", "Continue")
        legacy = {key: value for key, value in current.items() if key != "review"}
        legacy["schema_version"] = 3
        legacy["protocol_version"] = "1.2"
        raw = (json.dumps(legacy, ensure_ascii=False, separators=(",", ":")) + "\n\n").encode(
            "utf-8"
        )
        path = self.write_raw_state(raw)

        loaded = state_module.load_state(self.root)

        assert loaded is not None
        self.assertEqual(loaded["schema_version"], 4)
        self.assertEqual(loaded["protocol_version"], "1.3")
        self.assertEqual(loaded["workflow_id"], legacy["workflow_id"])
        self.assertEqual(loaded["revision"], legacy["revision"])
        self.assertEqual(loaded["outcome_lock"], legacy["outcome_lock"])
        self.assertEqual(loaded["review"]["policy"]["mode"], "blocking")
        self.assertEqual(path.read_bytes(), raw)

    def test_first_schema_3_mutation_archives_byte_identical_input_once(self) -> None:
        current = state_module.new_state("Legacy outcome", "brainstorm", "Continue")
        legacy = {key: value for key, value in current.items() if key != "review"}
        legacy["schema_version"] = 3
        legacy["protocol_version"] = "1.2"
        raw = (
            "{\n  "
            + ",\n  ".join(
                f"{json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}"
                for key, value in reversed(list(legacy.items()))
            )
            + "\n}\n"
        ).encode("utf-8")
        self.write_raw_state(raw)
        loaded = state_module.load_state(self.root)
        assert loaded is not None

        migrated = state_module.command_checkpoint(
            writer(loaded, next_action="Continue under schema 4"),
            self.root,
        )

        self.assertEqual(migrated["schema_version"], 4)
        archives = list(
            (self.root / ".littlepowers" / "archive").glob(
                "*-pre-schema4-v3.json"
            )
        )
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_bytes(), raw)

        state_module.command_checkpoint(
            writer(migrated, next_action="Still schema 4"), self.root
        )
        self.assertEqual(
            len(
                list(
                    (self.root / ".littlepowers" / "archive").glob(
                        "*-pre-schema4-v3.json"
                    )
                )
            ),
            1,
        )

    def test_rejected_schema_3_mutation_writes_no_archive(self) -> None:
        current = state_module.new_state("Legacy outcome", "brainstorm", "Continue")
        legacy = {key: value for key, value in current.items() if key != "review"}
        legacy["schema_version"] = 3
        legacy["protocol_version"] = "1.2"
        raw = json.dumps(legacy).encode("utf-8")
        path = self.write_raw_state(raw)
        loaded = state_module.load_state(self.root)
        assert loaded is not None

        with self.assertRaises(state_module.StateConflict):
            state_module.command_checkpoint(
                writer(loaded, expect_revision=999, next_action="Stale"),
                self.root,
            )

        self.assertEqual(path.read_bytes(), raw)
        self.assertFalse((self.root / ".littlepowers" / "archive").exists())

    def test_terminal_schema_3_status_remains_terminal(self) -> None:
        current = state_module.new_state("Old work", "brainstorm", "Done")
        current["status"] = "cancelled"
        legacy = {key: value for key, value in current.items() if key != "review"}
        legacy["schema_version"] = 3
        legacy["protocol_version"] = "1.2"
        self.write_raw_state(json.dumps(legacy).encode("utf-8"))

        loaded = state_module.load_state(self.root)

        assert loaded is not None
        self.assertEqual(loaded["status"], "cancelled")
        self.assertEqual(loaded["review"]["policy"]["mode"], "blocking")
        self.assertIsNone(loaded["review"]["gate"])


if __name__ == "__main__":
    unittest.main()
