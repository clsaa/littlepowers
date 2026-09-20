# Opt-in delegation protocol

Read this reference only when the main router has found a high-benefit
delegation candidate, the user explicitly requests subagents for the current
work unit, or an already authorized delegated result is being integrated. The
host—not Littlepowers—owns agent creation, model availability, permissions,
and isolation. Littlepowers supplies the decision and ownership boundary.

## Default and evaluation point

Stay single-agent by default. Do not create a scout merely to decide whether
to create scouts, and do not read this reference on the ordinary fast path.

Evaluate delegation at most once at one of these stable boundaries:

- after an approved Contract and Plan Map make two or more execution tasks
  ready;
- after a reproduced failure yields at least two independent diagnostic
  hypotheses with separate evidence paths;
- before a material review whose independent perspectives can inspect the same
  immutable candidate without coordinating edits.

A materially changed plan may be evaluated once again. A status prompt,
compaction, retry, or new phase label is not a material change.

## Benefit and veto gate

Recommend delegation only when all of these are true:

1. At least two bounded work packets are ready now.
2. They have no ordering dependency, shared mutable file, or exclusive
   resource.
3. Each packet has an independently verifiable output and stop condition.
4. Context isolation or critical-path reduction is likely to outweigh setup,
   duplicated context, integration, conflict, and review cost.
5. The current host exposes a callable native delegation mechanism with the
   required permission and isolation boundary.

Any one of these conditions vetoes delegation:

- unresolved product scope, architecture, interaction, migration, or
  acceptance decisions;
- sequential discovery where one result determines the next task;
- same-file edits or shared mutable database, port, simulator, device, build
  output, deployment target, or external account;
- a Direct or tiny task whose likely completion time is comparable to worker
  setup and integration;
- destructive, irreversible, secret-bearing, permission-broadening, publish,
  deploy, or other externally visible work;
- no safe native host mechanism. Never replace it with nested shell invocations
  of Codex, Claude, Qoder, or another coding CLI.

Parallel read-only investigation may remain safe when mutation is vetoed, but
only if its hypotheses or review perspectives are genuinely independent.

## Authorization proposal

When the gate passes, present one compact proposal and wait for the answer:

```text
Subagent recommendation
- Why: <measured or concrete critical-path/context benefit>
- Workers: <count and bounded roles>
- Host capability: <mechanism, runtime evidence source, fresh|fork|team context>
- Effective settings: <model and effort, normally inherit>
- Boundary: <isolation, permission/tool control, durability, leaf enforcement>
- Integration owner: root coordinator
- Main risk: <coordination or quality risk>
- If declined/unavailable: continue single-agent
Use subagents for this work unit?
```

Do not launch before explicit authorization for the current work unit. An
explicit user instruction to use named subagents for that bounded unit already
supplies authorization; a generic preference for speed, parallelism, or Ultra
does not. Authorization is scoped to the workflow, current approved plan,
roles, actions, and isolation described in the proposal. A material scope,
plan, role, action, or authority change invalidates it.

For tracked work, checkpoint a pending recommendation before waiting and an
approved or declined decision before continuing. These short `progress` and
`next_action` facts aid recovery but are not authenticated authority. After an
interruption, if the exact authorization cannot be established from the latest
visible request and unchanged plan, stay single-agent or ask again. Never infer
authorization from ledger prose alone.

If the user declines, the native mechanism is unavailable, or a supported
model/effort pair cannot be selected, continue single-agent without a retry
loop. Do not repeat the proposal unless the approved plan changes materially.

## Host Capability Snapshot

Only after the benefit gate passes, collect one short snapshot from the current
callable host interface. Documentation proves that a capability can exist; it
does not prove that the current session exposes it. Use one of these evidence
sources: the actual worker tool schema, a current host capability command, or
an already approved agent definition loaded by the host.

Record exactly these launch facts:

```text
Host capability
- Host/mechanism: <codex|claude|qoder|other> / <native mechanism>
- Source/context: <tool-schema|host-command|approved-agent-definition> / <fresh|fork|team>
- Effective model/effort: <inherit or current supported values>
- Isolation/permission: <read-only|worktree|equivalent> / <enforced tool, sandbox, or host boundary>
- Durability/leaf: <resumable|session-only|unknown> / nested delegation blocked by <tool-disabled|host-depth-limit>
```

