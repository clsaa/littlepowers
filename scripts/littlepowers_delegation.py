#!/usr/bin/env python3
"""Validate one explicit Littlepowers host capability snapshot.

This module does not discover capabilities or launch workers.  The coordinator
supplies facts observed from the current native host interface after the
Delegation Gate has already passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from typing import Any


SNAPSHOT_VERSION = 1
ALLOWED_HOSTS = frozenset({"codex", "claude", "qoder", "other"})
ALLOWED_CONTEXT_MODES = frozenset({"fresh", "fork", "team"})
ALLOWED_CAPABILITY_SOURCES = frozenset(
    {"tool-schema", "host-command", "approved-agent-definition"}
)
ALLOWED_ISOLATION = frozenset({"read-only", "worktree", "equivalent"})
ALLOWED_PERMISSION_BOUNDARIES = frozenset(
    {
        "tool-restricted",
        "sandbox-read-only",
        "host-policy",
        "worktree",
        "permission-mode-only",
        "prompt-only",
    }
)
ALLOWED_DURABILITY = frozenset({"resumable", "session-only", "unknown"})
ALLOWED_NESTED_DELEGATION = frozenset({"blocked", "available", "unknown"})
ALLOWED_LEAF_BOUNDARIES = frozenset(
    {"tool-disabled", "host-depth-limit", "prompt-only", "unknown"}
)
READ_ONLY_PERMISSION_BOUNDARIES = frozenset(
    {"tool-restricted", "sandbox-read-only"}
)
HIGH_COST_EFFORTS = frozenset({"max", "ultra"})
HIGH_COST_MODELS = frozenset({"ultimate"})
MAX_TEXT_LENGTH = 128


class SnapshotError(ValueError):
    """Raised when a capability snapshot violates a stable protocol boundary."""


def _required_text(snapshot: Mapping[str, Any], key: str) -> str:
    value = snapshot.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SnapshotError(f"{key} must be a non-empty string")
    normalized = value.strip()
    if len(normalized) > MAX_TEXT_LENGTH:
        raise SnapshotError(f"{key} exceeds {MAX_TEXT_LENGTH} characters")
    if not normalized.isprintable():
        raise SnapshotError(f"{key} must contain only printable characters")
    return normalized


def _choice(
    snapshot: Mapping[str, Any], key: str, allowed: frozenset[str]
) -> str:
    value = _required_text(snapshot, key).lower()
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise SnapshotError(f"{key} must be one of: {choices}")
    return value


def validate_snapshot(snapshot: Mapping[str, Any]) -> dict[str, object]:
    """Return a normalized capability snapshot or fail closed.

    Only host-independent Littlepowers invariants are enforced here. Model IDs,
    aliases, and effort availability deliberately remain owned by the current
    host interface.
    """

    host = _choice(snapshot, "host", ALLOWED_HOSTS)
    mechanism = _required_text(snapshot, "mechanism")
    capability_source = _choice(
        snapshot, "capability_source", ALLOWED_CAPABILITY_SOURCES
    )
    context_mode = _choice(snapshot, "context_mode", ALLOWED_CONTEXT_MODES)
    effective_model = _required_text(snapshot, "effective_model")
    effective_effort = _required_text(snapshot, "effective_effort")
    isolation = _choice(snapshot, "isolation", ALLOWED_ISOLATION)
    permission_boundary = _choice(
        snapshot, "permission_boundary", ALLOWED_PERMISSION_BOUNDARIES
    )
    durability = _choice(snapshot, "durability", ALLOWED_DURABILITY)
    nested_delegation = _choice(
        snapshot, "nested_delegation", ALLOWED_NESTED_DELEGATION
    )
    leaf_boundary = _choice(snapshot, "leaf_boundary", ALLOWED_LEAF_BOUNDARIES)

    mutation = snapshot.get("mutation")
    if not isinstance(mutation, bool):
        raise SnapshotError("mutation must be a boolean")
    team_boundary_declared = snapshot.get("team_boundary_declared", False)
    if not isinstance(team_boundary_declared, bool):
        raise SnapshotError("team_boundary_declared must be a boolean")

    boundary_errors = []
    if nested_delegation != "blocked":
        boundary_errors.append("Littlepowers workers must be leaf agents")
    if leaf_boundary not in {"tool-disabled", "host-depth-limit"}:
        boundary_errors.append(
            "leaf depth requires a disabled worker delegation tool or an effective "
            "native depth limit; worker instructions alone are insufficient"
        )
    if permission_boundary == "prompt-only":
        boundary_errors.append("a prompt-only permission boundary is not enforceable")
    if mutation and isolation not in {"worktree", "equivalent"}:
        boundary_errors.append("mutation requires worktree or equivalent isolation")
    if mutation and permission_boundary == "sandbox-read-only":
        boundary_errors.append("mutation conflicts with a read-only sandbox")
    if not mutation and permission_boundary not in READ_ONLY_PERMISSION_BOUNDARIES:
        boundary_errors.append(
            "read-only work requires a tool or sandbox boundary; permission mode "
            "or prose alone is insufficient"
        )
    if context_mode == "team":
        if not team_boundary_declared:
            boundary_errors.append("team mode requires a separately declared team boundary")
        if durability != "session-only":
            boundary_errors.append("team mode must be treated as session-only")
    elif team_boundary_declared:
        boundary_errors.append("team_boundary_declared is valid only for team mode")
    if boundary_errors:
        raise SnapshotError("; ".join(boundary_errors))

    model_key = effective_model.lower()
    effort_key = effective_effort.lower()
    setting_override = model_key != "inherit" or effort_key != "inherit"
    high_cost_selection = (
        context_mode == "team"
        or model_key in HIGH_COST_MODELS
        or effort_key in HIGH_COST_EFFORTS
    )

    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "host": host,
        "mechanism": mechanism,
        "capability_source": capability_source,
        "context_mode": context_mode,
        "effective_model": effective_model,
        "effective_effort": effective_effort,
        "isolation": isolation,
        "permission_boundary": permission_boundary,
        "durability": durability,
        "mutation": mutation,
        "nested_delegation": nested_delegation,
        "leaf_boundary": leaf_boundary,
        "authorization": "work-unit-required",
        "setting_override": setting_override,
        "high_cost_selection": high_cost_selection,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate facts observed from the current native delegation interface. "
            "This command does not discover capabilities or launch workers."
        )
    )
    parser.add_argument("--host", required=True, choices=sorted(ALLOWED_HOSTS))
    parser.add_argument("--mechanism", required=True)
    parser.add_argument(
        "--capability-source",
        required=True,
        choices=sorted(ALLOWED_CAPABILITY_SOURCES),
    )
    parser.add_argument(
        "--context-mode", required=True, choices=sorted(ALLOWED_CONTEXT_MODES)
    )
    parser.add_argument("--effective-model", default="inherit")
    parser.add_argument("--effective-effort", default="inherit")
    parser.add_argument("--isolation", required=True, choices=sorted(ALLOWED_ISOLATION))
    parser.add_argument(
        "--permission-boundary",
        required=True,
        choices=sorted(ALLOWED_PERMISSION_BOUNDARIES),
    )
    parser.add_argument(
        "--durability", required=True, choices=sorted(ALLOWED_DURABILITY)
    )
    parser.add_argument(
        "--nested-delegation",
        required=True,
        choices=sorted(ALLOWED_NESTED_DELEGATION),
    )
    parser.add_argument("--mutation", action="store_true")
    parser.add_argument(
        "--leaf-boundary", required=True, choices=sorted(ALLOWED_LEAF_BOUNDARIES)
    )
    parser.add_argument("--team-boundary-declared", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        normalized = validate_snapshot(vars(args))
    except SnapshotError as error:
        print(f"littlepowers-delegation: {error}", file=sys.stderr)
        return 2
    print(json.dumps(normalized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
