# Scope integrity and lean-route design

Date: 2026-07-26

## Routing design

The router keeps four proportional choices:

- **Direct:** clear outcome and approach; no planning artifact.
- **Lean plan:** one bounded decision; brainstorm checkpoints directly to `phase=plan`, then `writing-plans` reads the approved brainstorm.
- **Compact shape:** one combined brief for moderate connected decisions and legacy `phase=shape` recovery.
- **Full shape:** brainstorm → spec → design → plan for material unresolved decisions.

No route field is added to schema 2. Recovery distinguishes the lean route through `phase=plan`, a recorded brainstorm, no required spec/design, and a next action/progress string naming the lean route. Existing state transitions already permit this.

## Scope-integrity design

`using-littlepowers` binds the approved outcome before route selection:

1. parent contract inheritance;
2. distinct Scope Delta Gate;
3. no implicit product or technical slices;
4. approved baseline provenance.

Each phase skill repeats only its local enforcement point. Specs trace inherited requirements, design maps every inherited requirement, plans keep one definition of done, and execution cannot convert a blocker or partial rollback unit into deferred scope.

Review uses three independent verdicts:

1. work-unit compliance;
2. approved-outcome fidelity;
3. code quality.

Verification refuses completion until immediate and inherited claims have fresh evidence.

## Root-binding design

The state file remains worktree-local. `_recovery_data` accepts an optional root and emits `workspace_root`; Hook and CLI context callers pass the canonical root. Direct library callers remain compatible because the parameter is optional.

The router instructs hosts to invoke `--root <project-root> context`. This makes an ancestor/nested mismatch visible without scanning siblings, changing the current task root, or mutating either ledger.

## Failure and rollback

- Unapproved scope delta: stay at the current gate.
- Missing parent source or conflicting requirements: report the conflict; do not choose the narrower source.
- External blocker: keep the approved outcome incomplete.
- Rollback is one connected protocol unit: revert skill wording, root context field, tests, docs, and version metadata together. No ledger migration is required.
