# Littlepowers 1.4 opt-in delegation shape

## Outcome

Add a lightweight, host-native Delegation Gate that keeps Littlepowers
single-agent by default, recommends subagents only for clearly independent and
high-value work, requires work-unit-specific user authorization before launch,
and gives Codex, Claude Code, and Qoder workers safe model, effort, ownership,
isolation, and verification boundaries without adding an orchestrator or an
ordinary-path model call.

## Evidence that shaped the change

- Recent multi-perspective product, UI, and architecture reviews found material
  omissions that one implementation stream and its focused tests had missed.
- Recent database-design and simulator/E2E work had unresolved contracts,
  shared ports, databases, devices, and mutable files; parallel mutation would
  have added coordination risk rather than shortened the critical path.
- Recent small cleanup work completed in minutes and would not have repaid the
  setup, context, integration, and review cost of another agent.
- Codex 0.147.0 exposes native multi-agent support and per-spawn model/reasoning
  controls, while some context-sharing modes require inherited settings.
- Claude Code 2.1.227 supports subagents with model/effort selection and
  worktree/background isolation. Agent Teams remains experimental, higher-cost,
  and appropriate only when workers genuinely need peer communication.
- Qoder CLI 1.1.19 supports native subagents, concurrency, worktrees, and
  model/effort settings, but Qoder IDE does not reliably expose every worker
  lifecycle Hook; therefore the task envelope cannot depend on Hook delivery.

## Selected approach

1. Preserve the current single-agent route. Evaluate delegation at most once
   after the outcome and plan are stable, after a reproducer yields at least two
   independent debugging hypotheses, or before a material multi-perspective
   review.
2. Recommend delegation only when at least two ready work packets have no
   ordering dependency, shared mutable files, or exclusive resources; each has
   an independently verifiable output; and critical-path or context-isolation
   benefit clearly exceeds coordination cost.
3. Veto delegation while product scope, architecture, or acceptance is
   unsettled; for sequential work; for same-file or shared-state mutation; for
   tiny/direct work; or for destructive and externally visible actions.
4. Present one compact proposal naming roles, host-native mechanism,
   model/effort policy, isolation, benefit, risk, and single-agent fallback.
   Do not launch until the user authorizes that exact work unit. A decline or
   unavailable native mechanism continues single-agent and is not repeatedly
   raised unless the plan changes materially.
5. Use only the current host's callable native delegation API. Never simulate
   workers with nested shell CLIs, Codex user-visible tasks, or silent host
   configuration changes.
6. Default every worker to the coordinator's model and effort. Override only
   when a bounded role has a clear quality/cost reason and the current native
   API supports the pair. Never choose maximum effort, Codex Ultra, or Claude
   Agent Teams automatically.
7. Keep the root coordinator as sole ledger writer, integrator, acceptance
   owner, and final verifier. Workers are leaf agents with bounded files and
   actions, no scope changes, no nested delegation, no commits/pushes/deploys,
   and no authority over destructive or external state.
8. Put detailed, rarely needed instructions in one progressive-disclosure
   reference. Keep the normal router and Hook path concise, read-only, local,
   and free of additional model calls, repository scans, daemons, or telemetry.

## Non-goals

- No automatic subagent launch, static host agent registration, autonomous
  model benchmark, provider-specific hard-coded model name, or global setting.
- No new Littlepowers planning phase, ledger schema, background scheduler,
  transcript parser, telemetry collector, or worker-owned ledger.
- No claim that every Codex, Claude Code, Qoder, or OpenCode build exposes the
  same controls. Unsupported controls fall back to inheritance and are
  reported honestly.
- No parallel broad test suites, deployment, release, database migration,
  device use, or other exclusive-resource action by workers.

## Constraints and assumptions

- User approval is scoped to the current workflow, plan revision, proposed
  roles, and stated action boundaries. A material plan or scope change makes
  that approval stale.
- An explicit user request to use named subagents for a bounded work unit is
  authorization for that unit; a general preference for faster work is not.
- Host Hooks provide defense in depth only. Every worker prompt carries the
  complete ownership envelope because a host may omit a lifecycle event.
- Default concurrency is two workers; up to three is reserved for independent,
  read-only multi-perspective review. Delegation depth is one.
