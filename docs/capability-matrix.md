# Capability matrix

**Reviewed:** 2026-07-18

**Release:** 0.4.0-alpha.1

Littlepowers is checkpoint-assisted recovery. The table separates host events, durable state, and model behavior.

| Situation | Mechanism | Expected behavior | Boundary |
| --- | --- | --- | --- |
| Startup or new session | `SessionStart` | Inject a bounded active-ledger snapshot | Hooks can be disabled or blocked by policy |
| Resume, clear, or compaction | `SessionStart` | Reintroduce the last durable checkpoint | Work after the last checkpoint is not recoverable |
| Ordinary next prompt | `UserPromptSubmit` | Inject workflow ID, revision, phase, objective, and next action | This is context, not forced control |
| Same-turn steering | Host prompt handling plus reminder when the event fires | The router attempts to reconcile the message and continue | Littlepowers cannot prevent steering; use Codex Queue to defer a message |
| Status or side question | Router guidance | Answer, then return to the recorded action | Model compliance remains probabilistic |
| Long-wave status | Schema-2-compatible `progress` plus checkpoints | Report a named milestone or acceptance-check count, then continue | Littlepowers does not infer percentages or replace project-management systems |
| Clearly unrelated request | Router guidance | Preserve the ledger and use a side task or separate worktree | One worktree has one active workflow |
| Process crash | Ledger | Resume from the last successful checkpoint | Uncheckpointed tool work may be missing |
| Two coordinator writes | Revision compare-and-swap | The stale writer exits with conflict code 3 | Reload and reconcile manually |
| Codex Ultra or Claude dynamic workflow | `SubagentStart` plus skill guidance | Parent coordinator writes; workers are read-only | This is protocol-level ownership, not an OS access-control boundary |
| Replacing active work | `start --replace` | Archive the prior ledger, then create a new workflow ID | Replacement must reflect the latest user intent |
| Paused work | Explicit `pause` and `resume` | Checkpoint cannot silently resume it | A user or coordinator must resume or cancel |
| Ledger older than 30 days | Factual freshness marker plus router guard | Reconcile before continuing; side or status prompts do not restart it | Age is a warning, not proof that the objective is obsolete |
| Ledger artifact read | `read-artifact` with expected workflow ID and revision | Snapshot-bound UTF-8 Markdown returned as untrusted project data | Project content may still be misleading; latest user intent remains authoritative |
| Invalid local state | Shared validator | Hook fails open; CLI reports a fixed error | No recovery context is injected |
| Plugin cache replaced during a task | Host JSON plugin listing plus router guard | Resolve one enabled Littlepowers root, reread current skills, and reload context before edits | This is recovery, not hot reload; missing or ambiguous resolution requires a new task/session |
| Bug, failed test, regression, or unexplained behavior | `debugging-systematically` | Reproduce, trace the earliest supported divergence, test one hypothesis, and repair only when authorized | Skill invocation and model compliance remain probabilistic; diagnosis does not imply edit authority |
| Claim that work is fixed, complete, passing, ready, or released | `verifying-work` | Match each claim to fresh evidence after the latest relevant change | Evidence cannot cover unavailable credentials, platforms, or services; report the limitation |
| Requested review, delegated integration, shared milestone, or material rollback cost | `reviewing-changes` | Read-only acceptance/spec and code-quality verdicts with actionable findings | Littlepowers does not create a reviewer or select a model |
| Tiny isolated edit | Focused self-review and local verification | Run the direct check and inspect the independent rollback unit | A small textual edit still escalates when it changes a shared manifest, hook, API, or release surface |
| Transfer to another workspace root | Explicit `handoff` with both workflow IDs and revisions | Verify an existing active target, cancel only the source, and continue in a new target-root task/session | No sibling scan, target mutation, automatic task creation, or current-root switch |
| Broad uncommitted review candidate | Explicit bounded `snapshot` before review and verdict acceptance | Bind the verdict to a content-free token and invalidate it when the candidate changes | Hooks and ordinary routes never hash the worktree; a snapshot is evidence, not a lock |
| Review too large for one reliable pass | Partition by trust, state ownership, or rollback boundary | Review exact partitions, then aggregate shared-interface acceptance once | Littlepowers does not create reviewers, choose models, or duplicate broad tests |

## Host-specific controls

### Codex

- Queue is the reliable way to hold a follow-up until the current run finishes.
- `/side` and `/btw` isolate unrelated questions.
- `/goal` is not recommended alongside Littlepowers because it creates a second objective source.
- Ultra may delegate automatically. Littlepowers itself does not request delegation.
- The three engineering-discipline skills use native discovery and do not change Codex model or effort settings.
- Handoff, review snapshots, and review partitioning are explicit; the ordinary route adds no agent/model call, Git scan, hash, or test run.

### Claude Code

- Native resume, clear, and compaction events refresh the snapshot.
- Dynamic workflows may delegate. Littlepowers keeps ledger ownership at the parent coordinator.
- Organization policy can disable plugin hooks.
- The same debugging, verification, and review skill files are installed; Littlepowers does not change Claude model, effort, or dynamic-workflow settings.
- The same explicit-only boundary policy applies; no background watcher or global worktree registry is installed.

## Unsupported in this prerelease

- Several active top-level workflows in one worktree.
- Recovery without Python 3 or, on Windows, Git Bash.
- Cursor, OpenCode, Pi, or another harness compatibility layer.
- A guarantee that every model follows every recovery reminder.
