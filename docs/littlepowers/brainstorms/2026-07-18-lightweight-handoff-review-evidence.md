# Lightweight handoff and review evidence brainstorm

Date: 2026-07-18

## Problem

Termarium exposed two continuity gaps after the earlier runtime iteration:

- moving an objective to a sibling Git worktree was represented as a resumable paused workflow with a path in `next_action`; a task rooted above both worktrees cannot discover either ledger automatically;
- a branch-sized uncommitted R3 review had no immutable candidate identity, and one broad reviewer exhausted useful context before reaching a verdict.

The repair must not turn Littlepowers into an orchestrator or slow capable models with extra planning turns, background agents, sibling-directory scans, or default full-suite gates.

## Constraints and non-goals

- Keep schema 2 readable by the previous implementation.
- Keep hooks read-only, local, silent on failure, and free of network or transcript access.
- Add no daemon, global workflow index, model selection, subagent dispatch, or per-prompt repository hashing.
- Do not auto-follow a ledger path outside the current workspace.
- Do not require commits, because commit authority remains with the user.
- Leave the active Termarium worktree to its owning task; coordinate rather than edit it concurrently.

## Options

### 1. Skill-only conventions

Tell coordinators to cancel an old workflow, start a target workflow, and paste Git hashes into review prompts.

This has almost no code cost, but it cannot validate the target workflow, cannot preserve a safe handoff pointer, and repeats fragile hashing logic in model context.

### 2. Schema-compatible, on-demand CLI boundaries — selected

Add an optional `handoff` object while retaining schema 2. A handoff command validates one explicit target ledger, marks the source `cancelled`, and stores the target root, workflow ID, validated revision, and timestamp. New hooks may show a one-time SessionStart pointer from the old root, but never scan for or auto-open the target. Previous schema 2 readers ignore the extra field and still refuse to resume the cancelled source.

Add an on-demand `snapshot` command that hashes Git HEAD, porcelain status, and the bounded content of changed tracked and untracked files without modifying Git. Broad review guidance uses it only when there is no immutable candidate commit, compares the token after review, and invalidates a stale verdict.

When one reviewer cannot contain a material cross-system scope, split by trust or ownership boundary and aggregate cross-boundary acceptance once. Local and connected reviews keep their current single-pass behavior.

This adds deterministic work only at explicit handoff and broad-review boundaries. It adds no steady-state model turns or default tests.

### 3. Global workflow registry and automatic reviewer orchestration

Maintain a user-global worktree index, scan sibling repositories, spawn specialist reviewers, and merge their verdicts automatically.

This could find moved work automatically, but it adds hidden state, privacy and trust problems, model contention, and the exact latency/“左右互搏” behavior the user wants to avoid. Reject it.

## Success measures

- A validated handoff cannot be resumed at the source, does not mutate the target, and emits no prompt-boundary reminder after SessionStart.
- A task outside the target worktree is told to start a new task rooted there; Littlepowers never claims transparent cross-worktree continuation.
- A changed candidate produces a different snapshot token; ignored files do not; excessive or unsupported input fails closed.
- Hooks and ordinary direct/compact/full execution do not run snapshot logic or create reviewers.
- Existing schema 2 readers accept handoff-bearing and progress-bearing ledgers.
- Focused tests cover both commands before one aggregate plugin validation boundary.

## Open questions

None. The user explicitly authorized implementation and prioritized low execution overhead.
