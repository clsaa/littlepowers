# Outcome Lock brainstorm

Date: 2026-07-26

## Problem

Littlepowers 1.1 describes parent-contract inheritance, scope deltas, approved baselines, and separate review verdicts, but most of those guarantees live only in skill prose. The state CLI cannot tell whether:

- the active plan still covers the approved parent outcome;
- an older workflow was narrowed before the current protocol existed;
- an approved PRD, prototype, interaction spec, or contract changed after planning;
- an implementation-generated fixture was substituted for a user-approved baseline;
- a technically passing work unit is being reported as the complete product outcome.

The observed failure is therefore not missing instructions alone. An agent can implement and review a narrower child contract correctly while the durable ledger has no machine-checkable evidence that the parent outcome was lost.

## Scope anchor

### Approved outcome and parent acceptance sources

The approved outcome is a lightweight, cross-host Littlepowers protocol that durably binds the requested outcome and rejects silent scope shrinkage without becoming a second orchestrator.

Highest-authority sources, in order:

1. the latest user approval to implement the proposed Outcome Lock iteration;
2. the user constraints already carried by this project: proportional planning, no agent-created product slices, rollback-scoped testing, durable recovery, and low overhead on strong models;
3. `docs/littlepowers/specs/2026-07-26-scope-integrity-lean-route.md`;
4. `docs/littlepowers/designs/2026-07-26-scope-integrity-lean-route.md`;
5. `AGENTS.md` and the public cross-host compatibility contract.

### Inherited behaviors

- Keep direct work direct and small bounded work on brainstorm → plan → execute.
- Keep full planning for material architecture, security, migration, cross-system, irreversible-state, or costly-rollback decisions.
- Preserve one approved product outcome; one continuous implementation stream may use tasks, checkpoints, rollback units, and small commits without creating smaller definitions of done or staged deliveries.
- Keep hooks read-only, silent without active state, network-free, transcript-free, and cheap.
- Keep the runtime dependency-free beyond Python 3 and first-class on Codex, Claude Code, Qoder, and OpenCode.
- Keep the root coordinator as the only ledger writer.
- Test according to the changed rollback unit, then run the broad suite once at the aggregate release boundary.

### Scope delta

No scope delta.

The approved iteration intentionally adds reconciliation for active legacy workflows and deterministic completion checks. A legacy workflow may pause before further execution when its parent outcome cannot be proven; that is the requested safety behavior, not a deferral or removal.

### Baseline provenance

- Protocol compatibility baseline: the released `v1.1.0-alpha.1` route behavior, schema-2 recovery fixtures, and four-host validation surfaces.
- Outcome baseline for a consuming project: only user-approved or explicitly authorized PRDs, specifications, interaction flows, prototypes, screenshots, API contracts, migration contracts, and acceptance lists.
- Implementation-generated screenshots, snapshots, fixtures, or manifests remain regression evidence only and cannot establish approved-outcome fidelity.

## Constraints

- Add no model calls, reviewer agents, daemon, telemetry, transcript access, repository-wide background scan, or automatic broad test run.
- Hash only explicitly bound artifacts at explicit transitions, recovery checks, and completion checks.
- Keep hook output to one compact recovery summary; do not parse full contracts in hooks.
- Migrate schema 2 deterministically. Completed workflows remain readable; active workflows that cannot prove their contract become `reconcile_required` rather than silently continuing.
- Use stable outcome identifiers so coverage can be checked without adding YAML or third-party parser dependencies.
- Do not treat rollback units, checkpoints, or small commits as forbidden scope slices.

## Options

### 1. Add stronger prompt wording only

Smallest code change, but it repeats the 1.1 failure mode: correctness depends on the current model remembering prose across compaction and old sessions. Rejected.

### 2. Add a separate orchestration service or rich contract database

Could enforce detailed workflow state, but adds latency, dependencies, host coupling, and a competing planner. Rejected.

### 3. Extend the existing local ledger with a deterministic Outcome Lock

Selected. Add a schema-3 contract record, stable outcome coverage, explicit baseline provenance, digest drift detection, legacy reconciliation, and hard completion gates to the existing Python state CLI. Skills remain the policy and explanation layer; the CLI enforces only the small set of invariants that must survive interruption.

## Selected direction

1. **Contract Bind Gate:** bind explicit parent artifacts and their digests; never discover acceptance sources by scanning the repository.
2. **Outcome Coverage Gate:** use stable `OUT-###` identifiers in a compact Markdown contract and require the plan to map every active outcome to a task and evidence.
3. **Scope Delta Gate:** record `none`, `approved`, or `reconcile_required`; an omitted or deferred outcome cannot be hidden behind `No scope delta`.
4. **Baseline Gate:** record approved baseline provenance separately from implementation regression evidence.
5. **Legacy Reconciliation Gate:** schema-2 active workflows migrate safely but cannot execute or complete until the parent contract is explicitly rebound; terminal workflows remain terminal.
6. **Fidelity and Completion Gates:** distinguish work-unit compliance, approved-outcome fidelity, and code quality; completion requires full active-outcome coverage, approved scope delta, acceptable baseline status, and passing outcome fidelity.
7. **Lightweight host integration:** hooks display only a compact lock status. Contract parsing and hashing happen only when a coordinator explicitly binds, checks, transitions, or completes a workflow.

The contract format will be Markdown-first and dependency-free. Stable outcome lines and plan mappings will have a deliberately small grammar that the CLI can validate deterministically; human explanation remains ordinary Markdown.

## Decision rationale

The selected direction closes the actual failure boundary—the durable state did not know what was approved—while preserving Littlepowers as a thin protocol. It adds no competing reasoning loop and no background work. Strong models retain freedom over implementation; the state layer only prevents them from silently changing the requested outcome or declaring completion without coverage.

## Assumptions

- Explicit artifact paths are sufficient because Littlepowers already requires the coordinator to identify the highest-authority sources.
- SHA-256 from Python's standard library is adequate for drift detection; this is integrity evidence, not authentication.
- Outcome identifiers are local to one bound contract and need not form a global registry.
- A direct tiny task may remain untracked. A tracked direct task can bind a minimal contract without creating spec or design artifacts.

## Open questions

No product-direction question remains. The specification must settle the exact state fields, Markdown grammar, migration behavior, and command transition matrix before implementation.

## Measurable success

- A child plan that omits a parent `OUT-###` cannot pass coverage or complete even if its own tests are green.
- `No scope delta` cannot coexist with omitted or unapproved deferred outcomes.
- An active schema-2 execution workflow migrates to `reconcile_required`; a completed schema-2 workflow stays completed and readable.
- Changing an explicitly bound parent artifact marks the contract `drifted` at the next explicit check.
- An implementation-generated UI artifact cannot satisfy an approved-baseline requirement.
- Completion is rejected until coverage, scope delta, baseline, work-unit, outcome-fidelity, and blocking-evidence conditions pass.
- Direct tiny work remains free of mandatory artifacts, hooks remain cheap, and all four host validators continue to pass.
- Focused tests validate each changed rollback unit; the full suite runs once for the integrated candidate.
