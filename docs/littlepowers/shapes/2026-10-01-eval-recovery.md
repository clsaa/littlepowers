# Littlepowers 1.4.3: eval reporting and recovery

## Authority and scope

Latest user mandate: finish the previously approved v1.4.3 iteration. The user explicitly confirmed using verified v1.4.2 source skills and ledger tools instead of unavailable native installation. Baseline/main is 6aefb3687b70697df9503e5f9b396b1d071ab99d. No scope delta. No separate parent file was supplied; the Outcome records carry the full bounded request. No visual baseline applies.

## Selected approach

Keep the evaluator an opt-in recorder, not a grader. Project host events into a small typed report; free-form output is excluded by construction. Add an explicit sensitive-observable-log opt-in, private file creation, and no default raw diagnostics. Do not claim universal redaction or alter the host's own history. Test synthetic payload canaries without model calls.

Move OpenCode recovery bookkeeping into each plugin instance and session, cache successful context for reconstructed messages, and key empty retry eligibility to the latest actual user message rather than assistant/tool traffic. Preserve one injected block, tolerate malformed host data, and retain fail-open and bounded subprocess behavior. Cover child-session events and cache lifecycle with local host fixtures; do not claim real-host certification.

## Ordered plan and acceptance

T1: reproduce default payload leakage, implement minimal reports and explicit sensitive output; verify command/MCP/message/error canaries, malformed events, failure paths and output-file safety.
T2: reproduce empty retries and lost reconstructed context, repair cache semantics; verify user-only retries, replay, concurrent transform behavior, session/plugin isolation and observed child events.
T3: align existing package manifests/tests/docs to 1.4.3; add changelog and release notes. Protocol 1.3/schema 4 stay unchanged. Correct only related public claims.
T4: capture explicit pre-check inputs and a supplemental hash list for hidden paths unsupported by the stable verifier; run focused tests then the full suite, compilation, syntax/diff checks and available official validators; obtain independent read-only review, resolve findings, rerun affected checks and record evidence. Report macOS/Windows and real host tests as unrun unless exact-candidate evidence is available.

## Non-goals and constraints

No v1.5 grading/benchmark framework, portable manifest migration, model calls, hook authorization changes, persistent host settings, telemetry, new orchestrator, state/schema changes or plugin hot-loading. No commits, push, merge, PR, tags or public Release in this candidate. Keep source runtime separate from development tree. Do not equate a fixture with installed-host behavior or an old CI run with candidate CI. Validation tools/platforms unavailable locally are reported, not fabricated.

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
      "title": "Default live-eval reports omit free-form host command, MCP, message and diagnostic payloads; explicitly opted-in sensitive observable logs are separate and covered by synthetic canaries.",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "OpenCode recovery attempts follow real user-message boundaries, reconstructed same-ID messages retain one recovery block without redundant processes, and session/cache lifecycle isolation is tested.",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Prepare consistent 1.4.3 metadata and release notes, correct worker-marker documentation, retain protocol/schema and compatibility limits.",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "Deliver an independently reviewed patch with reproduced failures, focused and aggregate offline checks, available validators and explicit unavailable host/platform evidence; no push, merge or publication.",
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
        "test:eval-canaries"
      ]
    },
    {
      "outcome": "OUT-002",
      "tasks": [
        "T2"
      ],
      "evidence": [
        "test:opencode-lifecycle"
      ]
    },
    {
      "outcome": "OUT-003",
      "tasks": [
        "T3"
      ],
      "evidence": [
        "inspection:release-consistency"
      ]
    },
    {
      "outcome": "OUT-004",
      "tasks": [
        "T4"
      ],
      "evidence": [
        "review:independent-candidate"
      ]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
