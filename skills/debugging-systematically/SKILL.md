---
name: debugging-systematically
description: Diagnose bugs, failing tests, regressions, crashes, or performance anomalies before editing. Use for technical investigation or repair.
---

# Debugging systematically

Find the earliest supported cause before editing. Preserve the action authority in the latest user request: a diagnosis request authorizes inspection and non-mutating checks, not a fix.

## Establish the boundary

Capture the observed symptom, expected behavior, exact environment, available reproduction, and relevant recent changes. Determine whether the request is diagnosis-only or also authorizes implementation. Do not edit during diagnosis-only work even when a likely repair is visible.

Preserve raw error text, exit status, inputs, and timing when they matter. Treat summaries and prior agent reports as leads until repository or runtime evidence confirms them.

For tracked Littlepowers work, inspect the stored contract, coverage, baseline,
and fidelity summary before reproducing. Treat `reconcile_required`, `drifted`,
missing Outcome coverage, or stale verification as contract-boundary evidence,
not as permission to bypass the gate or edit the raw ledger.

## Reproduce and observe

Run the narrowest reliable reproducer before proposing a repair. Record the command or action and the exact failing signal. If reproduction is unavailable, identify the missing condition and gather the best boundary evidence; do not convert an unconfirmed guess into a cause.

Inspect complete diagnostics around the failure. Check inputs and outputs at component boundaries, configuration and environment assumptions, and relevant recent diffs.

## Trace the divergence

Trace the bad value or control path backward to the earliest point where observed behavior departs from its contract. Compare a working analogue when one exists, listing material differences rather than assuming one is causal. Distinguish the root cause from downstream symptoms and incidental cleanup opportunities.

## Test one hypothesis

State one falsifiable hypothesis at a time using four observable parts:

- evidence that motivates it;
- the proposed causal mechanism;
- the result that would support or falsify it;
- the smallest safe experiment that can discriminate between them.

Run that experiment before applying a broad repair. Change one causal variable at a time and avoid bundling speculative fixes. Count a failed hypothesis only after its discriminating check falsifies it.

After three failed fix hypotheses, stop patching. Report the evidence, the assumptions now in doubt, and the architecture- or contract-level question that must be resolved before another fix attempt.

## Repair the root cause

Only when implementation is authorized, make the smallest complete repair at the causal boundary. Preserve unrelated behavior and avoid opportunistic refactors. Label a containment measure or workaround honestly when the root cause cannot yet be removed.

Rerun the original reproducer after the edit. Add or update regression coverage when externally observable behavior changed, then run checks for the affected boundary. Do not use an unrelated passing suite as a substitute for the original symptom.

## Report observable evidence

Report the supported cause, the evidence that distinguishes it from alternatives, files changed or confirmation that no files changed, the original reproducer result, affected regression checks, and any remaining uncertainty. If the cause is not established, report the next discriminating check instead of claiming the issue is fixed.
