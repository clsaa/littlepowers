# Littlepowers runtime continuity iteration

Date: 2026-07-17

## Outcome and non-goals

Make an interrupted Codex or Claude Code workflow recover accurately when a plugin cache path changes, keep full-route brainstorm evidence distinct from ADRs, and expose observable execution progress in the local ledger. Preserve proportional planning and focused verification; do not turn every edit into a full-suite gate or make Littlepowers a second orchestrator.

## Constraints and assumptions

- Keep Python 3 as the only runtime dependency and preserve schema compatibility through deterministic migration.
- Treat host plugin installation and cache retention as host-owned behavior. Littlepowers may detect and recover from a replaced cache, but it cannot promise that Codex retains old cache directories.
- Keep approved plans stable. Store live progress in the recovery ledger instead of rewriting design checklists after every checkpoint.
- Preserve legacy artifact references, including existing ADR-backed brainstorm records, while preventing new full-route workflows from using an ADR as the brainstorm artifact.
- Keep Codex and Claude Code behavior equivalent; host-specific discovery instructions may differ.

## Requirements and acceptance checks

1. `using-littlepowers` must stop memory-only continuation when its loaded plugin path disappears, resolve the active Littlepowers source through the host, reread the current router/phase skill, and reload ledger context.
2. Plugin update guidance must warn that an active task cannot hot-load a replacement safely and must use a new task boundary; an updater must not claim seamless in-place replacement.
3. `brainstorming` must allow an ADR as a companion decision record but require the checkpointed brainstorm artifact to contain the shaping evidence and live under the resolved brainstorm area.
4. Ledger schema 2 must accept an optional concise `progress` field without a version bump, migrate schema 1 deterministically, render progress in status/context, reject malformed or oversized values, and remain readable by the previous schema 2 implementation.
5. Execution checkpoints must record an observable milestone or acceptance-check count, avoid invented percentages, and add a continuity checkpoint before compaction, handoff, plugin replacement, or a long batch crosses multiple subsystems.
6. Unit tests, eval scenarios, all skill validators, Codex plugin validation, Claude strict validation, and diff hygiene must pass.

## Selected approach

- Extend the existing state CLI rather than introducing a second progress file. This keeps optimistic concurrency, trust checks, and cross-host recovery in one store.
- Add recovery instructions to the router and execution/management skills instead of guessing host cache internals in the state CLI.
- Enforce brainstorm semantics in phase instructions and regression evals while accepting legacy ledger paths. Hard path enforcement would reject legitimate explicitly configured roots and break active workflows.

## Affected components

- `scripts/littlepowers_state.py`, state and hook tests
- `skills/using-littlepowers`, `brainstorming`, `executing-plans`, `managing-littlepowers`
- eval scenarios and user-facing README/CHANGELOG
- matching Littlepowers brainstorm/spec/design/plan records

## Execution and validation

1. Add schema-2-compatible progress parsing, rendering, old-reader compatibility, and tests.
2. Tighten the four affected skills and add regression scenarios for cache replacement, ADR misuse, status interruption, and progress recovery.
3. Update concise documentation and matching design records.
4. Run focused tests, the aggregate test suite, validators, and independent forward tests.
5. Stage the personal plugin source. Reinstall only when no active task depends on the current cache; otherwise leave the verified update staged and report the safe boundary.

Validation commands:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
git diff --check
claude plugin validate --strict .
```
