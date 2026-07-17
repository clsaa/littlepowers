from __future__ import annotations

import json
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestTests(unittest.TestCase):
    def test_native_plugin_manifests_share_name_version_and_repository(self) -> None:
        codex = read_json(ROOT / ".codex-plugin" / "plugin.json")
        claude = read_json(ROOT / ".claude-plugin" / "plugin.json")

        self.assertEqual(codex["name"], "littlepowers")
        self.assertEqual(claude["name"], "littlepowers")
        self.assertEqual(codex["version"], "0.3.0-alpha.1")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["repository"], codex["repository"])
        self.assertIn("Claude Code", codex["description"])

        self.assertEqual(codex["skills"], "./skills/")
        self.assertNotIn("hooks", codex)
        self.assertTrue((ROOT / "hooks" / "hooks.json").is_file())
        self.assertEqual(codex["interface"]["category"], "Developer Tools")

    def test_codex_marketplace_points_to_repository_root(self) -> None:
        marketplace = read_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        self.assertEqual(marketplace["name"], "littlepowers")
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "littlepowers")
        self.assertEqual(entry["source"], {"source": "url", "url": "./"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")

    def test_claude_marketplace_matches_plugin_release(self) -> None:
        manifest = read_json(ROOT / ".claude-plugin" / "plugin.json")
        marketplace = read_json(ROOT / ".claude-plugin" / "marketplace.json")

        self.assertEqual(marketplace["name"], "littlepowers")
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(entry["version"], manifest["version"])
        self.assertEqual(entry["description"], manifest["description"])
        self.assertEqual(entry["source"], "./")

    def test_hook_manifest_registers_recovery_boundaries(self) -> None:
        hooks = read_json(ROOT / "hooks" / "hooks.json")
        self.assertEqual(
            set(hooks["hooks"]),
            {"SessionStart", "UserPromptSubmit", "SubagentStart"},
        )
        registration = hooks["hooks"]["SessionStart"][0]
        self.assertEqual(registration["matcher"], "startup|resume|clear|compact")
        self.assertNotIn("matcher", hooks["hooks"]["UserPromptSubmit"][0])

        for event in ("SessionStart", "UserPromptSubmit", "SubagentStart"):
            with self.subTest(event=event):
                command_hook = hooks["hooks"][event][0]["hooks"][0]
                self.assertEqual(command_hook["type"], "command")
                self.assertEqual(command_hook["timeout"], 5)
                self.assertEqual(command_hook["shell"], "bash")
                self.assertIn("${CLAUDE_PLUGIN_ROOT}", command_hook["command"])
                self.assertIn("run-hook.cmd", command_hook["command"])

        launcher = ROOT / "hooks" / "run-hook.cmd"
        self.assertTrue(launcher.is_file())
        if os.name != "nt":
            self.assertTrue(os.access(launcher, os.X_OK))

    def test_skills_have_clean_frontmatter_and_ui_metadata(self) -> None:
        expected = {
            "brainstorming",
            "compact-shaping",
            "debugging-systematically",
            "designing-solutions",
            "executing-plans",
            "managing-littlepowers",
            "reviewing-changes",
            "using-littlepowers",
            "verifying-work",
            "writing-plans",
            "writing-specs",
        }
        skill_directories = {
            path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
        }
        self.assertEqual(skill_directories, expected)

        for name in expected:
            with self.subTest(skill=name):
                skill_text = (ROOT / "skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertNotIn("[TODO", skill_text)
                self.assertTrue(skill_text.startswith("---\n"))
                frontmatter = skill_text.split("---\n", 2)[1]
                keys = {
                    line.split(":", 1)[0]
                    for line in frontmatter.splitlines()
                    if ":" in line
                }
                self.assertEqual(keys, {"name", "description"})
                self.assertIn(f"name: {name}", frontmatter)

                metadata = (
                    ROOT / "skills" / name / "agents" / "openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn(f"${name}", metadata)

    def test_workflow_artifacts_cover_all_preimplementation_phases(self) -> None:
        for phase in ("brainstorms", "specs", "designs", "plans"):
            with self.subTest(phase=phase):
                files = list((ROOT / "docs" / "littlepowers" / phase).glob("*.md"))
                self.assertGreaterEqual(len(files), 2)

    def test_both_durable_guidance_snippets_exist(self) -> None:
        agents = (ROOT / "assets" / "agents-snippet.md").read_text(encoding="utf-8")
        claude = (ROOT / "assets" / "claude-snippet.md").read_text(encoding="utf-8")
        self.assertIn("littlepowers:using-littlepowers", agents)
        self.assertIn("littlepowers:using-littlepowers", claude)

    def test_internal_phase_skills_gate_direct_invocation(self) -> None:
        internal = {
            "brainstorming",
            "compact-shaping",
            "designing-solutions",
            "writing-plans",
            "writing-specs",
        }
        for name in internal:
            with self.subTest(skill=name):
                skill = (ROOT / "skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                frontmatter = skill.split("---\n", 2)[1]
                self.assertIn("using-littlepowers", frontmatter)
                self.assertIn("active state", frontmatter)

    def test_public_trust_and_contribution_files_exist(self) -> None:
        required = (
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "README.zh-CN.md",
            "SECURITY.md",
            "docs/capability-matrix.md",
            "docs/expert-review.md",
            "docs/inspiration.md",
            "docs/model-compatibility.md",
            "docs/security-model.md",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug.yml",
            ".github/ISSUE_TEMPLATE/compatibility.yml",
            ".github/ISSUE_TEMPLATE/feature.yml",
        )
        for relative_path in required:
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_readme_calibrates_recovery_and_model_claims(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("cannot force a model", readme)
        self.assertIn("UserPromptSubmit", readme)
        self.assertIn("coordinator is the only ledger writer", readme)
        self.assertIn("0.3.0-alpha.1", readme)
        self.assertNotIn("Follow-up messages do not silently replace", readme)


if __name__ == "__main__":
    unittest.main()
