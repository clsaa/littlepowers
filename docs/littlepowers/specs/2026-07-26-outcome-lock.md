# Outcome Lock specification

Date: 2026-07-26

Status: approved

## Purpose

Upgrade Littlepowers from prompt-only scope guidance to a lightweight, durable protocol that can deterministically detect contract drift, incomplete outcome coverage, invalid scope declarations, unverified approved baselines, and false completion claims.

The complete outcome is the `v1.2.0-alpha.1` Outcome Lock behavior. A `v1.1.1` wording-only backport may be published first, but it is a compatibility checkpoint rather than a smaller definition of done.

## Scope anchor

### Approved outcome and parent acceptance sources

The approved outcome is defined by:

1. the user's 2026-07-26 review conclusion and five proposed deterministic gates;
2. `docs/littlepowers/brainstorms/2026-07-26-outcome-lock.md`;
3. `docs/littlepowers/specs/2026-07-26-scope-integrity-lean-route.md`;
4. `docs/littlepowers/designs/2026-07-26-scope-integrity-lean-route.md`;
5. `AGENTS.md`, including proportional workflow, four-host support, dependency-free runtime, read-only hooks, single ledger writer, and rollback-scoped verification.

### Inherited behaviors

- Preserve direct, lean, compact, and full planning routes.
- Preserve one complete approved product outcome across one continuous implementation stream.
- Preserve exact-project-root binding, revision conflicts, secure artifact access, pause/cancel/handoff semantics, and terminal-state integrity.
- Keep Littlepowers subordinate to the host harness; add no competing planner or reasoning loop.
- Keep Codex, Claude Code, Qoder, and OpenCode behavior aligned.

### Scope delta

No scope delta.

Legacy reconciliation, deterministic completion checks, and contract drift blocking are part of the approved iteration. They intentionally make some formerly accepted state transitions fail until the approved outcome is rebound.

### Approved baseline provenance

- Protocol compatibility baseline: released `v1.1.0-alpha.1` route behavior, schema-2 fixtures, state security rules, hook behavior, and four-host validation surfaces.
- Requirement baseline: the user's explicit review conclusion plus the approved Outcome Lock brainstorm.
- Consuming-project baseline: only user-approved or explicitly authorized PRDs, specifications, interaction flows, prototypes, screenshots, API contracts, migration contracts, and acceptance lists.
- Implementation-generated fixtures, snapshots, screenshots, and manifests are regression evidence only.

## Users and callers

- The root coordinator that owns one Littlepowers ledger.
- A human approving planning artifacts or a highlighted scope delta.
- The shared Python state CLI used by all supported hosts.
- Read-only session-start hooks that surface recovery status.
- Review and verification skills that record evidence and verdicts.
- Existing projects with schema-1 or schema-2 ledgers.

## Definitions

- **Parent acceptance source:** an explicitly named, highest-authority file whose contents define requested behavior or compatibility.
- **Outcome Contract:** the approved, Markdown-first inventory of observable outcomes represented by stable `OUT-###` identifiers.
- **Active outcome:** an outcome that remains in the approved definition of done.
- **Outcome mapping:** one active outcome linked to at least one implementation task and at least one named verification evidence type.
- **Scope delta:** explicit Added, Changed, Deferred, or Removed outcomes and the recorded status of their approval.
- **Approved baseline:** a user-approved or explicitly authorized visual, interaction, output, or compatibility source.
- **Regression evidence:** an implementation-generated artifact that may detect later change but cannot prove fidelity to an approved baseline.
- **Contract drift:** a mismatch between a currently readable explicit source and the digest recorded when it was bound.
- **Reconciliation:** rebinding the active workflow to its current parent sources, rebuilding its outcome coverage, and resolving any scope delta before valid execution continues.
- **Tracked direct work:** direct-route work with a ledger because interruption recovery is useful.
- **Product slice:** a narrower definition of done created from an approved outcome. Dependency order, rollback units, checkpoints, and small commits are not product slices.

## Required durable state

### OUT-001 — Protocol identity

Every schema-3 ledger exposes a protocol version identifying the Outcome Lock contract. The initial protocol version is `1.2`.

Acceptance:

