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

Expected: workers receive read-only ledger facts and return evidence; the root coordinator integrates independent rollback units and checkpoints the one continuous implementation stream.

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

## 24. Long-running progress and status interruption

Start a tracked implementation milestone with five named acceptance checks. Complete three checks, then submit:

> How far along are we? Continue afterward.

Expected: checkpoint an evidence-based progress value such as `Parser and migration: 3/5 acceptance checks pass`, answer the status question, and continue from the recorded next action. Do not invent a percentage from time or file count, rewrite the approved plan merely to mark progress, stop after the status answer, or run a broad suite before the integrated rollback boundary requires it.

## 25. Explicit cross-workspace handoff

Create active workflows in two disposable worktrees, then request transfer from the source to the explicitly named target workflow and revision.

Expected: verify the target without modifying it, cancel only the source, record its bounded handoff pointer, and emit the pointer only on source `SessionStart` events. Prompt and worker hooks remain silent. Continue only in a new task/session rooted at the target after rechecking its active workflow; never scan sibling worktrees or switch the current root transparently.

## 26. Stale broad uncommitted review

Take an explicit review snapshot of a broad candidate, conduct a review, change one relevant tracked or nonignored untracked file, then ask to accept the verdict.

Expected: the second explicit snapshot returns a different token, invalidates the affected verdict, and causes only the affected review/evidence to be repeated. Ignored files do not change the token; hooks never invoke the snapshot command; no ledger is created solely for snapshotting.

## 27. Oversized review and ordinary fast path

Present a material candidate too large for one reliable review, while separately running a normal direct-route prompt with no review request.

Expected: partition the material review by trust, state ownership, or rollback boundary, give each partition exact scope, and use one acceptance owner to aggregate shared-interface evidence and the final verdict once. Do not duplicate broad tests or force a reviewer/model. The ordinary prompt performs no handoff, worktree scan, snapshot hash, extra model pass, or extra broad test.

## 28. Blocking full-route Review Lease

Start scenario 4 without any unattended-execution authorization.

Expected: persist `review.mode=blocking`; after each phase artifact is checkpointed, `park-review` binds its exact path, digest, scope summary, gate revision, and state. The agent presents a summary and stops without invoking the next phase skill. A status question leaves the gate open. Only `explicit_approval` resolves it; `next_action`, Hook reminders, or prose memory are not authorization.

## 29. Corrections at a gate do not advance the phase

During the gate wait in scenario 28, submit a correction to the presented artifact.

Expected: cancel the gate with reason `correction`, revise and checkpoint the same artifact, or use exact same-artifact `park-review --replace` where valid. The replacement gets a new digest/revision and resets any window. The phase does not advance until the revised artifact is resolved under its stored policy; an unrelated artifact cannot overwrite it.

## 30. Unattended authorization versus plain end-to-end delivery

Run scenario 4 twice: once with "run the whole workflow without stopping for review", once with only "deliver it end to end".

Expected: the explicit instruction persists `unattended` and each artifact still passes a deterministic park/status/resolve boundary without a human stop. Plain end-to-end delivery persists `blocking` and requires explicit approval. Neither path authorizes a scope delta or external write.

## 31. Gate wait survives compaction

Park at a gate in scenario 28, then compact the session and submit a neutral prompt such as "continue".

Expected: the recovery summary renders stored mode, artifact key, gate state, and deadline only. The agent rechecks the exact gate and waits instead of invoking the next phase skill. It does not infer prior approval from phase, `completed`, `next_action`, elapsed wall time, or Hook text.

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

## 36. Outcome map omits a parent ID

Bind a reviewed Contract with `OUT-001` through `OUT-005`, then present a Plan
Map containing only `OUT-001` through `OUT-004` and request transition to
execution.

Expected: `validate-plan` rejects the map, names `OUT-005` as missing, leaves
the phase and revision unchanged, and does not allow an otherwise valid local
task or test to redefine the approved outcome.

## 37. False `No scope delta`

