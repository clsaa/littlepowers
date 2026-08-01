# Littlepowers v1.3 Review Lease specification

Date: 2026-07-31
Candidate: `1.3.0-alpha.1`
State protocol: schema 4 / protocol 1.3

## Purpose

Littlepowers must preserve deliberate review while removing redundant approval
round trips. It must distinguish a request to implement an already fixed outcome
from a request to discuss or design, persist the chosen review policy, bind a
parked phase artifact to the ledger, and allow a pre-authorized timeout to resume
through a host-native callback without treating silence as an unscoped approval.

The complete outcome covers the shared state CLI and skills, recoverable schema
migration, read-only recovery context, Codex Scheduled Task behavior, a bounded
Claude Code one-shot adapter, Qoder/OpenCode compatibility, public documentation,
and release validation. These are one protocol outcome, not staged product
slices.

## Users and callers

- A user who wants strict review at every planned phase.
- A user who has already asked for a bounded accepted change to be implemented.
- A user who explicitly grants a design/plan review window and a fallback action.
- A user who explicitly authorizes unattended end-to-end execution.
- The root coordinator calling the shared Python state CLI.
- Codex App and Claude Code host adapters resuming the same task/session.
- Qoder and OpenCode sessions recovering the same stored state manually when no
  safe scheduler exists.

## Goals

1. Persist review intent and an exact current Review Gate independently of chat
   compaction.
2. Make timeout eligibility and one-time consumption deterministic at the state
   boundary.
3. Let common Lean/Compact implementation requests continue without a redundant
   confirmation.
4. Keep non-empty scope changes, unresolved decisions, stale artifacts, and
   changed contracts fail-closed.
5. Use host-native or opt-in one-shot continuation without polling, a daemon, or
   model/effort overrides.

## Non-goals

- Authenticating a human identity or parsing a transcript.
- Inferring whether free-form requirements were semantically complete.
- Running a persistent scheduler, repository watcher, or network service.
- Automatically approving external deployment, publishing, destructive action,
  secrets access, or any authority absent from the original request and host
  permission policy.
- Giving Qoder or OpenCode an undocumented background-resume mechanism.
- Creating reviewer agents, choosing models, or running a full test suite at
  every gate.

## Functional requirements

### OUT-001 — Exact persisted review policies

Every schema-4 ledger stores exactly one policy mode: `blocking`,
`implementation_mandate`, `windowed`, or `unattended`. It also stores the
authorized continuation boundary, policy timestamp, and a wait duration only
for `windowed`. Unknown fields, modes, boundaries, or contradictory values are
rejected.

Acceptance:

- New workflows default to `blocking` unless the coordinator records another
  mode from the latest request.
- `windowed` accepts 60 through 604800 seconds inclusive.
- Non-windowed modes reject a wait duration.
- A policy can be changed only by a workflow/revision-checked command and cannot
  be changed while a gate is open.

### OUT-002 — Review intent routing

The router maps intent as follows:

- “先讨论/先设计/等我确认” and equivalent wording selects `blocking`.
- A request to implement, fix, or iterate a fixed bounded outcome may select
  `implementation_mandate` only on Lean or Compact routes.
- A stated review interval plus fallback selects `windowed` and records whether
  it authorizes only the next phase or continuation through execution.
- Explicit wording such as “无需问我/不要停下来审阅/无人值守执行” selects
  `unattended` for the current unchanged objective.

Ambiguous wording keeps `blocking`. A new objective or scope ends prior review
authority.

### OUT-003 — Artifact-bound Review Gate

The coordinator can park one planning artifact at a time. The gate records only
bounded metadata: artifact key and normalized project-relative path, SHA-256
digest, open timestamp, earliest-resume timestamp when applicable, resulting
ledger revision, scope-delta claim, and unresolved-question count.

Acceptance:

- Only the active workflow and current planning artifact may be parked.
- The artifact uses the existing secure bounded Markdown reader.
- Parking advances revision exactly once and returns the persisted gate summary.
- A corrected artifact may explicitly replace the same open gate, resetting its
  digest and window; an unrelated gate cannot be overwritten.
- No prompt, transcript, artifact contents, credentials, or model reasoning are
  copied into state.

### OUT-004 — Blocking behavior

A `blocking` gate remains ineligible until the caller records explicit approval.
Status checks, hook reminders, elapsed time, `next_action`, and a generic
“continue” after compaction do not consume it.

