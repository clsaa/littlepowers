# Littlepowers 1.4.3 candidate evidence — 2026-10-01

Baseline: `6aefb3687b70697df9503e5f9b396b1d071ab99d`; isolated branch
`dev/v1.4.3-eval-recovery`. Candidate only: no commit, push, merge, tag or Release.
The original checkout and verified v1.4.2 source runtime remain separate.

## Reproduction and repairs

Two eval regressions failed against baseline: arbitrary observable payloads were
persisted/printed, and failed-host stderr was printed. Synthetic canaries cover
command, MCP, collaboration, file-change, task, message, error and thread fields.
Two OpenCode regressions failed: assistant/tool traffic retriggered empty hooks,
and reconstructed same-ID messages lost context. Baseline logs are in the
review bundle. Initial aggregate found one candidate README version-marker typo;
it was repaired before the final aggregate.

Independent review found retained coordinator context after late child discovery,
and a pending-transform variant that could inject a later coordinator reminder.
Both were repaired using identifiable synthetic blocks and generation guards,
with retained/deep-clone and concurrent lifecycle tests. Timeout diagnostics now
retain stderr only in explicitly opted-in sensitive output. Default output
remains free of synthetic payload canaries.

## Fresh checks

- `python3 -B -m unittest discover -s tests -v`: exit 0, 264 tests in 11.654s.
- Eight offline eval tests and twelve OpenCode fixture tests are included.
- Official `openai/skills` quick validator: all 11 skills passed; source blob
  identity is saved in the bundle. No candidate skill text changed.
- Claude Code 2.1.278 `plugin validate --strict .` and explicit
  `.claude-plugin/plugin.json`: both passed. This is manifest validation.
- Python compilation (`scripts hooks tests evals`), JavaScript syntax,
  Bash launcher syntax and `git diff --check`: passed.
- Explicit pre-check input capture matched afterward. Hidden adapter/manifest/CI
  paths cannot be represented by the stable verifier and are separately hashed
  before/after; this is supplemental evidence, not expanded runtime enforcement.

## Independent review

Final work-unit compliance: pass. Approved-outcome fidelity: pass. Code quality:
approve. No actionable findings remain. Reviewed candidate snapshot:
`sha256:5666dd94b2a6ba2f50a04c1541fcaa80e0b30eee255160b21f09443d0180fe28`.
Review used the user-requested native independent agent with an explicit read-only
task envelope; separate OS-enforced read-only/leaf controls were not exposed,
and no delegation capability-validator certification is claimed. Reviewer made
no file or ledger edits; the coordinator alone writes and completes the ledger.

## Limits and publication gate

The official standalone Codex `validate_plugin.py` was absent from this executor
and not found in the queried official source trees. That release check remains
unrun. Current-candidate macOS/Windows CI cannot be claimed without an authorized
remote publication workflow. Prior v1.4.2 CI is not evidence for this patch.
No paid model evaluation, native plugin installation, automatic Hook delivery,
positive real-host UI execution or live OpenCode certification was performed.
Fixtures establish adapter logic only. The normal host session history remains
host-owned. Protocol 1.3/schema 4 are unchanged. Sensitive opt-in output is
unredacted; default metadata minimization is not universal secret detection.

The candidate satisfies the bounded local implementation/review request; these
remaining release checks and final publication approval are separate gates.
The workflow used verified stable source skills/CLI under explicit user approval,
not a native plugin installation. Install examples remain on published v1.4.2.

