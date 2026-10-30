# Acceptance, repair, and efficient recovery

## Approved outcome and approach

Parent authority: the user's 2026-10-30 five-row P1/P2 iteration request in
this conversation. No scope delta. Complete all five rows in one continuous
workflow; tasks are rollback boundaries, not product slices.

Use a compact route and implementation mandate. Keep schema 4/protocol 1.3,
Python-standard-library runtime, four-host support, existing approvals, and
single ledger ownership. No release, installation, external write, model run,
subagent, background service, repository scan, or new tool dependency is part
of this request. Keep the package version unchanged until a release is requested.

T1: reproduce the failed/blocked fidelity result preventing repair-plan review.
The approved baseline's source availability/digest is already checked separately;
comparison failure must not act as absence of authority.

T2: allow failed/blocked comparison results at planning gates while retaining
fresh source, scope, coverage, and approval checks. On plan/contract invalidation
or return from verification to execution, clear current verdict eligibility but
retain the prior evidence artifact reference for recovery. Do not delete or
rewrite failure artifacts; a new verification attempt gets a new file and links
its predecessor. Completion still needs a new valid verification record.

T3: one progressively loaded acceptance reference supplies the original-user
journey/data/state/result checklist, applicable surfaces and explicitly approved
waivers, tool-capability checks, evidence reuse/invalidation, and operation
receipts. Route verification and relevant planning/recovery work to it; do not
add ceremony to trivial work. These are agent decision rules, not a claim that
the CLI can authenticate user success or arbitrary test provenance.

T4: regressions exercise fail/blocked repair, full/lean/compact policy boundaries,
unchanged failed evidence, stale pass invalidation, and fresh completion. Run
focused tests first and one aggregate suite after integration (state is a broad
boundary). Save lengthy non-sensitive test output once, then inspect a summary;
measure presented-output reduction, preserve exit status and failures, and do
not claim model-token/latency savings from byte counts. Review the integrated
candidate and record the remaining model/host evidence limits.

## Acceptance and rollback

- P1 repair: a failed comparison allows a scope-preserving repair plan to be
  reviewed, not auto-approved. Drifted/missing sources, incomplete coverage,
  unresolved approval and scope deltas remain blockers. Old failure evidence
  remains readable; a repair/replan cannot reuse an old pass to finish.
- P1 user task: start at the original entry point, cover applicable existing
  records as well as new data, observe persistence and final user-visible result;
  unit counts, seeded happy paths and self-generated screenshots are insufficient.
- P1 scope/tools: record applicable host/surface, available tools, approved
  exemptions and their limits once; permission reuse stays within the same scope.
- P2 evidence: record claim, command, result, relevant input/environment identity,
  evidence path and reuse reason; invalidate affected consumers, use focused
  reruns, and retain unaffected evidence only when its dependencies are known.
- P2 efficiency: use available host log/continuation/readback facilities without
  installing helpers; avoid retrying a still-running or already completed write.

Rollback: state gate/invalidation changes and their tests form one unit; skill
reference/routing and evaluation guidance form another. Neither changes the
ledger grammar, hook behavior, model selection, or test policy of user projects.

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "compact",
  "sources": [],
  "scope_delta": {"status": "none", "consequences": []},
  "baseline": {"requirement": "not_applicable", "source_ids": []},
  "review": {"code_quality_required": true},
  "outcomes": [
    {"id": "OUT-001", "title": "Failed acceptance allows lawful repair while retaining evidence, approval and completion gates", "disposition": "active"},
    {"id": "OUT-002", "title": "Acceptance follows the original user journey with applicable historical data and observable completion", "disposition": "active"},
    {"id": "OUT-003", "title": "Acceptance scopes applicable surfaces, tools and approved exemptions without repeated foreground requests", "disposition": "active"},
    {"id": "OUT-004", "title": "Evidence reuse and affected-check invalidation are explicit and stale success cannot survive a repair transition", "disposition": "active"},
    {"id": "OUT-005", "title": "Use available host efficiency facilities, prevent blind resubmission, and measure output-saving benefits honestly", "disposition": "active"}
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {"outcome": "OUT-001", "tasks": ["T1", "T2"], "evidence": ["test:acceptance-repair-gates"]},
    {"outcome": "OUT-002", "tasks": ["T3", "T4"], "evidence": ["inspection:user-task-acceptance", "test:repair-lifecycle"]},
    {"outcome": "OUT-003", "tasks": ["T3", "T4"], "evidence": ["inspection:surface-capability-scope"]},
    {"outcome": "OUT-004", "tasks": ["T2", "T3", "T4"], "evidence": ["test:stale-pass-invalidation", "inspection:evidence-reuse-rules"]},
    {"outcome": "OUT-005", "tasks": ["T3", "T4"], "evidence": ["test:bounded-output-measurement", "inspection:resume-receipts"]}
  ]
}
```
<!-- /littlepowers:plan-map -->
