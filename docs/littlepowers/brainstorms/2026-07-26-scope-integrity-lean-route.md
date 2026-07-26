# Scope integrity and lean-route brainstorm

Date: 2026-07-26

## Problem

Two observed failures need one protocol correction:

1. An agent can turn an approved product journey into a narrower technical slice, then obtain green reviews against the narrowed document while the product remains incomplete.
2. A small bounded change that needs one decision is often routed through brainstorm → spec → design → plan even though brainstorm → plan is sufficient.

A related recovery failure occurs when a task starts in a parent directory whose ledger belongs to another nested repository.

## Constraints

- Keep one shared skill implementation for Codex, Claude Code, Qoder, and OpenCode.
- Add no model calls, telemetry, daemon, transcript access, or background test run.
- Keep direct work direct and preserve existing shape/full workflows during recovery.
- Preserve one approved outcome through implementation; internal tasks may order work but may not become product slices.
- Avoid a state-schema migration unless durable recovery cannot express the new route.

## Options

1. **Add more mandatory full-route documents.** Rejected: it worsens the small-change ceremony and does not prevent a bad parent scope from being copied.
2. **Add a new state-schema route field.** Rejected for now: `phase=plan` plus the presence of a brainstorm and absence of spec/design already recovers the lean route.
3. **Add skill-level scope integrity and a lean route (selected).** Bind parent acceptance sources, require a highlighted scope delta, distinguish user-approved from implementation-generated baselines, add three independent review verdicts, expose the exact workspace root in hook context, and route bounded changes through brainstorm → plan.

## Selected direction

- New-work routes are direct, lean plan, compact shape, and full shape.
- Lean plan is `brainstorming → writing-plans → executing-plans`.
- Full shape remains available only for material unresolved decisions or explicit requests.
- A parent contract is inherited by every lower artifact. `Added / Changed / Deferred / Removed` requires explicit approval; otherwise the artifact states `No scope delta`.
- Development covers one approved outcome in one continuous implementation stream. Tasks and rollback units cannot redefine completion.
- Review reports work-unit compliance and approved-outcome fidelity separately.
- Hook snapshots include the canonical workspace root so an ancestor ledger is visible as such.

## Scope delta

No approved Littlepowers capability is removed. Compact shaping remains available and existing ledgers remain compatible.

## Measurable success

- A bounded small-change prompt produces brainstorm → plan without spec/design.
- A narrower child spec cannot claim product consistency against an inherited PRD or prototype.
- UI fidelity cannot pass solely against an implementation-generated snapshot.
- A parent-directory ledger cannot be mistaken for a nested project ledger without the root mismatch being observable.
- Existing schema-2 ledgers and all four hosts continue to validate.
