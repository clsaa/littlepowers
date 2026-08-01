# Littlepowers v1.3 Review Lease implementation plan

Date: 2026-07-31

Status: approved for unattended local implementation and validation

## Goal

Implement the complete schema-4 / protocol-1.3 Review Lease outcome from
OUT-001 through OUT-024: deterministic persisted review policies and artifact
gates, low-friction fixed implementation intent, pre-authorized timed
continuation in Codex and Claude Code, truthful manual fallback in Qoder and
OpenCode, and a validated `1.3.0-alpha.1` candidate.

## Approved inputs

- `docs/littlepowers/brainstorms/2026-07-31-review-lease.md`
- `docs/littlepowers/specs/2026-07-31-review-lease.md`
- `docs/littlepowers/designs/2026-07-31-review-lease.md`
- `AGENTS.md`
- `README.md`
- `skills/using-littlepowers/SKILL.md`
- `scripts/littlepowers_state.py`
- `evals/scenarios.md`
- `docs/security-model.md`
- `docs/capability-matrix.md`
- the user's explicit request to design, implement, and validate locally
  without further questions

## Scope and baseline

No scope delta.

The approved product contract is the 24-ID specification. Baseline provenance
is not applicable. Schema-3 Outcome Lock, proportional route behavior,
single-writer recovery, four-host discovery, security boundaries, and existing
tests are compatibility inputs that must remain intact.

## Global constraints

- Tasks 1–6 form one continuous implementation stream and one definition of
  done. They are dependency and rollback boundaries, not waves, product
  slices, staged releases, or stopping points.
- The root coordinator is the only live-ledger writer. No worker or host
  callback mutates the ledger without exact workflow/revision commands.
- Runtime code remains Python 3 standard library only. No daemon, polling
  loop, telemetry, repository recursion, sibling scan, transcript parser,
  hidden-reasoning capture, automatic broad test, or model/effort override is
  added.
- Hooks and the OpenCode transform remain read-only, bounded, network-free,
  transcript-free, fail-open, and silent without unfinished state.
- Automatic review resolution never approves a scope delta or expands commit,
  push, PR, publish, deploy, destructive-action, secret, or access authority.
- Use focused tests after each independently reversible unit. Run the full
  suite and cross-host release matrix once after integration, and rerun it only
  if an integrated fix invalidates that evidence.
- Keep the active workflow on the installed 1.2 CLI through Plan validation and
  the transition to execution. Exercise candidate schema 4 on temporary roots
  first. After focused migration evidence passes, migrate the live ledger once
  with the source CLI and use that CLI for all later mutations.
- Source changes will intentionally drift the self-hosted Contract. Rebind the
  unchanged specification and revalidate this complete Plan Map at the final
  integration boundary; do not weaken or renumber Outcomes.
- Do not commit, push, tag, publish, install, replace the currently enabled
  plugin, or modify another repository in this workflow. Those actions need
  separate user authorization.

## Definition of Done

- Schema 4 exactly validates four review modes, gate records, bounded audit
  state, and schema 1/2/3 migration with a byte-identical pre-schema4 archive.
- Gate commands enforce artifact bytes, UTC timing, route constraints, Outcome
  Lock health, scope/baseline rules, CAS, mutation isolation, and one-time
  resolution.
- Explicit implementation mandates avoid redundant Lean/Compact approval;
  blocking remains the ambiguous/default path; timed next-phase and
  through-execute boundaries behave exactly as specified.
- Codex guidance arms only a callable safe same-task callback and never claims
  success otherwise. The Claude runner performs at most one exact-session
  invocation without forbidden flags, shell interpolation, polling, or retry.
- Qoder/OpenCode show schema-4 state and truthfully require manual wake-up.
- Direct untracked work has zero Review Lease work; tracked direct work stores
  policy only and never parks a gate.
- English/Chinese docs, references, snippets, manifests, package metadata,
  changelog, scenarios, and evaluation evidence consistently identify
  `1.3.0-alpha.1`, schema 4, and protocol 1.3.
