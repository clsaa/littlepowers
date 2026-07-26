# Outcome Lock solution design

Date: 2026-07-26

Status: approved

## Scope anchor

This design implements all requirements in
`docs/littlepowers/specs/2026-07-26-outcome-lock.md` and preserves the approved
behaviors inherited from the 1.1 scope-integrity release.

No scope delta.

The approved compatibility baseline is `v1.1.0-alpha.1`: direct/lean/compact/full
routing, schema-2 recovery behavior, secure local state storage, read-only hooks,
single-writer revision control, and shared Codex/Claude Code/Qoder/OpenCode
runtime behavior.

## Architecture decision

Extend the existing Python state engine instead of adding another orchestrator.
Use three small, versioned JSON records embedded in ordinary Markdown artifacts:

1. an Outcome Contract in the approved brainstorm/spec/shape or an explicit
   contract artifact;
2. an Outcome Plan Map in the approved plan or compact shape;
3. a Verification Record in a verification evidence artifact.

The ledger stores only validated identifiers, digests, counts, verdict summaries,
and lifecycle status. It never stores parent-document contents, outcome prose,
screenshots, command output, or review prose.

### Alternatives rejected

- **More skill prose only:** cannot survive old sessions, compaction, or a
  narrowed child contract.
- **Full Markdown table parsing:** human-friendly but ambiguous around escaping,
  duplicate rows, whitespace, and future prose changes.
- **Standalone JSON/YAML sidecars for every route:** deterministic, but adds
  artifacts and ceremony to lean work; YAML would also add a runtime dependency
  or a custom parser.
- **A service/database/agent loop:** adds latency, host coupling, and competing
  orchestration without improving the local invariant.

### Why embedded JSON

- Python's standard library parses it deterministically.
- A tagged block is visible and reviewable in the same artifact as its prose.
- Canonical JSON produces a semantic digest unaffected by unrelated Markdown
  formatting.
- Lean and full routes reuse artifacts they already create.
- Direct untracked work remains untouched.

## Component responsibilities

### 1. Structured block parser

Add a dependency-free parser inside `scripts/littlepowers_state.py`.

It extracts exactly one explicitly tagged block:

````text
<!-- littlepowers:<record-kind>:v1 -->
```json
{ ... }
```
<!-- /littlepowers:<record-kind> -->
````

The literal record kinds are:

- `contract`
- `plan-map`
- `verification`

The implementation will construct the fence strings rather than nesting this
example verbatim in Python source.

Parser invariants:

- UTF-8 input with CRLF normalized to LF;
- exactly one opening marker, JSON fence, closing fence, and matching kind;
- JSON root must be an object;
- duplicate JSON keys are rejected through `object_pairs_hook`;
- unknown keys, invalid enums, overlong strings, duplicate IDs, and excessive
  counts are rejected;
- prose outside the tagged block is never interpreted as protocol data;
- validated records are canonicalized with sorted keys, compact separators, and
  UTF-8 preservation before SHA-256 hashing.

The semantic digest format is `sha256:<64 lowercase hex characters>`.
For contract, plan, and verification artifacts this digest covers the validated
protocol record, not surrounding Markdown prose. Raw SHA-256 digests cover every
explicit parent, baseline, and implementation-evidence file.

### 2. Secure explicit-file reader

Generalize the current bounded Markdown artifact reader into one shared
workspace-file reader while preserving:

- exact-root containment;
- normalized forward-slash relative paths;
- no `.`/`..` or hidden components;
- no symlink, reparse point, special file, or hard-linked file;
- descriptor-relative traversal on supported POSIX systems;
- inode/device recheck against path replacement;
- owned metadata checks;
- bounded reads.

Markdown protocol artifacts keep the current 128 KiB maximum. Explicit parent,
baseline, and implementation-evidence files use:

- at most 64 bound files per contract;
- at most 16 MiB per file;
- at most 64 MiB total per explicit check.

No recursive discovery, Git candidate scan, sibling search, URL fetch, or network
access is added. A remote prototype must be exported into the exact workspace or
represented by an approved local contract file before it can be hashed.

