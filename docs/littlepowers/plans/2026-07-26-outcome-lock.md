# Outcome Lock implementation plan

Date: 2026-07-26

Status: complete

## Goal

Implement the complete schema-3 Outcome Lock contract from OUT-001 through
OUT-023: durable parent-source binding, legacy reconciliation, deterministic
coverage/scope/baseline/fidelity/completion gates, and compact cross-host
recovery, without adding a second orchestrator or slowing ordinary model work.

## Approved inputs

- `docs/littlepowers/brainstorms/2026-07-26-outcome-lock.md`
- `docs/littlepowers/specs/2026-07-26-outcome-lock.md`
- `docs/littlepowers/designs/2026-07-26-outcome-lock.md`
- `docs/littlepowers/specs/2026-07-26-scope-integrity-lean-route.md`
- `docs/littlepowers/designs/2026-07-26-scope-integrity-lean-route.md`
- `AGENTS.md`
- the user's 2026-07-26 review conclusions and approval to proceed

## Scope and baseline

No scope delta.

The compatibility baseline is the released `v1.1.0-alpha.1` route, security,
recovery, hook, and four-host behavior. The approved Outcome Lock specification
is the product baseline. Implementation-generated tests and reports may prove
the new candidate but cannot replace those approved sources.

## Global constraints

- One workflow and one Definition of Done cover all OUT-001…OUT-023.
- Tasks below form one continuous implementation stream. Their boundaries exist
  only for focused checks and bounded rollback; they are never smaller product,
  platform, MVP, technical, or release slices, staged deliveries, or stopping
  points.
- The root coordinator is the only ledger writer.
- Do not spawn reviewers, agents, model calls, background scans, daemons,
  telemetry, or automatic test runs.
- Runtime remains Python 3 standard library only and shared by Codex, Claude
  Code, Qoder, and OpenCode.
- Hooks remain read-only, bounded, transcript-free, network-free, fail-open, and
  silent without active state.
- Continue live workflow checkpoints through the currently loaded installed 1.1
  CLI while source code is incomplete. Exercise edited schema-3 code only on
  temporary roots until the aggregate integration boundary.
- Use focused tests for each independently reversible unit. Run the complete
  suite and host validators once after integration.
- Do not commit, push, tag, publish, install, replace Claude Superpowers, or
  modify an external repository in this workflow unless the user separately
  authorizes it.

## Definition of Done

- Schema-3 state and protocol 1.2 implement the approved exact data and
  transition invariants.
- Every active legacy schema-1/schema-2 workflow is visibly
  `reconcile_required`; terminal workflows remain terminal.
- Contract, Plan Map, Verification Record, drift, coverage, scope delta,
  approved baseline, fidelity, three verdicts, and completion are behaviorally
  enforced.
- Untracked direct work remains zero-overhead; tracked direct work remains
  minimal; lean and full route depths are unchanged.
- Failed gates are atomic and report all actionable IDs/conditions.
- Migration has a recoverable pre-schema3 archive and is tested on an isolated
  copy before any live-ledger decision.
- Hook rendering reads stored summaries only.
- All 23 Outcomes have passing fresh evidence; work-unit compliance and
  approved-outcome fidelity pass; code quality approves; blocking evidence is
  zero.
- Focused checks, full Python tests, compilation, eleven skill validators,
  Codex plugin validation, Claude strict validation, Qoder validation when
  available, OpenCode syntax validation, Windows CI-compatible tests, and final
  diff inspection pass.
- The final report makes no authenticated GPT-5.6, Fable, or Opus execution
  claim unless such a run actually occurred.

## Continuous implementation order

Execute Tasks 1–8 continuously without treating any task as a partial delivery
or pausing for task-level approval. The dependency order is runtime foundation
→ deterministic gates → compact recovery and skill routing → public/cross-host
alignment → integrated verification. Focused checks protect each rollback
boundary; only Task 8 runs the aggregate host and regression matrix.

