# Execution efficiency: local candidate evidence — 2026-10-17

Status: local implementation and synthetic verification available; **independent
review pending / overall acceptance blocked**. Do not report the feature fully
accepted, certified on all hosts, or released. Baseline commit:
`6f3d897098674cbd6d40dbe87e1d79475900659f`. One local candidate commit is intended;
no push, Actions, PR, release, user Mac access or Termarium changes.

## Implementation and authority

The complete public attachment (353 lines, 12,069 bytes) was read from Library
`libfile_bc51fc8068688191a6e7a8adbf69973f`. Existing AGENTS and phase/reference
instructions were inspected before implementation. The approved fixed-outcome
Compact route used implementation_mandate, fresh eligible Review Lease resolution,
Contract bind and Plan Map validation. No fabricated explicit user approval.
The existing root ledger stays at verify; no second authority was created.

- `scripts/littlepowers_efficiency.py`: pure standard-library structured report,
  semantic diff, pending-event cursor, acknowledgment and error/batch proposals.
- `references/execution-efficiency.md`: exact adapter/schema/evidence/authority
  contract and honest host fallbacks. Four existing skills route on demand.
- `evals/efficiency_host_fixture.py`: explicit synthetic host fixture for real
  cooperative timeout/cancellation, handle reuse, independent read exits and
  root-owned atomic persistence. Not installed as a host adapter or monitor.
- `evals/efficiency_benchmark.py`: explicit reproducible local A/B experiment.
- Main brainstorm/spec/design/plan artifacts carry matching amendments; package,
  ledger schema, Outcome Lock, Review Lease, hooks and installed adapters unchanged.

## EFF acceptance map

| Criterion | Evidence and observed result | Boundary |
| --- | --- | --- |
| EFF-01 | Saved synthetic original compared to check IDs, coverage and all critical findings; hash-verified references | Local tests pass; adapter extraction remains domain-owned |
| EFF-02 | Tiny budget retains critical finding and synthetic PNG reference, explicit artifact/check/finding supplemental reads; unsaved/truncated evidence cannot PASS | Local tests pass; no real visual product acceptance claimed |
| EFF-03 | Reordering and sample clock ignored, unchanged action continues with no event/sequence advance | Helper has no filesystem or ledger imports; host must retain candidates locally |
| EFF-04 | Version, entity add/delete, optional-field deletion and same-name enabled-state swap return changes | Local semantic tests pass |
| EFF-05 | Missing/null/duplicate fields, stale/unknown source, critical errors and user action return; recovery returns same prior state | Local tests pass, including unknown source time and changed schema |
| EFF-06 | Integrity, exact task/environment/observer/contract scope, age, evidence digest, missing events and huge sequence rejected | Local tests pass; checksum is not authentication |
| EFF-07 | Actual atomic save/read interrupted before report retains pending event and uncertain delivery; explicit ack clears it; failed replacement retains old file | Local tests pass; at-least-once read-only reporting, not exactly-once |
| EFF-08 | 5-second synthetic coroutine ends at 30-ms observation/batch/report boundary, cancellation cleans up; periodic reports and sampling waits bounded | Real asyncio fixture, tests allow 0.5-s scheduling tolerance; uncooperative tools/real browsers not certified |
| EFF-09 | Structured code takes precedence, deterministic fixes require change, host retries surfaced, business wait separated, all automatic retry false | Policy tests pass; helper never executes repair/retry |
| EFF-10 | Missing capability produces degraded result with zero tool calls; actual exposed exec handle created/reused once | Actual cancel sent, later exit 1 lacks causal proof; cancellation capability unverified, no batching certification |
| EFF-11 | Cross-task cursor restore rejects, existing gate/state suite passes, single writer and isolated scope documented | No state/gate implementation changed; root-only persistence is host responsibility |
| EFF-12 | No network/browser/agent/filesystem dependencies in core, no hook imports, no automatic invocation on simple work | Existing hook/no-state tests pass; no daemon or session scanning |

## Fresh validation

- `python3 -m unittest discover -s tests -v`: **298 tests, 12.928 s, exit 0**.
  Full output: `2026-10-17-efficiency-tests.txt`.