### 3. Outcome Lock evaluator

Pure functions validate and derive:

- contract semantic identity;
- parent-source digests;
- active, added, changed, deferred, and removed Outcome sets;
- plan coverage and missing/unknown Outcome IDs;
- required fidelity comparison IDs;
- verification coverage and independent verdicts;
- completion failures.

These functions receive already-read bytes and dictionaries. They do not perform
I/O or mutate state, which keeps gate behavior independently testable.

### 4. Transaction coordinator

Existing command handlers remain the only writers. Each mutating command:

1. locks the exact ledger;
2. loads and validates current or migrated state;
3. verifies workflow ID and expected revision;
4. reads only explicitly required files;
5. computes a complete candidate state in memory;
6. validates every invariant and serialized-size limit;
7. writes a pre-migration archive when applicable;
8. advances revision exactly once and atomically replaces `state.json`.

Malformed input or a rejected transition does not write the ledger or increment
the revision. A valid observation that records `drifted`, or valid verification
evidence whose result is `fail`/`blocked`, is a successful state update rather
than a partial failure.

### 5. Recovery renderer and hooks

`_recovery_data` reads only persisted summary fields. It does not call the
structured parser, stat a bound source, or hash a file.

The brief recovery object adds one compact `outcome_lock` object:

```json
{
  "contract": "bound",
  "coverage": "23/23",
  "baseline": "bound",
  "fidelity": "pending"
}
```

Full session context may also report missing counts and `reconcile_required`, but
never source paths, titles, approval details, evidence paths, or file contents.
Existing silent/no-active-state and non-blocking hook behavior remains unchanged.

## Markdown protocol records

### Outcome Contract record

New lean/full/compact artifacts include:

````markdown
<!-- littlepowers:contract:v1 -->
```json
{
  "route": "full",
  "sources": [
    {
      "id": "SRC-001",
      "path": "docs/PRD-v1.3.md",
      "role": "requirements",
      "origin": "user",
      "approved": true
    },
    {
      "id": "SRC-002",
      "path": "docs/prototype/home.png",
      "role": "prototype",
      "origin": "user",
      "approved": true
    }
  ],
  "scope_delta": {
    "status": "none",
    "consequences": []
  },
  "baseline": {
    "requirement": "required",
    "source_ids": ["SRC-002"]
  },
  "review": {
    "code_quality_required": true
  },
  "outcomes": [
    {
      "id": "OUT-001",
      "title": "Complete approved home-page states",
      "disposition": "active"
    }
  ],
  "fidelity": [
    {
      "id": "FID-001",
      "outcome": "OUT-001",
      "baseline": "SRC-002",
      "surface": "home",
      "action": "open",
      "state": "default"
    }
  ]
}
```
<!-- /littlepowers:contract -->
````

Contract enums:

- `route`: `lean`, `compact`, or `full`;
- source `role`: `requirements`, `interaction`, `prototype`, `screenshot`,
  `api`, `migration`, `compatibility`, or `other`;
- source `origin`: `user`, `repository`, `external`, or `implementation`;
- outcome `disposition`: `active`, `added`, `changed`, `deferred`, or
  `removed`;
- scope delta `status`: `none` or `proposed`;
- baseline `requirement`: `required` or `not_applicable`.

Identifier grammar:

- Outcome: `OUT-[0-9]{3}`
- Parent/baseline source: `SRC-[0-9]{3}`
- Fidelity comparison: `FID-[0-9]{3}`

Contract limits:

- 1–200 outcomes;
- 0–64 sources;
- 0–500 fidelity comparisons;
- title/surface/action/state strings are bounded and may not be empty.

Derived rules:

- `scope_delta.status=none` requires every outcome disposition to be `active`
  and consequences to be empty.
- `scope_delta.status=proposed` requires at least one non-active disposition and
  at least one non-empty consequence.
- `added` and `changed` outcomes stay active.
- `deferred` and `removed` outcomes remain in the auditable original set but are
  excluded from the active denominator only after distinct delta approval.
