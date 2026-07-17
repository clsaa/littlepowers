#!/usr/bin/env python3
"""Inject bounded Littlepowers ledger facts into Codex or Claude Code."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def resolve_plugin_root() -> Path:
    """Resolve native Codex and Claude Code plugin root conventions."""
    for variable in ("CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT"):
        value = os.environ.get(variable)
        if value:
            return Path(value)
    return Path(__file__).resolve().parents[1]


PLUGIN_ROOT = resolve_plugin_root()
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from littlepowers_state import (  # noqa: E402
    StateError,
    discover_root,
    load_state,
    render_context,
    render_prompt_reminder,
    render_worker_context,
)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("hook input must be an object")
        root = discover_root(start=event.get("cwd") or Path.cwd())
        state = load_state(root, missing_ok=True)
        if not state:
            return 0
        event_name = event.get("hook_event_name") or event.get("hookEventName")
        if event_name == "UserPromptSubmit":
            context = render_prompt_reminder(state)
        elif event_name == "SubagentStart":
            context = render_worker_context(state)
        else:
            event_name = "SessionStart"
            context = render_context(state)
        if not context:
            return 0
        output = {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context,
            }
        }
        print(json.dumps(output, ensure_ascii=False))
    except (OSError, TypeError, ValueError, json.JSONDecodeError, StateError) as exc:
        print(f"littlepowers recovery hook skipped: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
