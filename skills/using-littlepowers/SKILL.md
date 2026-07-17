---
name: using-littlepowers
description: Route non-trivial software changes through Littlepowers and restore unfinished work. Use when a request is ambiguous, architectural, risky, spans multiple files, asks to continue or resume prior work, or explicitly requests brainstorm, spec, design, and plan stages. Do not use for simple explanations, read-only reviews, or tiny fully specified edits unless the user requests it.
---

# Using Littlepowers

Keep deliberate work moving without turning every edit into a ceremony.

## Start by recovering state

Resolve `<plugin-root>` by going two directories up from this skill directory. Run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py context
```

If it prints active state, read every referenced artifact and continue from `Next action`. If it prints paused state, preserve it and wait for an explicit resume. Do not silently replace either state.

Interpret a follow-up while work is active as follows:

- Added information, correction, or constraint: update the objective or plan, checkpoint, then continue.
- Question or status request: answer briefly, then return to `Next action`.
- Pause request: checkpoint and run `pause`.
- Clear replacement or cancellation: checkpoint, then run `cancel` or `start --replace` before switching.

## Classify new work

Use the direct path only when the work is fully specified, local, reversible, low-risk, and small enough that design choices are immaterial. Inspect, edit, and verify it proportionally.

Use the shaped path when any of these are true:

- requirements or success criteria are unclear;
- behavior, architecture, data, security, or compatibility choices matter;
- the change spans components or several files;
- failure is costly or rollback is difficult;
- the user explicitly asks for the workflow.

When uncertain, use the shaped path but keep each artifact as short as the task allows.

## Run the shaped path

Follow this order:

1. `brainstorming`
2. `writing-specs`
3. `designing-solutions`
4. `writing-plans`
5. `executing-plans`

Do not implement before the plan unless the user explicitly asks to skip or combine phases. User instructions override this workflow.

Start state before the first phase:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py start \
  --objective "<measurable outcome>" \
  --phase brainstorm \
  --next-action "Create the brainstorm artifact"
```

If the user requests an end-to-end result and no material decision needs them, proceed between phases without artificial approval stops. Pause for a choice only when alternatives change scope, behavior, cost, risk, or external state.

For long work, recommend `/goal` with a measurable outcome. Recommend Queue for follow-up behavior and `/side` or `/btw` for unrelated questions; do not change those settings yourself.

Never commit, branch, push, open a PR, or broaden access merely because this workflow is active. Do those only when the user requests them or they are an ordinary, authorized part of the stated delivery.