## Task 1 — Structured records and pure evaluators

**Testable outcome:** Contract, Plan Map, and Verification JSON blocks parse into
canonical bounded records; malformed or contradictory records fail without I/O;
coverage, scope, baseline, fidelity, and completion evaluators return complete
deterministic result sets.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_outcome_records.py`.

**Dependencies and consumers:**

- No implementation dependency.
- Task 2 consumes schema defaults and validation helpers.
- Tasks 3 and 4 consume the parser, canonical digest, and pure evaluators.

**Rollback unit:** Parser/evaluator constants, functions, and their isolated test
module. They are not yet reachable from a persisted command. Revert this unit
together if its record grammar changes.

**Steps:**

- [x] Add record markers, ID/digest/evidence-token regexes, enums, and explicit
      count/string limits.
- [x] Add duplicate-key-safe JSON loading and exact tagged-block extraction.
- [x] Add canonical JSON hashing.
- [x] Validate Contract sources, dispositions, scope declarations, approved
      baselines, and FID relationships.
- [x] Validate Plan Map task/evidence declarations and derive complete coverage.
- [x] Validate Verification Outcome/FID evidence and derive the three verdicts.
- [x] Add a completion evaluator that returns every failing condition.
- [x] Add behavior tests for duplicate blocks/keys, malformed IDs, unknown keys,
      bounds, semantic digest stability, scope contradictions, incomplete
      coverage, invalid baseline provenance, and inconsistent verdicts.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_outcome_records.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_outcome_records.py
```

Expected evidence: all record/evaluator cases pass; compilation exits 0.
Scope rationale: local—new pure functions have no command, state, hook, or host
consumer yet.

## Task 2 — Schema 3, legacy migration, and recoverable persistence

**Testable outcome:** New state is schema 3/protocol 1.2; legacy active/paused
state obtains a read-only reconciliation view; legacy terminal state remains
terminal; the first successful schema-3 mutation archives the exact validated
legacy record once.

**Files:**

- modify `scripts/littlepowers_state.py`;
- modify `tests/test_state.py`;
- create `tests/test_outcome_migration.py`.

**Dependencies and consumers:**

- Depends on Task 1 schema validators and constants.
- Tasks 3–5 consume `outcome_lock`, migration metadata, and transaction helpers.

**Rollback unit:** Schema version, exact state validator, legacy adapters,
pre-schema3 archive helper, and updated state fixtures/tests. Rollback is coupled
to Task 1 only where schema validation imports its enums.

**Steps:**

- [x] Extend artifact keys with `contract` and `evidence`.
- [x] Add exact schema-3/protocol-1.2 validation and compact default lock
      records.
- [x] Add `--direct-lock` start parsing and minimal direct-state construction,
      without adding contract/plan artifacts.
- [x] Split internal loading into a schema-3 view plus optional original legacy
      metadata while preserving the public dictionary return.
- [x] Map schema-1→2→3 and schema-2→3 deterministically, preserving IDs,
      revisions, phase/status, artifacts, progress, timestamps, and history.
- [x] Mark active/paused legacy state `reconcile_required`; map
      complete/cancelled state to `legacy_terminal/not_required`.
- [x] Archive the exact legacy JSON immediately before the first successful v3
      write; do not archive on a rejected candidate.
- [x] Preserve atomicity, permissions, ignored-state, symlink/hard-link/reparse,
      root-swap, size, timestamp, and revision defenses.
- [x] Update existing state tests from schema-2 creation expectations to schema
      3 while retaining explicit legacy fixtures.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_outcome_migration.py' -v
