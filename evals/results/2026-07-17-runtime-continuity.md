# Runtime continuity evaluation report

**Date:** 2026-07-17

**Candidate:** Unreleased Littlepowers working tree after Termarium usage review

**Platform:** macOS arm64, Europe/London

This report records the evidence for scenarios 22–24. It is a functional prerelease check, not a repeated-run reliability claim or a release record.

## Verification scope

The change affects state compatibility, hooks, host plugin recovery, and both plugin packages, so its aggregate rollback boundary is broad. Focused state, Hook, manifest, and forward checks ran before the aggregate suite and host validators.

## Scenario 22: plugin cache replaced during active execution

**Evidence level:** host discovery plus model routing response; live deletion of the cache used by the active Termarium task was deliberately not performed.

- Codex's installed-plugin JSON resolved exactly one enabled Littlepowers source at `/Users/nathan/plugins/littlepowers`.
- The verified working tree was staged to that source and compared checksum-for-checksum, so recovery through `source.path` rereads the current router, phase skills, and state CLI rather than obsolete files.
- The forward response stopped before edits, selected exactly one enabled `name=littlepowers` entry, verified the manifest, reread the current skills and ledger, and required a new task/session for missing or ambiguous discovery.
- Claude Code's actual installed-plugin JSON contained no Littlepowers entry. Under the same contract this is the missing-discovery branch: stop and use a new session after installation, never guess a cache path.

The live Codex cachebuster reinstall remains deferred until the active Termarium task reaches a safe task boundary. Therefore this is a contract pass with an explicit environment limitation, not an authenticated destructive replacement flow.

## Scenario 23: ADR companion is not the brainstorm artifact

**Evidence level:** model routing response plus static skill contract.

The forward response selected the full route, placed the shaping evidence in `docs/littlepowers/brainstorms/...`, pointed the ledger's `brainstorm` artifact there, treated the ADR only as a companion record, and continued to spec, design, and plan before any authorized implementation. It did not use the ADR as the brainstorm artifact.

## Scenario 24: long-wave progress and status interruption

**Evidence level:** model routing response plus state/Hook integration tests.

The forward response reported the recorded `3/5` milestone verbatim, did not invent a percentage, answered the status question, and returned to check 4 with focused verification. State and Hook tests confirm progress persistence and recovery rendering. A full-route regression advances progress through brainstorm, spec, design, and plan so execution cannot retain the stale phrase `spec is next`.

## Fresh aggregate evidence

The final command results are recorded in the active recovery ledger and handoff report. Required gates are:

- full Python unit suite and compilation;
- all 11 skill validators;
- Codex plugin validation;
- Claude strict plugin validation;
- previous schema 2 reader against a progress-bearing ledger;
- integrated diff and checksum inspection.

## Residual limits

- No live cache directory used by an active task was removed.
- Claude Code has no user-level Littlepowers installation on this machine, so only its missing-install branch and strict package validation were exercised.
- No three-run reliability claim is made for any model or effort level.
