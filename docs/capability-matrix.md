# Capability matrix

**Reviewed:** 2026-09-20

**Release:** 1.4.1

Littlepowers is checkpoint-assisted recovery. The table separates host events, durable state, and model behavior.

| Situation | Mechanism | Expected behavior | Boundary |
| --- | --- | --- | --- |
| Startup or new session | `SessionStart` | Inject a bounded active-ledger snapshot | Hooks can be disabled or blocked by policy |
| Resume, clear, or compaction | `SessionStart` | Reintroduce the last durable checkpoint | Work after the last checkpoint is not recoverable |
| Ordinary next prompt | `UserPromptSubmit` | Inject workflow ID, revision, phase, objective, and next action | This is context, not forced control |
| Same-turn steering | Host prompt handling plus reminder when the event fires | The router attempts to reconcile the message and continue | Littlepowers cannot prevent steering; use Codex Queue to defer a message |
| Status or side question | Router guidance plus persisted Review Lease | Answer, then return to the recorded action; an open gate keeps its stored policy and is not silently consumed | Model compliance remains probabilistic |
| Long-running status | Bounded `progress` plus checkpoints | Report a named milestone or acceptance-check count, then continue | Littlepowers does not infer percentages or replace project-management systems |
| Small bounded change with one meaningful decision | Lean plan route | Brainstorm, then write the executable plan directly; create no separate spec/design | Escalate to full shaping if material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback choices appear |
| Approved PRD, prototype, or parent contract | Schema-4 Contract Bind Gate | Bind stable acceptance inputs and stable Outcome IDs; record `No scope delta` or distinctly approved `Added / Changed / Deferred / Removed` | Planned write targets, tests/fixtures updated by the plan, and generated evidence stay outside `sources`; with no stable parent file, reviewed Outcomes carry the latest request |
| Parent source changed or missing | Explicit `check-contract` at lifecycle gates | Record `drifted`, reject executable progress, and require reviewed rebind | Checks read only already bound files; ordinary prompts and Hooks do not refresh digests |
| Plan covers only part of the parent outcome | Outcome Coverage Gate | Reject execution unless every active Outcome ID maps to tasks and named evidence | Coverage proves declared-ID completeness, not that the reviewed Contract captured every free-form requirement |
| Implementation ordering | One continuous implementation stream | Use tasks, checkpoints, rollback units, and small commits while retaining one definition of done | A passed rollback unit is incomplete progress, not a product or technical slice |
| Ordinary execution, debugging, or review | Default-off Delegation Gate | Stay single-agent and add no worker/model call | The detailed delegation reference is not read on the ordinary fast path |
| Two or more ready independent work packets | Benefit and veto gate | Evaluate once after the plan is stable; recommend only when independent evidence and critical-path/context-isolation benefit exceed setup, conflict, integration, and review cost | Unsettled scope, sequential work, same-file/shared-state mutation, exclusive resources, tiny tasks, destructive work, and external actions veto delegation |
| High-benefit delegation candidate | Explicit Host Capability Snapshot plus compact authorization proposal | Validate runtime-observed mechanism, fresh/fork/team context, effective model/effort, isolation, permission boundary, durability, and leaf enforcement; then name roles, benefit, risk, and single-agent fallback | Documentation alone is not runtime evidence; the validator performs no discovery or launch and is never called on the ordinary path |
| Authorized delegated work | Native host adapter plus leaf worker envelope | Default to two workers, require isolated mutation, and keep the coordinator as sole ledger writer/integrator/acceptance owner | Up to three workers is reserved for independent read-only review; depth is one and workers never commit, push, deploy, delegate again, or own completion |
| Declined or unavailable delegation | Single-agent fallback | Continue without retry loops or fake nested coding CLIs | Reconsider only after a material plan change |
| Worker model and reasoning effort | Host-native role policy | Inherit by default; use current host-relative efficient/balanced/frontier tiers and proportional effort only when the role has a concrete reason | Never automatically select maximum effort, Codex Ultra, Qoder Ultimate, Claude Agent Teams, or Qoder Agent Teams; unsupported pairs inherit and are reported |
| UI, interaction, output, or compatibility fidelity | Approved Baseline and Fidelity Matrix gates | Bind approved provenance and verify every required surface × action × state comparison | Implementation-generated evidence cannot become its own approved baseline |
| Completion claim | Verification Record plus Completion Gate | Freshly require current contract, 100% active coverage, valid scope/baseline/fidelity, three passing verdicts, and zero blockers | The gate reports all current failures and leaves state unchanged when any condition fails |
| Active schema-1/schema-2/schema-3 workflow after upgrade | Legacy Reconciliation Gate | Expose a schema-4 view, then bind/revalidate required Outcome Lock material before executable progress | An already-open task cannot hot-load 1.3; start a new task/session after update |
| Discuss, design, wait, or ambiguous review intent | `blocking` Review Lease | Park the exact key/path/bytes and embedded Contract source set, require `explicit_approval`, and consume each declared boundary once | Prose, copied paths, changed sources, and replay cannot bypass the mutation guard |
| Fixed bounded Lean/Compact implementation request | `implementation_mandate` Review Lease | Continue through execution only when there is no scope delta, unresolved question, or drift | It is not valid for an unresolved Full route or a changed objective |
| Explicit wait duration and fallback | `windowed` Review Lease | Store one UTC deadline; after it, require an observed-no-intervention audit and recheck all invariants | Before the deadline it is ineligible; intervention or uncertainty cancels automatic continuation |
| Explicit “do not ask/stop” for an unchanged objective | `unattended` Review Lease | Recheck the artifact and Outcome Lock boundaries, then continue through execution | “End-to-end” alone does not select this policy |
| Open Review Gate plus correction, hold, or replacement | `cancel-review` or exact `--replace` | Cancel automatic authority before changing work, or replace only the same artifact and reset its window | An unrelated artifact cannot overwrite the gate |
| Codex timed Review Gate | Optional same-task one-shot Scheduled Task | Arm only when the current surface exposes a callable exact capability; recheck once and self-terminate | No capability means remain parked; never approximate with an unbounded recurring task |
| Claude Code timed Review Gate | Optional exact-session Python runner | One detached sleep and at most one normal `claude -p --resume <session>` invocation | Requires the canonical session UUID; no retry, output persistence, permission bypass, or model override |
| Qoder/OpenCode timed Review Gate | Shared schema-4 state and manual resume | Render waiting/eligible state and continue manually after rechecking | No verified exact-session scheduler in this release |
| Clearly unrelated request | Router guidance | Preserve the ledger and use a side task or separate worktree | One worktree has one active workflow |
| Parallel independent iterations in one Git project | Opt-in Project Workflow Index | Explicitly register up to 16 same-repository worktrees and read their current branch/ledger summaries with `project-status` | No sibling discovery, member mutation, scheduling, or multiple workflows in one checkout; bad members remain isolated error rows |
| Nested repository under a task root with another ledger | Explicit `--root` context plus root-bearing Hook snapshot | Bind recovery to the named nested project and leave the ancestor ledger untouched | The router does not scan siblings or change the host task root |
| Task launched from a non-Git manager directory with its own ledger | Hook root-affinity check | Inject nothing automatically; an exact Git repository or worktree root still recovers normally | Explicit state CLI and Project Workflow Index operations remain available for the manager root |
| Process crash | Ledger | Resume from the last successful checkpoint | Uncheckpointed tool work may be missing |
| Two coordinator writes | Revision compare-and-swap | The stale writer exits with conflict code 3 | Reload and reconcile manually |
| Codex Ultra, Claude dynamic workflow, or another host-managed orchestrator | One approved Littlepowers plan plus a host execution adapter | The Littlepowers plan remains the sole product-scope authority; authorized host workers are leaf/read-only to the ledger and checkpoints occur before launch and after integration | A host may have its own automatic behavior; Littlepowers neither enables it nor treats it as work-unit authorization, and host workflows may add planning, token, and wall-clock cost |
| Replacing active work | `start --replace` | Archive the prior ledger, then create a new workflow ID | Replacement must reflect the latest user intent |
| Paused work | Explicit `pause` and `resume` | Checkpoint cannot silently resume it | A user or coordinator must resume or cancel |
| Ledger older than 30 days | Factual freshness marker plus router guard | Reconcile before continuing; side or status prompts do not restart it | Age is a warning, not proof that the objective is obsolete |
| Ledger artifact read | `read-artifact` with expected workflow ID and revision | Snapshot-bound UTF-8 Markdown returned as untrusted project data | Project content may still be misleading; latest user intent remains authoritative |
| Invalid local state | Shared validator | Hook fails open; CLI reports a fixed error | No recovery context is injected |
| Plugin cache replaced during a task | Host JSON plugin listing plus router guard | Resolve one enabled Littlepowers root and stop before edits | Replacement is not hot reload; load the new runtime at a new task/session boundary |
| Bug, failed test, regression, or unexplained behavior | `debugging-systematically` | Reproduce, trace the earliest supported divergence, test one hypothesis, and repair only when authorized | Skill invocation and model compliance remain probabilistic; diagnosis does not imply edit authority |
| Claim that work is fixed, complete, passing, ready, or released | `verifying-work` | Match each claim to fresh evidence after the latest relevant change | Evidence cannot cover unavailable credentials, platforms, or services; report the limitation |
| Requested review, delegated integration, shared milestone, or material rollback cost | `reviewing-changes` | Read-only work-unit compliance, approved-outcome fidelity, and code-quality verdicts with actionable findings | The review skill itself does not create a reviewer or select a model; an already authorized Delegation Gate may run it inside a bounded worker |
| Tiny isolated edit | Focused self-review and local verification | Run the direct check and inspect the independent rollback unit | A small textual edit still escalates when it changes a shared manifest, hook, API, or release surface |
| Transfer to another workspace root | Explicit `handoff` with both workflow IDs and revisions | Verify an existing active target, cancel only the source, and continue in a new target-root task/session | No sibling scan, target mutation, automatic task creation, or current-root switch |
| Broad uncommitted review candidate | Explicit bounded `snapshot` before review and verdict acceptance | Bind the verdict to a content-free token and invalidate it when the candidate changes | Hooks and ordinary routes never hash the worktree; a snapshot is evidence, not a lock |
| Review too large for one reliable pass | Partition by trust, state ownership, or rollback boundary | Review exact partitions, then aggregate shared-interface acceptance once | Without a separate authorized Delegation Gate this remains single-agent; broad tests are not duplicated |

