# Lightweight handoff and review evidence design

Date: 2026-07-18

## Design principles

The new behavior is command-driven and dormant by default. It adds no host service, model call, agent dispatch, directory search, or automatic test. The existing state CLI remains the single local runtime.

## Schema-compatible handoff

Keep `schema_version=2` and add optional top-level `handoff`:

```json
{
  "target_root": "/absolute/canonical/worktree",
  "target_workflow_id": "uuid",
  "validated_revision": 12,
  "transferred_at": "RFC3339"
}
```

New and migrated states normalize a missing field to `null`. Validation requires the exact four keys, bounded text, canonical UUID, non-negative revision, canonical absolute target path, and `status=cancelled` when the object is present. Previous schema 2 readers ignore the extra field, accept `cancelled`, and cannot resume it.

`handoff` takes source optimistic-concurrency arguments plus explicit target root/workflow/revision. While holding only the source lock, it reads and validates the trusted target ledger, requires it to be active and at the expected identity/revision, rejects the same root, then marks the source cancelled and writes the pointer. It never locks or writes the target, so there is no cross-worktree lock ordering or false atomicity claim. The target must already exist; if the source write fails, it remains resumable and the coordinator can reconcile rather than guess.

SessionStart renders a bounded transfer notice from an old-root task. `UserPromptSubmit` and `SubagentStart` stay silent for terminal handoffs, avoiding repeated token cost. The notice says to open a new task rooted at the target and reread it; it does not follow the path.

## On-demand candidate snapshot

Add a read-only `snapshot` subcommand. It requires a Git worktree and runs three bounded local Git queries:

- `rev-parse --verify HEAD`;
- `status --porcelain=v2 -z --untracked-files=all`;
- `diff --name-only -z HEAD` plus `ls-files --others --exclude-standard -z`.

Hash a versioned domain separator, canonical root, HEAD, raw porcelain status, and each sorted changed path with its lstat type/mode and raw regular-file bytes or symlink target text. Never follow symlinks. Reject changed directories/special files, more than 10,000 paths, more than 64 MiB of candidate file content, malformed/non-relative paths, or Git command failure. Hashing the status preserves deletion/rename/index facts; hashing current path content detects working-tree changes without materializing a binary diff or writing Git objects.

Return JSON containing `snapshot_version`, root, HEAD, SHA-256 token, changed-path count, untracked count, and hashed bytes. The command does not require or mutate a ledger.

This token is candidate identity, not a release signature. Submodules or unsupported path kinds fail closed rather than producing incomplete evidence.

## Review routing

Keep local and connected review unchanged. For broad review:

1. If a candidate commit already identifies the reviewed tree, record it; do not run `snapshot` ceremonially.
2. Otherwise run `snapshot` once before review and once before accepting the verdict.
3. If the token changed, invalidate the verdict and review only the invalidated boundary again.
4. If one review context cannot contain the material diff and contracts, partition by trust/state ownership/rollback boundary. One acceptance owner checks shared interfaces and combines verdicts.

Littlepowers provides the rule and token only. The host and user decide whether reviewers exist and which model/effort to use.

## Skill and documentation changes

- `using-littlepowers`: require a new task rooted at a handoff target; never scan or hot-switch roots.
- `managing-littlepowers`: document the handoff command and terminal semantics.
- `reviewing-changes`: add conditional snapshot and bounded partition/aggregation guidance.
- `executing-plans`: mention handoff only at an actual workspace transfer boundary.
- README, security model, capability matrix, changelog, and evals: document the dormant-by-default cost model and limitations.

## Verification mapping

- Handoff schema and transitions: state unit tests.
- SessionStart-only pointer: Hook tests.
- Snapshot identity and safety: temporary Git repository tests.
- No automatic overhead/orchestration language: manifest contract tests.
- Cross-host package behavior: all skill validators and both plugin validators.
- Termarium product fixes: evidence remains in its owning task and is not copied into Littlepowers tests.

## Rollback

Handoff state support, snapshot command, and skill policy are independently reversible code/doc groups. Removing new-reader handoff rendering still leaves old sources safely cancelled. Removing snapshot guidance returns broad review to commit/diff evidence without affecting workflow execution.
