# Littlepowers

Littlepowers is a small development workflow for **Codex and Claude Code**. It addresses two recurring failures:

- non-trivial work starts coding before the outcome, requirements, and design are clear;
- an unfinished task loses its place after follow-up messages, context compaction, resume, clear, or a newly opened session in the same workspace.

It is inspired by [Superpowers](https://github.com/obra/superpowers), but it is not a fork or dependency. Littlepowers keeps a proportional brainstorm → spec → design → plan → execute/verify path and adds a project-local recovery ledger.

## How it works

Littlepowers classifies work first:

- **Direct path:** tiny, local, reversible, fully specified changes proceed with proportional verification.
- **Shaped path:** ambiguous, architectural, risky, or multi-file changes use:

  1. brainstorm
  2. spec
  3. design
  4. implementation plan
  5. execution and verification

Artifacts default to `docs/littlepowers/<phase>/...`. Active scratch state lives in `.littlepowers/state.json`; the directory ignores itself so it does not pollute commits. One worktree has one active objective.

The SessionStart hook reads this ledger on startup, resume, clear, and compaction. When state is unfinished, it reminds the agent of the objective, artifacts, current task, and next action. When no unfinished state exists, it emits nothing.

Follow-up messages do not silently replace active work:

- information or corrections update the active objective and work continues;
- questions receive an answer, then work returns to the recorded next action;
- pause requests checkpoint the work;
- only explicit replacement or cancellation closes the prior objective.

## Requirements

- Codex or Claude Code
- Python 3 available as `python3` on macOS/Linux, or `py -3`, `python3`, or `python` on Windows

## Install in Codex

```bash
codex plugin marketplace add clsaa/littlepowers --ref main
codex plugin add littlepowers@littlepowers
```

Start a new Codex task after installation. Codex asks you to review and trust executable hooks; inspect the hook with `/hooks` before enabling it.

Explicit invocation:

```text
$littlepowers:using-littlepowers Help me design and build this feature end to end.
```

For stronger defaults, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into `~/.codex/AGENTS.md`, or into a repository's `AGENTS.md` for project-only use.

Codex-specific ergonomics remain optional: Queue prevents a follow-up from steering the current run; `/goal` helps long-running outcomes; `/side` or `/btw` keeps a side question separate. Littlepowers cannot change these Codex settings for you.

## Install in Claude Code

```bash
claude plugin marketplace add clsaa/littlepowers
claude plugin install littlepowers@littlepowers
```

Start a new session or run `/reload-plugins` after installation. Private GitHub repositories use your existing Git credentials.

Explicit invocation:

```text
/littlepowers:using-littlepowers Help me design and build this feature end to end.
```

For stronger defaults, copy [the optional CLAUDE.md snippet](assets/claude-snippet.md) into `~/.claude/CLAUDE.md`, or into a repository's `CLAUDE.md` for project-only use.

Claude Code uses its native resume, clear, and compaction flow. Littlepowers refreshes the active ledger at each of those SessionStart boundaries; it does not recommend Codex-only Queue or slash commands inside Claude Code.

## State CLI

Skills maintain state automatically. For inspection or manual recovery:

```bash
python3 scripts/littlepowers_state.py show
python3 scripts/littlepowers_state.py context
```

Lifecycle commands are `start`, `checkpoint`, `pause`, `complete`, and `cancel`. `start --replace` is intentionally explicit so a new request cannot silently erase unfinished work.

## Privacy and boundaries

- No telemetry or runtime network access.
- No transcript parsing or raw conversation storage; only workflow metadata is persisted.
- Tracked `.littlepowers/state.json` files are rejected; recovery values are injected as untrusted JSON data.
- No automatic commits, branches, pushes, pull requests, deployments, global setting changes, or subagents.
- No Cursor, OpenCode, Pi, or other harness compatibility layer in this release.
- The only executable hook is a time-bounded, read-only SessionStart state reader.

## Develop and verify

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
claude plugin validate --strict .
```

Release checks also run Codex's bundled skill validator for every directory under `skills/` and the bundled plugin validator for the repository root. GitHub Actions runs the unit suite, compilation, and pinned Claude Code strict validation.

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

Uninstalling the plugin does not delete project-local `.littlepowers/state.json`. Remove that file yourself only when its recovery record is no longer needed.

## 中文摘要

Littlepowers 同时支持 Codex 和 Claude Code。它不会复制 Superpowers 的整套强制流程，而只在中大型、含糊或高风险改动上执行“头脑风暴 → spec → design → write plan → 执行/验证”。未完成任务会记录在项目内、自忽略的状态文件里，并在启动、恢复、清空或上下文压缩后重新注入，因此新消息不应再让原任务无声丢失。

在 Codex 中还可以配合 Queue、`/goal` 和 `/side`；Claude Code 则使用原生的 resume/clear/compact 流程。核心技能、状态机和恢复 Hook 在两端共用同一份实现。

## License and inspiration

Littlepowers is released under the MIT License. The workflow was informed by a review of Superpowers v6.1.1, also MIT-licensed; this repository contains an independent implementation focused on proportional planning and durable recovery.
