from __future__ import annotations

import argparse
import json
import subprocess
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
        "inputs": {"mode": "manual", "files": [], "manual_reason": "Protocol-only fixture; no implementation files are changed."},
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
        (self.root / "implementation.py").write_text("value = 1\n", encoding="utf-8")
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
        record = verification_record(**values)
        record["inputs"] = state_module.capture_verification_inputs(
            self.root, files=["implementation.py"], absent=[]
        )
        self.evidence_path.write_text(
            block("verification", record),
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

    def failed_fidelity(self, result: str, *, route: str = "lean") -> dict[str, object]:
        """Persist real historical failure state before attempting a repair."""
        (self.root / "docs/product/approved-output.txt").write_text(
            "approved output\n", encoding="utf-8"
        )
        (self.root / "artifacts/evidence/output.txt").write_text(
            "observed mismatch or unavailable surface\n", encoding="utf-8"
        )
        contract = contract_record(fidelity=True)
        contract["route"] = route
        self.contract_path.write_text(block("contract", contract), encoding="utf-8")
        if route == "compact":
            self.plan_path.write_text(
                block("contract", contract) + block("plan-map", plan_map()),
                encoding="utf-8",
            )
            approved = self.approve_artifact(
                self.state, key="shape", relative="docs/plans/plan.md"
            )
            bound = state_module.command_bind_contract(
                self.writer(approved, artifact="docs/plans/plan.md", approval_kind="review-gate"),
                self.root,
            )
            planned = self.validate_plan(bound, approve=False)
            verifying = self.checkpoint(planned, phase="verify")
        else:
            verifying = self.ready_for_verify()
        record = verification_record(fidelity=True, outcome_fidelity=result)
        record["fidelity"][0]["result"] = result
        self.evidence_path.write_text(block("verification", record), encoding="utf-8")
        return self.record_verification(verifying)

    def park_repair(self, recorded: dict[str, object], *, compact: bool = False) -> dict[str, object]:
        key = "shape" if compact else "plan"
        planning = self.checkpoint(recorded, phase=key, next_action="Review same-scope repair")
        content = self.plan_path.read_text(encoding="utf-8")
        self.plan_path.write_text(content + "\nRepair the mismatch; retain every outcome.\n", encoding="utf-8")
        return state_module.command_park_review(
            self.writer(planning, artifact_key=key, scope_delta="none", unresolved_questions=0),
            self.root,
        )

    def assert_repair_cycle(self, *, route: str, result: str, mode: str) -> None:
        recorded = self.failed_fidelity(result, route=route)
        historical = self.evidence_path.read_bytes()
        recorded = state_module.command_set_review_policy(
            self.writer(recorded, mode=mode), self.root
        )
        parked = self.park_repair(recorded, compact=route == "compact")
        status = state_module.review_gate_status(
            self.root, parked, gate_revision=parked["revision"]
        )
        self.assertEqual(status["status"], "waiting" if mode == "blocking" else "eligible")
        with self.assertRaisesRegex(state_module.StateError, "[Rr]eview"):
            self.validate_plan(parked, approve=False)
        with self.assertRaises(state_module.StateError):
            state_module.command_finish(self.writer(parked), self.root, "complete")
        resolved = state_module.command_resolve_review(
            self.writer(parked, kind="explicit_approval" if mode == "blocking" else mode), self.root
        )
        repaired_plan = self.validate_plan(resolved, approve=False)
        self.assertEqual(repaired_plan["artifacts"]["evidence"], "docs/evidence/verification.md")
        self.assertIsNone(repaired_plan["outcome_lock"]["verification"]["artifact"])
        executing = self.checkpoint(repaired_plan, phase="execute")
        verifying = self.checkpoint(executing, phase="verify")
        with self.assertRaisesRegex(state_module.StateError, "Verification Record"):
            state_module.command_finish(self.writer(verifying), self.root, "complete")
        fresh_path = self.root / "docs/evidence/repaired.md"
        fresh_record = verification_record(fidelity=True)
        fresh_record["fidelity"][0]["evidence_path"] = "artifacts/evidence/repaired-output.txt"
        (self.root / "artifacts/evidence/repaired-output.txt").write_text(
            "approved output\n", encoding="utf-8"
        )
        self.assertEqual(
            (self.root / "artifacts/evidence/repaired-output.txt").read_bytes(),
            (self.root / "docs/product/approved-output.txt").read_bytes(),
        )
        fresh_path.write_text(
            "Supersedes verification.md; prior failure retained.\n" +
            block("verification", fresh_record), encoding="utf-8"
        )
        verified = state_module.command_record_verification(
            self.writer(verifying, artifact="docs/evidence/repaired.md"), self.root
        )
        finished = state_module.command_finish(self.writer(verified), self.root, "complete")
        self.assertEqual(finished["status"], "complete")
        self.assertEqual(finished["workflow_id"], recorded["workflow_id"])
        self.assertEqual(self.evidence_path.read_bytes(), historical)

    def test_failed_fidelity_allows_approved_lean_repair_without_erasing_history(self) -> None:
        self.assert_repair_cycle(route="lean", result="fail", mode="blocking")

    def test_blocked_fidelity_allows_compact_repair_under_existing_mandate(self) -> None:
        self.assert_repair_cycle(route="compact", result="blocked", mode="implementation_mandate")

    def test_failed_fidelity_allows_full_repair_under_explicit_approval(self) -> None:
        self.assert_repair_cycle(route="full", result="fail", mode="blocking")

    def test_failed_fidelity_does_not_bypass_missing_baseline_or_source_drift(self) -> None:
        recorded = self.failed_fidelity("fail")
        parked = self.park_repair(recorded)
        source = self.root / "docs/product/approved-output.txt"
        for missing in (False, True):
            with self.subTest(missing=missing):
                if missing:
                    source.unlink()
                else:
                    source.write_text("unapproved replacement", encoding="utf-8")
                status = state_module.review_gate_status(self.root, parked, gate_revision=parked["revision"])
                self.assertEqual(status["status"], "blocked")
                self.assertIn("contract_drift", status["reasons"])
                with self.assertRaises(state_module.StateError):
                    state_module.command_resolve_review(self.writer(parked, kind="explicit_approval"), self.root)
                self.assertEqual(state_module.load_state(self.root)["revision"], parked["revision"])

    def test_failed_fidelity_does_not_approve_narrow_repair_or_wrong_policy(self) -> None:
        recorded = self.failed_fidelity("blocked", route="full")
        recorded = state_module.command_set_review_policy(self.writer(recorded, mode="implementation_mandate"), self.root)
        self.write_plan(include_second=False)
        parked = self.park_repair(recorded)
        status = state_module.review_gate_status(self.root, parked, gate_revision=parked["revision"])
        self.assertEqual(status["status"], "blocked")
        self.assertIn("plan_coverage_incomplete", status["reasons"])
        self.assertIn("implementation_mandate_requires_lean_or_compact", status["reasons"])
        with self.assertRaises(state_module.StateError):
            state_module.command_resolve_review(self.writer(parked, kind="implementation_mandate"), self.root)

    def test_repair_execution_invalidates_old_pass_but_keeps_recovery_reference(self) -> None:
        verified = self.record_verification(self.ready_for_verify())
        # Status-only progress must not discard usable evidence.
        unchanged = self.checkpoint(verified, next_action="Inspect result")
        self.assertEqual(unchanged["outcome_lock"]["verification"], verified["outcome_lock"]["verification"])
        historical = self.evidence_path.read_bytes()
        executing = self.checkpoint(unchanged, phase="execute", next_action="Repair an observed issue")
        self.assertEqual(executing["artifacts"]["evidence"], "docs/evidence/verification.md")
        self.assertEqual(executing["outcome_lock"]["verification"]["work_unit"], "pending")
        verifying = self.checkpoint(executing, phase="verify")
        with self.assertRaisesRegex(state_module.StateError, "Verification Record"):
            state_module.command_finish(self.writer(verifying), self.root, "complete")
        self.assertEqual(self.evidence_path.read_bytes(), historical)

    def test_contract_rebind_preserves_historical_evidence_without_eligibility(self) -> None:
        verified = self.record_verification(self.ready_for_verify())
        historical = self.evidence_path.read_bytes()
        planning = self.checkpoint(verified, phase="spec")
        rebound = self.bind(planning)
        self.assertEqual(rebound["artifacts"]["evidence"], "docs/evidence/verification.md")
        self.assertIsNone(rebound["outcome_lock"]["verification"]["artifact"])
        self.assertEqual(self.evidence_path.read_bytes(), historical)

    def test_cli_recovers_existing_failure_and_completes_repair_without_reset(self) -> None:
        recorded = self.failed_fidelity("fail")
        historical_report = self.evidence_path.read_bytes()
        historical_output = (self.root / "artifacts/evidence/output.txt").read_bytes()
        mutation = {"workflow": recorded["workflow_id"], "revision": recorded["revision"]}

        def cli(command: str, *arguments: str, expected: int = 0) -> dict[str, object] | None:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/littlepowers_state.py"),
                 "--root", str(self.root), command,
                 "--workflow", mutation["workflow"],
                 "--expect-revision", str(mutation["revision"]), *arguments],
                capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            self.assertEqual(completed.returncode, expected, completed.stderr)
            if expected:
                return None
            result = json.loads(completed.stdout)
            mutation["revision"] = result["revision"]
            return result

        cli("checkpoint", "--phase", "plan", "--next-action", "Review repair")
        self.plan_path.write_text(
            self.plan_path.read_text(encoding="utf-8") + "\nRepair output, preserve old evidence.\n",
            encoding="utf-8",
        )
        cli("park-review", "--artifact-key", "plan", "--scope-delta", "none", "--unresolved-questions", "0")
        cli("checkpoint", "--phase", "execute", expected=2)
        cli("resolve-review", "--kind", "explicit_approval")
        cli("validate-plan", "--artifact", "docs/plans/plan.md")
        recovered = cli("read-artifact", "--key", "evidence")
        self.assertEqual(recovered["content"].encode("utf-8"), historical_report)
        cli("checkpoint", "--phase", "execute", "--next-action", "Repair and recheck")
        cli("checkpoint", "--phase", "verify")
        cli("complete", expected=2)
        # Observe the actual fixture output, not just a synthetic passing verdict.
        actual = self.root / "artifacts/evidence/repaired-output.txt"
        expected = self.root / "docs/product/approved-output.txt"
        actual.write_text("approved output\n", encoding="utf-8")
        self.assertEqual(actual.read_bytes(), expected.read_bytes())
        fresh = verification_record(fidelity=True)
        fresh["fidelity"][0]["evidence_path"] = "artifacts/evidence/repaired-output.txt"
        (self.root / "docs/evidence/repaired.md").write_text(
            "Supersedes verification.md.\n" + block("verification", fresh), encoding="utf-8"
        )
        cli("record-verification", "--artifact", "docs/evidence/repaired.md")
        finished = cli("complete")
        self.assertEqual(finished["status"], "complete")
        self.assertEqual(finished["workflow_id"], recorded["workflow_id"])
        self.assertEqual(self.evidence_path.read_bytes(), historical_report)
        self.assertEqual((self.root / "artifacts/evidence/output.txt").read_bytes(), historical_output)

    def test_completion_rechecks_approved_plan_bytes_not_only_mapping(self) -> None:
        verified = self.record_verification(self.ready_for_verify())
        self.plan_path.write_text(
            self.plan_path.read_text(encoding="utf-8") + "\nUnapproved repair approach.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(state_module.StateError, "[Rr]eview|approved"):
            state_module.command_finish(self.writer(verified), self.root, "complete")
        self.assertEqual(state_module.load_state(self.root)["revision"], verified["revision"])

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