- Fresh focused checks, full tests, compilation, eleven skill validators,
  Codex validation, Claude strict validation, available Qoder validation,
  OpenCode syntax/behavior validation, and final diff inspection pass.
- The final Verification Record reports work-unit compliance `pass`,
  approved-outcome fidelity `pass`, code quality `approve`, all 24 Outcomes
  passing, and zero blocking evidence, or the workflow remains incomplete.

## Continuous implementation order

Execute Tasks 1–6 in order without phase-level product slicing or task-level
approval pauses. The order is state foundation → deterministic commands →
skill/recovery integration → optional host wake-up → release surfaces → one
aggregate reconciliation and verification boundary.

## Task 1 — Schema 4, policy model, and recoverable migration

**Testable outcome:** New state is schema 4/protocol 1.3 with exact review
records; every policy combination and timestamp bound is validated; schema
1/2/3 reads preserve prior state; the first successful mutation archives exact
raw pre-schema4 bytes once.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_review_state.py`;
- modify `tests/test_outcome_migration.py`;
- modify shared state fixtures in `tests/test_state.py`,
  `tests/test_outcome_self_host.py`, and other test modules only where schema
  identity is their existing concern.

**Dependencies and consumers:** No implementation dependency. Task 2 consumes
the review validator, migration envelope, raw archive writer, and pure status
helpers. Every later task consumes schema-4 state.

**Named interfaces:** `new_review_state`, exact review validator, schema-3→4
migrator, raw migration source, bounded atomic raw archive writer, optional
review arguments on `start`.

**Rollback unit:** Schema/protocol constants, review data model, migration
chain, archive plumbing, and their fixtures/tests. Roll back together before
any Task-2 command persists a gate.

**Steps:**

- [ ] Add review enums, exact key sets, duration bounds, timestamp validation,
      and canonical default records.
- [ ] Add `review` to schema-4 state and `start` policy arguments without
      changing the untracked direct path.
- [ ] Implement 1→2→3→4 view migration; preserve every Outcome Lock and
      workflow field while defaulting policy to blocking with no gate.
- [ ] Retain validated original state bytes through a mutation transaction and
      atomically archive them once with `pre-schema4-v<schema>` naming.
- [ ] Keep future schema/protocol rejection, state-size, ownership, link,
      permission, lock, revision, root-pinning, and atomicity defenses.
- [ ] Update existing fixtures mechanically to schema 4 without weakening
      explicit legacy tests.
- [ ] Add positive/negative tests for all policy combinations, 60/604800
      boundaries, unknown keys, future timestamps, direct behavior, terminal
      migration, rejected-write atomicity, exact archive bytes, and one-time
      archival.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_review_state.py' -v
python3 -m unittest discover -s tests -p 'test_outcome_migration.py' -v
python3 -m unittest discover -s tests -p 'test_state.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_review_state.py tests/test_outcome_migration.py
```

Expected evidence: policy/schema cases pass; exact raw bytes match the archive;
rejected candidates create no archive or revision; existing state security and
concurrency tests remain green.

Scope rationale: connected—the schema and writer are shared by every command,
so focused migration tests are paired with the existing state module before
the candidate touches the live ledger.

## Task 2 — Deterministic Review Gate commands and lifecycle isolation

**Testable outcome:** The CLI parks, reports, resolves, replaces, and cancels
one exact planning artifact; every mode follows its timing/route rules; stale,
drifted, incomplete, paused, or replayed requests fail atomically; ordinary
mutations cannot bypass an open gate.

**Files:**

- modify `scripts/littlepowers_state.py`;
- create `tests/test_review_commands.py`;
- modify `tests/test_outcome_gates.py`, `tests/test_outcome_contract.py`, and
  `tests/test_state.py` for lifecycle interaction regressions.

**Dependencies and consumers:** Depends on Task 1. Task 3 calls these commands;
Task 4 reads the pure status interface; Task 6 exercises the integrated gates.

