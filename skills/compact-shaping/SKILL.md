---
name: compact-shaping
description: Create one concise Littlepowers shape brief for moderate software work. Use only when using-littlepowers selected the compact route or active state says phase=shape. Use the full phase skills for material unresolved architecture, security, migration, cross-system, irreversible, or costly choices, or when explicitly requested.
---

# Compact shaping

Resolve the few decisions that matter without producing four separate documents.

Read the active ledger and relevant repository evidence. Ask only when a missing answer materially changes behavior, cost, risk, or scope. Do not reopen settled choices.

Use the repository's artifact convention, or default to `docs/littlepowers/shapes/YYYY-MM-DD-<slug>.md`. Include:

- measurable outcome and non-goals;
- constraints and low-risk assumptions;
- requirements and acceptance checks;
- selected approach and decision rationale;
- affected files or components;
- ordered execution steps and validation commands.

Keep the brief proportional. If shaping exposes material unresolved architecture, security, migration, cross-system, irreversible-state, or costly-rollback choices, switch to the full route before implementation.

Checkpoint with the current workflow ID and revision:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase execute \
  --artifact shape=<artifact-path> \
  --completed "compact shape" \
  --next-action "Execute the first shape step"
```

Use the returned revision, then invoke `executing-plans`.
