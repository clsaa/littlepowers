# Multi-host support, Codex plan display, and phase review gates plan

Date: 2026-07-20

Status: implemented in the working tree; live completion state belongs in the ledger

## Goal and inputs

Implement the approved [specification](../specs/2026-07-20-multi-host-review-gates.md) and [design](../designs/2026-07-20-multi-host-review-gates.md): first-class Qoder/QoderCLI and OpenCode support, Codex native plan-surface mirroring, and full-route phase review gates, without forking shared content.

## Global constraints

- One shared implementation; Python 3 only at runtime; zero JavaScript dependencies.
- Hooks stay read-only and fail open; no telemetry, no transcript access, no user-config edits.
- Keep `${CLAUDE_PLUGIN_ROOT}` present in the hooks command for existing installs and tests.
- The root coordinator is the only ledger writer.

## Task 1: Qoder support

**Outcome:** Qoder CLI installs and loads Littlepowers with working hooks.

**Files:** `.qoder-plugin/plugin.json`, `hooks/hooks.json`, `hooks/session-start.py`, `skills/using-littlepowers/SKILL.md`, `tests/test_manifests.py`.

**Steps:**

- [x] Add `.qoder-plugin/plugin.json` sharing name, version, and repository with the other manifests.
- [x] Switch the hooks command to `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` in all three registrations.
- [x] Accept `QODER_PLUGIN_ROOT` in `resolve_plugin_root()`.
- [x] Document Qoder and OpenCode state-CLI and plugin-replacement resolution in the router.
- [ ] Assert Qoder manifest parity and hook command portability in `test_manifests.py`.

**Focused validation:** `python3 -m unittest tests.test_manifests -v`; expect parity and hook assertions green.

## Task 2: OpenCode support

**Outcome:** OpenCode installs from a git URL, discovers the skills, and injects the read-only ledger context.

**Files:** `.opencode/plugins/littlepowers.js`, `package.json`, `tests/test_manifests.py`.

**Steps:**

- [x] Add the plugin with `config` skills registration and `experimental.chat.messages.transform` injection backed by `hooks/session-start.py`, deduplicated per message and failing open.
- [x] Add root `package.json` with `main` pointing at the plugin and no dependencies.
- [ ] Assert plugin shape and `package.json` wiring in `test_manifests.py`; run `node --check`.

**Focused validation:** `node --check .opencode/plugins/littlepowers.js`; manifest tests green.

## Task 3: Codex plan display

**Outcome:** Plans appear in the Codex plan view and track execution.

**Files:** `skills/writing-plans/SKILL.md`, `skills/executing-plans/SKILL.md`, `assets/agents-snippet.md`.

**Steps:**

- [x] Mirror the checklist through `update_plan` after the plan artifact (OpenCode: todo tool).
- [x] Refresh the mirror at each checkpoint; re-issue from the ledger after resume/clear/compaction.
- [x] Note the mirror rule in the AGENTS.md snippet.

**Focused validation:** manual acceptance in Codex: a written plan appears in the host plan view and advances with checkpoints. Recorded as pending; docs mark it unverified until a live run.

## Task 4: Phase review gates

**Outcome:** Full-route phases pause for approval by default.

**Files:** `skills/using-littlepowers/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/writing-specs/SKILL.md`, `skills/designing-solutions/SKILL.md`, `skills/writing-plans/SKILL.md`, `skills/compact-shaping/SKILL.md`, both snippets, `tests/test_manifests.py`.

**Steps:**

- [x] Add the router "Review phase boundaries" policy with the explicit unattended-execution escape hatch.
- [x] Replace automatic next-phase chaining with present-and-stop wording in all phase skills.
- [x] Document the gate in both durable guidance snippets.
- [ ] Assert gate wording across skills in `test_manifests.py`.

**Focused validation:** `python3 -m unittest discover -s tests -v` green; manual acceptance: a full-route run stops after the brainstorm until approved.

## Task 5: Documentation and integration verification

**Outcome:** Public docs match behavior on all four hosts.

**Files:** `README.md`, `README.zh-CN.md`, `CHANGELOG.md`, `docs/capability-matrix.md`, this artifact set.

**Steps:**

- [x] Install/update/uninstall sections for Qoder and OpenCode in both READMEs.
- [x] Review-gate and `update_plan` behavior documented; untested-host status recorded.
- [x] Capability matrix gains Qoder and OpenCode controls; OpenCode leaves the unsupported list.
- [x] CHANGELOG Unreleased entries added.
- [ ] Final integration verification: full unittest suite, compileall, and diff review for regressions or unintended files.

**Broad validation:** `python3 -m unittest discover -s tests -v && python3 -m compileall -q scripts hooks tests` — justified as the release-facing boundary across all hosts.
