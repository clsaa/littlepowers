from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".opencode" / "plugins" / "littlepowers.js"

STUB_HOOK = textwrap.dedent(
    """
    import json, os, sys
    event = json.load(sys.stdin)
    with open(os.environ["LP_EVENT_LOG"], "a", encoding="utf-8") as handle:
        handle.write(event.get("hook_event_name", "?") + "\\n")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event.get("hook_event_name"), "additionalContext": "stub-ledger-context"}}))
    """
).lstrip()

DRIVER = textwrap.dedent(
    """
    const { LittlepowersPlugin } = await import(process.env.LP_PLUGIN);
    const log = (msg) => console.log(msg);
    const mk = (id, text, sessionID) => ({ info: { id, role: 'user', sessionID }, parts: [{ type: 'text', text }] });
    const hooks = await LittlepowersPlugin({ directory: process.cwd() });

    const config = {};
    await hooks.config(config);
    log('CONFIG=' + JSON.stringify(config.skills.paths.map((p) => p.endsWith('skills'))));

    const out = { messages: [mk('m1', 'hello', 's-parent')] };
    await hooks['experimental.chat.messages.transform']({}, out);
    log('M1_PARTS=' + out.messages[0].parts.length);

    // A repeated agent step must not double-inject or re-run the hook.
    await hooks['experimental.chat.messages.transform']({}, out);
    log('M1_PARTS_AFTER_STEP=' + out.messages[0].parts.length);

    out.messages.push(mk('m2', 'next', 's-parent'));
    await hooks['experimental.chat.messages.transform']({}, out);
    log('M2_PARTS=' + out.messages[1].parts.length);

    // A task-created child session receives the worker event instead.
    await hooks.event({ event: { type: 'session.created', properties: { info: { id: 's-child', parentID: 's-parent' } } } });
    const child = { messages: [mk('c1', 'worker start', 's-child')] };
    await hooks['experimental.chat.messages.transform']({}, child);
    log('C1_PARTS=' + child.messages[0].parts.length);

    // Host API drift must fail open, never throw.
    await hooks['experimental.chat.messages.transform']({}, { messages: [null, { info: null }] });
    await hooks.config(null);
    log('GARBAGE_OK');
    console.log('DRIVER_DONE');
    """
).lstrip()


class OpenCodePluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.node = shutil.which("node")
        if not self.node:
            self.skipTest("node is not available")

    def test_plugin_behaviour(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            plugin_dir = base / ".opencode" / "plugins"
            hooks_dir = base / "hooks"
            plugin_dir.mkdir(parents=True)
            hooks_dir.mkdir()
            shutil.copy(PLUGIN, plugin_dir / "littlepowers.js")
            (hooks_dir / "session-start.py").write_text(STUB_HOOK, encoding="utf-8")
            driver = base / "driver.mjs"
            driver.write_text(DRIVER, encoding="utf-8")
            event_log = base / "events.log"

            env = os.environ.copy()
            env["LP_PLUGIN"] = str(plugin_dir / "littlepowers.js")
            env["LP_EVENT_LOG"] = str(event_log)
            result = subprocess.run(
                [self.node, str(driver)],
                cwd=base,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = dict(
                line.split("=", 1)
                for line in result.stdout.splitlines()
                if "=" in line
            )
            self.assertEqual(lines["CONFIG"], "[true]")
            self.assertEqual(lines["M1_PARTS"], "2")
            self.assertEqual(lines["M1_PARTS_AFTER_STEP"], "2")
            self.assertEqual(lines["M2_PARTS"], "2")
            self.assertEqual(lines["C1_PARTS"], "2")
            self.assertIn("GARBAGE_OK", result.stdout)

            events = event_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                events, ["SessionStart", "UserPromptSubmit", "SubagentStart"]
            )

    def test_plugin_fails_open_without_python_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            plugin_dir = base / ".opencode" / "plugins"
            hooks_dir = base / "hooks"
            plugin_dir.mkdir(parents=True)
            hooks_dir.mkdir()
            shutil.copy(PLUGIN, plugin_dir / "littlepowers.js")
            (hooks_dir / "session-start.py").write_text(
                "import sys\nsys.exit(1)\n", encoding="utf-8"
            )
            driver = base / "driver.mjs"
            driver.write_text(
                "const { LittlepowersPlugin } = await import(process.env.LP_PLUGIN);\n"
                "const hooks = await LittlepowersPlugin({ directory: process.cwd() });\n"
                "const out = { messages: [{ info: { id: 'm1', role: 'user' }, parts: [{ type: 'text', text: 'hi' }] }] };\n"
                "await hooks['experimental.chat.messages.transform']({}, out);\n"
                "console.log('PARTS=' + out.messages[0].parts.length);\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["LP_PLUGIN"] = str(plugin_dir / "littlepowers.js")
            result = subprocess.run(
                [self.node, str(driver)],
                cwd=base,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PARTS=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
