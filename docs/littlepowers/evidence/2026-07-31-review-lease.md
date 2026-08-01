# Review Lease verification record

Date: 2026-07-31

Candidate: `1.3.0-alpha.1`

Scope delta: No scope delta.

Approved baseline: Not applicable.

The integrated code candidate was reviewed without mutation at snapshot
`sha256:fa25c3cd5e9c0a8d5a66e9d939bfec1d288cde18097814ab586620b897eaba03`.
Fresh commands, counts, host versions, repaired review findings, and limitations
are recorded in `evals/results/2026-07-31-v1.3-review-lease.md`.

<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": [
      "test:full-suite-162",
      "host:cross-host-validation"
    ]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": [
      "inspection:outcome-traceability",
      "review:integrated-candidate"
    ]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": [
      "review:integrated-candidate",
      "test:concurrent-runner-claim"
    ]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": ["test:review-policy-schema"]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": ["test:review-intent-routing"]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": ["test:artifact-bound-gate", "security:bounded-gate-reader"]
    },
    {
      "outcome": "OUT-004",
      "status": "pass",
      "evidence": ["test:blocking-gate"]
    },
    {
      "outcome": "OUT-005",
      "status": "pass",
      "evidence": ["test:implementation-mandate"]
    },
    {
      "outcome": "OUT-006",
      "status": "pass",
      "evidence": ["test:window-boundaries", "test:one-shot-resume"]
    },
    {
      "outcome": "OUT-007",
      "status": "pass",
      "evidence": ["test:unattended-gate"]
    },
    {
      "outcome": "OUT-008",
      "status": "pass",
      "evidence": ["test:auto-delta-rejection"]
    },
    {
      "outcome": "OUT-009",
      "status": "pass",
      "evidence": ["test:intervention-cancels"]
    },
    {
      "outcome": "OUT-010",
      "status": "pass",
      "evidence": ["test:stale-input-rejection", "security:fresh-gate-check"]
    },
    {
      "outcome": "OUT-011",
      "status": "pass",
      "evidence": ["test:mutation-isolation", "test:callback-replay"]
    },
    {
      "outcome": "OUT-012",
      "status": "pass",
      "evidence": ["test:schema4-migration", "migration:pre-schema4-archive"]
    },
    {
      "outcome": "OUT-013",
      "status": "pass",
      "evidence": ["test:stored-review-summary", "inspection:hook-read-only"]
    },
    {
      "outcome": "OUT-014",
      "status": "pass",
      "evidence": ["inspection:codex-one-shot-adapter", "host:codex-validation"]
    },
    {
      "outcome": "OUT-015",
      "status": "pass",
      "evidence": ["test:claude-exact-session", "host:claude-strict-validation"]
    },
    {
      "outcome": "OUT-016",
      "status": "pass",
      "evidence": ["test:opencode-review-summary", "host:qoder-validation"]
    },
    {
      "outcome": "OUT-017",
      "status": "pass",
      "evidence": ["test:direct-fast-path", "inspection:no-direct-gate"]
    },
    {
      "outcome": "OUT-018",
      "status": "pass",
      "evidence": ["security:no-daemon-boundary", "inspection:stdlib-only"]
    },
    {
      "outcome": "OUT-019",
      "status": "pass",
      "evidence": ["inspection:protocol-documentation", "inspection:rollback-guide"]
    },
    {
      "outcome": "OUT-020",
      "status": "pass",
      "evidence": ["test:version-parity", "host:eleven-skill-validation"]
    },
    {
      "outcome": "OUT-021",
      "status": "pass",
      "evidence": ["test:review-lease-regressions", "review:adversarial-scenarios"]
    },
    {
      "outcome": "OUT-022",
      "status": "pass",
      "evidence": ["host:cross-host-validation", "build:python-compilation"]
    },
    {
      "outcome": "OUT-023",
      "status": "pass",
      "evidence": ["review:verification-record", "review:dated-evaluation"]
    },
    {
      "outcome": "OUT-024",
      "status": "pass",
      "evidence": ["test:authority-containment", "inspection:no-external-write"]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
