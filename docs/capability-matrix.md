# Capability matrix

**Reviewed:** 2026-07-26

**Release:** 1.2.0-alpha.1

Littlepowers is checkpoint-assisted recovery. The table separates host events, durable state, and model behavior.

| Situation | Mechanism | Expected behavior | Boundary |
| --- | --- | --- | --- |
| Startup or new session | `SessionStart` | Inject a bounded active-ledger snapshot | Hooks can be disabled or blocked by policy |
| Resume, clear, or compaction | `SessionStart` | Reintroduce the last durable checkpoint | Work after the last checkpoint is not recoverable |
| Ordinary next prompt | `UserPromptSubmit` | Inject workflow ID, revision, phase, objective, and next action | This is context, not forced control |
| Same-turn steering | Host prompt handling plus reminder when the event fires | The router attempts to reconcile the message and continue | Littlepowers cannot prevent steering; use Codex Queue to defer a message |
| Status or side question | Router guidance | Answer, then return to the recorded action; while parked at a review gate, answer and keep waiting for approval | Model compliance remains probabilistic |
| Long-running status | Bounded `progress` plus checkpoints | Report a named milestone or acceptance-check count, then continue | Littlepowers does not infer percentages or replace project-management systems |
| Small bounded change with one meaningful decision | Lean plan route | Brainstorm, then write the executable plan directly; create no separate spec/design | Escalate to full shaping if material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback choices appear |
| Approved PRD, prototype, or parent contract | Schema-3 Contract Bind Gate | Bind explicit sources and stable Outcome IDs; record `No scope delta` or distinctly approved `Added / Changed / Deferred / Removed` | IDs and digests protect the reviewed contract; semantic extraction from free-form sources remains a review responsibility |
| Parent source changed or missing | Explicit `check-contract` at lifecycle gates | Record `drifted`, reject executable progress, and require reviewed rebind | Checks read only already bound files; ordinary prompts and Hooks do not refresh digests |
| Plan covers only part of the parent outcome | Outcome Coverage Gate | Reject execution unless every active Outcome ID maps to tasks and named evidence | Coverage proves declared-ID completeness, not that the reviewed Contract captured every free-form requirement |
| Implementation ordering | One continuous implementation stream | Use tasks, checkpoints, rollback units, and small commits while retaining one definition of done | A passed rollback unit is incomplete progress, not a product or technical slice |
| UI, interaction, output, or compatibility fidelity | Approved Baseline and Fidelity Matrix gates | Bind approved provenance and verify every required surface × action × state comparison | Implementation-generated evidence cannot become its own approved baseline |
| Completion claim | Verification Record plus Completion Gate | Freshly require current contract, 100% active coverage, valid scope/baseline/fidelity, three passing verdicts, and zero blockers | The gate reports all current failures and leaves state unchanged when any condition fails |
| Active schema-1/schema-2 workflow after upgrade | Legacy Reconciliation Gate | Show `reconcile_required`; bind the approved Contract and validate the current Plan Map before executable progress | An already-open task cannot hot-load 1.2; start a new task/session after update |
| Clearly unrelated request | Router guidance | Preserve the ledger and use a side task or separate worktree | One worktree has one active workflow |
| Nested repository under a task root with another ledger | Explicit `--root` context plus root-bearing Hook snapshot | Bind recovery to the named nested project and leave the ancestor ledger untouched | The router does not scan siblings or change the host task root |
| Process crash | Ledger | Resume from the last successful checkpoint | Uncheckpointed tool work may be missing |
| Two coordinator writes | Revision compare-and-swap | The stale writer exits with conflict code 3 | Reload and reconcile manually |
| Codex Ultra or Claude dynamic workflow | `SubagentStart` plus skill guidance | Parent coordinator writes; workers are read-only | This is protocol-level ownership, not an OS access-control boundary |
| Replacing active work | `start --replace` | Archive the prior ledger, then create a new workflow ID | Replacement must reflect the latest user intent |
| Paused work | Explicit `pause` and `resume` | Checkpoint cannot silently resume it | A user or coordinator must resume or cancel |
| Ledger older than 30 days | Factual freshness marker plus router guard | Reconcile before continuing; side or status prompts do not restart it | Age is a warning, not proof that the objective is obsolete |
| Ledger artifact read | `read-artifact` with expected workflow ID and revision | Snapshot-bound UTF-8 Markdown returned as untrusted project data | Project content may still be misleading; latest user intent remains authoritative |
| Invalid local state | Shared validator | Hook fails open; CLI reports a fixed error | No recovery context is injected |
| Plugin cache replaced during a task | Host JSON plugin listing plus router guard | Resolve one enabled Littlepowers root and stop before edits | Replacement is not hot reload; load the new runtime at a new task/session boundary |
| Bug, failed test, regression, or unexplained behavior | `debugging-systematically` | Reproduce, trace the earliest supported divergence, test one hypothesis, and repair only when authorized | Skill invocation and model compliance remain probabilistic; diagnosis does not imply edit authority |
| Claim that work is fixed, complete, passing, ready, or released | `verifying-work` | Match each claim to fresh evidence after the latest relevant change | Evidence cannot cover unavailable credentials, platforms, or services; report the limitation |
| Requested review, delegated integration, shared milestone, or material rollback cost | `reviewing-changes` | Read-only work-unit compliance, approved-outcome fidelity, and code-quality verdicts with actionable findings | Littlepowers does not create a reviewer or select a model |
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
- Outcome Lock runs local parsing and explicit-file hashes only at bind,
  transition, resume/readiness, verification, and completion boundaries; it
  does not alter Sol, xhigh, max, or Ultra settings.

