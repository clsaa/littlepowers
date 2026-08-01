# Review Lease protocol 1.3

Read this reference only when selecting review intent, parking or resolving a
planning artifact, recovering an open Review Gate, or arming a pre-authorized
host callback. The state CLI—not prose or a callback—is the deterministic
authority.

## Policies

Record exactly one policy from the latest request:

| Policy | Use when | Boundary |
| --- | --- | --- |
| `blocking` | The user asks to discuss/design/wait, or intent is ambiguous | One approved artifact |
| `implementation_mandate` | The user requests implementation of a fixed bounded Lean/Compact outcome | Through execution |
| `windowed` | The user gives a wait duration and fallback | `next_phase` or `execute` |
| `unattended` | The user explicitly says not to ask or stop for this unchanged objective | Through execution |

Plain “end-to-end delivery” is not unattended authority. A new objective,
scope correction, hold, or replacement ends prior automatic authority. No
policy approves a scope delta or an external action such as commit, push, PR,
publish, deploy, destructive work, secrets access, or permission broadening.

Start can persist policy atomically:

```bash
<python> <state-cli> --root <project-root> start \
  --objective "<complete outcome>" --phase <brainstorm|shape|execute> \
  --next-action "<next action>" \
  --review-policy <blocking|implementation_mandate|windowed|unattended> \
  [--review-through <next_phase|execute> \
   --review-wait-seconds <60..604800>]
```

The bracketed pair is mandatory for `windowed` and omitted for other policies.
There is no default execution boundary for a timed authorization.

Change policy only with no open gate:

```bash
<python> <state-cli> --root <project-root> set-review-policy \
  --workflow <id> --expect-revision <revision> \
  --mode <mode> [--through <boundary>] [--wait-seconds <seconds>]
```

## Phase boundary

After checkpointing a completed Lean, Compact, or Full planning artifact, park
that exact ledger key:

```bash
<python> <state-cli> --root <project-root> park-review \
  --workflow <id> --expect-revision <revision> \
  --artifact-key <brainstorm|spec|design|plan|shape> \
  --scope-delta <none|proposed> --unresolved-questions <count>
```

Parking binds the normalized ledger path, exact UTF-8 bytes, current policy,
deadline, and resulting revision. When the artifact embeds a Contract, it also
binds the bounded digest set of every explicitly named parent source. It stores
no artifact or source content and no prompt.
Correcting the same open artifact requires `--replace`, which resets its digest
and window. An unrelated gate cannot be overwritten.

Inspect one exact gate without mutation:

```bash
<python> <state-cli> --root <project-root> review-status \
  --workflow <id> --gate-revision <opened-revision> --json
```

Status is `no_gate`, `waiting`, `eligible`, or `blocked`. It freshly checks the
artifact and applicable Contract, Plan Map, scope, and baseline boundaries.
Hooks never run this check.

Resolve only with the kind required by the stored policy:

```bash
<python> <state-cli> --root <project-root> resolve-review \
  --workflow <id> --expect-revision <revision> \
  --kind <explicit_approval|implementation_mandate|window_expired|unattended> \
  [--observed-no-intervention]
```

`window_expired` requires the audit flag after inspecting the latest visible
conversation. Never supply it when intervention is visible or uncertain. A
`next_phase` window resets policy to blocking after resolution. An `execute`
window becomes unattended for the same unchanged workflow. Automatic kinds
always reject proposed scope delta, unresolved questions, changed bytes,
Contract drift, or incomplete Plan coverage.

After resolution, run the existing boundary owner:

- bind an approved Lean brainstorm, Compact shape, or Full specification;
- validate an approved plan or Compact shape;
- then enter the next phase or execution.

The bind and validate commands require the successful resolution to match the
current artifact key, original normalized path, exact bytes, and any embedded
Contract source-digest set. Contract bind and Plan validation each consume
their boundary authorization once in the same successful state revision; a
Compact shape may be consumed once by each of those two declared owners. A
prior bind or validation cannot be replayed to adopt changed sources or a
copied artifact. Their audit arguments cannot be used without that persisted
resolution. A prerelease schema-4 resolution missing path or consumption data
loads only for recovery and fails closed until the exact artifact is parked and
resolved again.

An open gate blocks ordinary bind/check/validate/checkpoint/pause/resume/
handoff/complete mutations. Cancel it before a correction or replacement:

```bash
<python> <state-cli> --root <project-root> cancel-review \
  --workflow <id> --expect-revision <revision> \
  --reason <intervention|correction|hold|replacement|manual>
```

Whole-workflow cancellation remains available and clears the gate safely.

## Host wake-up

Wake-up is optional and never changes eligibility.

### Codex

For a valid windowed gate, use a same-task one-shot Scheduled Task only when
the host exposes a callable automation-management tool that can schedule it at
the stored deadline and disable it after one observation. The fixed callback
prompt contains only the canonical root, workflow ID, and gate revision. It
must resolve the current plugin, inspect the latest conversation, run
`review-status`, and resolve only when still eligible and uninterrupted.

Do not claim the callback is armed until the tool succeeds. If that exact
capability is absent, remain parked; do not approximate with an unbounded
recurring task.

### Claude Code

Only after an explicit windowed authorization and with the exact current
session UUID, the optional standard-library runner may arm one sleeper:

```bash
<python> <plugin-root>/scripts/littlepowers_review_runner.py schedule \
  --root <canonical-root> --workflow <id> \
  --gate-revision <opened-revision> --session <session-uuid>
```

Use its `status` command for bounded job metadata. It invokes at most one normal
`claude -p --resume <session-id>` call, with no shell, `--continue`, permission
bypass, model/effort override, polling, transcript read, output persistence, or
retry. Losing the sleeper leaves the durable gate available for manual resume.

### Qoder and OpenCode

Render the stored gate and use manual resume. Until an exact-session scheduler
is verified, never claim background continuation was armed.

## Recovery and privacy

Schema 4 stores only policy, gate metadata, and one bounded last-resolution
summary, including artifact/source digests and the two possible consumption
revisions. Recovery hooks render stored mode/key/state/deadline only; they do
not hash artifacts, evaluate time, inspect prompts/transcripts, schedule work,
or mutate state. The root coordinator remains the only ledger writer.
