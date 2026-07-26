from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import littlepowers_state as state_module  # noqa: E402


def protocol_block(kind: str, value: object, *, prose: str = "") -> str:
    payload = json.dumps(value, ensure_ascii=False, indent=2)
    return (
        f"{prose}\n"
        f"<!-- littlepowers:{kind}:v1 -->\n"
        "```json\n"
        f"{payload}\n"
        "```\n"
        f"<!-- /littlepowers:{kind} -->\n"
    )


def base_contract() -> dict[str, object]:
    return {
        "route": "full",
        "sources": [
            {
                "id": "SRC-001",
                "path": "docs/product/prd.md",
                "role": "requirements",
                "origin": "user",
                "approved": True,
            },
            {
                "id": "SRC-002",
                "path": "docs/product/home.png",
                "role": "prototype",
                "origin": "user",
                "approved": True,
            },
        ],
        "scope_delta": {"status": "none", "consequences": []},
        "baseline": {"requirement": "required", "source_ids": ["SRC-002"]},
        "review": {"code_quality_required": True},
        "outcomes": [
            {
                "id": "OUT-002",
                "title": "The result can be shared",
                "disposition": "active",
            },
            {
                "id": "OUT-001",
                "title": "The approved home state is complete",
                "disposition": "active",
            },
        ],
        "fidelity": [
            {
                "id": "FID-001",
                "outcome": "OUT-001",
                "baseline": "SRC-002",
                "surface": "home",
                "action": "open",
                "state": "default",
            }
        ],
    }


def base_plan_map() -> dict[str, object]:
    return {
        "mappings": [
            {
                "outcome": "OUT-002",
                "tasks": ["Task 4"],
                "evidence": ["test:share-flow"],
            },
            {
                "outcome": "OUT-001",
                "tasks": ["Task 2"],
                "evidence": ["visual:approved-home", "test:home-state"],
            },
        ]
    }


def base_verification() -> dict[str, object]:
    return {
        "work_unit": {
            "status": "pass",
            "evidence": ["test:focused-state-suite"],
        },
        "outcome_fidelity": {
            "status": "pass",
            "evidence": ["inspection:outcome-traceability"],
        },
        "code_quality": {
            "required": True,
            "status": "approve",
            "evidence": ["review:integrated-diff"],
        },
        "blocking_evidence": [],
        "outcomes": [
            {
                "outcome": "OUT-002",
                "status": "pass",
                "evidence": ["test:share-flow"],
            },
            {
                "outcome": "OUT-001",
                "status": "pass",
                "evidence": ["test:home-state", "visual:approved-home"],
            },
        ],
        "fidelity": [
            {
                "id": "FID-001",
                "outcome": "OUT-001",
                "baseline": "SRC-002",
                "evidence_path": "artifacts/verification/home-default.png",
                "result": "pass",
            }
        ],
    }


