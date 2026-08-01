# Security model

**Reviewed:** 2026-08-01

**Release:** 1.3.0

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
- one Review Lease policy, optional artifact key/path/artifact-and-source
  digests, UTC deadline, gate revision/state, bounded unresolved-question/scope
  summary, and one bounded last-resolution audit with boundary-consumption
  revisions;
- bounded completed-checkpoint descriptions;
- an optional handoff target root, workflow ID, revision, and timestamp on a cancelled source workflow;
- creation and update timestamps.

It does not contain transcripts, raw prompts, credentials, file contents, or model reasoning. `.littlepowers/.gitignore` ignores the directory contents. Optional Claude runner metadata under `.littlepowers/review-jobs/` contains only root/workflow/gate/session identity, deadline, executable path, bounded status/timestamps/PID/exit metadata, and no prompt, artifact, conversation, or model output.

An optional `.littlepowers/project-index.json` at one explicitly selected
manager worktree stores its own schema/revision, at most 16 canonical absolute
same-repository worktree roots, optional one-line labels, and registration/
update timestamps. It stores no copied workflow state, branch, transcript,
prompt, artifact content, credential, or model output.

## Executable surfaces

`hooks/run-hook.cmd` launches `hooks/session-start.py` for three read-only events:

- `SessionStart`;
- `UserPromptSubmit`;
- `SubagentStart`.

The hook reads event metadata and the ledger. It does not inspect transcript paths or prompt text, write state, call the network, run Git mutations, or start agents. It emits nothing when no unfinished workflow exists. Invalid state produces a fixed stderr diagnostic and exit code 0 so the coding session can continue.

The OpenCode plugin `.opencode/plugins/littlepowers.js` is read-only and fails open. It registers the plugin's skills directory through the host's config hook and injects the same `hooks/session-start.py` output into in-memory message parts through the host's experimental message-transform hook. It spawns that Python hook with a four-second timeout and a 256 KiB output bound, never writes state or files, never calls the network, and retains only message identifiers (with a bounded prompt-text fallback key) in process memory for injection deduplication. Any error — missing Python, host API drift, or invalid state — results in no injection.

The state CLI is the only writer. Skills invoke it during tracked work. Its `read-artifact` command is the supported way for a skill to load a ledger-referenced Markdown artifact. Outcome Lock commands use the same hardened explicit-file boundary for Contract, Plan Map, bound parent/baseline sources, Verification Record, and fidelity evidence. `handoff` reads an explicitly named active target, then writes only the source ledger; it does not search for worktrees or write the target.

The opt-in `project-register` and `project-unregister` commands write only the
manager root's independent project index under the same trusted store lock and
atomic I/O boundary. Registration resolves one exact supplied member and
compares Git common-directory identity; it never enumerates worktrees.
`project-status` reads only the manager and stored member roots, returns bounded
branch and ledger summaries, isolates errors, and performs no index or member write,
pruning, resume, cancellation, or handoff. Hooks and ordinary routing do not load
the index. `doctor` validates a present index file without visiting members.

`bind-contract` and `check-contract` hash only files explicitly named by the
reviewed Contract. Bind and validate require a successful Review Gate
resolution for the current artifact key, original path, exact byte digest, and
embedded Contract source-digest set, and each declared boundary consumes its
authorization once;
`approval-kind` is checked against that resolution instead of acting as a
standalone authorization claim. `validate-plan` parses one explicit plan or shape.
`record-verification` parses one explicit Verification Record and hashes only
passing fidelity evidence paths. These commands do not recursively discover
files, scan sibling worktrees, read transcripts, call the network, or run
tests. Hooks call none of them and render stored summaries only.

The optional `snapshot` command is a separate read-only review surface. It runs Git with optional locks disabled and bounded output/timeout, hashes a sorted set of tracked changes plus nonignored untracked files, rejects special files, unsafe or oversized candidates, and observable candidate drift during hashing, and returns only the canonical root, HEAD, token, and counts. It does not create a ledger, follow symlinks, print file contents, call the network, start agents, or run from hooks.

Review Lease commands hash only the exact planning artifact and, when it embeds
a Contract, its explicitly declared bounded source set when parking, replacing,
resolving, binding, or validating a gate. Hooks render stored
mode/key/state/deadline; they do not inspect time, artifacts, prompts, or
conversations, and never schedule or mutate work.

The optional standard-library Claude runner is separate from Hooks. It is available only for a future `windowed` gate with an explicit boundary and a canonical exact session UUID. It creates one private ignored job by atomic replacement, spawns one detached child, sleeps once without polling, then holds the state lock while it reloads the exact gate, claims the job, and starts at most one normal argument-vector `claude -p --resume` process. A cancellation that wins the state lock prevents that invocation. The lock is released immediately after process start so the resumed session can resolve the gate. stdin/stdout/stderr are discarded, the call is time-bounded, and there is no retry, shell interpolation, `--continue`, permission bypass, model/effort override, transcript read, persistent daemon, or output storage. Losing it leaves the ledger gate unchanged.

