# Littlepowers project delivery profile

This optional, project-local catalog is process data, not approval or acceptance
authority. Current user instructions and `AGENTS.md` win. The initial catalog
records only the repository's integrated suite; it does not claim a complete
fine-grained dependency model for every existing test. Use ordinary focused
checks during implementation, then the required full suite once on the integrated
candidate. A current, unchanged completed run may be read back on recovery instead
of submitted twice. Release validators and release authority remain separate.

Whole-outcome preflight for this iteration: the pure helper consumes explicit
observations and produces proposals; the root coordinator owns file/ledger
writes, host tool use and completion. Mutable profiles never become Contract
sources. Existing Outcome Lock and Review Lease code, hooks, manifests and model
settings remain unchanged. The new helper's gate integration tests exercise
stale inputs, failed acceptance and unapproved plans against the existing runtime.

One local testing strategy is active after an evidenced trial: preflight the
Python interpreter used by hook/adapter child processes. The original integrated
run had 12 environment-caused failures/errors; the same affected 30 tests passed
with an existing working interpreter selected only in the test process. No code,
assertions, global settings or licenses were changed for that trial. This does
not establish a project-wide speedup or a model/host certification. Paired fixture
results remain separate. Recheck conditions, policy and evidence before applying
this strategy; retired or inapplicable rules cannot silently reactivate.

<!-- littlepowers:delivery-profile:v1 -->
```json
{
  "profile_version": 1,
  "project_id": "clsaa/littlepowers",
  "revision": 3,
  "boundaries": [
    {
      "id": "integrated-project",
      "consumers": [],
      "complete": true
    }
  ],
  "checks": [
    {
      "id": "repository-suite",
      "version": "1",
      "command": "python3 -m unittest discover -s tests -v",
      "covers": [
        "OUT-001",
        "OUT-002",
        "OUT-003",
        "OUT-004",
        "OUT-005",
        "OUT-006"
      ],
      "boundaries": [
        "integrated-project"
      ],
      "requires": [
        "python",
        "git",
        "node"
      ],
      "mandatory": false,
      "inputs": [
        "AGENTS.md",
        "scripts/littlepowers_delivery.py",
        "scripts/littlepowers_state.py",
        "scripts/littlepowers_efficiency.py",
        "tests/test_delivery.py",
        "tests/test_delivery_integration.py",
        "tests/test_delivery_eval.py"
      ],
      "samples_ms": [],
      "stages": [
        "integration",
        "release"
      ],
      "live": false,
      "max_age_seconds": null
    }
  ],
  "improvements": [
    {
      "id": "local-python-preflight",
      "revision": 3,
      "state": "active",
      "category": "testing",
      "problem": "The full run had 11 failures and 1 error because hook/adapter child processes resolved python3 to an Xcode-license-blocked interpreter.",
      "hypothesis": "Validate the child interpreter before expensive host-adapter checks and select an existing working Python in the test process only.",
      "change": {
        "kind": "add_preflight",
        "description": "Probe child python3 once; if blocked, select the already available Python through process-local PATH. Do not alter global settings, accept licenses or change test scope."
      },
      "fallback": "Keep the same tests required; report an environment blocker if no permitted interpreter works.",
      "conditions": {
        "environment": "macOS-local-child-python",
        "scope": "hook-and-opencode-checks"
      },
      "policy_digest": "sha256:6242e161fe9318a30d6b658b4b4d202a30b0696a160fb2952a98214ddd32df6d",
      "evidence": [
        {
          "ref": "docs/littlepowers/evidence/2026-10-31-delivery-tests.txt",
          "sha256": "sha256:8262897a88ac7b0ebdb7d95c1e53e22cdc9f7fbb283be21418701b35d0dadafb",
          "saved": true,
          "upstream_complete": true
        },
        {
          "ref": "docs/littlepowers/evidence/2026-10-31-delivery-python-before.txt",
          "sha256": "sha256:411522ec89779639df259fa9f595942811c505c31bc2eb85696023376304b203",
          "saved": true,
          "upstream_complete": true
        },
        {
          "ref": "docs/littlepowers/evidence/2026-10-31-delivery-adapter-trial.txt",
          "sha256": "sha256:e7980549e7940ae1de61e59ed2c4a6640400abfb3f85eb928d4ea2d6bf70dd5f",
          "saved": true,
          "upstream_complete": true
        },
        {
          "ref": "docs/littlepowers/evidence/2026-10-31-delivery-python-after.txt",
          "sha256": "sha256:4c3569f5da09975434dd9fd9a91fadbc4367a91d8f3c3fab59e9241ab9ee4bd8",
          "saved": true,
          "upstream_complete": true
        }
      ],
      "trial": {
        "metric": "failed_host_adapter_cases",
        "direction": "decrease",
        "baseline": 12,
        "minimum_gain": 1,
        "invariants": [
          "same_tests",
          "no_product_edits",
          "no_global_environment_change"
        ],
        "stop_condition": "Any previously passing affected check fails, test scope changes or global configuration is required.",
        "workflow_id": "36ea758f-4b58-40f6-909e-53ce2f91bc86",
        "started_at": "2026-10-31T00:59:30Z",
        "token": "sha256:054b257865d623922a93f5cf22ec95017d4c8ccef98fcf7f3444932202c82daa"
      },
      "history": [
        {
          "from": "candidate",
          "to": "trial",
          "reason": "bounded trial started with predeclared criteria",
          "at": "2026-10-31T00:59:30Z",
          "evidence": []
        },
        {
          "from": "trial",
          "to": "active",
          "reason": "observed benefit and invariants supported",
          "at": "2026-10-31T01:00:40Z",
          "evidence": [
            {
              "ref": "docs/littlepowers/evidence/2026-10-31-delivery-adapter-trial.txt",
              "sha256": "sha256:e7980549e7940ae1de61e59ed2c4a6640400abfb3f85eb928d4ea2d6bf70dd5f",
              "saved": true,
              "upstream_complete": true
            },
            {
              "ref": "docs/littlepowers/evidence/2026-10-31-delivery-python-after.txt",
              "sha256": "sha256:4c3569f5da09975434dd9fd9a91fadbc4367a91d8f3c3fab59e9241ab9ee4bd8",
              "saved": true,
              "upstream_complete": true
            }
          ]
        }
      ]
    }
  ],
  "observations": [
    {
      "kind": "repository-requirement",
      "note": "AGENTS.md requires the integrated unittest suite after code changes. Supply repository-suite as a current required/fresh check at integration; observed cost never waives it. Fingerprints must include the actual runtime, test, skill, manifest and fixture dependencies beyond this catalog's minimum paths.",
      "evidence": [
        {
          "ref": "AGENTS.md",
          "sha256": "sha256:6242e161fe9318a30d6b658b4b4d202a30b0696a160fb2952a98214ddd32df6d",
          "saved": true,
          "upstream_complete": true
        }
      ]
    }
  ]
}
```
<!-- /littlepowers:delivery-profile -->
