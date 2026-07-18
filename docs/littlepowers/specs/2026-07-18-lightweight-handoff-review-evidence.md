# Lightweight handoff and review evidence specification

Date: 2026-07-18

## Purpose

Make cross-worktree workflow transfer and broad uncommitted review recoverable and evidence-bound without adding steady-state orchestration, model turns, repository scans, or test cost.

## Functional requirements

### Handoff

1. A coordinator can transfer one active or paused source workflow to one explicitly named active target workflow.
2. The operation requires the current source workflow ID/revision and the target root, workflow ID, and revision. It rejects a stale source, stale or terminal target, the same source and target root, an untrusted target ledger, and a mismatched target workflow.
3. A successful transfer marks only the source workflow terminal and non-resumable, records a bounded handoff pointer, and leaves the target ledger byte-for-byte unchanged.
4. The handoff pointer contains the canonical target root, target workflow ID, target revision validated at transfer time, and transfer timestamp. It is recovery data, not authority to read or execute the target.
5. A SessionStart rooted in the source may render one concise transfer notice. Prompt-boundary reminders remain empty for a transferred source. Littlepowers never scans siblings, auto-follows the target, or claims that the current task changed roots.
6. Continuing transferred work requires a new task/session rooted in the target workspace and a fresh target-ledger read.
7. The representation remains schema-2-compatible: a previous schema 2 reader accepts the source as terminal and cannot resume it.

### Review snapshot

8. A read-only command produces a deterministic candidate token for a Git workspace from HEAD, porcelain status, and current content of changed tracked and non-ignored untracked paths.
9. The output contains no file content and exposes only the root, HEAD, token, counts, and bounded byte total needed to explain scope.
10. Identical candidate state produces the same token. A tracked or untracked content/path/status change produces a different token. Ignored-file changes do not change it.
11. The command follows no file symlink, writes no Git object or ledger state, uses no network, and fails closed for excessive file count/bytes or unsupported changed path types.
12. Snapshot work runs only when explicitly requested. Hooks, status rendering, route selection, ordinary checkpoints, and normal local/connected review never invoke it.

### Review scope

13. Broad review of an uncommitted candidate records a token before review and compares it before accepting the verdict. A changed token makes the verdict stale.
14. If one reviewer cannot contain the material diff and contracts, the review is partitioned by real trust, state-ownership, or rollback boundaries. One acceptance owner aggregates shared-interface coverage once.
15. Partitioning does not mandate a reviewer count, create agents, select models, rerun unchanged tests, or turn local/connected review into broad review.

### Termarium coordination

16. The existing Termarium task remains the only writer to its M4 worktree and fixes the two accepted R3 findings: truthful unavailable/unknown receipt presentation and cancellation/join of in-flight Host runtime work during logout or account switch.
17. Termarium uses focused failure-path tests for those findings, then pays its existing aggregate gate only after its finding batch freezes.

## Performance and compatibility constraints

- Python 3 remains the only Littlepowers runtime dependency.
- No daemon, telemetry, global workflow registry, sibling-worktree scan, automatic subagent, model setting, or background watcher is added.
- No new model round is required for direct, compact, or full execution outside a real handoff or broad review decision.
- Codex and Claude Code receive the same host-neutral semantics.
- Existing progress, optimistic concurrency, trust checks, and read-only Hook guarantees remain intact.

## Acceptance criteria

1. Focused state/Hook tests prove valid handoff, stale/mismatched rejection, source non-resumption, unchanged target bytes, and SessionStart-only transfer rendering.
2. Focused snapshot tests prove stability, tracked/untracked sensitivity, ignored-file insensitivity, symlink non-following, bounds, and no mutation.
3. Static skill/eval contracts prove task-root rebinding, snapshot invalidation, bounded review partitioning, and the absence of automatic orchestration language.
4. The previous schema 2 state tool reads a handoff-bearing source and treats it as terminal.
5. Full Python tests, compilation, all skill validators, Codex plugin validation, Claude strict validation, and diff hygiene pass once at the integrated boundary.
6. The staged plugin source is checksum-identical to the verified repository; cache replacement occurs only at a safe new-task boundary.

## Non-goals

- Automatically moving a running Codex or Claude task to another filesystem root.
- Discovering arbitrary related worktrees from a parent directory.
- Replacing Git commits, CI, release signing, or human risk acceptance.
- Guaranteeing that one model or effort setting always invokes a skill.
