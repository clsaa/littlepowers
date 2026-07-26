# Security model

**Reviewed:** 2026-07-26

**Release:** 1.2.0-alpha.1

## Assets and trust boundary

Littlepowers protects the user's repository, files outside the workspace, workflow integrity, and prompt context. The repository being worked on may be untrusted. Ledger values, artifact paths, and artifact content are data, not instructions.

The plugin trusts the installed Littlepowers package and the local Python runtime. It does not treat a repository-provided `.littlepowers` path as trusted merely because it is inside the workspace.

## Data stored

`.littlepowers/state.json` contains:

- schema/protocol identity, workflow ID, and revision;
- status, phase, objective, current task, optional observable progress, and next action;
- relative artifact paths;
- Outcome Lock source paths and SHA-256 digests, Contract/Plan/Verification
  semantic digests, coverage/baseline/fidelity/verdict summaries, drift reasons,
  and audit claims for route review and distinct scope-delta approval;
- bounded completed-checkpoint descriptions;
- an optional handoff target root, workflow ID, revision, and timestamp on a cancelled source workflow;
- creation and update timestamps.

It does not contain transcripts, raw prompts, credentials, file contents, or model reasoning. `.littlepowers/.gitignore` ignores the directory contents.

## Executable surfaces

`hooks/run-hook.cmd` launches `hooks/session-start.py` for three read-only events:

- `SessionStart`;
- `UserPromptSubmit`;
- `SubagentStart`.

The hook reads event metadata and the ledger. It does not inspect transcript paths or prompt text, write state, call the network, run Git mutations, or start agents. It emits nothing when no unfinished workflow exists. Invalid state produces a fixed stderr diagnostic and exit code 0 so the coding session can continue.

The OpenCode plugin `.opencode/plugins/littlepowers.js` is read-only and fails open. It registers the plugin's skills directory through the host's config hook and injects the same `hooks/session-start.py` output into in-memory message parts through the host's experimental message-transform hook. It spawns that Python hook with a four-second timeout and a 256 KiB output bound, never writes state or files, never calls the network, and retains only message identifiers (with a bounded prompt-text fallback key) in process memory for injection deduplication. Any error — missing Python, host API drift, or invalid state — results in no injection.

The state CLI is the only writer. Skills invoke it during tracked work. Its `read-artifact` command is the supported way for a skill to load a ledger-referenced Markdown artifact. Outcome Lock commands use the same hardened explicit-file boundary for Contract, Plan Map, bound parent/baseline sources, Verification Record, and fidelity evidence. `handoff` reads an explicitly named active target, then writes only the source ledger; it does not search for worktrees or write the target.

`bind-contract` and `check-contract` hash only files explicitly named by the
reviewed Contract. `validate-plan` parses one explicit plan or shape.
`record-verification` parses one explicit Verification Record and hashes only
passing fidelity evidence paths. These commands do not recursively discover
files, scan sibling worktrees, read transcripts, call the network, or run
tests. Hooks call none of them and render stored summaries only.

The optional `snapshot` command is a separate read-only review surface. It runs Git with optional locks disabled and bounded output/timeout, hashes a sorted set of tracked changes plus nonignored untracked files, rejects special files, unsafe or oversized candidates, and observable candidate drift during hashing, and returns only the canonical root, HEAD, token, and counts. It does not create a ledger, follow symlinks, print file contents, call the network, start agents, or run from hooks.

The v0.4 debugging, verification, and review skills add instructions only. The Unreleased continuity update adds one bounded state field through the existing CLI but no Hook event, network client, or execution privilege. `reviewing-changes` explicitly remains read-only; implementation and ledger mutation stay with the authorized coordinator.

## Store validation

The shared read/write boundary:

1. resolves the workspace root;
2. rejects `.littlepowers`, state, lock, ignore, and archive surfaces when their type or link metadata is unsafe;
3. on POSIX, requires current-user ownership and rejects group- or world-writable state surfaces;
4. rejects hard-linked state and lock files;
5. requires a regular state file no larger than 64 KiB;
6. rejects a Git-tracked state file;
7. requires the ledger to be ignored in a Git worktree;
8. accepts only normalized, non-hidden, workspace-relative protocol artifact
   and explicit source/evidence paths;