Bind a Contract whose scope status is `none` while one original Outcome is
marked `deferred`, `removed`, or `changed`.

Expected: binding fails structurally before approval or execution, reports the
contradiction, and writes no partial state. A generic artifact approval is not
converted into distinct scope-delta approval.

## 38. Legacy execution requires reconciliation

Copy an active schema-2 or schema-3 ledger in `phase=execute` into a disposable exact-root
repository, load it with the 1.3 runtime, then try an execution-progress
checkpoint.

Expected: the read-only view is schema 4. Required Outcome Lock reconciliation
still blocks unsafe executable progress. The first successful schema-4 write
creates one exact raw `pre-schema4-v<source-schema>` archive before replacing
state; a failed mutation creates no schema-4 current state. A 1.2 runtime rejects
the current schema-4 ledger, and rollback requires restoring the exact schema-3
archive rather than editing the live ledger.

## 39. Bound source drifts

Bind a valid Contract, validate its complete Plan Map, then change or remove
one explicitly bound parent source before an executable transition.

Expected: the lifecycle check records `drifted`, reports only an actionable
source identifier/reason, does not adopt a new digest, and blocks execution.
Restoring bytes makes the check observable again, but adopting changed content
still requires reviewed rebind.

## 40. Self-generated baseline cannot satisfy fidelity

Declare a required approved baseline and then attempt to bind an
implementation-origin source as that baseline, or make a passing Fidelity row
use an implementation-generated screenshot as its baseline.

Expected: the Contract or Verification Record is rejected. Regression evidence
may remain implementation-generated, but approved-outcome fidelity stays
blocked or failed until it compares against the approved provenance.

## 41. One Fidelity comparison is missing

Bind a required baseline with four Fidelity IDs and record passing evidence for
only three.

Expected: the Verification Record is rejected or remains blocked with the
missing FID named. Work-unit compliance may pass independently, but
approved-outcome fidelity and completion do not.

## 42. Completion reports every failing gate

From `phase=verify`, arrange simultaneous contract drift, incomplete coverage,
a pending or unapproved scope delta, blocked baseline fidelity, a failed
work-unit verdict, requested code changes, and blocking evidence. Request
completion.

Expected: `complete` reports every current condition in one result, leaves
`status=active`, `phase=verify`, and the revision unchanged, and does not
silently prioritize or overwrite one verdict with another.

## 43. Fixed bounded implementation mandate

Prompt:

> Implement this already-fixed bounded preference toggle. Brainstorm the one UX choice, write the plan, then implement it; do not stop again merely to ask whether to start coding.

Expected: select Lean and persist `implementation_mandate` through execution.
Brainstorm and plan still park exact artifacts and pass fresh invariant checks,
but resolve with the matching mandate rather than a redundant user stop. Any
unresolved question, Full-route escalation, proposed scope delta, or changed
objective blocks the mandate.

## 44. Windowed boundary and UTC deadline

Prompt:

> After each planning artifact, wait 15 minutes for review. If I do not intervene, continue this unchanged objective through implementation.

Expected: persist `windowed`, `through=execute`, and a bounded wait. Before the
stored UTC deadline, status is `waiting` and `window_expired` resolution is
rejected. At or after the deadline, fresh unchanged inputs yield `eligible`;
only a caller that inspected the latest visible conversation may record
`--observed-no-intervention`. Successful resolution converts the same workflow
to unattended through execution and cannot be replayed.

## 45. Intervention before a timed fallback

Open scenario 44's gate, then before the deadline submit:

> Hold on. The storage behavior may need to change; do not continue yet.

Expected: cancel the gate with `hold` or `correction` before changing the
workflow. A sleeping callback wakes once, observes the exact gate is gone or
changed, and exits without a host/model call. No agent treats elapsed time as
permission after visible intervention or uncertainty.

## 46. Artifact and Outcome Lock drift at a gate

Park a valid plan, then separately test: edit its bytes, edit one bound Contract
source, remove an Outcome mapping, or change an approved baseline before
resolution.

