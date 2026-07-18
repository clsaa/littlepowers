# Lightweight handoff and review evidence plan

Date: 2026-07-18

Status: approved by the user's end-to-end implementation request; live completion state belongs in the ledger

## Goal and inputs

Implement the approved [specification](../specs/2026-07-18-lightweight-handoff-review-evidence.md) and [design](../designs/2026-07-18-lightweight-handoff-review-evidence.md) while preserving schema-2 compatibility and zero steady-state model/test overhead. Termarium product repairs remain owned by its active Codex task.

## Global constraints

- Python 3 only; hooks remain read-only and never hash repositories.
- No daemon, global index, sibling scan, automatic reviewer, model selection, telemetry, or default full-suite trigger.
- Preserve all existing dirty-worktree changes.
- Do not commit, push, publish, or replace an active plugin cache without separate safe-boundary evidence.
- The root coordinator is the only Littlepowers ledger writer.

## Task 1: Schema-compatible explicit handoff

**Outcome:** An explicit target workflow can receive a source handoff without target mutation or source resumption.

**Files:** `scripts/littlepowers_state.py`, `tests/test_state.py`, `tests/test_hook.py`.

**Interfaces and rollback:** Extend schema 2 with optional `handoff`, add the `handoff` CLI command, and render a SessionStart-only pointer. This unit can be reverted independently; existing cancelled handoff sources remain terminal to old readers.

**Steps:**

- [ ] Normalize and validate the optional handoff object on new, schema-1-migrated, and legacy schema-2 states.
- [ ] Validate the explicit active target identity/revision without writing or locking it, then cancel and checkpoint only the source.
- [ ] Render a bounded source-root SessionStart notice while keeping prompt/subagent reminders silent.
- [ ] Test success, stale/mismatched/self/terminal rejection, target byte stability, non-resumption, bounds, and old-reader compatibility.

**Focused validation:**

```bash
python3 -m unittest tests.test_state tests.test_hook -v
```

Expected evidence: the source advances once to cancelled with an exact pointer; target bytes/revision do not change; invalid transfers leave both ledgers unchanged; Hook output occurs only for SessionStart.

Scope rationale: connected state/Hook contract with coordinated rollback, not yet the full package boundary.

## Task 2: Bounded on-demand review snapshot

**Outcome:** Broad uncommitted review can bind a verdict to one deterministic candidate without Git mutation or background cost.

**Files:** `scripts/littlepowers_state.py`, `tests/test_state.py`.

**Interfaces and rollback:** Add read-only `snapshot` output and bounded file hashing. It is independently removable and is never called by workflow mutation or hooks.

**Steps:**

- [ ] Hash HEAD, porcelain-v2 status, and sorted changed tracked/non-ignored untracked path content with a versioned domain.
- [ ] Handle regular files and symlink targets without following links; reject unsafe paths, special types, excessive count/bytes, or Git failure.
- [ ] Emit content-free JSON counts and token.
- [ ] Test stability, tracked/untracked/path sensitivity, ignored-file insensitivity, symlink non-following, bounds, non-Git rejection, and absence of mutation.

**Focused validation:**

```bash
python3 -m unittest tests.test_state.StateTests.test_snapshot_is_stable_and_tracks_candidate_changes tests.test_state.StateTests.test_snapshot_ignores_ignored_files_and_does_not_follow_symlinks tests.test_state.StateTests.test_snapshot_rejects_excessive_or_unsupported_candidates -v
```

Expected evidence: only relevant candidate changes alter the token; rejected candidates produce no ledger or Git mutation.

Scope rationale: local read-only command with direct unit coverage.

## Task 3: Lightweight routing and review policy

**Outcome:** Skills use handoff and snapshot only at real boundaries and partition an oversized broad review without prescribing agent/model orchestration.

**Files:** `skills/{using-littlepowers,managing-littlepowers,executing-plans,reviewing-changes}/SKILL.md`, `tests/test_manifests.py`, `evals/{README.md,scenarios.md}`, README/security/capability/changelog and matching workflow artifacts.

**Interfaces and rollback:** Concise skill-policy changes are independently reversible from the CLI features.

**Steps:**

- [ ] Require new-task target-root binding after handoff and prohibit sibling scans or transparent root switching.
- [ ] Use snapshot only for broad uncommitted candidates; compare before verdict acceptance.
- [ ] Partition only when material scope cannot fit one reviewer, then aggregate shared boundaries once.
- [ ] State explicitly that Littlepowers creates no reviewer, chooses no model/effort, and adds no normal-route model round or full test.
- [ ] Add static contracts and scenarios for worktree transfer, stale verdicts, oversized review, and ordinary fast-path behavior.

**Focused validation:**

```bash
python3 -m unittest tests.test_manifests -v
for skill in skills/using-littlepowers skills/managing-littlepowers skills/executing-plans skills/reviewing-changes; do
  uv run --no-project --with pyyaml python /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected evidence: contracts name every boundary while ordinary direct/compact/local review stays unchanged.

Scope rationale: connected host-neutral behavioral policy.

## Task 4: Integrated verification and safe staging

**Outcome:** The repository and personal source pass one broad package gate, and Termarium returns focused repair evidence from its owning task.

**Files:** integrated tree, `/Users/nathan/plugins/littlepowers`, Termarium task status only.

**Steps:**

- [ ] Run the aggregate Python suite and compilation once after integration.
- [ ] Validate all 11 skills, Codex plugin, Claude plugin, and diff hygiene.
- [ ] Exercise previous schema-2 reader compatibility with a handoff-bearing source.
- [ ] Measure the on-demand snapshot on the current Termarium worktree and confirm hooks never invoke it.
- [ ] Synchronize the verified tree to the host-listed source and compare checksums.
- [ ] Reinstall only if no active task depends on the current cache; otherwise stage and report the boundary.
- [ ] Read the owning Termarium task's final evidence without editing its worktree.

**Aggregate validation:**

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
for skill in skills/*; do
  uv run --no-project --with pyyaml python /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
uv run --no-project --with pyyaml python /Users/nathan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
claude plugin validate --strict .
git diff --check
```

Expected evidence: every command exits zero; old-reader and snapshot boundary checks pass; staged source is checksum-identical; no claim exceeds available Termarium or install evidence.

Scope rationale: broad state, Hook, packaging, compatibility, and cross-host rollback boundary.

## Definition of done

- Every specification requirement maps to a focused test or static contract.
- Direct, compact, full execution and local/connected review gain no automatic work.
- Handoff and snapshot are explicit commands with bounded failure behavior.
- Broad review evidence cannot silently survive candidate mutation.
- Termarium's product fixes are closed by its owning task or reported as an exact remaining limitation.
