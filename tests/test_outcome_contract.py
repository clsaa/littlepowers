from __future__ import annotations

import argparse
import hashlib
import json
import os
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
        "progress": None,
        "artifact": [],
        "completed": [],
        "replace": False,
        "workflow": None,
        "expect_revision": None,
        "direct_lock": False,
        "approval_kind": None,
        "approve_scope_delta": False,
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


def protocol_block(kind: str, value: object) -> str:
    return (
        f"<!-- littlepowers:{kind}:v1 -->\n"
        "```json\n"
        f"{json.dumps(value, ensure_ascii=False, indent=2)}\n"
        "```\n"
        f"<!-- /littlepowers:{kind} -->\n"
    )


def contract_record(
    *,
    source_path: str = "docs/product/prd.md",
    outcomes: list[dict[str, str]] | None = None,
    scope_status: str = "none",
    consequences: list[str] | None = None,
) -> dict[str, object]:
    return {
        "route": "lean",
        "sources": [
            {
                "id": "SRC-001",
                "path": source_path,
                "role": "requirements",
                "origin": "user",
                "approved": True,
            }
        ],
        "scope_delta": {
            "status": scope_status,
            "consequences": consequences or [],
        },
        "baseline": {
            "requirement": "not_applicable",
            "source_ids": [],
        },
        "review": {"code_quality_required": True},
        "outcomes": outcomes
        or [
            {
                "id": "OUT-001",
                "title": "The complete approved behavior works",
                "disposition": "active",
            }
        ],
        "fidelity": [],
    }


class OutcomeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "docs" / "product").mkdir(parents=True)
        (self.root / "docs" / "contracts").mkdir(parents=True)
        (self.root / "docs" / "product" / "prd.md").write_text(
            "Approved behavior v1\n", encoding="utf-8"
        )
        self.contract_path = (
            self.root / "docs" / "contracts" / "outcome-lock.md"
        )
        self.write_contract(contract_record())
        self.state = state_module.command_start(
            namespace(
                objective="Implement the complete approved behavior",
                phase="plan",
                next_action="Bind the approved contract",
            ),
            self.root,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_contract(self, value: dict[str, object]) -> None:
        self.contract_path.write_text(
            "# Outcome Contract\n\n" + protocol_block("contract", value),
            encoding="utf-8",
        )

    def writer(
        self, state: dict[str, object], **values: object
    ) -> argparse.Namespace:
        return namespace(
            workflow=state["workflow_id"],
            expect_revision=state["revision"],
            **values,
        )

    def bind(
        self,
        state: dict[str, object] | None = None,
        *,
        approve_scope_delta: bool = False,
    ) -> dict[str, object]:
        current = state or self.state
        return state_module.command_bind_contract(
            self.writer(
                current,
                artifact="docs/contracts/outcome-lock.md",
                approval_kind="review-gate",
                approve_scope_delta=approve_scope_delta,
            ),
            self.root,
        )

    def check(self, state: dict[str, object]) -> dict[str, object]:
        return state_module.command_check_contract(
            self.writer(state),
            self.root,
        )

    def test_bind_hashes_only_explicit_sources_and_stores_compact_summary(
        self,
    ) -> None:
        bound = self.bind()

        lock = bound["outcome_lock"]
        self.assertEqual(bound["revision"], self.state["revision"] + 1)
        self.assertEqual(lock["mode"], "artifact")
        self.assertEqual(lock["status"], "bound")
        self.assertEqual(
            lock["contract"]["artifact"], "docs/contracts/outcome-lock.md"
        )
        self.assertRegex(
            lock["contract"]["semantic_digest"], r"^sha256:[0-9a-f]{64}$"
        )
        source = lock["contract"]["sources"][0]
        expected = hashlib.sha256(b"Approved behavior v1\n").hexdigest()
        self.assertEqual(source["digest"], f"sha256:{expected}")
        self.assertEqual(set(lock["contract"]["outcomes"]), {"OUT-001"})
        self.assertEqual(lock["scope_delta"]["status"], "none")
        self.assertEqual(lock["plan"]["coverage"]["missing"], ["OUT-001"])
        self.assertEqual(lock["baseline"]["status"], "not_applicable")
        self.assertNotIn("Approved behavior v1", json.dumps(lock))

    def test_bind_rejects_missing_or_oversized_source_without_mutation(self) -> None:
        missing = contract_record(source_path="docs/product/missing.md")
        self.write_contract(missing)

        with self.assertRaisesRegex(state_module.StateError, "missing|cannot safely"):
            self.bind()

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["revision"], self.state["revision"])
        self.assertEqual(persisted["outcome_lock"]["status"], "unbound")

        oversized = self.root / "docs" / "product" / "large.bin"
        with oversized.open("wb") as stream:
            stream.truncate(state_module.MAX_BOUND_FILE_BYTES + 1)
        self.write_contract(contract_record(source_path="docs/product/large.bin"))
        with self.assertRaisesRegex(state_module.StateError, "exceeds"):
            self.bind()
        self.assertEqual(
            state_module.load_state(self.root)["revision"], self.state["revision"]
        )

    @unittest.skipIf(os.name == "nt", "POSIX link security regression")
    def test_bind_rejects_symlink_and_hard_link_sources(self) -> None:
        target = self.root / "docs" / "product" / "target.md"
        target.write_text("target\n", encoding="utf-8")
        linked = self.root / "docs" / "product" / "linked.md"
        linked.symlink_to(target)
        self.write_contract(contract_record(source_path="docs/product/linked.md"))
        with self.assertRaisesRegex(
            state_module.StateError, "linked|safely open"
        ):
            self.bind()

        linked.unlink()
        os.link(target, linked)
        with self.assertRaisesRegex(state_module.StateError, "hard-linked"):
            self.bind()
        self.assertEqual(
            state_module.load_state(self.root)["revision"], self.state["revision"]
        )

    def test_scope_delta_requires_distinct_approval_exactly_when_nonempty(
        self,
    ) -> None:
        with self.assertRaisesRegex(state_module.StateError, "no scope delta"):
            self.bind(approve_scope_delta=True)

        added = contract_record(
            outcomes=[
                {
                    "id": "OUT-001",
                    "title": "The complete approved behavior works",
                    "disposition": "active",
                },
                {
                    "id": "OUT-002",
                    "title": "A newly approved behavior works",
                    "disposition": "added",
                },
            ],
            scope_status="proposed",
            consequences=["OUT-002 expands the approved result"],
        )
        self.write_contract(added)
        with self.assertRaisesRegex(state_module.StateError, "distinct scope"):
            self.bind()

        bound = self.bind(approve_scope_delta=True)
        self.assertEqual(bound["outcome_lock"]["scope_delta"]["status"], "approved")
        self.assertEqual(
            bound["outcome_lock"]["scope_delta"]["added"], ["OUT-002"]
        )
        self.assertEqual(
            bound["outcome_lock"]["scope_delta"]["approval"]["kind"],
            "explicit_scope_delta",
        )

    def test_rebind_requires_old_ids_and_marks_new_or_changed_ids(self) -> None:
        bound = self.bind()

        self.write_contract(
            contract_record(
                outcomes=[
                    {
                        "id": "OUT-002",
                        "title": "Replacement outcome",
                        "disposition": "added",
                    }
                ],
                scope_status="proposed",
                consequences=["Replace the old outcome"],
            )
        )
        with self.assertRaisesRegex(state_module.StateError, "removed.*OUT-001"):
            self.bind(bound, approve_scope_delta=True)

        self.write_contract(
            contract_record(
                outcomes=[
                    {
                        "id": "OUT-001",
                        "title": "The silently changed behavior",
                        "disposition": "active",
                    }
                ]
            )
        )
        with self.assertRaisesRegex(state_module.StateError, "changed.*OUT-001"):
            self.bind(bound)

        self.write_contract(
            contract_record(
                outcomes=[
                    {
                        "id": "OUT-001",
                        "title": "The explicitly changed behavior",
                        "disposition": "changed",
                    }
                ],
                scope_status="proposed",
                consequences=["OUT-001 behavior changed"],
            )
        )
        rebound = self.bind(bound, approve_scope_delta=True)
        self.assertEqual(
            rebound["outcome_lock"]["scope_delta"]["changed"], ["OUT-001"]
        )

    def test_rebind_invalidates_plan_and_verification_summaries(self) -> None:
        bound = self.bind()
        state = json.loads(json.dumps(bound))
        (self.root / "docs" / "contracts" / "plan.md").write_text(
            "approved plan\n", encoding="utf-8"
        )
        (self.root / "docs" / "contracts" / "evidence.md").write_text(
            "evidence\n", encoding="utf-8"
        )
        state["artifacts"]["evidence"] = "docs/contracts/evidence.md"
        state["outcome_lock"]["plan"] = {
            "artifact": "docs/contracts/plan.md",
            "semantic_digest": "sha256:" + "1" * 64,
            "coverage": {
                "original_total": 1,
                "active_total": 1,
                "mapped_active": 1,
                "approved_deferred": 0,
                "approved_removed": 0,
                "missing": [],
                "unknown": [],
                "status": "pass",
            },
        }
        state["outcome_lock"]["verification"] = {
            "artifact": "docs/contracts/evidence.md",
            "semantic_digest": "sha256:" + "2" * 64,
            "work_unit": "pass",
            "outcome_fidelity": "pass",
            "code_quality": "approve",
            "blocking_evidence": 0,
            "verified_outcomes": 1,
        }
        state_module.write_state(self.root, state)

        rebound = self.bind(state)

        self.assertIsNone(rebound["outcome_lock"]["plan"]["artifact"])
        self.assertEqual(
            rebound["outcome_lock"]["plan"]["coverage"]["status"], "pending"
        )
        self.assertIsNone(rebound["outcome_lock"]["verification"]["artifact"])
        self.assertIsNone(rebound["artifacts"]["evidence"])

    def test_check_detects_source_drift_without_adopting_new_digest(self) -> None:
        bound = self.bind()
        recorded_digest = bound["outcome_lock"]["contract"]["sources"][0]["digest"]
        (self.root / "docs" / "product" / "prd.md").write_text(
            "Changed without approval\n", encoding="utf-8"
        )

        drifted = self.check(bound)

        self.assertEqual(drifted["outcome_lock"]["status"], "drifted")
        self.assertEqual(
            drifted["outcome_lock"]["contract"]["sources"][0]["digest"],
            recorded_digest,
        )
        self.assertEqual(
            drifted["outcome_lock"]["drift"],
            [
                {
                    "kind": "source",
                    "identifier": "SRC-001",
                    "reason": "changed",
                }
            ],
        )

        (self.root / "docs" / "product" / "prd.md").write_text(
            "Approved behavior v1\n", encoding="utf-8"
        )
        restored = self.check(drifted)
        self.assertEqual(restored["outcome_lock"]["status"], "bound")
        self.assertEqual(restored["outcome_lock"]["drift"], [])

    def test_check_records_missing_and_semantic_contract_drift(self) -> None:
        bound = self.bind()
        (self.root / "docs" / "product" / "prd.md").unlink()

        missing = self.check(bound)

        self.assertEqual(missing["outcome_lock"]["status"], "drifted")
        self.assertEqual(missing["outcome_lock"]["drift"][0]["reason"], "missing")

        (self.root / "docs" / "product" / "prd.md").write_text(
            "Approved behavior v1\n", encoding="utf-8"
        )
        changed = contract_record()
        changed["review"]["code_quality_required"] = False
        self.write_contract(changed)
        semantic = self.check(missing)
        self.assertEqual(semantic["outcome_lock"]["status"], "drifted")
        self.assertEqual(
            semantic["outcome_lock"]["drift"],
            [
                {
                    "kind": "contract",
                    "identifier": "docs/contracts/outcome-lock.md",
                    "reason": "semantic_changed",
                }
            ],
        )

    def test_direct_objective_change_is_rejected_atomically(self) -> None:
        other_root = self.root / "direct"
        other_root.mkdir()
        direct = state_module.command_start(
            namespace(
                objective="Rename one exact label",
                phase="execute",
                next_action="Edit the label",
                direct_lock=True,
            ),
            other_root,
        )
        with self.assertRaisesRegex(state_module.StateError, "objective is locked"):
            state_module.command_checkpoint(
                namespace(
                    workflow=direct["workflow_id"],
                    expect_revision=direct["revision"],
                    objective="Rename a different label",
                ),
                other_root,
            )

        persisted = state_module.load_state(other_root)
        assert persisted is not None
        self.assertEqual(persisted["objective"], "Rename one exact label")
        self.assertEqual(persisted["revision"], direct["revision"])

    def test_stale_bind_and_unbound_check_do_not_mutate(self) -> None:
        with self.assertRaises(state_module.StateConflict):
            state_module.command_bind_contract(
                namespace(
                    workflow=self.state["workflow_id"],
                    expect_revision=99,
                    artifact="docs/contracts/outcome-lock.md",
                    approval_kind="review-gate",
                ),
                self.root,
            )
        with self.assertRaisesRegex(state_module.StateError, "bound contract"):
            self.check(self.state)
        self.assertEqual(
            state_module.load_state(self.root)["revision"], self.state["revision"]
        )


if __name__ == "__main__":
    unittest.main()