### OUT-005 — Implementation-mandate behavior

An `implementation_mandate` gate can be consumed immediately only when the route
is Lean or Compact, the artifact declares no scope delta and zero unresolved
questions, and any bound Contract/Plan gate is healthy. Full-route material
decisions remain blocking unless the user selected `windowed` or `unattended`.

### OUT-006 — Windowed behavior

A `windowed` gate is ineligible before its stored deadline. At or after the
deadline it may be consumed once only when the caller records an
`observed-no-intervention` audit claim and all gate invariants remain true.

Acceptance:

- Wall-clock evaluation uses UTC and retains the existing future-skew rules.
- A status command is read-only and reports `waiting`, `eligible`, `blocked`, or
  `no_gate` with bounded reasons.
- Resolution before the deadline, without the audit claim, or a second
  resolution fails without mutation.
- `next_phase` authority ends after the next planned boundary;
  `execute` authority may cross later unchanged gates through implementation but
  never expands external-action authority.

### OUT-007 — Unattended behavior

An `unattended` gate may be consumed immediately for the current unchanged
workflow. It still rejects non-empty scope delta, unresolved questions, artifact
mutation, stale revision, Contract drift, incomplete Plan coverage before
execution, and missing required baseline state.

### OUT-008 — Scope-delta isolation

No automatic resolution kind (`implementation_mandate`, `window_expired`, or
`unattended`) approves a proposed scope delta. Distinct scope-delta approval
continues to use the existing explicit Contract command and audit record. A gate
claiming a proposed delta or any contradiction with the bound Contract remains
blocked.

### OUT-009 — Intervention and correction

While a gate is open, a new user correction, hold, replacement, or unrelated
request cancels automatic continuation before normal request routing. Explicit
approval resolves the gate; an explicit request to keep or restart the timer may
replace it. A scheduler callback instructs the resumed model to inspect the
visible latest conversation and must not claim no intervention when uncertain.

### OUT-010 — Stale and changed-input rejection

Automatic resolution fails atomically when any of these is observed:

- workflow or expected revision mismatch;
- artifact path, bytes, digest, or artifact key changed;
- policy changed or gate was cancelled/replaced;
- unresolved-question count is nonzero;
- scope delta is non-empty or contradictory;
- a bound source or Contract drifted;
- Plan coverage is incomplete when crossing into execution;
- required baseline binding is absent;
- workflow is paused, complete, cancelled, handed off, or rooted elsewhere.

### OUT-011 — Mutation isolation and idempotency

While a gate is open, ordinary checkpoint, bind, validate, pause/resume, or
completion mutations cannot silently advance around it. Only documented gate
resolution, replacement, cancellation, or workflow cancellation may change the
gate. Replayed callbacks and stale scheduler jobs are harmless and perform no
second phase transition.

### OUT-012 — Recoverable schema migration

Schema 1, 2, and 3 state loads into a validated schema-4 view. The first
successful schema-4 mutation creates one byte-for-byte pre-schema4 archive using
the existing secure archive mechanism. Active migrated workflows default to
`blocking` with no open gate; terminal state remains terminal.

Acceptance:

- Existing Outcome Lock, workflow ID, revision, artifacts, progress, and
  verification remain unchanged except for the new schema/protocol/review data.
- Rejected mutations do not write state or archives.
- Unknown future schema/protocol versions fail closed.
- A 1.2 runtime cannot read schema 4; rollback documentation requires restoring
  the exact pre-schema4 archive before installing an older runtime.

### OUT-013 — Recovery and hook summary

`show`, `context`, SessionStart, UserPromptSubmit, and OpenCode injection render
only stored bounded review metadata. They never open the gated artifact, refresh
its digest, inspect a transcript, schedule work, or mutate state.

The brief summary includes mode, gate artifact key, gate state, and deadline
when present. Hooks remain silent without unfinished state and fail open on
invalid state.

### OUT-014 — Codex adapter

In Codex App, a windowed phase asks the host to create one callback in the same
task only when the Scheduled Task capability is callable. The callback uses a
durable fixed prompt containing the exact root, workflow ID, and gate revision;
it re-resolves the installed plugin and calls Review Gate status before any
continuation.

Acceptance:

- The skill never claims a callback was armed when the tool is unavailable or
  the call failed.
- No repeated polling task is created; a callback self-terminates after one
  eligible, blocked, cancelled, or stale observation.
