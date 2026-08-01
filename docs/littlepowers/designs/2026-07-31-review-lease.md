# Littlepowers v1.3 Review Lease design

Date: 2026-07-31

Status: approved by the current unattended workflow authorization

## Design goal

Implement the complete `1.3.0-alpha.1` specification as one protocol outcome:
persist review intent, bind each planned pause to exact artifact bytes, make
eligibility and one-time consumption deterministic, and let Codex or Claude
Code resume a pre-authorized window without adding a daemon, polling loop,
reviewer agent, model selection, or broad-test trigger.

The design extends the existing single-writer schema-3 ledger and hardened
explicit-file boundary. It does not replace the host harness or Outcome Lock.
Qoder and OpenCode consume the same schema and expose eligible work for manual
resume until they provide a verified exact-session scheduling surface.

No scope delta.

The approved baseline is not applicable. Existing schema-3 behavior, security
properties, proportional routes, and four-host discovery are compatibility
constraints rather than a visual or interaction baseline.

## Selected architecture

Use a state-owned Review Lease with thin host adapters:

1. The Python state CLI owns policy validation, artifact binding, time
   eligibility, stale-input rejection, one-time resolution, and audit summary.
2. Phase skills classify the latest request, record one policy, park completed
   planning artifacts, and resolve or wait according to deterministic CLI
   output.
3. Codex may arm one same-task host Scheduled Task at the stored deadline.
4. Claude Code may opt into one detached Python sleeper that resumes one exact
   session once.
5. Hooks and the OpenCode transform remain read-only renderers of already
   persisted bounded data.

This separates authority from wake-up. A host callback can wake a task, but it
cannot make a stale or unsafe gate eligible. Conversely, losing the callback
does not lose the durable gate; the next ordinary resume sees the same state.

### Alternatives rejected

- **Prompt-only review wording:** cheapest, but it cannot survive compaction or
  reject a stale callback deterministically.
- **A persistent scheduler or repository watcher:** could wake every host, but
  adds a competing orchestrator, background scans, lifecycle complexity, and
  unnecessary model/runtime cost.
- **Automatic continuation inside Hook events:** Hook events are not reliable
  authorization boundaries and must remain read-only, network-free, and
  fail-open.
- **A new always-loaded scheduling skill:** increases discovery and prompt
  surface. The existing router and phase skills can describe the two thin
  adapters conditionally.
- **Directory-only Claude `--continue`:** may select the wrong session. Exact
  `--resume <session-id>` is required.

## Component responsibilities

### 1. Schema-4 review state

`scripts/littlepowers_state.py` advances to schema 4 / protocol 1.3 and adds one
top-level `review` record. Every key set remains exact.

```json
{
  "review": {
    "policy": {
      "mode": "blocking",
      "through": "next_phase",
      "wait_seconds": null,
      "recorded_at": "2026-07-31T12:00:00Z"
    },
    "gate": null,
    "last_resolution": null
  }
}
```

Policy modes and valid combinations:

| Mode | `through` | `wait_seconds` | Meaning |
| --- | --- | --- | --- |
| `blocking` | `next_phase` | `null` | Explicit artifact approval is required |
| `implementation_mandate` | `execute` | `null` | A fixed Lean/Compact implementation request may continue |
| `windowed` | `next_phase` or `execute` | 60–604800 | Wait once, then apply the recorded fallback boundary |
| `unattended` | `execute` | `null` | Continue the unchanged current objective through execution |

Contradictory combinations and unknown keys fail validation. New and migrated
workflows default to `blocking`. `start` accepts optional policy arguments so
the router can record the latest request atomically; `set-review-policy`
changes it later with workflow/revision compare-and-swap and only when no gate
is open.

An open gate has this exact bounded shape:

```json
{
  "artifact_key": "design",
  "artifact": "docs/littlepowers/designs/2026-07-31-review-lease.md",
  "digest": "sha256:...",
  "policy_mode": "windowed",
  "through": "execute",
  "opened_at": "2026-07-31T12:00:00Z",
  "not_before": "2026-07-31T12:10:00Z",
  "opened_revision": 8,
  "scope_delta": "none",
  "unresolved_questions": 0
}
```

