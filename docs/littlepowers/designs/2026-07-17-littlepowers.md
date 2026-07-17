# Littlepowers Technical Design

## Architecture

Littlepowers has three independent layers:

1. **Skills** describe how Codex routes and performs work.
2. **State CLI** owns the durable workflow record and all state transitions.
3. **SessionStart hook** reads the record and injects recovery context.

The hook does not load entire skills. Native Codex skill discovery remains the entry mechanism; the hook only restores unfinished work.

## Components

### Plugin package

`.codex-plugin/plugin.json` declares the skill directory and user-facing metadata. Codex's default `hooks/hooks.json` discovery is used so the manifest remains compatible with the current scaffold validator, whose schema has not yet caught up with the documented manifest `hooks` field.

`.agents/plugins/marketplace.json` points to the repository root, matching the single-repository marketplace pattern used by Superpowers.

### Skills

- `using-littlepowers`: classify scope, initialize/read state, route phases, and define interruption semantics.
- `brainstorming`: inspect context, ask only blocking questions, compare approaches, and save the decision record.
- `writing-specs`: turn the chosen outcome into testable behavior and boundaries.
- `designing-solutions`: define components, interfaces, data flow, failure modes, and test strategy.
- `writing-plans`: map the design to ordered, checkable tasks.
- `executing-plans`: review the plan, execute it, checkpoint after meaningful progress, and verify completion.

Skills stay short and refer to shared state commands rather than duplicating recovery prose.

### State CLI

`scripts/littlepowers_state.py` uses only the Python standard library.

Root selection:

1. explicit `--root`, if supplied;
2. `git rev-parse --show-toplevel` from the current directory;
3. the current directory when not in Git.

State lifecycle:

```text
absent/complete/cancelled ── start ──> active
active ── checkpoint ──> active
active ── pause ──> paused
paused ── checkpoint ──> active
active/paused ── complete ──> complete
active/paused ── cancel ──> cancelled
```

`start` refuses to overwrite active or paused state unless `--replace` is explicit. `checkpoint` updates only supplied fields and appends a completed checkpoint without duplicating it. Writes use a temporary file plus atomic replacement.

State schema:

```json
{
  "schema_version": 1,
  "status": "active",
  "objective": "Create Littlepowers",
  "phase": "design",
  "artifacts": {
    "brainstorm": "docs/littlepowers/brainstorms/2026-07-17-littlepowers.md",
    "spec": "docs/littlepowers/specs/2026-07-17-littlepowers.md",
    "design": "docs/littlepowers/designs/2026-07-17-littlepowers.md",
    "plan": null
  },
  "current_task": null,
  "next_action": "Write the implementation plan",
  "completed": ["brainstorm", "spec"],
  "updated_at": "2026-07-17T12:00:00Z"
}
```

### Recovery hook

`hooks/session-start.py` reads the event JSON from stdin and calls the state library in read-only mode. If state is active or paused, it returns:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "...concise active objective and next action..."
  }
}
```

No state, malformed state, tracked state, or a non-workspace directory produces no recovery stdout and exit code 0. A rejected file is reported only on stderr so it cannot block Codex startup. Recovery fields are serialized as JSON and explicitly labeled untrusted data so content inside a field is not treated as hook instructions.

## Interruption policy

Littlepowers cannot change whether a message is sent as Steer or Queue. The workflow therefore combines:

- preventive product configuration (Queue and side chat);
- a model-visible rule in the active skill;
- filesystem checkpoints at phase and task boundaries;
- hook-based recovery after startup, resume, clear, and compaction.

The design deliberately omits a `Stop` hook. Blocking turn completion can create loops or prevent intentional pauses. It also omits a `UserPromptSubmit` hook because SessionStart plus queued follow-ups covers recovery without injecting context on every prompt.

## Safety and privacy

- Standard library only; no runtime dependency installation.
- No network, telemetry, transcript parsing, or secret collection.
- State is self-ignored and local to the workspace/worktree.
- Tracked state files are rejected to keep repository content out of developer-context injection.
- Hooks are read-only and time-bounded.
- Automatic commits, branch creation, pushes, and PR creation are outside the workflow unless the user requests them.

## Verification strategy

- Python `unittest` for state transitions and hook output.
- JSON parsing checks for plugin and marketplace manifests.
- Codex skill and plugin validators.
- Direct hook smoke tests with representative stdin payloads.
- Local marketplace installation plus `codex debug prompt-input` inspection for skill discovery.
- A read-only, ephemeral `codex exec` probe for end-to-end SessionStart context injection; `debug prompt-input` does not execute lifecycle hooks in the tested Codex version.
