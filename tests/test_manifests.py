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
        self.assertEqual(codex["version"], "0.2.0")
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

    def test_hook_manifest_registers_portable_session_start(self) -> None:
        hooks = read_json(ROOT / "hooks" / "hooks.json")
        self.assertEqual(set(hooks["hooks"]), {"SessionStart"})
        registration = hooks["hooks"]["SessionStart"][0]
        self.assertEqual(registration["matcher"], "startup|resume|clear|compact")

        command_hook = registration["hooks"][0]
        self.assertEqual(command_hook["type"], "command")
        self.assertEqual(command_hook["timeout"], 5)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", command_hook["command"])
        self.assertIn("run-hook.cmd", command_hook["command"])

        launcher = ROOT / "hooks" / "run-hook.cmd"
        self.assertTrue(launcher.is_file())
        if os.name != "nt":
            self.assertTrue(os.access(launcher, os.X_OK))

    def test_skills_have_clean_frontmatter_and_ui_metadata(self) -> None:
        expected = {
            "brainstorming",
            "designing-solutions",
            "executing-plans",
            "using-littlepowers",
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
                self.assertEqual(len(files), 1)

    def test_both_durable_guidance_snippets_exist(self) -> None:
        agents = (ROOT / "assets" / "agents-snippet.md").read_text(encoding="utf-8")
        claude = (ROOT / "assets" / "claude-snippet.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("littlepowers:using-littlepowers", agents)
        self.assertIn("littlepowers:using-littlepowers", claude)


if __name__ == "__main__":
    unittest.main()
