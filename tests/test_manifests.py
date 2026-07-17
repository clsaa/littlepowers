from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_plugin_manifest_matches_repository(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "littlepowers")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertNotIn("hooks", manifest)
        self.assertTrue((ROOT / "hooks" / "hooks.json").is_file())
        self.assertEqual(manifest["interface"]["category"], "Developer Tools")

    def test_marketplace_points_to_repository_root(self) -> None:
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(marketplace["name"], "littlepowers")
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "littlepowers")
        self.assertEqual(entry["source"], {"source": "url", "url": "./"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")

    def test_hook_manifest_registers_only_session_start(self) -> None:
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(set(hooks["hooks"]), {"SessionStart"})
        registration = hooks["hooks"]["SessionStart"][0]
        self.assertEqual(registration["matcher"], "startup|resume|clear|compact")
        self.assertIn("$PLUGIN_ROOT", registration["hooks"][0]["command"])

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


if __name__ == "__main__":
    unittest.main()