- `python3 -m unittest discover -s tests -p 'test_efficiency*.py' -v`:
  **34 tests, 0.313 s, exit 0**, after the final documentation clarification.
  Output: `2026-10-17-efficiency-focused.txt`.
- `python3 -m compileall -q scripts hooks tests evals`, Node syntax for
  `.opencode/plugins/littlepowers.js`, Bash syntax for `hooks/run-hook.cmd`,
  and `git diff --check`: exit 0.
- Official openai/skills `quick_validate.py`: all **11 skill directories pass**.
  Fetched from `https://raw.githubusercontent.com/openai/skills/master/skills/.system/skill-creator/scripts/quick_validate.py`;
  SHA-256 `6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51`.
- Claude strict marketplace (`plugin validate --strict .`) and explicit
  `.claude-plugin/plugin.json` validation: both pass. This checks manifests only.
- `littlepowers_state.py doctor`: trusted state directory/ignore/lock, schema 4;
  no project index or scanner created.
- Official standalone Codex plugin validator: **unavailable/unrun**. Current
  `codex plugin --help` exposes no validate command; bounded public repository
  tree lookups in openai/plugins and openai/codex did not locate that validator.
  This release check is not replaced by a homemade validator.

Explicit 64-file implementation/test/skill/reference input hashes were captured
before checks. Final documentation clarified that host-local cursor JSON is not
model-facing text; input hashes were refreshed and focused checks rerun afterward.
The staged diff check also caught one extra EOF blank line in the shape. Its
whitespace-only repair went through fresh eligible Review Lease resolution,
Contract bind and Plan Map validation; inputs and focused tests were refreshed.
No implementation changed after the full suite. Existing hidden manifests/adapters
were unchanged; no new freshness coverage for those paths is claimed.

## Reproducible cost comparison

Command:
`python3 evals/efficiency_benchmark.py --output docs/littlepowers/evidence/2026-10-17-efficiency-benchmark.json`

Three paired runs, alternating order, 40 synthetic observations per arm, two
checks per observation (80 checked), zero business wait in both arms, identical
raw evidence saved. Semantic versions change every ten samples. No real project,
people, private paths, sessions, model calls or network data in this workload.
Host fixture emits events only; local candidate cursor JSON is excluded from
model-facing text in BOTH the described protocol and this measurement. Directly
printing whole CLI JSON is a different workload and is not covered by the saving.

| Arm/run | New text chars | Total wall s | Setup s | Tool s | Helper s | Save s | Recovery s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full 1 | 807710 | 0.009621 | 0.000152 | 0.000085 | 0.000000 | 0.006497 | 0.000000 |
| full 2 | 807710 | 0.009387 | 0.000032 | 0.000104 | 0.000000 | 0.006444 | 0.000000 |
| full 3 | 807710 | 0.009216 | 0.000029 | 0.000079 | 0.000000 | 0.006371 | 0.000000 |
| summary 1 | 3759 | 0.027293 | 0.000032 | 0.000094 | 0.018690 | 0.007715 | 0.000533 |
| summary 2 | 3759 | 0.026433 | 0.000030 | 0.000089 | 0.018009 | 0.007589 | 0.000496 |
| summary 3 | 3759 | 0.027454 | 0.000026 | 0.000093 | 0.018736 | 0.007862 | 0.000514 |

Each full arm emitted 807,710 characters; each summary arm emitted 3,759
(99.53% fewer in this synthetic workload). Full per-observation distribution:
min 20,192 / median 20,193 / p95 20,193 / max 20,193. Summary: min 0 /
median 0 / p95 945 / max 945. The JSON retains every observation value.
Tools remain **40 calls per arm**, not fewer. Helper/validation cost increases
local wall time; this experiment demonstrates text reduction, **not overall
speedup**. The measured recovery includes atomic cursor reload and evidence
verification once per summary arm. Runtime correction count and correction cost
are 0 in these successful benchmark runs; implementation/debugging costs outside
the executable are unmeasured, not included or claimed as zero whole-task cost.
Total wall includes setup, loop and recovery, excludes temporary-directory
cleanup; component times are not added as if overlapping costs were wall time.

