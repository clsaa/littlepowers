# Model compatibility

**Reviewed:** 2026-09-20

**Release:** 1.4.1

**Refresh trigger:** Recheck before release when any supported host version,
model alias, worker schema, or Hook contract changes; otherwise recheck after
30 days.

Littlepowers does not choose a model, reasoning effort, context window, or
worker on the ordinary path. Planning depth follows risk and unresolved
decisions. Only after the opt-in Delegation Gate finds a high-benefit candidate
does the coordinator inspect the current native interface, validate one Host
Capability Snapshot, and present the exact work unit for authorization.
Inheritance remains the default.

This report covers model and host compatibility, not simultaneous
orchestration with another workflow plugin. Littlepowers and Superpowers can
expose namespaced skills, but enabling both as default routers may duplicate or
contradict process instructions; evaluate one default router at a time.

## Dated compatibility boundary

| Host | Local binary inspected | Registry target checked | Current model/capability evidence | Certification boundary |
| --- | --- | --- | --- | --- |
| Codex | 0.147.0 | 0.155.1 | Official GPT-6 Astra and GPT-5.6 family guidance; current native subagent schema documentation | Historical GPT-5.6 routing/coordination evidence exists; no authenticated 0.155.1 + Astra implementation run is claimed |
| Claude Code | 2.1.227 | 2.1.278 | Fable 5.1/Fable 5, Opus 5, Sonnet 5 and Opus 4.8; fresh subagents, conversation forks, and Agent Teams | Current behavior is documentation/structural evidence; the earlier authenticated probe stopped before model execution because local OAuth had expired |
| Qoder CLI / IDE | 1.1.19 | 1.1.58 | The local account's current server list returned Auto, Ultimate, Performance, Efficient and rolling Qwen, Kimi, GLM, DeepSeek, and MiniMax entries; current Hook/Subagent/Agent Teams documentation | Earlier Qoder Hook routing passed on 1.1.18; no authenticated delegated implementation run on 1.1.58 is claimed |
| OpenCode | 1.18.4 historical boundary | Not refreshed in this work unit | Existing skill/state CLI and message-transform integration | Remains structurally supported and single-agent until an equivalent native worker boundary is verified |

Registry targets are observations from 2026-09-20, not minimum-version
guarantees. Model availability is account, provider, policy, and region
dependent. The active host's model picker or list command and callable worker
schema remain authoritative.

“Compatible by design” means the plugin uses supported skills, Hooks, and
native boundaries without writing model configuration. It does not mean every
model/effort combination has passed an authenticated end-to-end run.

## Current host implications

The subsequent [1.4.0 local Codex report](../evals/results/2026-09-20-v1.4.0-codex-live.md)
records authenticated Sol/max tiny-change and interruption/recovery runs,
including local CLI 0.155.1 cases. A real two-worker run exposed false
leaf-enforcement labeling, which was repaired and retested. These source-skill
runs do not certify Astra, a live cache upgrade, or delegated implementation.

### Codex

Codex now documents built-in `default`, `worker`, and `explorer` agent roles,
project/user custom agents, model and reasoning defaults, and per-agent sandbox,
MCP, and skill configuration. Explicit launch settings, `[agents]` defaults,
parent inheritance, and an applicable custom definition can participate in the
effective configuration. Littlepowers therefore records what the current spawn
interface resolves instead of encoding permanent model IDs or assuming that a
requested override won.

GPT-6 Astra is the current flagship and supports `low`, `medium`, `high`,
`xhigh`, and `max` reasoning effort. Official guidance says it maintains long
task coherence better, supports mid-turn steering, can be more sensitive to
conflicting skill/`AGENTS.md` instructions, may delegate less unless the harness
states when to do so, and may test too broadly for small tasks. Littlepowers'
progressive disclosure, single delegation decision, and impact-scaled testing
remain appropriate: do not duplicate the delegation policy in every skill and
do not repeat or broaden passing tests without a new risk signal.

