# Littlepowers Implementation Plan

**Goal:** Ship a small Codex-first workflow plugin that enforces deliberate shaping for non-trivial work and restores unfinished state after session boundaries.

**Architecture:** Six concise skills use one standard-library state CLI. A read-only SessionStart hook injects active state; Codex native skill discovery handles initial routing.

**Constraints:** No runtime dependencies, telemetry, transcript parsing, automatic commits, or non-Codex harness support.

## Task 1 — Package and repository metadata

**Files:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `README.md`, `LICENSE`, `.gitignore`, `AGENTS.md`, `assets/agents-snippet.md`

- [ ] Replace scaffold placeholders with valid Littlepowers metadata.
- [ ] Add a repository-root marketplace entry and installation instructions.
- [ ] Document product settings, workflow boundaries, hook trust, and attribution.
- [ ] Validate JSON and plugin structure.

## Task 2 — Workflow state CLI

**Files:** `scripts/littlepowers_state.py`, `tests/test_state.py`

- [ ] Implement root discovery, state loading, validation, atomic writes, and self-ignore setup.
- [ ] Implement `start`, `checkpoint`, `pause`, `complete`, `cancel`, `show`, and `context` commands.
- [ ] Add lifecycle, replacement, artifact, and malformed-state tests.
- [ ] Run `python3 -m unittest discover -s tests -v` and expect all tests to pass.

## Task 3 — Recovery hook

**Files:** `hooks/hooks.json`, `hooks/session-start.py`, `tests/test_hook.py`

- [ ] Register SessionStart for startup, resume, clear, and compact.
- [ ] Emit no stdout without active state.
- [ ] Emit valid Codex `additionalContext` JSON with active state.
- [ ] Cover silence, recovery, and malformed input in tests.

## Task 4 — Skills

**Files:** `skills/*/SKILL.md`, `skills/*/agents/openai.yaml`

- [ ] Initialize every skill with the official skill scaffold.
- [ ] Implement routing, brainstorming, spec, design, planning, and execution workflows.
- [ ] Keep instructions concise and point every phase to the shared state protocol.
- [ ] Run `quick_validate.py` for every skill.

## Task 5 — Automation and integration checks

**Files:** `.github/workflows/test.yml`, `tests/test_manifests.py`

- [ ] Add CI for unit tests, JSON checks, skill validation, and plugin validation.
- [ ] Run all tests locally.
- [ ] Exercise hook scripts directly.
- [ ] Add the repository as a temporary local Codex marketplace, install Littlepowers, and inspect model-visible prompt input; remove temporary configuration after the check if it was not already present.

## Task 6 — GitHub delivery

- [ ] Initialize `main`, review the diff, and commit the verified implementation.
- [ ] Create `clsaa/littlepowers` as a private GitHub repository.
- [ ] Push `main` and verify repository visibility and URL.

