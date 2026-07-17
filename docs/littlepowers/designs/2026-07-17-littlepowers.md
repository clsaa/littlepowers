# Littlepowers Technical Design

> Historical v0.2 artifact. Superseded by [the v0.3 design](2026-07-17-v0.3-expert-review.md).

## Architecture

Littlepowers has a shared core and two thin packaging layers:

```text
Codex manifest/marketplace ─┐
                           ├─ shared skills ─ shared state CLI
Claude manifest/marketplace┘        │
                                    └─ shared SessionStart recovery hook
```

No behavioral code is duplicated by harness.

## Repository layout

```text
.codex-plugin/plugin.json             Codex plugin metadata
.agents/plugins/marketplace.json      Codex marketplace entry
.claude-plugin/plugin.json            Claude Code plugin metadata
.claude-plugin/marketplace.json       Claude Code marketplace entry
skills/*/SKILL.md                     shared workflow instructions
skills/*/agents/openai.yaml           optional Codex UI metadata
scripts/littlepowers_state.py         shared state lifecycle and context renderer
hooks/hooks.json                      shared SessionStart registration
hooks/run-hook.cmd                    cross-platform Python launcher
hooks/session-start.py                shared read-only recovery hook
assets/agents-snippet.md              optional Codex durable guidance
assets/claude-snippet.md              optional Claude Code durable guidance
```

## Packaging

Both native manifests use the name `littlepowers` and the same semantic version. Component directories stay at the repository root so both harnesses can use default discovery.

The Claude marketplace uses a relative `./` source. Claude Code copies installed plugins into a versioned cache, so every runtime dependency must remain inside the plugin directory. The Codex marketplace continues to use its native URL-source object.

## Recovery hook

`hooks/hooks.json` registers `SessionStart` for `startup|resume|clear|compact`. The command points to a cross-platform launcher through `${CLAUDE_PLUGIN_ROOT}`. Claude Code defines that variable natively; current Codex plugin hooks provide it as a compatibility alias in addition to `PLUGIN_ROOT`.

The launcher runs `python3` on Unix. On Windows it tries `py -3`, `python3`, then `python`, and exits without blocking the session when Python is unavailable.

`session-start.py` resolves the plugin root in this order:

1. `CLAUDE_PLUGIN_ROOT`
2. `PLUGIN_ROOT`
3. the script's parent directory

It reads JSON from standard input, discovers the workspace root from `cwd`, rejects tracked state, and emits Claude-compatible `hookSpecificOutput.additionalContext`. Codex consumes the same payload.

## State boundary

`.littlepowers/state.json` is project-local scratch state and `.littlepowers/.gitignore` contains `*`. The hook reads but never writes this file. The state CLI alone performs atomic writes.

The state schema remains version 1:

```json
{
  "schema_version": 1,
  "status": "active",
  "objective": "Ship a dual-harness recovery workflow",
  "phase": "execute",
  "artifacts": {
    "plan": "docs/littlepowers/plans/2026-07-17-littlepowers.md"
  },
  "current_task": "Task 4",
  "next_action": "Run both native plugin validators",
  "completed": ["brainstorm", "spec", "design", "plan"],
  "updated_at": "2026-07-17T00:00:00Z"
}
```

State values are rendered as JSON data inside an explicit untrusted-data boundary. They are never interpreted as instructions.

## Skill behavior

`using-littlepowers` always checks the recovery ledger before classifying the new message. It routes non-trivial work through the phase skills and defines interruption semantics. The other five skills remain platform-neutral.

Harness-specific advice is deliberately small:

- Codex: Queue, `/goal`, `/side`, and `/btw` may improve interaction ergonomics.
- Claude Code: native resume, clear, and compaction are recovery boundaries; persistent defaults belong in `CLAUDE.md`.

The workflow itself does not depend on any of these optional controls.

## Security and failure behavior

- No runtime network access or telemetry.
- No transcript parsing.
- No automatic commits, worktrees, or global setting changes.
- Tracked state is rejected to avoid repository-supplied recovery injection.
- Malformed input and missing Python fail open so sessions still start.
- Hook timeout remains five seconds.

## Verification strategy

1. Unit-test state lifecycle and hook behavior under both root environment names.
2. Validate JSON, skill shape, versions, and marketplace sources in CI.
3. Run bundled Codex skill/plugin validators locally.
4. Run `claude plugin validate --strict .`.
5. Install from each native marketplace and inspect the six discovered skills.
6. Run one real, read-only recovery probe in each harness from a temporary workspace.
