# Native task checklist mirror

## Approved outcome and scope

The user approved the preceding diagnosis and lightweight mirror proposal.
Make planned work visible in the current host's native checklist when that
session exposes a supported tool. Cover Lean, Compact, Full, and meaningful
multi-step Direct work without creating sidebar sessions or subagents.
No scope delta. No release, installation, global configuration change,
background synchronization, or new orchestration layer is authorized here.

## Approach

Keep approved artifacts and the existing schema-4 ledger authoritative for
scope and acceptance. A shared progressively loaded reference describes native
tool selection and lifecycle. Add a standard-library-only pure projection
helper: bounded explicit JSON in, proposed operations out; never tool calls,
host discovery, transcript access, ledger writes, or network access.

Use stable task IDs and a workflow UUID. A session-scoped receipt contains only
last successfully mirrored rows and host IDs. Reconcile against a fresh native
observation: unchanged rows are no-ops, owned rows update, duplicate ownership
or user edits stop synchronization. Preserve unrelated native tasks. A missing
previously created item is a conflict, not permission to recreate deleted work.
Bulk-replacement surfaces require ownership of the entire existing checklist.
Unavailable tools degrade explicitly without blocking product implementation.

Receipts are optional ignored recovery caches, not a second task ledger.
Invalidate them when the native session/list changes; rediscover task ownership
through native tools before recreating anything. Do not introduce schema changes.

## Acceptance and continuous execution

- T1: Route all planning/execution paths to one reference; select actual tools,
  document Claude's opt-in tools and Qoder Task/Todo fallback. Tiny work skips it.
- T2: Implement bounded deterministic projection/reconciliation; test creation,
  update, no-op, unrelated tasks, duplicates, manual changes, deletions, stale
  receipts, unsupported tools, and bulk replacement safety.
- T3: Validate integrated skills and unit suite; attempt a bounded native Codex
  checklist smoke test if the installed CLI exposes it. Distinguish observed
  native tool events from visual UI verification. Report other-host UI checks
  as unverified, never inferred from mock adapters or package validation.

These are rollback/checkpoint boundaries, not product slices. The reference,
helper, skill entrypoints, and tests form one integration rollback unit.
No additional spec/design/plan documents or workers are needed.

## Outcome Contract

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "compact",
  "sources": [],
  "scope_delta": {"status": "none", "consequences": []},
  "baseline": {"requirement": "not_applicable", "source_ids": []},
  "review": {"code_quality_required": true},
  "outcomes": [
    {"id": "OUT-001", "title": "All applicable routes mirror through actual available native tools or report unavailable without configuration changes", "disposition": "active"},
    {"id": "OUT-002", "title": "Stable scoped identity and reconciliation avoid duplicate creation, manual-edit overwrite, and unrelated task mutation", "disposition": "active"},
    {"id": "OUT-003", "title": "Mirroring stays lightweight and subordinate to existing acceptance gates with truthful host verification evidence", "disposition": "active"}
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->

<!-- littlepowers:plan-map:v1 -->
```json
{"mappings": [
  {"outcome": "OUT-001", "tasks": ["T1", "T3"], "evidence": ["test:route-entrypoints", "test:capability-selection"]},
  {"outcome": "OUT-002", "tasks": ["T2"], "evidence": ["test:native-mirror-reconciliation"]},
  {"outcome": "OUT-003", "tasks": ["T3"], "evidence": ["review:bounded-mirror", "test:aggregate", "inspection:host-evidence-limits"]}
]}
```
<!-- /littlepowers:plan-map -->
