# Multi-host support, Codex plan display, and phase review gates design

Date: 2026-07-20

## Architecture

One shared core (skills, state CLI, hook script) plus thin per-host adapters:

- **Qoder**: `.qoder-plugin/plugin.json` manifest only. Skills and hooks are convention-discovered; the single `hooks/hooks.json` command resolves `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}`, so no second hooks file exists. `hooks/session-start.py` accepts `QODER_PLUGIN_ROOT` before falling back to its own path.
- **OpenCode**: `.opencode/plugins/littlepowers.js` (zero-dependency ES module) with two hooks:
  - `config` appends `<plugin-root>/skills` to `config.skills.paths`, so OpenCode's native skill tool discovers the unchanged skills.
  - `experimental.chat.messages.transform` runs `hooks/session-start.py` with a synthetic `{hook_event_name, cwd}` stdin payload and injects the returned `additionalContext` into message parts. The first user message gets the SessionStart snapshot; each later user message gets the UserPromptSubmit reminder. A processed-ID set plus an injection marker bound hook runs to at most one per message even though the hook fires every agent step. All errors resolve to no injection.
- **Codex and Claude Code**: unchanged manifests; description strings name all four hosts.

## Plan surface mirroring

Host plan views render tool calls, not files. `writing-plans` instructs mirroring the checklist through Codex `update_plan` (or OpenCode's todo tool) after the artifact is written; `executing-plans` refreshes it at each checkpoint and re-issues it from the ledger after resume/clear/compaction. The mirror is labeled ephemeral display state; the ledger and plan file stay authoritative, so recovery never depends on it.

## Review gates

Gates are skill instructions, not ledger state:

- `using-littlepowers` gains a "Review phase boundaries" policy: full-route artifacts are review gates; chaining requires user approval or explicit unattended end-to-end authorization; end-to-end delivery requests alone do not qualify.
- Each full-route phase skill and `compact-shaping` ends with present-and-stop wording naming the next phase skill.
- Rework uses the existing checkpoint flow: the CLI permits setting any phase and deduplicates `--completed`, so a rejected artifact is revised and re-checkpointed without schema changes.

## Failure and compatibility behavior

- Missing Python or state on OpenCode: no injection, session unaffected (fail open).
- Qoder IDE: unsupported hook events are ignored by the host; UserPromptSubmit reminders still fire.
- Existing Codex/Claude installations are unaffected; the hooks manifest still contains `${CLAUDE_PLUGIN_ROOT}`.
- Rollback: remove `.qoder-plugin/`, `.opencode/`, and `package.json`; revert skill wording. Each unit is independently reversible.

## Verification strategy

- Python: `python3 -m unittest discover -s tests -v` with new manifest/plugin assertions; `python3 -m compileall -q scripts hooks tests`.
- JavaScript: `node --check .opencode/plugins/littlepowers.js` (guarded in tests by node availability).
- Host validators (`claude plugin validate --strict .`, Codex and Qoder plugin validators) run at release; authenticated live runs on the new hosts are recorded separately before claiming support beyond documentation.
