"""Offline host-output fixtures; never invoke a model or require authentication."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('codex_live', ROOT / 'evals/run_codex_live.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
CANARY = 'SYNTHETIC_PRIVATE_PAYLOAD_DO_NOT_SHARE'


class LiveEvalTests(unittest.TestCase):
    def invoke(self, workspace, events, *, extra=(), code=0, stderr=CANARY, version="codex-cli 0.159.0\n", timeout=False):
        times_out = timeout
        class Host:
            returncode = code
            pid = 12345
            calls = 0
            def kill(self):
                pass
            def communicate(self, timeout=None):
                self.calls += 1
                if times_out and self.calls == 1:
                    raise subprocess.TimeoutExpired("synthetic-host", 1)
                return '\n'.join(json.dumps(e) for e in events), stderr
        argv = ['run_codex_live.py', '--workspace', str(workspace), '--case', 'tiny', *extra]
        stdout, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, 'argv', argv), patch.object(runner.os, 'killpg', create=True), patch.object(runner.subprocess, 'Popen', return_value=Host()), \
             patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, version, '')), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(errors):
            result = runner.main()
        return result, stdout.getvalue() + errors.getvalue()

    def workspace(self, directory):
        workspace = Path(directory) / 'fixture'
        (workspace / '.git').mkdir(parents=True)
        return workspace

    def test_default_report_excludes_payloads_in_all_observable_events(self):
        events = [{'type': 'item.completed', 'item': {'type': kind, 'text': CANARY,
                   'command': CANARY, 'aggregated_output': CANARY, 'arguments': {'secret': CANARY},
                   'result': CANARY, 'changes': [{'path': CANARY}], 'status': 'completed', 'exit_code': 0}}
                  for kind in ['agent_message', 'command_execution', 'mcp_tool_call', 'collab_tool_call', 'file_change', 'todo_list']]
        events += [{'type': 'error', 'message': CANARY}, {'type': 'turn.failed', 'error': {'message': CANARY}},
                   {'type': 'thread.started', 'thread_id': CANARY},
                   {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 2, 'extra': CANARY}}]
        with tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
            workspace = self.workspace(directory)
            result, output = self.invoke(workspace, events)
            report = (Path(directory) / 'fixture-run.json').read_text()
            self.assertEqual(result, 0)
            self.assertFalse(list(Path(directory).glob('*.sensitive.json')))
            self.assertNotIn(CANARY, report + output)
            self.assertEqual(json.loads(report)['events'][-1]['usage'], {'input_tokens': 10, 'output_tokens': 2})

    def test_failed_host_without_events_does_not_print_stderr(self):
        with tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
            result, output = self.invoke(self.workspace(directory), [], code=7)
            self.assertEqual(result, 7)
            self.assertNotIn(CANARY, output)

    def test_sensitive_logging_is_explicit_separate_and_private(self):
        events = [{'type': 'item.completed', 'item': {'type': kind, 'text': CANARY}}
                  for kind in ['command_execution', 'mcp_tool_call', 'agent_message', 'reasoning']]
        with tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
            workspace = self.workspace(directory)
            _, output = self.invoke(workspace, events, extra=['--sensitive-log'])
            shareable = Path(directory) / 'fixture-run.json'
            sensitive = Path(directory) / 'fixture-run.sensitive.json'
            self.assertNotIn(CANARY, shareable.read_text() + output)
            raw = json.loads(sensitive.read_text())
            self.assertTrue(raw['sensitive'])
            self.assertFalse(raw['redacted'])
            self.assertEqual(raw['stderr'], CANARY)
            self.assertEqual(len(raw['events']), 3)
            self.assertTrue(all(e['item']['text'] == CANARY for e in raw['events']))
            if sys.platform != 'win32':
                self.assertEqual(sensitive.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(SystemExit):
                self.invoke(workspace, [], extra=['--sensitive-log'])
            self.assertEqual(json.loads(sensitive.read_text()), raw)

    def test_timeout_diagnostics_are_only_retained_with_sensitive_opt_in(self):
        for sensitive in (False, True):
            with self.subTest(sensitive=sensitive), tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
                result, output = self.invoke(self.workspace(directory), [],
                                             extra=['--sensitive-log'] if sensitive else [], timeout=True)
                self.assertEqual(result, 124)
                self.assertNotIn(CANARY, output + (Path(directory) / 'fixture-run.json').read_text())
                path = Path(directory) / 'fixture-run.sensitive.json'
                self.assertEqual(path.exists(), sensitive)
                if sensitive:
                    self.assertEqual(json.loads(path.read_text())['stderr'], CANARY)

    def test_malformed_and_unknown_fields_never_escape_projection(self):
        payload = '\n'.join(json.dumps(e) for e in [None, [], 7, {'type': []},
            {'type': 'item.completed', 'item': None},
            {'type': 'item.completed', 'item': {'type': [], 'status': []}},
            {'type': 'item.completed', 'item': {'type': 'reasoning_summary', 'text': CANARY}},
            {'type': 'turn.completed', 'usage': {'input_tokens': True, 'output_tokens': CANARY}},
            {'type': CANARY, 'item': {'type': 'command_execution'}}])
        events = [runner.minimal_event(e) for e in runner.observable_events(payload)]
        self.assertNotIn(CANARY, json.dumps(events))
        self.assertEqual(len(events), 3)
        self.assertEqual(events[-1]['usage'], {})

    def test_valid_session_id_retained_but_untrusted_version_omitted(self):
        session = '12345678-1234-4234-8234-123456789abc'
        self.assertEqual(runner.thread_identity([{'type': 'thread.started', 'thread_id': session}]), session)
        self.assertIsNone(runner.thread_identity([{'type': 'thread.started', 'thread_id': CANARY}]))
        with tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
            _, output = self.invoke(self.workspace(directory), [], version=CANARY)
            report = json.loads((Path(directory) / 'fixture-run.json').read_text())
            self.assertEqual(report['codex_version'], 'unknown')
            self.assertNotIn(CANARY, output)

    def test_reports_do_not_follow_symlinks_or_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'target.json'
            target.write_text('keep')
            with self.assertRaises(FileExistsError):
                runner.write_private_report(target, {})
            self.assertEqual(target.read_text(), 'keep')
            link = Path(directory) / 'link.json'
            try:
                link.symlink_to(target)
            except OSError:
                return  # Windows may not permit symlinks; overwrite case ran.
            with self.assertRaises(FileExistsError):
                runner.write_private_report(link, {})
            self.assertEqual(target.read_text(), 'keep')

    def test_unsafe_output_label_is_rejected_before_host_launch(self):
        with tempfile.TemporaryDirectory(prefix='littlepowers-live.') as directory:
            with self.assertRaises(SystemExit):
                self.invoke(self.workspace(directory), [], extra=['--label', '../escape'])


if __name__ == '__main__':
    unittest.main()