- On rebind, an old ID may not disappear. It must remain and be marked
  `removed`; a new ID must be marked `added`; a changed normalized record must be
  marked `changed`.
- A required baseline must reference at least one existing source with
  `approved=true` and `origin != implementation`.
- Every fidelity row references an active Outcome and an approved baseline
  source.
- `baseline=not_applicable` requires no fidelity rows or baseline source IDs.

The CLI validates declarations and explicit approval claims. It cannot prove that
an agent truthfully labeled a source as user-approved; the route review gate is
the semantic trust boundary.

### Outcome Plan Map record

The full/lean plan, or compact shape, includes:

````markdown
<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 2"],
      "evidence": [
        "test:home-state",
        "visual:approved-home"
      ]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
````

Rules:

- exactly one mapping per active Outcome;
- no mapping for deferred or removed outcomes;
- every mapping has one or more unique task labels and evidence tokens;
- unknown Outcome IDs fail;
- evidence tokens use `<kind>:<stable-label>`;
- allowed kinds are `test`, `inspection`, `visual`, `interaction`, `manual`,
  `build`, `host`, `security`, `migration`, `review`, and `other`;
- prose contains the executable commands and rollback details; the block carries
  only stable references.

Coverage is derived as:

```text
original_total = every Outcome in the contract
active_total = active + added + changed
mapped_active = unique active Outcome IDs with valid mappings
coverage_pass = mapped_active == active_total and unknown == 0
```

### Verification Record

Tracked workflows create one Markdown evidence artifact in verification:

````markdown
<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": ["test:focused-state-suite"]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": ["inspection:outcome-traceability"]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": ["review:integrated-diff"]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": ["test:home-state", "visual:approved-home"]
    }
  ],
  "fidelity": [
    {
      "id": "FID-001",
      "outcome": "OUT-001",
      "baseline": "SRC-002",
      "evidence_path": "artifacts/verification/home-default.png",
      "result": "pass"
    }
  ]
}
```
<!-- /littlepowers:verification -->
````

Rules:

- every active Outcome appears exactly once with `pass`, `fail`, or `blocked`;
- evidence tokens follow the Plan Map grammar;
- every required FID appears exactly once;
- fidelity rows must preserve the contract's Outcome and baseline references;
- `evidence_path` uses the secure explicit-file reader and is hashed;
- implementation evidence is never promoted into the contract's approved
  baseline source list;
- aggregate `outcome_fidelity=pass` is valid only when every active outcome and
  required FID passes;
- `work_unit=pass` and required `code_quality=approve` each need evidence;
- a valid `fail` or `blocked` record is persisted for recovery;
- malformed or internally contradictory verification is rejected without a
  write.

For a nonvisual contract with `baseline=not_applicable`, `fidelity` is empty, but
every active Outcome still needs an outcome result and approved-outcome fidelity
must still pass before completion.

## Schema 3

The exact persisted shape is:

```json
{
  "schema_version": 3,
  "protocol_version": "1.2",
  "created_by": "littlepowers",
  "workflow_id": "uuid",
  "revision": 7,
  "status": "active",
  "objective": "...",
  "phase": "verify",
  "artifacts": {
    "brainstorm": null,
    "spec": null,
    "design": null,
    "plan": null,
    "shape": null,
    "contract": null,
    "evidence": null
  },
  "current_task": null,
  "progress": null,
  "handoff": null,
  "next_action": "...",
  "completed": [],
  "created_at": "...",
  "updated_at": "...",
  "outcome_lock": {
    "mode": "artifact",
    "status": "bound",
    "contract": {
      "artifact": "docs/littlepowers/specs/example.md",
      "semantic_digest": "sha256:...",
      "approval": {
        "kind": "review_gate",
        "recorded_at": "..."
      },
      "sources": [
        {
          "id": "SRC-001",
          "path": "docs/PRD.md",
          "role": "requirements",
          "origin": "user",
          "approved": true,
          "digest": "sha256:..."
        }
      ],
      "outcomes": {
        "OUT-001": "sha256:..."
      },
      "fidelity_ids": [],
      "code_quality_required": true
    },
    "scope_delta": {
      "status": "none",
      "added": [],
      "changed": [],
      "deferred": [],
      "removed": [],
      "approval": null
    },
    "plan": {
      "artifact": "docs/littlepowers/plans/example.md",
      "semantic_digest": "sha256:...",
      "coverage": {
        "original_total": 1,
        "active_total": 1,
        "mapped_active": 1,
        "approved_deferred": 0,
        "approved_removed": 0,
        "missing": [],
        "unknown": [],
        "status": "pass"
      }
    },
    "baseline": {
      "requirement": "not_applicable",
      "status": "not_applicable",
      "source_ids": [],
      "required_comparisons": 0,
      "passed_comparisons": 0
    },
    "verification": {
      "artifact": "docs/littlepowers/evidence/example.md",
      "semantic_digest": "sha256:...",
      "work_unit": "pass",
      "outcome_fidelity": "pass",
      "code_quality": "approve",
      "blocking_evidence": 0,
      "verified_outcomes": 1
    },
    "last_checked_at": "...",
    "drift": []
  }
}
```

Only digests and bounded summaries are duplicated into state. Detailed mappings,
titles, comparison states, evidence labels, and evidence paths stay in the
reviewed Markdown artifacts.

State enums:

- lock `mode`: `unbound`, `artifact`, `direct`, or `legacy_terminal`;
- lock `status`: `unbound`, `bound`, `drifted`, `reconcile_required`, or
  `not_required`;
- scope delta: `reconcile_required`, `none`, or `approved`;
- coverage: `pending` or `pass`;
- baseline: `unbound`, `bound`, `pending`, `pass`, `fail`, `blocked`,
  `not_applicable`, or `reconcile_required`;
- work-unit and fidelity verdicts: `pending`, `pass`, `fail`, or `blocked`;
- code-quality verdict: `not_required`, `pending`, `approve`,
  `request_changes`, or `blocked`.

`validate_state` checks exact key sets, enum values, ID grammar, digest grammar,
count bounds, path normalization, cross-field totals, and terminal/lock
invariants. It does not open bound sources.

## Direct route

Untracked direct work performs no ledger or Outcome Lock work.

Tracked direct work starts with:

```bash
<state-cli> --root <root> start \
  --objective "<objective>" \
  --phase execute \
  --direct-lock \
  --next-action "<action>"
