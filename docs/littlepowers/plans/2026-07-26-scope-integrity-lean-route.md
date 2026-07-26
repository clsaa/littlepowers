# Scope integrity and lean-route implementation plan

Date: 2026-07-26

Status: implemented and source-verified; live installation truth belongs in the ledger

## Goal

Ship one cross-host Littlepowers update that prevents silent scope shrinkage, prohibits agent-created product slices, adds a small-change brainstorm → plan route, and exposes the exact recovery root without increasing steady-state orchestration.

## Global constraints

- One approved outcome and one definition of done; tasks below are implementation order only.
- Shared behavior across Codex, Claude Code, Qoder, and OpenCode.
- Schema 2 and existing workflows remain compatible.
- No extra model call, reviewer, background scan, telemetry, or automatic broad test.
- Root coordinator is the only ledger writer.

## Task 1: Executable protocol contracts

**Outcome:** regression tests fail on the old behavior and pass only with the new route and guards.

**Files:** `tests/test_manifests.py`, `tests/test_hook.py`, `evals/scenarios.md`.

**Checks:** focused unittest selection for lean routing, scope integrity, baseline/verdict behavior, root binding, and Hook context.

## Task 2: Shared skill behavior

**Outcome:** all planning depths preserve parent scope; bounded small changes skip spec/design.

**Files:** router plus brainstorming, shaping, spec, design, plan, execution, review, and verification skills.

**Checks:** focused manifest/discipline tests and all eleven official skill validators.

## Task 3: Root evidence

**Outcome:** every supported Hook snapshot names the canonical workspace root without changing schema or root discovery.

**Files:** `scripts/littlepowers_state.py`, `hooks/session-start.py`, Hook/state tests.

**Checks:** Hook and state unittests plus compileall.

## Task 4: Cross-host release surfaces

**Outcome:** manifests, bilingual docs, snippets, compatibility guidance, and version identity agree.

**Files:** Codex/Claude/Qoder manifests, OpenCode package metadata, README files, capability/model/security docs, changelog.

**Checks:** manifest tests, Codex plugin validator, `claude plugin validate --strict .`, and source diff inspection.

## Task 5: Integrated verification and local pickup

**Outcome:** the connected release boundary is verified once, then safely staged/reinstalled for local Codex and Claude Code where host CLIs are healthy.

**Checks:** `python3 -m unittest discover -s tests -v`, compileall, all skill validators, plugin validators, and installed-source inspection. Report unavailable host validation rather than converting it to success.
