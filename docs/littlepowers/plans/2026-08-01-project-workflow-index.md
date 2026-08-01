# Project Workflow Index — lean implementation plan

Date: 2026-08-01

## Goal

Implement one opt-in, explicit Project Workflow Index that lets a manager
worktree inspect parallel independent Littlepowers worktrees without changing
the one-worktree/one-workflow execution model or adding steady-state overhead.

## Inputs

- Approved lean brainstorm and bound Outcome Contract:
  `docs/littlepowers/brainstorms/2026-08-01-project-workflow-index.md`
- Repository constraints: `AGENTS.md`
- Current public behavior: `README.md`, `README.zh-CN.md`,
  `docs/capability-matrix.md`, and `docs/security-model.md`
- Current shared runtime: `scripts/littlepowers_state.py`

No scope delta. Baseline is not applicable. There are no unresolved product,
security, compatibility, or implementation choices.

## Global constraints

- Keep one continuous approved outcome and one definition of done. Task
  boundaries below are implementation order and rollback units, not product
  slices or staged delivery.
- The root coordinator is the only Littlepowers ledger writer. No worker may
  checkpoint the parent workflow.
- Preserve all existing uncommitted v1.3 candidate changes. Before modifying an
  overlapping file, save a bounded temporary copy so this work unit can be
  reviewed or rolled back independently.
- Use only Python 3 standard-library runtime dependencies.
- Do not change state schema 4, Review Lease, Outcome Lock, member ledgers, Hook
  behavior, plugin discovery, package versions, or host-specific semantics.
- Do not scan sibling worktrees, inspect transcripts, call the network, create
  a daemon, schedule callbacks, add model calls, or run tests from Hooks.
- Run focused checks at each rollback unit and the broad repository suite once
  at the integrated boundary, as required by `AGENTS.md`.
- Commit, push, tag, publish, and local plugin replacement are outside this
  implementation authorization.

## Definition of done

- `project-register`, `project-unregister`, and `project-status [--json]` are
  callable through the shared state CLI on all four hosts.
- The manager root is always shown; up to 16 explicitly registered non-primary
  members must be canonical worktrees from the same Git common repository.
- The independent `.littlepowers/project-index.json` is bounded, ignored,
  trusted, cross-process locked, atomically written, and revisioned without
  changing `state.json` or its workflow revision.
- Status refreshes branch and bounded ledger fields on demand, isolates member
  errors, performs no pruning or writes, and leaves healthy rows visible.
- Public docs and management/router skills explain how to use the index and
  repeat that it is neither a second orchestrator nor multi-workflow support in
  one checkout.
- Focused tests, full unit tests, compilation, changed-skill validation, diff
  hygiene, integrated review, and the six Outcome checks all pass with fresh
  evidence.

## Task 1 — Bounded explicit membership and index storage

**Testable outcome:** A manager worktree can register and unregister only
explicit, distinct worktrees from the same Git common repository, while the
index has independent revisioned atomic storage and the manager ledger bytes
remain unchanged.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_project_index.py`.

**Dependencies and named interfaces:**

- independent schema-1 `project-index.json` with exact keys `schema_version`,
  `revision`, `members`, and `updated_at`;
- member keys `root`, `label`, and `registered_at`;
- constants for 16 members, 2,048-character roots, 80-character labels, and the
  existing 64 KiB store bound;
- shared trusted state-directory, `state_lock`, JSON duplicate-key rejection,
  atomic write, Git worktree identity, and Git-ignore boundaries;
- `command_project_register` and `command_project_unregister` plus CLI
  subcommands.

**Rollback unit:** The index constants, validator, loader/writer, same-repository
identity helper, two mutation commands, parser/dispatch entries, and their
focused tests revert together. They do not depend on status rendering.

**Steps:**

- [ ] Capture a pre-implementation snapshot token and temporary copies of all
      files this work unit may modify.
- [ ] Add exact index/member validation and bounded safe load/write functions
      without generalizing or weakening existing state validation.
- [ ] Resolve the manager and member as canonical Git worktree roots and compare
      their Git common directories without enumerating worktrees.
- [ ] Add explicit register/unregister lifecycle, duplicate/self/foreign/limit
      failures, monotonic index revision, and stable JSON mutation output.
- [ ] Assert that mutation changes only `project-index.json`, never member
      `state.json` or the manager workflow revision.

**Focused validation:**

```bash
python3 -m unittest \
  tests.test_project_index.ProjectIndexMutationTests -v
