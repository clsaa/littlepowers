# Codex plan tool opt-in follow-up

This supersedes the interpretation that missing `update_plan` implies an
unsupported Codex model/interface. The earlier unavailable observations were
valid for their configuration, but did not test the documented opt-in.

The [official 0.152.0 changelog](https://learn.chatgpt.com/docs/changelog)
states the planning tool defaults to disabled and supports
`tools.update_plan.enabled = true`.

- Codex 0.155.1 with Sol/max and a process-local opt-in produced real native
  `todo_list` start/update/completion events in 31.26 seconds. Diagnostic
  session: `01a0bf7a-9bbe-7b03-8986-e84e72c6b555`.
- The user then explicitly authorized persistent enablement. Added only the
  root-level `tools.update_plan.enabled = true` key to local Codex config.
  TOML parsing and a semantic digest comparison verified all other settings,
  including model/effort, were preserved.
- A fresh CLI probe without a plan-tool command-line override and without
  ignoring user config succeeded in 28.92 seconds. It produced native list
  creation, update and completion events. Session:
  `01a0bf7d-2ca2-7450-8129-d2445820a221`.
- All 14 mirror regression tests passed in 0.142 seconds; whitespace checks
  passed. This follow-up changed configuration and documentation only, not
  runtime code, tests, schema, hooks, plugin installation, or model settings.

Native event submission is now positively verified for Codex. Desktop visual
rendering still requires a fresh desktop task (and application restart if the
host retains its previous config). The current task does not hot-load tools.
This probe is not a full mirror-helper lifecycle or cross-host UI certification.
To roll back the local opt-in, remove the added root key or set it to false and
start a new session. No release or production plugin replacement was performed.
