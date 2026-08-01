from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "littlepowers_state.py"
CONTRACT = Path(
    "docs/littlepowers/contracts/2026-07-26-outcome-lock.md"
)
PLAN = Path("docs/littlepowers/plans/2026-07-26-outcome-lock.md")
EVIDENCE = Path("docs/littlepowers/evidence/self-host.md")


class OutcomeSelfHostTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.workflow = str(uuid.uuid4())
        self.legacy = {
            "schema_version": 2,
            "created_by": "littlepowers",
            "workflow_id": self.workflow,
            "revision": 4,
            "status": "active",
            "objective": "Implement the complete Outcome Lock candidate",
            "phase": "execute",
            "artifacts": {
                "brainstorm": (
                    "docs/littlepowers/brainstorms/"
                    "2026-07-26-outcome-lock.md"
                ),
                "spec": (
                    "docs/littlepowers/specs/2026-07-26-outcome-lock.md"
                ),
                "design": (
                    "docs/littlepowers/designs/2026-07-26-outcome-lock.md"
                ),
                "plan": PLAN.as_posix(),
                "shape": None,
            },
            "current_task": "Reconcile the legacy implementation",
            "progress": "Legacy implementation checkpoint",
            "handoff": None,
            "next_action": "Reconcile before executable progress",
            "completed": ["Approved planning"],
            "created_at": "2026-07-26T08:00:00Z",
            "updated_at": "2026-07-26T09:00:00Z",
        }
        self._copy_protocol_fixture()
        store = self.root / ".littlepowers"
        store.mkdir()
        (store / ".gitignore").write_text("*\n", encoding="utf-8")
        (store / "state.json").write_text(
            json.dumps(self.legacy), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _copy(self, relative_path: str | Path) -> None:
        relative = Path(relative_path)
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)

    def _copy_protocol_fixture(self) -> None:
        for relative_path in (
            CONTRACT,
            PLAN,
            "docs/littlepowers/specs/2026-07-26-outcome-lock.md",
            "docs/littlepowers/brainstorms/2026-07-26-outcome-lock.md",
            "docs/littlepowers/designs/2026-07-26-outcome-lock.md",
            (
                "docs/littlepowers/specs/"
                "2026-07-26-scope-integrity-lean-route.md"
            ),
            (
                "docs/littlepowers/designs/"
                "2026-07-26-scope-integrity-lean-route.md"
            ),
            "evals/results/2026-07-26-v1.1-scope-integrity.md",
            "AGENTS.md",
        ):
            self._copy(relative_path)
        for host in ("codex", "claude-code", "qoder", "opencode"):
            path = self.root / "artifacts" / "verification" / f"{host}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"{host}: shared protocol validation passed\n",
                encoding="utf-8",
            )
        self._write_verification()

    def _write_verification(self) -> None:
        record = {
            "work_unit": {
                "status": "pass",
                "evidence": ["test:self-host-cli"],
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
                    "outcome": f"OUT-{index:03d}",
                    "status": "pass",
                    "evidence": ["test:self-host-cli"],
                }
                for index in range(1, 24)
            ],
            "fidelity": [
                {
                    "id": f"FID-{index:03d}",
                    "outcome": "OUT-021",
                    "baseline": "SRC-004",
                    "evidence_path": (
                        "artifacts/verification/"
                        f"{host}.txt"
                    ),
                    "result": "pass",
                }
                for index, host in enumerate(
                    ("codex", "claude-code", "qoder", "opencode"),
                    start=1,
                )
            ],
        }
        path = self.root / EVIDENCE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "<!-- littlepowers:verification:v1 -->\n"
            "```json\n"
            f"{json.dumps(record, indent=2)}\n"
            "```\n"
            "<!-- /littlepowers:verification -->\n",
            encoding="utf-8",
        )

    def run_cli(
        self, *arguments: str, expected: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--root",
                str(self.root),
                *arguments,
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=20,
        )
        self.assertEqual(
            result.returncode,
            expected,
            f"stdout={result.stdout}\nstderr={result.stderr}",
        )
        return result

    def show(self) -> dict[str, object]:
        return json.loads(self.run_cli("show", "--json").stdout)

    def writer(self, state: dict[str, object]) -> list[str]:
        return [
            "--workflow",
            str(state["workflow_id"]),
            "--expect-revision",
            str(state["revision"]),
        ]

    def test_schema_2_reconciles_and_completes_through_the_public_cli(self) -> None:
        legacy_view = self.show()
        self.assertEqual(
            legacy_view["outcome_lock"]["status"], "reconcile_required"
        )
        self.assertEqual(
            json.loads(
                (self.root / ".littlepowers" / "state.json").read_text()
            ),
            self.legacy,
        )

        rejected = self.run_cli(
            "checkpoint",
            *self.writer(legacy_view),
            "--progress",
            "Must not execute before reconciliation",
            expected=2,
        )
        self.assertIn("reconcile", rejected.stderr)
        self.assertFalse((self.root / ".littlepowers" / "archive").exists())

        self.run_cli(
            "checkpoint",
            *self.writer(legacy_view),
            "--next-action",
            "Bind the approved Outcome Contract",
        )
        migrated = self.show()
        archives = list(
            (self.root / ".littlepowers" / "archive").glob(
                "*-pre-schema4-v2.json"
            )
        )
        self.assertEqual(len(archives), 1)
        self.assertEqual(json.loads(archives[0].read_text()), self.legacy)

        self.run_cli(
            "checkpoint",
            *self.writer(migrated),
            "--phase",
            "spec",
            "--artifact",
            f"spec={CONTRACT.as_posix()}",
            "--completed",
            "spec",
            "--next-action",
            "Review the approved Outcome Contract",
        )
        contract_ready = self.show()
        self.run_cli(
            "park-review",
            *self.writer(contract_ready),
            "--artifact-key",
            "spec",
            "--scope-delta",
            "none",
            "--unresolved-questions",
            "0",
        )
        contract_gate = self.show()
        self.run_cli(
            "resolve-review",
            *self.writer(contract_gate),
            "--kind",
            "explicit_approval",
        )
        contract_approved = self.show()
        self.run_cli(
            "bind-contract",
            *self.writer(contract_approved),
            "--artifact",
            CONTRACT.as_posix(),
            "--approval-kind",
            "review-gate",
        )
        bound = self.show()
        self.assertEqual(bound["outcome_lock"]["status"], "bound")

        self.run_cli(
            "checkpoint",
            *self.writer(bound),
            "--phase",
            "plan",
            "--artifact",
            f"plan={PLAN.as_posix()}",
            "--completed",
            "plan",
            "--next-action",
            "Review the complete Outcome Plan Map",
        )
        plan_ready = self.show()
        self.run_cli(
            "park-review",
            *self.writer(plan_ready),
            "--artifact-key",
            "plan",
            "--scope-delta",
            "none",
            "--unresolved-questions",
            "0",
        )
        plan_gate = self.show()
        self.run_cli(
            "resolve-review",
            *self.writer(plan_gate),
            "--kind",
            "explicit_approval",
        )
        plan_approved = self.show()
        self.run_cli(
            "validate-plan",
            *self.writer(plan_approved),
            "--artifact",
            PLAN.as_posix(),
        )
        planned = self.show()
        coverage = planned["outcome_lock"]["plan"]["coverage"]
        self.assertEqual(
            (coverage["mapped_active"], coverage["active_total"]),
            (23, 23),
        )

        source = (
            self.root
            / "docs/littlepowers/specs/2026-07-26-outcome-lock.md"
        )
        original_source = source.read_text(encoding="utf-8")
        source.write_text(original_source + "\nDrift\n", encoding="utf-8")
        self.run_cli("check-contract", *self.writer(planned))
        drifted = self.show()
        self.assertEqual(drifted["outcome_lock"]["status"], "drifted")
        blocked = self.run_cli(
            "checkpoint",
            *self.writer(drifted),
            "--phase",
            "verify",
            expected=2,
        )
        self.assertIn("drift", blocked.stderr)

        source.write_text(original_source, encoding="utf-8")
        self.run_cli("check-contract", *self.writer(drifted))
        restored = self.show()
        self.assertEqual(restored["outcome_lock"]["status"], "bound")
        self.run_cli(
            "checkpoint",
            *self.writer(restored),
            "--phase",
            "verify",
        )
        verifying = self.show()

        incomplete = self.run_cli(
            "complete",
            *self.writer(verifying),
            expected=2,
        )
        self.assertIn("work-unit compliance", incomplete.stderr)
        self.assertIn("approved-outcome fidelity", incomplete.stderr)
        self.assertIn("code-quality", incomplete.stderr)
        self.assertIn("Verification Record", incomplete.stderr)
        self.assertEqual(self.show()["revision"], verifying["revision"])

        self.run_cli(
            "record-verification",
            *self.writer(verifying),
            "--artifact",
            EVIDENCE.as_posix(),
        )
        verified = self.show()
        self.assertEqual(
            verified["outcome_lock"]["verification"]["verified_outcomes"],
            23,
        )
        self.assertEqual(
            verified["outcome_lock"]["baseline"]["passed_comparisons"],
            4,
        )

        self.run_cli("complete", *self.writer(verified))
        complete = self.show()
        self.assertEqual(complete["status"], "complete")
        self.assertEqual(complete["phase"], "verify")
        self.assertEqual(
            complete["outcome_lock"]["verification"]["code_quality"],
            "approve",
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


if __name__ == "__main__":
    unittest.main()
