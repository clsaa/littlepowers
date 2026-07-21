# Multi-host support, Codex plan display, and phase review gates specification

Date: 2026-07-20

## Purpose and goals

Make Littlepowers first-class on Qoder CLI/Qoder IDE and OpenCode, make its plans visible in Codex's native plan view, and make full-route phases wait for human review by default.

## Non-goals

- No per-host forks of skill bodies, the state CLI, or the hook script.
- No model, effort, or subagent selection for the new hosts.
- No Qoder IDE workaround for missing SessionStart/SubagentStart events; the limitation is documented.
- No state schema change for review gates.

## Functional requirements

1. Qoder CLI discovers the plugin through `.qoder-plugin/plugin.json` with the shared `skills/` directory and `hooks/hooks.json`.
2. The shared hooks manifest resolves the plugin root on Claude Code and Qoder via `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}`; the recovery hook also accepts `QODER_PLUGIN_ROOT`.
3. The router resolves the state CLI on Qoder through `${QODER_PLUGIN_ROOT}` and on OpenCode relative to the loaded `SKILL.md` path; plugin-replacement recovery names each host's resolution path.
4. OpenCode installs through the `plugin` array in `opencode.json` and the repository root `package.json` (`main` points at `.opencode/plugins/littlepowers.js`). The plugin registers the skills directory through the `config` hook and injects the same `hooks/session-start.py` output through `experimental.chat.messages.transform`: full snapshot on the first user message, short reminder on each later user message, deduplicated per message, failing open on any error.
5. After a plan artifact is written, the plan checklist is mirrored through the host's native plan surface (Codex `update_plan`; OpenCode's todo tool), and execution checkpoints keep it current; after resume or compaction it is re-issued from the ledger. The Markdown plan file and the ledger remain authoritative.
6. After checkpointing a brainstorm, specification, design, plan, or compact shape, the agent presents the artifact, names the next phase, and stops. It invokes the next phase only after user approval or an explicit unattended end-to-end authorization in the latest request. Asking for end-to-end delivery alone does not skip gates.

## Acceptance criteria

- `python3 -m unittest discover -s tests -v` passes, including new manifest and OpenCode plugin checks.
- `node --check .opencode/plugins/littlepowers.js` passes.
- Manifests for Codex, Claude Code, and Qoder share name, version, and repository.
- README and README.zh-CN document installation, update, uninstall, and untested-host status for Qoder and OpenCode.
- Capability matrix lists Qoder and OpenCode controls and no longer lists OpenCode as unsupported.

## Assumptions and open questions

- Qoder CLI hook input/output matches the Claude Code JSON contract (`hook_event_name`, `hookSpecificOutput.additionalContext`); validated against Qoder documentation, with a live authenticated run still pending.
- OpenCode message objects expose `info.role`, `info.id`, and `parts[]`; the plugin degrades silently if that shape changes.
