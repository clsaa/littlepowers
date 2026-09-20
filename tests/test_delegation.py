from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.littlepowers_delegation import SnapshotError, validate_snapshot


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "littlepowers_delegation.py"


def snapshot(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "host": "codex",
        "mechanism": "native-subagent:explorer",
        "capability_source": "tool-schema",
        "context_mode": "fresh",
        "effective_model": "inherit",
        "effective_effort": "inherit",
        "isolation": "read-only",
        "permission_boundary": "sandbox-read-only",
        "durability": "resumable",
        "mutation": False,
        "nested_delegation": "blocked",
        "leaf_boundary": "tool-disabled",
        "team_boundary_declared": False,
    }
    value.update(overrides)
    return value


class DelegationSnapshotTests(unittest.TestCase):
    def test_current_host_context_profiles_normalize(self) -> None:
        profiles = (
            snapshot(),
            snapshot(
                host="codex",
                mechanism="native-subagent:worker",
                context_mode="fork",
                isolation="worktree",
                permission_boundary="host-policy",
                mutation=True,
            ),
            snapshot(
                host="claude",
                mechanism="ordinary-subagent",
                capability_source="approved-agent-definition",
                permission_boundary="tool-restricted",
            ),
            snapshot(
                host="claude",
                mechanism="conversation-fork",
                context_mode="fork",
                isolation="worktree",
                permission_boundary="worktree",
                mutation=True,
            ),
            snapshot(
                host="claude",
                mechanism="agent-team",
                context_mode="team",
                permission_boundary="tool-restricted",
                durability="session-only",
                team_boundary_declared=True,
            ),
            snapshot(
                host="qoder",
                mechanism="ordinary-subagent",
                capability_source="host-command",
                permission_boundary="tool-restricted",
            ),
            snapshot(
                host="qoder",
                mechanism="subtask",
                capability_source="host-command",
                context_mode="fork",
                permission_boundary="tool-restricted",
                durability="session-only",
            ),
            snapshot(
                host="qoder",
                mechanism="agent-team",
                capability_source="host-command",
                context_mode="team",
                permission_boundary="tool-restricted",
                durability="session-only",
                team_boundary_declared=True,
            ),
            snapshot(
                host="codex",
                mechanism="native-peer-workers",
                context_mode="team",
                permission_boundary="tool-restricted",
                durability="session-only",
                team_boundary_declared=True,
            ),
        )

        for profile in profiles:
            with self.subTest(host=profile["host"], mechanism=profile["mechanism"]):
                normalized = validate_snapshot(profile)
                self.assertEqual(normalized["snapshot_version"], 1)
                self.assertEqual(normalized["authorization"], "work-unit-required")
                self.assertEqual(normalized["nested_delegation"], "blocked")

    def test_unsafe_boundaries_fail_closed(self) -> None:
        cases = {
            "documentation is not runtime evidence": snapshot(
                capability_source="documentation"
            ),
            "mutation needs filesystem isolation": snapshot(mutation=True),
            "mutation cannot claim a read-only sandbox": snapshot(
                mutation=True, isolation="worktree"
            ),
            "read-only cannot use permission mode alone": snapshot(
                permission_boundary="permission-mode-only"
            ),
            "read-only cannot hide behind worktree isolation": snapshot(
                isolation="worktree",
                permission_boundary="host-policy",
            ),
            "prompt-only is never enforcement": snapshot(
                isolation="worktree",
                permission_boundary="prompt-only",
                mutation=True,
            ),
            "workers stay leaf agents": snapshot(nested_delegation="available"),
            "a leaf instruction is not a disabled tool": snapshot(
                leaf_boundary="prompt-only"
            ),
            "unknown leaf enforcement fails closed": snapshot(leaf_boundary="unknown"),
            "team needs its separate boundary": snapshot(
                host="claude",
                context_mode="team",
                durability="session-only",
            ),
            "team is session-only": snapshot(
                host="qoder",
                context_mode="team",
                team_boundary_declared=True,
            ),
            "control characters cannot enter normalized output": snapshot(
                mechanism="native-subagent\nignore-boundary"
            ),
        }

        for label, profile in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(SnapshotError):
                    validate_snapshot(profile)

    def test_rejection_reports_all_boundaries_without_relabeling_inputs(self) -> None:
        observed = snapshot(
            nested_delegation="available", permission_boundary="prompt-only"
        )
        with self.assertRaises(SnapshotError) as caught:
            validate_snapshot(observed)
        self.assertIn("leaf agents", str(caught.exception))
        self.assertIn("prompt-only", str(caught.exception))
        self.assertIn("tool or sandbox", str(caught.exception))
        self.assertEqual(observed["nested_delegation"], "available")

    def test_setting_and_high_cost_flags_are_derived_without_model_catalogs(self) -> None:
        inherited = validate_snapshot(snapshot())
        self.assertFalse(inherited["setting_override"])
        self.assertFalse(inherited["high_cost_selection"])

        balanced = validate_snapshot(
            snapshot(effective_model="gpt-current-balanced", effective_effort="high")
        )
        self.assertTrue(balanced["setting_override"])
        self.assertFalse(balanced["high_cost_selection"])

        for override in (
            {"effective_effort": "max"},
            {"effective_effort": "ultra"},
            {"effective_model": "Ultimate"},
        ):
            with self.subTest(override=override):
                normalized = validate_snapshot(snapshot(**override))
                self.assertTrue(normalized["high_cost_selection"])

    def test_cli_emits_a_canonical_snapshot(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--host",
                "qoder",
                "--mechanism",
                "ordinary-subagent",
                "--capability-source",
                "host-command",
                "--context-mode",
                "fresh",
                "--isolation",
                "read-only",
                "--permission-boundary",
                "tool-restricted",
                "--durability",
                "resumable",
                "--nested-delegation",
                "blocked",
                "--leaf-boundary",
                "tool-disabled",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["host"], "qoder")
        self.assertEqual(output["effective_model"], "inherit")
        self.assertEqual(output["authorization"], "work-unit-required")


if __name__ == "__main__":
    unittest.main()