Official sources: [GPT-6 Astra model guidance](https://developers.openai.com/api/docs/guides/latest-model),
[GPT-6 Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra),
and [Codex subagents](https://developers.openai.com/zh-Hans/docs/agent-configuration/subagents).

### Claude Code

Current Claude Code separates three materially different mechanisms:

- a normal subagent starts with a fresh context and its agent definition;
- a conversation fork inherits the parent history, prompt, tools, model, and
  prompt cache, making it useful only when rebuilding context would dominate;
- Agent Teams provide peer communication but remain experimental and
  session-scoped. In-process teammates do not survive session resume, task
  status can lag, and nested teams are unavailable.

Current agent definitions support model, effort, background execution,
`omitClaudeMd`, tool restrictions, and worktree isolation. Background workers
surface permission requests in the main session. Plugin-provided agent
definitions do not retain every permission, Hook, or MCP field, so
Littlepowers does not ship static agents or treat frontmatter as stronger than
the effective native boundary.

The `fable` alias resolves to Fable 5.1 on current Anthropic API paths, with a
documented Claude-apps-gateway exception that still resolves to Fable 5. Opus 5
and Sonnet 5 are current choices; Fable 5.1, Fable 5, Opus 5, Sonnet 5, and
Opus 4.8 support `low` through `max` when the provider and organization expose
them. Aliases evolve, so a version-specific evaluation pins a full model name
and the ordinary path continues to inherit.

Official sources: [Claude Code model configuration](https://code.claude.com/docs/en/model-config),
[Claude Code subagents](https://code.claude.com/docs/en/sub-agents), and
[Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams).

### Qoder

Qoder's catalog is server-driven. `/model` or `--list-models` is the source of
truth; Littlepowers uses host-relative Efficient, Performance, Ultimate, or
Auto/inherited tiers and never bakes the rolling provider list into the
protocol.

An ordinary Subagent has a fresh bounded context. `/subtask` is the
inherited-session-context option for a background side task. Agent Teams is a
beta, opt-in, session-only peer mechanism. Qoder Subagents expose model, effort,
background execution, tool allow/deny lists, maximum turns, timeout, worktree
isolation, and permission mode. Because a permissive parent can prevent a
Subagent from becoming stricter through `permissionMode`, Littlepowers enforces
read-only work with a tool boundary and leaf depth with an `Agent` deny rule.

Current Qoder documentation also defines `QODER_PLUGIN_ROOT` for plugin Hook
processes and lists `SessionStart`, `UserPromptSubmit`, and `SubagentStart`.
The complete worker envelope remains mandatory because Hook trust or policy may
disable delivery; Hook context is defense in depth, not launch authority.

Official sources: [Qoder models](https://docs.qoder.com/cli/model),
[Qoder Subagents](https://docs.qoder.com/cli/subagent),
[Qoder Agent Teams](https://docs.qoder.com/cli/agent-teams), and
[Qoder Hooks](https://docs.qoder.com/cli/hooks).

## Engineering-discipline and performance compatibility

The debugging, verification, and review skills request observable summaries—
reproducer results, commands, exit status, verdicts, and file locations—not
hidden reasoning or chain-of-thought. They do not select a model, effort,
context window, reviewer, or worker count.

Ordinary routing does not read the detailed delegation reference or run the
capability validator. Hooks read only the bounded ledger summary. Outcome Lock
and Review Lease parse bounded Markdown/JSON and hash explicitly named files at
lifecycle boundaries; they do not scan the repository or call a model. The
Host Capability Snapshot helper accepts explicit command-line facts only and
does not inspect host configuration, environment, project files, ledger,
transcript, or network.

This keeps the ordinary path free of extra Agent/model calls, background work,
capability probes, effort overrides, or broad tests. Planning gates add a small
number of local tool/continuation turns. An authorized delegated run
intentionally adds worker tokens, latency, and integration work and is proposed
only when the measured critical-path or context-isolation benefit is likely to
be higher.

Testing stays proportional. Tiny isolated changes get focused checks;
connected behavior gets affected-boundary checks; broad shared or release
boundaries run the relevant broad suite once after integration. This matches
current model guidance and prevents a capable high-effort model from converting
every small edit into repeated full-suite work.

Littlepowers does not call Superpowers or depend on its runtime. Both can expose
namespaced skills, but making both default workflow authorities can still
create process-level duplication even though neither creates a model-parameter
conflict.

## Opt-in delegated model controls

Selection remains host-relative:

- search, inventory, logs, and bounded scouting prefer an efficient current
  tier at medium effort;
- bounded independent implementation prefers a balanced current tier or
  inheritance at medium/high effort;
- architecture, security, migration, and adversarial review prefer the current
  frontier/coordinator tier at high or xhigh when supported.

Every proposal includes a validated Host Capability Snapshot. Maximum effort,
Codex Ultra, Qoder Ultimate, Claude Agent Teams, and Qoder Agent Teams are never
automatic. Unsupported settings fall back to inheritance without cycling model
aliases. The user authorizes one exact work unit; model selection never expands
commit, push, PR, publish, deployment, destructive, secret, permission, or
external-write authority.

Historical routing and coordination evidence remains in
[the v0.3 alpha report](../evals/results/2026-07-17-v0.3-alpha.1.md),
[the v0.4 discipline report](../evals/results/2026-07-17-v0.4-alpha.1.md), and
[the 1.4.0-alpha.1 delegation report](../evals/results/2026-08-21-v1.4.0-alpha.1.md).
Those results are not silently promoted to current-host certification.

## Validation levels

Release evidence must distinguish:

1. manifest, policy-validator, and static skill validation;
2. Hook delivery without model authentication;
3. authenticated model routing response;
4. authenticated implementation, interruption, and delegated integration flow.

Before a stable release claims a current-host quality, cost, or speed benefit,
run at least three comparable cases per host/role combination and record only
observable data: elapsed time, accepted findings or patches, conflicts,
duplicate work, rework, exposed token/cost data, and final quality evidence.
Do not record chain-of-thought. Until those runs exist, report the adapter as
documentation/structurally compatible rather than orchestration-certified.