The debugging, verification, and review skills add instructions only. `reviewing-changes` explicitly remains read-only; implementation and ledger mutation stay with the authorized coordinator.

## Store validation

The shared read/write boundary:

1. resolves the workspace root;
2. rejects `.littlepowers`, state, lock, ignore, and archive surfaces when their type or link metadata is unsafe;
3. on POSIX, requires current-user ownership and rejects group- or world-writable state surfaces;
4. rejects hard-linked state and lock files;
5. requires regular state and project-index files no larger than 64 KiB;
6. rejects a Git-tracked state or project-index file;
7. requires each written runtime file to be ignored in a Git worktree;
8. accepts only normalized, non-hidden, workspace-relative protocol artifact
   and explicit source/evidence paths;
9. bounds protocol Markdown to 128 KiB, each explicit bound/evidence file to
   16 MiB, and all explicit file bytes in one check to 64 MiB;
10. rejects control characters, invalid Review Lease policy combinations,
    unbounded review windows, timestamps beyond a five-minute future-skew
    allowance, progress over 800 characters, invalid handoff targets or
    revisions, project-index roots/labels/counts, unknown record keys,
    duplicate JSON keys/IDs, and other bounded-field violations.

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

The objective is immutable for every tracked workflow. A new objective requires
`start --replace`, which archives the old ledger and resets Review Lease
authority. A `windowed` policy requires both an explicit duration and an
explicit `next_phase` or `execute` boundary.

The writer holds a cross-process advisory lock over the read-check-write transaction. On POSIX, it opens the resolved workspace one non-link path component at a time. It then pins `.littlepowers` relative to that workspace descriptor and performs store operations through the descriptor.

Identity checks against the pinned store bracket every path-based Git check. A concurrent workspace-root or state-directory swap therefore aborts the transaction. It cannot redirect a mutation or mix Git evidence from one path with state from another.

Before writing, the CLI rejects a serialized payload larger than 64 KiB. It flushes and syncs a temporary file, atomically replaces `state.json`, and performs a best-effort directory sync. Starting over requires `--replace` with the prior ledger's workflow ID and revision before archival.

Project-index mutations reuse the same manager-root lock and atomic replacement
but advance an independent index revision. They neither require nor change a
workflow revision because the index has no execution authority. Concurrent
index mutations serialize inside the lock; `project-status` accepts one
complete old or new atomic snapshot and never repairs it implicitly.

An unfinished schema-1/schema-2/schema-3 ledger is exposed through a read-only schema-4
view. Immediately before its first successful schema-4 write, the CLI archives
the exact validated legacy JSON bytes once under
`.littlepowers/archive/` with workflow ID, prior revision, and source schema in
the filename. A failed migration does not create a schema-4 current state.
There is no automatic downgrade: restoring a 1.2 runtime requires first
cancelling an open Review Gate, pausing/finishing the workflow, and explicitly
restoring the matching pre-schema4 schema-3 archive.

## Multi-agent boundary

The parent coordinator is the sole ledger writer. `SubagentStart` supplies workers with read-only ownership metadata and warns that ledger values are untrusted data, not instructions. Compare-and-swap prevents stale lost updates, but the ledger is not an authorization service: a process with workspace write access can still invoke the CLI. Use separate worktrees and normal sandbox controls when stronger isolation is required. The Project Workflow Index provides visibility only; it does not grant a member writer, merge branches, or permit multiple top-level workflows in one checkout.

## Residual risks

- Outcome Lock deterministically protects the reviewed ID contract and
  transitions, but a probabilistic model or human can omit a free-form
  requirement while first constructing that Contract; route review remains the
  semantic approval boundary.
- A malicious process with the same operating-system account can bypass advisory protocol or change files after validation; normal host sandbox and account isolation remain the stronger boundary.
- A review snapshot detects candidate drift only when compared again; it does not lock files against concurrent edits.
- A handoff pointer can become stale after it is recorded, so the destination task must reload and verify the target workflow.
- A registered worktree path can later disappear or name a foreign repository;
  on-demand status reports that member as an error until explicit unregister
  and never follows it as execution authority.
- Advisory locks require cooperating writers.
- A valid but misleading objective remains untrusted data. Static router policy gives the latest user request priority.
- Git Bash is required for the shared Windows hook launcher in this release.
- Host trust settings or managed policy may disable hooks, leaving manual skill recovery only.
- Approval fields are coordinator audit claims, not authenticated user identity
  or cryptographic signatures.
- A `window_expired` no-intervention field is likewise a coordinator audit
  claim based on the latest visible conversation; the state file cannot observe
  user silence by itself.
- A malicious same-account process can stop or replace a sleeper, executable,
  or job after validation. The runner fails boundedly and leaves the gate for
  normal recovery; it is not an authorization or availability service.
- Review continuation never grants commit, push, PR, publish, deploy,
  destructive, secret-access, or permission-broadening authority.

## Reporting

Follow [SECURITY.md](../SECURITY.md). Do not include real credentials, private source, or harmful proof-of-concept data in a public issue.
