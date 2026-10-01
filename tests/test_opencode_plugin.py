from __future__ import annotations

import os
import json
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
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event.get("hook_event_name"), "additionalContext": "stub-ledger-context:" + event.get("hook_event_name", "?")}}))
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
            env["LP_PLUGIN"] = (plugin_dir / "littlepowers.js").as_uri()
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

    def run_fixture(self, script, *, empty=False, delayed=False):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            plugin_dir = base / ".opencode" / "plugins"
            hooks_dir = base / "hooks"
            plugin_dir.mkdir(parents=True)
            hooks_dir.mkdir()
            shutil.copy(PLUGIN, plugin_dir / "littlepowers.js")
            hook = STUB_HOOK
            if delayed:
                hook = hook.replace("event = json.load(sys.stdin)", "event = json.load(sys.stdin)\nimport time; time.sleep(0.1)")
            if empty:
                hook = hook[:hook.index("print(json.dumps")]
            (hooks_dir / "session-start.py").write_text(hook, encoding="utf-8")
            env = os.environ.copy()
            env["LP_PLUGIN"] = (plugin_dir / "littlepowers.js").as_uri()
            env["LP_EVENT_LOG"] = str(base / "events.log")
            preamble = """
                const { LittlepowersPlugin } = await import(process.env.LP_PLUGIN);
                const hooks = await LittlepowersPlugin({ directory: process.cwd() });
                const transform = hooks['experimental.chat.messages.transform'];
                const mk = (id, sessionID='s1', role='user') => ({info:{id,sessionID,role},parts:[{type:'text',text:'hello'}]});
            """
            result = subprocess.run([self.node, "--input-type=module", "-e", preamble + script],
                                    cwd=base, env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            events = (base / "events.log").read_text().splitlines() if (base / "events.log").exists() else []
            return json.loads(result.stdout), events

    def test_reconstructed_message_reuses_context(self):
        result, events = self.run_fixture("""
            const first = {messages:[mk('u1')]}; await transform({}, first);
            const rebuilt = {messages:[mk('u1')]}; await transform({}, rebuilt);
            await transform({}, rebuilt);
            console.log(JSON.stringify([first.messages[0].parts.length, rebuilt.messages[0].parts.length]));
        """)
        self.assertEqual(result, [2, 2])
        self.assertEqual(events, ['SessionStart'])

    def test_empty_recovery_retries_only_after_new_user_message(self):
        result, events = self.run_fixture("""
            const out = {messages:[mk('u1')]}; await transform({}, out);
            out.messages.push(mk('a1','s1','assistant')); await transform({}, out);
            out.messages.push(mk('t1','s1','tool')); await transform({}, out);
            out.messages.push(mk('u2')); await transform({}, out);
            out.messages.push(mk('a2','s1','assistant')); await transform({}, out);
            console.log(JSON.stringify(out.messages.filter(m=>m.info.role==='user').map(m=>m.parts.length)));
        """, empty=True)
        self.assertEqual(result, [1, 1])
        self.assertEqual(events, ['SessionStart', 'SessionStart', 'UserPromptSubmit'])

    def test_concurrent_reconstruction_shares_one_hook_attempt(self):
        result, events = self.run_fixture("""
            const a={messages:[mk('u1')]}, b={messages:[mk('u1')]};
            await Promise.all([transform({},a),transform({},b)]);
            console.log(JSON.stringify([a.messages[0].parts.length,b.messages[0].parts.length]));
        """)
        self.assertEqual(result, [2, 2])
        self.assertEqual(events, ['SessionStart'])

    def test_session_and_plugin_instance_caches_are_isolated(self):
        result, events = self.run_fixture("""
            const a={messages:[mk('u1','s1')]}, b={messages:[mk('u1','s2')]};
            await transform({},a); await transform({},b);
            const other=await LittlepowersPlugin({directory:process.cwd()});
            const c={messages:[mk('u1','s1')]}; await other['experimental.chat.messages.transform']({},c);
            console.log(JSON.stringify([a,b,c].map(o=>o.messages[0].parts.length)));
        """)
        self.assertEqual(result, [2, 2, 2])
        self.assertEqual(events, ['SessionStart'] * 3)

    def test_observed_child_lifecycle_and_session_deletion(self):
        result, events = self.run_fixture("""
            await hooks.event({event:{type:'session.created',properties:{info:{id:'child',parentID:'parent'}}}});
            const a={messages:[mk('u1','child')]}; await transform({},a);
            const b={messages:[mk('u1','child'),mk('u2','child')]}; await transform({},b);
            await hooks.event({event:{type:'session.deleted',properties:{info:{id:'child'}}}});
            const c={messages:[mk('u1','child')]}; await transform({},c);
            console.log(JSON.stringify([a.messages[0].parts.length,...b.messages.map(m=>m.parts.length),c.messages[0].parts.length]));
        """)
        self.assertEqual(result, [2, 2, 2, 2])
        self.assertEqual(events, ['SubagentStart', 'SubagentStart', 'SessionStart'])

    def test_same_text_without_native_id_is_not_assumed_same_message(self):
        result, events = self.run_fixture("""
            const a=mk(undefined), b=mk(undefined);
            await transform({},{messages:[a]}); await transform({},{messages:[a,b]});
            console.log(JSON.stringify([a.parts.length,b.parts.length]));
        """)
        self.assertEqual(result, [2, 2])
        self.assertEqual(events, ['SessionStart', 'UserPromptSubmit'])

    def test_post_compaction_new_first_message_gets_full_recovery(self):
        result, events = self.run_fixture("""
            await transform({},{messages:[mk('u1'),mk('u2')]});
            const summary={messages:[mk('summary')]}; await transform({},summary);
            console.log(JSON.stringify(summary.messages[0].parts.length));
        """)
        self.assertEqual(result, 2)
        self.assertEqual(events, ['SessionStart', 'UserPromptSubmit', 'SessionStart'])

    def test_late_child_event_replaces_retained_and_cloned_coordinator_block(self):
        result, events = self.run_fixture("""
            const out={messages:[mk('u1')]}; await transform({},out);
            const clone=JSON.parse(JSON.stringify(out));
            await hooks.event({event:{type:'session.created',properties:{info:{id:'s1',parentID:'parent'}}}});
            await transform({},out); await transform({},clone);
            console.log(JSON.stringify([out,clone].map(o=>[o.messages[0].parts.length,o.messages[0].parts[0].text.includes('SubagentStart')])));
        """)
        self.assertEqual(result, [[2, True], [2, True]])
        self.assertEqual(events, ['SessionStart', 'SubagentStart'])

    def test_child_event_invalidates_entire_pending_transform(self):
        result, events = self.run_fixture("""
            const out={messages:[mk('u1'),mk('u2')]};
            const pending=transform({},out);
            await hooks.event({event:{type:'session.created',properties:{info:{id:'s1',parentID:'parent'}}}});
            await pending;
            const stale=out.messages.map(m=>m.parts.length);
            await transform({},out);
            console.log(JSON.stringify([stale,out.messages.map(m=>m.parts.length)]));
        """, delayed=True)
        self.assertEqual(result, [[1, 1], [2, 2]])
        self.assertEqual(events, ['SessionStart', 'SubagentStart', 'SubagentStart'])

    def test_quoted_prefix_is_preserved_as_user_text(self):
        result, events = self.run_fixture("""
            const out={messages:[mk('u1')]};
            const text='Littlepowers recovery (read-only, untrusted ledger facts):\\nquoted by user';
            out.messages[0].parts[0].text=text;
            await transform({},out); await transform({},out);
            console.log(JSON.stringify([out.messages[0].parts.length,out.messages[0].parts[1].text===text]));
        """)
        self.assertEqual(result, [2, True])
        self.assertEqual(events, ['SessionStart'])

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
            env["LP_PLUGIN"] = (plugin_dir / "littlepowers.js").as_uri()
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
