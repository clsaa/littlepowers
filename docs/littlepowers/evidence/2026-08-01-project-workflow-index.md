# Project Workflow Index — verification evidence

Date: 2026-08-01

## Reviewed outcome

The approved lean outcome is one opt-in manager-root index for independent
same-repository worktrees. Every worktree retains one workflow ledger and one
writer. Registration is explicit and bounded; status is on-demand and
read-only; Hooks and ordinary routing never load the index.

This is a broad verification boundary because the shared state CLI, trusted
runtime storage, public management contract, and all four host surfaces are
affected. Focused checks were run at the rollback units, followed by the
aggregate suite once after integration.

## Rollback and candidate boundary

- Pre-implementation candidate token:
  `sha256:71be8959cc6ce5accd88d98dffe3cff105db25e7fe7193b22d1c8252e720ae01`.
- Pre-change copies of every overlapping file were retained at
  `/tmp/littlepowers-project-index-rollback.H8Uex4` for incremental inspection
  and bounded rollback during this task.
- The implementation is recorded under `[Unreleased]`; it does not change a
  package version, manifest, Hook, plugin installation, tag, or release.

## Fresh evidence

| Claim | Evidence | Result |
| --- | --- | --- |
| Explicit membership, independent index revision, unchanged manager/member ledgers, bounded labels/counts, linked/self/duplicate/foreign rejection, and member inspection-error isolation | `python3 -m unittest tests.test_project_index` | 19 tests passed in 3.884s |
| Public commands, four-host shared guidance, no Hook/index coupling, no worktree enumeration | `python3 -m unittest tests.test_manifests` and integrated manifest cases | 26 focused manifest tests passed; the same cases passed in the aggregate suite |
| Existing Outcome Lock, Review Lease, state migration, Hook, handoff, snapshot, host, and new index behavior remain integrated | `python3 -m unittest discover -s tests -v` | 182 tests passed in 18.434s |
| Python sources compile | `python3 -m compileall -q scripts hooks tests` | Exit 0 |
| Both changed skills have valid frontmatter and names | system `quick_validate.py` against `skills/managing-littlepowers` and `skills/using-littlepowers` with temporary validator-only PyYAML | Both reported `Skill is valid!` |
| Patch has no whitespace errors | `git diff --check` | Exit 0 |

The focused review first found that resolving a member path before checking its
type accepted a final-component directory symlink. A regression test reproduced
the failure, the explicit input root is now rejected before canonicalization,
and the focused and aggregate suites pass after the repair. Parent-path aliases
such as macOS `/var` remain valid because the canonical worktree itself is still
opened through the existing non-link workspace boundary.

The final review also found that a raw permission error while inspecting one
member path could escape the per-member error boundary. A second regression
reproduced that failure; Git identity inspection now normalizes that operating-
system error to a bounded `StateError`, so the manager and healthy rows remain
available. The 182-test aggregate run above is the fresh post-repair result.

## Outcome traceability

- `OUT-001`: exact schema-1 index storage and lifecycle tests prove that the
  manager index is independent of both worktree ledgers.
- `OUT-002`: real Git worktree tests cover explicit register/unregister,
  duplicate, self, foreign, linked, missing, and bounded membership cases; the
  implementation contains no `git worktree list` or sibling scan.
- `OUT-003`: status tests refresh manager/member branch and ledger summaries,
  isolate missing/foreign/corrupt members, and compare index and ledger bytes
  before and after reads.
- `OUT-004`: the index has no workflow mutation command, member status uses the
  existing trusted `load_state`, and tests prove manager/member workflow
  revisions remain unchanged.
- `OUT-005`: index writes reuse the manager lock and atomic store I/O; the Hook
  contains no index/status reference and the new path performs no network,
  scheduling, transcript, telemetry, model, or agent work.
- `OUT-006`: the shared Python CLI and shared skills are the only behavior
  surface; English/Chinese docs and the capability/security contracts describe
  identical Codex, Claude Code, Qoder, and OpenCode semantics.

## Integrated review

- Work-unit compliance: `pass` — all six mapped Outcomes are implemented with
  focused and aggregate evidence and no scope delta.
- Approved-outcome fidelity: `pass` — the final behavior preserves the
  highest-authority one-worktree/one-workflow and coordinator-only ownership
  contracts; no narrower technical slice replaced the approved outcome.
- Code quality: `approve` — no blocking findings remain after the linked-root
  repair. Storage is exact, bounded, locally trusted, locked, atomic, and
  independently revisioned; per-member failures are isolated.

Residual limitation: verification ran locally on macOS and proves host parity
through the shared implementation and static host contracts. This task did not
run remote Windows/Linux CI or authenticated GPT/Claude sessions, and makes no
release or installed-runtime claim.

## Verification Record

<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": [
      "test:project-index-lifecycle",
      "test:isolated-status",
      "test:aggregate-suite"
    ]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": ["inspection:outcome-traceability"]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": ["review:integrated-diff"]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": ["test:project-index-lifecycle"]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": ["test:explicit-membership", "security:bounded-index-io"]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": ["test:isolated-status"]
    },
    {
      "outcome": "OUT-004",
      "status": "pass",
      "evidence": [
        "inspection:single-ledger-boundary",
        "test:existing-ledger-regression"
      ]
    },
    {
      "outcome": "OUT-005",
      "status": "pass",
      "evidence": ["security:bounded-index-io", "inspection:hook-nonuse"]
    },
    {
      "outcome": "OUT-006",
      "status": "pass",
      "evidence": [
        "test:aggregate-suite",
        "host:shared-cli-docs",
        "review:integrated-diff"
      ]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
