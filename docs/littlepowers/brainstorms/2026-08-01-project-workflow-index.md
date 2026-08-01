# Project Workflow Index — lean brainstorm

Date: 2026-08-01

## Problem

Littlepowers intentionally keeps one current top-level workflow in one
worktree-local `.littlepowers/state.json`. That is the correct execution and
write-isolation boundary, but a maintainer running several independent
iterations of the same Git project has no lightweight way to see those
workflows together. Opening multiple sessions against one worktree would create
semantic multi-writer ambiguity; manually searching sibling directories would
violate Littlepowers' explicit-root and no-scan boundaries.

## Approved outcome and constraints

Add an opt-in Project Workflow Index that gives one explicitly selected manager
worktree an on-demand overview of its own workflow plus explicitly registered
worktrees from the same Git repository.

The complete outcome must preserve these inherited behaviors:

- every worktree keeps exactly one independent `state.json` and one ledger
  writer;
- independent top-level outcomes use separate Git worktrees, while workers for
  one outcome remain read-only ledger participants;
- registration never scans siblings or infers likely worktrees;
- status is read-only and never checkpoints, resumes, cancels, hands off, or
  otherwise mutates a member ledger;
- hooks do not load the index, so ordinary prompts pay no additional Git,
  filesystem, model, or orchestration cost;
- the shared implementation remains Python-standard-library-only and available
  through the same CLI in Codex, Claude Code, Qoder, and OpenCode;
- runtime state remains ignored by Git, bounded, locally owned, non-linked,
  atomically written, and free of transcript content, telemetry, and network
  access.

## Options

### A. Multiple workflow files in one worktree

Store `.littlepowers/workflows/<id>.json` and let each session select a slot.
This makes simultaneous agents edit the same checkout, weakens the meaning of
the current contract and completion gate, and turns conflict avoidance into a
product concern. Rejected.

### B. Global registry with automatic worktree discovery

Store a user-wide database and scan repositories or sibling directories for
ledgers. This gives convenient discovery but adds global lifecycle, privacy,
staleness, and cleanup behavior that is disproportionate to the need. Rejected.

### C. Explicit manager-root index with on-demand status

Keep `.littlepowers/project-index.json` beside the manager worktree's normal
ledger. Register and unregister exact member roots explicitly. `project-status`
reads the manager root and registered roots only, derives their current branch
and ledger summary on demand, and reports per-member errors without mutating or
pruning anything. Selected.

## Selected interface

The existing global `--root` identifies the manager worktree:

```text
littlepowers_state.py --root /project project-register \
  --member-root /project-search --label search
littlepowers_state.py --root /project project-unregister \
  --member-root /project-search
littlepowers_state.py --root /project project-status [--json]
```

The primary manager root is always included in status and is never stored as a
member. A registered entry stores only its canonical absolute root, optional
label, and registration timestamp. Branch, workflow ID, ledger status, phase,
progress, next action, update time, and Review Gate summary are refreshed from
the current member at display time.

Registration accepts at most 16 distinct non-primary Git worktrees whose Git
common directory matches the manager root. It rejects foreign repositories,
linked or non-directory roots, duplicate roots, unsafe labels, and an oversized
index. Unregistration remains possible for a missing worktree by matching its
stored canonical path. A missing, invalid, moved, or foreign member is returned
as an isolated error row; other rows remain visible and the index is not
silently repaired.

Index writes reuse the manager root's trusted `.littlepowers` directory,
cross-process lock, size limit, and atomic replacement. They do not require or
change the workflow revision because the index is coordination metadata rather
than execution authority. The index has its own small schema and monotonic
revision.

## Decision rationale

Option C solves the visibility problem while retaining the existing safety
model. The steady-state cost is zero because no Hook or normal route reads the
index. The explicit commands are easy to explain, test, roll back, and use from
all four hosts. Keeping execution state out of the index prevents it from
becoming a second orchestrator or another source of workflow truth.

## Scope anchor

Approved outcome: provide a lightweight, explicit, read-only overview for
parallel independent Littlepowers worktrees without enabling concurrent
workflows in one checkout.

Highest-authority parent sources:

- the latest user request to provide a lightweight solution and execute it;
- `AGENTS.md` for repository-wide runtime, host, Hook, ownership, and test
  constraints;
- `README.zh-CN.md` for the public one-worktree/one-workflow contract;
- `scripts/littlepowers_state.py` for the current ledger and storage boundary;
- `docs/security-model.md` for write integrity and multi-agent isolation.

No scope delta.

Baseline provenance: not applicable. This change has no approved visual,
interaction, or output-format baseline.

## Measurable success

- One manager worktree can explicitly register and unregister up to 16 sibling
  worktrees from the same Git repository.
- One on-demand command returns the manager plus every registered member with
  freshly read branch and bounded ledger summary.
- A bad member produces a local error row without hiding healthy members or
  changing any member ledger or index membership.
- Existing `state.json`, Review Lease, Outcome Lock, Hook output, and
  one-writer semantics remain unchanged.
- Focused index tests and the aggregate repository suite pass on the integrated
  candidate; public documentation describes the boundary and commands.

## Assumptions and open questions

- The manager root is itself a Git worktree and is the explicit place from
  which the user wants the overview.
- Registered worktrees may be removed later; explicit unregister handles
  cleanup without requiring the missing path to exist.
- Cross-repository portfolios and automatic scheduling are non-goals.
- Open questions: none.

## Outcome Contract

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "lean",
  "sources": [
    {
      "id": "SRC-001",
      "path": "AGENTS.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-002",
      "path": "README.zh-CN.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-003",
      "path": "scripts/littlepowers_state.py",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-004",
      "path": "docs/security-model.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-005",
      "path": "docs/littlepowers/brainstorms/2026-08-01-project-workflow-index.md",
      "role": "requirements",
      "origin": "implementation",
      "approved": true
    }
  ],
  "scope_delta": {
    "status": "none",
    "consequences": []
  },
  "baseline": {
    "requirement": "not_applicable",
    "source_ids": []
  },
  "review": {
    "code_quality_required": true
  },
  "outcomes": [
    {
      "id": "OUT-001",
      "title": "An explicit manager-root index represents parallel independent worktrees without replacing their individual ledgers",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "Register and unregister accept only explicit bounded same-repository worktree membership and never discover siblings",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "On-demand status returns fresh bounded branch and workflow summaries while isolating member failures and making no member writes",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "One-worktree one-workflow and coordinator-only ledger ownership remain unchanged",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "Index storage reuses bounded trusted local locking and atomic I/O with no Hook background network transcript telemetry or model cost",
      "disposition": "active"
    },
    {
      "id": "OUT-006",
      "title": "Shared CLI documentation and regression evidence cover Codex Claude Code Qoder and OpenCode without host-specific semantics",
      "disposition": "active"
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->