```

`--direct-lock` is valid only for `phase=execute` with no planning artifacts. It
creates:

- `mode=direct`;
- one inline `OUT-001` whose digest covers the normalized objective;
- `status=bound`;
- scope delta `none`;
- baseline `not_applicable`;
- code-quality review not required;
- no contract or plan artifact.

Visual, interaction, output-format, migration, security, or compatibility work
that needs an approved baseline or material review is not eligible for this
minimal direct lock and must use a proportional artifact route.

Before completion, tracked direct work still transitions to verify and records a
Verification Record for `OUT-001`. This is evidence, not a planning artifact.

Starting at execute without `--direct-lock` remains accepted for compatibility
but produces `mode=unbound`; it cannot enter valid verification or completion
until explicitly bound.

## CLI interfaces

### `bind-contract`

```bash
<state-cli> --root <root> bind-contract \
  --workflow <id> --expect-revision <revision> \
  --artifact docs/.../approved.md \
  --approval-kind <review-gate|unattended-authorization> \
  [--approve-scope-delta]
```

Behavior:

- parses the Outcome Contract;
- securely hashes every declared source;
- validates baseline provenance and scope declarations;
- on rebind, compares old/new IDs and normalized record hashes;
- requires `--approve-scope-delta` exactly when the delta is non-empty;
- stores `artifacts.contract`, invalidates prior plan and verification summaries,
  clears drift, and returns `bound`;
- clears `reconcile_required` only on complete success.

The approval flags are explicit coordinator audit claims, not authentication.

### `check-contract`

```bash
<state-cli> --root <root> check-contract \
  --workflow <id> --expect-revision <revision>
