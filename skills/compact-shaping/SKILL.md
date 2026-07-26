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

Keep the brief proportional. If shaping exposes material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback choices, switch to the full route before implementation.

Checkpoint with the current workflow ID and revision:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase execute \
  --artifact shape=<artifact-path> \
  --completed "compact shape" \
  --progress "Compact shape complete; execution is next" \
  --next-action "Execute the first shape step"
```

Use the returned revision, then present the shape brief for review and stop: summarize the selected approach and execution steps, name the artifact path, and name `executing-plans` as the next phase. Invoke `executing-plans` only after explicit approval of this artifact, or immediately when the latest user request explicitly authorized unattended end-to-end execution. When the user asks for corrections, revise this artifact, checkpoint again, and present it again instead of advancing.