**Named interfaces:** `set-review-policy`, `park-review`, `review-status`,
`resolve-review`, `cancel-review`, shared fresh-gate evaluator, open-gate
mutation guard.

**Rollback unit:** Command parsers/handlers, pure gate evaluator, mutation
guard, and command tests. It is coupled to Task 1's persisted review record but
not to host adapters.

**Steps:**

- [ ] Add exact CLI parsers and workflow/revision/gate-revision validation.
- [ ] Hash only the current ledger planning artifact through the existing
      secure bounded reader and snapshot policy authority in the gate.
- [ ] Return bounded `no_gate`, `waiting`, `eligible`, or `blocked` status
      without mutation or artifact content.
- [ ] Enforce resolution-kind matching, UTC deadline, observed-no-intervention
      claim, Lean/Compact implementation mandate, and window boundary policy
      transition.
- [ ] Reuse fresh Contract/Plan/baseline evaluation at applicable boundaries;
      reject automatic scope delta and unresolved-question claims.
- [ ] Support exact same-artifact replacement and bounded cancellation audit.
- [ ] Guard every ordinary state mutation while a gate is open; allow only
      documented review mutations and whole-workflow cancellation.
- [ ] Make callback replay, stale CAS, changed bytes, path replacement, clock
      rollback, pause/terminal state, drift, incomplete coverage, and missing
      baseline no-op failures.
- [ ] Verify tiny untracked direct work never invokes the CLI and tracked direct
      work never accepts `park-review`.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_review_commands.py' -v
python3 -m unittest discover -s tests -p 'test_outcome_gates.py' -v
python3 -m unittest discover -s tests -p 'test_outcome_contract.py' -v
python3 -m compileall -q scripts/littlepowers_state.py tests/test_review_commands.py
```

Expected evidence: each mode and timestamp edge has a passing behavior test;
every rejected/replayed command preserves state bytes and revision; ordinary
lifecycle commands cannot cross the gate; Outcome Lock behavior stays intact.

Scope rationale: connected—gate commands deliberately mediate the shared
lifecycle and Outcome Lock boundary, so affected gate/contract modules run
together.

## Task 3 — Intent routing, phase integration, and stored-only recovery

**Testable outcome:** Existing skills record blocking, implementation,
windowed, or unattended intent proportionally; every Lean/Compact/Full artifact
uses the deterministic gate; new messages cancel or preserve it correctly;
hooks render bounded stored review facts without evaluating or scheduling.

**Files:**

- modify `skills/using-littlepowers/SKILL.md`;
- modify phase skills under `skills/brainstorming`, `compact-shaping`,
  `writing-specs`, `designing-solutions`, and `writing-plans`;
- modify `skills/executing-plans/SKILL.md` and
  `skills/managing-littlepowers/SKILL.md` where recovery/status ownership
  changes;
- create `references/review-lease.md`;
- modify `references/outcome-lock.md` only for schema/lifecycle integration;
- modify recovery rendering in `scripts/littlepowers_state.py`;
- modify `tests/test_hook.py`, `tests/test_manifests.py`, and
  `tests/test_engineering_disciplines.py`.

**Dependencies and consumers:** Depends on Tasks 1–2. Task 4 reuses the fixed
callback contract. Task 5 documents the same host behavior.

**Named interfaces:** review-intent routing table, artifact park/resolve phase
sequence, intervention cancellation rule, recovery `review` summary, Codex
conditional Scheduled Task procedure.

**Rollback unit:** Skill/reference wording, recovery renderer, and static/hook
tests. Roll back together to avoid skills naming unavailable commands.

**Steps:**

- [ ] Add an early router check for any open gate before ordinary request
      reconciliation; distinguish approval, correction/hold, timer keep/reset,
      side/status, and unrelated replacement.
- [ ] Record explicit intent at start or with `set-review-policy`; keep
      ambiguity blocking and restrict implementation mandate to fixed
      Lean/Compact work.
- [ ] Replace prompt-only phase waits with checkpoint → park → status →
      resolve/wait → existing bind/validate flow in every planning skill.
- [ ] Preserve distinct scope-delta approval, parent Contract inheritance,
      baseline provenance, one continuous definition of done, and no product
      slicing.
- [ ] Add the exact protocol command/reference guide without duplicating its
      grammar throughout all skills.
- [ ] Render mode, artifact key, stored gate state, and deadline from state
      only; keep Hook/OpenCode behavior silent, bounded, read-only, and
      fail-open.
- [ ] Describe Codex same-task callback creation only when a callable safe
      Scheduled Task surface exists; require exact root/workflow/gate prompt,
      one-shot termination, and truthful failure reporting.
- [ ] State Qoder/OpenCode manual wake-up limits and prohibit fabricated
      scheduler claims.
- [ ] Add adversarial static/behavior assertions for ambiguous intent, fixed
      implementation, timed next phase, timed execute, correction, status,
      compaction, no capability, no scope-delta approval, and authority limits.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_hook.py' -v
python3 -m unittest discover -s tests -p 'test_manifests.py' -v
python3 -m unittest discover -s tests -p 'test_engineering_disciplines.py' -v
python3 /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/using-littlepowers
python3 /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/writing-plans
```

