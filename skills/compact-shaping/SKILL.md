---
name: compact-shaping
description: Create one concise shape brief. Use only when routed by using-littlepowers or active state phase=shape.
---

# Compact shaping

Resolve the few decisions that matter without producing four separate documents or narrowing the approved outcome.

Read the active ledger, highest-authority parent acceptance sources, approved baselines, and relevant repository evidence. Ask only when a missing answer materially changes behavior, cost, risk, or scope. Do not reopen settled choices.

For an existing workflow, keep the artifact root already resolved by `using-littlepowers`. When resolving a new workflow, use a non-default root only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not qualify by themselves. Otherwise use `docs/littlepowers/shapes/YYYY-MM-DD-<slug>.md`. Include:

- measurable outcome and non-goals;
- constraints and low-risk assumptions;
- requirements and acceptance checks;
- selected approach and decision rationale;
- affected files or components;
- ordered execution steps and validation commands.

Include the inherited complete outcome and `Added / Changed / Deferred / Removed`, or `No scope delta`. Do not create product or technical slices; ordered steps are implementation order only. Highlight and obtain explicit approval for any non-empty scope delta.

Read
[`../../references/outcome-lock.md`](../../references/outcome-lock.md). Include
one Outcome Contract and one Outcome Plan Map in the shape. Give each complete
observable outcome a stable `OUT-###` ID and map every active ID to a task and
named evidence. The shape is one artifact, not a reason to add a specification,
design, or separate plan.

Keep the brief proportional. If shaping exposes material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback choices, switch to the full route before implementation.

Checkpoint with the current workflow ID and revision:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase shape \
  --artifact shape=<artifact-path> \
  --completed shape \
  --progress "Compact shape complete; execution is next" \
  --next-action "Review, bind, and validate the compact shape"
```

Use the returned revision, read
[`../../references/review-lease.md`](../../references/review-lease.md), and
`park-review --artifact-key shape` with the Contract scope state and
open-question count. The fresh gate check validates the embedded Contract and
complete Plan Map. For a blocking policy, present the shape brief for review
and stop: summarize the selected approach and execution steps, name the
artifact path, and name `executing-plans` as the next phase. Resolve an exact
eligible implementation mandate, unattended gate, or expired window with its
matching kind. Then bind with the corresponding approval kind and run
`validate-plan --artifact <artifact-path>`; a distinctly approved blocking
gate uses `review-gate`, and delta approval remains separate. After both
commands succeed, checkpoint `--phase execute` and invoke `executing-plans`. A
correction cancels the gate, revises/checkpoints the same shape, and parks it
again instead of advancing.
