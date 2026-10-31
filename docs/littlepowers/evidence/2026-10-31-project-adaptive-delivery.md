# Project-adaptive delivery — implementation verification

Date: 2026-10-31. Scope: the complete approved Compact shape
[project-adaptive delivery](../shapes/2026-10-31-project-adaptive-delivery.md).
No scope delta. This is an uncommitted implementation candidate, not a release,
installation, authenticated four-host certification or model-speed claim.
The package version and installed Codex plugin remain 1.5.1.

## Delivered outcome

- Outcome-sized tasks and evidence-backed whole-user-path preflight are integrated
  into the existing routes. Rollback steps remain internal; no extra planning
  artifact, fixed task quota, mandatory batching or default subagent.
- A stdlib-only, on-demand pure helper selects checks by declared impact,
  environment, current acceptance and intact per-check evidence. It preserves
  mandatory checks, failed attempts, original input snapshots and existing gates.
- Project learning uses candidate → trial → active → retired, with explicit
  conditions, reversible authority, predeclared metrics/invariants, version checks,
  promotion evidence and consistent persisted history. Unknown/negative results
  do not promote; inapplicable or invalid strategies are not silently applied.
- The optional [project profile](../project-delivery.md) demonstrates an actual
  local trial and automatic applicable reuse. No runtime changes were made to
  state/approval/completion gates, hooks, manifests, host settings or model/effort.
- Skill-creator's progressive-disclosure guidance kept phase entrypoints concise;
  the [detailed protocol](../../../references/project-adaptive-delivery.md) loads
  only for meaningful connected work or reusable process evidence.

## Actual project trial (not a simulated success)

The first integrated run had 11 failures and one error, all in hook/adapter
subprocess tests. Its exact log remains [preserved](2026-10-31-delivery-tests.txt).
The main interpreter was usable, but child `python3` selected the macOS system
interpreter blocked by Xcode license acceptance. The
[before](2026-10-31-delivery-python-before.txt) and
[after](2026-10-31-delivery-python-after.txt) probes show the environment distinction.

A candidate proposed a child-interpreter preflight and process-local selection of
an already installed working Python. Before the trial, it fixed the metric
(failed adapter cases: baseline 12, minimum improvement 1) and invariants (same
tests, no product edits, no global environment changes). The same affected
[30 tests passed](2026-10-31-delivery-adapter-trial.txt); the helper promoted the
strategy to active. No assertions were weakened, global settings changed or
licenses accepted. This is evidence for this conditional environment rule,
not a claim of lower long-term project rework or faster model execution.

The [current Codex self-host check](2026-10-31-delivery-current-host-final.json)
re-reads and verifies original evidence, applies the matching active rule,
refuses an environment mismatch, proposes retirement on invalidation, and leaves
the ledger unchanged. The retirement branch was tested without persisting it;
the evidenced active strategy remains in the project profile.

## Review and regression boundaries

Review found and repaired two concrete gaps: a requested check with an incomplete
dependency graph could qualify for reuse with an empty change list; a persisted
trial could be relabeled active without a matching promotion history. Both
reproducers failed before their repairs and pass afterward. Earlier trial-token
drift and unsafe-path CLI error handling were also repaired during focused work.

The runtime helper has no project-file, command, network or ledger side effects.
It consumes explicit bounded observations; the root remains responsible for
reading actual evidence and truthful impact/authority declarations. It cannot
authenticate a wholly forged, internally consistent set of observations or infer
all semantics omitted from a reviewed free-form requirement.

## Scenario coverage

| Scenarios | Evidence |
| --- | --- |
| AD-01–03 | Current three-outcome-group workflow, route/diff inspection, small-work opt-out, whole-path fixture and engineering routing checks |
| AD-04–06 | Selection/receipt tests: consumer closure, partial invalidation, added inputs, incomplete graph, environment and live expiry |
| AD-07–08 | Failed/running/timeout and latest-attempt tests; preserved real failure; mandatory coverage, authority and cost constraints |
| AD-09 | Unit lifecycle/negative/conflict/read-only cases, persisted-history rejection, real candidate/trial/active profile and invalidation probe |
| AD-10 | Bounds, duplicate keys, unsafe paths, pure-input immutability and passive injection-text tests |
| AD-11 | Unchanged-gate integration, four host-neutral protocol environments, full hook/OpenCode regression, unchanged manifest/environment digests |
| AD-12 | Three alternating paired real-check runs, unchanged known defect detection, planning and testing promotion/retirement demonstrations |

