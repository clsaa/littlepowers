# Lightweight handoff and review-evidence verification

**Date:** 2026-07-18

**Environment:** macOS 26.5.1, Python 3.9.6, Git 2.50.1, Claude Code 2.1.207

**Scope:** Static/runtime verification of the Unreleased handoff, review snapshot, and lightweight routing policy. This is not a live-model reliability claim.

## Results

- `python3 -m unittest discover -s tests -v`: 64 tests passed.
- `python3 -m compileall -q scripts hooks tests`: passed.
- All 11 skills and the Codex plugin passed their bundled validators.
- `claude plugin validate --strict .`: passed.
- `git diff --check`: passed.
- A handoff-bearing cancelled source was readable by the previously installed schema-2 CLI; the old reader preserved the unknown optional field and did not resume the source.
- A current Termarium candidate with 178 changed paths and 3,374,356 hashed bytes produced an explicit snapshot in 0.21 seconds. Snapshotting was invoked manually and is absent from Hook code.
- Twenty no-ledger prompt-hook runs took 0.82 seconds total; twenty active-ledger prompt-hook runs took 1.01 seconds total on this machine. This measures Python/ledger hook cost only, not host scheduling or model latency.
- The plugin contains no model, reasoning-effort, reviewer, or subagent selection. Ordinary routing does not invoke handoff, snapshot, an extra model pass, or an extra broad test.

## Boundaries

- Snapshot timing is one local measurement, not a cross-platform benchmark.
- The snapshot token detects candidate drift when explicitly compared; it does not lock files.
- Handoff records a verified pointer and cancels only the source. The target must be revalidated in a new target-root task or session.
- GPT-5.6 Sol xhigh/max and Codex Ultra remain host-selected. Fable 5 and Opus 4.8 remain Claude Code-selected. This verification proves non-selection by Littlepowers, not equal latency or model quality.