`digest` hashes the exact bounded UTF-8 artifact bytes; it is deliberately not
the semantic Contract/Plan digest. A byte edit therefore invalidates a queued
callback even when the embedded protocol block is unchanged. `policy_mode` and
`through` snapshot the authority at opening time, so later state cannot reinterpret
the gate.

`last_resolution` stores only artifact key, digest, opened revision, resolution
kind, optional cancellation reason, and timestamp. Allowed kinds are
`explicit_approval`, `implementation_mandate`, `window_expired`, `unattended`,
and `cancelled`. It stores no prompt, artifact content, transcript, or identity
claim.

### 2. Review state commands

Add six interfaces to the shared CLI:

```text
start ... [--review-policy MODE] [--review-through BOUNDARY]
          [--review-wait-seconds SECONDS]
set-review-policy --workflow ID --expect-revision N --mode MODE
                  [--through BOUNDARY] [--wait-seconds SECONDS]
park-review --workflow ID --expect-revision N --artifact-key KEY
            --scope-delta none|proposed --unresolved-questions N [--replace]
review-status --workflow ID --gate-revision N [--json]
resolve-review --workflow ID --expect-revision N --kind KIND
               [--observed-no-intervention]
cancel-review --workflow ID --expect-revision N --reason REASON
```

`park-review` resolves the artifact path only from the current ledger key,
opens it through the existing bounded Markdown boundary, hashes its raw bytes,
and records the resulting revision as `opened_revision`. It accepts planning
keys only. `--replace` requires the same open artifact key and explicitly
restarts digest/deadline state; it cannot overwrite an unrelated gate.

`review-status` is read-only. It reloads the exact root and workflow, requires
the supplied gate revision, rereads the explicit artifact, and evaluates the
current Contract/Plan/baseline boundary only where applicable. It returns one
of:

- `no_gate`: the exact gate no longer exists;
- `waiting`: a valid window has not reached `not_before`;
- `eligible`: the recorded policy permits resolution now;
- `blocked`: a named bounded invariant fails.

The status result includes no artifact content. It may hash explicit gate and
Outcome Lock files because it is an explicit lifecycle check; recovery hooks do
not call it.

`resolve-review` reruns the same fresh evaluator while holding the state lock.
It advances revision once and clears the gate only when the requested kind
matches the snapshotted policy:

- `explicit_approval` resolves only `blocking`;
- `implementation_mandate` resolves only a verified Lean/Compact route;
- `window_expired` resolves only at/after `not_before` and requires
  `--observed-no-intervention`;
- `unattended` resolves only the current unchanged unattended workflow.

Automatic kinds reject a proposed scope delta or unresolved question. They do
not call `bind-contract --approve-scope-delta` and cannot manufacture its audit
record.

When a `windowed/next_phase` gate resolves, the policy atomically resets to
`blocking`. The just-cleared artifact authorizes work in the already recorded
next phase, while the next completed artifact opens a normal blocking gate.
When `windowed/execute` resolves, the policy atomically becomes `unattended`
for this unchanged workflow; later planning artifacts are still parked and
freshly checked, but resolve immediately until execution. The
`window_expired` last-resolution record preserves how that authority began.

`cancel-review` clears the gate and records a bounded reason from
`intervention`, `correction`, `hold`, `replacement`, or `manual`. It does not
advance a phase or approve an artifact.

### 3. Mutation isolation

One helper rejects ordinary mutations while `review.gate` is non-null. It is
called immediately after workflow/revision/status validation by:

- `bind-contract`, `check-contract`, and `validate-plan`;
- `record-verification` and ordinary `checkpoint`;
- `pause`, `resume`, `handoff`, and `complete`;
- policy changes.

Allowed gate mutations are exact replacement, resolution, cancellation, and
whole-workflow `cancel`. This prevents a coordinator from advancing the ledger
around a parked artifact. It does not pretend to be OS-level authorization: a
process with repository write access can still edit files, but the resulting
artifact digest or Contract drift prevents deterministic continuation.

Every automatic resolution also rejects:

- stale workflow, expected revision, or opened revision;
- changed/missing/unsafe artifact path or bytes;
- policy/gate mismatch;
- nonzero unresolved questions or non-empty delta;
- paused or terminal workflow;
- current Contract/source drift;
- incomplete Plan Map when the cleared boundary would enter execution;
- missing required approved baseline state.

