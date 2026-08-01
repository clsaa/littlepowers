---
name: managing-littlepowers
description: Inspect or manage Littlepowers ledger status, health, pause, resume, cancel, replacement, cleanup, or troubleshooting. Do not edit product code.
---

# Managing Littlepowers

Operate the recovery ledger without assuming the user's project contains the Littlepowers source tree.

Resolve `<state-cli>` as follows:

- Claude Code expands `${CLAUDE_PLUGIN_ROOT}/scripts/littlepowers_state.py`.
- Qoder CLI expands `${QODER_PLUGIN_ROOT}/scripts/littlepowers_state.py`.
- In Codex or OpenCode, resolve `../../scripts/littlepowers_state.py` from this loaded `SKILL.md` path.

If that path disappeared after a plugin replacement, do not continue from memory. Use the host-native installed-plugin listing described by `using-littlepowers` to resolve exactly one active Littlepowers root, reread this skill there, and then run the state CLI. If resolution is missing or ambiguous, stop and use a new task or session after installation.

Use an available Python 3 launcher. Run `doctor` for trust, ignore, schema, and validity checks; run `show --json` for status. These commands are read-only.

Report the ledger's `progress` as written. If it is absent, describe the current task, completed checkpoints, and next action without inventing a percentage. Also report the stored contract, coverage, baseline, fidelity, review policy, gate key/state, and deadline summary. These are last-known facts; `show`, context, and Hook commands do not refresh files. For an open gate, run `review-status --workflow <id> --gate-revision <opened-revision> --json` when the user asks for current eligibility.

When the user explicitly asks for an overview of independent iterations in the
same Git project, use the opt-in Project Workflow Index. The global `--root`
must name the exact manager worktree. Register and unregister only roots the
user or current task explicitly supplied; never search siblings or infer likely
worktrees. `project-status` is read-only, reports the manager plus stored
members, isolates per-member errors, and never changes, resumes, hands off, or
prunes a workflow. The index is not a second ledger and does not allow multiple
top-level workflows in one worktree.

If the lock is `reconcile_required`, explain that active legacy implementation
cannot continue until the approved contract is bound and its Plan Map passes.
If it is `drifted`, use `check-contract` for an explicit observation and require
approved rebind for changed content. Do not repair either condition by editing
`.littlepowers/state.json`.

Pause, resume, handoff, cancel, checkpoint, and complete require the workflow ID and current revision from `show --json`. Pass both with `--workflow <id> --expect-revision <revision>`. Use the newly returned revision after every mutation.

Completion is valid only from `phase=verify` after a current bound contract,
passing coverage, a recorded Verification Record, passing work-unit and
approved-outcome fidelity verdicts, required code-quality approval, and zero
blockers. The completion command performs fresh deterministic checks and lists
all failures.

An open Review Gate blocks ordinary checkpoint, bind/check/validate,
pause/resume, handoff, and completion mutations. Use the exact
policy-matching `resolve-review`, replace the same corrected artifact, or
`cancel-review` before another lifecycle operation. Whole-workflow cancellation
remains available. Do not edit the raw ledger.

Examples:

```bash
<python> <state-cli> doctor
<python> <state-cli> show --json
<python> <state-cli> --root <manager-root> project-register \
  --member-root <explicit-worktree-root> [--label <label>]
<python> <state-cli> --root <manager-root> project-status --json
<python> <state-cli> --root <manager-root> project-unregister \
  --member-root <explicit-worktree-root>
<python> <state-cli> review-status \
  --workflow <id> --gate-revision <opened-revision> --json
<python> <state-cli> set-review-policy \
  --workflow <id> --expect-revision <revision> \
  --mode <blocking|implementation_mandate|windowed|unattended> \
  [--through <next_phase|execute> --wait-seconds <60..604800>]
<python> <state-cli> cancel-review \
  --workflow <id> --expect-revision <revision> --reason <reason>
<python> <state-cli> check-contract \
  --workflow <id> --expect-revision <revision>
<python> <state-cli> bind-contract \
  --workflow <id> --expect-revision <revision> \
  --artifact <contract.md> --approval-kind review-gate
<python> <state-cli> validate-plan \
  --workflow <id> --expect-revision <revision> --artifact <plan-or-shape.md>
<python> <state-cli> record-verification \
  --workflow <id> --expect-revision <revision> --artifact <verification.md>
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

The bracketed policy pair is mandatory only for `windowed`. Contract binding
and Plan validation also require and once consume the matching successful
Review Gate resolution for the original path, bytes, and declared source
digests; the displayed `approval-kind` is not standalone authorization.

Use `handoff` only for an actual transfer to a different workspace root. The target ledger must already exist and be active. The command verifies that explicit target, then cancels only the source workflow and records a pointer; it never writes the target or changes the current task root. Continue in a new task or session rooted at the target and verify its current state there. Do not scan sibling worktrees to discover a destination.

On a conflict, reload and explain which workflow or revision changed. Do not retry blindly.

Starting with `--replace` archives any current ledger, including a terminal one, and requires its workflow ID and revision. Use it for an active or paused ledger only when the latest request clearly switches objectives; use it for a terminal ledger when beginning the next tracked objective. Uninstalling the plugin does not remove `.littlepowers`; preserve, archive, or delete that local directory only when the user requests cleanup and confirms the exact workspace.

`project-unregister` removes only index membership and remains usable after a
registered worktree was deleted. It never deletes a worktree, branch, ledger,
or archive. `doctor` validates a present index without visiting member roots.

Schema 4's first successful mutation of a schema-1/2/3 ledger writes one
byte-identical matching `pre-schema4` archive. A 1.2 runtime cannot read schema
4; stop all writers and restore the exact matching archive before an explicit
runtime rollback. Never downgrade the live ledger in place.
