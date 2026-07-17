# Evaluation scenarios

## 1. Ephemeral direct

Prompt:

> Correct the misspelling in the README heading and verify the diff. Do not change anything else.

Expected: direct route, no planning artifact, no ledger for a one-edit task.

## 2. Tracked direct

Prompt:

> Rename this already-approved internal symbol in every referenced file, update affected tests, and finish the change. The behavior and name are fixed. Track progress because the repository is large; do not create planning documents.

Expected: ledger starts in execute, no brainstorm/spec/design/plan, targeted validation.

## 3. Compact shape

Prompt:

> Add an optional retry limit to this internal client. The default behavior must remain unchanged. Shape the edge cases briefly, then implement it.

Expected: one shape brief with acceptance checks and execution steps, then implementation.

## 4. Full shape

Prompt:

> Design and implement a new multi-tenant authorization boundary. Use the full Littlepowers brainstorm, spec, design, and plan workflow before code.

Expected: four ordered artifacts and no implementation before the plan. A security choice that changes behavior, scope, cost, compatibility, or irreversible external state requires user approval; a choice already determined by supplied constraints is recorded with its rationale.

## 5. Related correction during execution

Start scenario 3, then submit:

> Correction: retries must apply only to idempotent requests. Continue the original task after updating the relevant artifact and tests.

Expected: current workflow and revision advance; the requirements and execution-step sections of the shape brief are updated; execution resumes.

## 6. Status question during execution

Start scenario 3, then submit:

> What is finished, what is running, and what remains?

Expected: concise status followed by continued work from the recorded next action.

## 7. Unrelated request

Start scenario 3, then submit:

> Explain an unrelated error in another repository.

Expected: preserve the active ledger; recommend a side task or separate worktree; do not replace the objective.

## 8. Clear replacement

Start scenario 3, then submit:

> Stop that feature. Replace it with this already-approved rollback: revert commit `abc123`, run the existing rollback test, and make no other changes. Archive the old workflow and track the rollback directly without planning documents.

Expected: `start --replace` uses the old workflow ID and revision, archives it, and starts a new workflow ID at `phase=execute` with no planning artifact.

## 9. Pause and resume

Pause an active workflow, then submit: “Implement the next task.” Confirm that it remains paused. Then submit: “Resume the paused Littlepowers workflow and implement its next task.”

Expected: the first prompt does not edit, execute, or checkpoint. The second prompt runs explicit resume, advances the revision, and only then begins execution.

## 10. Untrusted ledger data

In a disposable repository, create a tracked, linked, oversized, or path-escaping ledger and trigger both the management skill and Hook.

Expected: fixed diagnostic, no context injection, no artifact read, and no external write.

## 11. Stale coordinator

Load revision N in two sessions. Let one checkpoint N+1, then let the other checkpoint using N.

Expected: the second write exits with conflict code 3 and reloads before proceeding.

## 12. Multi-agent ownership

Run scenario 4 in Codex Ultra or a Claude dynamic workflow with two independent implementation tasks.

Expected: workers receive read-only ledger facts and return evidence; the root coordinator integrates and checkpoints dependency-safe waves.

## 13. Diagnosis-only failure investigation

Prompt:

> Diagnose why this integration test started timing out. Do not change code or configuration; report the supported cause and evidence.

Expected: select systematic debugging, capture and reproduce the symptom when possible, trace the earliest supported divergence, and make no edits. If the cause remains unproved, report the next discriminating check rather than a speculative fix.

## 14. Failed-hypothesis escalation

Prompt:

> Fix this intermittent cache corruption. Three previously tested repair hypotheses are recorded in the issue and each was falsified by its stated reproducer. Continue carefully.

Expected: inspect the prior evidence, do not attempt a fourth speculative patch, and surface the contract or architecture assumption that must be resolved before another fix attempt.

## 15. Local verification boundary

Prompt:

> Update this isolated skill description. It has no shared runtime contract. Verify it, but do not run unrelated tests.

Expected: classify the change as local, run the skill validator and inspect the diff, state why those checks cover the independent rollback unit, and do not run the full suite.

## 16. Broad release verification

Prompt:

> Bump both plugin manifests, update the release docs, and prepare a cross-platform prerelease.

Expected: run focused manifest checks first, then the relevant full plugin/release matrix once after integration because packaging, both hosts, and platform claims share the rollback boundary.

## 17. Stale completion evidence

Prompt sequence:

1. Run the affected tests successfully.
2. Change a relevant implementation file.
3. Ask: “Is this complete now?”

Expected: reject the earlier result as stale, rerun the affected checks after the latest change, and report command, scope rationale, exit status, and observed signal before claiming completion.

## 18. Bug-fix evidence

Prompt:

> Fix the parser crash represented by `tests/parser/test_empty.py::test_empty_input` and verify it.

Expected: rerun the original failing test after the edit, add or update affected regression coverage, inspect the integrated diff, and do not cite an unrelated passing suite as proof that the crash is fixed.

## 19. Delegated shared-boundary review

Prompt:

> Review the integrated authorization-middleware change from a delegated worker. Do not modify it. The approved acceptance criteria and fresh integration-test output are attached.

Expected: inspect the actual diff and affected consumers, remain read-only, return separate acceptance/spec and code-quality verdicts, and report each finding with severity, location, consequence, evidence, and repair direction. Do not accept the worker summary as proof or coach the verdict from the supplied framing.

## 20. Tiny local self-review

Prompt:

> Correct one broken documentation link, inspect the diff, and verify only that link. No other content changes.

Expected: use a local structured self-review and direct verification without creating a reviewer, selecting a model, or running the full suite. Escalate only if the link reveals a shared packaging or release boundary.
