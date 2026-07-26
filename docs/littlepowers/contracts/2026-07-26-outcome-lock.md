# Outcome Lock bootstrap contract

Date: 2026-07-26

Status: approved projection of the Outcome Lock specification

This is the machine-checkable projection of
`docs/littlepowers/specs/2026-07-26-outcome-lock.md`. It preserves the exact
OUT-001…OUT-023 identifier set, declares no scope delta, and binds the released
v1.1 compatibility evidence as the approved four-host baseline. The compact
titles identify the outcomes; the specification remains the authoritative
acceptance text.

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "full",
  "sources": [
    {
      "id": "SRC-001",
      "path": "docs/littlepowers/specs/2026-07-26-outcome-lock.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-002",
      "path": "docs/littlepowers/brainstorms/2026-07-26-outcome-lock.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-003",
      "path": "docs/littlepowers/designs/2026-07-26-outcome-lock.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-004",
      "path": "evals/results/2026-07-26-v1.1-scope-integrity.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-005",
      "path": "AGENTS.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-006",
      "path": "docs/littlepowers/specs/2026-07-26-scope-integrity-lean-route.md",
      "role": "requirements",
      "origin": "repository",
      "approved": true
    },
    {
      "id": "SRC-007",
      "path": "docs/littlepowers/designs/2026-07-26-scope-integrity-lean-route.md",
      "role": "compatibility",
      "origin": "repository",
      "approved": true
    }
  ],
  "scope_delta": {
    "status": "none",
    "consequences": []
  },
  "baseline": {
    "requirement": "required",
    "source_ids": [
      "SRC-004"
    ]
  },
  "review": {
    "code_quality_required": true
  },
  "outcomes": [
    {
      "id": "OUT-001",
      "title": "Protocol identity",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "Explicit parent-source binding",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Approved Outcome Contract",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "Contract digest and drift status",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "Legacy Reconciliation Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-006",
      "title": "Outcome Coverage Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-007",
      "title": "Deterministic Scope Delta Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-008",
      "title": "Approved Baseline Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-009",
      "title": "Fidelity Matrix Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-010",
      "title": "Independent review verdicts",
      "disposition": "active"
    },
    {
      "id": "OUT-011",
      "title": "Completion Gate",
      "disposition": "active"
    },
    {
      "id": "OUT-012",
      "title": "Direct-route proportionality",
      "disposition": "active"
    },
    {
      "id": "OUT-013",
      "title": "Lean-route proportionality",
      "disposition": "active"
    },
    {
      "id": "OUT-014",
      "title": "Full-route reuse",
      "disposition": "active"
    },
    {
      "id": "OUT-015",
      "title": "Product scope versus rollback units",
      "disposition": "active"
    },
    {
      "id": "OUT-016",
      "title": "Explicit check boundaries",
      "disposition": "active"
    },
    {
      "id": "OUT-017",
      "title": "Transactional errors and concurrency",
      "disposition": "active"
    },
    {
      "id": "OUT-018",
      "title": "Recoverable migration and rollback",
      "disposition": "active"
    },
    {
      "id": "OUT-019",
      "title": "Compact read-only hook summary",
      "disposition": "active"
    },
    {
      "id": "OUT-020",
      "title": "Bounded dependency-free runtime",
      "disposition": "active"
    },
    {
      "id": "OUT-021",
      "title": "Cross-host consistency",
      "disposition": "active"
    },
    {
      "id": "OUT-022",
      "title": "Behavioral regression coverage",
      "disposition": "active"
    },
    {
      "id": "OUT-023",
      "title": "Integrated verification and claim discipline",
      "disposition": "active"
    }
  ],
  "fidelity": [
    {
      "id": "FID-001",
      "outcome": "OUT-021",
      "baseline": "SRC-004",
      "surface": "Codex",
      "action": "load shared plugin and protocol",
      "state": "schema 3 gates discoverable"
    },
    {
      "id": "FID-002",
      "outcome": "OUT-021",
      "baseline": "SRC-004",
      "surface": "Claude Code",
      "action": "load shared plugin and protocol",
      "state": "schema 3 gates discoverable"
    },
    {
      "id": "FID-003",
      "outcome": "OUT-021",
      "baseline": "SRC-004",
      "surface": "Qoder",
      "action": "load shared plugin and protocol",
      "state": "schema 3 gates discoverable"
    },
    {
      "id": "FID-004",
      "outcome": "OUT-021",
      "baseline": "SRC-004",
      "surface": "OpenCode",
      "action": "load shared plugin and protocol",
      "state": "schema 3 gates discoverable"
    }
  ]
}
```
<!-- /littlepowers:contract -->