Expected evidence: recovery tests prove no artifact read or state mutation;
phase tests name every new deterministic command; existing proportional,
Outcome Lock, no-slicing, and conditional-discipline assertions remain green.

Scope rationale: connected—the router, phase skills, and recovery renderer are
one user-facing protocol boundary, while full eleven-skill validation remains
reserved for Task 6.

## Task 4 — Exact-session Claude Code one-shot adapter

**Testable outcome:** An explicitly windowed Claude gate can arm at most one
private detached sleeper for one canonical session; the child wakes once,
rechecks the exact gate, makes at most one normal `claude -p --resume` call,
stores no output, and never retries or bypasses permissions.

**Files:**

- create `scripts/littlepowers_review_runner.py`;
- create `tests/test_review_runner.py`;
- modify `skills/using-littlepowers/SKILL.md` and/or
  `references/review-lease.md` only for the exact invocation procedure;
- modify `.gitignore` behavior only if the existing `.littlepowers/.gitignore`
  does not already cover private job metadata.

**Dependencies and consumers:** Depends on Task 2's read-only status evaluator
and Task 3's callback contract. Task 5 documents security/host limitations.

**Named interfaces:** runner `schedule`, runner `status`, private child entry
point, private atomic job metadata, fixed resumed-session prompt.

**Rollback unit:** Runner script, runner tests, and its conditional skill
paragraph. Removing it leaves the durable Review Gate and manual Claude resume
fully functional.

**Steps:**

- [ ] Validate canonical root, workflow UUID, gate revision, future windowed
      deadline, session UUID, and discovered Claude executable.
- [ ] Create one mode-0600 job record under the ignored private state store and
      reject links, unsafe ownership, path replacement, and duplicate active
      sleepers.
- [ ] Spawn one detached internal child with no inherited stdin/stdout/stderr;
      sleep once to the deadline without polling.
- [ ] Recheck exact root/workflow/gate and require `eligible` immediately before
      invoking the host.
- [ ] Invoke an argument vector with `shell=False` exactly once and normal
      permissions; prohibit `--continue`, permission bypass, model/effort
      flags, transcript access, interpolation, and retries.
- [ ] Bound the resumed call, record only status/timestamps/PID/exit or timeout,
      and preserve the gate on every host failure.
- [ ] Make exact duplicate scheduling idempotent and stale/cancelled/replaced
      jobs exit without a model call.
- [ ] Test with patched time and a fake executable; inspect argv and metadata,
      including no output persistence, timeout, reboot/lost-sleeper recovery,
      and one-call maximum.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_review_runner.py' -v
