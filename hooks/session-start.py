#!/usr/bin/env python3
"""Inject unfinished Littlepowers state into Codex or Claude Code."""

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
    state_file_is_tracked,
)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("hook input must be an object")
        root = discover_root(start=event.get("cwd") or Path.cwd())
        if state_file_is_tracked(root):
            print(
                "littlepowers SessionStart hook skipped: refusing tracked state file",
                file=sys.stderr,
            )
            return 0
        state = load_state(root, missing_ok=True)
        if not state:
            return 0
        context = render_context(state)
        if not context:
            return 0
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
        print(json.dumps(output, ensure_ascii=False))
    except (OSError, TypeError, ValueError, json.JSONDecodeError, StateError) as exc:
        print(f"littlepowers SessionStart hook skipped: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
