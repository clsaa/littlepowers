---
name: verifying-work
description: Verify changed work before claiming it is complete, fixed, passing, ready, or released. Use after implementation, bug fixes, delegated integration, or release preparation to require fresh evidence at the appropriate impact and rollback scope.
---

# Verifying work

Match every success claim to fresh observable evidence. Test count alone is not proof, and a broad suite is not automatically better than a check that directly exercises the changed behavior.

## Define the claims

List the acceptance claims that the final report must support. Include the original symptom for a bug, affected contracts for connected work, and package or platform claims for a release. Do not claim more than the available environment can verify.

Inspect the changes since the last evidence was collected. A check becomes stale after any relevant code, configuration, dependency, generated artifact, or environment change. Rerun it when ordering is uncertain.

## Classify impact and rollback scope

Choose the smallest level that covers the plausible rollback boundary:

- **Local:** one isolated contract and an independently reversible file or feature. Run the original reproducer or focused unit/skill check, then inspect the diff.
- **Connected:** several modules or consumers share a boundary and rollback needs coordination. Add the affected integration, build, type, or contract checks to the focused check.
- **Broad:** state or schema, security, hooks, packaging, public API, migration, cross-platform behavior, or a release is affected. Run focused checks first, then the relevant broad suite or release matrix once after integration.

Impact is not line count. A one-line manifest or shared-contract edit may be broad; a larger isolated fixture change may remain local. A full suite is not the default after every small edit.

When independently reversible features are combined, verify each feature at its own boundary first. Run aggregate broad checks only when their integration or release surface requires them.

## Collect fresh evidence

For each claim, record:

- the command, inspection, or user-visible action;
- why its scope covers the impact and rollback boundary;
- its exit status or equivalent result;
- the relevant observed signal, count, or output.

For a bug fix, rerun the original reproducer after the latest edit and run regression coverage for the affected behavior. Do not substitute an unrelated passing suite for the symptom that was fixed.

Treat delegated worker reports as inputs, not final proof. The coordinator inspects the integrated tree and reruns the checks needed to support its own completion claim.

If a required tool, credential, platform, service, or deterministic environment is unavailable, state the exact limitation. Do not turn a skipped, flaky, partial, or unexecuted check into success.

## Inspect the integrated diff

Review the final intended diff and status for unintended files, debug statements, temporary artifacts, accidental generated output, secrets, and changes outside the authorized scope. Confirm that the actual rollback unit still matches the chosen verification level.

## Gate the report

Use a compact claim-evidence summary when several claims exist. Mark work complete only when every required claim has fresh supporting evidence and no blocking limitation remains. For a tracked Littlepowers workflow, stay in `phase=verify` and complete the ledger only after this gate passes.

Report the selected scope and rationale, exact checks and observed results, diff inspection, and unresolved limitations. Use narrower language when evidence is narrower than the requested outcome.
