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
        self.assertIn("reviewing-changes", skill)
        self.assertIn("tiny isolated changes", skill)
        self.assertIn("does not create a reviewer or select a model", skill)

    def test_plan_contract(self) -> None:
        skill = read_skill("writing-plans").lower()

        self.assertIn("global constraints", skill)
        self.assertIn("named interfaces", skill)
        self.assertIn("rollback coupling", skill)
        self.assertIn("local, connected, or broad", skill)
        self.assertIn("broad suite", skill)

    def test_review_contract(self) -> None:
        skill = read_skill("reviewing-changes").lower()

        self.assertIn("staying read-only", skill)
        self.assertIn("do not edit code", skill)
        self.assertIn("do not include a proposed verdict", skill)
        self.assertIn("acceptance/spec compliance", skill)
        self.assertIn("pass`, `fail`, or `blocked", skill)
        self.assertIn("code quality", skill)
        self.assertIn("approve`, `request changes`, or `blocked", skill)
        self.assertIn("exact file and line", skill)
        self.assertIn("concrete consequence", skill)
        self.assertIn("supporting code or test evidence", skill)
        self.assertIn("repair direction", skill)
        self.assertIn("critical and important findings block completion", skill)
        self.assertIn("coordinator verifies every finding technically", skill)
        self.assertIn("tiny isolated change", skill)

    def test_new_disciplines_are_model_neutral(self) -> None:
        disciplines = "\n".join(
            read_skill(name).lower()
            for name in (
                "debugging-systematically",
                "reviewing-changes",
                "verifying-work",
            )
        )

        for model_or_setting in (
            "gpt-",
            "fable",
            "opus",
            "reasoning.effort",
            "reasoning_effort",
            "model_reasoning_effort",
            "spawn_agent",
        ):
            with self.subTest(forbidden=model_or_setting):
                self.assertNotIn(model_or_setting, disciplines)


if __name__ == "__main__":
    unittest.main()