Validate the explicit facts with the dependency-free helper when it is
available:

```bash
<python> <plugin-root>/scripts/littlepowers_delegation.py \
  --host <host> --mechanism <native-mechanism> \
  --capability-source <tool-schema|host-command|approved-agent-definition> \
  --context-mode <fresh|fork|team> \
  --effective-model <inherit-or-effective-model> \
  --effective-effort <inherit-or-effective-effort> \
  --isolation <read-only|worktree|equivalent> \
  --permission-boundary <tool-restricted|sandbox-read-only|host-policy|worktree> \
  --durability <resumable|session-only|unknown> \
  --nested-delegation blocked --leaf-boundary <tool-disabled|host-depth-limit> \
  [--mutation] [--team-boundary-declared]
```

The helper normalizes supplied observations and enforces stable Littlepowers
boundaries. It does not discover a host, inspect configuration, read the
repository or ledger, select a model, authorize a launch, or create a worker.
It is never called on the ordinary single-agent path. If the facts cannot form
a valid snapshot, use a safer supported boundary or continue single-agent; do
not probe model aliases or weaken isolation in a retry loop.
Report all rejected boundaries together. A declaration is not enforcement:
never relabel `available` or `unknown` nested delegation as `blocked`, or a
prompt-only permission as a tool/sandbox restriction, without new native
evidence. A failed snapshot ends this attempt unless an already exposed,
safer mechanism actually changes the observed facts.
`blocked` requires native evidence that the worker cannot call a delegation
tool, or that the effective host depth limit prevents another level. A worker
prompt, role name, or unverified configuration key does not establish this.
An approved agent definition is evidence only for fields the current host
actually applies. If enforcement is unavailable, report the limitation and
continue single-agent; do not silently downgrade this gate to a prompt rule.

## Host adapters

Use only controls callable in the current runtime. Documentation about a host
capability is not proof that the current task exposes it.

### Codex

- Use the current Codex native subagent/spawn tool. Do not create or fork
  user-visible Codex tasks as workers and do not invoke a nested `codex` CLI.
- Prefer a current built-in `explorer` for bounded read-only discovery and a
  `worker` for isolated mutation when those roles are exposed; otherwise use
  `default` or an already approved custom agent whose effective tools and
  sandbox match the task. Never create or edit a persistent agent definition as
  an incidental delegation step.
- Read the actual spawn schema before selecting fresh, forked, or peer/team
  context, a model, reasoning effort, sandbox, or tool boundary. Prefer fresh
  context for isolation and use a bounded/full-history fork only when
  recreating the approved context would dominate the task. Use a peer/team
  context only when the current interface actually exposes it and the separate
  team proposal is authorized. Inspect the effective setting because explicit
  launch values, host defaults, inheritance, and custom agent definitions can
  all participate in resolution. The validator deliberately has no static
  host-capability catalog; the current callable interface remains authority.
- Do not select Ultra automatically. Some Codex surfaces expose `ultra` as a
  host-native worker reasoning value even though public API effort values may
  differ. Use it only when the actual spawn schema supports it, the proposal
  names its cost/latency tradeoff, and the user explicitly authorizes it;
  otherwise inherit.

### Claude Code

- Prefer an ordinary fresh subagent for context isolation. Use the built-in
  read-only Explore agent when it fits and is currently exposed. Use a
  conversation fork only when the worker needs most of the approved parent
  history: a fork inherits the conversation, system prompt, tools, model, and
  prompt cache, and it cannot spawn another fork.
- Use Agent Teams only after a separate explicit proposal when workers need
  peer-to-peer communication. Treat a team as experimental and session-only:
  in-process teammates do not resume with the parent session, task status can
  lag, and only the lead owns integration and completion.
- Pass a supported model alias/full identifier and effort only through the
  current native Agent interface or an already approved project agent
  definition. Never edit user configuration, environment variables, allowlists,
  or organization policy to make a selection work.
- Host aliases, environment rules, provider routing, and allowlists may override
  a request. Report the effective limitation and inherit rather than retrying.
- Require `isolation: worktree` or an equivalent native boundary for mutation.
  Background permission prompts surface in the main session and are not
  unattended authority. Plugin-provided Claude agents ignore some permission,
  Hook, and MCP fields, so use the actual effective tool boundary rather than
  trusting frontmatter that the host discards.

