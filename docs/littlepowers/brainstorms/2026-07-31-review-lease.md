# Littlepowers v1.3 Review Lease brainstorm

Date: 2026-07-31

## Problem

Littlepowers 1.2 protects a reviewed outcome with deterministic Contract,
coverage, fidelity, drift, and completion gates. Its phase-review policy is
still binary, however: either stop for an explicit reply at every planned
boundary or receive one broad unattended authorization for the entire run.

Recent Codex traces expose three consequences:

- an explicit request to iterate and fix a bounded set of accepted issues still
  stopped after a Compact Shape and asked for a redundant approval reply;
- long-running work can remain parked at a useful design or plan while the user
  is away even when the user would have preferred a bounded review window;
- a timeout cannot be recovered safely because schema 3 records neither the
  review policy nor an artifact-bound deadline.

The requested outcome is `v1.3.0-alpha.1`: reduce unnecessary human
intervention, allow a durable stage artifact such as a design to wait for a
pre-authorized interval and then continue safely, and support both Codex and
Claude Code without turning Littlepowers into a competing orchestrator.

## Scope anchor

Highest-authority sources are the latest user request, the immediately preceding
approved review of recent Codex sessions, and the repository constraints in
`AGENTS.md`. Existing public and protocol baselines are `README.md`,
`skills/using-littlepowers/SKILL.md`, `scripts/littlepowers_state.py`,
`evals/scenarios.md`, and `docs/security-model.md`.

Inherited behavior that remains in the definition of done:

- Outcome Lock continues to reject drift, missing coverage, unapproved scope
  changes, incomplete fidelity, and false completion;
- non-empty scope delta never becomes approved through silence, a timer, an
  implementation request, or broad unattended wording;
- direct work stays cheap and proportional; no route gains mandatory agents,
  model selection, full-suite repetition, transcript parsing, telemetry, or a
  background scanner;
- hooks remain read-only, bounded, network-free, and silent without unfinished
  state;
- Codex, Claude Code, Qoder, and OpenCode keep one shared skill/state core;
- only the root coordinator writes the ledger, and optimistic revision checks
  continue to fail stale writers;
- implementation is one continuous approved outcome, while checkpoints and
  rollback units remain recovery mechanics rather than product slices.

No scope delta.

No visual or output-format baseline is required. Host CLI behavior is a
compatibility surface and will be validated against the locally installed
Codex/Claude Code commands and their official documentation.

## Options

### A. Prompt-only intent wording

Teach the router that “implement” or “fix” can cross a Compact/Lean review gate
and tell it to remember a timeout in prose.

This is the smallest change, but compaction, a new session, a stale artifact, or
another writer can erase or falsify the decision. It repeats the limitation that
Outcome Lock was created to remove.

### B. State-owned Review Lease with thin host adapters — selected

Add one bounded review-policy/gate record to a new state schema. Phase skills
park an exact artifact digest. The state CLI computes whether the gate is still
waiting or may advance and consumes it exactly once. Codex uses a same-task
scheduled callback when that native capability is callable. Claude Code uses a
small optional one-shot Python runner bound to an exact session ID and project
root. Qoder and OpenCode keep manual recovery until they expose an equivalent
safe scheduler, while sharing the same deterministic state.

This adds one state transition at a phase boundary and one model turn only when
an armed timeout expires. It adds no polling loop or daemon.

### C. Littlepowers-owned background orchestrator

Run a persistent service that watches ledgers, messages, repositories, and host
sessions and resumes work itself.

This could automate more cases, but it would require transcript/session access,
credentials, lifecycle management, network authority, and conflict handling. It
would make Littlepowers a second orchestrator and violate its lightweight and
privacy boundaries.

## Selected direction

Use option B with four persisted policies:

- `blocking`: current explicit-review behavior;
- `implementation_mandate`: a fixed, explicitly requested implementation may
  cross Lean or Compact gates immediately when there is no delta or unresolved
  material choice;
- `windowed`: park the artifact until a pre-authorized deadline, then allow one
  host callback to continue through the recorded boundary;
- `unattended`: current explicit end-to-end authorization, now represented in
  recoverable state.

The policy and one current gate live in schema 4 / protocol 1.3. A gate binds the
artifact key, normalized path, digest, open revision, open time, earliest resume
time, scope-delta claim, and unresolved-question count. The CLI provides pure
status evaluation plus CAS-protected policy, park, resolve, and cancel commands.

Timeout resolution is an audit claim rather than user authentication, matching
existing approval records. It succeeds only when the mode is `windowed`, the
deadline elapsed, the caller explicitly observed no later intervention, the
artifact digest and ledger revision still match, no unresolved question or
scope delta exists, and any already-bound Outcome Contract remains healthy.
Correction, cancellation, drift, artifact mutation, an unavailable scheduler,
or a concurrent ledger write leaves the workflow parked.

Codex automation remains host-owned. A phase skill asks for a one-shot callback
inside the same task only when the Scheduled Task capability is callable; it
never claims a timer was armed when the tool is absent. Claude Code may arm the
bundled one-shot runner with an exact session ID; at expiry the runner invokes
normal `claude -p --resume <session-id>` without changing permission mode or
passing a bypass flag. The resumed model must inspect the visible conversation,
call the deterministic gate, and stop if intervention or ambiguity exists.

## Measurable success

1. Schema 1, 2, and 3 ledgers migrate recoverably to schema 4; an older runtime
   fails closed on schema 4 and rollback instructions name the pre-schema4
   archive.
2. The four policy modes are exact, validated, and rendered in recovery context.
3. An implementation mandate can immediately consume an eligible Lean/Compact
   gate but cannot bypass Full-route material decisions, scope delta, drift, or
   unresolved questions.
4. A windowed gate is ineligible before its deadline, eligible afterward only
   with the no-intervention audit claim, and consumable exactly once.
5. Artifact mutation, stale revision, concurrent mutation, policy change,
   cancellation, contract drift, or proposed scope delta blocks automatic
   continuation without a partial ledger write.
6. Codex instructions use a same-task Scheduled Task only when callable and
   fail closed otherwise.
7. The Claude one-shot runner binds an exact root, workflow, gate revision, and
   session ID; it performs no polling, transcript read, permission bypass, or
   retrying model loop.
8. Hooks remain read-only and report only a compact stored gate summary.
9. Direct work pays no review-lease command, scheduler, file hash, or model-call
   cost.
10. All skill validators, state/hook tests, plugin validators, and four host
    package surfaces pass with version `1.3.0-alpha.1`.

## Assumptions

- The user’s “不需要问我” is explicit unattended authorization for this
  development workflow only; it is not permission to commit, push, publish, or
  install the candidate.
- Codex Scheduled Tasks remain the preferred Codex App adapter. Codex CLI and
  IDE sessions without that capability remain safely parked.
- Claude Code supplies or can obtain an exact session ID for the opt-in runner;
  directory-only `--continue` is not accepted because another session may share
  the directory.
- A sleeping one-shot process may be lost on reboot. The durable gate remains in
  the ledger and becomes eligible on the next normal resume; Littlepowers does
  not add a persistent daemon to recreate it.

## Open questions

None. The selected direction follows from the approved constraints and this
workflow is explicitly unattended.