Model obedience and new authenticated Claude Code/Qoder/OpenCode implementation
runs were not measured. Native checklist updates were accepted by the exposed
Codex plan tool; no new UI-render certification is claimed.

## Verification and measurement

- Final integrated command: `python3 -m unittest discover -s tests -v`, using
  the explicitly selected local test interpreters and Git/Node tools:
  **346 tests pass, exit 0**, including 37 new regression/structure checks.
  [Full final log](2026-10-31-delivery-tests-final.txt).
- All **11 skills** pass the official skill validator:
  [validator log](2026-10-31-delivery-skills.txt). PyYAML was supplied only in a
  task-specific temporary validator environment, not added as a runtime dependency.
- Diff whitespace checks pass. The 137 explicit pre-check input hashes are
  unchanged. Twelve hidden manifest/adapter/CI files, excluded by the existing
  safe-path grammar, were independently hashed before/after and remained unchanged;
  no relaxation of that grammar or raw-ledger edit was used.
- The final [paired benchmark](2026-10-31-delivery-benchmark-final.json) runs
  three alternating pairs over 6,000 records and the same ten scenarios.
  Executions per pair: **30 → 18**; required coverage and known
  UI/API/historical-data defect detection are identical.
  Total fixture medians: **185.96 ms → 147.30 ms**.
  Cold-check medians: **16.99 ms → 17.86 ms**:
  the new path has overhead on a cold run, so it is not a default for cheap work.
  Preparation, helper, checks, evidence and recovery costs remain separately recorded.
  These measurements do not establish model-token savings or project-wide speed.
- The final benchmark ran separately from the integrated suite. Earlier successful
  intermediate reports remain recoverable under
  `/tmp/littlepowers-delivery-validation.dIYF8s`; the original failed run remains
  in the project. One intermediate run had inconsistent shell/unittest wall timing;
  it is not used for a performance claim.

## Final read-only review

Work-unit compliance: **pass**. Approved-outcome fidelity: **pass**.
Code quality: **approve**. No unresolved blocking findings.

The root coordinator reviewed the full approved outcome, changed instructions,
pure proposal boundary, receipt freshness, learning transitions, regression
evidence and unchanged gate interfaces. Review snapshots matched before/after:
`sha256:5b0be063760e8641a9ede31642beedd1c09eb6d288fd0811620c0cfe1eeeac1d` (HEAD `16e64bf0a610d842be919022b072e6d0005abf95`).
That snapshot covers the candidate and its evidence before this reporting
artifact was added; the record itself is not a verification input.

Evidence-token index: `test:integrated-suite`, `test:delivery-scenarios`,
`test:delivery-selection-and-reuse`, `test:verification-integrity`,
`test:delivery-learning-lifecycle`, `test:delivery-learning-and-recovery`
and `test:delivery-authority-and-portability` refer to the final 346-test log and
the corresponding delivery/gate/integrity/host-protocol test cases.
`test:delivery-paired-evaluation` refers to the final paired benchmark;
`host:current-host-delivery` and `inspection:project-feedback` refer to the
real project trial/profile and current-host probe above.
`inspection:cohesive-plan`, `inspection:whole-outcome-walkthrough` and
`review:complete-outcome` refer to the approved shape, current three-task
workflow, shared protocol and this bounded self-review.

Release-specific external validators/CI, publication and installation were not
requested for this iteration and were not performed. Prior release waivers were
not reused. No new agent or additional model run was started.