## Host-specific controls

### Codex

- Queue is the reliable way to hold a follow-up until the current run finishes.
- `/side` and `/btw` isolate unrelated questions.
- `/goal` is not recommended alongside Littlepowers because it creates a second objective source.
- Ultra may delegate automatically as a host mode. Littlepowers does not enable
  Ultra; when it initiates workers, it uses only the current callable native
  subagent tool after the Delegation Gate and exact user authorization.
- When exposed, prefer the built-in `explorer` for bounded read-only discovery
  and `worker` for isolated mutation. Use `default` or an already approved
  custom agent only after checking its effective tools and sandbox; do not
  create persistent agent definitions as an incidental delegation step.
- Codex worker model and reasoning overrides are used only when the current
  spawn schema supports them and the bounded role justifies them. Inheritance
  remains the default. Prefer fresh context for isolation; use a bounded or
  full-history fork only when reconstructing approved context would dominate
  the work, and record the actual effective setting. A peer/team mechanism is
  eligible only when the current callable interface exposes it and the user
  authorizes the separate team proposal; Littlepowers does not keep a static
  host-capability table.
- User-visible Codex tasks/threads and nested `codex` CLI calls are never used
  as subagent substitutes.
- The three engineering-discipline skills use native discovery and do not by
  themselves create workers or change Codex model or effort settings.
