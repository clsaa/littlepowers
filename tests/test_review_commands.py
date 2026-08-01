from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import littlepowers_state as state_module


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


def contract(route: str = "lean", outcomes: int = 1) -> dict[str, object]:
    return {
        "route": route,
        "sources": [],
        "scope_delta": {"status": "none", "consequences": []},
        "baseline": {"requirement": "not_applicable", "source_ids": []},
        "review": {"code_quality_required": False},
        "outcomes": [
            {
                "id": f"OUT-{index:03d}",
                "title": f"Outcome {index}",
                "disposition": "active",
            }
            for index in range(1, outcomes + 1)
        ],
        "fidelity": [],
    }


def protocol_block(kind: str, record: dict[str, object]) -> str:
    return (
        f"<!-- littlepowers:{kind}:v1 -->\n"
        "```json\n"
        f"{json.dumps(record, indent=2)}\n"
        "```\n"
        f"<!-- /littlepowers:{kind} -->\n"
    )


class ReviewCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def start(
        self,
        *,
        mode: str = "blocking",
        through: str | None = None,
        wait: int | None = None,
        phase: str = "brainstorm",
        direct: bool = False,
    ) -> dict[str, object]:
        return state_module.command_start(
            namespace(
                objective="Implement the complete approved outcome",
                phase=phase,
                next_action="Complete the current phase",
                review_policy=mode,
                review_through=through,
                review_wait_seconds=wait,
                direct_lock=direct,
            ),
            self.root,
        )

    @staticmethod
    def writer(state: dict[str, object], **values: object) -> argparse.Namespace:
        return namespace(
            workflow=state["workflow_id"],
            expect_revision=state["revision"],
            **values,
        )

    def write_artifact(self, relative: str, content: str = "# Reviewed artifact\n") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def checkpoint_artifact(
        self,
        state: dict[str, object],
        *,
        key: str = "brainstorm",
        content: str = "# Reviewed artifact\n",
    ) -> tuple[dict[str, object], str]:
        relative = f"docs/littlepowers/{key}s/review.md"
        self.write_artifact(relative, content)
        updated = state_module.command_checkpoint(
            self.writer(
                state,
                phase=("spec" if key == "brainstorm" else state["phase"]),
                artifact=[f"{key}={relative}"],
                completed=[key],
                next_action="Review the artifact",
            ),
            self.root,
        )
        return updated, relative

    def park(
        self,
        state: dict[str, object],
        *,
        key: str = "brainstorm",
        scope: str = "none",
        questions: int = 0,
        replace: bool = False,
    ) -> dict[str, object]:
        return state_module.command_park_review(
            self.writer(
                state,
                artifact_key=key,
                scope_delta=scope,
                unresolved_questions=questions,
                replace=replace,
            ),
            self.root,
        )

    def resolve(
        self,
        state: dict[str, object],
        kind: str,
        *,
        observed: bool = False,
    ) -> dict[str, object]:
        return state_module.command_resolve_review(
            self.writer(
                state,
                kind=kind,
                observed_no_intervention=observed,
            ),
            self.root,
        )

    def status(self, state: dict[str, object]) -> dict[str, object]:
        gate = state["review"]["gate"]
        assert isinstance(gate, dict)
        return state_module.review_gate_status(
            self.root,
            state,
            gate_revision=gate["opened_revision"],
        )

    def test_blocking_gate_waits_for_exact_explicit_resolution(self) -> None:
        state, _ = self.checkpoint_artifact(self.start())
        parked = self.park(state)

        self.assertEqual(parked["review"]["gate"]["opened_revision"], 2)
        self.assertEqual(self.status(parked)["status"], "waiting")
        with self.assertRaisesRegex(state_module.StateError, "requires resolution"):
            self.resolve(parked, "unattended")

        resolved = self.resolve(parked, "explicit_approval")
        self.assertIsNone(resolved["review"]["gate"])
        self.assertEqual(
            resolved["review"]["last_resolution"]["kind"],
            "explicit_approval",
        )

    def test_implementation_mandate_is_immediate_only_for_lean_or_compact(self) -> None:
        for route in ("lean", "compact"):
            with self.subTest(route=route):
                state = self.start(mode="implementation_mandate")
                content = "# Contract\n" + protocol_block("contract", contract(route))
                state, _ = self.checkpoint_artifact(state, content=content)
                parked = self.park(state)
                self.assertEqual(self.status(parked)["status"], "eligible")
                self.resolve(parked, "implementation_mandate")

                self.temporary_directory.cleanup()
                self.temporary_directory = tempfile.TemporaryDirectory()
                self.root = Path(self.temporary_directory.name)

        state = self.start(mode="implementation_mandate")
        state, _ = self.checkpoint_artifact(
            state,
            content="# Full\n" + protocol_block("contract", contract("full")),
        )
        parked = self.park(state)
        result = self.status(parked)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("implementation_mandate_requires_lean_or_compact", result["reasons"])

    def test_unattended_gate_resolves_immediately_but_not_scope_or_questions(self) -> None:
        state, _ = self.checkpoint_artifact(self.start(mode="unattended"))
        parked = self.park(state)
        self.assertEqual(self.status(parked)["status"], "eligible")
        resolved = self.resolve(parked, "unattended")
        self.assertEqual(resolved["review"]["policy"]["mode"], "unattended")

        for scope, questions, reason in (
            ("proposed", 0, "automatic_scope_delta_forbidden"),
            ("none", 1, "unresolved_questions"),
        ):
            with self.subTest(scope=scope, questions=questions):
                self.temporary_directory.cleanup()
                self.temporary_directory = tempfile.TemporaryDirectory()
                self.root = Path(self.temporary_directory.name)
                state, _ = self.checkpoint_artifact(self.start(mode="unattended"))
                parked = self.park(state, scope=scope, questions=questions)
                result = self.status(parked)
                self.assertEqual(result["status"], "blocked")
                self.assertIn(reason, result["reasons"])
                with self.assertRaisesRegex(state_module.StateError, "blocked"):
                    self.resolve(parked, "unattended")

    def test_windowed_gate_waits_requires_audit_and_consumes_next_phase_policy(self) -> None:
        with mock.patch.object(
            state_module, "utc_now", return_value="2026-07-31T00:00:00Z"
        ):
            state = self.start(mode="windowed", through="next_phase", wait=60)
            state, _ = self.checkpoint_artifact(state)
            parked = self.park(state)

        gate = parked["review"]["gate"]
        self.assertEqual(gate["not_before"], "2026-07-31T00:01:00Z")
        before = state_module.review_gate_status(
            self.root,
            parked,
            gate_revision=gate["opened_revision"],
            now=datetime(2026, 7, 31, 0, 0, 59, tzinfo=timezone.utc),
        )
        at = state_module.review_gate_status(
            self.root,
            parked,
            gate_revision=gate["opened_revision"],
            now=datetime(2026, 7, 31, 0, 1, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(before["status"], "waiting")
        self.assertEqual(at["status"], "eligible")
        with self.assertRaisesRegex(state_module.StateError, "observed"):
            self.resolve(parked, "window_expired")

        resolved = self.resolve(parked, "window_expired", observed=True)
        self.assertEqual(resolved["review"]["policy"]["mode"], "blocking")
        self.assertEqual(
            resolved["review"]["last_resolution"]["kind"], "window_expired"
        )

    def test_windowed_execute_boundary_becomes_unattended(self) -> None:
        with mock.patch.object(
            state_module, "utc_now", return_value="2026-07-31T00:00:00Z"
        ):
            state = self.start(mode="windowed", through="execute", wait=60)
            state, _ = self.checkpoint_artifact(state)
            parked = self.park(state)

        resolved = self.resolve(parked, "window_expired", observed=True)
        self.assertEqual(resolved["review"]["policy"]["mode"], "unattended")
        self.assertEqual(resolved["review"]["policy"]["through"], "execute")

    def test_artifact_drift_blocks_until_same_gate_is_replaced(self) -> None:
        state, relative = self.checkpoint_artifact(self.start(mode="unattended"))
        parked = self.park(state)
        self.write_artifact(relative, "# Corrected artifact\n")

        result = self.status(parked)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("artifact_changed", result["reasons"])
        with self.assertRaisesRegex(state_module.StateError, "blocked"):
            self.resolve(parked, "unattended")

        replaced = self.park(parked, replace=True)
        self.assertEqual(replaced["revision"], parked["revision"] + 1)
        self.assertEqual(self.status(replaced)["status"], "eligible")
        self.resolve(replaced, "unattended")

    def test_contract_source_drift_blocks_the_parked_gate(self) -> None:
        source = "requirements.md"
        self.write_artifact(source, "Approved requirement\n")
        record = contract("lean")
        record["sources"] = [
            {
                "id": "SRC-001",
                "path": source,
                "role": "requirements",
                "origin": "user",
                "approved": True,
            }
        ]
        state = self.start(mode="unattended", phase="spec")
        contract_path = "docs/littlepowers/specs/source-lock.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", record),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Review contract",
            ),
            self.root,
        )
        parked = self.park(state, key="spec")
        self.write_artifact(source, "Changed after parking\n")

        result = self.status(parked)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("contract_sources_changed", result["reasons"])
        with self.assertRaisesRegex(state_module.StateError, "blocked"):
            self.resolve(parked, "unattended")

    def test_unrelated_gate_cannot_be_replaced(self) -> None:
        state, _ = self.checkpoint_artifact(self.start())
        parked = self.park(state)
        with self.assertRaisesRegex(state_module.StateError, "same open"):
            self.park(parked, key="design", replace=True)

    def test_open_gate_blocks_ordinary_mutations_but_workflow_cancel_is_safe(self) -> None:
        state, _ = self.checkpoint_artifact(self.start())
        parked = self.park(state)
        before = (self.root / ".littlepowers" / "state.json").read_bytes()

        with self.assertRaisesRegex(state_module.StateError, "open Review Gate"):
            state_module.command_checkpoint(
                self.writer(parked, next_action="Bypass"), self.root
            )
        with self.assertRaisesRegex(state_module.StateError, "open Review Gate"):
            state_module.command_pause(self.writer(parked), self.root)
        self.assertEqual(
            (self.root / ".littlepowers" / "state.json").read_bytes(), before
        )

        cancelled = state_module.command_finish(
            self.writer(parked), self.root, "cancelled"
        )
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertIsNone(cancelled["review"]["gate"])
        self.assertEqual(
            cancelled["review"]["last_resolution"]["kind"], "cancelled"
        )

    def test_cancel_review_records_reason_and_resets_policy(self) -> None:
        state, _ = self.checkpoint_artifact(self.start(mode="unattended"))
        parked = self.park(state)

        cancelled = state_module.command_cancel_review(
            self.writer(parked, reason="correction"), self.root
        )

        self.assertIsNone(cancelled["review"]["gate"])
        self.assertEqual(cancelled["review"]["policy"]["mode"], "blocking")
        self.assertEqual(
            cancelled["review"]["last_resolution"]["reason"], "correction"
        )

    def test_policy_cannot_change_while_gate_is_open(self) -> None:
        state, _ = self.checkpoint_artifact(self.start())
        parked = self.park(state)
        with self.assertRaisesRegex(state_module.StateError, "open Review Gate"):
            state_module.command_set_review_policy(
                self.writer(
                    parked,
                    mode="unattended",
                    through=None,
                    wait_seconds=None,
                ),
                self.root,
            )

    def test_plan_gate_reports_incomplete_coverage_before_resolution(self) -> None:
        state = self.start(phase="spec")
        contract_path = "docs/littlepowers/specs/contract.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", contract("lean", outcomes=2)),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                phase="plan",
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Write plan",
            ),
            self.root,
        )
        state = self.resolve(self.park(state, key="spec"), "explicit_approval")
        state = state_module.command_bind_contract(
            self.writer(
                state,
                artifact=contract_path,
                approval_kind="review-gate",
                approve_scope_delta=False,
            ),
            self.root,
        )
        state = state_module.command_set_review_policy(
            self.writer(
                state,
                mode="unattended",
                through=None,
                wait_seconds=None,
            ),
            self.root,
        )
        plan = {
            "mappings": [
                {
                    "outcome": "OUT-001",
                    "tasks": ["Task 1"],
                    "evidence": ["test:first"],
                }
            ]
        }
        plan_path = "docs/littlepowers/plans/incomplete.md"
        self.write_artifact(plan_path, "# Plan\n" + protocol_block("plan-map", plan))
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"plan={plan_path}"],
                completed=["plan"],
                next_action="Review plan",
            ),
            self.root,
        )
        parked = self.park(state, key="plan")

        result = self.status(parked)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("plan_coverage_incomplete", result["reasons"])

    def test_bound_contract_source_drift_blocks_gate_atomically(self) -> None:
        state = self.start(mode="unattended", phase="spec")
        source_path = "requirements.md"
        self.write_artifact(source_path, "approved requirement\n")
        record = contract("full")
        record["sources"] = [
            {
                "id": "SRC-001",
                "path": source_path,
                "role": "requirements",
                "origin": "repository",
                "approved": True,
            }
        ]
        contract_path = "docs/littlepowers/specs/contract.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", record),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                phase="design",
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Design",
            ),
            self.root,
        )
        state = self.resolve(self.park(state, key="spec"), "unattended")
        state = state_module.command_bind_contract(
            self.writer(
                state,
                artifact=contract_path,
                approval_kind="unattended-authorization",
                approve_scope_delta=False,
            ),
            self.root,
        )
        state, _ = self.checkpoint_artifact(
            state, key="design", content="# Design\n"
        )
        parked = self.park(state, key="design")
        before = (self.root / ".littlepowers" / "state.json").read_bytes()
        self.write_artifact(source_path, "changed requirement\n")

        result = self.status(parked)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("contract_drift", result["reasons"])
        with self.assertRaisesRegex(state_module.StateError, "blocked"):
            self.resolve(parked, "unattended")
        self.assertEqual(
            (self.root / ".littlepowers" / "state.json").read_bytes(), before
        )

    def test_contract_and_plan_boundaries_require_exact_review_resolution(self) -> None:
        state = self.start(phase="spec")
        contract_path = "docs/littlepowers/specs/exact.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", contract("lean")),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Review contract",
            ),
            self.root,
        )

        with self.assertRaisesRegex(state_module.StateError, "Review Gate"):
            state_module.command_bind_contract(
                self.writer(
                    state,
                    artifact=contract_path,
                    approval_kind="review-gate",
                    approve_scope_delta=False,
                ),
                self.root,
            )

        approved = self.resolve(self.park(state, key="spec"), "explicit_approval")
        self.assertEqual(
            approved["review"]["last_resolution"]["artifact"],
            contract_path,
        )
        with self.assertRaisesRegex(state_module.StateError, "requires.*unattended"):
            state_module.command_bind_contract(
                self.writer(
                    approved,
                    artifact=contract_path,
                    approval_kind="unattended-authorization",
                    approve_scope_delta=False,
                ),
                self.root,
            )
        bound = state_module.command_bind_contract(
            self.writer(
                approved,
                artifact=contract_path,
                approval_kind="review-gate",
                approve_scope_delta=False,
            ),
            self.root,
        )
        self.assertEqual(
            bound["review"]["last_resolution"]["consumption"][
                "contract_bind_revision"
            ],
            bound["revision"],
        )
        with self.assertRaisesRegex(state_module.StateError, "already consumed"):
            state_module.command_bind_contract(
                self.writer(
                    bound,
                    artifact=contract_path,
                    approval_kind="review-gate",
                    approve_scope_delta=False,
                ),
                self.root,
            )

        plan_path = "docs/littlepowers/plans/exact.md"
        plan = {
            "mappings": [
                {
                    "outcome": "OUT-001",
                    "tasks": ["Task 1"],
                    "evidence": ["test:exact-boundary"],
                }
            ]
        }
        self.write_artifact(
            plan_path,
            "# Plan\n" + protocol_block("plan-map", plan),
        )
        plan_ready = state_module.command_checkpoint(
            self.writer(
                bound,
                phase="plan",
                artifact=[f"plan={plan_path}"],
                completed=["plan"],
                next_action="Review plan",
            ),
            self.root,
        )
        with self.assertRaisesRegex(state_module.StateError, "artifact key"):
            state_module.command_validate_plan(
                self.writer(plan_ready, artifact=plan_path), self.root
            )

        plan_approved = self.resolve(
            self.park(plan_ready, key="plan"), "explicit_approval"
        )
        planned = state_module.command_validate_plan(
            self.writer(plan_approved, artifact=plan_path), self.root
        )
        self.assertEqual(
            planned["review"]["last_resolution"]["consumption"][
                "plan_validation_revision"
            ],
            planned["revision"],
        )
        with self.assertRaisesRegex(state_module.StateError, "already consumed"):
            state_module.command_validate_plan(
                self.writer(planned, artifact=plan_path), self.root
            )
        executing = state_module.command_checkpoint(
            self.writer(planned, phase="execute"), self.root
        )
        self.assertEqual(executing["phase"], "execute")

    def test_same_bytes_at_another_path_cannot_reuse_contract_resolution(self) -> None:
        state = self.start(phase="spec")
        original = "docs/littlepowers/specs/original.md"
        copied = "docs/littlepowers/specs/copied.md"
        content = "# Contract\n" + protocol_block("contract", contract("lean"))
        self.write_artifact(original, content)
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"spec={original}"],
                completed=["spec"],
                next_action="Review contract",
            ),
            self.root,
        )
        approved = self.resolve(self.park(state, key="spec"), "explicit_approval")
        self.write_artifact(copied, content)
        redirected = state_module.command_checkpoint(
            self.writer(
                approved,
                artifact=[f"spec={copied}"],
                next_action="Bind copied contract",
            ),
            self.root,
        )

        with self.assertRaisesRegex(state_module.StateError, "approved artifact path"):
            state_module.command_bind_contract(
                self.writer(
                    redirected,
                    artifact=copied,
                    approval_kind="review-gate",
                    approve_scope_delta=False,
                ),
                self.root,
            )
        persisted = state_module.load_state(self.root)
        assert persisted is not None
        self.assertEqual(persisted["outcome_lock"]["status"], "unbound")

    def test_compact_shape_consumes_each_declared_boundary_once(self) -> None:
        state = self.start(phase="shape")
        shape_path = "docs/littlepowers/shapes/compact.md"
        content = (
            "# Compact shape\n"
            + protocol_block("contract", contract("compact"))
            + protocol_block(
                "plan-map",
                {
                    "mappings": [
                        {
                            "outcome": "OUT-001",
                            "tasks": ["Task 1"],
                            "evidence": ["test:compact-shape"],
                        }
                    ]
                },
            )
        )
        self.write_artifact(shape_path, content)
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"shape={shape_path}"],
                completed=["shape"],
                next_action="Review shape",
            ),
            self.root,
        )
        approved = self.resolve(self.park(state, key="shape"), "explicit_approval")
        bound = state_module.command_bind_contract(
            self.writer(
                approved,
                artifact=shape_path,
                approval_kind="review-gate",
                approve_scope_delta=False,
            ),
            self.root,
        )
        planned = state_module.command_validate_plan(
            self.writer(bound, artifact=shape_path), self.root
        )
        consumption = planned["review"]["last_resolution"]["consumption"]

        self.assertEqual(
            consumption["contract_bind_revision"], bound["revision"]
        )
        self.assertEqual(
            consumption["plan_validation_revision"], planned["revision"]
        )
        executing = state_module.command_checkpoint(
            self.writer(planned, phase="execute"), self.root
        )
        self.assertEqual(executing["phase"], "execute")

    def test_same_bytes_at_another_path_cannot_reuse_plan_resolution_or_execute(
        self,
    ) -> None:
        state = self.start(phase="spec")
        contract_path = "docs/littlepowers/specs/path-lock.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", contract("lean")),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Review contract",
            ),
            self.root,
        )
        state = self.resolve(self.park(state, key="spec"), "explicit_approval")
        state = state_module.command_bind_contract(
            self.writer(
                state,
                artifact=contract_path,
                approval_kind="review-gate",
                approve_scope_delta=False,
            ),
            self.root,
        )
        original = "docs/littlepowers/plans/original.md"
        copied = "docs/littlepowers/plans/copied.md"
        content = "# Plan\n" + protocol_block(
            "plan-map",
            {
                "mappings": [
                    {
                        "outcome": "OUT-001",
                        "tasks": ["Task 1"],
                        "evidence": ["test:path-lock"],
                    }
                ]
            },
        )
        self.write_artifact(original, content)
        state = state_module.command_checkpoint(
            self.writer(
                state,
                phase="plan",
                artifact=[f"plan={original}"],
                completed=["plan"],
                next_action="Review plan",
            ),
            self.root,
        )
        approved = self.resolve(self.park(state, key="plan"), "explicit_approval")
        self.write_artifact(copied, content)
        redirected = state_module.command_checkpoint(
            self.writer(
                approved,
                artifact=[f"plan={copied}"],
                next_action="Validate copied plan",
            ),
            self.root,
        )
        with self.assertRaisesRegex(state_module.StateError, "approved artifact path"):
            state_module.command_validate_plan(
                self.writer(redirected, artifact=copied), self.root
            )

        restored = state_module.command_checkpoint(
            self.writer(
                redirected,
                artifact=[f"plan={original}"],
                next_action="Validate approved plan",
            ),
            self.root,
        )
        planned = state_module.command_validate_plan(
            self.writer(restored, artifact=original), self.root
        )
        redirected_after_validation = state_module.command_checkpoint(
            self.writer(
                planned,
                artifact=[f"plan={copied}"],
                next_action="Execute copied plan",
            ),
            self.root,
        )
        with self.assertRaisesRegex(state_module.StateError, "artifact path"):
            state_module.command_checkpoint(
                self.writer(redirected_after_validation, phase="execute"),
                self.root,
            )

    def test_prerelease_resolution_without_path_or_consumption_fails_closed(
        self,
    ) -> None:
        state = self.start(phase="spec")
        contract_path = "docs/littlepowers/specs/legacy-resolution.md"
        self.write_artifact(
            contract_path,
            "# Contract\n" + protocol_block("contract", contract("lean")),
        )
        state = state_module.command_checkpoint(
            self.writer(
                state,
                artifact=[f"spec={contract_path}"],
                completed=["spec"],
                next_action="Review contract",
            ),
            self.root,
        )
        approved = self.resolve(self.park(state, key="spec"), "explicit_approval")
        legacy = json.loads(json.dumps(approved))
        resolution = legacy["review"]["last_resolution"]
        del resolution["artifact"]
        del resolution["sources_digest"]
        del resolution["consumption"]
        (self.root / ".littlepowers" / "state.json").write_text(
            json.dumps(legacy), encoding="utf-8"
        )

        loaded = state_module.load_state(self.root)
        assert loaded is not None
        with self.assertRaisesRegex(state_module.StateError, "legacy Review Gate"):
            state_module.command_bind_contract(
                self.writer(
                    loaded,
                    artifact=contract_path,
                    approval_kind="review-gate",
                    approve_scope_delta=False,
                ),
                self.root,
            )

    def test_replayed_resolution_is_harmless(self) -> None:
        state, _ = self.checkpoint_artifact(self.start(mode="unattended"))
        parked = self.park(state)
        self.resolve(parked, "unattended")

        with self.assertRaises(state_module.StateConflict):
            self.resolve(parked, "unattended")
        current = state_module.load_state(self.root)
        assert current is not None
        self.assertEqual(current["revision"], parked["revision"] + 1)

    def test_tracked_direct_cannot_park_a_review_gate(self) -> None:
        state = self.start(phase="execute", direct=True)
        with self.assertRaisesRegex(state_module.StateError, "direct"):
            self.park(state)


if __name__ == "__main__":
    unittest.main()
