---
name: managing-littlepowers
description: Inspect or manage a Littlepowers recovery ledger. Use when the user asks for workflow status, health checks, pause, resume, cancel, replacement, cleanup, or troubleshooting in Codex, Claude Code, Qoder, or OpenCode. Do not change product code unless separately requested.
---

# Managing Littlepowers

Operate the recovery ledger without assuming the user's project contains the Littlepowers source tree.

Resolve `<state-cli>` as follows:

- Claude Code expands `${CLAUDE_PLUGIN_ROOT}/scripts/littlepowers_state.py`.
- Qoder CLI expands `${QODER_PLUGIN_ROOT}/scripts/littlepowers_state.py`.
- In Codex or OpenCode, resolve `../../scripts/littlepowers_state.py` from this loaded `SKILL.md` path.

If that path disappeared after a plugin replacement, do not continue from memory. Use the host-native installed-plugin listing described by `using-littlepowers` to resolve exactly one active Littlepowers root, reread this skill there, and then run the state CLI. If resolution is missing or ambiguous, stop and use a new task or session after installation.

Use an available Python 3 launcher. Run `doctor` for trust, ignore, schema, and validity checks; run `show --json` for status. These commands are read-only.

Report the ledger's `progress` as written. If it is absent, describe the current task, completed checkpoints, and next action without inventing a percentage.

Pause, resume, handoff, cancel, checkpoint, and complete require the workflow ID and current revision from `show --json`. Pass both with `--workflow <id> --expect-revision <revision>`. Use the newly returned revision after every mutation.

Completion is valid only from `phase=verify`; checkpoint that phase and gather fresh evidence before completing the workflow.

Examples:

```bash
<python> <state-cli> doctor
<python> <state-cli> show --json
<python> <state-cli> pause --workflow <id> --expect-revision <revision>
<python> <state-cli> resume --workflow <id> --expect-revision <revision>
<python> <state-cli> handoff --workflow <id> --expect-revision <revision> \
  --target-root <absolute-path> \
  --target-workflow <target-id> --target-revision <target-revision>
<python> <state-cli> cancel --workflow <id> --expect-revision <revision>
<python> <state-cli> start --replace \
  --workflow <id> --expect-revision <revision> \
  --objective "<replacement outcome>" \
  --phase <brainstorm|shape|execute> \
  --next-action "<next observable action>"
```

Use `handoff` only for an actual transfer to a different workspace root. The target ledger must already exist and be active. The command verifies that explicit target, then cancels only the source workflow and records a pointer; it never writes the target or changes the current task root. Continue in a new task or session rooted at the target and verify its current state there. Do not scan sibling worktrees to discover a destination.

On a conflict, reload and explain which workflow or revision changed. Do not retry blindly.

Starting with `--replace` archives any current ledger, including a terminal one, and requires its workflow ID and revision. Use it for an active or paused ledger only when the latest request clearly switches objectives; use it for a terminal ledger when beginning the next tracked objective. Uninstalling the plugin does not remove `.littlepowers`; preserve, archive, or delete that local directory only when the user requests cleanup and confirms the exact workspace.