Callback replay sees a revision mismatch or `no_gate` and performs no second
transition.

### 4. Phase-skill control flow

`using-littlepowers` classifies only explicit semantic intent; the CLI never
parses chat text.

- discuss/design/wait-for-me wording → `blocking`;
- fixed bounded implement/fix/iterate request on Lean/Compact →
  `implementation_mandate`;
- explicit duration plus fallback boundary → `windowed`;
- explicit no-question/unattended wording → `unattended`;
- ambiguity → `blocking`.

A changed objective or material scope correction cancels an open gate first
and records a new policy. A side/status question does not resolve a gate. At a
windowed callback, the model inspects the visible latest conversation; if it
cannot establish no intervention, it must not supply the audit flag.

Each Lean, Compact, or Full phase uses the same sequence:

1. write and checkpoint the artifact exactly as today;
2. `park-review` against that artifact and current revision;
3. inspect `review-status`;
4. resolve immediately for an eligible implementation mandate or unattended
   policy, present-and-stop for blocking, or arm one supported host callback
   and stop for windowed;
5. after resolution, run the existing Contract Bind or Plan Coverage command
   owned by that boundary and enter the next phase.

This preserves the existing review meaning while making it durable. Direct
untracked work performs none of these operations. Tracked direct work stores
the default policy but never parks a gate.

### 5. Schema migration and rollback

Migration is a pure chain: schema 1 → 2 → 3 → 4. Schema-3 Outcome Lock data,
workflow identity, revision, status, phase, artifacts, progress, history, and
verification are retained; schema 4 adds `review` and changes only protocol
identity. Active/paused views receive `blocking` with no gate. Terminal views
remain terminal.

`load_state` retains the exact raw state bytes alongside the validated migrated
view. The first successful schema-4 mutation writes those raw bytes once into:

```text
.littlepowers/archive/<timestamp>-<workflow>-r<revision>-pre-schema4-v<schema>.json
```

The archive uses the existing pinned private archive directory and a new
bounded atomic raw-byte writer. Failed validation or mutation creates neither
archive nor current state. Later writes do not duplicate the archive.

A 1.2 runtime must fail closed on schema 4. Rollback requires stopping the
active workflow, restoring the exact pre-schema4 archive as `state.json`, and
then installing 1.2. Live state is never edited or downgraded in place.

For this self-hosted implementation, the plan and initial execution transition
use the already installed 1.2 CLI. Candidate schema-4 code is first exercised
only on temporary roots. After migration tests pass, the source CLI performs
the live first mutation and records the current user authorization as
`unattended`; every later live mutation uses that source CLI. At integration,
the implementation-modified bound repository sources are explicitly rebound
and the unchanged 24-ID Plan Map is revalidated before verification.

### 6. Recovery and hooks

`_recovery_data` adds a constant-size review summary:

```json
{
  "mode": "windowed",
  "gate": "design",
  "state": "waiting",
  "not_before": "2026-07-31T12:10:00Z"
}
```

The rendered state comes only from stored fields. Hooks do not reopen the
artifact, evaluate wall-clock eligibility, schedule work, inspect prompts or
transcripts, or mutate the ledger. To avoid misleading stale time claims, the
stored renderer reports `waiting` for an open window and tells the coordinator
to use `review-status`; only the explicit status command may report `eligible`.
Blocking/unattended/implementation modes can render their stored mode and gate
presence without inferring approval.

The existing silent-without-state, fail-open, 5-second hook, 4-second OpenCode
transform, context-size, ownership, and worker-read-only behavior remains.

### 7. Codex host adapter

No Codex-specific runtime module is added. The phase/router skill contains one
conditional adapter procedure:

1. Only for a valid open `windowed` gate, search for the host's Scheduled Task
   management capability.
2. If unavailable, remain parked and report that automatic wake-up is not
   armed.
3. If available, create one callback in the current task at `not_before` with a
   fixed prompt containing only canonical root, workflow ID, and opened gate
   revision.
4. The callback resolves the currently enabled Littlepowers plugin, runs
   `review-status`, inspects the latest visible conversation, and either calls
   `resolve-review --kind window-expired --observed-no-intervention` or exits
   without continuation.