```

Expected evidence: `test:project-index-lifecycle`,
`test:explicit-membership`, and `security:bounded-index-io`. This is local to
the independently reversible index storage and membership boundary.

## Task 2 — Read-only current status with isolated member failures

**Testable outcome:** One on-demand command displays the manager and every
registered member with fresh branch/workflow summaries; a missing, foreign, or
invalid member produces only its own error row and no filesystem mutation.

**Files:**

- modify `scripts/littlepowers_state.py`;
- extend `tests/test_project_index.py`.

**Dependencies and named interfaces:**

- Task 1 index loader and Git identity helper;
- `command_project_status`, one stable JSON response, and concise text output;
- row fields for role, label, canonical root, branch, error, and a bounded ledger
  summary containing workflow ID, status, phase, progress, next action,
  update time, and Review Gate metadata;
- existing trusted `load_state(..., missing_ok=True)` as the sole member-ledger
  reader.

**Rollback unit:** Status collection, output functions, parser/dispatch entry,
and status tests revert together while Task 1 registration remains usable.

**Steps:**

- [ ] Always produce a primary manager row followed by registered rows in stored
      order, without scanning or sorting sibling paths.
- [ ] Revalidate same-repository identity on every status request and summarize
      each ledger without opening artifacts or changing state.
- [ ] Treat missing ledgers as an explicit non-error `missing` state; isolate
      missing roots, foreign replacements, and invalid ledger data as bounded
      member errors.
- [ ] Prove JSON and text output remain useful when healthy and broken members
      coexist, and prove status leaves index and all ledger bytes unchanged.

**Focused validation:**

```bash
python3 -m unittest tests.test_project_index -v
```

Expected evidence: `test:isolated-status`, `inspection:single-ledger-boundary`,
and `test:existing-ledger-regression`. This covers the complete new CLI behavior
without invoking unrelated broad suites mid-implementation.

## Task 3 — Shared contract documentation and integrated verification

**Testable outcome:** All hosts receive the same documented opt-in commands and
the integrated repository proves the complete six-Outcome contract without
claiming automatic orchestration or same-worktree concurrency.

**Files:**

- modify `README.md` and `README.zh-CN.md`;
- modify `docs/capability-matrix.md` and `docs/security-model.md`;
- modify `skills/managing-littlepowers/SKILL.md` and
  `skills/using-littlepowers/SKILL.md`;
- modify `evals/scenarios.md`, `CHANGELOG.md`, and
  `tests/test_manifests.py`;
- create `docs/littlepowers/evidence/2026-08-01-project-workflow-index.md`.

**Dependencies and named interfaces:**

- Tasks 1–2 command names and response semantics;
- existing four-host shared CLI resolution and root-coordinator ownership;
- Outcome Contract IDs `OUT-001` through `OUT-006`;
- focused skill validators, aggregate Python suite, compilation, and diff
  hygiene.

**Rollback unit:** Public documentation, skill guidance, evaluation scenario,
static assertions, and evidence record revert together. Rollback is coupled to
Tasks 1–2 only because documentation must not advertise absent commands.

**Steps:**

- [ ] Document explicit registration, on-demand overview, isolated errors,
      cleanup, and the unchanged single-workflow/single-writer boundary in both
      languages and the capability/security references.
- [ ] Teach the router and management skill to recommend separate worktrees and
      use the index only when the user explicitly wants a project overview;
      Hooks remain unaware of it.
- [ ] Add one adversarial evaluation scenario and static manifest checks for
      command parity, no discovery, and no orchestration claims.
- [ ] Run the complete new tests, then one aggregate repository suite and
      compilation after the final relevant change.
- [ ] Validate the two changed skills, inspect the complete incremental diff
      against the saved rollback copy, run `git diff --check`, and record the
      three independent review verdicts plus per-Outcome evidence.

**Integrated validation:**

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
git diff --check
```

Also run the official skill validator for the two changed skill directories.
Expected evidence: `test:aggregate-suite`, `host:shared-cli-docs`,
`inspection:hook-nonuse`, and `review:integrated-diff`. The broad suite runs
once because the shared state CLI and public routing contract are aggregate
boundaries.

## Outcome Plan Map

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 1", "Task 2"],
      "evidence": ["test:project-index-lifecycle"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 1"],
      "evidence": ["test:explicit-membership"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 2"],
      "evidence": ["test:isolated-status"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["inspection:single-ledger-boundary", "test:existing-ledger-regression"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 1", "Task 2"],
      "evidence": ["security:bounded-index-io", "inspection:hook-nonuse"]
    },
    {
      "outcome": "OUT-006",
      "tasks": ["Task 3"],
      "evidence": ["test:aggregate-suite", "host:shared-cli-docs", "review:integrated-diff"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
