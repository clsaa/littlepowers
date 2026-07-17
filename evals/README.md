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
- Completion includes fresh, relevant verification evidence.

Use [scenarios.md](scenarios.md) for the prompts and expected observations.
