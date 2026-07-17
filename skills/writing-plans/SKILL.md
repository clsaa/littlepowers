---
name: writing-plans
description: Convert an approved specification and technical design into an exact, checkable implementation plan before editing code. Use in the Littlepowers plan phase for multi-step work that needs file paths, dependencies, ordered tasks, verification commands, and completion criteria.
---

# Writing Plans

Produce a plan another capable engineer or agent can execute without rediscovering the design.

## Prepare

Read active state, specification, design, repository instructions, current files, and test commands. Verify that every named path, interface, and command is plausible in the actual codebase. Return to the earlier phase if a material gap prevents a reliable plan.

## Write the plan

Use the repository's convention or default to:

`docs/littlepowers/plans/YYYY-MM-DD-<slug>.md`

Start with the goal, input artifacts, architecture summary, global constraints, and definition of done.

For each task include:

- a testable outcome;
- exact files to create, modify, or verify;
- dependencies and interfaces from adjacent tasks;
- ordered checkbox steps;
- exact validation commands and expected success evidence;
- any user or external decision that blocks the task.

Size a task around one coherent, independently reviewable outcome. Fold setup and docs into the task that needs them. Do not force every action into a tiny step, paste speculative full-file code, or leave placeholders such as TODO, "handle errors", or "add tests".

Order tasks so each leaves the repository in a coherent state. Include final integration verification and a diff review. Include commits only when the user requested a commit-based workflow.

## Review and checkpoint

Map every specification requirement to at least one task. Check paths, names, dependencies, commands, and rollback or migration steps. Fix gaps in the plan.

Resolve `<plugin-root>` by going two directories up from this skill directory, then run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py checkpoint \
  --phase execute \
  --artifact plan=<artifact-path> \
  --completed plan \
  --next-action "Review and execute the first implementation task"
```

Use `executing-plans` next when implementation is authorized.

