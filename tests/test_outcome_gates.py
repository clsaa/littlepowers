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


def block(kind: str, value: object) -> str:
    return (
        f"<!-- littlepowers:{kind}:v1 -->\n"
        "```json\n"
        f"{json.dumps(value, ensure_ascii=False, indent=2)}\n"
        "```\n"
        f"<!-- /littlepowers:{kind} -->\n"
    )


def contract_record(*, fidelity: bool = False) -> dict[str, object]:
    sources: list[dict[str, object]] = [
        {
            "id": "SRC-001",
            "path": "docs/product/prd.md",
            "role": "requirements",
            "origin": "user",
            "approved": True,
        }
    ]
    baseline: dict[str, object] = {
        "requirement": "not_applicable",
        "source_ids": [],
    }
    fidelity_rows: list[dict[str, str]] = []
    if fidelity:
        sources.append(
            {
                "id": "SRC-002",
                "path": "docs/product/approved-output.txt",
                "role": "compatibility",
                "origin": "user",
                "approved": True,
            }
        )
        baseline = {"requirement": "required", "source_ids": ["SRC-002"]}
        fidelity_rows = [
            {
                "id": "FID-001",
                "outcome": "OUT-001",
                "baseline": "SRC-002",
                "surface": "generated output",
                "action": "render",
                "state": "approved",
            }
        ]
    return {
        "route": "lean",
        "sources": sources,
        "scope_delta": {"status": "none", "consequences": []},
        "baseline": baseline,
        "review": {"code_quality_required": True},
        "outcomes": [
            {
                "id": "OUT-001",
                "title": "The primary behavior works",
                "disposition": "active",
            },
            {
                "id": "OUT-002",
                "title": "The recovery behavior works",
                "disposition": "active",
            },
        ],
        "fidelity": fidelity_rows,
    }


def plan_map(*, include_second: bool = True) -> dict[str, object]:
    mappings: list[dict[str, object]] = [
        {
            "outcome": "OUT-001",
            "tasks": ["Task 1"],
            "evidence": ["test:primary-behavior"],
        }
    ]
    if include_second:
        mappings.append(
            {
                "outcome": "OUT-002",
                "tasks": ["Task 2"],
                "evidence": ["test:recovery-behavior"],
            }
        )
    return {"mappings": mappings}


def verification_record(
    *,
    fidelity: bool = False,
    second_status: str = "pass",
    outcome_fidelity: str = "pass",
    work_unit: str = "pass",
    code_quality: str = "approve",
    blockers: list[str] | None = None,
) -> dict[str, object]:
    rows: list[dict[str, object]] = [
        {
            "outcome": "OUT-001",
            "status": "pass",
            "evidence": ["test:primary-behavior"],
        },
        {
            "outcome": "OUT-002",
            "status": second_status,
            "evidence": ["test:recovery-behavior"],
        },
    ]
    fidelity_rows: list[dict[str, str]] = []
    if fidelity:
        fidelity_rows = [
            {
                "id": "FID-001",
                "outcome": "OUT-001",
                "baseline": "SRC-002",
                "evidence_path": "artifacts/evidence/output.txt",
                "result": "pass",
            }
        ]
    return {
        "work_unit": {
            "status": work_unit,
            "evidence": ["test:focused-suite"],
        },
        "outcome_fidelity": {
            "status": outcome_fidelity,
            "evidence": ["inspection:outcome-traceability"],
        },
        "code_quality": {
            "required": True,
            "status": code_quality,
            "evidence": (
                ["review:integrated-diff"] if code_quality == "approve" else []
            ),
        },
        "blocking_evidence": blockers or [],
        "outcomes": rows,
        "fidelity": fidelity_rows,
    }


class OutcomeGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for directory in (
            "docs/product",
            "docs/contracts",
            "docs/plans",
            "docs/evidence",
            "artifacts/evidence",
        ):
            (self.root / directory).mkdir(parents=True)
        (self.root / "docs/product/prd.md").write_text(
            "Approved requirements\n", encoding="utf-8"
        )
        self.contract_path = self.root / "docs/contracts/contract.md"
        self.plan_path = self.root / "docs/plans/plan.md"
        self.evidence_path = self.root / "docs/evidence/verification.md"
        self.write_contract()
        self.write_plan()
        self.write_verification()
        self.state = state_module.command_start(
            namespace(
                objective="Ship the complete approved behavior",
                phase="plan",
                next_action="Bind and validate the plan",
            ),
            self.root,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def writer(
        self, state: dict[str, object], **values: object
    ) -> argparse.Namespace:
        return namespace(
            workflow=state["workflow_id"],
            expect_revision=state["revision"],
            **values,
        )

    def write_contract(self, *, fidelity: bool = False) -> None:
        self.contract_path.write_text(
            block("contract", contract_record(fidelity=fidelity)),
            encoding="utf-8",
        )

    def write_plan(self, *, include_second: bool = True) -> None:
        self.plan_path.write_text(
            block("plan-map", plan_map(include_second=include_second)),
            encoding="utf-8",
        )

    def write_verification(self, **values: object) -> None:
        self.evidence_path.write_text(
            block("verification", verification_record(**values)),
            encoding="utf-8",
        )

    def bind(self, state: dict[str, object] | None = None) -> dict[str, object]:
        current = state or self.state
        current = self.approve_artifact(
            current, key="spec", relative="docs/contracts/contract.md"
        )
        return state_module.command_bind_contract(
            self.writer(
                current,
                artifact="docs/contracts/contract.md",
                approval_kind="review-gate",
            ),
            self.root,
        )

    def validate_plan(
        self, state: dict[str, object], *, approve: bool = True
    ) -> dict[str, object]:
        if approve:
            state = self.approve_artifact(
                state, key="plan", relative="docs/plans/plan.md"
            )
        return state_module.command_validate_plan(
            self.writer(state, artifact="docs/plans/plan.md"),
            self.root,
        )

    def approve_artifact(
        self,
        state: dict[str, object],
        *,
        key: str,
        relative: str,
    ) -> dict[str, object]:
        if state["artifacts"][key] != relative or key not in state["completed"]:
            state = state_module.command_checkpoint(
                self.writer(
                    state,
                    artifact=[f"{key}={relative}"],
                    completed=[key],
                    next_action=f"Review {key}",
                ),
                self.root,
            )
        parked = state_module.command_park_review(
            self.writer(
                state,
                artifact_key=key,
                scope_delta="none",
                unresolved_questions=0,
                replace=False,
            ),
            self.root,
        )
        return state_module.command_resolve_review(
            self.writer(
                parked,
                kind="explicit_approval",
                observed_no_intervention=False,
            ),
            self.root,
        )

    def checkpoint(
        self, state: dict[str, object], **values: object
    ) -> dict[str, object]:
        return state_module.command_checkpoint(
            self.writer(state, **values), self.root
        )

    def record_verification(
        self, state: dict[str, object]
    ) -> dict[str, object]:
        return state_module.command_record_verification(
            self.writer(state, artifact="docs/evidence/verification.md"),
            self.root,
        )

    def ready_for_verify(self) -> dict[str, object]:
        bound = self.bind()
        planned = self.validate_plan(bound)
        executing = self.checkpoint(planned, phase="execute")
        return self.checkpoint(executing, phase="verify")

    def test_narrow_plan_is_rejected_with_all_missing_ids_atomically(self) -> None:
        bound = self.bind()
        self.write_plan(include_second=False)
        plan_ready = state_module.command_checkpoint(
            self.writer(
                bound,
                artifact=["plan=docs/plans/plan.md"],
                completed=["plan"],
                next_action="Review plan",
            ),
            self.root,
        )
        parked = state_module.command_park_review(
            self.writer(
                plan_ready,
                artifact_key="plan",
                scope_delta="none",
                unresolved_questions=0,
                replace=False,
            ),
            self.root,
        )

        status = state_module.review_gate_status(
            self.root,
            parked,
            gate_revision=parked["review"]["gate"]["opened_revision"],
        )
        self.assertEqual(status["status"], "blocked")
        self.assertIn("plan_coverage_incomplete", status["reasons"])
        with self.assertRaisesRegex(state_module.StateError, "coverage"):
            state_module.command_resolve_review(
                self.writer(
                    parked,
                    kind="explicit_approval",
                    observed_no_intervention=False,
                ),
                self.root,
            )

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["revision"], parked["revision"])
        self.assertEqual(
            persisted["outcome_lock"]["plan"]["coverage"]["status"], "pending"
        )

    def test_complete_plan_allows_fresh_execute_and_verify_transitions(self) -> None:
        bound = self.bind()
        planned = self.validate_plan(bound)

        self.assertEqual(
            planned["outcome_lock"]["plan"]["coverage"]["status"], "pass"
        )
        self.assertEqual(
            planned["outcome_lock"]["plan"]["coverage"]["mapped_active"], 2
        )
        executing = self.checkpoint(planned, phase="execute")
        verifying = self.checkpoint(executing, phase="verify")
        self.assertEqual(executing["phase"], "execute")
        self.assertEqual(verifying["phase"], "verify")

    def test_unbound_or_drifted_work_cannot_execute_but_can_return_to_planning(
        self,
    ) -> None:
        with self.assertRaisesRegex(state_module.StateError, "contract"):
            self.checkpoint(self.state, phase="execute")
        self.assertEqual(
            state_module.load_state(self.root)["revision"], self.state["revision"]
        )

        executing = self.checkpoint(
            self.validate_plan(self.bind()), phase="execute"
        )
        (self.root / "docs/product/prd.md").write_text(
            "Unapproved source change\n", encoding="utf-8"
        )
        progress = self.checkpoint(
            executing,
            progress="Focused implementation checks pass",
        )
        self.assertEqual(progress["phase"], "execute")
        with self.assertRaisesRegex(state_module.StateError, "drift"):
            self.checkpoint(progress, phase="verify")

        planning = self.checkpoint(progress, phase="plan")
        self.assertEqual(planning["phase"], "plan")

    def test_legacy_execute_resume_remains_reconciliation_only(self) -> None:
        paused = state_module.command_pause(
            self.writer(self.state, next_action="Reconcile later"),
            self.root,
        )
        paused["phase"] = "execute"
        paused["outcome_lock"]["status"] = "reconcile_required"
        paused["outcome_lock"]["baseline"]["status"] = "reconcile_required"
        state_module.write_state(self.root, paused)

        resumed = state_module.command_resume(
            self.writer(paused, next_action="Reconcile now"), self.root
        )

        self.assertEqual(resumed["status"], "active")
        with self.assertRaisesRegex(state_module.StateError, "reconcile|contract"):
            self.checkpoint(resumed, progress="Must not execute")

    def test_resume_freshly_rejects_source_drift(self) -> None:
        executing = self.checkpoint(
            self.validate_plan(self.bind()), phase="execute"
        )
        paused = state_module.command_pause(
            self.writer(executing, next_action="Resume after interruption"),
            self.root,
        )
        (self.root / "docs/product/prd.md").write_text(
            "Drifted while paused\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(state_module.StateError, "drift"):
            state_module.command_resume(
                self.writer(paused, next_action="Resume implementation"),
                self.root,
            )

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["status"], "paused")
        self.assertEqual(persisted["revision"], paused["revision"])

    def test_valid_verification_completes_only_after_all_three_verdicts(self) -> None:
        verifying = self.ready_for_verify()
        verified = self.record_verification(verifying)

        self.assertEqual(
            verified["outcome_lock"]["verification"]["work_unit"], "pass"
        )
        self.assertEqual(
            verified["outcome_lock"]["verification"]["outcome_fidelity"],
            "pass",
        )
        self.assertEqual(
            verified["outcome_lock"]["verification"]["code_quality"], "approve"
        )
        completed = state_module.command_finish(
            self.writer(verified), self.root, "complete"
        )
        self.assertEqual(completed["status"], "complete")

    def test_state_validator_rejects_forged_schema_3_completion(self) -> None:
        bound = self.bind()
        planned = self.validate_plan(bound)
        forged = self.checkpoint(planned, phase="verify")
        forged["status"] = "complete"

        with self.assertRaisesRegex(
            state_module.StateError, "completion gate|Verification Record"
        ):
            state_module.write_state(self.root, forged)

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["status"], "active")
        self.assertEqual(persisted["revision"], planned["revision"] + 1)

    def test_valid_blocked_record_persists_and_completion_lists_all_failures(
        self,
    ) -> None:
        verifying = self.ready_for_verify()
        self.write_verification(
            second_status="blocked",
            outcome_fidelity="blocked",
            work_unit="fail",
            code_quality="request_changes",
            blockers=["Approved recovery environment unavailable"],
        )

        recorded = self.record_verification(verifying)

        self.assertEqual(
            recorded["outcome_lock"]["verification"]["work_unit"], "fail"
        )
        self.assertEqual(
            recorded["outcome_lock"]["verification"]["outcome_fidelity"],
            "blocked",
        )
        before = recorded["revision"]
        with self.assertRaises(state_module.StateError) as raised:
            state_module.command_finish(
                self.writer(recorded), self.root, "complete"
            )
        message = str(raised.exception)
        self.assertIn("work-unit compliance", message)
        self.assertIn("approved-outcome fidelity", message)
        self.assertIn("code-quality", message)
        self.assertIn("blocking evidence", message)
        self.assertEqual(state_module.load_state(self.root)["revision"], before)

    def test_malformed_verification_is_rejected_without_mutation(self) -> None:
        verifying = self.ready_for_verify()
        malformed = verification_record()
        malformed["outcomes"] = malformed["outcomes"][:1]
        self.evidence_path.write_text(
            block("verification", malformed), encoding="utf-8"
        )

        with self.assertRaisesRegex(state_module.StateError, "OUT-002"):
            self.record_verification(verifying)

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["revision"], verifying["revision"])
        self.assertIsNone(persisted["outcome_lock"]["verification"]["artifact"])

    def test_fidelity_evidence_is_hashed_and_rechecked_at_completion(self) -> None:
        (self.root / "docs/product/approved-output.txt").write_text(
            "approved\n", encoding="utf-8"
        )
        (self.root / "artifacts/evidence/output.txt").write_text(
            "matches approved output\n", encoding="utf-8"
        )
        self.write_contract(fidelity=True)
        self.write_verification(fidelity=True)
        verifying = self.ready_for_verify()
        verified = self.record_verification(verifying)
        digest = verified["outcome_lock"]["verification"]["semantic_digest"]
        self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(verified["outcome_lock"]["baseline"]["status"], "pass")

        (self.root / "artifacts/evidence/output.txt").write_text(
            "changed evidence\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(
            state_module.StateError, "verification|evidence"
        ):
            state_module.command_finish(
                self.writer(verified), self.root, "complete"
            )
        self.assertEqual(
            state_module.load_state(self.root)["revision"], verified["revision"]
        )

    def test_direct_route_needs_no_plan_but_still_needs_verification(self) -> None:
        direct_root = self.root / "direct"
        (direct_root / "docs/evidence").mkdir(parents=True)
        direct = state_module.command_start(
            namespace(
                objective="Rename one exact label",
                phase="execute",
                next_action="Edit and verify the label",
                direct_lock=True,
            ),
            direct_root,
        )
        verifying = state_module.command_checkpoint(
            namespace(
                workflow=direct["workflow_id"],
                expect_revision=direct["revision"],
                phase="verify",
            ),
            direct_root,
        )
        direct_record = verification_record()
        direct_record["code_quality"] = {
            "required": False,
            "status": "not_required",
            "evidence": [],
        }
        direct_record["outcomes"] = [
            {
                "outcome": "OUT-001",
                "status": "pass",
                "evidence": ["test:label"],
            }
        ]
        (direct_root / "docs/evidence/direct.md").write_text(
            block("verification", direct_record), encoding="utf-8"
        )
        verified = state_module.command_record_verification(
            namespace(
                workflow=verifying["workflow_id"],
                expect_revision=verifying["revision"],
                artifact="docs/evidence/direct.md",
            ),
            direct_root,
        )

        completed = state_module.command_finish(
            namespace(
                workflow=verified["workflow_id"],
                expect_revision=verified["revision"],
            ),
            direct_root,
            "complete",
        )
        self.assertEqual(completed["status"], "complete")
        self.assertIsNone(completed["outcome_lock"]["plan"]["artifact"])

    def test_execute_handoff_rejects_invalid_source_lock(self) -> None:
        executing = self.checkpoint(
            self.validate_plan(self.bind()), phase="execute"
        )
        (self.root / "docs/product/prd.md").write_text(
            "drift\n", encoding="utf-8"
        )
        drifted = state_module.command_check_contract(
            self.writer(executing), self.root
        )
        target_root = self.root / "target"
        target_root.mkdir()
        target = state_module.command_start(
            namespace(
                objective="Continue target",
                phase="execute",
                next_action="Continue",
                direct_lock=True,
            ),
            target_root,
        )

        with self.assertRaisesRegex(state_module.StateError, "contract"):
            state_module.command_handoff(
                self.writer(
                    drifted,
                    target_root=str(target_root),
                    target_workflow=target["workflow_id"],
                    target_revision=target["revision"],
                ),
                self.root,
            )
        self.assertEqual(
            state_module.load_state(self.root)["status"], "active"
        )

    def test_execute_handoff_freshly_detects_unrecorded_source_drift(self) -> None:
        executing = self.checkpoint(
            self.validate_plan(self.bind()), phase="execute"
        )
        (self.root / "docs/product/prd.md").write_text(
            "Drift before handoff\n", encoding="utf-8"
        )
        target_root = self.root / "fresh-target"
        target_root.mkdir()
        target = state_module.command_start(
            namespace(
                objective="Continue target",
                phase="execute",
                next_action="Continue",
                direct_lock=True,
            ),
            target_root,
        )

        with self.assertRaisesRegex(state_module.StateError, "drift"):
            state_module.command_handoff(
                self.writer(
                    executing,
                    target_root=str(target_root),
                    target_workflow=target["workflow_id"],
                    target_revision=target["revision"],
                ),
                self.root,
            )

        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["status"], "active")
        self.assertEqual(persisted["revision"], executing["revision"])

    def test_stale_plan_and_verification_writers_do_not_mutate(self) -> None:
        bound = self.bind()
        with self.assertRaises(state_module.StateConflict):
            state_module.command_validate_plan(
                namespace(
                    workflow=bound["workflow_id"],
                    expect_revision=999,
                    artifact="docs/plans/plan.md",
                ),
                self.root,
            )
        self.assertEqual(
            state_module.load_state(self.root)["revision"], bound["revision"]
        )


if __name__ == "__main__":
    unittest.main()