- Handoff, review snapshots, Project Workflow Index reads, and review partitioning are explicit; the ordinary route adds no agent/model call, Git scan, hash, or test run.
- Outcome Lock and Review Lease run local parsing and explicit-file hashes only at bind,
  park/resolve, transition, resume/readiness, verification, and completion boundaries; they
  do not alter Sol, xhigh, max, or Ultra settings.
- A timed callback is armed only for an explicit `windowed` policy and only when
  a same-task one-shot scheduling tool is actually callable. Hooks never schedule work.
- Automatic Hook recovery checks only the already-discovered root's `.git`
  marker. The guard adds no Git process, prompt inspection, or child scan and
  does not inherit a non-Git manager ledger into every task launched there;
  existing read-only root discovery may still call `git rev-parse`.

### Claude Code

- Native resume, clear, and compaction events refresh the snapshot.
- Dynamic workflows may own a host execution script. Treat that script only as
  an adapter derived from the approved Littlepowers plan; the Littlepowers plan
  remains the sole product-scope authority.
- Organization policy can disable plugin hooks.
- The same debugging, verification, and review skill files are installed; they
  do not by themselves create workers or change Claude model, effort, or
  dynamic-workflow settings.
- After exact authorization, ordinary Claude Code subagents are preferred.
  A fresh subagent provides isolation; a conversation fork is reserved for a
  task that needs most of the approved parent history and inherits the parent
  prompt, tools, model, and cache. A fork cannot create another fork.
