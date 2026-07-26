# Expert reviews

## Outcome Lock 1.2 follow-up

**Review date:** 2026-07-26

The architecture, OpenAI/Codex, Anthropic/Claude Code, daily AI-coding, and
open-source perspectives rechecked the observed failure: an implementation can
follow a narrow child plan while silently abandoning an earlier approved PRD or
interaction baseline.

### Consensus

| Finding | Candidate response | Remaining boundary |
| --- | --- | --- |
| Prompt-only parent inheritance cannot prevent a narrower plan | Schema 3 binds explicit parent sources and a reviewed `OUT-###` Contract; execution requires complete Plan Map coverage | A Contract that semantically omitted a free-form requirement can still be wrong; the existing route review gate must catch it |
| Old open workflows can keep following pre-1.2 plans | Active/paused legacy ledgers become `reconcile_required` before executable progress | An already-open host task cannot hot-load a replaced plugin; update and start a new task/session |
| “No scope delta” was not machine-checkable | Non-active dispositions contradict `none`; non-empty delta requires a distinct approval audit claim | The claim records coordinator-observed approval; it is not user authentication |
| UI or host fidelity evidence was unstructured | Required baseline provenance and stable Fidelity rows independently gate approved-outcome fidelity | Missing external tools or evidence stays `blocked`, never silently becomes `not_applicable` |
| Review wording mixed two and three verdicts | Work-unit compliance, approved-outcome fidelity, and code quality are independently persisted and required at completion | A passing work unit still does not imply product fidelity |
| “No slices” encouraged oversized batches | Public and skill wording now requires one continuous implementation stream with independently reversible rollback units, checkpoints, and small commits | These boundaries control recovery and review; none is a staged product delivery |
| More ceremony could slow high-effort models | Gates are standard-library parsing/hashing at explicit lifecycle boundaries only; Hooks render stored summaries | No model call or reasoning conflict is added, but local I/O is not literally zero |
| Static wording tests were insufficient | Behavioral suites exercise malformed records, migration, drift, incomplete coverage, fidelity, atomicity, and completion aggregation | Model reliability still requires separate authenticated repeated runs |

### Compatibility conclusion

Outcome Lock does not select or override GPT-5.6 Sol xhigh/max/Ultra, Fable 5,
Opus 4.8, host delegation, or reasoning effort. It adds no second planner,
review agent, background scan, or automatic test run. The candidate can
therefore claim model-parameter compatibility by construction, but not that
any particular model will always form a semantically complete Contract.

Codex, Claude Code, Qoder, and OpenCode consume the same state CLI and skill
files. Host adapters remain discovery and read-only recovery surfaces. Exact
candidate validation and any unavailable or unauthenticated host/model run are
reported separately rather than promoted into a compatibility guarantee.

## v0.3 expert review

**Review date:** 2026-07-17

**Reviewed revision:** `155c782b22497ff70908f9ef3118158462300010`

Five independent reviewers assessed the v0.2 implementation before v0.3 work began.

## Review roles

- software architect: state integrity, security boundaries, concurrency, and migration;
- OpenAI and Codex specialist: GPT-5.6 Sol, xhigh, max, Ultra, hooks, skills, and prompt guidance;
- Anthropic and Claude Code specialist: Fable 5, Opus 4.8, effort, hooks, plugin paths, and dynamic workflows;
- daily AI-coding practitioner: installation, interruption, resume, side requests, state management, and uninstallation;
- open-source maintainer: positioning, trust, onboarding, releases, community health, and discoverability.

## Consensus findings and v0.3 response

| Finding | Severity | v0.3 response |
| --- | --- | --- |
| SessionStart alone cannot cover ordinary follow-ups | P0/P1 | Add `UserPromptSubmit`; calibrate claims and retain Codex Queue guidance |
| Linked `.littlepowers` could redirect writes outside the workspace | P0 | Reject symlink and reparse-point stores and files |
| Atomic replace did not prevent concurrent lost updates | P1 | Add workflow UUID, revision compare-and-swap, and cross-process lock |
| Artifact paths could escape, block, race, or carry prompt-like text | P1 | Add a snapshot-bound reader for bounded untrusted Markdown and reject links and special files |
| Hook context repeated imperative policy | P1 | Inject bounded factual data; keep behavior in the router |
| Four documents were required too broadly | P2 | Add direct tracking and one-file compact shaping; reserve full shaping for risk |
| Ultra and dynamic workflows had no ownership rule | P1 | Make the root coordinator the only ledger writer and workers read-only |
| `/goal` created a second objective source | P2 | Remove the recommendation; keep Queue and side-chat guidance |
| Repository claims exceeded test evidence | P1/P2 | Add capability, security, and dated compatibility reports plus OS CI |
| Public contribution and reporting paths were missing | P1 | Add community files, issue forms, PR checklist, changelog, and security policy |

## Compatibility conclusion

There is no model-parameter conflict with GPT-5.6 Sol xhigh/max, Fable 5, or Opus 4.8. The v0.2 structural conflict was multi-agent writes to one unrevisioned ledger. v0.3 addresses lost updates and defines coordinator ownership.

The independent Codex review then forward-tested the revised behavior:

- xhigh passed routing scenarios 1 through 9 after the pause/resume wording was made explicit;
- max completed the adversarial security review with no remaining P0/P1 issue and 43 tests passing;
- Ultra preserved root-only ledger writes with two workers and rejected a stale coordinator update.

These are prerelease functional results, not a reliability claim across repeated runs. Ultra's ownership rule remains cooperative rather than OS-enforced. OpenAI API users must not set `reasoning.effort=ultra`; Ultra is a Codex orchestration mode. Claude Fable 5 and Opus 4.8 remain “compatible by design” until an authenticated end-to-end model run is recorded. See the [dated evaluation report](../evals/results/2026-07-17-v0.3-alpha.1.md).

## Naming conclusion

The open-source reviewer recommended **Planthread** for a public long-term brand because it names the differentiating capability and avoids perceived affiliation with Superpowers. Littlepowers remains the v0.3 name because renaming the repository and plugin is an owner decision. Repository visibility also remains unchanged pending explicit owner approval.