python3 -m unittest discover -s tests -p 'test_state.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_state.py tests/test_outcome_migration.py
```

Expected evidence: active, paused, complete, cancelled, failed migration,
idempotence, archive, state-security, and concurrency cases pass.
Scope rationale: connected—schema and persistence affect every state caller, so
the existing state module runs once in addition to focused migration tests.

## Task 3 — Contract binding, secure hashing, drift, and scope gate

**Testable outcome:** `bind-contract` and `check-contract` securely bind only
explicit sources, reject invalid scope/baseline declarations, detect semantic or
source drift without adopting it, and invalidate stale downstream summaries.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_outcome_contract.py`;
- modify `tests/test_state.py` only when an existing shared-file security fixture
  is the correct regression home.

**Dependencies and consumers:**

- Depends on Tasks 1 and 2.
- Task 4 requires a bound contract.
- Task 5 renders its stored summary.

**Named interfaces:**

- `bind-contract --artifact --approval-kind [--approve-scope-delta]`
- `check-contract`
- generalized secure workspace-file reader and SHA-256 helper.

**Rollback unit:** Explicit-file reader generalization, contract commands,
invalidation rules, parser registration, and contract command tests. Roll back
with schema contract fields from Task 2 if removing the feature.

**Steps:**

- [x] Generalize the safe artifact descriptor into a bounded explicit-file
      reader without weakening Markdown artifact security.
- [x] Enforce normalized exact-root paths, regular-file ownership, no links or
      reparse points, per-file/source-count/total-byte limits, and no scan.
- [x] Implement initial bind and rebind comparison for old/new Outcome IDs and
      normalized record hashes.
- [x] Require distinct scope-delta approval exactly when the declaration is
      non-empty; store approval as an audit claim, not authentication.
- [x] Hash contract semantics and explicit parent/baseline sources.
- [x] Persist bound/drifted status and reason codes without source contents.
- [x] Invalidate plan and verification whenever the approved contract changes.
- [x] Register both commands and return compact mutation results.
- [x] Add path, size, duplicate, missing, changed, unsafe, baseline-origin,
      scope contradiction, stale revision, failed-bind atomicity, and drift
      tests.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_outcome_contract.py' -v
python3 -m unittest discover -s tests -p 'test_state.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_outcome_contract.py
```

Expected evidence: valid bind/rebind/check paths pass; every unsafe or
contradictory case preserves the prior revision/state.
Scope rationale: connected—the new reader extends a security boundary shared
with existing artifact access.

## Task 4 — Plan, verification, lifecycle, and completion gates

**Testable outcome:** A tracked workflow can enter execution/verification and
complete only with a current bound contract, complete Plan Map or direct lock,
passing Outcome/FID evidence, required three-verdict approval, and zero blockers.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_outcome_gates.py`;
- modify `tests/test_state.py` for shared lifecycle compatibility only.

**Dependencies and consumers:**

- Depends on Tasks 1–3.
- Task 6 teaches phase skills to call these interfaces.
- Task 8 uses them on an isolated self-host ledger.

**Named interfaces:**

- `validate-plan --artifact`
- `record-verification --artifact`
- gated `checkpoint`, `resume`, `handoff`, and `complete`
- tracked direct `start --phase execute --direct-lock`.

**Rollback unit:** Plan/verification commands, lifecycle checks, direct-lock
behavior, completion evaluator integration, and their tests. It is coupled to
Task 3 because execution readiness requires a contract.

**Steps:**

- [x] Implement Plan Map parsing against active/deferred/removed Outcome sets
      and persist only semantic digest plus coverage summary.
- [x] Reject missing/unknown/evidence-less mappings atomically and report all
      offending IDs.
- [x] Implement direct `OUT-001` objective lock with no planning artifact and
      require later verification evidence.
- [x] Gate transition into execute, execute progress, legacy resume,
      execute/verify handoff, and transition into verify according to the
      approved matrix.
- [x] Implement Verification Record parsing, secure FID evidence hashing,
      per-Outcome results, baseline/FID totals, blockers, and three verdicts.
- [x] Persist valid `fail`/`blocked` evidence while rejecting malformed or
      contradictory records without mutation.
