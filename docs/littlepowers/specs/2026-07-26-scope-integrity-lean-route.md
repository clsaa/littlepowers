# Scope integrity and lean-route specification

Date: 2026-07-26

## Purpose

Prevent silent scope shrinkage while reducing planning ceremony for bounded changes.

## Functional requirements

1. Before routing, the agent identifies the latest request and highest-authority approved PRD, interaction, prototype, screenshot, contract, or acceptance source.
2. Every planning artifact inherits applicable parent requirements. A lower-level artifact cannot override them by declaring a narrower non-goal, MVP, phase, or slice.
3. The agent reports `Added / Changed / Deferred / Removed` with consequences, or exactly `No scope delta`. A non-empty delta requires explicit approval when highlighted.
4. The agent does not split the approved outcome into product, technical, platform, MVP, or phase slices. Tasks may order one continuous implementation stream but remain under one definition of done.
5. UI and interaction work names baseline provenance. User-approved sources can prove fidelity; implementation-generated snapshots can prove only regression.
6. Review returns separate `work-unit compliance`, `approved-outcome fidelity`, and code-quality verdicts.
7. Verification covers inherited acceptance criteria before completion; a partial rollback unit cannot complete the workflow.
8. Small bounded changes with one meaningful decision use brainstorm → plan → execute and create no spec or design artifact.
9. Full route remains brainstorm → spec → design → plan → execute for explicit requests or material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback decisions.
10. Recovery context includes the canonical workspace root. The router uses an explicit project root and leaves an unrelated ancestor ledger untouched.

## Compatibility and performance

- State schema remains version 2.
- Existing direct, shape, full, paused, terminal, and handed-off ledgers remain readable.
- Runtime remains Python 3 only; Hook work adds one path string and no filesystem scan beyond existing root discovery.
- The protocol does not select a model, reviewer, subagent, or reasoning effort.

## Acceptance criteria

- Focused regression tests cover lean routing, scope inheritance, no slicing, baseline provenance, dual verdicts, explicit root routing, and root-bearing Hook output.
- Full Python tests, compile checks, eleven skill validators, Codex plugin validation, and Claude strict validation pass where the host CLI is available.
- Bilingual README, durable guidance snippets, capability/model docs, changelog, and evaluation scenarios match the new behavior.