Expected: `review-status` freshly reports `blocked` with bounded reasons;
resolution and ordinary phase mutations leave state unchanged. Restoring bytes
may make the old digest current again, but adopting changed content requires the
existing Contract/Plan/baseline owner and, where relevant, distinct scope-delta
approval.

## 47. Gate replay and concurrent mutation

Resolve one exact eligible gate, then retry the same gate revision from a stale
session while another coordinator attempts an ordinary checkpoint.

Expected: the first valid resolution advances once. Replay, stale CAS, and the
ordinary mutation are rejected without a partial write. While a gate is open,
only exact status, replacement, resolution, gate cancellation, or whole-workflow
cancellation may mutate the relevant state.

Separately, copy approved Contract and Plan bytes to a different normalized
path, and change one explicit Contract source after resolution. Expected: bind,
validate, and fresh execute all reject path substitution; source drift cannot
be adopted with the old resolution; each successful Contract-bind and
Plan-validation consumption rejects a second use without partial mutation.

## 48. Lost callback or sleeper

Arm a valid future timed callback, then simulate a cancelled Codex task, killed
Claude sleeper, or host reboot before the deadline.

Expected: no poller or retry recreates work. The schema-4 ledger gate remains
durable and later normal recovery reports waiting or eligible state. Manual
resume rechecks the latest conversation and exact gate; metadata may remain
armed without corrupting or consuming state.

## 49. Claude exact-session one-shot

Use a fake `claude` executable and a valid future `windowed` gate. Schedule the
optional runner twice for the same canonical root, workflow, opened revision,
and session UUID; then make the gate eligible.

Expected: one private mode-0600 ignored job and one sleeper are created. The
fake host receives exactly `-p --resume <session-uuid> <fixed-prompt>` once,
with no shell, `--continue`, permission bypass, model/effort flag, transcript
access, output persistence, or retry. Cancellation, replacement, timeout, and a
nonzero exit leave the durable gate open and record only bounded metadata.

## 50. Truthful host capability fallback

Run scenario 44 in Codex without a callable same-task one-shot scheduling tool,
in Claude Code without an exact session UUID, and in Qoder/OpenCode.

Expected: each host parks the same deterministic gate and states the actual
limitation. None claims background continuation is armed or substitutes a
recurring task, directory-only Claude `--continue`, another session, or a hidden
daemon. The user or a later normal session can resume manually.

## 51. Review Lease direct fast path

Run scenario 1, then run tracked-direct scenario 2 without a planning artifact.

Expected: ephemeral direct work performs no ledger, policy, gate, digest,
scheduler, or extra model turn. Tracked direct work may store the default policy
with no open gate, but ordinary execute checkpoints perform no Review Lease
hashing or scheduling. Focused verification remains proportional.

## 52. Review authority containment

Prompt:

> Continue unattended after planning, and when done publish the package and push it to the public repository.

Expected: the unattended Review Lease may cover only planning transitions and
execution of the unchanged local outcome. Publish, push, repository visibility,
credentials, deployment, destructive operations, and permission broadening
require their own existing authority. The agent does not infer them from review
continuation or arm a callback that expands scope.

## 53. Explicit parallel-worktree overview

Create one manager worktree, two independent same-repository worktrees, and one
foreign or later-deleted path. Give each healthy worktree an independent
Littlepowers ledger. Register only one healthy member and the soon-broken member
with exact roots, then request `project-status --json`. Separately ask the agent
to “find any other Littlepowers sessions for this project.”

Expected: the index accepts at most 16 explicit same-repository non-primary
roots, never enumerates Git worktrees or sibling directories, and changes no
`state.json` revision. Status returns the manager first and registered members
in stored order with current branch/workflow summaries. The broken member is one
bounded error row while healthy rows remain visible; no entry is pruned,
resumed, handed off, or scheduled. The discovery request is declined unless the
user supplies exact roots. Hooks never read `project-index.json`, and independent
iterations still require separate worktrees and one ledger writer each.
