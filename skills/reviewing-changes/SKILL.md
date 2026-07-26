---
name: reviewing-changes
description: Review changes read-only for work-unit compliance, approved-outcome fidelity, and code quality. Use for requested or material integration review.
---

# Reviewing changes

Produce a skeptical, evidence-backed assessment while staying read-only. Do not edit code, mutate a Littlepowers ledger, create a reviewer, or select a model. When fixes are also requested, finish the review first and let the authorized coordinator handle repairs as a separate action.

## Choose proportional review scope

Match review depth to impact and rollback coupling:

- **Local:** inspect the focused diff, acceptance check, and direct evidence. A tiny isolated change may use structured self-review without a separate reviewer pass.
- **Connected:** inspect the changed boundary and affected consumers, integration evidence, and coordinated rollback risks.
- **Broad:** inspect cross-system, security, state/schema, hook, packaging, migration, platform, public API, or release effects and the relevant aggregate evidence.

Use review when the user asks for it, delegated output is integrated, a shared milestone changes behavior, or rollback cost is material. Do not force separate-review ceremony onto every tiny edit.

## Prepare a neutral brief

Review the highest-authority approved outcome and parent acceptance sources, the immediate work-unit requirements, exact diff or commit range, named affected interfaces, approved baselines, fresh verification evidence, and known limitations. Do not include a proposed verdict or coach the reviewer with a list of suspected findings.

Treat implementation summaries and worker claims as navigation aids rather than proof. Inspect the actual files and tests. Keep unrelated pre-existing issues out of scope unless they directly change the safety or correctness of this change.

## Bind a changing review candidate

Prefer an immutable commit or exact range when one already exists. For a broad uncommitted candidate, explicitly run `<python> <state-cli> --root <candidate-root> snapshot` before review and again before accepting its verdict. Record the content-free token with the brief. A changed token invalidates the review verdict; inspect the new diff and repeat only the affected review and evidence.

The snapshot command is bounded, read-only, and on demand. Hooks and ordinary routes never invoke it. It does not create reviewers or select models, effort, or tests.

If one material candidate cannot fit a reliable review, report the scope limit and partition by trust, state ownership, or rollback boundary. Give each partition an exact scope, then have one acceptance owner aggregate shared-interface coverage and the final verdict once. Do not duplicate broad test runs per partition.

## Assess acceptance and quality separately

First assess acceptance/spec compliance as **work-unit compliance**. Map each immediate required behavior and bound `OUT-###` ID to the implementation and evidence, identify unauthorized scope, and return exactly one verdict: `pass`, `fail`, or `blocked`.

Then assess **approved-outcome fidelity** independently against the highest-authority parent requirements and approved baseline. Return exactly one verdict: `pass`, `fail`, or `blocked`. A narrower specification, implementation plan, technical slice, or generated fixture cannot erase parent requirements. When the available review inputs omit a known parent source or cover only part of it, report the fidelity verdict as `blocked`, never as product consistency. For visual or interaction fidelity, an implementation-generated screenshot or snapshot is regression evidence only and cannot replace the approved user or design baseline.

Treat stored coverage as a deterministic completeness check, not semantic proof.
If the Outcome Contract itself omits a known parent behavior, fail or block
approved-outcome fidelity even when the CLI reports `coverage=100%`. Check every
required `FID-###` comparison against its approved baseline.

Finally assess code quality independently. Check correctness, failure modes, boundary handling, security and portability where relevant, maintainability, and whether tests exercise the changed risks. Return exactly one verdict: `approve`, `request changes`, or `blocked`.

Do not let a quality preference fail compliant code without a concrete consequence. Do not let clean style hide a missing requirement.

## Write actionable findings

Order findings by severity: **Critical**, **Important**, then **Minor**. For every finding include:

- exact file and line when applicable;
- the violated requirement or engineering risk;
- the concrete consequence;
- supporting code or test evidence;
- a repair direction without silently implementing it.

Critical and Important findings block completion until repaired or explicitly accepted by the authorized user. Minor findings remain non-blocking unless they violate an acceptance criterion. If there are no actionable findings, say so and list residual risk or unverified assumptions separately.

## Adjudicate and reverify

The coordinator verifies every finding technically against the repository and requirements. Do not accept feedback blindly, dismiss it performatively, or change code merely to satisfy reviewer phrasing. Resolve disagreements with concrete evidence and surface a genuine product decision to the user when required.

After an accepted repair, invalidate and rerun evidence affected by that repair. A prior approval does not cover code changed after the review.

## Report

Return the review scope and rationale, the work-unit compliance verdict, the approved-outcome fidelity verdict, the code-quality verdict, ordered findings, and residual risk or verification gaps. Keep the report read-only and distinguish blocking findings from optional improvements.
