# Outcome Lock under protocol 1.3

Read this reference only when creating, binding, mapping, reconciling, or
verifying a tracked Outcome Lock workflow. The state CLI is the authority for
syntax and deterministic transitions.

## Core rules

- Bind only explicit project-relative files. Do not scan the repository,
  sibling worktrees, transcripts, or the network.
- Bind only stable acceptance inputs for the lifetime of the workflow. Never
  bind a planned write target: any file that the approved plan is expected to
  modify. Tests, fixtures, generated screenshots, run cards, and implementation
  evidence stay outside
  `sources` when this workflow will update them. If the latest user request has
  no stable parent file, use an empty source list and express the complete
  reviewed request through the Outcome records instead of inventing a mutable
  source.
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
  --approval-kind <review-gate|implementation-mandate|window-expired|unattended-authorization> \
  [--approve-scope-delta]
```

Use `--approve-scope-delta` exactly when the highlighted delta is non-empty.
The approval kind must match the persisted successful Review Gate resolution
for this exact artifact key, original path, byte digest, and explicit
source-digest set. A successful bind consumes that boundary authorization once.

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

The command fails atomically when the plan lacks an unconsumed matching
successful Review Gate resolution, an active ID is missing, an
unknown/ineligible ID is mapped, evidence is absent, the contract drifted, or
the delta lacks distinct approval. Successful validation consumes that exact
Plan boundary once; execution checks the recorded consumption instead of
reusing the authorization.

## Verification input freshness (1.4.2)

After the last implementation edit and BEFORE running the checks, capture the
explicit input scope with the read-only helper. Include implementation, tests,
configuration and local dependencies that can affect the claimed outcome:

```bash
<python> <state-cli> --root <project-root> verification-inputs \
  --file src/module.py --file tests/test_module.py --absent removed_module.py
```

Copy the returned object unchanged into the Verification Record's `inputs`
field. Run the declared checks after capture, then record their commands, scope,
exit status and observed signals. Do not recapture merely to silence drift:
recapture after repairs, rerun the affected checks, and record a new receipt.
The runtime compares inputs both at `record-verification` and at `complete`,
including completed-state atomic writes. A rejected write leaves status and
revision unchanged. Recording does not silently adopt current input hashes.

The object has `mode`, `files`, and `manual_reason`. In `files` mode, `files`
is a nonempty list of `{ "path": "src/module.py", "sha256": "sha256:<64 hex>" }`
rows and `manual_reason` is null. A null `sha256` explicitly asserts that the
path must be absent, including after a planned deletion. A missing `--file`
fails; it is never implicitly converted to absence. A directory, symlink,
linked parent, hard-linked readable file, or unsafe path is rejected. Existing
workspace-file rules apply: normalized relative paths, no hidden components,
no traversal or escape. At most 256 paths, 16 MiB/file and 64 MiB total are read.
Inputs unsupported by these path rules are not silently covered: state the
limitation and do not claim full file freshness for that scope.

For a genuinely manual outcome with no project-file candidate, use:

```bash
<python> <state-cli> --root <project-root> verification-inputs \
  --manual-reason "Review external operating procedure; no project files implement this outcome"
```

This yields `mode=manual`, no files, and a required nonempty justification.
Manual scope is a coordinator assertion, not an exemption for code changes.
Do not include the Verification Record itself, the input snapshot output,
ledger files or generated logs among the input files: these are written after
capture. Store a snapshot outside the declared scope. Explicit fidelity output
files remain separately hashed by the existing fidelity mechanism.

These hashes protect only declared bytes and absence. They do not prove checks
ran or passed, capture every dependency/environment variable, detect undeclared
changes, cover file modes, or prevent changes after the last observation. The
coordinator owns scope completeness, pre-check ordering and honest evidence;
a same-account writer can fabricate claims. No automatic scan or Hook hashing
is added.

### Existing verification receipts

Schema 4 and protocol 1.3 remain unchanged. Records without `inputs` still parse
for recovery and historical inspection, but cannot be newly recorded or used
to complete work. After upgrading at a fresh session boundary, retain the
approved outcome/plan, capture inputs, rerun relevant checks, add the explicit
scope, and call `record-verification` again. Never bless old evidence by adding
current hashes after the fact. Legacy terminal ledgers remain readable; rewriting
a completed state must meet the fresh gate. Older runtimes reject the new record
field; do not mix runtime versions within an active workflow.

A current plan/shape must also still match its consumed Review Gate's original
path, exact approved bytes (including prose outside JSON), and current embedded
Contract sources at execution, recording and completion. Re-approval follows
the normal planning boundary; do not revalidate changed bytes implicitly.

## Verification Record

Include exactly one block. Insert the pre-check helper output as `inputs` in
this record before recording it; the remaining verdict structure is:

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
- Every tracked objective is locked in place. If it changes, use
  `start --replace` with the current workflow ID and revision; no checkpoint
  may carry prior Review Lease authority into a new objective.
- Active or paused schema-1/schema-2/schema-3 workflows load as schema 4;
  older workflows without a bound Outcome Contract remain
  `reconcile_required`. Bind the current approved contract and validate its
  current Plan Map before execution progress.
- A planning Review Gate is resolved before its boundary owner binds a
  Contract or validates a Plan Map. An automatic Review Lease never supplies
  `--approve-scope-delta`; distinct delta approval remains mandatory.
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
ledger. A 1.2 runtime cannot read a schema-4 ledger, so stop writers and restore
the byte-identical matching `pre-schema4` archive before any runtime rollback.

## Bounded runtime

The protocol uses only Python's standard library. Each protocol Markdown file
is limited to 128 KiB. An explicit parent or evidence file is limited to 16 MiB,
with a 64 MiB total per check. There is no background process in the Outcome
Lock path, automatic broad test run, model call, telemetry, recursive discovery,
or network access. Review Lease may create one explicitly authorized host
callback or one-shot Claude sleeper; neither runs from hooks or changes Outcome
Lock authority.
