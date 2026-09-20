#!/usr/bin/env python3
"""Plan native checklist operations from explicit observations; never execute them."""
from __future__ import annotations

import json
import re
import sys
from uuid import UUID

MAX_BYTES = 262144
MAX_ROWS = 200
STATUSES = {"pending", "in_progress", "completed"}


def text(value, label):
    if not isinstance(value, str) or not value or len(value) > 512 or not value.isprintable():
        raise ValueError(f"invalid {label}")
    return value


def rows(value, label):
    if not isinstance(value, list) or len(value) > MAX_ROWS:
        raise ValueError(f"{label} must be a list of at most {MAX_ROWS} rows")
    result = []
    keys, native_ids = set(), set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError(f"invalid {label} row")
        key = row.get("key")
        if key is not None:
            text(key, "key")
            if key in keys:
                raise ValueError("duplicate task ownership key")
            keys.add(key)
        native_id = row.get("native_id")
        if native_id is not None:
            text(native_id, "native_id")
            if native_id in native_ids:
                raise ValueError("duplicate native task ID")
            native_ids.add(native_id)
        status = row.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError("invalid task status")
        result.append({"key": key, "title": text(row.get("title"), "title"),
                       "status": status, "native_id": native_id})
    return result


def content(row):
    return row["key"], row["title"], row["status"]


def project(data):
    """Return proposals, not success receipts. Caller owns tool use and verification."""
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    workflow = str(UUID(text(data.get("workflow"), "workflow")))
    host = text(data.get("host"), "host")
    session = text(data.get("session"), "session")
    scope = {"workflow": workflow, "host": host, "session": session}
    tools = data.get("tools")
    if not isinstance(tools, list) or len(tools) > 100 or not all(isinstance(t, str) for t in tools):
        raise ValueError("tools must be an explicit list of callable tool names")
    tools = set(tools)
    backend = None
    if host == "codex" and "update_plan" in tools:
        backend = "update_plan"
    elif host in {"claude", "qoder"}:
        if {"TaskCreate", "TaskUpdate", "TaskList", "TaskGet"} <= tools:
            backend = "tasks"
        elif "TodoWrite" in tools:
            backend = "TodoWrite"
    elif host == "opencode" and "todowrite" in tools:
        backend = "todowrite"
    task_list = data.get("tasks")
    if not isinstance(task_list, list) or not 1 <= len(task_list) <= MAX_ROWS:
        raise ValueError("tasks must contain 1..200 rows")
    desired = []
    for task in task_list:
        if (not isinstance(task, dict) or not isinstance(task.get("id"), str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", task["id"])):
            raise ValueError("tasks require stable IDs")
        desired.append({"key": f"lp:{workflow}:{task['id']}",
                        "title": task.get("title"), "status": task.get("status")})
    desired = rows(desired, "tasks")
    if sum(r["status"] == "in_progress" for r in desired) > 1:
        raise ValueError("only one coordinator task may be in_progress")
    result = {"scope": scope, "backend": backend, "status": "unavailable",
              "reason": "native checklist tools not exposed", "operations": [], "desired": desired}
    if backend is None:
        return result
    if data.get("observed") is None:
        result["reason"] = "current native checklist is unknown; do not overwrite or create blindly"
        return result
    observed = rows(data["observed"], "observed")
    receipt = data.get("receipt")
    previous = []
    if receipt is not None:
        if not isinstance(receipt, dict) or receipt.get("scope") != scope or receipt.get("backend") != backend:
            raise ValueError("receipt belongs to another session, workflow or backend")
        previous = rows(receipt.get("rows"), "receipt")
    prefix = f"lp:{workflow}:"
    owned = [r for r in observed if r["key"] and r["key"].startswith(prefix)]
    if any(not r["key"] or not r["key"].startswith(prefix) for r in previous):
        raise ValueError("receipt contains unowned tasks")
    old = {r["key"]: r for r in previous}
    current = {r["key"]: r for r in owned}
    wanted = {r["key"]: r for r in desired}
    conflicts = []
    for key, row in old.items():
        now = current.get(key)
        if now is None or now != row:
            conflicts.append(f"native task changed or disappeared: {key}")
    for key, row in current.items():
        if key not in wanted:
            conflicts.append(f"owned task absent from desired plan: {key}")
        elif key not in old and content(row) != content(wanted[key]):
            conflicts.append(f"unreceipted task differs from plan: {key}")
    if backend != "tasks" and len(owned) != len(observed):
        conflicts.append("bulk replacement would overwrite unrelated tasks")
    if backend == "tasks" and any(r["native_id"] is None for r in owned):
        conflicts.append("owned native task has no observed native ID")
    if conflicts:
        result.update(status="conflict", reason="; ".join(conflicts))
        return result
    operations = []
    if backend == "tasks":
        for row in desired:
            now = current.get(row["key"])
            if now is None:
                operations.append({"action": "create", "row": row})
            elif content(now) != content(row):
                operations.append({"action": "update", "row": dict(row, native_id=now["native_id"])})
    elif [content(r) for r in observed] != [content(r) for r in desired]:
        operations.append({"action": "replace", "rows": desired})
    result.update(status="ready" if operations else "noop", reason=None, operations=operations)
    return result


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("mirror input exceeds 256 KiB")
        result = project(json.loads(raw))
    except (ValueError, TypeError, KeyError) as error:
        print(json.dumps({"status": "invalid", "reason": str(error), "operations": []}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