python3 -m compileall -q scripts/littlepowers_review_runner.py tests/test_review_runner.py
python3 scripts/littlepowers_review_runner.py --help
```

Expected evidence: fake-host argv contains exact `-p --resume <session-id>` and
no forbidden flag; duplicate/stale paths make zero host calls; job files are
private and content-free; failures leave the Review Gate open.

Scope rationale: local—the optional runner is isolated from hooks and ordinary
routes and can be removed without changing core state semantics.

## Task 5 — Four-host packaging, public protocol, and evaluation scenarios

**Testable outcome:** Every release surface consistently describes schema 4,
protocol 1.3, four review policies, safe host-specific wake-up limits, rollback,
authority, and version `1.3.0-alpha.1`; all eleven skills remain discoverable.

**Files:**

- modify `.codex-plugin/plugin.json`;
- modify `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`;
- modify `.qoder-plugin/plugin.json`;
- modify `package.json` and marketplace metadata under `.agents/`;
- modify `README.md`, `README.zh-CN.md`, `CHANGELOG.md`;
- modify `assets/agents-snippet.md`, `assets/claude-snippet.md`;
- modify `docs/capability-matrix.md`, `docs/security-model.md`, and
  `docs/model-compatibility.md`;
- modify `evals/scenarios.md` and `evals/README.md`.

**Dependencies and consumers:** Depends on Tasks 1–4 so documentation names
implemented behavior. Task 6 validates the integrated package and writes the
dated result.

**Named interfaces:** package version parity, install/upgrade/rollback
instructions, Codex/Claude/Qoder/OpenCode capability matrix, Review Lease
adversarial scenarios.

**Rollback unit:** All release identity and public documentation changes.
Revert together with the code candidate; never leave a 1.3 manifest describing
1.2 behavior or vice versa.

**Steps:**

- [ ] Bump every manifest/package/marketplace version to
      `1.3.0-alpha.1` and keep name/repository/skill discovery aligned.
- [ ] Update English/Chinese quick starts and route behavior for blocking,
      fixed implementation, timed fallback, and explicit unattended use.
- [ ] Document Codex capability detection, Claude optional runner, and
      Qoder/OpenCode manual continuation without overstating live support.
- [ ] Document schema-4 archive restoration before a 1.2 rollback and the
      prohibition on hot-replacing an active task.
- [ ] Update security/privacy and model compatibility: no daemon/polling,
      scheduler in Hooks, extra agent, model/effort selection, or ordinary
      route model turn.
- [ ] Add evaluation scenarios for all four modes, intervention, artifact
      drift, replay, lost callback, exact session, and direct fast path while
      preserving all existing Outcome Lock adversarial scenarios.
- [ ] Keep public authority wording explicit: review continuation is not
      external-write permission.

**Focused validation:**

```bash
python3 -m unittest discover -s tests -p 'test_manifests.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_plugin.py' -v
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:/Users/nathan/.local/bin:$PATH node --check .opencode/plugins/littlepowers.js
git diff --check
```

Expected evidence: version parity and eleven-skill discovery assertions pass;
OpenCode remains read-only; docs contain no 1.2 current-release claim or false
host/model certification; formatting is clean.

Scope rationale: connected—package identity, host capability claims, security,
and rollback instructions are one release-facing contract.

## Task 6 — Self-host reconciliation, integrated review, and release evidence

**Testable outcome:** The live workflow safely adopts schema 4 only after
isolated evidence, all source changes reconcile to the unchanged 24-ID
Contract/Plan Map, the full four-host validation boundary passes, and a fresh
Verification Record/evaluation report supports every completion claim.

**Files:**

- exercise all changed runtime, skill, package, docs, and test files;
- create `docs/littlepowers/evidence/2026-07-31-review-lease.md`;
- create `evals/results/2026-07-31-v1.3-review-lease.md`;
- modify this plan only to check completed steps and record exact final
  limitations; do not rewrite scope or Outcomes.

**Dependencies and consumers:** Depends on Tasks 1–5. This is the sole broad
integration/release boundary and final consumer of all 24 Outcomes.

**Named interfaces:** isolated self-host migration, live
`set-review-policy unattended`, Contract rebind, Plan Map revalidation,
Verification Record, completion gate, cross-host validators.

**Rollback unit:** The complete uncommitted candidate. Defect fixes remain
coupled to their owning prior task. Live-ledger rollback uses the exact
pre-schema4 archive, not source-file reversion alone.

**Steps:**

- [ ] On a temporary exact-root repository, run schema-3→4 migration, all four
      policy paths, artifact replacement/drift, Outcome Lock gates, runner
      fake-host behavior, verification, completion, and archive restoration.
- [ ] Confirm temporary tests did not mutate the live ledger.
- [ ] After Tasks 1–2 focused checks pass, use the source CLI and current
      revision to perform the live first mutation with policy `unattended`;
      verify one exact pre-schema4 archive before any further live mutation.
- [ ] Continue all checkpoints through the source CLI only.
- [ ] Rebind the unchanged specification after implementation-modified source
      files settle, then validate the complete 24-ID Plan Map again.
- [ ] Run the complete Python suite and compilation once.
- [ ] Run all eleven official skill validators plus Codex, Claude strict,
      available Qoder, and OpenCode validators.
- [ ] Perform read-only integrated review with separate work-unit compliance,
      approved-outcome fidelity, and code-quality verdicts; repair every
      actionable finding and rerun its focused checks.
- [ ] If an integrated repair changes a shared runtime/package boundary, rerun
      the affected aggregate commands once so final evidence is fresh.
- [ ] Build the Verification Record with passing rows for OUT-001…OUT-024,
      three independent verdicts, exact command evidence tokens, and zero
      blockers; record it through the state CLI.
- [ ] Write the dated evaluation report with exact exits/counts, unsupported
      live scheduling/model limitations, and no inferred certification.
- [ ] Inspect `git diff --check`, complete diff, status, untracked files,
      temporary/debug/generated files, secrets, executable bits, and scope.
- [ ] Run the deterministic completion gate. Do not commit, push, tag,
      publish, or install the candidate.

**Aggregate validation:**

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
for skill in skills/*; do
  python3 /Users/nathan/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
python3 /Users/nathan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/nathan/workspace/littlepowers
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:/Users/nathan/.local/bin:$PATH claude plugin validate --strict .
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:/Users/nathan/.local/bin:$PATH qodercli plugins validate .
PATH=/Users/nathan/.nvm/versions/node/v24.15.0/bin:/Users/nathan/.local/bin:$PATH node --check .opencode/plugins/littlepowers.js
git diff --check
git status --short
```

