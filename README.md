# Littlepowers

Littlepowers is a small, Codex-first development workflow for two recurring problems:

- non-trivial work starts coding before the outcome, requirements, and design are clear;
- an unfinished task loses its place after follow-up messages, context compaction, a resume, or a newly opened task in the same workspace.

It is inspired by [Superpowers](https://github.com/obra/superpowers), but it is not a fork. Littlepowers keeps only a proportional brainstorm → spec → design → plan → execute/verify path and adds a project-local recovery ledger. It is designed around current Codex and GPT-5.6 behavior rather than cross-harness compatibility.

## What fixes what

| Failure | Primary control | Littlepowers support |
| --- | --- | --- |
| A message interrupts an in-flight run | Set follow-up behavior to **Queue** | Active-skill continuity rules and checkpoints |
| A side question derails the main task | Use `/side` or `/btw` | Return to the recorded next action |
| Long work stops before the outcome | Start with `/goal` and a verifiable result | Plan execution and completion checks |
| Resume/compact/new task loses context | Persist state outside the transcript | SessionStart recovery hook |
| Codex skips planning stages | Explicit skill invocation or durable `AGENTS.md` guidance | Six focused workflow skills |

No plugin can change Steer into Queue for you. In the ChatGPT desktop app, open **Settings → General → Follow-up behavior** and choose **Queue**. Use the alternate shortcut only when you intentionally want to steer the current run.

## Workflow

Littlepowers classifies work first:

- **Direct path:** tiny, local, reversible, fully specified changes proceed with proportional verification.
- **Shaped path:** ambiguous, architectural, risky, or multi-file changes use:

  1. brainstorm
  2. spec
  3. design
  4. implementation plan
  5. execution and verification

Artifacts default to `docs/littlepowers/<phase>/...`. Active scratch state lives in `.littlepowers/state.json`; the directory ignores itself so it does not pollute commits.

Littlepowers supports one active objective per worktree. Use separate worktrees for parallel tasks that need independent state.

## Install

After this repository is available on GitHub:

```bash
codex plugin marketplace add clsaa/littlepowers --ref main
codex plugin add littlepowers@littlepowers
```

Start a new Codex task after installation. Codex requires review and trust before a plugin hook can run; inspect it with `/hooks`. The hook is read-only, uses no network, reads no transcript, and emits nothing when the workspace has no unfinished Littlepowers state.

Invoke the workflow explicitly when it matters:

```text
$littlepowers:using-littlepowers Help me design and build this feature end to end.
```

Implicit skill matching remains available. For stronger defaults across repositories, copy [the optional AGENTS.md snippet](assets/agents-snippet.md) into `~/.codex/AGENTS.md`. For one repository, add it to that repository's `AGENTS.md` instead.

## State CLI

Skills maintain state automatically. For inspection or recovery:

```bash
python3 scripts/littlepowers_state.py show
python3 scripts/littlepowers_state.py context
```

Lifecycle commands are `start`, `checkpoint`, `pause`, `complete`, and `cancel`. `start --replace` is intentionally explicit so a new request cannot silently erase unfinished work.

## Privacy and boundaries

- No telemetry or runtime network access.
- No transcript parsing or raw conversation storage; only the workflow metadata shown by `show` is persisted.
- Tracked `.littlepowers/state.json` files are rejected; recovery values are injected as untrusted JSON data.
- No automatic commits, branches, pushes, PRs, deployments, or subagents.
- No Claude Code, Cursor, OpenCode, or Pi compatibility layer.
- The only executable hook is a time-bounded SessionStart state reader.

## Develop and verify

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
```

Validate each skill with Codex's `skill-creator/scripts/quick_validate.py`, then validate the repository root with `plugin-creator/scripts/validate_plugin.py`.

## Uninstall

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
```

Removing the plugin does not delete project-local `.littlepowers/state.json` files. Delete those files yourself only when you no longer need their recovery record.

## 中文摘要

Littlepowers 不会复制 Superpowers 的整套强制流程。它只在中大型、含糊或高风险改动上执行“头脑风暴 → spec → design → write plan → 执行/验证”，并把未完成任务写进项目内的本地状态文件。配合 Codex 的 Queue、`/goal` 和 `/side`，可以显著减少新消息把原任务带偏后不再续跑的问题。

## License and inspiration

Littlepowers is released under the MIT License. The workflow was informed by a review of Superpowers v6.1.1, also MIT-licensed; this repository contains an independent, Codex-specific implementation.