- New ledgers report state schema 3 and protocol version `1.2`.
- Migrated ledgers preserve their workflow ID, timestamps, phase, status, artifacts, progress, and completed history unless a migration rule below explicitly changes a lock field.
- Unknown future schema or protocol versions fail closed with an actionable error and no state mutation.

### OUT-002 — Explicit parent-source binding

A locked workflow records only explicitly supplied parent acceptance sources. For each file source, recovery data can identify its normalized project-relative path, role, and SHA-256 digest.

Acceptance:

- Binding never discovers files through a recursive repository, sibling-worktree, transcript, or network scan.
- Paths outside the exact project root, non-regular files, unsafe links, oversized inputs, missing files, duplicate source declarations, and malformed roles are rejected.
- A failed bind leaves the prior ledger and revision unchanged.
- The coordinator can inspect the bound source list without reading full source contents into hook output.

### OUT-003 — Approved Outcome Contract

Lean and full workflows bind a reviewed Outcome Contract before entering valid execution. Stable `OUT-###` identifiers are unique within that contract.

Acceptance:

- Duplicate, malformed, or empty outcome inventories are rejected.
- Full-route specifications reuse their approved Outcome IDs in design and plan.
- Lean-route brainstorms contain or reference one compact Outcome map; no separate specification or design is added.
- A contract generated from free-form parent documents is not treated as semantically approved until its existing route review gate is approved.
- Reordering prose without changing an outcome's normalized contract record does not create a false omission; changing a bound source still triggers the drift rule in OUT-004.

### OUT-004 — Contract digest and drift status

The ledger exposes contract status at least equivalent to `bound`, `drifted`, and `reconcile_required`.

Acceptance:

- Explicit contract checks at the defined lifecycle boundaries recompute only recorded source digests.
- A changed, missing, replaced, or newly unsafe bound source makes the contract non-executable and records an actionable reason.
- Drift never silently updates the recorded digest.
- Returning to `bound` requires explicit reconciliation; merely rerunning a check cannot approve new content.

## Deterministic gates

### OUT-005 — Legacy Reconciliation Gate

An active or paused schema-1/schema-2 workflow cannot claim valid schema-3 execution or completion until its approved outcome has been reconciled.

Acceptance:

- An active legacy workflow in `execute` or `verify` becomes `reconcile_required` when first handled by the schema-3 protocol.
- Planning and reconciliation operations needed to repair the workflow remain available, but execution-progress checkpoints, verification completion, resume into executable work, and handoff-as-ready are rejected while reconciliation is incomplete.
- A paused workflow stays paused until an authorized resume; migration does not infer resume permission.
- Complete and cancelled legacy workflows remain terminal and readable without being reopened or falsely marked incomplete.
- Existing open Codex, Claude Code, Qoder, or OpenCode sessions are explicitly documented as unable to hot-load a replacement plugin; the new gate is guaranteed only after a new task/session boundary loads the new runtime.

### OUT-006 — Outcome Coverage Gate

Before entering `execute`, every active Outcome ID maps to at least one task and at least one named evidence type.

Acceptance:

- Coverage reports the original total, active total, mapped active count, approved deferred count, approved removed count, unknown mappings, and pass/fail status.
- Coverage passes only when every active outcome is mapped and no mapping references an unknown outcome.
- A plan covering 12 of 30 active outcomes is rejected even when its local tasks and tests are valid.
- One task may cover several outcomes and one outcome may map to several tasks; coverage is evaluated by Outcome ID, not task count.
- A mapping with a task but no evidence type is incomplete.
- Failed coverage validation leaves the workflow at the prior phase and revision.

### OUT-007 — Deterministic Scope Delta Gate

The ledger distinguishes `none`, pending reconciliation, and explicitly approved non-empty scope delta states.

Acceptance:

- `No scope delta` is valid only when all parent Outcome IDs remain active and no Changed, Deferred, or Removed record exists.
- Added outcomes become active and must be mapped.
- Changed outcomes identify the affected Outcome IDs and require the currently bound contract to be approved again.
- Deferred or Removed outcomes are excluded from the active denominator only after the highlighted non-empty delta is explicitly approved.
- Generic approval of an artifact does not count as scope-delta approval unless the delta was distinctly presented.
- Approval records are audit claims made by the coordinator, not cryptographic proof of user identity; documentation must not claim authentication.