- [x] Revalidate current contract, plan/direct lock, and evidence at completion.
- [x] Return every completion failure in one response; complete atomically only
      when none remain.
- [x] Add tests for all transitions, direct/lean/full behavior, invalidation,
      legitimate blocked evidence, every independent completion failure,
      aggregated errors, and stale writer conflicts.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_outcome_gates.py' -v
python3 -m unittest discover -s tests -p 'test_state.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_outcome_gates.py
```

Expected evidence: complete mappings can execute; narrower plans cannot; each
completion condition fails independently and collectively without a revision
change.
Scope rationale: connected—these commands share lifecycle and completion
contracts with the existing state CLI.

## Task 5 — Compact recovery and hook isolation

**Testable outcome:** Session, prompt-boundary, worker, and OpenCode-injected
recovery show last-known lock summaries while proving that render/hook paths
never open, stat, parse, or hash contract/evidence sources.

**Files:**

- modify `scripts/littlepowers_state.py`;
- inspect and modify `hooks/session-start.py` only if the shared renderer
  interface requires it;
- modify `tests/test_hook.py`;
- modify `tests/test_opencode_plugin.py` only for affected injection assertions.

**Dependencies and consumers:**

- Depends on Tasks 2–4 persisted summaries.
- All four host adapters consume the same renderer.

**Rollback unit:** Recovery-summary fields and hook tests. The state schema stays
valid if this display unit is reverted, but hook tests and docs must revert with
it.

**Steps:**

- [x] Add bounded `contract`, `coverage`, `baseline`, and `fidelity` summary
      values to brief/full recovery data.
- [x] Keep terminal-state silence and existing handoff rendering.
- [x] Mock the secure reader/parser/hash helpers and prove renderers never call
      them.
- [x] Verify no source/evidence path, title, approval prose, or contents appear.
- [x] Exercise SessionStart, UserPromptSubmit, SubagentStart, missing state,
      malformed state, and OpenCode injection behavior.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_hook.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_plugin.py' -v
python3 -m compileall -q hooks scripts tests/test_hook.py tests/test_opencode_plugin.py
```

Expected evidence: summaries appear only for active state; mocked source readers
have zero calls; every hook remains fail-open.
Scope rationale: connected—the renderer is shared across four hosts, but no
manifest or packaging surface changes yet.

## Task 6 — Skills and shared protocol reference

**Testable outcome:** Every applicable phase uses the deterministic commands and
one shared grammar reference; legacy reconciliation, three verdicts, and
“product scope ≠ rollback units” are consistent without bloating always-on skill
metadata.

**Files:**

- create `references/outcome-lock.md`;
- modify:
  - `skills/using-littlepowers/SKILL.md`
  - `skills/brainstorming/SKILL.md`
  - `skills/compact-shaping/SKILL.md`
  - `skills/writing-specs/SKILL.md`
  - `skills/designing-solutions/SKILL.md`
  - `skills/writing-plans/SKILL.md`
  - `skills/executing-plans/SKILL.md`
  - `skills/reviewing-changes/SKILL.md`
  - `skills/verifying-work/SKILL.md`
  - `skills/managing-littlepowers/SKILL.md`
- inspect `skills/debugging-systematically/SKILL.md`; change only if a real
  protocol reference is required;
- modify `tests/test_manifests.py`;
- modify `tests/test_engineering_disciplines.py`.

**Dependencies and consumers:**

- Depends on final command names and semantics from Tasks 3–5.
- Codex, Claude Code, Qoder, and OpenCode consume the same files.

**Rollback unit:** Shared protocol reference, phase-skill call sites, and
skill-contract tests. Revert as one unit if command semantics revert.

**Steps:**

- [x] Use `skill-creator` guidance before editing and keep imperative,
      concise, model-neutral skill bodies.
- [x] Put exact JSON record grammar and command examples in one shared reference;
      load it only in phases that create or validate a record.
