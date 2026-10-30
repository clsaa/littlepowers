# P1/P2 acceptance and repair verification

Date: 2026-10-30. Local unreleased candidate based on `23583fd` (v1.4.1 source).
Parent: the five-row iteration request, mapped in
[the compact shape](../shapes/2026-10-30-acceptance-repair.md).
No scope delta, release, commit, push, production install, or model-setting change.

## Scope and observable outcome

Applicable surface: Littlepowers' Python state CLI and the four-host skill
instructions. No browser foreground, personal/production data, or external write
was necessary for these checks; no acceptance exemption was invented.

- A stored fidelity `fail`/`blocked` now allows a lawful same-scope repair-plan
  review. Missing/drifted baseline sources, insufficient coverage, wrong policy,
  open approval and completion gates still reject progress as applicable.
- Rebinding, revalidating a plan and returning to execution invalidate current
  verification eligibility but retain the last evidence path. Distinct attempt
  files preserve the original report and raw evidence; the CLI is not an
  immutable evidence archive and cannot prevent direct filesystem edits.
- Completion now freshly checks exact approved plan bytes and consumed approval,
  not just its Outcome mapping. Old passing reports cannot complete a repaired
  execution without a new Verification Record.
- One on-demand reference now covers original user journeys, relevant historical
  data, final persisted results, applicable terminals, available tools, scoped
  approved exemptions, evidence reuse, bounded logs and operation readback.
  Four applicable skill entrypoints link it; tiny tasks need no new artifact.

## Reproductions and checks

Python 3.12 on local macOS, using the existing fallback Git because system Git
still reports the Xcode license issue. No host configuration was changed.

| Check | Observed result |
| --- | --- |
| New outcome-gate regressions before runtime fix | 21 tests, 5 expected failures: three repair routes blocked, historical reference cleared, old pass retained on repair |
| Same focused module after initial fix | 21/21 pass |
| Additional completion/plan-prose reproducer before its fix | Expected failure: completion accepted unapproved plan prose |
| Same completion reproducer after fix | 1/1 pass |
| CLI subprocess recovery/repair/completion scenario | 1/1 pass; same workflow, open-gate execution rejected, old report read back, completion rejected until fresh report, historical report and raw output unchanged |
| Engineering discipline/link checks | 7/7 pass; includes routing/link validation, not a model-behavior proof |
| Aggregate `python3 -m unittest discover -s tests -v` | 232 executed in 94.209 s: 231 pass, one obsolete assertion still expected the historical evidence pointer to be cleared |
| Corrected `test_outcome_contract.py` only | 14/14 pass in 8.050 s, including the former failure; now asserts preserved readable history AND pending current verification |
| Official skill validator | All 11 skills pass |
| Python compilation and `git diff --check` | Pass |

The runtime and skill files were unchanged after the aggregate run. Only the
obsolete test assertion was corrected, so the affected 14-test contract module
was rerun rather than the entire suite. The aggregate's original failure log
was retained. This is combined evidence, **not** a claim of a later all-green
aggregate invocation. No known failing check remains.

The CLI fixture starts from historical failed state rather than a clean ledger,
uses new output matching its explicit approved baseline, and verifies old
evidence byte preservation after completion. This is a real state-CLI lifecycle
test, not authenticated model behavior or a production user's browser journey.

## Measured efficiency

Used existing shell redirection, `rg`, bounded file reads, and the returned
process continuation handle; no output wrapper, package or runtime was added.
The skill validator's PyYAML dependency was isolated in a temporary validation
directory, not added to Littlepowers or host configuration.

- Aggregate raw log: 36,587 bytes. Initial summary: 240 bytes (99.34% less),
  preserving the failure identity, test count/result and elapsed-time lines.
- Pre-fix failing log: 7,582 bytes. Failure/result summary: 958 bytes (87.36%
  less), preserving all five failure identities and the nonzero outcome.
- Full diagnostics were subsequently read where needed; those extra bytes are
  not included in the initial-summary savings. Raw logs remain available locally.
- Original command exit status was retained independently of `rg`'s status.
  The aggregate command was submitted once and resumed via its existing handle,
  never resubmitted because its output was large. Only the affected test module
  ran after the assertion-only change.

These are measured output-volume savings, not a comparative model-token, cost
or wall-clock speed claim. External-write duplicate prevention is documented
and existing native-mirror reconciliation tests still passed; no live publish,
payment, or other external mutation was attempted for this iteration.

Local logs: `/tmp/littlepowers-acceptance-before.log`,
`/tmp/littlepowers-acceptance-after.log`,
`/tmp/littlepowers-acceptance-aggregate.log`,
`/tmp/littlepowers-acceptance-contract.log`. These temporary diagnostic logs may
be cleaned by the host; this report retains the commands and observed results.

## Integrated review and limits

Self-review covered the exact runtime diff, rejection/repair tests, historical
readback, reference routing, approval boundaries, host-neutral wording and
absence of new hook/background/model work. Snapshot before/after the main review:
`sha256:9e53b8be4e944be59b413822d4cdfdafa8c9ef68c279ac43acbc1957a002967e`.
The later assertion-only delta was separately reviewed and tested; its snapshot
was stable across review:
`sha256:60512b690cf8697ef6aba497fcb2c2e1941ccb755de30b305a35cabc0fec5ade`.
This report is the subsequent documentation-only addition.

Work-unit compliance: pass. Approved-outcome fidelity: pass for these five
bounded protocol/rule improvements. Code quality: approve; no blocking finding.

User-task semantics, arbitrary dependency reach, scoped browser grants and
external operation receipts still require agent judgment. The reference and
evaluation scenarios do not prove every model will follow them. No authenticated
Codex/Claude/Qoder/OpenCode model matrix, new desktop UI certification, or remote
cross-platform CI was run; none is claimed. Schema 4/protocol 1.3 and package
version remain unchanged; this is not a published or installed release.

## Verification Record

<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {"status": "pass", "evidence": ["test:aggregate-and-focused-repair", "test:cli-recovery", "test:skill-validation"]},
  "outcome_fidelity": {"status": "pass", "evidence": ["inspection:five-outcome-traceability", "test:cli-recovery"]},
  "code_quality": {"required": true, "status": "approve", "evidence": ["review:integrated-candidate"]},
  "blocking_evidence": [],
  "outcomes": [
    {"outcome": "OUT-001", "status": "pass", "evidence": ["test:acceptance-repair-gates", "test:cli-recovery"]},
    {"outcome": "OUT-002", "status": "pass", "evidence": ["inspection:user-task-acceptance", "test:repair-lifecycle"]},
    {"outcome": "OUT-003", "status": "pass", "evidence": ["inspection:surface-capability-scope"]},
    {"outcome": "OUT-004", "status": "pass", "evidence": ["test:stale-pass-invalidation", "inspection:evidence-reuse-rules"]},
    {"outcome": "OUT-005", "status": "pass", "evidence": ["test:bounded-output-measurement", "inspection:resume-receipts"]}
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