Images: 0 in this text workload; synthetic PNG retention is tested separately.
Tokens, actual host model request count, context usage and compression events:
**unknown/null**, because no host model logs were available. No fixed character
conversion, cumulative-input proxy or long-task compression improvement claim.
Full task development/repair/model cost is unmeasured. All performance conclusions
are limited to these samples. Raw timing/distribution data is in the JSON.

## Review and remaining blockers

Coordinator self-review repaired: stale WAIT incorrectly retaining a waiting
result; cursor sequence validation risking an enormous range allocation;
incomplete event summary restoration; required semantic schema drift; future
collection timestamps; explicit unknown source timestamps; and unnecessary
repetition of supplemental-read identifiers. Adversarial tests cover these.
Self-review is **not independent code review**.

Independent review action: launch a read-only leaf reviewer of this exact local
candidate. Status: **not attempted / capability blocked**, not denied by an
approval reviewer. Current collaboration schema has no tool-restricted read-only
or enforced leaf-depth control. The loaded
`skills/executing-plans/SKILL.md` requires the complete Delegation Gate;
`references/delegation.md` states: “If enforcement is unavailable, report the
limitation and continue single-agent; do not silently downgrade this gate to a
prompt rule.” No nested CLI or prompt-only substitute was launched. An upstream
independent reviewer can inspect the local commit; until then code-quality and
overall acceptance remain blocked. No approval was invented. The parent is
requesting an exception for independent-context, read-only-convention review with
before/after hashes; no reply has been received and no exception is assumed.

Real Codex/Claude/Qoder/OpenCode browser or installed-plugin flows, macOS/Windows,
non-cooperative tool cancellation, long-running compression and official Codex
plugin validation remain unverified. Actual current-host probe details are in
`2026-10-17-efficiency-host-probe.json`; handle reuse is observed, cancellation
semantics are not established. These limitations are neither scope removal nor
claims of full-host acceptance. The existing ledger remains active at verify. OUT-004 is explicitly blocked for
the unverified real-host cancellation boundary: fixture EFF-08/EFF-10 success is
not promoted to a real-host pass. All twelve EFF criteria remain in scope.

