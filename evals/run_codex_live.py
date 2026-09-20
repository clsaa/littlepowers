#!/usr/bin/env python3
"""Opt-in authenticated Codex fixture runner; never used by plugin runtime.

Writes generated fixtures and observable events to an explicit disposable root.
No reasoning events or credentials are retained. Each invocation is bounded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--case", choices=["tiny", "approval", "review", "followup"], required=True)
    parser.add_argument("--resume")
    parser.add_argument("--prompt")
    parser.add_argument("--label", default="run")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--git", default=shutil.which("git"))
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="max")
    parser.add_argument("--sandbox", choices=["read-only", "workspace-write"], default="workspace-write")
    args = parser.parse_args()
    if args.timeout <= 0 or not args.git:
        parser.error("a positive timeout and an available Git executable are required")
    workspace = args.workspace.resolve()
    temporary_roots = {Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve()}
    if not any(parent.parent in temporary_roots and parent.name.startswith("littlepowers-live.")
               for parent in workspace.parents):
        raise SystemExit("workspace must be inside a mktemp littlepowers-live directory")
    workspace.mkdir(parents=True, exist_ok=True)
    if not (workspace / ".git").exists():
        subprocess.run([args.git, "init", "-q", str(workspace)], check=True)
        (workspace / "formatting.py").write_text('def display_name(name):\n    return name\n')
        (workspace / "test_formatting.py").write_text(
            'import unittest\nfrom formatting import display_name\n'
            'class Tests(unittest.TestCase):\n'
            '    def test_trim(self): self.assertEqual(display_name("  Ada  "), "Ada")\n'
            '    def test_empty(self): self.assertEqual(display_name("   "), "Anonymous")\n'
            '    def test_preserve(self): self.assertEqual(display_name("Ada Lovelace"), "Ada Lovelace")\n')
        (workspace / "AGENTS.md").write_text(
            f'Use {sys.executable} for Python and {args.git} for Git.\n'
            f'Use the Littlepowers candidate skills at {ROOT}/skills.\n'
            'Only modify this disposable repository. No network, commits, pushes, or host configuration changes.\n')
        (workspace / "PRD.md").write_text(
            '# Approved outcome\n'
            'Implement display_name(name): trim outer whitespace and use Anonymous for empty/whitespace input.\n'
            'Also implement initials(name): first character of each whitespace-separated word, uppercase, or ? for empty input.\n'
            'Preserve Unicode text. Both APIs must have tests.\n')
    prompts = {
        "tiny": "Fix display_name to trim outer whitespace and return Anonymous for empty or whitespace-only strings. Preserve internal spaces. Run its focused tests. This request concerns only display_name; PRD.md is for a separate future change.",
        "approval": "Implement the complete PRD.md outcome. First prepare a proportional plan and wait for my approval before changing implementation or tests.",
        "review": "Use two native read-only subagents to independently review formatting.py against PRD.md and test_formatting.py for test gaps. This explicitly authorizes only these two bounded reviews. Keep the existing files unchanged. Report concrete defects, effective worker settings, and any capability limitation.",
        "followup": args.prompt or "Continue.",
    }
    prompt = (f'Use $littlepowers:using-littlepowers by reading {ROOT}/skills/using-littlepowers/SKILL.md. '
              'This source tree is the candidate under test; use its references and scripts.\n' + prompts[args.case])
    command = [args.codex, "exec", "--ignore-user-config", "-s", args.sandbox,
               "-c", 'approval_policy="never"', "-c", f'model_reasoning_effort="{args.effort}"',
               "--enable", "multi_agent_v2", "-m", args.model, "--json", "-C", str(workspace)]
    if args.resume:
        command += ["resume", args.resume, prompt]
    else:
        command += [prompt]
    started = time.monotonic()
    version = subprocess.run([args.codex, "--version"], capture_output=True,
                             text=True, check=True, timeout=15).stdout.strip()
    candidate_digest = hashlib.sha256()
    for source in sorted([*ROOT.glob("skills/*/SKILL.md"),
                          *ROOT.glob("references/*.md"), *ROOT.glob("scripts/*.py")]):
        candidate_digest.update(str(source.relative_to(ROOT)).encode())
        candidate_digest.update(b"\0" + source.read_bytes())
    env = os.environ.copy()
    env["PATH"] = str(Path(args.git).parent) + os.pathsep + env["PATH"]
    # Captured output is filtered before persistence; never write raw reasoning.
    process = subprocess.Popen(command, cwd=workspace, env=env, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=os.name == "posix")
    try:
        output, stderr = process.communicate(timeout=args.timeout)
        code = process.returncode
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        output, _ = process.communicate()
        stderr, code = "bounded execution timeout", 124
    events = []
    thread_id = None
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        item = event.get("item", {})
        if item.get("type") in {"reasoning", "reasoning_summary"}:
            continue
        if event.get("type") in {"thread.started", "turn.started", "turn.completed", "turn.failed", "error"} or item.get("type") in {
            "agent_message", "command_execution", "file_change", "collab_tool_call", "mcp_tool_call", "todo_list"
        }:
            events.append(event)
    report = {"case": args.case, "label": args.label, "model": args.model, "effort": args.effort,
              "sandbox": args.sandbox,
              "codex_version": version, "candidate_digest": candidate_digest.hexdigest(),
              "exit_code": code, "elapsed_seconds": round(time.monotonic()-started, 2),
              "thread_id": thread_id, "events": events}
    evidence = workspace.parent / (workspace.name + "-" + args.label + ".json")
    evidence.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "events"}))
    print(f"evidence={evidence}")
    for event in events:
        if event.get("type") in {"error", "turn.failed"} or event.get("item", {}).get("type") == "agent_message":
            print(json.dumps(event, ensure_ascii=False))
    if code and not events:
        print(stderr[-2000:])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
