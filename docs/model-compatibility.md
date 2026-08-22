# Model compatibility

**Reviewed:** 2026-08-21

**Release:** 1.4.0-alpha.1 candidate

Littlepowers does not choose a model, reasoning effort, context window, or
worker on the ordinary path. Planning depth follows task risk and unresolved
decisions. Only after the opt-in Delegation Gate and exact user authorization
may the coordinator pass a role-appropriate model/effort choice through a
callable native worker interface; inheritance remains the default.

This report covers model and host compatibility, not simultaneous orchestration with another workflow plugin. Littlepowers and Superpowers can expose namespaced skills, but enabling both as default routers may duplicate or contradict process instructions; evaluate one default router at a time.

## Compatibility summary

| Host and model | Status | Evidence | Main caveat |
| --- | --- | --- | --- |
| Codex, GPT-5.6 Sol, xhigh | Earlier prerelease routing evaluation passed; v1.3.1 level-3 probe used `low`, not xhigh | Independent routing evaluation passed scenarios 1 through 9; Codex 0.147.0 delivered the current Hook to an authenticated `gpt-5.6-sol` probe and the model returned the exact workflow ID | The current probe proves delivery/routing, not a full implementation flow or xhigh reliability |
| Codex, GPT-5.6 Sol, max | Prerelease adversarial review passed | Independent review found no remaining P0/P1 issue; 43 state, Hook, and manifest tests passed | Max may add latency, token use, and overplanning; use only when measured value justifies it |
| Codex, GPT-5.6 Sol, Ultra | Prerelease coordination evaluation passed, with a protocol caveat | A root coordinator and two workers preserved sole-writer ownership; a stale write conflicted instead of overwriting | Worker read-only ownership is a protocol, not OS access control |
| Claude Code, Fable 5 | Compatible by design; current live probe blocked before model execution | Claude Code 2.1.227 is the current local validation host; the earlier 2.1.226 source-plugin probe reached the local host but expired OAuth could not refresh, returned cost 0, and provided no model evidence | Reauthenticate before claiming authenticated routing, delegated selection, or implementation behavior; Fable prefers outcome-focused prompts |
| Claude Code, Opus 4.8 | Compatible by design; authenticated v1.4 flow not yet recorded | Existing host/model review plus strict plugin validation; fake-host runner tests prove argv/control behavior only | Higher effort can overthink fixed ceremony; the ordinary path does not select it |
| Qoder CLI / Qoder IDE, any model | Qoder CLI level-3 Hook routing probe passed on the prior release; IDE remains structurally validated only | Qoder CLI 1.1.19 is the current local validation host; the earlier 1.1.18 probe loaded the source plugin in an isolated project-settings run and returned the exact temporary workflow ID | No authenticated delegated-model flow is claimed; the IDE fires only a subset of events and does not document `QODER_PLUGIN_ROOT` injection |
| OpenCode, any model | Loads the same skills and state CLI; authenticated flow not yet recorded | Source-level verification of the config and message-transform hooks against OpenCode v1.18.4, plus stubbed plugin behavior tests | Relies on two hooks OpenCode's docs do not document; no live end-to-end run recorded |

“Compatible by design” means the plugin uses supported hooks and skills and does not set conflicting model parameters. It does not mean every scenario has passed an authenticated live-model evaluation.

The 2026-08-21 local candidate boundary uses Codex 0.147.0, Claude Code
2.1.227, and Qoder CLI 1.1.19. The prior 1.3.1 package passed all three host
validators; an authenticated Qoder CLI probe returned the exact Hook workflow
ID, while the Claude model probe was blocked by expired local OAuth. Candidate
validation is reported separately rather than silently promoting prior results.
Codex 0.147.0 also enforces 128 characters per starter
prompt; 1.3.1 shortens all three and adds a regression for that host limit.
These are dated compatibility observations, not permanent minimum-version
guarantees.

## Engineering-discipline compatibility

v0.4 adds native skills for systematic debugging, verification, and review.
Those skills do not by themselves select a model, effort, context window,
reviewer, or subagent count. They request observable summaries—reproducer
results, commands, exit status, verdicts, and file locations—not hidden
reasoning or chain-of-thought. The 1.4 Delegation Gate is a separate opt-in
coordinator decision around those skills, not a second mandatory router.

The disciplines are conditional rather than a second mandatory router: debugging applies to unexpected behavior, review applies at requested or material boundaries, and verification applies before a success claim. Tiny isolated changes can use focused self-review and direct evidence without a separate reviewer or full suite. This limits repeated ceremony at xhigh/max/high effort while keeping an explicit evidence gate where mistakes are costly.

