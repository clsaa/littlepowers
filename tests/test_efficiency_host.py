import asyncio
import copy
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
import efficiency_host_fixture as host
from test_efficiency import observe, report, observation, SCOPE, NOW

CAPS = dict(bounded_wait=True, cancel=True, reuse_handle=True)


class HostTests(unittest.IsolatedAsyncioTestCase):
    async def run_batch(self, observer, **kwargs):
        args = dict(duration_ms=120, observation_timeout_ms=30, report_after_ms=100,
                    interval_ms=10, cancel=asyncio.Event(), capabilities=CAPS)
        args.update(kwargs)
        return await host.bounded_batch(observer, 'existing-synthetic-handle', **args)

    async def test_eff08_slow_observation_really_cancelled(self):
        stopped = asyncio.Event()
        async def slow(handle):
            self.assertEqual(handle, 'existing-synthetic-handle')
            try:
                await asyncio.sleep(5)
            finally:
                stopped.set()
        start = time.monotonic()
        result = await self.run_batch(slow)
        self.assertEqual(result['reason'], 'observation_timeout')
        self.assertTrue(stopped.is_set())
        self.assertLess(time.monotonic() - start, .5)

    async def test_eff08_batch_deadline_and_periodic_report_bound_slow_tool(self):
        async def slow(handle):
            await asyncio.sleep(5)
        for expected, values in [('batch_deadline', dict(duration_ms=30, report_after_ms=100)),
                                 ('periodic_report_due', dict(duration_ms=100, report_after_ms=30))]:
            start = time.monotonic()
            result = await self.run_batch(slow, observation_timeout_ms=1000, **values)
            self.assertEqual(result['reason'], expected)
            self.assertLess(time.monotonic() - start, .5)

    async def test_eff08_external_cancellation_during_read(self):
        cancel = asyncio.Event()
        stopped = asyncio.Event()
        async def slow(handle):
            try:
                await asyncio.sleep(5)
            finally:
                stopped.set()
        asyncio.get_running_loop().call_later(.02, cancel.set)
        result = await self.run_batch(slow, cancel=cancel, observation_timeout_ms=1000)
        self.assertEqual(result['reason'], 'cancelled')
        self.assertTrue(stopped.is_set())

    async def test_eff08_same_state_still_reports_on_schedule_and_reuses_handle(self):
        handles = []
        async def same(handle):
            handles.append(handle)
            return dict(action='continue')
        result = await self.run_batch(same, report_after_ms=35)
        self.assertEqual(result['reason'], 'periodic_report_due')
        self.assertGreater(len(handles), 1)
        self.assertEqual(set(handles), {'existing-synthetic-handle'})

    async def test_eff10_missing_capability_never_calls_tool(self):
        async def unavailable(handle):
            self.fail('tool invoked without capabilities')
        result = await self.run_batch(unavailable, capabilities=dict(bounded_wait=False, cancel=False, reuse_handle=False))
        self.assertEqual(result['action'], 'degraded')
        self.assertEqual(result['calls'], 0)

    async def test_error_event_returns_at_first_sample(self):
        async def critical(handle):
            return dict(action='report', result='ERROR')
        result = await self.run_batch(critical)
        self.assertEqual(result['reason'], 'event')
        self.assertEqual(result['calls'], 1)

    async def test_independent_read_failure_does_not_skip_other_results(self):
        async def good():
            return 'synthetic'
        async def bad():
            raise ValueError('synthetic')
        result = await host.independent_reads([good, bad, good])
        self.assertEqual([r['exit_status'] for r in result], [0, 1, 0])


class PersistenceTests(unittest.TestCase):
    def test_eff07_atomic_save_then_crash_before_report_preserves_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = host.atomic_save(root / 'evidence.json', {'synthetic': True})
            r = report()
            r['evidence'] = [receipt]
            result = observe(r, verified_evidence=[receipt])
            host.atomic_save(root / 'cursor.json', result['candidate_cursor'])
            # The host interrupted here, BEFORE reporting/acknowledging.
            import json
            loaded = json.loads((root / 'cursor.json').read_text())
            verified = host.verify_receipt(root / 'evidence.json', receipt)
            restored = observe(r, cursor=loaded, verified_evidence=[verified])
            self.assertTrue(restored['delivery_uncertain'])
            self.assertEqual(restored['events'], result['events'])
            self.assertEqual(restored['candidate_cursor']['last_acknowledged'], 0)
            (root / 'evidence.json').write_text('changed')
            with self.assertRaises(ValueError):
                host.verify_receipt(root / 'evidence.json', receipt)

    def test_eff01_eff02_saved_original_and_visual_remain_traceable(self):
        import base64
        import hashlib
        import json
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = dict(checks=[dict(id='C1', result='FAIL'), dict(id='C2', result='PASS')],
                       findings=[dict(id='F1', check_id='C1', severity='critical', message='synthetic failure'),
                                 dict(id='F2', check_id='C2', severity='info', message='synthetic detail')])
            receipt = host.atomic_save(root / 'original.json', raw)
            png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aXioAAAAASUVORK5CYII=')
            (root / 'visual.png').write_bytes(png)
            visual = dict(ref='visual.png', sha256='sha256:'+hashlib.sha256(png).hexdigest(),
                          saved=True, upstream_complete=True)
            r = report()
            r.update(raw)
            r['evidence'] = [receipt, visual]
            r['visual_refs'] = ['visual.png']
            summary = host.eff.pack(r, 20)
            saved = json.loads((root / 'original.json').read_text())
            self.assertEqual(summary['checks'], saved['checks'])
            self.assertEqual(summary['findings'], [f for f in saved['findings'] if f['severity']=='critical'])
            self.assertEqual(summary['visual_refs'], ['visual.png'])
            self.assertEqual(summary['supplemental_reads'][0]['artifact_refs'], ['original.json', 'visual.png'])
            self.assertEqual(host.verify_receipt(root / 'visual.png', visual), visual)

    def test_failed_replace_keeps_previous_cursor_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cursor.json'
            host.atomic_save(path, {'previous': True})
            with patch.object(host.os, 'replace', side_effect=OSError('synthetic failure')):
                with self.assertRaises(OSError):
                    host.atomic_save(path, {'next': True})
            self.assertEqual(path.read_text(), '{"previous":true}')
            self.assertEqual([p.name for p in path.parent.iterdir()], ['cursor.json'])


if __name__ == '__main__':
    unittest.main()