5. It self-disables after one eligible, blocked, cancelled, stale, or failed
   observation. It never creates a polling model loop.

The skill acknowledges an armed callback only after the host tool succeeds. If
the tool cannot express a same-task one-shot callback at the deadline, the
adapter is unsupported and the gate stays parked; it does not approximate with
an unbounded recurring task.

### 8. Claude Code one-shot runner

Add `scripts/littlepowers_review_runner.py`, using only the Python standard
library. It has public `schedule` and `status` commands plus an internal child
entry point.

`schedule` requires:

- a canonical absolute workspace root;
- canonical workflow UUID and exact opened gate revision;
- a current valid `windowed` gate with a future deadline;
- a canonical Claude Code session UUID;
- a discoverable `claude` executable.

It creates private mode-0600 metadata under
`.littlepowers/review-jobs/<workflow>-r<gate-revision>.json`, then starts one
detached child. The child sleeps once until the stored UTC deadline—there is no
poll loop. On wake it reloads the exact root and exits unless `review-status`
for the same workflow/gate is `eligible`. It then invokes exactly one argument
vector, without a shell:

```text
claude -p --resume <session-id> <fixed-callback-prompt>
```

The prompt instructs the resumed coordinator to resolve the current plugin,
inspect the latest conversation, recheck the exact gate, and continue only
when no intervention is visible. Normal Claude permissions remain in force.
The runner never supplies `--continue`, `--dangerously-skip-permissions`, a
model/effort flag, or transcript path.

Child stdout/stderr are discarded; no model output is stored. Metadata records
only `armed`, `invoking`, `completed`, `failed`, or `stale`, timestamps, child
PID where available, and bounded exit/timeout status. Writes use private atomic
replacement and reject links, unsafe ownership, duplicate jobs, or path
replacement. The resumed host call has one bounded timeout and no retry.

If the sleeper is lost, metadata may remain `armed`, but the ledger gate is
unchanged. `status` reports the bounded job state; a normal later Claude resume
can consume an eligible gate manually. Scheduling the same exact job is
idempotent and never creates a second sleeper.

### 9. Qoder and OpenCode

Both hosts use the same schema validator, state CLI, skills, and stored recovery
summary. A window can become eligible, but the router reports manual resume
because no verified exact-session scheduler is part of this release. The
OpenCode JavaScript plugin remains a read-only skill/recovery adapter and does
not launch the Claude runner.

### 10. Packaging and documentation

Update all version surfaces to `1.3.0-alpha.1`:

- Codex, Claude Code, Claude marketplace, and Qoder manifests;
- root `package.json` for OpenCode;
- README install examples and English/Chinese behavior;
- changelog, snippets, capability matrix, security model, and model
  compatibility report.

Add `references/review-lease.md` for the exact policy/gate command contract and
update `references/outcome-lock.md` only where schema/protocol/lifecycle
integration changes. Keep eleven skills; no new always-loaded skill is needed.

## Failure and recovery matrix

| Failure | Deterministic result | Recovery |
| --- | --- | --- |
| Deadline not reached | `waiting`, no mutation | Wait or explicit human approval |
| New correction/hold | Gate cancelled before routing | Revise/restart explicitly |
| Artifact bytes changed | `blocked`, no mutation | Replace gate after correction |
| Contract/source drift | `blocked`, no digest adoption | Review and rebind Contract |
| Incomplete Plan coverage | Execution resolution blocked | Fix and revalidate Plan Map |
| Scope delta proposed | Automatic resolution blocked | Distinct explicit delta approval |
| Callback replay | Conflict or `no_gate` | Exit once |
| Codex scheduler unavailable | Gate remains parked | Manual resume/approval |
| Claude sleeper lost | Gate remains durable | Normal session resume |
| Claude process fails/times out | Bounded failed job status; gate open | Manual resume; no auto retry |
| Host/session mismatch | Callback exits stale | Arm only from exact current session |
| Old runtime sees schema 4 | Fail closed | Restore pre-schema4 archive before rollback |

## Security and privacy invariants

- The root coordinator remains the only ledger writer.
- Repository data and artifact contents remain untrusted.
- The state file remains ignored, private, bounded, exact-key validated, and
  atomically written under workflow/revision CAS.