<!-- littlepowers:verification:v1 -->
```json
{
  "work_unit": {
    "status": "pass",
    "evidence": [
      "test:264-unit-tests"
    ]
  },
  "outcome_fidelity": {
    "status": "pass",
    "evidence": [
      "inspection:four-approved-outcomes"
    ]
  },
  "code_quality": {
    "required": true,
    "status": "approve",
    "evidence": [
      "review:independent-candidate"
    ]
  },
  "blocking_evidence": [],
  "outcomes": [
    {
      "outcome": "OUT-001",
      "status": "pass",
      "evidence": [
        "test:eval-canaries"
      ]
    },
    {
      "outcome": "OUT-002",
      "status": "pass",
      "evidence": [
        "test:opencode-lifecycle"
      ]
    },
    {
      "outcome": "OUT-003",
      "status": "pass",
      "evidence": [
        "inspection:release-consistency"
      ]
    },
    {
      "outcome": "OUT-004",
      "status": "pass",
      "evidence": [
        "review:independent-candidate",
        "test:264-unit-tests"
      ]
    }
  ],
  "fidelity": [],
  "inputs": {
    "files": [
      {
        "path": "AGENTS.md",
        "sha256": "sha256:6242e161fe9318a30d6b658b4b4d202a30b0696a160fb2952a98214ddd32df6d"
      },
      {
        "path": "CHANGELOG.md",
        "sha256": "sha256:9a37ba7bd79d281c8619991098ceea502fca2c33c3f91d075808a8093f07f764"
      },
      {
        "path": "README.md",
        "sha256": "sha256:0505443833a2732910545f0d30235d2ac12e4e168072c4cdf2db57fe22c1a566"
      },
      {
        "path": "README.zh-CN.md",
        "sha256": "sha256:85df2c58318ea5fbfe7f6cf54440519843427a7c0465a5467b7d58056f5eb0ea"
      },
      {
        "path": "docs/capability-matrix.md",
        "sha256": "sha256:be126af8847cfbc9ae73c65b17f2084680e3545e6acc79ce53eced0643ac0b07"
      },
      {
        "path": "docs/littlepowers/shapes/2026-10-01-eval-recovery.md",
        "sha256": "sha256:2ab3ebcda86fa0b5ad4d03c00147f5282aa18fcdf54e56d1a399cf2ca0c75cfe"
      },
      {
        "path": "docs/model-compatibility.md",
        "sha256": "sha256:cefcecb48f9998997d05cf5f2066dca535c60fe6635c17dfe5d141c721bbff1d"
      },
      {
        "path": "docs/releases/v1.4.3.md",
        "sha256": "sha256:14c618ab208b219b80dda04005c9b5bcf96da17133fef49da619c3186b31a721"
      },
      {
        "path": "docs/security-model.md",
        "sha256": "sha256:3e60f10b45c97273a2a624353f109bb5c6dcfc608f783441934c3dd413324330"
      },
      {
        "path": "evals/README.md",
        "sha256": "sha256:24b5d1af6cc6cba42f6b7bc7e879b97f5dcca01c3627b90a44f5b4c45750d17b"
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
        "path": "skills/brainstorming/agents/openai.yaml",
        "sha256": "sha256:22ca8eab3de455e10fee824015ce8ead3f6b82089f9ca466689ba6600cb4161d"
      },
      {
        "path": "skills/compact-shaping/SKILL.md",
        "sha256": "sha256:90f5b70edeedd5d2340e6170188e439c400e44fc8dd98d2096fbbd848c051ea4"
      },
      {
        "path": "skills/compact-shaping/agents/openai.yaml",
        "sha256": "sha256:99a73e55a2c89ab0c4a7e0e57dfcb8d75c840f8be4704dc093f507295223333f"
      },
      {
        "path": "skills/debugging-systematically/SKILL.md",
        "sha256": "sha256:93b2b291b41c482b946cee4060b64aae58605b944a5634e43fae966f0bb46ec0"
      },
      {
        "path": "skills/debugging-systematically/agents/openai.yaml",
        "sha256": "sha256:c531292b9c30c477cf63032952518c32d74bd925403735b9f35a4eda128ac953"
      },
      {
        "path": "skills/designing-solutions/SKILL.md",
        "sha256": "sha256:1cc4ff09e3a9699da7a26fb4dea89709e557c52971006c1876fd219bcaa50079"
      },
      {
        "path": "skills/designing-solutions/agents/openai.yaml",
        "sha256": "sha256:9e29a873ab70310801e6928df370b0ed2cdc4c6dbf57ad020d60b88cca95867b"
      },
      {
        "path": "skills/executing-plans/SKILL.md",
        "sha256": "sha256:5f2a3405e2f0a26e5d2ae9dd0231497da1d3375baa1b57a1f0d340a0255058fe"
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
        "sha256": "sha256:49d092600f2865a9fd3a5e6f95d16a4a0b46459eb0cf61f2db928079cadc3e1a"
      },
      {
        "path": "skills/reviewing-changes/agents/openai.yaml",
        "sha256": "sha256:c9a13669271db891f404a728f77a013808cc0d33b7642650db318e19607d839a"
      },
      {
        "path": "skills/using-littlepowers/SKILL.md",
        "sha256": "sha256:30e657543d2c35ce4e3f67ce13a05dec590fd24d0c4e49e5fa9af4d6bd7a1890"
      },
      {
        "path": "skills/using-littlepowers/agents/openai.yaml",
        "sha256": "sha256:75aad3515f1433e02a1aec0fabba4b2cdf4e7e0e1f6eec29020e6d9ea2a93049"
      },
      {
        "path": "skills/verifying-work/SKILL.md",
        "sha256": "sha256:02162dda161d63a8bb30aa3c52a42819f073e103dc018b5e7d217d733f78b98a"
      },
      {
        "path": "skills/verifying-work/agents/openai.yaml",
        "sha256": "sha256:b9fab12845eb23a82f3baf0425b7a289727c3ef8b4529360039d0f0aea892988"
      },
      {
        "path": "skills/writing-plans/SKILL.md",
        "sha256": "sha256:9d024af2a0d5b5a0fcb0c878819ba265dde4a5677f29e3530af43eff33b90bf6"
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
  }
}
```
<!-- /littlepowers:verification -->
