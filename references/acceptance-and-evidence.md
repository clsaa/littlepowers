# User-task acceptance and evidence reuse

For project-specific check selection, per-check input reuse and evidence-backed
process learning, use [project-adaptive delivery](project-adaptive-delivery.md).
It proposes equivalent strategies; all acceptance and repair rules here remain
authoritative.

Load for user-facing acceptance, a failed acceptance repair, reuse of prior
evidence, or long-running/noisy execution. Tiny, fully specified edits need only
their focused check, not a separate acceptance document or tool probe.

## Establish acceptance scope once

Reuse the approved plan or evidence artifact; a short section is sufficient:

`OUT ID | original user goal / entry point | applicable surface + data/state |
observable result | tool + evidence | approved exemption (source and limits)`

- Derive the journey from the original request and approved parent requirements,
  not a tour of the implemented controls. Start where the user would start,
  follow the necessary actions, verify persisted side effects/readback, and
  check that the user can reach the final intended result. A successful button
  click, HTTP 200, test count, or generated screenshot alone is not completion.
- Cover relevant pre-existing/historical records and current/new records,
  including changed formats, permissions or migration/recovery states when they
  affect this goal. Do not empty real data, replace old records with a happy-path
  seed, or use a new account to make an existing-user problem disappear. Use an
  authorized local fixture or sanitized copy; accessing production/personal data
  still requires scope and permission. Mark unavailable historical-data coverage
  blocked rather than claiming all user tasks passed.
- Scope by the applicable product terminal (CLI, browser, desktop, mobile, API),
  not by every conceivable platform. Respect an explicit approved exemption and
  its exact scope. Do not silently exempt a requirement or repeatedly demand an
  exempted surface. A new exemption that removes a bound OUT/FID needs the normal
  highlighted Scope Delta approval and rebind; a missing tool is not an exemption.
- Inspect actual callable tools and their readback/capture capabilities before
  promising acceptance. Use a suitable existing API/CLI or background surface
  where it proves the claim. It cannot replace a required visible interaction
  check. Missing capabilities are a specific evidence gap, not grounds to
  install tools, escalate permission, switch host, or open extra browsers.
- Reuse the current target/tab/session and a still-valid grant within its scope.
  Ask for foreground browser access only when the required check needs it and
  no valid grant covers that action. Record the granted target/actions and reuse
  them after recovery; recheck if the target, permission, session, or request
  changed. This never bypasses a host permission prompt or revocation. Stop or
  report the gap on denial instead of asking in a loop.

## Failed acceptance is repair input, not new authority

Preserve the failed report and raw evidence under distinct attempt paths. A
repair report links the earlier attempt and says which checks supersede it;
never edit an old `fail` into `pass` or overwrite its screenshot/log/data.

Stay in the same workflow and complete outcome. If the approved plan still
covers the repair, return to `execute` with a repair checkpoint. If its approach
or task mapping must change, retreat to `plan`/`shape`, revise only the plan,
and use the usual Review Gate and `validate-plan`. Contract/scope changes still
need their normal separate approval. Do not rebind an unchanged baseline merely
to clear a failure; do not reset the workflow, drop failing OUT/FID rows, or
edit the ledger by hand.

A previous comparison `fail`/`blocked` does not mean the approved baseline is
unavailable. Fresh source availability/digest, coverage, scope and approval are
checked independently. Validating a new plan, rebinding a contract, or returning
to execution invalidates the current verdicts. `artifacts.evidence` remains the
last report for recovery; only `outcome_lock.verification` is completion
authority. Reading a historical report is not re-recording it as current proof.
The CLI keeps references, not an immutable archive of their bytes; preserving
attempt files is the coordinator's responsibility.

## Reuse checks, not an old completion verdict

For material evidence that might be reused, record a compact receipt alongside
the results: claim/OUT/FID, command or user action, result/exit status, explicit
evidence path, relevant code/config/data/dependency identity, environment and
permission scope, and observed user result. Use existing commit/snapshot/hash
facts only when available and relevant; do not scan the repository on every turn.

Use the existing `verification-inputs` command before checks to bind explicit
implementation/test/config bytes (and intended absence), then preserve that
snapshot in the new Verification Record. Reusing a check needs evidence that
its dependencies remain unchanged; capturing today's hashes is not permission
to relabel an old result. Current input and exact approval gates remain active.

| Change since evidence | Decision |
| --- | --- |
| No relevant dependency, environment, data or acceptance change | Retain the check with its original receipt and an explicit reuse reason |
| Isolated behavior or fixture changed | Rerun its reproducer and affected checks/consumers; retain provably unrelated checks |
| Shared schema, authorization, migration, build/runtime config or dependency changed | Recheck affected integration and user journeys; run the relevant broad boundary once after integration |
| Acceptance source, terminal, permission, data history, environment or output changed | Invalidate dependent checks; reconcile changed authority before re-running |
| Missing receipt/file, unknown dependency reach, ambiguous ordering or stale live-service observation | Do not reuse; rerun the smallest check that re-establishes the claim or report blocked |

Failure remains unresolved until a fresh superseding check passes. A waiver is
not a passing test. A timeout, skip, partial run or unavailable tool is never a
pass. Do not rerun all checks just because unrelated docs changed, and do not
reuse an entire old pass after a repair. Aggregate fresh and valid reused checks
into a **new** Verification Record, covering every active outcome and required
comparison. The state CLI checks explicit bound artifacts and fidelity evidence;
it cannot infer arbitrary test dependencies, external state, or genuine user
success from evidence tokens. The coordinator must establish those facts.

## Reuse available efficiency facilities

For structured check collections, repeated observations or pending report
recovery, load [execution-efficiency](execution-efficiency.md) and use the
existing `scripts/littlepowers_efficiency.py` pack/observe proposals. Preserve
required check IDs, critical failures and evidence digests; a report cursor
acknowledges read-only delivery, never a business write. Simple logs can use
the native bounded-output path below without a cursor or structured wrapper.

- For long non-sensitive command output, capture it once in a task-scoped log
  with the original exit status and command identity, then inspect a bounded
  failure/summary excerpt using the host's file/output tools. Preserve needed
  diagnostics and the log path. Do not rerun a completed command just because
  its displayed output was truncated. A summarizer's exit code is not the test
  exit code. Avoid persisting secrets, personal data, raw model reasoning or
  unrelated transcripts; use redaction or a safe structured result instead.
- Prefer already available host facilities: bounded output/file reads, search,
  returned process/job continuation handles, and native task/readback tools.
  An optional installed output reducer is usable only if it preserves failures,
  exit status and access to raw evidence; fall back to native tools otherwise.
  No automatic helper installation, global hook changes or extra agent/model call.
- Before an externally mutating or non-idempotent operation, record its exact
  target and pending status in existing progress/evidence. Record the confirmed
  result/remote ID afterward. On interruption, inspect that receipt and read
  remote status before retrying: succeeded means do not resubmit; running means
  resume/wait on the existing handle; unknown means readback or stop for a
  decision. A missing receipt or a timeout does not prove the write failed.
  Existing native-checklist ownership/readback rules still apply.
- Measure a representative run before claiming benefit: preserved result and
  failures, raw bytes versus presented bytes, command/write count, and elapsed
  time where meaningful. Label output-volume savings separately from actual
  model-token, cost or wall-clock savings. Do not add background benchmarking.
