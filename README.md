# Littlepowers

[![CI](https://github.com/clsaa/littlepowers/actions/workflows/test.yml/badge.svg)](https://github.com/clsaa/littlepowers/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/clsaa/littlepowers)](https://github.com/clsaa/littlepowers/releases)

[简体中文](README.zh-CN.md)

Littlepowers is a proportional planning, recovery, and engineering-discipline protocol for Codex, Claude Code, Qoder, and OpenCode. It helps an agent shape consequential work before coding, recover the last durable checkpoint after an interruption, debug from evidence, review material changes, and verify completion at the actual impact scope.

It is inspired by [Superpowers](https://github.com/obra/superpowers), but it is an independent implementation with no runtime dependency or affiliation.

**Why not Superpowers?** Superpowers applies its full workflow ceremony broadly; Littlepowers scales the ceremony to the risk. A one-line fix stays a one-line fix, only material decisions get brainstorm → spec → design → plan, and every full-route artifact pauses for your review before the next phase. Try it in 30 seconds:

```text
Use Littlepowers compact shaping for this API change, then implement and verify it.
```

## What it changes

Littlepowers selects planning depth by unresolved decisions and risk:

| Route | When to use it | Durable artifact |
| --- | --- | --- |
| Direct | The outcome and approach are clear | None; long work may still use an execution ledger |
| Compact | A few connected decisions need shaping | One shape brief |
| Full | Explicit request, or material unresolved architecture, security, migration, cross-system, irreversible, or costly-rollback choices | Brainstorm → spec → design → plan |

Durable artifacts default to `docs/littlepowers/...`. A different root is used only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not silently override the default.

Full-route phase artifacts are review gates: the agent presents each brainstorm, specification, design, and plan for approval and waits before starting the next phase, unless you explicitly authorize unattended end-to-end execution. In Codex, the tracked task checklist is also mirrored through the native `update_plan` tool (in OpenCode, through its todo tool) so the plan renders in the host interface; the Markdown plan file remains the durable source of truth.

Three complementary skills apply only when their conditions are present:

- **Systematic debugging** reproduces a failure, traces the earliest supported divergence, tests one hypothesis at a time, and preserves diagnosis-only authority.
- **Proportional verification** gates completion on fresh evidence. Local rollback units get focused checks; shared contracts and releases add the relevant broad checks after integration. A full suite is not the default after every small edit.
- **Lightweight review** gives acceptance/spec and code-quality verdicts for requested reviews, delegated integrations, shared milestones, or material rollback risk. Tiny isolated edits may use focused self-review.

These skills do not create agents, choose models, require mandatory TDD, or expose hidden reasoning. Codex, Claude Code, Qoder, and OpenCode discover the same implementation.

All tracked routes use a worktree-local `.littlepowers/state.json` ledger. The ledger records an objective, phase, current task, optional evidence-based progress, next action, workflow ID, and monotonic revision. It ignores itself in Git. Progress names a milestone or acceptance-check count; Littlepowers does not infer percentages from time or file count.

Three read-only hook boundaries expose that ledger to the host:

- `SessionStart` provides a bounded snapshot after startup, resume, clear, or compaction.
- `UserPromptSubmit` provides a shorter reminder before each supported prompt.
- `SubagentStart` marks the parent workflow as coordinator-owned and read-only for workers.

The root coordinator is the only ledger writer. A stale revision fails instead of overwriting newer state.

Two boundary tools stay dormant until explicitly needed:

- **Workspace handoff** verifies a named active workflow in another root, cancels only the source ledger, and leaves a pointer for a new task or session rooted at the target. It never scans sibling worktrees or changes the current task root.
- **Review snapshot** hashes a bounded Git candidate and returns a content-free token so a broad uncommitted review can detect stale input. It runs only when explicitly invoked; hooks never scan Git or hash project files.

If a material review is too large for one reliable pass, split it by trust, state ownership, or rollback boundary and use one acceptance owner to aggregate shared-interface coverage once. Littlepowers does not create reviewers, select models or effort, or add test runs. The ordinary route therefore pays no handoff/snapshot or extra-model cost.

## What it cannot guarantee

Littlepowers records and restores workflow facts; it cannot force a model to obey them, prevent same-turn steering, override the latest user request, or make an active task hot-load a replacement plugin. In Codex, use Queue when a follow-up must wait for the current run to finish.

Hooks may be disabled by trust settings or organization policy. The Qoder IDE currently supports only a subset of hook events, so the SessionStart and SubagentStart boundaries stay silent there while UserPromptSubmit reminders still work. Recovery can only return to the last checkpoint that was written. One worktree supports one active top-level workflow; use another worktree for independent concurrent work.

Littlepowers is standalone. Enabling it and Superpowers as simultaneous default routers can produce duplicate planning instructions. For side-by-side evaluation, invoke one namespaced router explicitly and do not install both durable guidance snippets in the same repository.

See the [capability matrix](docs/capability-matrix.md) for exact boundaries.

## Requirements

- Codex, Claude Code, Qoder CLI or the Qoder IDE, or OpenCode
- Python 3.9 or later
- Git Bash on Windows for the shared plugin hook launcher

## Install in Codex

Install the current release by tag:

```bash
codex plugin marketplace add clsaa/littlepowers --ref v1.0.0
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

```bash
claude plugin marketplace add clsaa/littlepowers
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

Claude Code uses its native resume, clear, and compaction flow. Littlepowers does not recommend Codex-only commands in Claude Code.

## Install in Qoder

Qoder CLI and the Qoder IDE share the same plugin layout.

```bash
qodercli plugins marketplace add clsaa/littlepowers
qodercli plugins install littlepowers
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

For repository-wide defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into the project's `AGENTS.md`; Qoder reads it automatically. The Qoder IDE currently fires only a subset of hook events, so SessionStart snapshots and SubagentStart markers do not appear there yet, and it does not document `QODER_PLUGIN_ROOT` injection for plugin hooks, so hook commands may not resolve the plugin root in the IDE until the host provides it.

## Install in OpenCode

Add the plugin to the `plugin` array in `opencode.json` (global or project-level):

```json
{
  "plugin": ["littlepowers@git+https://github.com/clsaa/littlepowers.git"]
}
```

Restart OpenCode. The plugin registers the skills directory with OpenCode's native skill tool and injects the same read-only ledger snapshot produced for the other hosts. Verify the install by asking the model to list its skills — the eleven Littlepowers skills should appear. OpenCode prints the plugin name in its logs only when loading fails, so `opencode run --print-logs "hello" 2>&1 | grep -i littlepowers` serves as a failure check: output means a load error, silence means healthy.

Invoke the router by naming the skill:

```text
Use the using-littlepowers skill to design and build this feature end to end. Use the full brainstorm, spec, design, and plan path.
```

For repository-wide defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into the project's `AGENTS.md`; OpenCode reads it automatically. OpenCode has no SubagentStart equivalent, so the worker read-only marker is not injected there; coordinator-only ledger writes remain the protocol.

## Use it

Ask for the outcome and planning depth you want:

```text
Use Littlepowers to implement this clear migration script. Track it because it may take several turns, but do not create planning documents.
```

```text
Use Littlepowers compact shaping for this API change, then implement and verify it.
```

```text
Use the full Littlepowers workflow. Brainstorm alternatives, write the spec, design the solution, write the plan, then implement and verify it.
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
- status or side questions on a recent active workflow are answered before returning to the next action — except while parked at a review gate, where the agent answers and keeps waiting for approval;
- unrelated work preserves the ledger and moves to a side task or separate worktree;
- replacement archives the prior ledger;
- pause and resume are explicit state transitions.

For a real cross-workspace transfer, create the active target workflow first, hand off the source with both explicit workflow IDs and revisions, then continue from a new task or session rooted at the target. Handoff is not used for ordinary phases, status questions, or compaction.

A paused workflow never resumes from an ordinary implementation prompt. A ledger older than 30 days is marked stale by age and is reconciled before it can continue.

The router receives the latest user request and treats it as authoritative. It does not require special cancellation words when the intent is clear.

## Update and roll back

Do not replace Littlepowers while a tracked Codex task is running. A cachebuster install may remove the cache path captured when that task started. Let the active task checkpoint and finish or pause, install the update, then start a new task. If a path was already replaced, Littlepowers resolves the single enabled installation through the host's JSON plugin listing and rereads the current skills before continuing; it stops when resolution is ambiguous.

For a tagged Codex installation, replace the marketplace snapshot with the desired tag:

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
codex plugin marketplace add clsaa/littlepowers --ref v1.0.0
codex plugin add littlepowers@littlepowers
```

Use an earlier tag in the same commands to roll back.

For Claude Code:

```bash
claude plugin marketplace update littlepowers
claude plugin update littlepowers@littlepowers
```

Restart Claude Code or run `/reload-plugins`. Claude's repository marketplace follows its configured Git source; consult the [changelog](CHANGELOG.md) before updating.

For Qoder CLI:

```bash
qodercli plugins marketplace update littlepowers
qodercli plugins update littlepowers
```

Restart the session or run `/skills reload`. For OpenCode, refresh the git-backed plugin (clear the package cache or reinstall it) and restart OpenCode; pin a tag in the git URL when you need a fixed version.

## Privacy and security

- No telemetry, runtime network calls, or transcript parsing.
- Hooks only read the ledger and fail open when state is missing or invalid.
- The shared reader rejects a Git-tracked state file, links and reparse points, unexpected ownership or write permissions, non-regular files, and state over 64 KiB. The writer also checks the serialized size before replacement.
- POSIX transactions pin both the workspace path and validated state directory before lock, state, and archive I/O, preventing an intermediate or final pathname swap from redirecting writes.
- Artifact references are normalized Markdown paths. Skills read them through a snapshot-bound, bounded safe-reader command that rejects links and special files and labels content as untrusted project data.
- The optional review snapshot is read-only, bounded by path/output/byte/time limits, returns hashes and counts rather than file content, and is never called by a hook.
- Mutations use a cross-process lock, workflow ID, expected revision, atomic replacement, and an archive before replacement.
- Littlepowers does not request commits, branches, pushes, pull requests, deployments, publication, visibility changes, or subagents by itself. The host may delegate in Ultra or dynamic workflows.

Read the [security model](docs/security-model.md) before broader deployment. Report vulnerabilities through [the security policy](SECURITY.md).

## Model compatibility

Littlepowers does not select a model or effort level. Its planning depth follows task risk, not reasoning effort. Its debugging, review, and verification skills ask for observable evidence and concise verdicts, not private chain-of-thought.

- GPT-5.6 Sol xhigh passed routing scenarios 1 through 9 in one prerelease evaluation campaign.
- GPT-5.6 Sol max completed the v0.3 adversarial review with no remaining P0/P1 issue and 43 tests passing.
- Codex Ultra passed a two-worker coordination scenario. Coordinator ownership remains a cooperative protocol, not operating-system authorization. Ultra maps to an OpenAI API `reasoning.effort` value and also switches the host's multi-agent delegation on; Littlepowers does not select it.
- Claude Fable 5 and Opus 4.8 have no model-setting conflict. The new disciplines are conditionally selected rather than repeated on every prompt. Claude Code strict validation accepts the plugin, but an authenticated v0.4 model flow has not been recorded.
- Qoder CLI, the Qoder IDE, and OpenCode load the same skills, hooks, and state CLI, but no authenticated end-to-end model run has been recorded for these hosts yet.

Compatibility evidence and untested claims are separated in the dated [model compatibility report](docs/model-compatibility.md).

## Troubleshooting

Run the management skill's `doctor` flow first. Common causes:

- The plugin or hooks were not trusted, were disabled, or are blocked by managed policy.
- Python 3 or Git Bash on Windows is unavailable.
- The prompt runs in a different worktree or non-Git directory than the ledger.
- The ledger is tracked, linked, malformed, oversized, or contains an escaping artifact path.
- Another coordinator advanced the revision; reload instead of retrying a stale write.
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