### Qoder

- Prefer an ordinary fresh Subagent. Use `/subtask` only when the bounded task
  benefits from inheriting the current session context, and use beta Agent
  Teams only after a separate explicit proposal for genuine peer coordination;
  treat a team as session-only.
- Resolve models and effort from the current `/model` or `--list-models`
  surface. Prefer `Auto`/inheritance; role-relative Efficient, Performance, or
  Ultimate tiers may be proposed only when currently exposed and justified.
  Do not hard-code the rolling provider model catalog into Littlepowers.
- Enforce leaf depth with the current tool boundary, such as
  `disallowedTools: [Agent]`. For read-only work, restrict visible tools or
  deny mutation tools; `permissionMode` alone may not make a worker stricter
  than an already permissive parent session.
- Use background, concurrency, worktree, model, or effort controls only when
  the current native Agent/Subagent interface actually exposes them.
- For concurrent mutation, require native worktree or equivalent filesystem
  isolation. Current Qoder documentation exposes `QODER_PLUGIN_ROOT`,
  `SessionStart`, and `SubagentStart`; keep the complete worker envelope anyway
  because Hooks are optional defense in depth and may be disabled by trust or
  organization policy.
- Do not add static plugin agents merely to make implicit delegation more
  likely. The gate must remain default-off.

### OpenCode and unknown hosts

Stay single-agent unless the current runtime exposes and verifies a native
delegation mechanism with equivalent bounded-task and isolation controls. Do
not claim an adapter based only on another host's behavior.

## Model and effort policy

Default to inheritance. Select a different supported setting only when the
role has a concrete quality/cost reason and the proposal tells the user.

| Worker role | Preferred class | Preferred effort |
| --- | --- | --- |
| Search, inventory, logs, or bounded scout | Efficient host tier | Medium |
| Bounded independent implementation | Balanced host tier or inherit | Medium; High for connected risk |
| Architecture, security, migration, adversarial review | Frontier/current coordinator tier | High or xhigh when supported |

Use Low only for mechanical enumeration with a deterministic output. Never
select maximum effort, Codex Ultra, Qoder Ultimate, Claude Agent Teams, or
Qoder Agent Teams automatically; an explicit proposal and user authorization
are required even when the host offers them.
Provider model names and aliases change, so resolve them from the current host
instead of hard-coding one into the protocol. If the requested pair is absent,
inherit and report the fallback; do not cycle through models.

## Worker envelope

Every worker receives all of these facts in its launch task, regardless of
Hook support:

- canonical project/worktree root;
- parent workflow ID and observed revision, when tracked;
- approved plan or shape path and exact Outcome IDs in scope;
- one exact task, allowed files/actions, and required evidence;
- isolation method and any resource it alone owns;
- forbidden actions: parent-ledger writes, scope/Contract/Plan changes, nested
  delegation, commit, push, PR, publish, deploy, destructive work, secrets,
  permission changes, or other external writes;
- stop condition and report format: findings or changed paths, commands, exit
  status, observed signal, assumptions, and blockers.

Workers are leaf agents. They do not reinterpret the product outcome, widen
their file set, integrate other workers, or make completion claims.

## Limits, integration, and evidence

- Default to two concurrent workers. Allow up to three only for independent,
  read-only multi-perspective review. Delegation depth is one.
- Concurrent implementation uses separate worktrees or equivalent native
  isolation. Otherwise keep implementation single-agent and use workers only
  for read-only investigation or review.
- The root coordinator is the sole ledger writer, integrator, finding
  adjudicator, and acceptance owner. Checkpoint immediately before launch and
  after integrated results.
- Workers run focused checks for their bounded outputs. The coordinator
  inspects the combined diff and runs affected integration or broad shared
  suites once after integration; workers do not duplicate them.
- Treat worker summaries as navigation, not proof. Verify the integrated tree
  freshly before a completion, release, or fidelity claim.

For representative evaluation, record only data the host exposes: elapsed
time, accepted findings or patches, conflicts, duplicate work, rework, and
token/cost when available, plus final quality evidence. Do not add telemetry.
Require at least three comparable runs for a host/role combination before
claiming a reliable speed, cost, or quality advantage.
