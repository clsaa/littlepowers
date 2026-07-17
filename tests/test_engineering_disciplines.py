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


if __name__ == "__main__":
    unittest.main()