## Verification Record

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
        "path": "CHANGELOG.md",
        "sha256": "sha256:bbd2e265e62729625bee032590d58f6407a97415281da30516d371caf23e64ab"
      },
      {
        "path": "CONTRIBUTING.md",
        "sha256": "sha256:8ecd8ba89316d4a59828a98b5a6c0a9f53c3bc704873d25b8556036e5e83724e"
      },
      {
        "path": "LICENSE",
        "sha256": "sha256:1d0609f186444283d9de4067c8c0c1310c7623b2d4256789bacb4ec2aae63d04"
      },
      {
        "path": "README.md",
        "sha256": "sha256:6d66401bebf43970452a7d69d6958308eaa11b9c4a9ad21592c47fd3f6aff8a2"
      },
      {
        "path": "README.zh-CN.md",
        "sha256": "sha256:41583b3b2fe92a0b801fb3a1c769abda416f09fc7aa7761731182037558bb6bd"
      },
      {
        "path": "SECURITY.md",
        "sha256": "sha256:706cc57dbddcd289cb7a8fa98eb17f76a9b50ddfaeaf39757fb92bf34afd0ac5"
      },
      {
        "path": "assets/agents-snippet.md",
        "sha256": "sha256:ae80602466c35432f27fd359aa0749820f41c94142e9187b54b4bdfc1e7a213a"
      },
      {
        "path": "assets/claude-snippet.md",
        "sha256": "sha256:15316c415850eb632913c64e4a6e66ee5f1d4377a3d82d83095b716b03722a3a"
      },
      {
        "path": "docs/capability-matrix.md",
        "sha256": "sha256:e06dca0b9e79246b21acb2157779cde9d8d6afbbaccba59b8bdef6fbaefefbed"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-17-littlepowers.md",
        "sha256": "sha256:e1a63373861995a7a95ad96ec790d8b6bb9853d29013ce52f8887f552718ecab"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-17-v0.3-expert-review.md",
        "sha256": "sha256:8157d770d001ad5336f3a747b62a9ec50d52fa15e6f27e0b7564972342bed510"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-17-v0.4-engineering-discipline.md",
        "sha256": "sha256:8b175b948ed3c81ebc2b0fa94fba49ae9f3672648ae90c4fc22b428aaf57a068"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-18-lightweight-handoff-review-evidence.md",
        "sha256": "sha256:533ab8cde8dadfa6ab50801b448e4daf8b4a6bc513351741f7c764889c6daa03"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-20-multi-host-review-gates.md",
        "sha256": "sha256:9f193848b8493c5b77c8fda2a2bf6e70159324ebcb97f393c047c5a9ee693b33"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-26-outcome-lock.md",
        "sha256": "sha256:60493dd65ac5993fac5a71b35eea7510db35a3fd59a8f64a3365bbb75c40de26"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-26-scope-integrity-lean-route.md",
        "sha256": "sha256:d03b5ffe58932f1309abda5f91a0fad1017f33c4be6cca7557b31c8b5cd4e3cb"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-07-31-review-lease.md",
        "sha256": "sha256:a5483f65cc0a7d367e65591d4a0379df06082ba4c0e55e146f05f51e003165c4"
      },
      {
        "path": "docs/littlepowers/brainstorms/2026-08-01-project-workflow-index.md",
        "sha256": "sha256:9c9f5daea788252afeaeb2bbab5d7ac700e15c73caa50d0326530ae29b77d386"
      },
      {
        "path": "docs/littlepowers/contracts/2026-07-26-outcome-lock.md",
        "sha256": "sha256:568d672683d4634076d7f41ca4bdb7823f4723565e76b013147dc2b61bed6fff"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-17-littlepowers.md",
        "sha256": "sha256:5b2bca30799d6fadbf5392ffd3a590c8d0f8dbac3bd8a363839121aefc276b39"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-17-v0.3-expert-review.md",
        "sha256": "sha256:365272becee8a5c95116b08eb46dc0ecfe5dd3960e43f5a61cdac3051a27eeb2"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-17-v0.4-engineering-discipline.md",
        "sha256": "sha256:4627d359a46eaf11efe9919fd69aa424d5b98e08c59878aafbeaa112e2a801ea"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-18-lightweight-handoff-review-evidence.md",
        "sha256": "sha256:fdc3bef040288680776a79cd67b1a3cec058112470b33c4401ff60c4ef45f13a"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-20-multi-host-review-gates.md",
        "sha256": "sha256:8b502882d00f47e3c035a7b3fd90316beabb817c682eb4e9214d7c9f337999d2"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-26-outcome-lock.md",
        "sha256": "sha256:85543c060989f4d59a79dae50b05293cd7188699bbfe09bcbbe7d0476dfce251"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-26-scope-integrity-lean-route.md",
        "sha256": "sha256:d9ef0c7d58a0d0f1a93ed8cd7527276188abfa0880430de6f052070456a93d6d"
      },
      {
        "path": "docs/littlepowers/designs/2026-07-31-review-lease.md",
        "sha256": "sha256:8ac62bcd19338b4ebd1eb92dea535376d59f931b86e96d24cd71ac634a096ea3"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-17-littlepowers.md",
        "sha256": "sha256:d481cc9955c997512f108a07eab3c90922759ccd641335917019a166512b05cc"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-17-v0.3-expert-review.md",
        "sha256": "sha256:e88edcbdb214b2119c08315325055760e7722b43aa8dd82792f96650816b2976"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-17-v0.4-engineering-discipline.md",
        "sha256": "sha256:01d2e2165791fee6e56ac173f16f868a8e32b138aae8df672c9c7c2d5cb3672c"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-18-lightweight-handoff-review-evidence.md",
        "sha256": "sha256:16962d59263eaa428479be34ab74892bcd3f03aace787594c26af9e884331183"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-20-multi-host-review-gates.md",
        "sha256": "sha256:9ae0cfd98fdefd4693e312e863d372df314260a1f635c33e9b363d53fd8fc059"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-26-outcome-lock.md",
        "sha256": "sha256:a26a7f14957970f11c968bb8a2f219405a1dbf4be015a47948d99f5b1624a283"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-26-scope-integrity-lean-route.md",
        "sha256": "sha256:ab6794259b8a4b21f767e5fe8b7855fe30152cbb4ea47bfbb5867618e76a02ea"
      },
      {
        "path": "docs/littlepowers/plans/2026-07-31-review-lease.md",
        "sha256": "sha256:a7f5adbf03866090576eb2c197710e582247b731ee09d33bc939bf8cc4db44cc"
      },
      {
        "path": "docs/littlepowers/plans/2026-08-01-project-workflow-index.md",
        "sha256": "sha256:8dfd5145410bfad204fa9e6f16639b051be8d3889d43b9754c51619e532f0b83"
      },
      {
        "path": "docs/littlepowers/project-delivery.md",
        "sha256": "sha256:05eb652d69150f80993eca6598288b0c1d5bbd9953d2ab2aeac87c263b3503ed"
      },
      {
        "path": "docs/littlepowers/shapes/2026-07-17-runtime-continuity.md",
        "sha256": "sha256:3026afefb9cf4c98e96fecb9296b5ecf6a52de51b5a51c7f87594cd1cc75502e"
      },
      {
        "path": "docs/littlepowers/shapes/2026-08-10-host-root-affinity.md",
        "sha256": "sha256:f86d05daa5d221f4a56f7044520d51f742d48cf78b3fa270ad9f3f31ff4ca055"
      },
      {
        "path": "docs/littlepowers/shapes/2026-08-21-delegation-gate.md",
        "sha256": "sha256:b720ed686fb570c01cde3ece9b7a761a96cf3d10ed862b5f837a0d099f458bfd"
      },
      {
        "path": "docs/littlepowers/shapes/2026-09-20-current-host-capability-refresh.md",
        "sha256": "sha256:fe03c0de66ff9556eb3cc9f0760ae1d79537681e3b1d9dc81929ac91452fd9cc"
      },
      {
        "path": "docs/littlepowers/shapes/2026-09-20-native-task-mirror.md",
        "sha256": "sha256:39ff88f72648e40adfd51aea2469eb538b2e26a0e730ca5ae13b07331d92700c"
      },
      {
        "path": "docs/littlepowers/shapes/2026-09-30-verification-integrity.md",
        "sha256": "sha256:22d2cc6479a625ebefdc2683073760a1333c6f551cff4ed0ee2484a15d1a048d"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-01-eval-recovery.md",
        "sha256": "sha256:2ab3ebcda86fa0b5ad4d03c00147f5282aa18fcdf54e56d1a399cf2ca0c75cfe"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-17-execution-efficiency.md",
        "sha256": "sha256:cdf12382be23892217eea05d89f2c4bb575954350e39ebc5e7ea911bf23f49da"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-30-acceptance-repair.md",
        "sha256": "sha256:51d613ed55b3faf1a1d3a4acfc6371f571aeafb59235f9b684338b5e8d6c37f2"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-31-project-adaptive-delivery.md",
        "sha256": "sha256:1216d324e83c0293c295d8dc12f55fa55cb679701f29c92ad4bc21d5e8aeade1"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-17-littlepowers.md",
        "sha256": "sha256:52c8a68f8bd5775a059c771d7d1921efddf2aec63ce21e42d30d67759b7ed1c2"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-17-v0.3-expert-review.md",
        "sha256": "sha256:c2d0700315edabd571d814087239f3cf1815bc9df6c5f6ca80bc50376b856eda"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-17-v0.4-engineering-discipline.md",
        "sha256": "sha256:070a8e76d53470ebac0eb2ce30f729f05d9be0e85eb8bdc9af4413667353e709"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-18-lightweight-handoff-review-evidence.md",
        "sha256": "sha256:f3782bf3fffa0a5b12e553c3b90ac5e33d349e7c835bb88195984622c8696b6d"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-20-multi-host-review-gates.md",
        "sha256": "sha256:462240a51450ca921b8113ac36d224bba9dc44b793f64eadfa5b03fc34042146"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-26-outcome-lock.md",
        "sha256": "sha256:63d66b6db819bb4219b608058e189ca32f704282cf17a042652ee17547cd1227"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-26-scope-integrity-lean-route.md",
        "sha256": "sha256:4dc4444a0ef4ca9eb25ba383089059589f3ddc9b63daeaa033a368c6093a558c"
      },
      {
        "path": "docs/littlepowers/specs/2026-07-31-review-lease.md",
        "sha256": "sha256:9b852dfdf0862ea198f28f4ef0f5827f9ef661be9247892c0c5c9c34974aaf1b"
      },
      {
        "path": "docs/model-compatibility.md",
        "sha256": "sha256:5d25b07bea145bc3dd2a26f253a9d697fff893ab197696008d795e802d07b2d5"
      },
      {
        "path": "docs/security-model.md",
        "sha256": "sha256:5fbad7e514a2c7596f56ac61c85e57e6cb392b4aa833deb2553823f7129201e9"
      },
      {
        "path": "evals/README.md",
        "sha256": "sha256:9b1a2a4efa473bacc32dcf23772c6588ccd5fa651cd41b43b6404b5915c14034"
      },
      {
        "path": "evals/delivery_benchmark.py",
        "sha256": "sha256:8c3b3d42d27c80dbb579c66bd20edc18b8cbbc75ab8b95d5d785ea35337cb9dc"
      },
      {
        "path": "evals/delivery_fixture.py",
        "sha256": "sha256:4901ba7d33943e7b616a97cc25b9cad206eb60fc18ef32bc27e8fdf1541b0c60"
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
        "sha256": "sha256:384c2ed27bbb085b1845ec18df662cf948a1dc5072850fa74d4251390e3908b1"
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
        "path": "references/acceptance-and-evidence.md",
        "sha256": "sha256:4eb5dc75546a49bbdb239279376366ae5accdd22b85d3bb0d9dfc9e93813bc8f"
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
        "sha256": "sha256:bd3a208b91c019054d1171de42e9a2fed90ea2bd7249a6d9d2fcff1f8a44cf81"
      },
      {
        "path": "references/project-adaptive-delivery.md",
        "sha256": "sha256:3a58da45f6f35b9bd22ea50a3359d61d7c5052a753815663b9d38f702f446c14"
      },
      {
        "path": "references/review-lease.md",
        "sha256": "sha256:03bda6ac85b86f73012370301b6db8b99c5f49c8ff91e9e8aac3f05349fff78a"
      },
      {
        "path": "scripts/littlepowers_delegation.py",
        "sha256": "sha256:fb99913def66dce0ecd058a69f665f85d86fd038387b143058d6de0f76dd93f1"
      },
      {
        "path": "scripts/littlepowers_delivery.py",
        "sha256": "sha256:7a653b96519fbcca7ac8dcddd1752cd1ec8fbdeea18bbad6f449724abae1e57e"
      },
      {
        "path": "scripts/littlepowers_efficiency.py",
        "sha256": "sha256:a6844551df9462cec4118df907c58e0aff7eeb74215f0daf33629121f9698b05"
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
        "sha256": "sha256:ee2b0c39a0287b9fae723172bbd1685b82851520f19374f6b592eea356a81db6"
      },
      {
        "path": "skills/brainstorming/SKILL.md",
        "sha256": "sha256:ceac06914750684705eead8910719facf5accb4107874e1d4dd17d1cf34e753c"
      },
      {
        "path": "skills/brainstorming/agents/openai.yaml",
        "sha256": "sha256:22ca8eab3de455e10fee824015ce8ead3f6b82089f9ca466689ba6600cb4161d"
      },
      {
        "path": "skills/compact-shaping/SKILL.md",
        "sha256": "sha256:79469de60cdd53abf5eed6bb042b137718b1c4de7d542dec1f08ece7aeb2189e"
      },
      {
        "path": "skills/compact-shaping/agents/openai.yaml",
        "sha256": "sha256:99a73e55a2c89ab0c4a7e0e57dfcb8d75c840f8be4704dc093f507295223333f"
      },
      {
        "path": "skills/debugging-systematically/SKILL.md",
        "sha256": "sha256:6c323c14e60c25cb9eff16cc7c9ad5ecb1bdad034aa6c3741a729679382af389"
      },
      {
        "path": "skills/debugging-systematically/agents/openai.yaml",
        "sha256": "sha256:c531292b9c30c477cf63032952518c32d74bd925403735b9f35a4eda128ac953"
      },
      {
        "path": "skills/designing-solutions/SKILL.md",
        "sha256": "sha256:6ce38ed9ab51fce24a7ca7cef23adb0c3a4a19bfa6255da3568ecc0b4bc3a3b3"
      },
      {
        "path": "skills/designing-solutions/agents/openai.yaml",
        "sha256": "sha256:9e29a873ab70310801e6928df370b0ed2cdc4c6dbf57ad020d60b88cca95867b"
      },
      {
        "path": "skills/executing-plans/SKILL.md",
        "sha256": "sha256:2b2026459c689b238f9c9e773b6f5079a2a8eccc5e9bce3ff80f1bad2d3e23d1"
      },
      {
        "path": "skills/executing-plans/agents/openai.yaml",
        "sha256": "sha256:9bd12df3e984e41f9fe6dec9e226416f74cf31522faf0e3fd494e57ae22687ac"
      },
      {
        "path": "skills/managing-littlepowers/SKILL.md",
        "sha256": "sha256:786e13f09c49f18aa7a855903e32aa4c2bda0ba6a6e8824a05c600d556cd4b7e"
      },
      {
        "path": "skills/managing-littlepowers/agents/openai.yaml",
        "sha256": "sha256:ba4276dba258d3000ea6695f3e23c50e5229a867727bc3c94f8a2229a3799075"
      },
      {
        "path": "skills/reviewing-changes/SKILL.md",
        "sha256": "sha256:631762316910783f3f07034ba6b168039d9b3f9df2910f6afe012f5f26da866c"
      },
      {
        "path": "skills/reviewing-changes/agents/openai.yaml",
        "sha256": "sha256:c9a13669271db891f404a728f77a013808cc0d33b7642650db318e19607d839a"
      },
      {
        "path": "skills/using-littlepowers/SKILL.md",
        "sha256": "sha256:261acd0e758d4cb5706a70eb382b3440b58ab7b9c8e8e6f5e68fc1ce3f4c0ba8"
      },
      {
        "path": "skills/using-littlepowers/agents/openai.yaml",
        "sha256": "sha256:75aad3515f1433e02a1aec0fabba4b2cdf4e7e0e1f6eec29020e6d9ea2a93049"
      },
      {
        "path": "skills/verifying-work/SKILL.md",
        "sha256": "sha256:f38ef638a92a1d98fc54408ae338f0b44daa031ba6a16edcad8a7177e94869a6"
      },
      {
        "path": "skills/verifying-work/agents/openai.yaml",
        "sha256": "sha256:b9fab12845eb23a82f3baf0425b7a289727c3ef8b4529360039d0f0aea892988"
      },
      {
        "path": "skills/writing-plans/SKILL.md",
        "sha256": "sha256:dc1200753845214277b39a543c54491f211694c9e88471151189cba425dd9afb"
      },
      {
        "path": "skills/writing-plans/agents/openai.yaml",
        "sha256": "sha256:50d2cfb130e3fcf4062f5eb46c435732d53953a8039be29dc2dbea469d186019"
      },
      {
        "path": "skills/writing-specs/SKILL.md",
        "sha256": "sha256:fb19006879f8120a5172063929aab622bd77549cf1bd8aa9904d3676207f1e2b"
      },
      {
        "path": "skills/writing-specs/agents/openai.yaml",
        "sha256": "sha256:de7d896dc1243cee5bfac5ffe53e9a8e004a841105e8c826b8e4de1d5580a397"
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
        "path": "tests/test_delivery.py",
        "sha256": "sha256:8d35c61517bf631064d476190fc84002f59adf578c6df66e7dd54b3ab42cf84e"
      },
      {
        "path": "tests/test_delivery_eval.py",
        "sha256": "sha256:9470ed31319cf3bec942283f9afd8096bfe42ffea6db7e94ced78734715fff2c"
      },
      {
        "path": "tests/test_delivery_integration.py",
        "sha256": "sha256:15ef16e4f57ebb2bae7ab8a220e6d858bed6ef080e80bd7a38ee6b4690dd22a8"
      },
      {
        "path": "tests/test_efficiency.py",
        "sha256": "sha256:f1f92925ee7e6a559b468200c24474fb7713bc0420832f945eb14f6fb22ec451"
      },
      {
        "path": "tests/test_efficiency_host.py",
        "sha256": "sha256:7bfb274a52665e85ef25562b38b5152f097c2bf60151c57f80b753e510898b4d"
      },
      {
        "path": "tests/test_engineering_disciplines.py",
        "sha256": "sha256:345193d6e1e0edc22be07e8bdcb149792739f4948a697c2d3b711804fe8e8188"
      },
      {
        "path": "tests/test_hook.py",
        "sha256": "sha256:4aebf07ab7d72fdff5a57344d9ba23494325860f64b362cc4db58c3af90d2f82"
      },
      {
        "path": "tests/test_manifests.py",
        "sha256": "sha256:37351a86194dad45852b3034b09cac777208f427e20a8d1ecb7cba4f341956bf"
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
        "sha256": "sha256:eb582c4867087dbeca6a9a87ed9d3dc4bfc8ee93695a1b18dd80e14823a97a27"
      },
      {
        "path": "tests/test_outcome_gates.py",
        "sha256": "sha256:c6cf4a0224e9420b319567a70a9939aee59eac0bb898f37a87ebe6ec16d9f2fd"
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
    "status": "pass",
    "evidence": [
      "test:integrated-suite",
      "test:delivery-scenarios"
    ]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": [
      "review:complete-outcome",
      "host:current-host-delivery",
      "inspection:project-feedback"
    ]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": [
      "review:complete-outcome"
    ]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": [
        "inspection:cohesive-plan",
        "test:delivery-scenarios"
      ]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": [
        "inspection:whole-outcome-walkthrough",
        "test:delivery-scenarios"
      ]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": [
        "test:delivery-selection-and-reuse",
        "test:verification-integrity"
      ]
    },
    {
      "outcome": "OUT-004",
      "status": "pass",
      "evidence": [
        "test:delivery-learning-lifecycle",
        "test:delivery-learning-and-recovery",
        "inspection:project-feedback"
      ]
    },
    {
      "outcome": "OUT-005",
      "status": "pass",
      "evidence": [
        "test:delivery-authority-and-portability",
        "test:integrated-suite"
      ]
    },
    {
      "outcome": "OUT-006",
      "status": "pass",
      "evidence": [
        "test:delivery-paired-evaluation",
        "host:current-host-delivery",
        "review:complete-outcome"
      ]
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:verification -->