class OutcomeRecordTests(unittest.TestCase):
    def test_contract_parser_ignores_prose_and_normalizes_entity_order(self) -> None:
        first = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract(), prose="# Approved contract")
        )
        reordered = base_contract()
        reordered["sources"] = list(reversed(reordered["sources"]))
        reordered["outcomes"] = list(reversed(reordered["outcomes"]))
        second = state_module.parse_outcome_contract(
            protocol_block("contract", reordered).replace("\n", "\r\n")
        )

        self.assertEqual(first, second)
        self.assertEqual(
            [item["id"] for item in first["outcomes"]],
            ["OUT-001", "OUT-002"],
        )
        self.assertEqual(
            state_module.protocol_digest(first),
            state_module.protocol_digest(second),
        )
        self.assertRegex(
            state_module.protocol_digest(first),
            r"^sha256:[0-9a-f]{64}$",
        )

    def test_parser_requires_exactly_one_exact_tagged_block(self) -> None:
        block = protocol_block("contract", base_contract())

        with self.assertRaisesRegex(state_module.StateError, "exactly one"):
            state_module.parse_outcome_contract("# prose only")
        with self.assertRaisesRegex(state_module.StateError, "exactly one"):
            state_module.parse_outcome_contract(block + block)
        with self.assertRaisesRegex(state_module.StateError, "contract"):
            state_module.parse_outcome_contract(
                block.replace("```json", "```javascript", 1)
            )

    def test_parser_rejects_duplicate_json_keys_and_unknown_fields(self) -> None:
        duplicate = (
            "<!-- littlepowers:contract:v1 -->\n"
            "```json\n"
            '{"route":"full","route":"lean"}\n'
            "```\n"
            "<!-- /littlepowers:contract -->\n"
        )
        with self.assertRaisesRegex(state_module.StateError, "duplicate JSON key"):
            state_module.parse_outcome_contract(duplicate)

        contract = base_contract()
        contract["surprise"] = True
        with self.assertRaisesRegex(state_module.StateError, "unknown or missing keys"):
            state_module.parse_outcome_contract(
                protocol_block("contract", contract)
            )

    def test_contract_rejects_duplicate_ids_unsafe_paths_and_excessive_counts(
        self,
    ) -> None:
        duplicate = base_contract()
        duplicate["sources"][1]["id"] = "SRC-001"
        with self.assertRaisesRegex(state_module.StateError, "duplicate source ID"):
            state_module.parse_outcome_contract(
                protocol_block("contract", duplicate)
            )

        unsafe = base_contract()
        unsafe["sources"][0]["path"] = "../outside.md"
        with self.assertRaisesRegex(state_module.StateError, "must not contain"):
            state_module.parse_outcome_contract(protocol_block("contract", unsafe))

        excessive = base_contract()
        excessive["outcomes"] = [
            {
                "id": f"OUT-{index:03d}",
                "title": f"Outcome {index}",
                "disposition": "active",
            }
            for index in range(1, state_module.MAX_OUTCOMES + 2)
        ]
        with self.assertRaisesRegex(state_module.StateError, "outcomes exceeds"):
            state_module.parse_outcome_contract(
                protocol_block("contract", excessive)
            )

    def test_contract_enforces_scope_delta_rules(self) -> None:
        undeclared = base_contract()
        undeclared["outcomes"][0]["disposition"] = "deferred"
        with self.assertRaisesRegex(state_module.StateError, "scope_delta.status=none"):
            state_module.parse_outcome_contract(
                protocol_block("contract", undeclared)
            )

        empty_proposal = base_contract()
        empty_proposal["scope_delta"] = {
            "status": "proposed",
            "consequences": [],
        }
        empty_proposal["outcomes"][0]["disposition"] = "changed"
        with self.assertRaisesRegex(state_module.StateError, "consequence"):
            state_module.parse_outcome_contract(
                protocol_block("contract", empty_proposal)
            )

    def test_contract_enforces_baseline_provenance_and_fidelity_links(self) -> None:
        implementation_baseline = base_contract()
        implementation_baseline["sources"][1]["origin"] = "implementation"
        with self.assertRaisesRegex(state_module.StateError, "approved baseline"):
            state_module.parse_outcome_contract(
                protocol_block("contract", implementation_baseline)
            )

        unknown_outcome = base_contract()
        unknown_outcome["fidelity"][0]["outcome"] = "OUT-099"
        with self.assertRaisesRegex(state_module.StateError, "active outcome"):
            state_module.parse_outcome_contract(
                protocol_block("contract", unknown_outcome)
            )

        nonvisual = base_contract()
        nonvisual["baseline"] = {
            "requirement": "not_applicable",
            "source_ids": [],
        }
        nonvisual["fidelity"] = []
        parsed = state_module.parse_outcome_contract(
            protocol_block("contract", nonvisual)
        )
        self.assertEqual(parsed["baseline"]["requirement"], "not_applicable")

    def test_plan_parser_validates_tokens_and_rejects_duplicate_mappings(self) -> None:
        invalid_token = base_plan_map()
        invalid_token["mappings"][0]["evidence"] = ["unknown-kind:evidence"]
        with self.assertRaisesRegex(state_module.StateError, "evidence token"):
            state_module.parse_outcome_plan_map(
                protocol_block("plan-map", invalid_token)
            )

        duplicate = base_plan_map()
        duplicate["mappings"][1]["outcome"] = "OUT-002"
        with self.assertRaisesRegex(state_module.StateError, "duplicate mapping"):
            state_module.parse_outcome_plan_map(
                protocol_block("plan-map", duplicate)
            )

    def test_coverage_reports_every_missing_and_unknown_outcome(self) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        plan = base_plan_map()
        plan["mappings"] = [
            {
                "outcome": "OUT-099",
                "tasks": ["Task 9"],
                "evidence": ["test:unknown"],
            }
        ]
        parsed_plan = state_module.parse_outcome_plan_map(
            protocol_block("plan-map", plan)
        )

        coverage = state_module.evaluate_plan_coverage(contract, parsed_plan)

        self.assertEqual(coverage["original_total"], 2)
        self.assertEqual(coverage["active_total"], 2)
        self.assertEqual(coverage["mapped_active"], 0)
        self.assertEqual(coverage["missing"], ["OUT-001", "OUT-002"])
        self.assertEqual(coverage["unknown"], ["OUT-099"])
        self.assertEqual(coverage["status"], "fail")

    def test_coverage_requires_distinct_scope_delta_approval(self) -> None:
        changed = base_contract()
        changed["scope_delta"] = {
            "status": "proposed",
            "consequences": ["OUT-002 changes its public result format"],
        }
        changed["outcomes"][0]["disposition"] = "changed"
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", changed)
        )
        plan = state_module.parse_outcome_plan_map(
            protocol_block("plan-map", base_plan_map())
        )

        pending = state_module.evaluate_plan_coverage(contract, plan)
        approved = state_module.evaluate_plan_coverage(
            contract, plan, scope_delta_approved=True
        )

        self.assertEqual(pending["status"], "fail")
        self.assertTrue(pending["scope_delta_approval_required"])
        self.assertEqual(approved["status"], "pass")
        self.assertFalse(approved["scope_delta_approval_required"])

    def test_verification_accepts_independent_passing_verdicts(self) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        verification = state_module.parse_outcome_verification(
            protocol_block("verification", base_verification())
        )

        summary = state_module.evaluate_outcome_verification(
            contract, verification
        )

        self.assertEqual(summary["work_unit"], "pass")
        self.assertEqual(summary["outcome_fidelity"], "pass")
        self.assertEqual(summary["code_quality"], "approve")
        self.assertEqual(summary["blocking_evidence"], 0)
        self.assertEqual(summary["verified_outcomes"], 2)
        self.assertEqual(summary["passed_comparisons"], 1)

    def test_verification_accepts_consistent_fail_without_promoting_work_unit(
        self,
    ) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        failed = base_verification()
        failed["outcome_fidelity"]["status"] = "fail"
        failed["outcomes"][0]["status"] = "fail"
        failed["outcomes"][0]["evidence"] = ["test:share-flow-failure"]
        verification = state_module.parse_outcome_verification(
            protocol_block("verification", failed)
        )

        summary = state_module.evaluate_outcome_verification(
            contract, verification
        )

        self.assertEqual(summary["work_unit"], "pass")
        self.assertEqual(summary["outcome_fidelity"], "fail")

    def test_verification_rejects_missing_rows_and_contradictory_aggregate(
        self,
    ) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        missing = base_verification()
        missing["outcomes"] = missing["outcomes"][:1]
        parsed_missing = state_module.parse_outcome_verification(
            protocol_block("verification", missing)
        )
        with self.assertRaisesRegex(state_module.StateError, "missing outcomes.*OUT-001"):
            state_module.evaluate_outcome_verification(contract, parsed_missing)

        contradiction = base_verification()
        contradiction["fidelity"][0]["result"] = "blocked"
        parsed_contradiction = state_module.parse_outcome_verification(
            protocol_block("verification", contradiction)
        )
        with self.assertRaisesRegex(state_module.StateError, "outcome_fidelity"):
            state_module.evaluate_outcome_verification(
                contract, parsed_contradiction
            )

    def test_fidelity_evidence_cannot_be_the_approved_baseline_itself(
        self,
    ) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        self_comparison = base_verification()
        self_comparison["fidelity"][0]["evidence_path"] = (
            "docs/product/home.png"
        )
        verification = state_module.parse_outcome_verification(
            protocol_block("verification", self_comparison)
        )

        with self.assertRaisesRegex(
            state_module.StateError,
            "implementation evidence must differ",
        ):
            state_module.evaluate_outcome_verification(
                contract, verification
            )

    def test_verification_enforces_contract_code_quality_requirement(self) -> None:
        contract = state_module.parse_outcome_contract(
            protocol_block("contract", base_contract())
        )
        wrong = base_verification()
        wrong["code_quality"] = {
            "required": False,
            "status": "not_required",
            "evidence": [],
        }
        verification = state_module.parse_outcome_verification(
            protocol_block("verification", wrong)
        )

        with self.assertRaisesRegex(state_module.StateError, "code_quality.required"):
            state_module.evaluate_outcome_verification(contract, verification)

    def test_completion_failures_are_aggregate_and_deterministic(self) -> None:
        lock = {
            "status": "drifted",
            "scope_delta": {"status": "reconcile_required"},
            "plan": {"coverage": {"status": "pending"}},
            "baseline": {"status": "blocked"},
            "verification": {
                "work_unit": "pass",
                "outcome_fidelity": "blocked",
                "code_quality": "request_changes",
                "blocking_evidence": 2,
            },
        }

        failures = state_module.outcome_lock_completion_failures(lock)

        self.assertEqual(
            failures,
            [
                "contract status must be bound",
                "scope delta must be none or approved",
                "outcome coverage must pass",
                "approved baseline must pass or be not_applicable",
                "approved-outcome fidelity must pass",
                "required code-quality review must approve",
                "blocking evidence must be zero",
            ],
        )


if __name__ == "__main__":
    unittest.main()
