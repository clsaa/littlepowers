---
name: managing-littlepowers
description: Inspect or manage a Littlepowers recovery ledger. Use when the user asks for workflow status, health checks, pause, resume, cancel, replacement, cleanup, or troubleshooting in Codex or Claude Code. Do not change product code unless separately requested.
---

# Managing Littlepowers

Operate the recovery ledger without assuming the user's project contains the Littlepowers source tree.

Resolve `<state-cli>` as follows:

- Claude Code expands `${CLAUDE_PLUGIN_ROOT}/scripts/littlepowers_state.py`.
- In Codex, resolve `../../scripts/littlepowers_state.py` from this loaded `SKILL.md` path.

Use an available Python 3 launcher. Run `doctor` for trust, ignore, schema, and validity checks; run `show --json` for status. These commands are read-only.

Pause, resume, cancel, checkpoint, and complete require the workflow ID and current revision from `show --json`. Pass both with `--workflow <id> --expect-revision <revision>`. Use the newly returned revision after every mutation.

Completion is valid only from `phase=verify`; checkpoint that phase and gather fresh evidence before completing the workflow.

Examples:

```bash
<python> <state-cli> doctor
<python> <state-cli> show --json
<python> <state-cli> pause --workflow <id> --expect-revision <revision>
<python> <state-cli> resume --workflow <id> --expect-revision <revision>
<python> <state-cli> cancel --workflow <id> --expect-revision <revision>
<python> <state-cli> start --replace \
  --workflow <id> --expect-revision <revision> \
  --objective "<replacement outcome>" \
  --phase <brainstorm|shape|execute> \
  --next-action "<next observable action>"
```

On a conflict, reload and explain which workflow or revision changed. Do not retry blindly.

Starting with `--replace` archives any current ledger, including a terminal one, and requires its workflow ID and revision. Use it for an active or paused ledger only when the latest request clearly switches objectives; use it for a terminal ledger when beginning the next tracked objective. Uninstalling the plugin does not remove `.littlepowers`; preserve, archive, or delete that local directory only when the user requests cleanup and confirms the exact workspace.
