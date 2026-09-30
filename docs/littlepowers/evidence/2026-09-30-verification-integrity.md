# Verification integrity candidate evidence — 2026-09-30

Base: `23583fd11b386196ec10e3f4c6996db10c529d93`. Unpublished v1.4.2 candidate;
package manifests and the installed workflow remain stable 1.4.1.

## Reproduction and changes

Stock 1.4.1 was reproduced in an isolated fixture: after approved plan and
verification, appended prose made fresh execution report `artifact bytes`,
but completion failures were empty and finish returned complete. The new shared
plan observer checks the consumed approval at record/completion as well.

The isolated pre-change implementation experiment also permitted stale code.
The candidate captures explicit existing/absent inputs before checks, compares
them at record/completion and atomic completed-state writes, and rejects old
receipts until recaptured and reverified. It never scans unrelated files.
The path fixture checks the in-memory gate directly and separately checks the
atomic writer, since command_finish reloads persisted state.

## Final checks

- `python3 -m unittest discover -s tests -v`: exit 0; 246 tests, including 24 new integrity regressions (baseline 222).
- `python3 -m compileall -q scripts hooks tests`: exit 0.
- `git diff --check`: exit 0.
- Official `quick_validate.py` on each of 11 `skills/` directories: all exit 0.
- Official `validate_plugin.py .`: exit 0.
- Claude Code 2.1.278 `plugin validate --strict .`: exit 0.
- `bash -n hooks/run-hook.cmd`: exit 0.
- `node --check .opencode/plugins/littlepowers.js`: exit 0.

The delivered validation bundle includes exact commands, output logs and the
explicit pre-check input snapshot. Its files were captured after the last
implementation edit, before final checks, and compared unchanged afterward.
This evidence document is produced afterward and is not a verification input.

## Review and limitations

Structured coordinator self-review: work-unit pass; approved-outcome fidelity
pass; code-quality approve; no unresolved findings. During review, missing
workspace roots were found to be too permissive for absence and fixed with a
regression before final checks. Before/after bounded review snapshots match.
This is not independent third-party review. Only Linux was executed; no native
host Hook loading, Windows/macOS execution, release or remote publication is
claimed. Hashes cover declared bytes/absence, not file modes, undeclared files,
external environment or proof that checks really ran. Scope and timing remain
coordinator obligations; hidden-component paths retain existing restrictions.

This workflow receipt uses the installed stable 1.4.1 record syntax so the
active plugin is not replaced mid-task. Candidate `inputs` enforcement is
exercised by the regression/CLI self-host suite; the final coordinator also
compared the candidate's captured scope before completion. Future candidate
workflows must use the new inputs field; this historical receipt is not an
exemption from the documented migration gate.

<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": [
      "test:246-unit-tests",
      "test:verification-integrity"
    ]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": [
      "inspection:four-outcomes-covered"
    ]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": [
      "review:coordinator-integrated-diff"
    ]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": [
        "test:verification-integrity"
      ]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": [
        "test:verification-integrity"
      ]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": [
        "inspection:workflow-docs"
      ]
    },
    {
      "outcome": "OUT-004",
      "status": "pass",
      "evidence": [
        "review:final-validation"
      ]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