The lean route reduces fixed ceremony: a small bounded change with one meaningful decision goes from brainstorm directly to plan, skipping separate specification and design artifacts. Outcome Lock protocol 1.3 moves declared scope integrity from prompt-only wording into the local state boundary: stable Outcome IDs, explicit source digests, coverage, fidelity rows, and completion invariants are checked without another reviewer, model call, hidden chain-of-thought request, repository scan, or automatic test run. Review Lease avoids a redundant human stop when the latest request already supplies a fixed implementation mandate or explicit unattended authorization. Implementation remains one continuous stream; tasks and rollback units do not become independently accepted product slices.

The additional runtime cost occurs only at explicit lifecycle boundaries.
Ordinary prompt and Hook paths read the bounded ledger summary and never open
parent or evidence files. Bind, park/resolve, transition, resume/readiness, verification, and
completion parse bounded Markdown/JSON and hash only explicitly named files
(16 MiB per file, 64 MiB total). Cost is independent of repository size.
The ordinary path neither requests hidden reasoning nor starts an independent
model call, so it has no model-parameter conflict with GPT-5.6 Sol
xhigh/max/Ultra, Fable 5, or Opus 4.8. It adds small local I/O boundaries plus a
limited number of planning-gate tool/continuation turns, which can add
wall-clock time. An authorized delegated run intentionally adds worker token,
latency, and integration cost; Littlepowers recommends it only when the
expected critical-path or context-isolation gain is higher.
The 1.3.1 root-affinity guard adds one local `.git` marker `lstat` before Hook
ledger loading and no Git process, repository scan, prompt read, model turn, or
network call.

Ordinary routes do not run a scheduler. Only an explicitly `windowed` Review
Lease may arm one host callback: Codex only when a same-task one-shot scheduling
capability is actually callable, or Claude Code through the optional exact-
session runner. The callback resumes the configured host/model once; it neither
selects another model nor adds a reviewer. Qoder and OpenCode continue manually.