9. bounds protocol Markdown to 128 KiB, each explicit bound/evidence file to
   16 MiB, and all explicit file bytes in one check to 64 MiB;
10. rejects control characters, timestamps beyond a five-minute future-skew
    allowance, progress over 800 characters, invalid handoff targets or
    revisions, unknown record keys, duplicate JSON keys/IDs, and other
    bounded-field violations.

Hook context is bounded to 10,000 characters and only includes the ten most recent completed entries. It labels records older than 30 days as stale by age and marks paused records as requiring explicit resume.

Recovery context also includes the canonical workspace root used to load the ledger. This is a local filesystem path already available to the host process; it is included so the model can distinguish a nested project ledger from an unrelated ancestor ledger. The Hook does not discover or list sibling roots.

The shared explicit-file reader walks workspace directories without following
links where the operating system supports descriptor-relative access. It
rejects stale snapshots where applicable, hidden/escaping paths, links,
reparse points, hard links, special files, unexpected ownership or write
permissions, replacement during a read, non-UTF-8 protocol content, and
oversized input. `read-artifact` returns workflow/revision identifiers and
labels content as untrusted project data.

## Write integrity

Each workflow has a UUID and monotonic revision. Every mutation after `start` supplies the expected UUID and revision. A mismatch exits with code 3 and does not write.

The writer holds a cross-process advisory lock over the read-check-write transaction. On POSIX, it opens the resolved workspace one non-link path component at a time. It then pins `.littlepowers` relative to that workspace descriptor and performs store operations through the descriptor.

Identity checks against the pinned store bracket every path-based Git check. A concurrent workspace-root or state-directory swap therefore aborts the transaction. It cannot redirect a mutation or mix Git evidence from one path with state from another.

Before writing, the CLI rejects a serialized payload larger than 64 KiB. It flushes and syncs a temporary file, atomically replaces `state.json`, and performs a best-effort directory sync. Starting over requires `--replace` with the prior ledger's workflow ID and revision before archival.

An unfinished schema-1/schema-2 ledger is exposed through a read-only schema-3
view with `reconcile_required`. Immediately before its first successful
schema-3 write, the CLI archives the exact validated legacy JSON once under
`.littlepowers/archive/` with workflow ID, prior revision, and source schema in
the filename. A failed migration does not create a schema-3 current state.
There is no automatic downgrade: restoring a 1.1 runtime requires explicitly
restoring the matching pre-schema3 archive first.

## Multi-agent boundary

The parent coordinator is the sole ledger writer. `SubagentStart` supplies workers with read-only ownership metadata and warns that ledger values are untrusted data, not instructions. Compare-and-swap prevents stale lost updates, but the ledger is not an authorization service: a process with workspace write access can still invoke the CLI. Use separate worktrees and normal sandbox controls when stronger isolation is required.

## Residual risks

- Outcome Lock deterministically protects the reviewed ID contract and
  transitions, but a probabilistic model or human can omit a free-form
  requirement while first constructing that Contract; route review remains the
  semantic approval boundary.
- A malicious process with the same operating-system account can bypass advisory protocol or change files after validation; normal host sandbox and account isolation remain the stronger boundary.
- A review snapshot detects candidate drift only when compared again; it does not lock files against concurrent edits.
- A handoff pointer can become stale after it is recorded, so the destination task must reload and verify the target workflow.
- Advisory locks require cooperating writers.
- A valid but misleading objective remains untrusted data. Static router policy gives the latest user request priority.
- Git Bash is required for the shared Windows hook launcher in this release.
- Host trust settings or managed policy may disable hooks, leaving manual skill recovery only.
- Approval fields are coordinator audit claims, not authenticated user identity
  or cryptographic signatures.

## Reporting

Follow [SECURITY.md](../SECURITY.md). Do not include real credentials, private source, or harmful proof-of-concept data in a public issue.