- Codex CLI/IDE without Scheduled management remains parked and reports that
  limitation.

### OUT-015 — Claude Code one-shot adapter

The plugin provides an optional Python-standard-library runner for an exact
Claude Code session. It accepts only an explicit canonical root, workflow ID,
gate revision, deadline-bound open gate, and canonical session identifier. It
spawns one detached sleeper and invokes normal non-interactive
`claude -p --resume <session-id>` once at the deadline.

Acceptance:

- It never uses directory-only `--continue`, `--dangerously-skip-permissions`, a
  model/effort override, transcript access, shell interpolation, polling, or an
  automatic retry loop.
- Job metadata is private, ignored local state; output text is not persisted.
- Before invoking Claude, the child checks the exact gate is still current. A
  cancelled, replaced, stale, blocked, or already consumed gate exits without a
  model call.
- Invocation failure records only bounded status/exit metadata and leaves the
  durable gate open for normal recovery.
- Loss of the sleeping process or reboot does not corrupt state; a later normal
  resume sees an eligible gate.

### OUT-016 — Qoder and OpenCode behavior

Qoder and OpenCode load, validate, and render schema-4 Review Lease state. Until
they expose a verified exact-session scheduler, a windowed gate becomes eligible
but is resumed manually. Neither host receives a fabricated background-resume
claim.

### OUT-017 — Direct-path cost

Tiny untracked direct work creates no policy, gate, digest, scheduler, hook I/O,
or additional model turn. Tracked direct work stores the default policy but does
not park a Review Gate. Ordinary execution checkpoints do not run scheduler
logic.

### OUT-018 — Runtime, privacy, and security boundary

The shared core remains Python 3 standard library only. No telemetry, transcript
parsing, repository recursion, sibling scan, automatic Git mutation, automatic
broad test, hidden reasoning capture, or persistent service is added. Hooks stay
read-only and network-free. The optional Claude adapter invokes the user’s
existing host only after an explicit windowed authorization and does not broaden
its configured permissions.

### OUT-019 — Host and protocol documentation

English/Chinese README, snippets, capability matrix, security model, model
compatibility, Outcome Lock/Review Lease references, changelog, and install and
rollback instructions consistently describe schema 4, protocol 1.3, the four
policies, host limitations, and `1.3.0-alpha.1`.

### OUT-020 — Version and package parity

Codex, Claude Code, Claude marketplace, Qoder, and package metadata share
`1.3.0-alpha.1`. All eleven existing skills remain discoverable with concise
metadata; no new always-loaded skill is required.

### OUT-021 — Behavioral regression coverage

Focused tests cover policy validation, every gate resolution kind, timing
boundaries, replacement/cancellation, stale replay, mutation isolation, artifact
drift, Contract drift, scope delta, schema migration/archive, hook rendering,
runner dry/fake-host behavior, and no-direct-path overhead. Adversarial scenarios
cover implementation intent and timed review without weakening existing Outcome
Lock scenarios.

### OUT-022 — Cross-host validation

The full repository suite, Python compilation, eleven official skill validators,
Codex plugin validator, Claude strict plugin validator, Qoder validator when
installed, and OpenCode syntax/behavior checks pass once at the integrated
release boundary.

### OUT-023 — Completion evidence

The release candidate includes a fresh Verification Record and dated evaluation
report that separate work-unit compliance, approved-outcome fidelity, and code
quality. Unsupported live scheduling or authenticated model runs are reported as
limitations rather than inferred passes.

### OUT-024 — Authority containment

Review policy controls only whether the workflow may advance across Littlepowers
planning gates. It never authorizes commit, push, PR, publish, deploy, access
broadening, destructive action, or another external side effect not already
explicitly included in the latest user request and allowed by the host.

## Error and recovery rules

- State-command errors are concise, non-secret, and leave revision and bytes
  unchanged.
- A scheduler that cannot arm reports the exact limitation; it does not convert
  `windowed` into `unattended`.
- A scheduled callback that cannot acquire the exact session or state exits once
  and leaves the gate recoverable.
- Clock rollback keeps the gate waiting; excessive future timestamps are
  rejected by existing skew validation.
- Correction replaces the same gate and restarts its window. Cancellation leaves
  a bounded last-resolution audit summary.
- After compaction or restart, the host rereads the current plugin, exact root,
  ledger, policy, gate, and artifact before deciding whether to continue.

