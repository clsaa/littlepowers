# Security model

**Reviewed:** 2026-07-17

**Release:** 0.4.0-alpha.1

## Assets and trust boundary

Littlepowers protects the user's repository, files outside the workspace, workflow integrity, and prompt context. The repository being worked on may be untrusted. Ledger values, artifact paths, and artifact content are data, not instructions.

The plugin trusts the installed Littlepowers package and the local Python runtime. It does not treat a repository-provided `.littlepowers` path as trusted merely because it is inside the workspace.

## Data stored

`.littlepowers/state.json` contains:

- workflow ID and revision;
- status, phase, objective, current task, and next action;
- relative artifact paths;
- bounded completed-checkpoint descriptions;
- creation and update timestamps.

It does not contain transcripts, raw prompts, credentials, file contents, or model reasoning. `.littlepowers/.gitignore` ignores the directory contents.

## Executable surfaces

`hooks/run-hook.cmd` launches `hooks/session-start.py` for three read-only events:

- `SessionStart`;
- `UserPromptSubmit`;
- `SubagentStart`.

The hook reads event metadata and the ledger. It does not inspect transcript paths or prompt text, write state, call the network, run Git mutations, or start agents. It emits nothing when no unfinished workflow exists. Invalid state produces a fixed stderr diagnostic and exit code 0 so the coding session can continue.

The state CLI is the only writer. Skills invoke it during tracked work. Its `read-artifact` command is the only supported way for a skill to load a ledger-referenced artifact.

The v0.4 debugging, verification, and review skills add instructions only. They add no Hook, script, state field, network client, or execution privilege. `reviewing-changes` explicitly remains read-only; implementation and ledger mutation stay with the authorized coordinator.

## Store validation

The shared read/write boundary:

1. resolves the workspace root;
2. rejects `.littlepowers`, state, lock, ignore, and archive surfaces when their type or link metadata is unsafe;
3. on POSIX, requires current-user ownership and rejects group- or world-writable state surfaces;
4. rejects hard-linked state and lock files;
5. requires a regular state file no larger than 64 KiB;
6. rejects a Git-tracked state file;
7. requires the ledger to be ignored in a Git worktree;
8. accepts only normalized, non-hidden, workspace-relative Markdown artifact paths;
9. rejects control characters, timestamps beyond a five-minute future-skew allowance, and bounded-field violations.

Hook context is bounded to 10,000 characters and only includes the ten most recent completed entries. It labels records older than 30 days as stale by age and marks paused records as requiring explicit resume.

`read-artifact` requires the expected workflow ID and revision, returns the same snapshot identifiers, and walks workspace directories without following links where the operating system supports descriptor-relative access. It rejects stale snapshots, links, hard links, special files, unexpected ownership or write permissions, non-UTF-8 content, and files over 128 KiB. Output labels artifact content as untrusted project data and tells the agent to reconcile it with the latest request and repository evidence.

## Write integrity

Each workflow has a UUID and monotonic revision. Every mutation after `start` supplies the expected UUID and revision. A mismatch exits with code 3 and does not write.

The writer holds a cross-process advisory lock over the read-check-write transaction. On POSIX, it opens the resolved workspace one non-link path component at a time. It then pins `.littlepowers` relative to that workspace descriptor and performs store operations through the descriptor.

Identity checks against the pinned store bracket every path-based Git check. A concurrent workspace-root or state-directory swap therefore aborts the transaction. It cannot redirect a mutation or mix Git evidence from one path with state from another.

Before writing, the CLI rejects a serialized payload larger than 64 KiB. It flushes and syncs a temporary file, atomically replaces `state.json`, and performs a best-effort directory sync. Starting over requires `--replace` with the prior ledger's workflow ID and revision before archival.

## Multi-agent boundary

The parent coordinator is the sole ledger writer. `SubagentStart` supplies workers with read-only ownership metadata and warns that ledger values are untrusted data, not instructions. Compare-and-swap prevents stale lost updates, but the ledger is not an authorization service: a process with workspace write access can still invoke the CLI. Use separate worktrees and normal sandbox controls when stronger isolation is required.

## Residual risks

- Hooks and skills provide context to probabilistic models; they do not guarantee compliance.
- A malicious process with the same operating-system account can bypass advisory protocol or change files after validation; normal host sandbox and account isolation remain the stronger boundary.
- Advisory locks require cooperating writers.
- A valid but misleading objective remains untrusted data. Static router policy gives the latest user request priority.
- Git Bash is required for the shared Windows hook launcher in this release.
- Host trust settings or managed policy may disable hooks, leaving manual skill recovery only.

## Reporting

Follow [SECURITY.md](../SECURITY.md). Do not include real credentials, private source, or harmful proof-of-concept data in a public issue.