<!-- littlepowers:verification:v1 -->
```json
{
  "inputs": {
    "files": [
      {
        "path": "AGENTS.md",
        "sha256": "sha256:6242e161fe9318a30d6b658b4b4d202a30b0696a160fb2952a98214ddd32df6d"
      },
      {
        "path": "README.md",
        "sha256": "sha256:4576f5d800978396c3a9c83983e33aff10720dae9cec5580733c994f7d052f09"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-17-execution-efficiency.md",
        "sha256": "sha256:cdf12382be23892217eea05d89f2c4bb575954350e39ebc5e7ea911bf23f49da"
      },
      {
        "path": "evals/README.md",
        "sha256": "sha256:24b5d1af6cc6cba42f6b7bc7e879b97f5dcca01c3627b90a44f5b4c45750d17b"
      },
      {
        "path": "evals/efficiency_benchmark.py",
        "sha256": "sha256:ba02efa15e51345170b9022eff5b21cbc4c4393cf43aeda7a5efa2978de5c301"
      },
      {
        "path": "evals/efficiency_host_fixture.py",
        "sha256": "sha256:fe4ae189a3a776269274de0d718ce7b61e82003137b0744ffa843dc31ba5866d"
      },
      {
        "path": "evals/results/2026-07-17-runtime-continuity.md",
        "sha256": "sha256:d8dfc903655bfea24fe9ae87d2f9f20658d211da40257e7900ca2ee35b2074a6"
      },
      {
        "path": "evals/results/2026-07-17-v0.3-alpha.1.md",
        "sha256": "sha256:4b3863d22d8f4b38f70c5019b307d43cf360c974999b79f195c1d07db67f758e"
      },
      {
        "path": "evals/results/2026-07-17-v0.4-alpha.1.md",
        "sha256": "sha256:ed89f9a71860c48330072997cad19426dc6cf986b97fdf6b561de3b5df630ebb"
      },
      {
        "path": "evals/results/2026-07-18-lightweight-handoff-review-evidence.md",
        "sha256": "sha256:5494f69db10fa31134d4f6e2575440b6d1e7ad4b66dddf9f853c643372165b95"
      },
      {
        "path": "evals/results/2026-07-26-v1.1-scope-integrity.md",
        "sha256": "sha256:774c5d51bf32ee0dc51e6184aae067bd7035e31b7ac3ff0967157321103c4195"
      },
      {
        "path": "evals/results/2026-07-26-v1.2-outcome-lock.md",
        "sha256": "sha256:75e8fb257a9dfd07bbc6ea2675bd27364cb6430ec038dce849c03a7dfb577d68"
      },
      {
        "path": "evals/results/2026-07-31-v1.3-review-lease.md",
        "sha256": "sha256:9f194ea8567ef7f217243a07e55ca032fc9d9aefa61efcfce727a8cb278fd04b"
      },
      {
        "path": "evals/results/2026-08-01-v1.3.0-release.md",
        "sha256": "sha256:e9de81e213f9fc83e6141e39e45d0b2b14defae8b1972ccb622b5e73c03528bc"
      },
      {
        "path": "evals/results/2026-08-10-v1.3.1-release.md",
        "sha256": "sha256:1d1ce9a0b8db949304670798d6c63323de0d9be5d3282baf25901931d5e9b295"
      },
      {
        "path": "evals/results/2026-08-21-v1.4.0-alpha.1.md",
        "sha256": "sha256:db70deb6eadd2d946c6860854b951cfd8ce79300ac9dbc99f117d0f74466fb60"
      },
      {
        "path": "evals/results/2026-09-20-v1.4.0-codex-live.md",
        "sha256": "sha256:9a32fca355ccf735c0761fe1bae2d1e68ce5e1484bdb42ccc3004460d51c6fd6"
      },
      {
        "path": "evals/run_codex_live.py",
        "sha256": "sha256:586f3deecef07e42abe1c39f910f24f7cbece9fbfce9a5857a189969a7f0cb28"
      },
      {
        "path": "evals/scenarios.md",
        "sha256": "sha256:a7d29bdf53b4cedb3a3c553ead252aca8ef056453b081135f5110fb807fdd7a8"
      },
      {
        "path": "hooks/hooks.json",
        "sha256": "sha256:a9deb55751b145a2db22b4becfba65b62bad1d3850b4c903957695383db08466"
      },
      {
        "path": "hooks/run-hook.cmd",
        "sha256": "sha256:4a41085eb3682f11a5aae537701ec246ddb9225af95bfd7b46e6c8330f6e5052"
      },
      {
        "path": "hooks/session-start.py",
        "sha256": "sha256:55caf7be6a8635a1e8b538ffe9f542215c3f257002c48944d8a284c9cf1e30a9"
      },
      {
        "path": "package.json",
        "sha256": "sha256:2dd49fd2a30473c027d8615b04a61bcf906068d6ae0db615e6085ce406a614f8"
      },
      {
        "path": "references/delegation.md",
        "sha256": "sha256:eac34ff0e9cece627d5febc1b7ebf2f90abd3d5c47c2b0d0674406b1228e86bf"
      },
      {
        "path": "references/execution-efficiency.md",
        "sha256": "sha256:26eda1ae02f753833e0416e87cb5a2978dca12e00b4bdcc342e7537dad1bc201"
      },
      {
        "path": "references/native-task-mirror.md",
        "sha256": "sha256:07abb2b3bd848ca51f9649784996b7d9ac9eb8745463eb80bcbd10b4ee8b0efe"
      },
      {
        "path": "references/outcome-lock.md",
        "sha256": "sha256:0b56a88eee25fab45f9b07bb119dfa7d082ae129a6380ddc236a74694ffe6fda"
      },
      {
        "path": "references/review-lease.md",
        "sha256": "sha256:b1b575c0527010dee3f1ceb3d609d21e5fa4cca4666a0564e211e3791fa01399"
      },
      {
        "path": "scripts/littlepowers_delegation.py",
        "sha256": "sha256:fb99913def66dce0ecd058a69f665f85d86fd038387b143058d6de0f76dd93f1"
      },
      {
        "path": "scripts/littlepowers_efficiency.py",
        "sha256": "sha256:5e726af5ff97ebc01e35428eb5311c567df3ef5ca6485f9f4935749cfc3f10b4"
      },
      {
        "path": "scripts/littlepowers_mirror.py",
        "sha256": "sha256:0dfa0251754369a138b1d66729c7e2181d06f95a9351a115f0fe5fc45163d58e"
      },
      {
        "path": "scripts/littlepowers_review_runner.py",
        "sha256": "sha256:67d394bd04edfe9a877d987a65695d3bc8cfb8327a91ffbd3fe8170dbd063249"
      },
      {
        "path": "scripts/littlepowers_state.py",
        "sha256": "sha256:0fe848c6ad734a258b5a6c8fe22bc32ccff4465efcf9d1fe67e81bd7a6bb0c06"
      },
      {
        "path": "skills/brainstorming/SKILL.md",
        "sha256": "sha256:9eb323805846612eeb37bdc622045cd39d9d5e4aac4d1fae23d21948acc85a5f"
      },
      {
        "path": "skills/compact-shaping/SKILL.md",
        "sha256": "sha256:90f5b70edeedd5d2340e6170188e439c400e44fc8dd98d2096fbbd848c051ea4"
      },
      {
        "path": "skills/debugging-systematically/SKILL.md",
        "sha256": "sha256:6c323c14e60c25cb9eff16cc7c9ad5ecb1bdad034aa6c3741a729679382af389"
      },
      {
        "path": "skills/designing-solutions/SKILL.md",
        "sha256": "sha256:1cc4ff09e3a9699da7a26fb4dea89709e557c52971006c1876fd219bcaa50079"
      },
      {
        "path": "skills/executing-plans/SKILL.md",
        "sha256": "sha256:7638c65d606980801df282ade84b232ee6cea6beedd5f874ac1932633f671fcc"
      },
      {
        "path": "skills/managing-littlepowers/SKILL.md",
        "sha256": "sha256:786e13f09c49f18aa7a855903e32aa4c2bda0ba6a6e8824a05c600d556cd4b7e"
      },
      {
        "path": "skills/reviewing-changes/SKILL.md",
        "sha256": "sha256:49d092600f2865a9fd3a5e6f95d16a4a0b46459eb0cf61f2db928079cadc3e1a"
      },
      {
        "path": "skills/using-littlepowers/SKILL.md",
        "sha256": "sha256:f711d0ea361a9361459e650295d3773e60aa3175b5c9c4726f7d9a4da2ddfc4c"
      },
      {
        "path": "skills/verifying-work/SKILL.md",
        "sha256": "sha256:e93218e17c1062181e6871548615d0784b3020f12a64f346e48b97dbcead8869"
      },
      {
        "path": "skills/writing-plans/SKILL.md",
        "sha256": "sha256:9d024af2a0d5b5a0fcb0c878819ba265dde4a5677f29e3530af43eff33b90bf6"
      },
      {
        "path": "skills/writing-specs/SKILL.md",
        "sha256": "sha256:fb19006879f8120a5172063929aab622bd77549cf1bd8aa9904d3676207f1e2b"
      },
      {
        "path": "tests/test_codex_live_eval.py",
        "sha256": "sha256:682b9cdb6fb3bb1a464b8abb071a36fe654a2c9c1690e56aa8e911f8fb6fc6b9"
      },
      {
        "path": "tests/test_delegation.py",
        "sha256": "sha256:d9d9cafcf045e895848c2ec789f43a70d5b83e669744682b7e0a6321b43e9547"
      },
      {
        "path": "tests/test_efficiency.py",
        "sha256": "sha256:c5054a0e6f2f98eb064fb81a1b1701dc36ccdd0cc6537f62433901df6cd25104"
      },
      {
        "path": "tests/test_efficiency_host.py",
        "sha256": "sha256:7bfb274a52665e85ef25562b38b5152f097c2bf60151c57f80b753e510898b4d"
      },
      {
        "path": "tests/test_engineering_disciplines.py",
        "sha256": "sha256:d322b6fa727381b136e15efe8a403a93d7c1515d695f98b67ba3af58cfdeb4fd"
      },
      {
        "path": "tests/test_hook.py",
        "sha256": "sha256:4aebf07ab7d72fdff5a57344d9ba23494325860f64b362cc4db58c3af90d2f82"
      },
      {
        "path": "tests/test_manifests.py",
        "sha256": "sha256:1770293e5552affe9a5d73cd2c122930f5861b9dafdd786f0ccebd116e31a378"
      },
      {
        "path": "tests/test_native_mirror.py",
        "sha256": "sha256:7bc1963b69df3f7f6b20cad0c9b1fb9d42e213dc762135f4878b850f3e369229"
      },
      {
        "path": "tests/test_opencode_plugin.py",
        "sha256": "sha256:4d8773c5032f5db3d5a3c1f3fbec83bcf09c1fc9052c3c03045ca395c179236c"
      },
      {
        "path": "tests/test_outcome_contract.py",
        "sha256": "sha256:fb5068e5048e8b96188a95b82e9ed9f4aeb69f74ef1bd0662e882c8b41262aa5"
      },
      {
        "path": "tests/test_outcome_gates.py",
        "sha256": "sha256:a6ac237dadd9099bfb29367a2df263b957b49b0dc2f24fdeb9194e183fa42522"
      },
      {
        "path": "tests/test_outcome_migration.py",
        "sha256": "sha256:f8bb2b82917c1fc42a986b933c5ed96f983a27f8e4de99dc8e5972c458d4f56d"
      },
      {
        "path": "tests/test_outcome_records.py",
        "sha256": "sha256:4f018c8fecac2a4f0863350ae9a4aa575b81359528c5c031ab366dc5e7a0c5ad"
      },
      {
        "path": "tests/test_outcome_self_host.py",
        "sha256": "sha256:7b08e8be4f1441d86a73f97073d6a4d70e0965c102dc3fceaeac08565718c8cf"
      },
      {
        "path": "tests/test_project_index.py",
        "sha256": "sha256:08462004c09def71cff9efd27e40d5a75bbd4126a0904ace08dfd1d3304b55f9"
      },
      {
        "path": "tests/test_review_commands.py",
        "sha256": "sha256:d165d208ab32f88e242a2298b7cdff7b4ab5a76a378d30d2082526fa86319cd8"
      },
      {
        "path": "tests/test_review_runner.py",
        "sha256": "sha256:c56a01ba3d304c2b4bf5323de757e9ec804f0fae45c4d286e770b76b3bcbc283"
      },
      {
        "path": "tests/test_review_state.py",
        "sha256": "sha256:40ef1bfdb658232c7c0545448845343f4ddd4d3e3e7fd8b03f49ca77dcd6068d"
      },
      {
        "path": "tests/test_state.py",
        "sha256": "sha256:c83b4b1658dabe7f4f81c1601405a23477f3a22fb4a7ea6571ea4c7064a25553"
      },
      {
        "path": "tests/test_verification_integrity.py",
        "sha256": "sha256:50cf4ad442751c6f4461b499e72f794a3f77af1c0854a7c53b0124cdbbef9466"
      }
    ],
    "manual_reason": null,
    "mode": "files"
  },
  "work_unit": {
    "status": "blocked",
    "evidence": [
      "test:efficiency-local-suite"
    ]
  },
  "outcome_fidelity": {
    "status": "blocked",
    "evidence": [
      "inspection:attachment-eff-traceability"
    ]
  },
  "code_quality": {
    "required": true,
    "status": "blocked",
    "evidence": [
      "review:independent-boundary-unavailable"
    ]
  },
  "blocking_evidence": [
    "review:independent-boundary-unavailable",
    "host:cancellation-unverified"
  ],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": [
        "test:efficiency-1"
      ]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": [
        "test:efficiency-2"
      ]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": [
        "test:efficiency-3"
      ]
    },
    {
      "outcome": "OUT-004",
      "status": "blocked",
      "evidence": [
        "test:efficiency-4",
        "host:cancellation-unverified"
      ]
    },
    {
      "outcome": "OUT-005",
      "status": "pass",
      "evidence": [
        "test:efficiency-5"
      ]
    },
    {
      "outcome": "OUT-006",
      "status": "blocked",
      "evidence": [
        "test:efficiency-6"
      ]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
