# Outcome Lock protocol 1.2

Read this reference only when creating, binding, mapping, reconciling, or
verifying a tracked Outcome Lock workflow. The state CLI is the authority for
syntax and deterministic transitions.

## Core rules

- Bind only explicit project-relative files. Do not scan the repository,
  sibling worktrees, transcripts, or the network.
- Keep one complete approved outcome. Tasks and checkpoints are implementation
  order and rollback boundaries, not smaller product outcomes or staged
  deliveries.
- Treat `Added`, `Changed`, `Deferred`, and `Removed` as one highlighted scope
  delta. Pass `--approve-scope-delta` only after distinct authorization.
- A user-approved requirements, interaction, prototype, screenshot, API,
  migration, output, or compatibility file may be a parent source. An
  implementation-generated fixture, screenshot, or snapshot is regression
  evidence, never an approved baseline.
- Approval flags are coordinator audit claims. They do not authenticate a user.
- Hooks render stored counts and verdicts only. They never refresh digests.

## Route ownership

| Route | Contract record lives in | Plan Map lives in |
| --- | --- | --- |
| tracked direct | inline objective created by `--direct-lock` | implicit one-outcome coverage |
| lean | approved brainstorm | approved plan |
| compact | approved shape | the same approved shape |
| full | approved specification | approved plan |

Full-route design reuses the specification's Outcome IDs. It does not create a
replacement contract.

## Outcome Contract

Include exactly one block:

````markdown
<!-- littlepowers:contract:v1 -->
```json
{
  "route": "lean",
  "sources": [
    {
      "id": "SRC-001",
      "path": "docs/product/PRD.md",
      "role": "requirements",
      "origin": "user",
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
    {
      "id": "OUT-001",
      "title": "The complete approved behavior is observable",
      "disposition": "active"
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->
````

Allowed values:

- route: `lean`, `compact`, `full`;
- source role: `requirements`, `interaction`, `prototype`, `screenshot`,
  `api`, `migration`, `compatibility`, `other`;
- source origin: `user`, `repository`, `external`, `implementation`;
- outcome disposition: `active`, `added`, `changed`, `deferred`, `removed`;
- scope status: `none`, `proposed`;
- baseline requirement: `required`, `not_applicable`.

Use stable `SRC-###`, `OUT-###`, and `FID-###` IDs. The limits are 64 sources,
200 outcomes, and 500 fidelity comparisons.

`scope_delta.status=none` requires only `active` outcomes and no consequences.
`proposed` requires at least one non-active disposition and one consequence.
`added` and `changed` stay in the active denominator. `deferred` and `removed`
leave it only after distinct delta approval.

A required baseline names at least one approved source whose origin is not
`implementation`. Add one Fidelity row per required surface/output × action ×
state comparison:

```json
{
  "id": "FID-001",
  "outcome": "OUT-001",
  "baseline": "SRC-002",
  "surface": "home",
  "action": "open",
  "state": "default"
}
```

On rebind, retain every old Outcome ID. Mark a removed ID `removed`, a new ID
`added`, and a changed normalized record `changed`. Rebinding invalidates the
stored Plan Map and Verification Record.

Bind an approved artifact:

```bash
<python> <state-cli> --root <project-root> bind-contract \
  --workflow <id> --expect-revision <revision> \
  --artifact <contract-artifact.md> \
  --approval-kind <review-gate|unattended-authorization> \
  [--approve-scope-delta]
```

Use `--approve-scope-delta` exactly when the highlighted delta is non-empty.

## Outcome Plan Map

Include exactly one block:

````markdown
<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 2"],
      "evidence": ["test:approved-behavior"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
````

Map every active Outcome exactly once. Do not map deferred or removed IDs. Each
mapping needs at least one task label and one evidence token. Evidence uses
`<kind>:<stable-label>` where kind is `test`, `inspection`, `visual`,
`interaction`, `manual`, `build`, `host`, `security`, `migration`, `review`, or
`other`.

Validate an approved plan or compact shape:

```bash
<python> <state-cli> --root <project-root> validate-plan \
  --workflow <id> --expect-revision <revision> \
  --artifact <plan-or-shape.md>
```

The command fails atomically when an active ID is missing, an unknown/ineligible
ID is mapped, evidence is absent, the contract drifted, or the delta lacks
distinct approval.

## Verification Record

Include exactly one block:

````markdown
<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": ["test:focused-suite"]
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
      "evidence": ["test:approved-behavior"]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
````

Every active Outcome appears once with `pass`, `fail`, or `blocked`. Every
required FID appears once and preserves its contract Outcome and baseline:

```json
{
  "id": "FID-001",
  "outcome": "OUT-001",
  "baseline": "SRC-002",
  "evidence_path": "artifacts/verification/home-default.png",
  "result": "pass"
}
```

The implementation evidence path must differ from the referenced approved
baseline source path; a baseline cannot prove fidelity to itself.

Keep the three verdicts independent:

- work-unit compliance: `pass`, `fail`, `blocked`;
- approved-outcome fidelity: `pass`, `fail`, `blocked`;
- code quality: `approve`, `request_changes`, `blocked`, or `not_required`
  when the contract says review is not required.

A valid failing or blocked record is durable recovery evidence; it does not
complete the outcome. A passing comparison requires readable explicit evidence.
An unavailable file may support a `blocked` comparison, never a pass.

Record verification only in active `phase=verify`:

```bash
<python> <state-cli> --root <project-root> record-verification \
  --workflow <id> --expect-revision <revision> \
  --artifact <verification.md>
```

The command freshly checks the contract, Plan Map, Outcome rows, FID rows,
explicit fidelity evidence, and aggregate verdict consistency.

## Lifecycle

- Start tracked direct work with `start --phase execute --direct-lock`; do not
  add a planning artifact. Visual, interaction, output-format, migration,
  security, or compatibility work needing a baseline or material review is not
  direct.
- The tracked direct objective is its locked Contract. If that objective
  changes, replace the workflow or reconcile through an approved artifact
  Contract; do not rewrite it with an execution checkpoint.
- Active or paused schema-1/schema-2 workflows load as
  `reconcile_required`. Bind the current approved contract and validate its
  current Plan Map before execution progress.
- `check-contract` records `bound` or `drifted` without adopting changed
  content. Only an explicit rebind adopts new digests.
- Entering `execute` or `verify` performs a fresh contract/plan check. Ordinary
  execute checkpoints use the stored gate summary; hooks do not hash files.
- Pause and cancel remain available when a gate fails. A planning retreat is
  allowed for reconciliation.
- `complete` freshly rechecks contract, plan, verification, baseline,
  evidence, three verdicts, and blockers. It reports all failures and leaves
  the revision unchanged unless every condition passes.

Use:

```bash
<python> <state-cli> --root <project-root> check-contract \
  --workflow <id> --expect-revision <revision>
```

after a drift report. Rebind changed approved content; do not edit the raw
ledger. A 1.1 runtime cannot read a schema-3 ledger, so preserve the matching
`pre-schema3` archive before any runtime rollback.

## Bounded runtime

The protocol uses only Python's standard library. Each protocol Markdown file
is limited to 128 KiB. An explicit parent or evidence file is limited to 16 MiB,
with a 64 MiB total per check. There is no background process, automatic broad
test run, model call, telemetry, recursive discovery, or network access.