### OUT-008 — Approved Baseline Gate

Visual, interaction, output-format, and compatibility work records whether an approved baseline is required, bound, verified, failed, blocked, or not applicable.

Acceptance:

- A required baseline names at least one approved source and its provenance.
- Implementation-generated evidence cannot be registered as an approved baseline.
- A baseline may be `not_applicable` only when the Outcome Contract contains no requirement whose fidelity depends on a visual, interaction, output-format, or compatibility source.
- Missing or unverified required baselines block approved-outcome fidelity and completion.
- Baseline source drift follows OUT-004.

### OUT-009 — Fidelity Matrix Gate

When an approved baseline is required, the workflow carries a deterministic inventory of required page/output × action × state comparisons and their evidence result.

Acceptance:

- Every required comparison has a stable identifier, associated Outcome ID, approved baseline reference, expected state, implementation evidence reference, and result.
- Missing evidence, an unknown Outcome ID, an implementation-only baseline, an evidence path identical to its approved baseline source, or a non-passing required comparison makes approved-outcome fidelity `blocked` or `fail`.
- Passing work-unit checks may coexist with blocked or failed approved-outcome fidelity; the two statuses never overwrite one another.
- Non-UI compatibility work can use the same comparison model for API shape, migration state, generated output, or host behavior.

### OUT-010 — Independent review verdicts

Review state and reports keep three independent verdicts:

1. work-unit compliance;
2. approved-outcome fidelity;
3. code quality.

Acceptance:

- Each verdict has an explicit status and may carry evidence references or a blocking reason.
- A passing work unit cannot imply outcome fidelity.
- Code quality wording is consistently three-verdict language across planning, execution, review, verification, and documentation.
- When material review is required, `request changes` or `blocked` code quality prevents readiness or release claims even if outcome coverage passes.

### OUT-011 — Completion Gate

A tracked Outcome Lock workflow can become `complete` only from verification with all required lock conditions satisfied.

Acceptance:

- Active-outcome coverage is 100%.
- Scope delta is `none` or explicitly approved.
- Required approved baseline and fidelity comparisons pass, or baseline is validly not applicable.
- Work-unit compliance is `pass`.
- Approved-outcome fidelity is `pass`.
- Required code-quality review is `approve`.
- Blocking evidence count is zero.
- Contract status is `bound` and an explicit final drift check succeeds.
- Failure of any one condition reports every currently failing condition, preserves `phase=verify`, and leaves the revision and status unchanged.

## Proportional workflow requirements

### OUT-012 — Direct-route proportionality

Tiny, fully specified direct work may remain untracked and incurs no Outcome Lock artifact or CLI work.

Acceptance:

- Littlepowers does not force a ledger, contract file, spec, or design onto untracked direct work.
- Tracked direct work may use its normalized objective as a one-outcome lock without a separate planning artifact.
- A tracked direct workflow still cannot claim completion without named evidence for its locked objective.

### OUT-013 — Lean-route proportionality

Lean work remains brainstorm → plan → execute.

Acceptance:

- The approved brainstorm supplies the compact Outcome inventory and scope/baseline declarations.
- The plan supplies Outcome-to-task-and-evidence mappings.
- No retroactive specification or design artifact is required.
- Gate checks add deterministic local parsing and hashing, not another model call or review agent.

### OUT-014 — Full-route reuse

Full work remains brainstorm → spec → design → plan → execute and reuses one Outcome ID set.

Acceptance:

- The approved specification owns the Outcome IDs.
- Design may refine solution decisions but cannot delete or redefine an Outcome ID.
- The plan maps all active IDs without generating a narrower replacement contract.
- Tasks remain implementation order and rollback boundaries only; they are not staged deliveries.

### OUT-015 — Product scope versus rollback units

Littlepowers explicitly distinguishes forbidden product-scope slicing from required engineering rollback control.

Acceptance:

- Skills state that “no product slices” does not prohibit independently reversible changes, checkpoints, or small commits.
- Plans identify rollback units and coupling.
- Focused checks cover each changed rollback unit.
- The broad suite runs once when the integrated schema, hook, packaging, cross-host, or release boundary requires it, rather than after every small edit.
- Partial rollback-unit success cannot complete the approved product outcome.

## Lifecycle and recovery behavior

### OUT-016 — Explicit check boundaries

Bound source digests and deterministic gates run only when their result is needed.

Required boundaries:

- contract bind or rebind;
- transition into `execute`;
- explicit resume toward executable work;
- handoff or readiness snapshot that represents executable work;
- transition to or within `verify` when evidence is recorded;
- final completion.

Acceptance:

- Ordinary prompts and read-only hook rendering do not hash or parse parent artifacts.
- An explicit status command may show the last known lock state without claiming freshness.
- An explicit contract-check operation can refresh drift status without changing approval.

### OUT-017 — Transactional errors and concurrency

Outcome Lock preserves optimistic concurrency and fail-closed mutation.

Acceptance:

- Every mutation still requires workflow ID and expected revision.
- A stale writer, malformed contract, incomplete coverage, drift, invalid approval, or failed completion gate produces a non-zero result and no partial state update.
- Error output names actionable failing Outcome IDs or gate conditions without dumping full sensitive source contents.
- The root coordinator remains the only ledger writer; delegated workers return mappings and evidence but do not mutate the parent ledger.

### OUT-018 — Recoverable migration and rollback

The first persistent schema-3 migration of an existing ledger creates a recoverable pre-migration snapshot before replacing current state.

Acceptance:

- Migration is deterministic and idempotent.
- A migration failure preserves the original schema-1/schema-2 state.
- The backup is local, excluded from normal source control, bounded by existing ledger security limits, and named so the source workflow and revision can be identified.
- Rollback guidance states that a schema-2 runtime cannot read a schema-3 current ledger and identifies the explicit restore path; no automatic downgrade is implied.
- Migration does not access sibling worktrees or an ancestor ledger.

## Hook, performance, privacy, and security

### OUT-019 — Compact read-only hook summary

When active state exists, hooks may add one compact lock summary equivalent to:

```text
contract=bound coverage=23/23 baseline=bound fidelity=pending
```

Acceptance:

- Hooks remain silent when no active state exists.
- Hooks read only local ledger recovery data and do not read, parse, stat, or hash bound contract/baseline sources.
- Hook output is bounded and does not include full source paths, outcome descriptions, approval prose, or evidence contents.
- Hook failures remain non-blocking and do not mutate the ledger.

### OUT-020 — Bounded, dependency-free runtime

Acceptance:

- Runtime uses only Python 3 standard-library functionality already permitted by the project.
- No telemetry, network access, transcript access, daemon, background scanner, automatic test runner, model selection, reasoning-effort selection, reviewer creation, or additional model call is introduced.
- Contract work is proportional to explicitly bound file bytes and declared Outcome/mapping rows, never repository size.
- Existing state and artifact size limits remain enforced or are replaced only by equally explicit bounded limits.
- Strong models remain free to reason and implement normally; the state layer evaluates identifiers, digests, declared statuses, and transition invariants rather than duplicating planning.

### OUT-021 — Cross-host consistency

Acceptance:

- Codex, Claude Code, Qoder, and OpenCode use the same state CLI behavior and skill contract.
- Host adapters add no host-specific planning semantics.
- Installation documentation states that a new task/session boundary is required to load an updated plugin.
- Host validation continues to cover manifest shape, hook launcher behavior, skill metadata, and supported-platform syntax.

## Verification requirements

### OUT-022 — Behavioral regression coverage

Tests must exercise state transitions and observable failures, not only skill wording.

Minimum deterministic cases:

1. a valid bound contract and complete mapping can enter execution;
2. a child plan omitting one parent Outcome ID is rejected;
3. `No scope delta` plus an omitted, deferred, changed, or removed Outcome ID is rejected;
4. approved defer/remove changes the active denominator and remains auditable;
5. an active schema-2 execution workflow becomes `reconcile_required`;
6. a complete schema-2 workflow stays complete and readable;
7. a changed or missing explicit parent source becomes `drifted`;
8. an implementation-generated artifact cannot satisfy an approved-baseline requirement;
9. one missing page/action/state comparison blocks fidelity;
10. completion is independently rejected for each unsatisfied gate;
11. a failed gate does not increment the revision or partially write state;
12. untracked direct work remains unaffected and tracked direct work stays minimal;
13. hook rendering performs no contract-source read or hash;
14. migration backup and restore guidance are valid;
15. Windows path serialization, command launchers, and atomic state behavior remain valid.

Static skill-text tests remain useful for trigger and host metadata consistency but cannot substitute for these behavioral cases.

### OUT-023 — Integrated verification and claim discipline

Acceptance:

- Focused tests run first for each independently reversible state, parser, hook, skill, and migration boundary.
- After integration, run the full Python suite, compilation, all skill validators, the Codex plugin validator, Claude strict validation, Qoder validation, OpenCode syntax validation, diff inspection, and repository status inspection.
- A release report states exactly which hosts and model runs were actually exercised.
- No authenticated GPT-5.6, Fable, or Opus behavior claim is made without a corresponding fresh run.
- Passing protocol tests may support model-agnostic compatibility, but not a claim that a particular model always follows free-form source semantics.

## Error and edge-case expectations

- Empty outcome descriptions, duplicate IDs, duplicate mappings, unknown IDs, invalid evidence kinds, and contradictory delta declarations fail with actionable messages.
- If the approved contract itself omitted a free-form parent requirement, deterministic coverage cannot infer that semantic omission. The route review gate must expose and approve the Outcome Contract; documentation must state this boundary instead of claiming perfect semantic enforcement.
- A user-authorized non-empty scope delta may change the active outcome set, but the prior set and approval claim remain auditable.
- External blockers do not silently become approved deferrals.
- If a required tool or baseline is unavailable, fidelity remains blocked; it is not converted to `not_applicable`.
- Contract and baseline digests provide change detection, not authorship authentication.

## Version delivery order

### `v1.1.1` compatibility backport

- Correct every two-verdict reference to the three independent verdicts.
- Add the explicit rule that prohibiting product slices does not prohibit rollback units, checkpoints, or small commits, while implementation remains one continuous stream.
- Require active legacy workflows to reconcile against parent acceptance sources before further execution, while clearly labeling this as a skill-level guard rather than a hard state gate.

This backport reduces risk but does not satisfy the Outcome Lock definition of done.

### `v1.2.0-alpha.1` complete candidate

- State schema 3 and protocol version 1.2.
- Contract Bind, Legacy Reconciliation, Coverage, Scope Delta, Baseline/Fidelity, and Completion deterministic gates.
- Recoverable schema migration, compact hook summary, cross-host skills/docs, and behavioral verification.

The two versions are delivery order only. The workflow remains incomplete until the complete candidate satisfies OUT-001 through OUT-023.

## Parent traceability

| Parent finding | Covered by |
| --- | --- |
| Parent contract absent from ledger | OUT-001–OUT-004 |
| Old workflow can continue without rebase | OUT-005, OUT-016, OUT-018 |
| Plan mapping is prompt-only | OUT-003, OUT-006, OUT-007 |
| UI baseline/evidence is unstructured | OUT-008, OUT-009 |
| Completion can report the wrong contract as green | OUT-010, OUT-011 |
| Tests mostly assert text presence | OUT-022, OUT-023 |
| “No slicing” may create giant rollback units | OUT-015 |
| Strong-model slowdown or orchestration conflict | OUT-012–OUT-014, OUT-019, OUT-020 |
| Cross-host and open-session compatibility | OUT-005, OUT-021 |

## Assumptions and known limits

- Stable identifiers and hashes can deterministically protect an approved contract after it is formed; they cannot semantically extract every requirement from arbitrary prose without human/model judgment.
- Existing brainstorm/spec review gates provide the approval point for the Outcome Contract, so no additional planning phase is introduced.
- The state CLI can reject protocol transitions and completion claims; it cannot physically prevent a user or unrelated process from editing source files outside the protocol.
- No product-direction question remains open. Exact command names, state nesting, Markdown row grammar, transition implementation, and backup filename belong to solution design.
