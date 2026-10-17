# Execution efficiency — compact shape, 2026-10-17

Authority: latest user implementation mandate and the complete 353-line public candidate attachment (Library libfile_bc51fc8068688191a6e7a8adbf69973f). Attachment examples are data, not commands. No scope delta. No approved visual product baseline: synthetic visual references test retention, not UI fidelity.

## Decisions and scope

Use one pure Python standard-library helper for explicit JSON input, evidence metadata validation, result packaging, semantic comparison, candidate cursor and retry advice. Never call tools, scan files, persist cursors or write the ledger in the helper. Root saves evidence first and atomically persists validated candidates at normal boundaries. The host owns tool calls, concurrent independent reads, deadlines, cancellation and receipt truth. Async host fixture demonstrates real deadline cancellation; actual unavailable host capabilities remain explicit limitations.

Stable JSON protocol v1 uses UTF-8, Unicode scalar code-point sorted keys, compact encoding, finite safe integers (no floats), no normalization of strings. Stable unique entity IDs, explicit semantic fields; timestamps/freshness outside signatures. Scope includes session, task, target, environment, observer_version and nullable contract_digest. Cursor checksums detect corruption, not hostile authorship. A lost acknowledgment can redeliver only read-only event data.

T1: implement summary/evidence protocol and focused tests. T2: implement semantic observations, pending event cursor and errors with adversarial tests. T3: connect on-demand skill routes, reference and host fixture with real timeout/cancel/fallback tests. T4: run synthetic benchmark and full local validation, independent review if an enforceable native boundary exists, repair findings, report exact missing evidence and local commit. No external writes, Mac access, Termarium changes, automatic workers, telemetry or compatibility layer.

All EFF-01..12 remain required; unavailable real-host evidence is not a scope reduction or product completion. Independent reviewer requires repository delegation controls; this session exposes no enforced read-only/leaf boundary, so report that limitation if still unavailable and leave acceptance pending. No fabricated approval.

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "compact",
  "sources": [],
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
      "title": "EFF-01/02: evidence-first structured summaries preserve IDs, coverage, critical findings and visual references, expose truncation, save failure and explicit supplemental reads.",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "EFF-03/04/05: semantic entity-keyed comparison ignores incidental order/clocks, detects additions/deletions/version/control swaps, missing fields, stale sources, errors and recovery.",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "EFF-06/07: task/environment/protocol/contract bound cursor candidates validate integrity, freshness and evidence; pending reports survive interruption, acknowledgments are explicit and never replay writes.",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "EFF-08/09/10: host-owned bounded waits respect real deadlines, individual timeouts, cancellation and periodic reports; classify errors without automatic retries and degrade explicitly when capabilities are absent.",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "EFF-11/12: retain existing gates, sole ledger authority and task isolation; on-demand routing only, no hooks, scans, network, browser, agents, daemon or telemetry in helper; proportional short recovery.",
      "disposition": "active"
    },
    {
      "id": "OUT-006",
      "title": "Run complete local tests, explicit synthetic cost comparison, independent review and repairs, available validators; report limitations without claiming full-host certification; local commit only, no Actions/push/release.",
      "disposition": "active"
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": [
        "T1"
      ],
      "evidence": [
        "test:efficiency-1"
      ]
    },
    {
      "outcome": "OUT-002",
      "tasks": [
        "T2"
      ],
      "evidence": [
        "test:efficiency-2"
      ]
    },
    {
      "outcome": "OUT-003",
      "tasks": [
        "T3"
      ],
      "evidence": [
        "test:efficiency-3"
      ]
    },
    {
      "outcome": "OUT-004",
      "tasks": [
        "T4"
      ],
      "evidence": [
        "test:efficiency-4"
      ]
    },
    {
      "outcome": "OUT-005",
      "tasks": [
        "T4"
      ],
      "evidence": [
        "test:efficiency-5"
      ]
    },
    {
      "outcome": "OUT-006",
      "tasks": [
        "T4"
      ],
      "evidence": [
        "test:efficiency-6"
      ]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