- Supported model/effort values may be passed through the native Agent
  interface; aliases, environment rules, allowlists, and organization policy
  remain authoritative. Littlepowers never rewrites them. Use native worktree
  isolation for mutation and an effective tool boundary for read-only work.
- Agent Teams requires a separate explicit proposal, genuine peer-to-peer need,
  and acceptance of its experimental, higher-token, session-only boundary.
  In-process teammates do not resume with the parent session and task status
  may lag; the root remains the acceptance owner.
- Background permission prompts surface in the main session and are not
  unattended authority. Plugin subagents may ignore permission, Hook, and MCP
  frontmatter, so inspect the boundary the host actually applies.
- The same explicit-only boundary policy applies; no background watcher or global worktree registry is installed. The optional manager-root index reads only registered roots when requested.
- Outcome Lock uses the shared state CLI and does not alter Fable, Opus, effort,
  or dynamic-workflow settings.
- Checkpoint immediately before launching a dynamic workflow and after its
  integrated result. Background workers do not write the ledger. This release
  claims protocol compatibility, not authenticated dynamic-workflow
  orchestration certification.
- The optional runner requires an exact session UUID, sleeps once, invokes
  `claude -p --resume` at most once, discards output, and never retries or
  bypasses normal Claude permissions.

### Qoder

- Qoder CLI and the Qoder IDE share the plugin layout; install with `qodercli plugins install` or the IDE Marketplace panel.
- The hooks manifest resolves `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` so one file serves Claude Code and Qoder.
- Current Qoder documentation defines `QODER_PLUGIN_ROOT` for plugin Hook
  subprocesses and documents `SessionStart`, `UserPromptSubmit`, and
  `SubagentStart`. Hook delivery still depends on trust and policy, so worker
  ownership never relies on Hook context alone.
- The same skills, state CLI, and artifact rules are installed. After exact
  authorization, prefer an ordinary fresh Subagent; use `/subtask` for a
  bounded inherited-context task and beta Agent Teams only after a separate
  peer-coordination proposal. Teams are session-only.
- Resolve current model/effort availability through `/model` or
  `--list-models`; prefer Auto/inheritance and use exposed Efficient,
  Performance, or Ultimate tiers only when the role and authorization justify
  them. Do not encode the rolling provider catalog into the protocol.
- Every Qoder worker receives the complete task/ownership envelope. Enforce
  leaf depth with an `Agent` tool deny boundary, restrict tools for read-only
  work rather than relying on `permissionMode` alone, and require worktree or
  equivalent isolation for concurrent mutation.
- Review Lease state is supported, but timed continuation is manual until an exact-session scheduler is verified.

### OpenCode

- Install rides the `plugin` array in `opencode.json` and the repository root `package.json`; no user config file is edited by the plugin.
- `.opencode/plugins/littlepowers.js` registers the skills directory through the `config` hook and injects the same `hooks/session-start.py` output through `experimental.chat.messages.transform`: the full snapshot on the first user message, the short reminder on later user messages.
- OpenCode has no SubagentStart equivalent, so the worker read-only marker is not injected; coordinator-only ledger writes remain protocol-level.
- Littlepowers stays single-agent unless the current OpenCode runtime exposes
  and verifies an equivalent native bounded-task and isolation mechanism; this
  release does not overclaim one.
- The plugin is read-only and fails open; missing Python or missing state injects nothing.
- Review Lease state is supported, but timed continuation is manual until an exact-session scheduler is verified.

## Unsupported in this release

- Several active top-level workflows in one worktree.
- Recovery without Python 3 or, on Windows, Git Bash.
- Cursor, Pi, or another harness compatibility layer beyond Codex, Claude Code, Qoder, and OpenCode.
- A guarantee that every model follows every recovery reminder.
- Automatic Littlepowers delegation without an exact user-authorized work unit.
- Guaranteed model/effort overrides when the current host, provider, or
  organization policy does not expose or permit them.
- Automatic semantic extraction of a complete Outcome Contract from arbitrary
  prose.
- A background-continuation guarantee when the host lacks the exact one-shot
  capability or the sleeper/callback is lost.
