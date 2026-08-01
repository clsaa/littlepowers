from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.littlepowers_state import parse_outcome_contract


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestTests(unittest.TestCase):
    def test_native_plugin_manifests_share_name_version_and_repository(self) -> None:
        codex = read_json(ROOT / ".codex-plugin" / "plugin.json")
        claude = read_json(ROOT / ".claude-plugin" / "plugin.json")

        self.assertEqual(codex["name"], "littlepowers")
        self.assertEqual(claude["name"], "littlepowers")
        self.assertEqual(codex["version"], "1.3.0")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["repository"], codex["repository"])
        self.assertIn("Claude Code", codex["description"])
        self.assertIn("verification", codex["description"])

        self.assertEqual(codex["skills"], "./skills/")
        self.assertNotIn("hooks", codex)
        self.assertTrue((ROOT / "hooks" / "hooks.json").is_file())
        self.assertEqual(codex["interface"]["category"], "Developer Tools")
        prompts = codex["interface"]["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(any("rollback scope" in prompt for prompt in prompts))

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

    def test_qoder_manifest_shares_release_identity(self) -> None:
        codex = read_json(ROOT / ".codex-plugin" / "plugin.json")
        qoder = read_json(ROOT / ".qoder-plugin" / "plugin.json")

        self.assertEqual(qoder["name"], "littlepowers")
        self.assertEqual(qoder["version"], codex["version"])
        self.assertEqual(qoder["repository"], codex["repository"])
        self.assertIn("Qoder", qoder["description"])

        hooks = read_json(ROOT / "hooks" / "hooks.json")
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}", command)

        hook_source = (ROOT / "hooks" / "session-start.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("QODER_PLUGIN_ROOT", hook_source)

    def test_opencode_plugin_registers_skills_and_injects_read_only(self) -> None:
        package = read_json(ROOT / "package.json")
        self.assertEqual(package["name"], "littlepowers")
        self.assertEqual(package["version"], "1.3.0")
        self.assertEqual(package["main"], ".opencode/plugins/littlepowers.js")
        self.assertEqual(package["type"], "module")
        self.assertNotIn("dependencies", package)

        plugin_path = ROOT / ".opencode" / "plugins" / "littlepowers.js"
        plugin = plugin_path.read_text(encoding="utf-8")
        self.assertIn("export const LittlepowersPlugin", plugin)
        self.assertIn("config.skills.paths", plugin)
        self.assertIn("experimental.chat.messages.transform", plugin)
        self.assertIn("session-start.py", plugin)
        self.assertIn("SessionStart", plugin)
        self.assertIn("UserPromptSubmit", plugin)
        self.assertIn("finish(null)", plugin)
        self.assertIn("error.code === 'ENOENT'", plugin)

        node = shutil.which("node")
        if node:
            result = subprocess.run(
                [node, "--check", str(plugin_path)],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_planning_phases_use_deterministic_review_lease_gates(self) -> None:
        router = (ROOT / "skills" / "using-littlepowers" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Review phase boundaries", router)
        for mode in (
            "blocking",
            "implementation_mandate",
            "windowed",
            "unattended",
        ):
            self.assertIn(mode, router)
        self.assertIn("review-status", router)
        self.assertIn("--observed-no-intervention", router)

        gated = {
            "brainstorming": ("brainstorm", "writing-plans"),
            "writing-specs": ("spec", "designing-solutions"),
            "designing-solutions": ("design", "writing-plans"),
            "writing-plans": ("plan", "executing-plans"),
            "compact-shaping": ("shape", "executing-plans"),
        }
        for name, (artifact_key, next_skill) in gated.items():
            with self.subTest(skill=name):
                skill = (ROOT / "skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(f"park-review --artifact-key {artifact_key}", skill)
                self.assertIn("blocking", skill)
                self.assertIn(f"`{next_skill}`", skill)

        reference = (ROOT / "references" / "review-lease.md").read_text(
            encoding="utf-8"
        )
        for command in (
            "set-review-policy",
            "park-review",
            "review-status",
            "resolve-review",
            "cancel-review",
        ):
            self.assertIn(command, reference)
        self.assertIn("same-task one-shot Scheduled Task", reference)
        self.assertIn("claude -p --resume", reference)

    def test_lean_route_runs_brainstorm_then_plan_without_spec_or_design(self) -> None:
        router = (
            ROOT / "skills" / "using-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        brainstorm = (
            ROOT / "skills" / "brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        writing = (
            ROOT / "skills" / "writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("### Lean plan", router)
        self.assertIn(
            "`brainstorming` → `writing-plans` → `executing-plans`",
            router,
        )
        self.assertIn("Do not create a specification or design artifact", router)
        self.assertIn("Lean route", brainstorm)
        self.assertIn("--phase plan", brainstorm)
        self.assertIn("`writing-plans`", brainstorm)
        self.assertIn("brainstorm or design", writing)
        self.assertIn("lean route", writing.lower())

    def test_scope_integrity_prevents_implicit_product_slices(self) -> None:
        router = (
            ROOT / "skills" / "using-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        brainstorm = (
            ROOT / "skills" / "brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        specification = (
            ROOT / "skills" / "writing-specs" / "SKILL.md"
        ).read_text(encoding="utf-8")
        design = (
            ROOT / "skills" / "designing-solutions" / "SKILL.md"
        ).read_text(encoding="utf-8")
        plan = (
            ROOT / "skills" / "writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        execution = (
            ROOT / "skills" / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for skill in (router, brainstorm, specification, design, plan, execution):
            with self.subTest(skill=skill[:80]):
                self.assertIn("approved outcome", skill.lower())

        self.assertIn("Parent contract inheritance", router)
        self.assertIn("Scope Delta Gate", router)
        self.assertIn("No scope delta", router)
        self.assertIn("Do not split the approved outcome into product slices", router)
        self.assertIn("implementation order only", router)
        self.assertIn("Added / Changed / Deferred / Removed", brainstorm)
        self.assertIn("No scope delta", brainstorm)
        self.assertIn("lower-level specification", specification)
        self.assertIn("every inherited requirement", design)
        self.assertIn("one definition of done", plan)
        self.assertIn("passed rollback unit", execution)

    def test_outcome_lock_protocol_is_shared_and_deterministic(self) -> None:
        reference = (ROOT / "references" / "outcome-lock.md").read_text(
            encoding="utf-8"
        )
        router = (
            ROOT / "skills" / "using-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        brainstorm = (
            ROOT / "skills" / "brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        compact = (
            ROOT / "skills" / "compact-shaping" / "SKILL.md"
        ).read_text(encoding="utf-8")
        specification = (
            ROOT / "skills" / "writing-specs" / "SKILL.md"
        ).read_text(encoding="utf-8")
        plan = (
            ROOT / "skills" / "writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        execution = (
            ROOT / "skills" / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        verification = (
            ROOT / "skills" / "verifying-work" / "SKILL.md"
        ).read_text(encoding="utf-8")
        managing = (
            ROOT / "skills" / "managing-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "<!-- littlepowers:contract:v1 -->",
            "<!-- littlepowers:plan-map:v1 -->",
            "<!-- littlepowers:verification:v1 -->",
        ):
            self.assertIn(marker, reference)
        for command in (
            "bind-contract",
            "check-contract",
            "validate-plan",
            "record-verification",
        ):
            self.assertIn(command, reference)
            self.assertTrue(
                any(
                    command in skill
                    for skill in (
                        router,
                        brainstorm,
                        compact,
                        specification,
                        plan,
                        execution,
                        verification,
                        managing,
                    )
                )
            )
        self.assertIn("--direct-lock", router)
        self.assertIn("reconcile_required", router)
        self.assertIn("../../references/outcome-lock.md", brainstorm)
        self.assertIn("../../references/outcome-lock.md", compact)
        self.assertIn("../../references/outcome-lock.md", specification)
        self.assertIn("../../references/outcome-lock.md", plan)
        self.assertIn("../../references/outcome-lock.md", verification)

    def test_bootstrap_contract_projects_exactly_all_approved_outcomes(self) -> None:
        contract_path = (
            ROOT
            / "docs"
            / "littlepowers"
            / "contracts"
            / "2026-07-26-outcome-lock.md"
        )
        contract = parse_outcome_contract(contract_path.read_text(encoding="utf-8"))
        expected = {f"OUT-{index:03d}" for index in range(1, 24)}

        self.assertEqual(
            {outcome["id"] for outcome in contract["outcomes"]},
            expected,
        )
        self.assertTrue(
            all(
                outcome["disposition"] == "active"
                for outcome in contract["outcomes"]
            )
        )
        self.assertEqual(contract["scope_delta"]["status"], "none")
        self.assertEqual(contract["baseline"]["requirement"], "required")
        self.assertEqual(len(contract["sources"]), 7)
        self.assertIn(
            "docs/littlepowers/specs/"
            "2026-07-26-scope-integrity-lean-route.md",
            {source["path"] for source in contract["sources"]},
        )
        self.assertIn(
            "docs/littlepowers/designs/"
            "2026-07-26-scope-integrity-lean-route.md",
            {source["path"] for source in contract["sources"]},
        )
        self.assertEqual(
            {row["id"] for row in contract["fidelity"]},
            {"FID-001", "FID-002", "FID-003", "FID-004"},
        )
        self.assertEqual(
            {row["surface"] for row in contract["fidelity"]},
            {"Codex", "Claude Code", "Qoder", "OpenCode"},
        )

    def test_skill_workflow_uses_continuous_tasks_not_wave_slicing(self) -> None:
        for skill_path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill_path.parent.name):
                skill = skill_path.read_text(encoding="utf-8").lower()
                self.assertNotIn("wave", skill)
        plan = (
            ROOT / "skills" / "writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        execution = (
            ROOT / "skills" / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("one continuous implementation stream", plan)
        self.assertIn("bounded rollback", plan)
        self.assertIn("continuous implementation", execution)

    def test_visual_baseline_and_dual_acceptance_verdicts_are_bound(self) -> None:
        router = (
            ROOT / "skills" / "using-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT / "skills" / "reviewing-changes" / "SKILL.md"
        ).read_text(encoding="utf-8")
        verify = (
            ROOT / "skills" / "verifying-work" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Baseline provenance", router)
        self.assertIn("implementation-generated", router)
        self.assertIn("work-unit compliance", review)
        self.assertIn("approved-outcome fidelity", review)
        self.assertIn("highest-authority", review)
        self.assertIn("implementation-generated", review)
        self.assertIn("approved baseline", verify)
        self.assertIn("implementation-generated", verify)

    def test_router_binds_recovery_to_the_exact_project_root(self) -> None:
        router = (
            ROOT / "skills" / "using-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("--root <project-root> context", router)
        self.assertIn("ancestor ledger", router)
        self.assertIn("leave it untouched", router)

    def test_plan_checklist_mirrors_the_host_plan_surface(self) -> None:
        writing = (ROOT / "skills" / "writing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        executing = (ROOT / "skills" / "executing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("update_plan", writing)
        self.assertIn("durable source of truth", writing)
        self.assertIn("update_plan", executing)
        self.assertIn("re-issue", executing)

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
        for snippet in (agents, claude):
            self.assertIn("docs/littlepowers/...", snippet)
            self.assertIn("latest user request", snippet)
            self.assertIn("new workflow artifacts", snippet)
            self.assertIn("legacy directories or backlinks", snippet)
            self.assertIn("brainstorm → plan", snippet)
            self.assertIn("Do not create product or technical slices", snippet)
            self.assertIn("No scope delta", snippet)
            self.assertIn("approved-outcome fidelity", snippet)
            self.assertIn("one continuous implementation stream", snippet)
            self.assertNotIn("wave", snippet.lower())

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

    def test_artifact_roots_require_an_explicit_current_declaration(self) -> None:
        defaults = {
            "brainstorming": "docs/littlepowers/brainstorms/",
            "compact-shaping": "docs/littlepowers/shapes/",
            "writing-specs": "docs/littlepowers/specs/",
            "designing-solutions": "docs/littlepowers/designs/",
            "writing-plans": "docs/littlepowers/plans/",
        }

        for name, default_root in defaults.items():
            with self.subTest(skill=name):
                skill = (ROOT / "skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                ).lower()
                self.assertIn(
                    "existing workflow, keep the artifact root already resolved",
                    skill,
                )
                self.assertIn(
                    "latest user request or a current repository instruction "
                    "explicitly names it for new workflow artifacts",
                    skill,
                )
                self.assertIn(
                    "existing directories, backlinks, and historical or "
                    "tool-branded paths",
                    skill,
                )
                self.assertIn(default_root, skill)

        router = (ROOT / "skills" / "using-littlepowers" / "SKILL.md").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("resolve artifact placement", router)
        self.assertIn(
            "latest user request or a current repository instruction "
            "explicitly names it for new workflow artifacts",
            router,
        )
        self.assertIn("recorded artifact paths", router)

    def test_runtime_continuity_contracts_cover_observed_failures(self) -> None:
        router = (ROOT / "skills" / "using-littlepowers" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        brainstorm = (
            ROOT / "skills" / "brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        executing = (
            ROOT / "skills" / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        managing = (
            ROOT / "skills" / "managing-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("codex plugin list --json", router)
        self.assertIn("claude plugin list --json", router)
        self.assertIn("Do not continue from remembered instructions", router)
        self.assertIn("new task boundary", router)
        self.assertIn("An ADR may be created or updated as a companion", brainstorm)
        self.assertIn("an ADR is not a substitute", brainstorm)
        self.assertIn("--progress", executing)
        self.assertIn("Do not invent a percentage", executing)
        self.assertIn("before a likely context compaction", executing)
        self.assertIn("without inventing a percentage", managing)
        phase_progress = {
            "brainstorming": "spec is next",
            "writing-specs": "design is next",
            "designing-solutions": "plan is next",
            "writing-plans": "execution is next",
            "compact-shaping": "execution is next",
        }
        for skill_name, expected_progress in phase_progress.items():
            with self.subTest(progress_skill=skill_name):
                phase_skill = (ROOT / "skills" / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("--progress", phase_skill)
                self.assertIn(expected_progress, phase_skill)

    def test_handoff_and_review_evidence_stay_explicit_and_lightweight(self) -> None:
        router = (ROOT / "skills" / "using-littlepowers" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        managing = (
            ROOT / "skills" / "managing-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        executing = (
            ROOT / "skills" / "executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        reviewing = (
            ROOT / "skills" / "reviewing-changes" / "SKILL.md"
        ).read_text(encoding="utf-8")
        hook = (ROOT / "hooks" / "session-start.py").read_text(encoding="utf-8")

        self.assertIn("new task or session rooted at the target", router)
        self.assertIn("Never scan sibling worktrees", router)
        self.assertIn("cannot change the current task root", router)
        self.assertIn("handoff --workflow", managing)
        self.assertIn("cancels only the source workflow", managing)
        self.assertIn("actual workspace transfer", executing)
        self.assertIn("does not hand off ordinary phase changes", executing)
        self.assertIn("snapshot", reviewing)
        self.assertIn("A changed token invalidates the review verdict", reviewing)
        self.assertIn("trust, state ownership, or rollback boundary", reviewing)
        self.assertIn("one acceptance owner", reviewing)
        self.assertIn("does not create reviewers or select models", reviewing)
        self.assertNotIn("create_review_snapshot", hook)
        self.assertNotIn("snapshot", hook)

    def test_project_workflow_index_is_explicit_read_only_and_hook_free(self) -> None:
        state_cli = (ROOT / "scripts" / "littlepowers_state.py").read_text(
            encoding="utf-8"
        )
        router = (ROOT / "skills" / "using-littlepowers" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        managing = (
            ROOT / "skills" / "managing-littlepowers" / "SKILL.md"
        ).read_text(encoding="utf-8")
        hook = (ROOT / "hooks" / "session-start.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        capability = (ROOT / "docs" / "capability-matrix.md").read_text(
            encoding="utf-8"
        )
        security = (ROOT / "docs" / "security-model.md").read_text(
            encoding="utf-8"
        )
        scenarios = (ROOT / "evals" / "scenarios.md").read_text(
            encoding="utf-8"
        )

        for command in ("project-register", "project-unregister", "project-status"):
            with self.subTest(command=command):
                self.assertIn(command, state_cli)
                self.assertIn(command, managing)
                self.assertIn(command, readme)
                self.assertIn(command, readme_zh)
        self.assertIn("MAX_PROJECT_MEMBERS = 16", state_cli)
        self.assertIn("Project Workflow Index", router)
        self.assertIn("Never scan siblings", router)
        self.assertIn("Parallel independent iterations", capability)
        self.assertIn("performs no index or member write", security)
        self.assertIn("Explicit parallel-worktree overview", scenarios)
        self.assertNotIn("worktree\", \"list", state_cli)
        self.assertNotIn("project-index", hook)
        self.assertNotIn("project-status", hook)

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
            "evals/results/2026-07-17-v0.4-alpha.1.md",
            "evals/results/2026-08-01-v1.3.0-release.md",
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
        self.assertIn("v1.3.0", readme)
        self.assertIn("Outcome Lock protocol 1.3", readme)
        self.assertIn("Review Lease", readme)
        self.assertIn("one continuous stream", readme)
        self.assertIn("Systematic debugging", readme)
        self.assertIn("Proportional verification", readme)
        self.assertIn("Lightweight review", readme)
        self.assertNotIn("Follow-up messages do not silently replace", readme)

    def test_release_docs_cover_engineering_disciplines(self) -> None:
        capability = (ROOT / "docs" / "capability-matrix.md").read_text(
            encoding="utf-8"
        )
        compatibility = (ROOT / "docs" / "model-compatibility.md").read_text(
            encoding="utf-8"
        )
        evals = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        evaluation = (
            ROOT / "evals" / "results" / "2026-07-17-v0.4-alpha.1.md"
        ).read_text(encoding="utf-8")
        stable_evaluation = (
            ROOT / "evals" / "results" / "2026-08-01-v1.3.0-release.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Release:** 1.3.0", capability)
        self.assertIn("Outcome Coverage Gate", capability)
        self.assertIn("`debugging-systematically`", capability)
        self.assertIn("`verifying-work`", capability)
        self.assertIn("`reviewing-changes`", capability)
        self.assertIn("observable summaries", compatibility)
        self.assertIn("Tiny isolated changes", compatibility)
        self.assertIn("original reproducer", evals)
        self.assertIn(
            "separate work-unit compliance, approved-outcome fidelity, "
            "and code-quality verdicts",
            evals,
        )
        self.assertIn("legacy tool-branded artifact root", evals)
        self.assertIn("## [0.4.0-alpha.1]", changelog)
        self.assertIn("49 Python tests passed", evaluation)
        self.assertIn("17 directly affected", evaluation)
        self.assertIn("Acceptance/spec compliance:** `pass`", evaluation)
        self.assertIn("Code quality:** `approve`", evaluation)
        self.assertIn("Candidate: `1.3.0`", stable_evaluation)
        self.assertIn("198/198 passed", stable_evaluation)
        self.assertIn("same-byte path substitution", stable_evaluation)


if __name__ == "__main__":
    unittest.main()