- Hooks remain read-only, network-free, transcript-free, and scheduler-free.
- Only explicit files are read; no repository or sibling scan is added.
- No telemetry, prompts, transcripts, credentials, model output, or hidden
  reasoning are persisted.
- Scheduled continuation never bypasses host permissions or expands external
  authority. It does not authorize commit, push, PR, publish, deploy,
  destructive action, or access broadening.
- No adapter selects a model, reasoning effort, or agent topology.
- The direct untracked path performs no Review Lease work.

## Verification strategy

Pure policy/gate evaluators are tested independently from I/O. State command
tests then cover exact schema, CAS, locking, migration/archive, raw artifact
drift, every resolution mode, boundary timestamps, cancellation/replacement,
mutation isolation, Outcome Lock interaction, and replay. Hook tests assert
stored-only rendering. Runner tests use temporary roots, patched clocks, and a
fake executable to prove one exact invocation, no shell/forbidden flags,
idempotency, stale exit, private metadata, timeout, and no retry.

Skill/manifest tests assert proportional routing, intervention behavior,
Codex truthful capability handling, Claude exact-session instructions, Qoder
and OpenCode limitations, authority containment, eleven-skill discovery, and
version parity. Evaluation scenarios add fixed-implementation,
windowed-next-phase, windowed-through-execute, intervention-before-deadline,
callback replay, lost sleeper, and direct fast-path cases.

Focused checks run after each reversible code unit. The full Python suite,
compilation, all eleven skill validators, Codex plugin validator, Claude strict
validator, Qoder validator when installed, OpenCode syntax/behavior tests, and
integrated diff review run once at the release boundary. Live Codex scheduling
or authenticated Claude model behavior is reported as untested unless actually
exercised.

## Reversible implementation units

These units are dependency order and rollback boundaries, not waves, staged
deliveries, or product slices:

1. Schema-4 review records, migration, raw archive, and pure evaluator.
2. Review commands plus lifecycle mutation isolation.
3. Recovery rendering and phase/router skill integration.
4. Claude one-shot runner and conditional Codex adapter guidance.
5. Cross-host package/docs/evals and aggregate verification.

All five remain one workflow and one definition of done. A passing unit is
incomplete progress until every OUT ID and the integrated release boundary
passes.

## Requirement-to-design mapping

| Outcome | Design path |
| --- | --- |
| OUT-001 | Exact schema-4 policy record and combination table |
| OUT-002 | Router intent classification and ambiguity default |
| OUT-003 | Artifact-bound gate shape and `park-review` |
| OUT-004 | Blocking resolution-kind match and mutation isolation |
| OUT-005 | Lean/Compact route check for implementation mandate |
| OUT-006 | UTC deadline evaluator, audit flag, and policy-boundary transition |
| OUT-007 | Unattended fresh invariant evaluation |
| OUT-008 | Automatic delta rejection and separate Contract approval |
| OUT-009 | Cancel/replace semantics and callback conversation inspection |
| OUT-010 | Fresh artifact, Contract, plan, baseline, status, and CAS checks |
| OUT-011 | Shared open-gate mutation guard and replay behavior |
| OUT-012 | 1→2→3→4 migration and raw pre-schema4 archive |
| OUT-013 | Stored-only recovery summary and unchanged Hook boundary |
| OUT-014 | Conditional one-shot same-task Codex adapter |
| OUT-015 | Exact-session standard-library Claude runner |
| OUT-016 | Shared schema plus truthful manual Qoder/OpenCode resume |
| OUT-017 | No gate on untracked/tracked direct paths |
| OUT-018 | Explicit-file, no-daemon, no-telemetry security invariants |
| OUT-019 | README/reference/capability/security/compatibility updates |
| OUT-020 | Five package/version surfaces and unchanged eleven skills |
| OUT-021 | Pure, command, hook, runner, adversarial, and fast-path tests |
| OUT-022 | One integrated four-host validation boundary |
| OUT-023 | Fresh Verification Record and dated evaluation report |
| OUT-024 | Planning-gate-only authority and external-action exclusions |

## Open questions

None. When a host does not expose a safe exact-session one-shot scheduling
capability, the specified behavior is to leave the durable gate parked and
state the limitation rather than inventing a weaker mechanism.
