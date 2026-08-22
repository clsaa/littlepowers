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
- Host mechanism: <current callable native mechanism>
- Model/effort: <inherit or supported role-specific choice>
- Isolation: <read-only or separate worktrees/files/resources>
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

## Host adapters

Use only controls callable in the current runtime. Documentation about a host
capability is not proof that the current task exposes it.

### Codex

- Use the current Codex native subagent/spawn tool. Do not create or fork
  user-visible Codex tasks as workers and do not invoke a nested `codex` CLI.
- Read the actual tool schema before selecting a model or reasoning effort.
  Prefer inherited settings. Some full-history or host-managed contexts require
  inheritance; accept that boundary or use a supported bounded-context mode
  only when the worker has every required input.
- Do not select Ultra automatically. Some Codex surfaces expose `ultra` as a
  host-native worker reasoning value even though public API effort values may
  differ. Use it only when the actual spawn schema supports it, the proposal
  names its cost/latency tradeoff, and the user explicitly authorizes it;
  otherwise inherit.

### Claude Code

- Prefer ordinary native subagents. Use Agent Teams only after a separate
  explicit proposal when workers need peer-to-peer communication; it is
  experimental and materially more expensive than ordinary subagents.
- Pass a supported model alias/full identifier and effort only through the
  current native Agent interface or an already approved project agent
  definition. Never edit user configuration, environment variables, allowlists,
  or organization policy to make a selection work.
- Host aliases, environment rules, provider routing, and allowlists may override
  a request. Report the effective limitation and inherit rather than retrying.

### Qoder

- Use the current native Agent/Subagent interface. Use its background,
  concurrency, worktree, model, or effort controls only when the current
  surface actually exposes them.
- For concurrent mutation, require native worktree or equivalent filesystem
  isolation. Qoder IDE may omit `SubagentStart`; therefore every worker prompt
  carries the full ownership envelope even when a Hook is configured.
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
select maximum effort, Codex Ultra, or Claude Agent Teams automatically; an
explicit proposal and user authorization are required even when the host
offers them.
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
