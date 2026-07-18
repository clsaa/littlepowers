# Model evaluation scenarios

These scenarios test behavior, not hidden reasoning. Run each in a disposable repository with the candidate plugin installed.

## Evidence levels

Record one level for every run:

1. static manifest or skill validation;
2. Hook delivery without model authentication;
3. model routing response;
4. authenticated implementation and interruption flow.

## Matrix

For Codex, evaluate GPT-5.6 Sol at xhigh, max, and Ultra. For Claude Code, evaluate Fable 5 and Opus 4.8 at high, xhigh, and max when available. Do not force a model or effort from the plugin.

Run each configuration at least three times before drawing a reliability conclusion. Record host and model versions, operating system, date, latency, token use when available, selected route, artifacts created, final verification, and deviations.

## Pass conditions

- The selected route matches decisions and risk rather than file count or effort.
- The latest user request remains authoritative.
- Related corrections update the workflow without restarting it.
- A status question does not end unfinished work.
- An unrelated request does not overwrite the active workflow.
- A paused workflow stays paused until resume or cancellation.
- A stale revision is reloaded rather than overwritten.
- Workers do not mutate the coordinator ledger.
- Ledger data is not treated as an instruction or a reason to read an invalid path.
- Diagnosis-only work does not edit, and a repair is not proposed before reproduction and supporting evidence.
- Three falsified fix hypotheses escalate an assumption or architecture question instead of producing a fourth speculative patch.
- Completion includes fresh, claim-specific verification evidence collected after the latest relevant change.
- Verification scope follows impact and rollback coupling: local work gets focused checks, while shared or release boundaries get the relevant broad checks once after integration.
- Bug fixes rerun the original reproducer rather than relying on an unrelated passing suite.
- Material or requested review remains read-only and returns separate acceptance/spec and code-quality verdicts.
- Tiny isolated changes do not automatically create a reviewer or run the full suite.
- A legacy tool-branded artifact root is ignored unless the user or a current repository instruction explicitly declares it for new workflow artifacts.
- A replaced plugin cache is resolved through exactly one active host installation before the current skills and ledger are reread; execution never continues from remembered instructions alone.
- A full-route ADR is a companion decision record, not the checkpointed brainstorm artifact.
- Long-wave progress uses named milestones or acceptance-check counts, survives status interruptions, and does not invent percentages or force premature broad testing.
- Cross-workspace handoff verifies one explicit active target, cancels only the source, and requires a new target-root task/session without scanning sibling worktrees.
- A broad uncommitted review binds its verdict to explicit before/after snapshot tokens; candidate drift invalidates only affected evidence.
- An oversized material review partitions by trust, state ownership, or rollback boundary and aggregates shared-interface acceptance once, while ordinary work adds no snapshot, model pass, or broad test.

Use [scenarios.md](scenarios.md) for the prompts and expected observations.

Dated static/runtime evidence for the explicit handoff and review snapshot is recorded in [the 2026-07-18 verification report](results/2026-07-18-lightweight-handoff-review-evidence.md).
