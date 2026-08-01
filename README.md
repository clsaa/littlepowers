# Littlepowers

[![CI](https://github.com/clsaa/littlepowers/actions/workflows/test.yml/badge.svg)](https://github.com/clsaa/littlepowers/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/clsaa/littlepowers)](https://github.com/clsaa/littlepowers/releases)

[简体中文](README.zh-CN.md)

Littlepowers is a proportional planning, recovery, and engineering-discipline protocol for Codex, Claude Code, Qoder, and OpenCode. It helps an agent shape consequential work before coding, recover the last durable checkpoint after an interruption, debug from evidence, review material changes, and verify completion at the actual impact scope.

It is inspired by [Superpowers](https://github.com/obra/superpowers), but it is an independent implementation with no runtime dependency or affiliation.

**Why not Superpowers?** Superpowers applies its full workflow ceremony broadly; Littlepowers scales the ceremony to the risk. A one-line fix stays a one-line fix, a bounded change can go brainstorm → plan, and only material unresolved decisions need brainstorm → spec → design → plan. Planning boundaries use an explicit Review Lease instead of assuming that every artifact must always stop. Try it in 30 seconds:

```text
Use Littlepowers to brainstorm this bounded API change, write the plan directly, then implement and verify it.
```

## What it changes

Littlepowers selects planning depth by unresolved decisions and risk:

| Route | When to use it | Durable artifact |
| --- | --- | --- |
| Direct | The outcome and approach are clear | None; long work may still use an execution ledger |
| Lean plan | A small bounded change needs one real decision and an executable plan | Brainstorm → plan |
| Compact | A few connected decisions need shaping | One shape brief |
| Full | Explicit request, or material unresolved architecture, security, migration, cross-system, irreversible, or costly-rollback choices | Brainstorm → spec → design → plan |

Durable artifacts default to `docs/littlepowers/...`. A different root is used only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not silently override the default.

Lean, Compact, and Full planning artifacts can become deterministic Review Gates. The latest request selects exactly one policy:

| Review policy | Meaning |
| --- | --- |
| `blocking` | Discuss, design, wait, or ambiguous intent: present the artifact and require explicit approval |
| `implementation_mandate` | A fixed bounded Lean/Compact outcome was already requested for implementation: continue through execution when invariants pass |
| `windowed` | Wait for a user-specified duration, then continue the unchanged objective only after observing no intervention |
| `unattended` | The user explicitly said not to ask or stop for the unchanged objective: continue through execution |

“End-to-end” alone is not unattended authority. A correction, hold, replacement, unresolved question, proposed scope delta, changed artifact, or drifted Contract stops automatic continuation. Review authority never grants commit, push, PR, publish, deploy, destructive, secret-access, or permission-broadening authority.

All routes bind the latest request and any approved parent PRD, interaction flow, prototype, screenshot set, or contract as the complete outcome. The agent cannot create a smaller product or technical slice on its own. Any `Added / Changed / Deferred / Removed` scope delta is highlighted for explicit approval; otherwise it records `No scope delta`. Implementation runs as one continuous stream under one definition of done. Tasks, checkpoints, rollback units, and small commits control order and safe recovery; they are not staged deliveries. For UI fidelity, implementation-generated screenshots are regression evidence, not substitutes for a user-approved baseline.

Tracked work uses Outcome Lock protocol 1.3. A reviewed Contract records stable `OUT-###` IDs and explicit parent-source digests; a Plan Map must map every active ID to tasks and evidence before execution; a Verification Record keeps work-unit compliance, approved-outcome fidelity, and code quality independent. Schema 4 combines those checks with a persisted Review Lease and blocks execution on drift, incomplete coverage, or an unresolved gate. It cannot infer a requirement that was omitted from the reviewed Contract, so route review still owns semantic completeness.

In Codex, the tracked task checklist is mirrored through the native `update_plan` tool (in OpenCode, through its todo tool) so the plan renders in the host interface; the Markdown plan file remains the durable source of truth.

Three complementary skills apply only when their conditions are present:

- **Systematic debugging** reproduces a failure, traces the earliest supported divergence, tests one hypothesis at a time, and preserves diagnosis-only authority.
- **Proportional verification** gates completion on fresh evidence. Local rollback units get focused checks; shared contracts and releases add the relevant broad checks after integration. A full suite is not the default after every small edit.
- **Lightweight review** gives separate work-unit compliance, approved-outcome fidelity, and code-quality verdicts for requested reviews, delegated integrations, shared milestones, or material rollback risk. Tiny isolated edits may use focused self-review.

These skills do not create agents, choose models, require mandatory TDD, or expose hidden reasoning. Codex, Claude Code, Qoder, and OpenCode discover the same implementation.

All tracked routes use a worktree-local `.littlepowers/state.json` ledger. The schema-4 ledger records protocol identity, the Outcome Lock summary, Review Lease policy and bounded gate audit, objective, phase, current task, optional evidence-based progress, next action, workflow ID, and monotonic revision. A successful planning resolution is bound to its original key, path, bytes, and declared parent-source digests; Contract bind and Plan validation each consume their boundary once, so copied paths or changed sources cannot reuse an old approval. The ledger ignores itself in Git. Progress names a milestone or acceptance-check count; Littlepowers does not infer percentages from time or file count.

Three read-only hook boundaries expose that ledger to the host:

- `SessionStart` provides a bounded snapshot after startup, resume, clear, or compaction.
- `UserPromptSubmit` provides a shorter reminder before each supported prompt.
- `SubagentStart` marks the parent workflow as coordinator-owned and read-only for workers.

The root coordinator is the only ledger writer. A stale revision fails instead of overwriting newer state.

Three boundary tools stay dormant until explicitly needed:

- **Workspace handoff** verifies a named active workflow in another root, cancels only the source ledger, and leaves a pointer for a new task or session rooted at the target. It never scans sibling worktrees or changes the current task root.
- **Review snapshot** hashes a bounded Git candidate and returns a content-free token so a broad uncommitted review can detect stale input. It runs only when explicitly invoked; hooks never scan Git or hash project files.
- **Project Workflow Index** records at most 16 explicitly named worktrees from the same Git repository and reads their current branch and ledger summaries only when `project-status` is called. It never discovers, schedules, or writes a member workflow.

If a material review is too large for one reliable pass, split it by trust, state ownership, or rollback boundary and use one acceptance owner to aggregate shared-interface coverage once. Littlepowers does not create reviewers, select models or effort, or add test runs. The ordinary route therefore pays no handoff/snapshot or extra-model cost.

## What it cannot guarantee

Outcome Lock and Review Lease deterministically reject drift, missing declared IDs, invalid scope state, incomplete declared fidelity, stale gate replay, and false completion transitions. They cannot force a model to extract every meaning from free-form prose, prevent same-turn steering, override the latest user request, infer silence without inspecting the latest visible conversation, or make an active task hot-load a replacement plugin. In Codex, use Queue when a follow-up must wait for the current run to finish.

Hooks may be disabled by trust settings or organization policy. Host wake-up is optional: Codex requires a callable same-task one-shot Scheduled Task capability, Claude Code requires the optional exact-session runner, and Qoder/OpenCode currently resume manually. A lost callback leaves the durable gate intact. The Qoder IDE currently supports only a subset of hook events, so the SessionStart and SubagentStart boundaries stay silent there while UserPromptSubmit reminders still work. Recovery can only return to the last checkpoint that was written. One worktree supports one active top-level workflow; use another worktree for independent concurrent work. In Claude dynamic workflows, keep the approved Littlepowers plan as the sole product-scope authority and use the host workflow only as its execution adapter.

### Parallel worktree overview

Choose one Git worktree as the explicit manager root. Register only the other
same-repository worktrees that you want to see, then request status on demand:

```bash
python3 <state-cli> --root /project project-register \
  --member-root /project-search --label search
python3 <state-cli> --root /project project-status
python3 <state-cli> --root /project project-status --json
python3 <state-cli> --root /project project-unregister \
  --member-root /project-search
```

The manager root is always included. `.littlepowers/project-index.json` stores
only canonical roots, optional labels, timestamps, and its own revision. Status
freshly reads branch, workflow, phase, progress, next action, and Review Gate
metadata from each explicit root. A missing worktree, foreign replacement, or
invalid ledger becomes one error row; healthy rows remain visible and nothing
is pruned or resumed. Hooks never read the index, so an unused index adds no
ordinary prompt cost. This is a project overview, not multi-workflow support in
one checkout and not a replacement for `handoff`.

Littlepowers is standalone. Enabling it and Superpowers as simultaneous default routers can produce duplicate planning instructions. For side-by-side evaluation, invoke one namespaced router explicitly and do not install both durable guidance snippets in the same repository.

See the [capability matrix](docs/capability-matrix.md) for exact boundaries.

## Requirements

- Codex, Claude Code, Qoder CLI or the Qoder IDE, or OpenCode
- Python 3.9 or later
- Git Bash on Windows for the shared plugin hook launcher

## Install in Codex

Install the stable 1.3 release by its exact tag:

```bash
codex plugin marketplace add clsaa/littlepowers --ref v1.3.0
codex plugin add littlepowers@littlepowers
```

Start a new task. Codex asks you to review executable hooks; inspect `/hooks` before trusting them.

Invoke the router:

```text
$littlepowers:using-littlepowers Design and build this feature end to end. Use the full brainstorm, spec, design, and plan path.
```

Inspect recovery state:

```text
$littlepowers:managing-littlepowers Run doctor and show the active workflow.
```

For repository-wide defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into the project's `AGENTS.md`. Use `~/.codex/AGENTS.md` only when you want the behavior in every repository.

Codex Queue defers a follow-up; `/side` or `/btw` isolates an unrelated question. Littlepowers does not use `/goal` because that would create a second objective source.

## Install in Claude Code

For an exact release, use a tag-pinned local marketplace checkout:

```bash
git clone --depth 1 --branch v1.3.0 \
  https://github.com/clsaa/littlepowers.git \
  /absolute/path/littlepowers-v1.3.0
claude plugin marketplace add /absolute/path/littlepowers-v1.3.0
claude plugin install littlepowers@littlepowers
```

Start a new session or run `/reload-plugins`. Review the installed hooks before enabling them.

Invoke the router:

```text
/littlepowers:using-littlepowers Design and build this feature end to end. Use the full brainstorm, spec, design, and plan path.
```

Inspect recovery state:

```text
/littlepowers:managing-littlepowers Run doctor and show the active workflow.
```

For repository-wide defaults, copy [the optional CLAUDE.md snippet](assets/claude-snippet.md) into the project's `CLAUDE.md`. Use `~/.claude/CLAUDE.md` only for a personal global default.

Claude Code uses its native resume, clear, and compaction flow. Littlepowers does not recommend Codex-only commands in Claude Code. After an explicit `windowed` authorization has opened a future gate, an agent with the exact current Claude session UUID may optionally arm one private sleeper:

```bash
python3 /path/to/littlepowers/scripts/littlepowers_review_runner.py schedule \
  --root /canonical/project/root --workflow <workflow-uuid> \
  --gate-revision <opened-revision> --session <session-uuid>
```

It performs at most one normal `claude -p --resume <session-uuid>` call at the deadline, stores no model output, and never retries or bypasses configured permissions. Without the exact session UUID, continue manually.

## Install in Qoder

Qoder CLI and the Qoder IDE share the same plugin layout.

For an exact release, install a tag-pinned checkout:

```bash
git clone --depth 1 --branch v1.3.0 \
  https://github.com/clsaa/littlepowers.git \
  /absolute/path/littlepowers-v1.3.0
qodercli plugins install /absolute/path/littlepowers-v1.3.0
```

For a local checkout, run `qodercli plugins install /path/to/littlepowers` instead. Restart the session or run `/skills reload`, then review the plugin hooks before trusting them. In the Qoder IDE, install through the Marketplace panel or import the local plugin folder.

Invoke the router:

```text
/using-littlepowers Design and build this feature end to end. Use the full brainstorm, spec, design, and plan path.
```

Inspect recovery state:

```text
/managing-littlepowers Run doctor and show the active workflow.
```

For repository-wide defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into the project's `AGENTS.md`; Qoder reads it automatically. Qoder currently has no verified exact-session Review Lease scheduler, so an eligible timed gate resumes manually. The Qoder IDE currently fires only a subset of hook events, so SessionStart snapshots and SubagentStart markers do not appear there yet, and it does not document `QODER_PLUGIN_ROOT` injection for plugin hooks, so hook commands may not resolve the plugin root in the IDE until the host provides it.

## Install in OpenCode

Add the plugin to the `plugin` array in `opencode.json` (global or project-level):

```json
{
  "plugin": ["littlepowers@git+https://github.com/clsaa/littlepowers.git#v1.3.0"]
}
```

Restart OpenCode. The plugin registers the skills directory with OpenCode's native skill tool and injects the same read-only ledger snapshot produced for the other hosts. Verify the install by asking the model to list its skills — the eleven Littlepowers skills should appear. OpenCode prints the plugin name in its logs only when loading fails, so `opencode run --print-logs "hello" 2>&1 | grep -i littlepowers` serves as a failure check: output means a load error, silence means healthy.

Invoke the router by naming the skill:

```text
Use the using-littlepowers skill to design and build this feature end to end. Use the full brainstorm, spec, design, and plan path.
```

For repository-wide defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into the project's `AGENTS.md`; OpenCode reads it automatically. OpenCode has no verified exact-session Review Lease scheduler, so an eligible timed gate resumes manually. It also has no SubagentStart equivalent, so the worker read-only marker is not injected there; coordinator-only ledger writes remain the protocol.

## Use it

Ask for the outcome and planning depth you want:

```text
Use Littlepowers to implement this clear migration script. Track it because it may take several turns, but do not create planning documents.
```

```text
Use Littlepowers to brainstorm this bounded change, write the plan directly without a separate spec or design, then implement and verify the complete outcome.
```

```text
Use Littlepowers compact shaping for this API change, then implement and verify it.
```

```text
Use the full Littlepowers workflow. Brainstorm alternatives, write the spec, design the solution, write the plan, then implement and verify it.
```

State the desired review behavior in ordinary language:

```text
Discuss each planning artifact with me and wait for approval.
```

```text
This bounded change is approved for implementation: brainstorm once, write the plan, then continue without another planning stop.
```

```text
After each planning artifact, wait 15 minutes; if I have not intervened, continue only to the next phase and return to blocking review.
```

```text
Complete this unchanged objective unattended. Do not ask me at planning boundaries.
```

The engineering disciplines can also be invoked directly:

```text
Use Littlepowers to diagnose this failing test without editing. Reproduce it, trace the first divergence, and report the supported cause.
```

```text
Review this integrated change read-only, then verify each completion claim at its actual rollback scope.
```

During tracked work:

- related corrections update the active workflow;
- status or side questions on a recent active workflow are answered before returning to the next action; an open gate then follows its stored policy rather than being silently consumed;
- any correction, hold, replacement, or uncertainty cancels automatic continuation before the workflow changes;
- unrelated work preserves the ledger and moves to a side task or separate worktree;
- replacement archives the prior ledger;
- pause and resume are explicit state transitions.

For a real cross-workspace transfer, create the active target workflow first, hand off the source with both explicit workflow IDs and revisions, then continue from a new task or session rooted at the target. Handoff is not used for ordinary phases, status questions, or compaction.

A paused workflow never resumes from an ordinary implementation prompt. A ledger older than 30 days is marked stale by age and is reconciled before it can continue.

The router receives the latest user request and treats it as authoritative. It does not require special cancellation words when the intent is clear.

## Update and roll back

Do not replace Littlepowers while a tracked task or session is running on any host. A cachebuster install may remove the plugin path captured when that task or session started. Let the active workflow checkpoint and finish or pause, install the update, then start a new task or session. If a Codex cache path was already replaced, Littlepowers resolves the single enabled installation through the host's JSON plugin listing and rereads the current skills before continuing; it stops when resolution is ambiguous.

Schema 4 migration is deterministic and creates one exact
`.littlepowers/archive/<timestamp>-<workflow>-r<revision>-pre-schema4-v<schema>.json`
archive before the first successful schema-4 write. A 1.2 runtime cannot read a
schema-4 current ledger. To roll the runtime back to 1.2, first cancel any open
Review Gate and pause or finish the task, restore that exact pre-schema4 schema-3
archive as `state.json`, then install the older runtime. Never edit or downgrade
the live ledger in place, and never hot-replace the plugin inside an active task.

After the ledger precondition above is satisfied, install or roll back each host
from an exact tag and start a new task/session. For Codex:

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
codex plugin marketplace add clsaa/littlepowers --ref v1.3.0
codex plugin add littlepowers@littlepowers
```

Use the desired earlier tag in the same commands to roll back.

For Claude Code, use a separate checkout of the desired tag as the marketplace:

```bash
git clone --depth 1 --branch v1.3.0 \
  https://github.com/clsaa/littlepowers.git \
  /absolute/path/littlepowers-v1.3.0
claude plugin uninstall littlepowers@littlepowers
claude plugin marketplace remove littlepowers
claude plugin marketplace add /absolute/path/littlepowers-v1.3.0
claude plugin install littlepowers@littlepowers
```

For Qoder CLI, install the same tagged checkout directly:

```bash
git clone --depth 1 --branch v1.3.0 \
  https://github.com/clsaa/littlepowers.git \
  /absolute/path/littlepowers-v1.3.0
qodercli plugins uninstall littlepowers
qodercli plugins install /absolute/path/littlepowers-v1.3.0
```

For OpenCode, change the `#v1.3.0` suffix in the git plugin URL to the exact
desired tag, force-refresh its package cache if necessary, and restart OpenCode.
After any host change, open a new task/session, confirm all eleven skills, and
run the management skill's `doctor`; do not treat plugin reload as ledger
migration.

## Privacy and security

- No telemetry, runtime network calls, or transcript parsing.
- Hooks only read the ledger and fail open when state is missing or invalid.
- The shared reader rejects a Git-tracked state file, links and reparse points, unexpected ownership or write permissions, non-regular files, and state over 64 KiB. The writer also checks the serialized size before replacement.
- POSIX transactions pin both the workspace path and validated state directory before lock, state, and archive I/O, preventing an intermediate or final pathname swap from redirecting writes.
- Protocol artifacts are normalized Markdown paths. Explicit parent and evidence files are read only at lifecycle gates through a bounded safe reader that rejects path escapes, links, special files, replacement races, and oversized input. Hooks never open or hash those files.
- The optional review snapshot is read-only, bounded by path/output/byte/time limits, returns hashes and counts rather than file content, and is never called by a hook.
- Review Lease checks only the explicit planning artifact and declared Outcome Lock files at phase transitions; hooks do not evaluate deadlines, hash artifacts, or schedule work.
- The optional Claude runner creates one private ignored job, sleeps once without polling, invokes the existing exact session with normal permissions, discards output, and has no retry loop. It is not a daemon.
- Mutations use a cross-process lock, workflow ID, expected revision, atomic replacement, and an archive before replacement.
- A Review Lease authorizes only the stored planning transition for the unchanged objective. Littlepowers does not request commits, branches, pushes, pull requests, deployments, publication, visibility changes, destructive actions, secret access, permission changes, or subagents by itself. In Claude dynamic workflows, the approved Littlepowers plan remains the sole product-scope authority and the host workflow is only its execution adapter.

Read the [security model](docs/security-model.md) before broader deployment. Report vulnerabilities through [the security policy](SECURITY.md).

## Model compatibility

Littlepowers does not select a model or effort level. Its planning depth follows task risk, not reasoning effort. Its debugging, review, and verification skills ask for observable evidence and concise verdicts, not private chain-of-thought.

Outcome Lock and Review Lease add local JSON validation and SHA-256 work only at bind, park/resolve, transition, resume/readiness, verification, and completion boundaries. Ordinary routing starts no independent model call, agent, background scan, automatic test run, scheduler, or effort override. Planning gates do add a small number of tool/continuation turns and therefore some wall-clock overhead. Only an explicitly windowed policy may arm one host callback; it resumes the configured host once without selecting a reviewer or model. Runtime work is proportional to explicitly bound files and declared rows, not repository size, so there is no model-parameter conflict with GPT-5.6 Sol xhigh/max/Ultra, Fable 5, or Opus 4.8.

- GPT-5.6 Sol xhigh passed routing scenarios 1 through 9 in one prerelease evaluation campaign.
- GPT-5.6 Sol max completed the v0.3 adversarial review with no remaining P0/P1 issue and 43 tests passing.
- Codex Ultra passed a two-worker coordination scenario. Coordinator ownership remains a cooperative protocol, not operating-system authorization. Ultra is a Codex product mode that adds automatic task delegation beyond the public API's `max` effort; Littlepowers does not select it.
- Claude Fable 5 and Opus 4.8 have no model-setting conflict. The new disciplines are conditionally selected rather than repeated on every prompt. Claude Code strict validation accepts the plugin, but authenticated v1.3 model and dynamic-workflow orchestration flows have not been recorded. A dynamic workflow may add its own planning, token, and time cost.
- Qoder CLI, the Qoder IDE, and OpenCode load the same skills, hooks, and state CLI, but no authenticated end-to-end model run has been recorded for these hosts yet.

Compatibility evidence and untested claims are separated in the dated [model compatibility report](docs/model-compatibility.md).

## Troubleshooting

Run the management skill's `doctor` flow first. Common causes:

- The plugin or hooks were not trusted, were disabled, or are blocked by managed policy.
- Python 3 or Git Bash on Windows is unavailable.
- The prompt runs in a different worktree or non-Git directory than the ledger.
- The ledger is tracked, linked, malformed, oversized, or contains an escaping artifact path.
- Another coordinator advanced the revision; reload instead of retrying a stale write.
- A Review Gate is still `waiting` or became `blocked` because its artifact, Contract, Plan Map, scope, baseline, or latest conversation changed; inspect `review-status` rather than bypassing it.
- A timed callback was not armed because this Codex surface lacks same-task one-shot scheduling, the Claude session UUID was unavailable, or Qoder/OpenCode requires manual resume. The durable gate remains recoverable.
- A plugin cache was replaced during an active task; resolve the one enabled installation, reread the current skills, and use a new task boundary for future updates.
- Claude Code still uses an older cached plugin; update and reload it.
- In Codex, the plan does not appear in the interface because only the native `update_plan` tool renders there; confirm the plan was mirrored after the artifact was written. The Markdown file alone never shows up in that view.
- In the Qoder IDE, SessionStart and SubagentStart hooks are not fired by the host; in OpenCode, the plugin entry in `opencode.json` must point at a refreshed install.

The [capability matrix](docs/capability-matrix.md) distinguishes expected limitations from faults.

## Develop and verify

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
claude plugin validate --strict .
qodercli plugins validate .
```

Release checks also run the bundled Codex skill and plugin validators. GitHub Actions exercises the state and hook suite on Linux, macOS, and Windows and runs pinned Claude Code validation on Linux.

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Uninstall

Codex:

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
```

Claude Code:

```bash
claude plugin uninstall littlepowers@littlepowers
claude plugin marketplace remove littlepowers
```

Qoder CLI: disable the plugin through `enabledPlugins` in `settings.json`, or remove it and the marketplace with `qodercli plugins marketplace remove littlepowers`.

OpenCode: remove the `littlepowers@git+...` entry from the `plugin` array in `opencode.json` and restart.

Also remove any snippet you copied into `AGENTS.md` or `CLAUDE.md`. Uninstalling does not delete `.littlepowers`; keep it for recovery, or remove the exact workspace directory only after its record is no longer needed.

## License and inspiration

Littlepowers is MIT-licensed. The design was informed by Superpowers v6.1.1, also MIT-licensed. Littlepowers is not a fork, is not endorsed by Superpowers or obra, and contains an independent implementation focused on proportional planning and bounded recovery. See [inspiration and provenance](docs/inspiration.md).
