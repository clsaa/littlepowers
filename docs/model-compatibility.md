# Model compatibility

**Reviewed:** 2026-07-17

**Release:** 0.4.0-alpha.1

Littlepowers does not choose a model, reasoning effort, or context window. Planning depth follows task risk and unresolved decisions.

This report covers model and host compatibility, not simultaneous orchestration with another workflow plugin. Littlepowers and Superpowers can expose namespaced skills, but enabling both as default routers may duplicate or contradict process instructions; evaluate one default router at a time.

## Compatibility summary

| Host and model | Status | Evidence | Main caveat |
| --- | --- | --- | --- |
| Codex, GPT-5.6 Sol, xhigh | Prerelease evaluation passed | Independent routing evaluation passed scenarios 1 through 9 after two specification corrections | One evaluation campaign is functional evidence, not a reliability claim |
| Codex, GPT-5.6 Sol, max | Prerelease adversarial review passed | Independent review found no remaining P0/P1 issue; 43 state, Hook, and manifest tests passed | Max may add latency, token use, and overplanning; use only when measured value justifies it |
| Codex, GPT-5.6 Sol, Ultra | Prerelease coordination evaluation passed, with a protocol caveat | A root coordinator and two workers preserved sole-writer ownership; a stale write conflicted instead of overwriting | Worker read-only ownership is a protocol, not OS access control |
| Claude Code, Fable 5 | Compatible by design; authenticated flow not yet recorded | Official Fable and Claude Code review, Claude Code 2.1.207 strict plugin validation | Fable prefers outcome-focused prompts and may fall back to Opus 4.8 for classified domains |
| Claude Code, Opus 4.8 | Compatible by design; authenticated flow not yet recorded | Official Opus and Claude Code review, Claude Code 2.1.207 strict plugin validation | High effort is the documented default; xhigh/max can overthink fixed ceremony |

“Compatible by design” means the plugin uses supported hooks and skills and does not set conflicting model parameters. It does not mean every scenario has passed an authenticated live-model evaluation.

## Engineering-discipline compatibility

v0.4 adds native skills for systematic debugging, verification, and review. They do not select a model, effort, context window, reviewer, or subagent count. They request observable summaries—reproducer results, commands, exit status, verdicts, and file locations—not hidden reasoning or chain-of-thought.

The disciplines are conditional rather than a second mandatory router: debugging applies to unexpected behavior, review applies at requested or material boundaries, and verification applies before a success claim. Tiny isolated changes can use focused self-review and direct evidence without a separate reviewer or full suite. This limits repeated ceremony at xhigh/max/high effort while keeping an explicit evidence gate where mistakes are costly.

Littlepowers does not call Superpowers or depend on its runtime. Both can expose namespaced skills, but making both default workflow authorities can still create process-level duplication even though neither creates a model-parameter conflict.

The dated evidence and its limits are recorded in [the v0.3 alpha evaluation report](../evals/results/2026-07-17-v0.3-alpha.1.md). The project requires three runs per configuration before making a reliability claim; this prerelease reports only the narrower outcomes actually observed.

## GPT-5.6

OpenAI's current model guidance lists `gpt-5.6-sol` as the frontier model and supports API reasoning efforts `none`, `low`, `medium`, `high`, `xhigh`, and `max`. It recommends reserving max for the hardest quality-first work and comparing it with xhigh.

Codex Ultra is a product-level mode that combines deep reasoning with proactive subagent delegation. It is not a valid OpenAI Responses API `reasoning.effort` value. Littlepowers does not write `reasoning.effort` or select Ultra.

GPT-5.6 guidance also recommends lean prompts, single-stated rules, outcome-focused autonomy boundaries, and representative evaluation. v0.4 responds by:

- keeping static behavior in the router instead of Hook context;
- reducing repeated policy in phase skills;
- routing direct, compact, or full work by risk;
- keeping the host in charge of delegation;
- using factual bounded recovery snapshots;
- selecting debugging and review only at applicable boundaries;
- tying completion claims to observable evidence without requesting private reasoning.

Official sources: [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6), [Codex models](https://developers.openai.com/codex/models), and [Codex hooks](https://developers.openai.com/codex/hooks).

## Claude Fable 5 and Opus 4.8

Claude Code exposes `fable` for Claude Fable 5 and `opus` for the current Opus model. Claude Code 2.1.207 or later satisfies the documented minimum versions for Fable 5 and Opus 4.8.

Fable 5 is designed for long autonomous work. Anthropic recommends describing outcomes rather than prescribing every step and says repeated verification reminders are usually unnecessary. Opus 4.8 supports higher effort for difficult or asynchronous work, but max should be evaluated for diminishing returns.

Littlepowers does not request hidden reasoning or chain-of-thought. Artifacts record a reviewable decision rationale. The plugin does not override effort or model aliases. Its verification reminder appears at a completion boundary instead of repeating the whole workflow on every prompt, and proportional scope avoids forcing broad checks or separate review onto tiny work. Fable safety classifiers may route some cybersecurity, biology, chemistry, or distillation requests to Opus 4.8; that host behavior does not change the ledger schema.

Official sources: [Claude Code model configuration](https://code.claude.com/docs/en/model-config), [Claude Fable 5](https://www.anthropic.com/news/claude-fable-5-mythos-5), [Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8), and [Claude Code hooks](https://code.claude.com/docs/en/hooks).

## Validation levels

Release reports should distinguish:

1. manifest and static skill validation;
2. Hook delivery without model authentication;
3. model routing evaluation;
4. full authenticated implementation and interruption evaluation.

The prerelease does not claim level 4 for Fable 5 or Opus 4.8, and the v0.3 model results are not silently promoted into v0.4 reliability claims. Add dated results rather than turning a model snapshot into a permanent guarantee.