```

For an artifact lock it reparses the tagged contract, recomputes its semantic
digest, and recomputes every recorded source digest. For a direct lock it checks
the normalized objective digest. The command successfully persists either
`bound` or `drifted`, updates `last_checked_at`, advances revision once, and
returns the observed status. It never adopts new digests. Rebinding is a
separate approved operation.

### `validate-plan`

```bash
<state-cli> --root <root> validate-plan \
  --workflow <id> --expect-revision <revision> \
  --artifact docs/.../plan-or-shape.md
```

It parses the Plan Map against the bound contract. Complete coverage stores the
semantic digest and summary. Missing/unknown IDs or absent evidence reject the
command without mutation and report all offending IDs.

### `record-verification`

```bash
<state-cli> --root <root> record-verification \
  --workflow <id> --expect-revision <revision> \
  --artifact docs/littlepowers/evidence/<name>.md
```

It is valid only in active verification. It rechecks current contract and plan
semantics, securely hashes explicit fidelity evidence, derives verdicts, and
stores valid pass/fail/blocked summaries. Contradictory or malformed records are
rejected without mutation.

### Existing commands

- `show`, `context`, `read-artifact`, and hooks never refresh digests.
- `read-artifact` gains `contract` and `evidence` keys.
- `checkpoint` enforces the transition matrix below.
- `resume` may resume a legacy workflow only into reconciliation; it cannot make
  execution ready.
- `pause`, `cancel`, and explicit replacement remain available even when the
  lock is invalid.
- `complete` performs the aggregate gate and lists all failures.
- `handoff` from execute/verify requires a current executable lock; planning
  handoffs retain existing behavior.

## Transition matrix

| Operation | Required lock behavior |
| --- | --- |
| New brainstorm/spec/design/plan/shape checkpoint | May remain `unbound`; no source hashing |
| Bind/rebind contract | Explicit artifact read and source hashing |
| Validate plan | Requires `bound`; parses one explicit map |
| Transition into execute | Requires fresh contract check and passing plan coverage; direct lock is exempt from plan |
| Execute progress checkpoint | Requires last-known `bound` and passing coverage; no source rehash |
| Resume into legacy execute/verify | Becomes active for reconciliation, stays non-executable |
| Transition into verify | Fresh contract check plus passing current plan/direct lock |
| Record verification | Fresh contract/plan validation and explicit evidence reads |
| Complete | Fresh contract, plan, verification, baseline, fidelity, verdict, and blocker checks |
| Pause/cancel | Always permitted with normal writer authority |
| Handoff during planning | Existing target validation |
| Handoff from execute/verify | Requires current executable lock before existing target validation |
| Show/context/hook | Stored summaries only; no mutation or hashing |

A transition command that discovers stale data rejects without mutation and tells
the coordinator to run the explicit check/rebind/validate command. This preserves
the invariant that failed gates do not increment revision.

## Completion evaluator

`complete` builds one list of failures instead of stopping at the first:

- phase is not verify;
- contract is not bound;
- a current parent source digest differs;
- plan digest or coverage is stale/incomplete;
- active coverage is not 100%;
- scope delta is pending/unapproved;
- required baseline is not pass;
- required fidelity comparison is missing/non-pass;
- an active Outcome has no passing verification;
- work-unit compliance is not pass;
- approved-outcome fidelity is not pass;
- required code-quality review is not approve;
- blocking evidence is nonzero.

If the list is non-empty, output all conditions and do not mutate state. If it is
empty, set `status=complete`, advance revision once, and write atomically.

## Migration and rollback

### Read-only migration view

Split loading internally:

- `_load_state_record` returns a validated schema-3 view plus optional migration
  metadata containing the original parsed legacy state and schema;
- public `load_state` continues returning a dictionary, preserving callers and
  tests;
- read-only commands and hooks do not rewrite legacy state.

Schema-1 migration first reuses the existing deterministic v1→v2 normalization,
then applies v2→v3.

### v2→v3 mapping

- Preserve all existing common fields and workflow revision.
- Add `protocol_version=1.2`.
- Add `contract` and `evidence` artifact keys with `null`.
- Active or paused workflows receive:
  - `mode=unbound`;
  - `status=reconcile_required`;
  - scope/baseline `reconcile_required`;
  - pending coverage and verdicts.
- Complete or cancelled workflows receive:
  - `mode=legacy_terminal`;
  - `status=not_required`;
  - no reopening, new acceptance failure, or hook output.

### First persistent v3 write

After the candidate state has fully validated, but before replacing current
state, archive the exact validated legacy JSON under:

```text
.littlepowers/archive/<timestamp>-<workflow>-r<revision>-pre-schema3-v<schema>.json
```

Then write schema 3 atomically. A failed candidate validation creates no backup
or state change. If backup succeeds but the final atomic replace fails, current
legacy state remains intact and the extra backup is harmless.

Migration is idempotent because schema-3 state has no legacy metadata and never
creates another pre-schema3 archive.

### Rollback

A 1.1 runtime cannot read a current schema-3 ledger. Rollback documentation will
require:

1. stop/pause writers;
2. preserve the current schema-3 file separately;
3. select the matching `pre-schema3` archive by workflow ID and revision;
4. restore it as `.littlepowers/state.json` through a safe explicit file
   operation;
5. restart the older host task/session.

No automatic downgrade or destructive repository command is added.

## Self-hosted upgrade

This repository's current workflow is schema 2 and the loaded Codex task uses the
installed 1.1 state CLI. During implementation:

- continue live ledger checkpoints with that installed absolute CLI;
- exercise edited schema-3 code only against temporary test roots;
- do not point the half-edited source CLI at this repository's live ledger;
- after the integrated candidate passes and the Outcome Contract/Plan Map
  artifacts exist, test migration on a copied ledger;
- migrate and bind the live project ledger only at the explicit integration
  boundary.

This prevents a partial implementation from stranding its own recovery state.

For this one bootstrap workflow, create a dedicated machine projection under
`docs/littlepowers/contracts/2026-07-26-outcome-lock.md` from the already
approved OUT-001…OUT-023 specification. Future lean/full/compact workflows embed
the contract block directly in their existing approved artifact and do not add a
separate planning phase.

## Failure and invalidation rules

- Rebinding a contract invalidates plan coverage and all verification summaries.
- Revalidating a changed Plan Map invalidates verification summaries.
- Recording changed verification replaces the previous summary atomically.
- Drift never adopts new content and blocks execute/verify readiness.
- A non-empty delta without the distinct approval flag remains pending.
- Missing tools or evidence remain blocked, never `not_applicable`.
- External blockers do not modify Outcome disposition.
- Pausing/cancelling never converts failure into completion.
- Unknown future schema, protocol, or record versions fail closed.
- Error text includes IDs and reason codes, not source content.

Retry behavior remains caller-driven. A revision conflict requires reload; the
CLI does not retry a stale mutation.

## Security and privacy

- Preserve the current `.littlepowers` ownership, permissions, ignore, lock,
  atomic-write, hard-link, symlink, reparse-point, and root-swap defenses.
- Treat all contract, plan, verification, parent, baseline, and implementation
  files as untrusted project data.
- Never execute commands from structured evidence or Markdown.
- Hash bytes only; do not copy source/evidence contents into state or hook
  context.
- Approval fields are local audit claims and must not be described as signatures
  or authenticated user identity.
- Keep state below 64 KiB by storing hashes/counts instead of titles and rows.

## Skill and documentation changes

### v1.1.1-compatible wording

- `executing-plans` consistently names all three verdicts.
- Router, planning, execution, review, and verification explicitly say:
  product-scope slicing is forbidden; rollback units, checkpoints, dependency
  checkpoints, rollback units, and small commits are expected inside one
  continuous implementation stream.
- Legacy active workflows must reconcile before implementation continues, while
  clearly identifying this as a prompt-level guard until schema 3 is loaded.

### v1.2 protocol use

- `using-littlepowers` resolves and uses the new lock commands at phase
  boundaries.
- Brainstorm/spec/shape skills emit the Outcome Contract block.
- Plan skill emits the Plan Map and validates it before execute.
- Execution refuses non-ready lock state without reopening settled design.
- Review produces three verdicts and Outcome/FID evidence.
- Verification writes the Verification Record, calls
  `record-verification`, and calls `complete` only after the aggregate gate.
- Managing skill reports last-known lock state and distinguishes it from a fresh
  digest check.

Descriptions remain concise; detailed record grammar moves to one shared
reference loaded only by the applicable phase skills. This avoids duplicating a
large schema across eleven skill bodies.

## Verification design

### Rollback unit A — parser and pure evaluator

Focused tests cover:

- duplicate JSON keys and record blocks;
- ID, enum, count, and size bounds;
- canonical semantic digests;
- scope contradiction and rebind set differences;
- coverage missing/unknown/evidence errors;
- fidelity and verdict consistency.

### Rollback unit B — secure hashing and migration

Focused tests cover:

- explicit regular files;
- outside-root, hidden, symlink, reparse, hard-link, special, missing, changed,
  and oversized files;
- total-byte limits;
- v1/v2 active, paused, complete, and cancelled migration;
- exact pre-schema3 archive creation;
- no archive or state write on failed mutation;
- idempotent later writes.

### Rollback unit C — command transition gates

Focused tests cover the complete transition matrix, optimistic concurrency,
invalidation, direct lock, legitimate blocked evidence, and the all-failures
completion report.

### Rollback unit D — hooks and skills

Focused tests prove:

- hook output uses stored summaries;
- parent and evidence readers are not called by render/hook paths;
- direct/lean/full routing remains proportional;
- legacy reconciliation and rollback-unit wording is present;
- three-verdict language is consistent.

### Aggregate boundary

After the independently reversible units integrate:

- full Python unittest suite once;
- Python compile checks;
- all skill validators;
- Codex plugin validator;
- Claude Code strict validation;
- Qoder validation;
- OpenCode syntax validation;
- diff/status inspection;
- Windows CI for serialization, launchers, migration, and atomic behavior.

No broad suite is required after every isolated edit.

## Requirement-to-design mapping

| Requirement | Design path |
| --- | --- |
| OUT-001 | Schema 3 and exact validation |
| OUT-002 | Secure explicit-file reader and contract sources |
| OUT-003 | Tagged Outcome Contract and approval command |
| OUT-004 | Semantic/source digests and `check-contract` |
| OUT-005 | v2→v3 migration plus reconciliation transition rules |
| OUT-006 | Plan Map evaluator and `validate-plan` |
| OUT-007 | Outcome dispositions, rebind comparison, distinct delta flag |
| OUT-008 | Contract baseline rules and source provenance |
| OUT-009 | Contract FID inventory plus Verification Record |
| OUT-010 | Three independent persisted verdict summaries |
| OUT-011 | Aggregate completion evaluator |
| OUT-012 | Untracked direct bypass and `--direct-lock` |
| OUT-013 | Contract in brainstorm and map in plan |
| OUT-014 | Contract in spec and one reused Outcome set |
| OUT-015 | Skill wording, rollback-unit plan fields, scoped verification |
| OUT-016 | Explicit command and transition matrix |
| OUT-017 | Existing lock/revision transaction extended around pure evaluation |
| OUT-018 | Read-only migration view and pre-schema3 archive |
| OUT-019 | Stored compact recovery object |
| OUT-020 | Standard library, bounded explicit reads, no background work |
| OUT-021 | One shared CLI/hook and cross-host validation |
| OUT-022 | Behavioral rollback-unit test suites |
| OUT-023 | Aggregate validation and evidence-limited release claims |

## Known boundary

The hard gates enforce the integrity of an approved, explicit Outcome Contract.
They cannot determine whether the first human/model projection from arbitrary
free-form PRD prose was semantically complete. Existing brainstorm/spec review
is therefore the one semantic approval boundary; schema 3 then prevents later
plans, evidence, old workflows, or completion reports from silently shrinking
that approved set. The Plan Map likewise proves that every approved ID has a
declared task and evidence reference; it does not semantically prove that the
surrounding task prose is an adequate implementation. Plan review and fresh
verification remain responsible for that judgment.
