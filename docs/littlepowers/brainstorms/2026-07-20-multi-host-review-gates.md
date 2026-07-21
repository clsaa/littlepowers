# Multi-host support, Codex plan display, and phase review gates brainstorm

Date: 2026-07-20

## Problem

Three maintainer-reported issues:

1. Littlepowers runs only on Codex and Claude Code; Qoder, QoderCLI, and OpenCode are unsupported.
2. In Codex, Littlepowers plans never appear in the host plan view, because that view renders only native `update_plan` tool calls and never reads Markdown files.
3. Full-route phases (brainstorm, spec, design, plan) chain automatically, so consequential artifacts are produced and executed without human review.

## Constraints

- One shared implementation; no per-host forks of skill bodies or the state CLI.
- Python 3 only at runtime; the OpenCode plugin entry adds no dependency.
- Hooks stay read-only and fail open; no telemetry, no transcript access.
- Proportional workflow preserved: direct route keeps its current light footprint.
- Do not edit user global config; everything rides each host's install mechanism.

## Options

1. **Per-host skill copies.** Rejected: content drift and quadruple maintenance.
2. **Shared skills plus thin per-host adapters (selected).** Qoder consumes the same `skills/` and `hooks/hooks.json` through `.qoder-plugin/plugin.json`; OpenCode gets a small JS plugin that registers the skills directory and reuses `hooks/session-start.py` output verbatim.
3. **File-watching plan display bridge for Codex.** Rejected: Codex renders plans only from `update_plan` tool calls; no file convention can populate the view. The fix is instructional: mirror the checklist through `update_plan` while the Markdown plan stays the durable source of truth.
4. **Ledger-enforced phase gates.** Rejected: gating is model behavior, so it belongs in skill instructions, not in state schema. Default is present-and-stop at each full-route boundary; explicit unattended end-to-end authorization is the only skip.

## Selected direction

Option 2 plus the instructional `update_plan` mirror and skill-level review gates.

## Measurable success

- Qoder CLI installs via `qodercli plugins install` and resolves the state CLI through `${QODER_PLUGIN_ROOT}`.
- OpenCode installs via an `opencode.json` plugin entry; the skills register and the ledger snapshot injects read-only.
- In Codex, a written plan appears in the host plan view and tracks execution checkpoints.
- A full-route run pauses for approval after each phase artifact unless the user explicitly authorized unattended execution.

## Open questions

- Qoder IDE fires only UserPromptSubmit among the hook events; documented as a host limitation, not worked around.
- OpenCode has no SubagentStart equivalent; the worker read-only marker is not injected there.
- Authenticated end-to-end model runs on the new hosts are not yet recorded; docs mark them untested.
