# Verification integrity fixes

Authority: latest user request to directly implement the two confirmed fixes; prior draft is optional and remains unapplied. No scope delta.

## Approach and constraints

T1: Put exact consumed plan approval checking in the shared current-plan observer so fresh execution, record-verification, completion and atomic state writers agree. Reuse existing path/byte/source checks; direct workflows remain plan-free.

T2: Add a read-only verification-inputs CLI helper returning an explicit files/manual scope. Capture existing file SHA-256 or declared absent paths BEFORE checks, then copy unchanged into Verification Record inputs. Require nonempty file scope or an explicit manual justification; reobserve at record/completion. Reuse bounded safe readers, reject unsafe paths and self-inclusion of the verification artifact, and never scan unrelated files. Hashes detect declared byte changes, not test execution, semantic coverage, undeclared inputs, or malicious coordinator forgery.

T3: Update affected workflow skills, protocol/security/migration docs. Old verification records remain parseable for recovery but must capture inputs and rerun checks before recording/completion; no automatic adoption. No schema bump or plugin reinstall mid-workflow. Existing runtime path safety restrictions continue.

T4: Add focused regressions including prose outside plan JSON, source/path drift, atomic writer rejection, missing/changed/absent inputs, justified manual work and unrelated-file changes. Run full unittest suite, compileall, skill/plugin validators, shell/JS syntax and whitespace checks. Review the integrated diff. Keep changes local and return a patch via Library if available.

Non-goals: automatic Hooks, remote publication, native host certification, recursive repository hashing, or applying the old draft.

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
      "title": "Exact consumed plan path, bytes and current embedded sources are freshly checked at record and completion; failed writers preserve state.",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "Pre-check explicit file hashes or justified manual scope are required; recording and completion reject changed, missing or unsafe inputs, including explicit absence.",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Migration and skills document revalidation, bounded declared scope, manual legitimacy and the fact hashes do not prove test execution; no hook work or broad scanning.",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "Regressions, full suite, available validators, compilation, syntax and read-only review support an unpublished deliverable.",
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
        "test:verification-integrity"
      ]
    },
    {
      "outcome": "OUT-002",
      "tasks": [
        "T2"
      ],
      "evidence": [
        "test:verification-integrity"
      ]
    },
    {
      "outcome": "OUT-003",
      "tasks": [
        "T3"
      ],
      "evidence": [
        "inspection:workflow-docs"
      ]
    },
    {
      "outcome": "OUT-004",
      "tasks": [
        "T4"
      ],
      "evidence": [
        "review:final-validation"
      ]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