## Performance constraints

- Policy/status evaluation is in-memory and constant-size.
- Artifact hashing occurs only on park, replacement, resolution, or an explicit
  lifecycle check.
- Hooks read only the ledger and remain under their existing output/time bounds.
- One window creates at most one sleeping Claude process or one Codex callback
  and at most one resumed model turn.
- No automatic full test run is triggered by a phase or timer.

## Parent traceability

| Parent requirement | Outcomes |
| --- | --- |
| Reduce redundant human intervention | OUT-002, OUT-005, OUT-017 |
| Produce a stage artifact, wait, then continue when pre-authorized | OUT-003, OUT-006, OUT-009, OUT-010 |
| Codex support | OUT-014, OUT-022 |
| Claude Code support | OUT-015, OUT-022 |
| Preserve lightweight model-neutral behavior | OUT-017, OUT-018, OUT-020 |
| Preserve Outcome Lock and scope integrity | OUT-008, OUT-010, OUT-011, OUT-012 |
| Deliver `v1.3.0-alpha.1` candidate | OUT-019, OUT-020, OUT-021, OUT-022, OUT-023 |

## Assumptions and open questions

The current user authorization permits unattended local design, implementation,
and validation of this candidate. It does not authorize publishing or installing
the candidate. There are no unresolved product or architecture questions.

## Outcome Contract

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "full",
  "sources": [
    {
      "id": "SRC-001",
      "path": "AGENTS.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-002",
      "path": "README.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-003",
      "path": "skills/using-littlepowers/SKILL.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-004",
      "path": "scripts/littlepowers_state.py",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-005",
      "path": "evals/scenarios.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-006",
      "path": "docs/security-model.md",
      "role": "other",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-007",
      "path": "docs/capability-matrix.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-008",
      "path": "docs/littlepowers/brainstorms/2026-07-31-review-lease.md",
      "role": "requirements",
      "origin": "implementation",
      "approved": true
    }
  ],
  "scope_delta": {
    "status": "none",
    "consequences": []
  },
  "baseline": {
    "requirement": "not_applicable",
    "source_ids": []
  },
  "review": {
    "code_quality_required": true
  },
  "outcomes": [
    {"id": "OUT-001", "title": "Exact persisted review policies", "disposition": "active"},
    {"id": "OUT-002", "title": "Review intent routing", "disposition": "active"},
    {"id": "OUT-003", "title": "Artifact-bound Review Gate", "disposition": "active"},
    {"id": "OUT-004", "title": "Blocking behavior", "disposition": "active"},
    {"id": "OUT-005", "title": "Implementation-mandate behavior", "disposition": "active"},
    {"id": "OUT-006", "title": "Windowed behavior", "disposition": "active"},
    {"id": "OUT-007", "title": "Unattended behavior", "disposition": "active"},
    {"id": "OUT-008", "title": "Scope-delta isolation", "disposition": "active"},
    {"id": "OUT-009", "title": "Intervention and correction", "disposition": "active"},
    {"id": "OUT-010", "title": "Stale and changed-input rejection", "disposition": "active"},
    {"id": "OUT-011", "title": "Mutation isolation and idempotency", "disposition": "active"},
    {"id": "OUT-012", "title": "Recoverable schema migration", "disposition": "active"},
    {"id": "OUT-013", "title": "Recovery and hook summary", "disposition": "active"},
    {"id": "OUT-014", "title": "Codex adapter", "disposition": "active"},
    {"id": "OUT-015", "title": "Claude Code one-shot adapter", "disposition": "active"},
    {"id": "OUT-016", "title": "Qoder and OpenCode behavior", "disposition": "active"},
    {"id": "OUT-017", "title": "Direct-path cost", "disposition": "active"},
    {"id": "OUT-018", "title": "Runtime privacy and security boundary", "disposition": "active"},
    {"id": "OUT-019", "title": "Host and protocol documentation", "disposition": "active"},
    {"id": "OUT-020", "title": "Version and package parity", "disposition": "active"},
    {"id": "OUT-021", "title": "Behavioral regression coverage", "disposition": "active"},
    {"id": "OUT-022", "title": "Cross-host validation", "disposition": "active"},
    {"id": "OUT-023", "title": "Completion evidence", "disposition": "active"},
    {"id": "OUT-024", "title": "Authority containment", "disposition": "active"}
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->