- [x] Route legacy active state to reconciliation before executable work.
- [x] Emit/bind contracts at approved brainstorm/spec/shape boundaries.
- [x] Emit/validate Plan Maps before execute and Verification Records before
      complete.
- [x] Make all review/execution wording consistently name work-unit compliance,
      approved-outcome fidelity, and code quality.
- [x] State explicitly that product slices are forbidden while rollback units,
      checkpoints, dependency-safe implementation order, and small commits
      remain expected.
- [x] Keep direct untracked work unchanged and lean work free of spec/design.
- [x] Add behavior-facing text/reference assertions without treating them as a
      substitute for Tasks 1–5 runtime tests.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_manifests.py' -v
python3 -m unittest discover -s tests -p 'test_engineering_disciplines.py' -v
for skill in skills/*; do
  python3 /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected evidence: all skill-contract tests and eleven official skill
validators pass; descriptions remain concise and model-neutral.
Scope rationale: connected—all supported hosts share these phase contracts.

## Task 7 — Cross-host, public, version, and self-host surfaces

**Testable outcome:** Every host and public document describes the same
`1.2.0-alpha.1` Outcome Lock behavior, limitations, migration/rollback, and new
task/session pickup boundary; a machine contract projection contains exactly
OUT-001…OUT-023 for isolated self-host verification.

**Files:**

- create `docs/littlepowers/contracts/2026-07-26-outcome-lock.md`;
- modify `README.md`, `README.zh-CN.md`, `CHANGELOG.md`, `CONTRIBUTING.md`;
- modify `docs/capability-matrix.md`, `docs/model-compatibility.md`,
  `docs/security-model.md`, and `docs/expert-review.md`;
- modify `evals/scenarios.md` and `evals/README.md`;
- modify `.codex-plugin/plugin.json`;
- modify `.claude-plugin/plugin.json`;
- modify `.claude-plugin/marketplace.json`;
- modify `.qoder-plugin/plugin.json`;
- inspect `.agents/plugins/marketplace.json` and change only user-visible
  metadata that is actually stale;
- modify `package.json`;
- inspect `.opencode/plugins/littlepowers.js`; change only if the shared hook
  contract or metadata requires it;
- modify `tests/test_manifests.py`.

**Dependencies and consumers:**

- Depends on Tasks 1–6 final behavior and wording.
- Task 8 consumes the self-host contract and evaluation scenarios.

**Rollback unit:** Version identity, public docs, capability/security/model
claims, evaluation scenarios, host metadata, and self-host contract. Revert
metadata and claims together; do not leave manifests on different versions.

**Steps:**

- [x] Build the bootstrap Contract block from the approved specification's
      exact OUT-001…OUT-023 set, with no added/deferred/removed Outcome.
- [x] Bind the approved v1.1 evaluation report and prior scope artifacts as
      compatibility/requirements sources; define cross-host fidelity IDs.
- [x] Document schema-3 migration, pre-schema3 restore procedure, legacy
      reconciliation, deterministic limits, semantic boundary, and no-hot-load
      session behavior.
- [x] Explain direct/lean/full cost and that gates add no model calls,
      background scans, automatic tests, or effort/model selection.
- [x] Record the v1.1.1-compatible wording fixes under the 1.2 candidate without
      publishing a separate release in this workflow.
- [x] Align all version-bearing surfaces to `1.2.0-alpha.1`.
- [x] Add adversarial scenarios for omitted IDs, false `No scope delta`, old
      workflow, changed source, self-generated baseline, incomplete FID, and
      completion aggregation.
- [x] Update manifest tests to compare aligned identity and new capability
      wording.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_manifests.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_plugin.py' -v
python3 /Users/nathan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/nathan/workspace/littlepowers
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:$PATH node --check .opencode/plugins/littlepowers.js
```

Expected evidence: release identity agrees, plugin validation passes, OpenCode
syntax exits 0, and the bootstrap Contract contains the same 23 unique IDs as
the approved specification.
Scope rationale: broad metadata boundary, but this task runs focused manifest
and syntax validation only; the complete host matrix is reserved for Task 8.

## Task 8 — Integrated review, verification, and self-host evidence

**Testable outcome:** The integrated source candidate passes every applicable
check once, survives isolated schema-2→3 self-host migration and gate execution,
receives all three review verdicts, and records evidence without installing or
publishing.

**Files:**

- create `docs/littlepowers/evidence/2026-07-26-outcome-lock.md`;
- create `evals/results/2026-07-26-v1.2-outcome-lock.md`;
- modify only defects discovered by verification in their owning task files;
- inspect every changed/untracked path and the live `.littlepowers` boundary.

**Dependencies and consumers:**

- Depends on Tasks 1–7.
- This is the single aggregate acceptance owner for OUT-001…OUT-023.

**Rollback unit:** Evidence/report artifacts are independently removable.
Defect fixes remain coupled to their owning implementation task. The live ledger
is not migrated until isolated migration evidence passes and a safe current-task
boundary is confirmed.

**Steps:**

- [x] Run each original focused reproducer after the latest owning edit.
- [x] Create a temporary exact-root fixture containing a copy of a schema-2
      active ledger and the approved bootstrap Contract/Plan Map.
- [x] Use the edited source CLI on that fixture to verify read-only migration,
      pre-schema3 archive, contract bind, plan validation, drift, blocked
      completion, passing verification, and successful completion.
- [x] Confirm the repository's live ledger was not touched by temporary tests.
- [x] Run the complete Python suite and compile checks once.
- [x] Run all eleven skill validators and all available host validators.
- [x] Use `reviewing-changes` read-only against the approved specification and
      design; report work-unit compliance, approved-outcome fidelity, and code
      quality separately.
- [x] Adjudicate and repair every critical/important finding, rerunning only its
      focused rollback-unit checks before the final aggregate rerun if relevant
      integrated files changed.
- [x] Use `verifying-work` to build a fresh claim-evidence matrix for all 23
      Outcomes and the cross-host FIDs.
- [x] Write the Verification Record and evaluation report with exact commands,
      exits, counts, limitations, and no unexecuted model claim.
- [x] Inspect `git diff --check`, complete diff, status, untracked files,
      temporary/debug/generated files, secrets, and scope.
- [x] Decide the live schema-3 ledger pickup only at a safe boundary. If the
      currently loaded 1.1 task cannot safely adopt the source runtime, leave
      the live schema-2 ledger intact and explicitly require installation plus a
      new task/session rather than hot-loading.

**Aggregate validation:**

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
for skill in skills/*; do
  python3 /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
python3 /Users/nathan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/nathan/workspace/littlepowers
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:$PATH claude plugin validate --strict .
qodercli plugins validate .
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:$PATH node --check .opencode/plugins/littlepowers.js
git diff --check
git status --short
```

Expected evidence:

- all Python tests pass on the local interpreter;
- compilation and all eleven skill validators pass;
- Codex, Claude strict, available Qoder, and OpenCode validations pass, or an
  unavailable host is reported precisely rather than counted as success;
- isolated migration/gates complete with the expected archive and no live-ledger
  mutation;
- review verdicts are `pass`, `pass`, and `approve`;
- every active Outcome and required FID is present and passing;
- no unintended file, secret, temporary artifact, or unapproved scope delta
  remains.

Scope rationale: broad—state schema, migration, security, hooks, packaging,
skills, public protocol, and four hosts share the release boundary. This is the
one justified full-suite/matrix run after focused rollback-unit checks.

## Outcome Plan Map

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 2"],
      "evidence": ["test:schema3-identity", "inspection:state-json"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 3"],
      "evidence": ["security:explicit-file-reader", "test:source-binding"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 1", "Task 3", "Task 6"],
      "evidence": ["test:contract-record", "inspection:phase-contract"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 3"],
      "evidence": ["test:contract-drift", "inspection:drift-status"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 2", "Task 4", "Task 6"],
      "evidence": ["test:legacy-reconciliation", "inspection:recovery-route"]
    },
    {
      "outcome": "OUT-006",
      "tasks": ["Task 1", "Task 4"],
      "evidence": ["test:coverage-gate", "inspection:coverage-summary"]
    },
    {
      "outcome": "OUT-007",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["test:scope-delta-gate", "inspection:delta-approval"]
    },
    {
      "outcome": "OUT-008",
      "tasks": ["Task 1", "Task 3", "Task 4"],
      "evidence": ["test:baseline-provenance", "inspection:baseline-state"]
    },
    {
      "outcome": "OUT-009",
      "tasks": ["Task 1", "Task 4"],
      "evidence": ["test:fidelity-matrix", "inspection:fid-coverage"]
    },
    {
      "outcome": "OUT-010",
      "tasks": ["Task 1", "Task 4", "Task 6"],
      "evidence": ["test:three-verdicts", "review:verdict-consistency"]
    },
    {
      "outcome": "OUT-011",
      "tasks": ["Task 4"],
      "evidence": ["test:completion-gate", "inspection:all-failures"]
    },
    {
      "outcome": "OUT-012",
      "tasks": ["Task 2", "Task 4", "Task 6"],
      "evidence": ["test:direct-lock", "inspection:direct-cost"]
    },
    {
      "outcome": "OUT-013",
      "tasks": ["Task 4", "Task 6"],
      "evidence": ["test:lean-route-lock", "inspection:no-lean-spec-design"]
    },
    {
      "outcome": "OUT-014",
      "tasks": ["Task 4", "Task 6"],
      "evidence": ["test:full-route-reuse", "inspection:single-outcome-set"]
    },
    {
      "outcome": "OUT-015",
      "tasks": ["Task 6", "Task 8"],
      "evidence": ["inspection:rollback-unit-wording", "review:one-definition-of-done"]
    },
    {
      "outcome": "OUT-016",
      "tasks": ["Task 3", "Task 4"],
      "evidence": ["test:transition-boundaries", "inspection:no-prompt-hash"]
    },
    {
      "outcome": "OUT-017",
      "tasks": ["Task 2", "Task 3", "Task 4"],
      "evidence": ["test:mutation-atomicity", "security:revision-conflict"]
    },
    {
      "outcome": "OUT-018",
      "tasks": ["Task 2", "Task 8"],
      "evidence": ["test:migration-archive", "migration:self-host-copy"]
    },
    {
      "outcome": "OUT-019",
      "tasks": ["Task 5"],
      "evidence": ["test:hook-summary", "inspection:zero-source-reads"]
    },
    {
      "outcome": "OUT-020",
      "tasks": ["Task 1", "Task 3", "Task 5", "Task 8"],
      "evidence": ["inspection:stdlib-only", "test:bounded-runtime"]
    },
    {
      "outcome": "OUT-021",
      "tasks": ["Task 5", "Task 6", "Task 7", "Task 8"],
      "evidence": ["host:four-host-validation", "inspection:new-session-boundary"]
    },
    {
      "outcome": "OUT-022",
      "tasks": ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"],
      "evidence": ["test:behavioral-regressions", "inspection:no-static-substitute"]
    },
    {
      "outcome": "OUT-023",
      "tasks": ["Task 7", "Task 8"],
      "evidence": ["host:aggregate-validation", "review:evidence-limited-claims"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->

## External limitations

- A missing Claude, Qoder, Node, or Codex validator is a reported limitation,
  not a passing result.
- No remote model credentials or authenticated GPT-5.6/Fable/Opus evaluation are
  assumed.
- No existing task can hot-load the new plugin. Local installation and new-task
  pickup are separate actions after source verification.
- The deterministic gate protects the approved ID contract; it cannot
  semantically infer a requirement that was omitted from the first approved
  projection.