### Claude Code

- Native resume, clear, and compaction events refresh the snapshot.
- Dynamic workflows may delegate. Littlepowers keeps ledger ownership at the parent coordinator.
- Organization policy can disable plugin hooks.
- The same debugging, verification, and review skill files are installed; Littlepowers does not change Claude model, effort, or dynamic-workflow settings.
- The same explicit-only boundary policy applies; no background watcher or global worktree registry is installed.
- Outcome Lock uses the shared state CLI and does not alter Fable, Opus, effort,
  or dynamic-workflow settings.

### Qoder

- Qoder CLI and the Qoder IDE share the plugin layout; install with `qodercli plugins install` or the IDE Marketplace panel.
- The hooks manifest resolves `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` so one file serves Claude Code and Qoder.
- The Qoder IDE currently fires only UserPromptSubmit among the Littlepowers hook events; SessionStart snapshots and SubagentStart markers stay silent there while the state CLI remains available. The IDE does not document `QODER_PLUGIN_ROOT` injection for plugin hooks, so hook commands may not resolve the plugin root there until the host provides it.
- The same skills, state CLI, and artifact rules are installed; Littlepowers does not change Qoder model or effort settings.

### OpenCode

- Install rides the `plugin` array in `opencode.json` and the repository root `package.json`; no user config file is edited by the plugin.
- `.opencode/plugins/littlepowers.js` registers the skills directory through the `config` hook and injects the same `hooks/session-start.py` output through `experimental.chat.messages.transform`: the full snapshot on the first user message, the short reminder on later user messages.
- OpenCode has no SubagentStart equivalent, so the worker read-only marker is not injected; coordinator-only ledger writes remain protocol-level.
- The plugin is read-only and fails open; missing Python or missing state injects nothing.

## Unsupported in this prerelease

- Several active top-level workflows in one worktree.
- Recovery without Python 3 or, on Windows, Git Bash.
- Cursor, Pi, or another harness compatibility layer beyond Codex, Claude Code, Qoder, and OpenCode.
- A guarantee that every model follows every recovery reminder.
- Automatic semantic extraction of a complete Outcome Contract from arbitrary
  prose.