Expected evidence:

- all Python tests pass after the latest integrated code change;
- compilation and all eleven skill validators pass;
- Codex and Claude strict validation pass;
- Qoder and OpenCode pass when their local tools are available, otherwise the
  missing validator is reported as a limitation and not counted as success;
- isolated and live migration evidence show exact one-time archives with no
  unsafe mutation;
- Contract is bound, Plan coverage is 24/24, scope delta is none, baseline is
  not applicable, three verdicts pass/approve, and blocking evidence is zero;
- no unintended file, secret, temporary artifact, scheduler process, or
  unapproved external action remains.

Scope rationale: broad—the shared state protocol, migration, security, phase
skills, optional wake-up, packaging, and four host claims share one release
rollback boundary. This is the single justified aggregate suite after focused
rollback-unit checks.

## Outcome Plan Map

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 1"],
      "evidence": ["test:review-policy-schema", "inspection:review-state"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 3"],
      "evidence": ["test:review-intent-routing", "inspection:ambiguity-blocks"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 2"],
      "evidence": ["test:artifact-bound-gate", "security:bounded-gate-reader"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["test:blocking-gate", "inspection:no-silent-approval"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["test:implementation-mandate", "inspection:lean-compact-only"]
    },
    {
      "outcome": "OUT-006",
      "tasks": ["Task 2", "Task 4"],
      "evidence": ["test:window-boundaries", "test:one-shot-resume"]
    },
    {
      "outcome": "OUT-007",
      "tasks": ["Task 2", "Task 3"],
      "evidence": ["test:unattended-gate", "inspection:unchanged-objective"]
    },
    {
      "outcome": "OUT-008",
      "tasks": ["Task 2"],
      "evidence": ["test:auto-delta-rejection", "inspection:distinct-delta-approval"]
    },
    {
      "outcome": "OUT-009",
      "tasks": ["Task 2", "Task 3", "Task 4"],
      "evidence": ["test:intervention-cancels", "inspection:callback-conversation-check"]
    },
    {
      "outcome": "OUT-010",
      "tasks": ["Task 2"],
      "evidence": ["test:stale-input-rejection", "security:fresh-gate-check"]
    },
    {
      "outcome": "OUT-011",
      "tasks": ["Task 2"],
      "evidence": ["test:mutation-isolation", "test:callback-replay"]
    },
    {
      "outcome": "OUT-012",
      "tasks": ["Task 1", "Task 6"],
      "evidence": ["test:schema4-migration", "migration:pre-schema4-archive"]
    },
    {
      "outcome": "OUT-013",
      "tasks": ["Task 3"],
      "evidence": ["test:stored-review-summary", "inspection:hook-read-only"]
    },
    {
      "outcome": "OUT-014",
      "tasks": ["Task 3", "Task 6"],
      "evidence": ["inspection:codex-one-shot-adapter", "host:codex-validation"]
    },
    {
      "outcome": "OUT-015",
      "tasks": ["Task 4", "Task 6"],
      "evidence": ["test:claude-exact-session", "host:claude-strict-validation"]
    },
    {
      "outcome": "OUT-016",
      "tasks": ["Task 3", "Task 5"],
      "evidence": ["test:opencode-review-summary", "inspection:qoder-manual-resume"]
    },
    {
      "outcome": "OUT-017",
      "tasks": ["Task 1", "Task 3"],
      "evidence": ["test:direct-fast-path", "inspection:no-direct-gate"]
    },
    {
      "outcome": "OUT-018",
      "tasks": ["Task 1", "Task 2", "Task 4"],
      "evidence": ["security:no-daemon-boundary", "inspection:stdlib-only"]
    },
    {
      "outcome": "OUT-019",
      "tasks": ["Task 5"],
      "evidence": ["inspection:protocol-documentation", "inspection:rollback-guide"]
    },
    {
      "outcome": "OUT-020",
      "tasks": ["Task 5", "Task 6"],
      "evidence": ["test:version-parity", "host:eleven-skill-validation"]
    },
    {
      "outcome": "OUT-021",
      "tasks": ["Task 1", "Task 2", "Task 3", "Task 4", "Task 6"],
      "evidence": ["test:review-lease-regressions", "review:adversarial-scenarios"]
    },
    {
      "outcome": "OUT-022",
      "tasks": ["Task 6"],
      "evidence": ["host:cross-host-validation", "build:python-compilation"]
    },
    {
      "outcome": "OUT-023",
      "tasks": ["Task 6"],
      "evidence": ["review:verification-record", "review:dated-evaluation"]
    },
    {
      "outcome": "OUT-024",
      "tasks": ["Task 3", "Task 4", "Task 5", "Task 6"],
      "evidence": ["test:authority-containment", "inspection:no-external-write"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->

## External limitations

- The current Codex task does not expose Scheduled Task management, so live
  same-task callback creation cannot be certified in this run. Static protocol
  behavior and host validation are still testable.
- Authenticated Claude, GPT-5.6, Fable, or Opus model execution is not assumed.
  The fake-host runner test proves argv/control behavior, not model quality.
- Qoder validation is conditional on a locally available validator.
- Publishing and installing `1.3.0-alpha.1` are intentionally outside this
  local implementation workflow.
