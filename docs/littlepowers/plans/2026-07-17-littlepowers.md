# Littlepowers Implementation Plan

**Goal:** Ship a small Codex-first workflow plugin that enforces deliberate shaping for non-trivial work and restores unfinished state after session boundaries.

**Architecture:** Six concise skills use one standard-library state CLI. A read-only SessionStart hook injects active state; Codex native skill discovery handles initial routing.

**Constraints:** No runtime dependencies, telemetry, transcript parsing, automatic commits, or non-Codex harness support.

## Task 1 — Package and repository metadata

**Files:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `README.md`, `LICENSE`, `.gitignore`, `AGENTS.md`, `assets/agents-snippet.md`

- [x] Replace scaffold placeholders with valid Littlepowers metadata.
- [x] Add a repository-root marketplace entry and installation instructions.
- [x] Document product settings, workflow boundaries, hook trust, and attribution.
- [x] Validate JSON and plugin structure.

## Task 2 — Workflow state CLI

**Files:** `scripts/littlepowers_state.py`, `tests/test_state.py`

- [x] Implement root discovery, state loading, validation, atomic writes, and self-ignore setup.
- [x] Implement `start`, `checkpoint`, `pause`, `complete`, `cancel`, `show`, and `context` commands.
- [x] Add lifecycle, replacement, artifact, and malformed-state tests.
- [x] Run `python3 -m unittest discover -s tests -v` and expect all tests to pass.

## Task 3 — Recovery hook

**Files:** `hooks/hooks.json`, `hooks/session-start.py`, `tests/test_hook.py`

- [x] Register SessionStart for startup, resume, clear, and compact.
- [x] Emit no stdout without active state.
- [x] Emit valid Codex `additionalContext` JSON with active state.
- [x] Cover silence, recovery, and malformed input in tests.

## Task 4 — Skills

**Files:** `skills/*/SKILL.md`, `skills/*/agents/openai.yaml`

- [x] Initialize every skill with the official skill scaffold.
- [x] Implement routing, brainstorming, spec, design, planning, and execution workflows.
- [x] Keep instructions concise and point every phase to the shared state protocol.
- [x] Run `quick_validate.py` for every skill.

## Task 5 — Automation and integration checks

**Files:** `.github/workflows/test.yml`, `tests/test_manifests.py`

- [x] Add CI for unit tests, JSON and skill-shape checks, and Python compilation; keep official skill and plugin validation as a local release check.
- [x] Run all tests locally.
- [x] Exercise hook scripts directly.
- [x] Add the repository as a temporary local Codex marketplace and install Littlepowers.
- [x] Use `codex debug prompt-input` to confirm skill discovery and a read-only, ephemeral `codex exec` probe to confirm SessionStart recovery context; remove temporary configuration afterward if it was not already present.

## Task 6 — GitHub delivery

- [x] Initialize `main`, review the diff, and commit the verified implementation.
- [x] Create `clsaa/littlepowers` as a private GitHub repository.
- [x] Push `main` and verify repository visibility and URL.
