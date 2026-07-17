---
name: executing-plans
description: Execute and verify an approved Littlepowers implementation plan while preserving progress across turns. Use when a plan exists, when resuming unfinished implementation, or when follow-up messages arrive during active work. Do not mark completion without fresh verification evidence.
---

# Executing Plans

Carry the approved plan to a verified result and keep durable checkpoints.

## Recover and review

Resolve `<plugin-root>` by going two directories up from this skill directory. Run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py context
```

Read the plan, specification, design, current diff, and repository instructions. Compare the plan with the current code before editing. Fix small stale details in the plan; stop for user input only when a gap changes behavior, scope, cost, risk, or external state.

Mirror plan tasks into the available task tracker. Keep at most one task in progress.

## Execute

For each task:

1. Checkpoint the exact task and next action before making material changes.
2. Preserve unrelated user changes and the existing architecture.
3. Follow the task's dependency order.
4. Add or update tests when behavior changes; use the repository's established validation style.
5. Run the task-level checks and inspect their output.
6. Review the diff against the task outcome.
7. Checkpoint the completed task and the next task.

Example checkpoint:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py checkpoint \
  --phase execute \
  --current-task "Task 2: recovery hook" \
  --completed "Task 1: state CLI" \
  --next-action "Implement and test the SessionStart hook"
```

Treat follow-up corrections and questions according to `using-littlepowers`: address them, update artifacts if requirements changed, and return to the recorded next action. Pause, cancel, or replace only on clear user intent.

Do not commit, push, open a PR, deploy, or mutate external systems unless the user authorized that delivery action.

## Verify and finish

After all tasks:

1. Set phase to `verify` and record the full verification command.
2. Run targeted tests, then the relevant broader checks.
3. Compare the delivered behavior with every acceptance criterion.
4. Inspect the complete diff for omissions, regressions, debug artifacts, and unintended files.
5. Record any limitation honestly.

Only after fresh evidence shows no required work remains, run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py complete
```

Report the outcome, changed surfaces, verification evidence, and any optional next step.
