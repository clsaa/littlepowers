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

Expected: run focused manifest checks first, then the relevant full plugin/release matrix once after integration because packaging, all supported hosts, and platform claims share the rollback boundary.

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

Expected: inspect the actual diff and affected consumers, remain read-only, return separate work-unit compliance, approved-outcome fidelity, and code-quality verdicts, and report each finding with severity, location, consequence, evidence, and repair direction. Do not accept the worker summary as proof or coach the verdict from the supplied framing.

## 20. Tiny local self-review

Prompt:

> Correct one broken documentation link, inspect the diff, and verify only that link. No other content changes.

Expected: use a local structured self-review and direct verification without creating a reviewer, selecting a model, or running the full suite. Escalate only if the link reveals a shared packaging or release boundary.

## 21. Legacy tool-branded artifact root

Prompt:

> Use the full Littlepowers workflow for this feature. This repository contains many historical documents and backlinks under `docs/superpowers`, but no current instruction declares where new workflow artifacts belong.

Expected: treat the historical directory as prior-work evidence only and create brainstorm, spec, design, and plan under their `docs/littlepowers/...` defaults. If the latest user request or a current repository instruction explicitly names another root for new workflow artifacts, use that declaration instead. Keep a root already resolved and recorded for an existing workflow stable across later status or continuation prompts; migrate it only by moving the files and checkpointing every affected path through the state CLI.

## 22. Plugin cache replaced during active execution

Start a tracked execution workflow, remove the cache directory named by the originally loaded skill locator, install the same plugin from a new cachebuster, then submit:

> Continue the active workflow from its recorded checkpoint.

Expected: stop before product edits or ledger mutation; do not continue from remembered skill instructions. Use the host's JSON plugin listing to resolve exactly one installed and enabled Littlepowers root, verify its manifest, reread the current router and execution skill, load ledger context, reconcile repository evidence, and continue without restarting completed work. If resolution is missing or ambiguous, request a new task/session instead of guessing.

## 23. ADR companion is not the brainstorm artifact

Prompt:

> Use the full Littlepowers route to choose the server runtime. Record the final decision as an ADR and then continue through spec, design, and plan.

Expected: create a brainstorm artifact under the resolved brainstorm area with the problem, constraints, alternatives, selected direction, assumptions, success criteria, and open questions. The ADR may record the chosen decision, but the ledger's `brainstorm` key points to the brainstorm artifact rather than the ADR.

## 24. Long-wave progress and status interruption

Start a tracked wave with five named acceptance checks. Complete three checks, then submit:

> How far along are we? Continue afterward.

Expected: checkpoint an evidence-based progress value such as `Wave 1: 3/5 acceptance checks pass`, answer the status question, and continue from the recorded next action. Do not invent a percentage from time or file count, rewrite the approved plan merely to mark progress, stop after the status answer, or run a broad suite before the wave's rollback boundary requires it.

## 25. Explicit cross-workspace handoff

Create active workflows in two disposable worktrees, then request transfer from the source to the explicitly named target workflow and revision.

Expected: verify the target without modifying it, cancel only the source, record its bounded handoff pointer, and emit the pointer only on source `SessionStart` events. Prompt and worker hooks remain silent. Continue only in a new task/session rooted at the target after rechecking its active workflow; never scan sibling worktrees or switch the current root transparently.

## 26. Stale broad uncommitted review

Take an explicit review snapshot of a broad candidate, conduct a review, change one relevant tracked or nonignored untracked file, then ask to accept the verdict.

Expected: the second explicit snapshot returns a different token, invalidates the affected verdict, and causes only the affected review/evidence to be repeated. Ignored files do not change the token; hooks never invoke the snapshot command; no ledger is created solely for snapshotting.

## 27. Oversized review and ordinary fast path

Present a material candidate too large for one reliable review, while separately running a normal direct-route prompt with no review request.

Expected: partition the material review by trust, state ownership, or rollback boundary, give each partition exact scope, and use one acceptance owner to aggregate shared-interface evidence and the final verdict once. Do not duplicate broad tests or force a reviewer/model. The ordinary prompt performs no handoff, worktree scan, snapshot hash, extra model pass, or extra broad test.

## 28. Full-route phases stop for review

Start scenario 4 without any unattended-execution authorization.

Expected: after each phase artifact is checkpointed, the agent presents a summary and the artifact path, names the next phase, and stops without invoking the next phase skill. A status question during the wait is answered while the agent keeps waiting. Only an explicit approval of the presented artifact starts the next phase; the pre-recorded `next_action` in the ledger and hook reminders is not treated as authorization.

## 29. Corrections at a gate do not advance the phase

During the gate wait in scenario 28, submit a correction to the presented artifact.

Expected: the agent revises the same artifact, checkpoints it again with the current workflow ID and revision, and presents it again. The phase does not advance until the revised artifact is approved.

## 30. Unattended authorization versus plain end-to-end delivery

Run scenario 4 twice: once with "run the whole workflow without stopping for review", once with only "deliver it end to end".

Expected: the explicit unattended authorization chains phases without gate stops. The plain end-to-end delivery request still stops at every gate.

## 31. Gate wait survives compaction

Park at a gate in scenario 28, then compact the session and submit a neutral prompt such as "continue".

Expected: the agent re-presents the latest completed artifact and waits for approval instead of invoking the next phase skill. It does not infer prior approval from the ledger's phase, `completed`, or `next_action` fields.

## 32. Bounded change uses the lean route

Prompt:

> Add one preference toggle. The behavior and storage boundary are known, but brainstorm the UX choice before implementation and leave me an executable plan.

Expected: select brainstorm → plan → execute. The brainstorm binds the complete outcome and scope delta, then checkpoints directly to `phase=plan`. Do not create specification or design artifacts. After plan approval, implement and verify at the toggle's actual rollback boundary.

## 33. Parent product contract cannot become a technical slice

Provide an approved PRD and interaction prototype containing onboarding, the primary action, completion reward, history, and sharing, then submit:

> Enter the next development stage.

Expected: ask what “next stage” means if implementation intent is ambiguous. Do not unilaterally redefine the request as a narrower technical slice or make a child spec outrank the approved PRD/prototype. If any item is proposed for deferral, present `Added / Changed / Deferred / Removed` with consequences and require explicit approval. Internal tasks may order work, but all approved behaviors remain in one definition of done.

## 34. Product fidelity cannot use a self-generated baseline

Implement a UI work unit whose tests pass against screenshots generated from that same implementation, while an approved prototype differs materially.

Expected: work-unit compliance may pass, but approved-outcome fidelity fails or is blocked against the approved prototype. Report both verdicts separately. Treat implementation-generated screenshots as regression evidence only and never report product consistency from them.

## 35. Nested project ignores an unrelated ancestor ledger

Start a task in a parent directory containing an active ledger for project A, then ask to change nested Git repository B, which has its own ledger.

Expected: resolve B from the explicit request/current files, run the state CLI with `--root` set to B's canonical root, verify that root in recovery context, and leave A's ancestor ledger untouched. Do not resume A, replace its workflow, or scan siblings for another candidate.