- Runtime remains Python 3 only. No scope delta is present.

## Execution and rollback units

### Task 1 — Delegation protocol and skill routing

- Add one `references/delegation.md` protocol with the benefit/veto gate,
  authorization proposal, host adapters, role-based model/effort policy,
  worker envelope, concurrency limits, and evaluation guidance.
- Add concise conditional routing to the main router and execution/review/
  verification disciplines without creating an automatically discoverable
  agent definition or another top-level skill.
- Rollback: revert the reference and linked skill guidance together.

### Task 2 — Worker defense-in-depth context

- Strengthen the existing bounded worker context to name leaf depth, prohibited
  parent-ledger writes, and lack of commit/push/deploy/destructive/external
  authority while preserving fail-open, read-only Hook behavior.
- Add focused state and Hook tests for the exact worker boundary.
- Rollback: revert renderer, Hook assertions, and state assertions together.

### Task 3 — Compatibility, evaluation, and candidate packaging

- Add representative positive, negative, decline, stale-approval, unavailable-
  capability, unsupported-setting, and missing-Hook scenarios.
- Refresh bilingual public docs, capability/model/security guidance, changelog,
  and aligned `1.4.0-alpha.1` package metadata while keeping stable install
  commands on the latest published release.
- Run focused tests, the aggregate suite once after integration, every skill
  validator, Codex plugin validation, Claude strict validation, Qoder
  validation, OpenCode syntax, and package consistency checks.
- Rollback: revert docs/evals/version metadata as one candidate unit; schema and
  installed stable releases remain unchanged.

## Acceptance checks

- Ordinary direct, lean, compact, full, and recovery paths remain single-agent
  and add no model call, worker, repository scan, network access, or wait.
- Tiny, sequential, unsettled, same-file, shared-resource, destructive, and
  external-state tasks do not produce a delegation recommendation.
- A qualifying independent workload produces one compact recommendation and no
  worker starts before exact user authorization.
- Decline, missing native capability, or unsupported model/effort continues
  single-agent without retry loops or fake nested CLI orchestration.
- Codex, Claude Code, and Qoder guidance matches their currently available
  native controls; OpenCode remains capability-gated rather than overclaimed.
- Every authorized worker receives a bounded leaf envelope and cannot become
  the acceptance owner, ledger writer, releaser, or nested delegator.
- The coordinator integrates outputs, handles shared broad tests once, reviews
  material delegated changes, and freshly verifies the combined tree.
- Package versions align at `1.4.0-alpha.1`; all unit, skill, plugin, host, and
  syntax validators pass with no new top-level skill or static agent directory.

## Scope delta

No scope delta.

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "compact",
  "sources": [],
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
      "title": "Littlepowers remains single-agent by default and launches no worker before exact work-unit-specific user authorization",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "A deterministic benefit and veto gate recommends delegation only for ready independent work whose critical-path or context-isolation benefit exceeds coordination cost",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Codex, Claude Code, and Qoder use only callable native delegation controls while unsupported hosts and settings fall back honestly to single-agent or inherited settings",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "Model and effort selection is role-based and conservative, defaults to inheritance, and never automatically chooses maximum effort, Codex Ultra, or Claude Agent Teams",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "Workers receive a bounded leaf ownership envelope while the root coordinator alone owns the ledger, integration, shared broad tests, review adjudication, and final verification",
      "disposition": "active"
    },
    {
      "id": "OUT-006",
      "title": "Representative evaluations, cross-host documentation, security boundaries, regression tests, and aligned 1.4.0-alpha.1 candidate metadata cover both beneficial and harmful delegation cases without adding default-path overhead",
      "disposition": "active"
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["inspection:default-off-routing", "test:authorization-before-spawn"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["inspection:benefit-veto-gate", "test:positive-and-negative-workloads"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["inspection:host-adapters", "host:codex-claude-qoder-validation"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["inspection:role-selection-policy", "test:unsupported-setting-fallback"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 1", "Task 2"],
      "evidence": ["test:worker-context-boundary", "inspection:coordinator-integration-ownership"]
    },
    {
      "outcome": "OUT-006",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["test:aggregate-regression", "test:version-and-package-parity", "inspection:no-default-runtime-path"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
