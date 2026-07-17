# Littlepowers Dual-Harness Implementation Plan

**Goal:** Ship one lightweight brainstorm → spec → design → plan → execute workflow with durable interruption recovery in both Codex and Claude Code.

**Architecture:** Keep skills, state, and recovery behavior shared. Add native Codex and Claude Code manifests/marketplaces as thin packaging layers around that core.

**Constraints:** No runtime dependencies beyond Python 3, telemetry, transcript parsing, automatic commits, forced subagents, or global settings changes.

## Task 1 — Record the dual-harness product decision

**Files:** `docs/littlepowers/brainstorms/2026-07-17-littlepowers.md`, `docs/littlepowers/specs/2026-07-17-littlepowers.md`, `docs/littlepowers/designs/2026-07-17-littlepowers.md`, this plan

- [x] Compare separate implementations, a shared core, and a Superpowers dependency.
- [x] Define native packaging, shared recovery behavior, and acceptance criteria.
- [x] Record the naming trade-off without renaming absent an explicit decision.

## Task 2 — Add Claude Code packaging and align releases

**Files:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`

- [x] Add native Claude Code manifest and marketplace entry.
- [x] Bump all release metadata to `0.2.0` and keep versions consistent.
- [x] Describe both harnesses in shared metadata; update GitHub repository details after push.

## Task 3 — Make recovery truly cross-harness

**Files:** `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start.py`, `tests/test_hook.py`

- [x] Use a command path accepted by both plugin systems.
- [x] Add a cross-platform Python launcher.
- [x] Resolve both `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT`.
- [x] Prove identical recovery output under both environment conventions.

## Task 4 — Make guidance platform-aware

**Files:** `skills/using-littlepowers/SKILL.md`, `AGENTS.md`, `assets/agents-snippet.md`, `assets/claude-snippet.md`, `README.md`

- [x] Keep the core interruption protocol platform-neutral.
- [x] Isolate Codex-only Queue and slash-command advice.
- [x] Add Claude Code installation, invocation, persistent-guidance, and uninstall instructions.
- [x] Remove stale claims that Claude Code is unsupported.

## Task 5 — Expand automated validation

**Files:** `tests/test_manifests.py`, `.github/workflows/test.yml`

- [x] Check both native manifests, both marketplaces, shared versions, and the Hook command.
- [x] Run unit tests, Python compilation, and strict Claude plugin validation.
- [x] Run all six bundled skill validators and the Codex plugin validator locally.

## Task 6 — Exercise both real installations

- [ ] Install and inspect Littlepowers through a temporary Codex marketplace configuration.
- [x] Install and inspect `littlepowers@littlepowers` through a temporary Claude marketplace configuration.
- [ ] Prove active recovery context reaches a read-only CLI session in each harness.
- [ ] Remove temporary installation/configuration created only for verification.

## Task 7 — Publish and verify

- [x] Review the complete diff and security boundary.
- [ ] Commit and push `main` to `clsaa/littlepowers`.
- [ ] Update the GitHub repository description for both harnesses.
- [ ] Confirm GitHub Actions succeeds on the published commit.
- [ ] Mark the recovery state complete only after all acceptance criteria pass.
