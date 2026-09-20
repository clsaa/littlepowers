# Current host capability refresh

## Outcome

Refresh Littlepowers' opt-in delegation guidance for current Codex, Claude
Code, and Qoder without changing the default single-agent path, ledger schema,
or user-authorization boundary.

## Non-goals

- Do not enable automatic delegation, Agent Teams, maximum effort, Ultra, or
  Qoder Ultimate.
- Do not create static plugin agents or edit user/organization host settings.
- Do not auto-detect hosts, query the network, persist capability data in the
  ledger, or add work to the ordinary routing path.
- Do not publish, tag, commit, push, or install a release in this work unit.

## Constraints and assumptions

- Host documentation describes possible capabilities; the current callable
  tool schema or host command remains the authority for a launch.
- Provider model aliases and availability change. Runtime policy stays
  role-relative and defaults to inheritance; dated compatibility evidence may
  name observed versions and models.
- The worker task envelope remains mandatory even when host Hooks work, because
  Hooks are defense in depth and may be disabled by policy or trust settings.
- One small dependency-free validator may run only after the Delegation Gate
  has already found a high-benefit candidate. It must not read the repository,
  ledger, transcript, environment, or network.

## Requirements and selected approach

1. Correct the obsolete Qoder claims. Current Qoder documents
   `QODER_PLUGIN_ROOT`, `SessionStart`, and `SubagentStart`; public guidance,
   scenarios, and regression expectations must stop claiming otherwise.
2. Add a canonical Host Capability Snapshot to the existing delegation
   reference and authorization proposal. It records the observed native
   mechanism, fresh/fork/team context, effective model and effort, isolation,
   permission/tool boundary, durability, and leaf-agent enforcement.
3. Add a standard-library snapshot validator for host-independent safety
   invariants. It validates only explicit observations and never selects or
   launches a worker.
4. Describe current adapters proportionally:
   - Codex uses the current built-in/custom native agent interface and actual
     spawn precedence, with inherited settings by default.
   - Claude distinguishes fresh subagents, full-context forks, and
     session-scoped Agent Teams.
   - Qoder distinguishes ordinary subagents, inherited-context `/subtask`, and
     beta Agent Teams; leaf depth is enforced through tool controls and
     read-only work does not rely on `permissionMode` alone.
5. Replace stale prose-presence assertions with behavioral, table-driven
   validation of safe and rejected capability snapshots. Retain focused
   manifest checks only for package structure and progressive-disclosure
   routing.
6. Refresh the dated compatibility and evaluation matrices for the latest
   observed registry versions and current model families, while clearly
   separating documentation/structural compatibility from authenticated live
   execution evidence.

No scope delta.

## Affected components

- `references/delegation.md`
- `scripts/littlepowers_delegation.py`
- `tests/test_delegation.py`
- `tests/test_manifests.py`
- `docs/capability-matrix.md`
- `docs/model-compatibility.md`
- `evals/README.md`
- `evals/scenarios.md`
- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`

## Execution and validation

1. Implement the snapshot validator and table-driven tests.
2. Update the delegation adapter and proposal around the validator's stable
   fields.
3. Correct Qoder claims and refresh current Codex, Claude Code, and Qoder
   compatibility/evaluation documentation.
4. Remove tests that preserve obsolete host facts and add focused behavioral
   regressions.
5. Run the focused delegation/manifest/Hook tests, inspect the complete diff,
   then run the repository-required aggregate suite and package validators once.

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
      "title": "Qoder guidance and regressions match current documented Hook and plugin-root behavior",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "Delegation proposals carry a validated lightweight Host Capability Snapshot with safe leaf-worker boundaries",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Codex, Claude Code, and Qoder adapters distinguish their current context, isolation, permission, durability, and model-selection semantics",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "Behavioral compatibility tests reject unsafe snapshot combinations instead of merely matching policy prose",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "The ordinary single-agent route retains zero capability-probe, extra-model, network, schema, or background cost",
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
      "tasks": ["Task 3", "Task 4"],
      "evidence": ["test:qoder-current-hook-contract", "inspection:no-stale-qoder-claims"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 1", "Task 2"],
      "evidence": ["test:capability-snapshot-validator", "inspection:delegation-proposal-fields"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["test:current-host-profile-matrix", "inspection:host-adapter-semantics"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 1", "Task 4"],
      "evidence": ["test:unsafe-snapshot-rejections", "test:focused-delegation-suite"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 1", "Task 2", "Task 5"],
      "evidence": ["inspection:progressive-disclosure-boundary", "test:aggregate-suite"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