Claude dynamic workflows need a stricter authority boundary because the host
workflow script can own an execution plan and may launch additional workflows.
The approved Littlepowers plan remains the sole product-scope and acceptance
authority; the host script is an execution adapter derived from it. Checkpoint
before launch and after integration, and keep background workers ledger-read-
only. This is protocol-compatible, but no authenticated representative dynamic-
workflow run has certified orchestration behavior. Host workflows can add their
own planning, token, and wall-clock cost. See [Claude Code dynamic
workflows](https://code.claude.com/docs/en/workflows).

Handoff and review-evidence additions are dormant commands, not a second execution loop. Ordinary routing and hooks do not scan sibling worktrees, hash review candidates, create reviewers, select models, add a model turn, or add a test run. A broad uncommitted review opts into one bounded snapshot before review and one comparison before verdict acceptance; an oversized review may be partitioned, but one acceptance owner aggregates shared-boundary evidence once.

Littlepowers does not call Superpowers or depend on its runtime. Both can expose namespaced skills, but making both default workflow authorities can still create process-level duplication even though neither creates a model-parameter conflict.

## Opt-in delegated model controls

The Delegation Gate is default-off and evaluated at most once after a stable
plan, after a reproduced bug yields independent evidence paths, or before a
material multi-perspective review. It vetoes unsettled, sequential, same-file,
shared-resource, tiny, destructive, or external-state work. A qualifying
proposal names roles, current native mechanism, model/effort policy, isolation,
benefit, risk, and single-agent fallback; no worker starts before exact
work-unit authorization.

Selection is host-relative rather than tied to permanent model IDs:

- search, inventory, and log scouts prefer an efficient tier at medium effort;
- bounded independent implementation prefers a balanced tier or inheritance at
  medium/high effort;
- architecture, security, migration, and adversarial review prefer the current
  frontier/coordinator tier at high or xhigh when supported.

Maximum effort, Codex Ultra, and Claude Agent Teams are never automatic.
Unsupported pairs inherit without retry loops. Codex uses only its current
native spawn schema and never user-visible tasks or nested CLIs. Claude uses
ordinary subagents first; Agent Teams requires a separate explicit decision
because it is experimental and materially more expensive. Qoder uses only the
current native Agent/Subagent controls and carries the full task envelope even
when the IDE omits `SubagentStart`. OpenCode stays single-agent until an
equivalent native boundary is verified.

Host delegation sources: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents),
[Claude Code agent teams](https://code.claude.com/docs/en/agent-teams), and
[Qoder CLI subagents](https://docs.qoder.com/cli/subagent).

Historical routing and coordination evidence is recorded in [the v0.3 alpha evaluation report](../evals/results/2026-07-17-v0.3-alpha.1.md). The three v0.4 discipline checks and their limits are recorded separately in [the v0.4 alpha evaluation report](../evals/results/2026-07-17-v0.4-alpha.1.md), while [the 2026-07-18 static/runtime report](../evals/results/2026-07-18-lightweight-handoff-review-evidence.md) covers explicit handoff, snapshot timing, Hook cost, and model non-selection. The project requires three runs per configuration before making a reliability claim; this release reports only the narrower outcomes actually observed.

The current candidate evidence is in [the 1.4.0-alpha.1 delegation verification
report](../evals/results/2026-08-21-v1.4.0-alpha.1.md). It separates fresh
static/package validation from the prior 1.3.1 Codex/Qoder routing probes and
authentication-blocked Claude probe.

## GPT-5.6

OpenAI's current model guidance lists `gpt-5.6-sol` as the frontier model and supports API reasoning efforts `none`, `low`, `medium`, `high`, `xhigh`, and `max`. It recommends reserving max for the hardest quality-first work and comparing it with xhigh.

Codex Ultra is a product-level mode that adds automatic subagent delegation to
the highest Codex reasoning choice. It is not a public Responses API
`reasoning.effort` value: GPT-5.6's API efforts currently stop at `max`.
Littlepowers does not write model configuration, change the coordinator's
`reasoning.effort`, or select Ultra. Codex's model picker/configuration remains
the authority for Sol and xhigh/max, while the host remains the authority for
Ultra delegation. A current Codex native spawn tool may still expose `ultra` as
a host-specific worker reasoning value. After exact authorization, the
coordinator may pass one value that the actual spawn schema supports; Ultra or
maximum effort must be named in the proposal and explicitly authorized rather
than selected automatically. Otherwise the worker inherits.

GPT-5.6 guidance also recommends lean prompts, single-stated rules, outcome-focused autonomy boundaries, and representative evaluation. Littlepowers responds by:

- keeping static behavior in the router instead of Hook context;
- reducing repeated policy in phase skills;
- routing direct, lean-plan, compact, or full work by risk;
- keeping the host in charge of delegation;
- using factual bounded recovery snapshots;
- selecting debugging and review only at applicable boundaries;
- tying completion claims to observable evidence without requesting private reasoning.

Official sources: [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6), [Codex models](https://developers.openai.com/codex/models), and [Codex hooks](https://developers.openai.com/codex/hooks).

## Claude Fable 5 and Opus 4.8

Claude Code exposes `fable` for Claude Fable 5. The evolving `opus` alias maps
to Opus 5 on current Anthropic API releases, so an Opus 4.8 evaluation must use
its full model name or an explicit provider pin rather than assuming the alias.
The documented minimums are Claude Code 2.1.170 for Fable 5 and 2.1.154 for
Opus 4.8; the local validation host is 2.1.227.

Fable 5 is designed for long autonomous work. Anthropic recommends describing outcomes rather than prescribing every step and says repeated verification reminders are usually unnecessary. Opus 4.8 supports higher effort for difficult or asynchronous work, but max should be evaluated for diminishing returns.

Littlepowers does not request hidden reasoning or chain-of-thought. Artifacts record a reviewable decision rationale. The ordinary path does not override effort or model aliases. An authorized native subagent may receive a supported model/effort selection, but environment, allowlist, provider, and organization rules remain authoritative and unsupported choices fall back to inheritance. Its verification reminder appears at a completion boundary instead of repeating the whole workflow on every prompt, and proportional scope avoids forcing broad checks or separate review onto tiny work. Current Claude Code can route Fable 5 cybersecurity flags to Opus 4.8 and biology flags to Opus 5; provider and organization settings can alter availability. That host behavior does not change the ledger schema.

Official sources: [Claude Code model configuration](https://code.claude.com/docs/en/model-config), [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams), [Claude Fable 5](https://www.anthropic.com/news/claude-fable-5-mythos-5), [Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8), and [Claude Code hooks](https://code.claude.com/docs/en/hooks).

## Validation levels

Release reports should distinguish:

1. manifest and static skill validation;
2. Hook delivery without model authentication;
3. model routing evaluation;
4. full authenticated implementation and interruption evaluation.

This candidate does not claim level 4 for Fable 5 or Opus 4.8, or a reliable
delegated speed/quality gain on any host. Earlier model results are not silently
promoted into 1.4 reliability claims. Passing
schema-4 protocol and fake-host runner tests is model-agnostic evidence; it is not proof that a
model always builds a semantically complete Contract from free-form sources.
Add dated results rather than turning a model snapshot into a permanent
guarantee.
