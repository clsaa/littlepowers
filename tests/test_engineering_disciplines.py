from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


class EngineeringDisciplineTests(unittest.TestCase):
    def test_debugging_contract(self) -> None:
        skill = read_skill("debugging-systematically").lower()

        self.assertIn("diagnosis-only", skill)
        self.assertIn("do not edit during diagnosis-only", skill)
        self.assertIn("narrowest reliable reproducer", skill)
        self.assertIn("earliest point", skill)
        self.assertIn("one falsifiable hypothesis at a time", skill)
        self.assertIn("after three failed fix hypotheses, stop patching", skill)
        self.assertIn("original reproducer", skill)
        self.assertIn("regression coverage", skill)

    def test_verification_contract(self) -> None:
        skill = read_skill("verifying-work").lower()

        self.assertIn("after any relevant code", skill)
        self.assertIn("local:", skill)
        self.assertIn("connected:", skill)
        self.assertIn("broad:", skill)
        self.assertIn("plausible rollback boundary", skill)
        self.assertIn("a full suite is not the default after every small edit", skill)
        self.assertIn("original reproducer", skill)
        self.assertIn("exit status", skill)
        self.assertIn("relevant observed signal", skill)
        self.assertIn("worker reports as inputs", skill)
        self.assertIn("debug statements", skill)

    def test_execution_integration(self) -> None:
        skill = read_skill("executing-plans").lower()

        self.assertIn("debugging-systematically", skill)
        self.assertIn("verifying-work", skill)
        self.assertIn("impact and rollback scope", skill)
        self.assertIn("a full suite is not the default after every small edit", skill)
        self.assertIn("worker reports are inputs", skill)

    def test_plan_contract(self) -> None:
        skill = read_skill("writing-plans").lower()

        self.assertIn("global constraints", skill)
        self.assertIn("named interfaces", skill)
        self.assertIn("rollback coupling", skill)
        self.assertIn("local, connected, or broad", skill)
        self.assertIn("broad suite", skill)


if __name__ == "__main__":
    unittest.main()
