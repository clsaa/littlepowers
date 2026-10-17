"""Synthetic acceptance coverage. No host/model/network/private session access."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import littlepowers_efficiency as eff

NOW = '2000-01-01T00:00:01Z'
SCOPE = dict(session='synthetic-session', task='synthetic-task', target='synthetic-target',
             environment='synthetic-environment-v1', observer_version='v1', contract_digest=None)
RECEIPT = dict(ref='evidence/synthetic.json', sha256='sha256:' + 'a' * 64, saved=True, upstream_complete=True)


def report():
    return dict(schema_version=1, scope=copy.deepcopy(SCOPE), result='PASS', observed_at=NOW,
                source_updated_at=NOW, source_freshness='fresh', required=['C1', 'C2'],
                checks=[dict(id='C1', result='PASS'), dict(id='C2', result='PASS')], findings=[],
                evidence=[copy.deepcopy(RECEIPT)], visual_refs=[])


def observation():
    return dict(schema_version=1, required_fields=['state', 'version', 'enabled'], entities=[
        dict(id='button-a', fields=dict(state='ready', version=1, enabled=True, name='Run')),
        dict(id='button-b', fields=dict(state='ready', version=1, enabled=False, name='Run'))])


def observe(r=None, o=None, cursor=None, **kwargs):
    args = dict(now=NOW, max_source_age_seconds=10, max_cursor_age_seconds=100,
                verified_evidence=[RECEIPT], budget_chars=8000)
    args.update(kwargs)
    return eff.observe(r or report(), observation() if o is None else o, cursor, **args)


def ack(result):
    return eff.acknowledge(result['candidate_cursor'], result['events'][-1]['id'], expected_scope=SCOPE,
                           now=NOW, max_age_seconds=100, verified_evidence=[RECEIPT])


class SummaryTests(unittest.TestCase):
    def test_eff01_coverage_and_critical_traceability(self):
        r = report()
        r['findings'] = [dict(id='F1', check_id='C1', severity='critical', message='broken')]
        s = eff.pack(r, 8000)
        self.assertEqual(s['result'], 'FAIL')
        self.assertEqual(s['findings'], r['findings'])
        self.assertEqual(s['required'], ['C1', 'C2'])
        self.assertEqual(s['coverage'], dict(required=2, checked=2, unknown=0))
        self.assertEqual(s['artifact_refs'], [RECEIPT['ref']])

    def test_eff02_budget_keeps_errors_visual_and_explicit_reads(self):
        r = report()
        r['visual_refs'] = [RECEIPT['ref']]
        r['findings'] = [dict(id='F1', check_id='C1', severity='critical', message='failure'),
                         dict(id='F2', check_id='C2', severity='info', message='detail')]
        s = eff.pack(r, 10)
        self.assertEqual([f['id'] for f in s['findings']], ['F1'])
        self.assertTrue(s['summary_has_more'])
        self.assertTrue(s['budget_exceeded'])
        self.assertTrue(s['evidence_complete'])
        self.assertEqual(s['visual_refs'], r['visual_refs'])
        self.assertEqual(s['supplemental_reads'][0]['finding_ids'], ['F2'])

    def test_check_details_never_silently_omitted(self):
        r = report()
        r['checks'][0]['details'] = 'full details retained in original'
        self.assertTrue(eff.pack(r, 8000)['summary_has_more'])

    def test_incomplete_and_failed_save_cannot_pass(self):
        for change in ('saved', 'upstream_complete'):
            r = report()
            r['evidence'][0][change] = False
            self.assertEqual(eff.pack(r, 8000)['result'], 'ERROR')
        r = report()
        r['evidence'] = []
        self.assertFalse(eff.pack(r, 8000)['evidence_complete'])

    def test_missing_unknown_and_unplanned_checks(self):
        r = report()
        r['checks'].pop()
        self.assertEqual(eff.pack(r, 8000)['unknown_checks'], ['C2'])
        self.assertEqual(eff.pack(r, 8000)['result'], 'UNKNOWN')
        r['checks'].append(dict(id='alien', result='PASS'))
        with self.assertRaises(ValueError):
            eff.pack(r, 8000)

    def test_malformed_structure(self):
        for field in report():
            r = report()
            del r[field]
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                eff.pack(r, 8000)


class ObservationTests(unittest.TestCase):
    def test_eff03_baseline_reorder_clock_and_no_ledger_writes(self):
        first = observe()
        self.assertEqual(first['events'][0]['kind'], 'baseline')
        c = ack(first)
        o = observation()
        o['entities'].reverse()
        o['sampling_clock'] = 999
        r = report()
        r['observed_at'] = '2000-01-01T00:00:02Z'
        same = observe(r, o, c, now='2000-01-01T00:00:02Z')
        self.assertEqual(same['action'], 'continue')
        self.assertEqual(same['events'], [])
        self.assertNotIn('ledger', eff.canonical(same))
        self.assertEqual(c['next_sequence'], same['candidate_cursor']['next_sequence'])

    def test_eff04_swaps_versions_additions_removals(self):
        c = ack(observe())
        for variant in ('swap', 'version', 'add', 'delete', 'optional_delete'):
            o = observation()
            if variant == 'swap':
                for entity in o['entities']:
                    entity['fields']['enabled'] = not entity['fields']['enabled']
            elif variant == 'version':
                o['entities'][0]['fields']['version'] = 2
            elif variant == 'add':
                o['entities'].append(dict(id='new', fields=dict(state='new', version=1, enabled=True)))
            elif variant == 'delete':
                o['entities'].pop()
            else:
                del o['entities'][0]['fields']['name']
            result = observe(o=o, cursor=c)
            with self.subTest(variant=variant):
                self.assertEqual(result['events'][0]['kind'], 'changed')
                self.assertTrue(result['events'][0]['summary']['changed_fields'])

    def test_eff05_missing_failure_empty_and_recovery(self):
        c = ack(observe())
        for variant in ('missing', 'failed', 'null', 'duplicate', 'stale', 'unknown', 'critical', 'action'):
            o, r = observation(), report()
            if variant == 'missing':
                del o['entities'][0]['fields']['enabled']
            elif variant == 'failed':
                del o['entities']
            elif variant == 'null':
                o['entities'] = None
            elif variant == 'duplicate':
                o['entities'].append(o['entities'][0])
            elif variant == 'stale':
                r['source_updated_at'] = '1999-12-31T23:00:00Z'
            elif variant == 'unknown':
                r['checks'][0]['result'] = 'UNKNOWN'
            elif variant == 'critical':
                r['findings'] = [dict(id='F1', check_id='C1', severity='critical', message='bad')]
            else:
                r['result'] = 'ACTION_REQUIRED'
            broken = observe(r, o, c)
            with self.subTest(variant=variant):
                self.assertEqual(broken['events'][0]['kind'], 'error')
                self.assertEqual(observe(cursor=ack(broken))['events'][0]['kind'], 'recovered')
        empty = observation()
        empty['entities'] = []
        self.assertEqual(observe(o=empty)['events'][0]['kind'], 'baseline')

    def test_eff08_periodic_report_not_suppressed(self):
        self.assertEqual(observe(cursor=ack(observe()), report_due=True)['events'][0]['kind'], 'periodic')

    def test_stale_wait_and_changed_required_schema_are_not_unchanged(self):
        r = report()
        r['result'] = 'WAIT'
        r['source_freshness'] = 'stale'
        self.assertEqual(observe(r)['events'][0]['summary']['result'], 'UNKNOWN')
        o = observation()
        o['required_fields'] = ['state', 'version']
        result = observe(o=o, cursor=ack(observe()))
        self.assertEqual(result['events'][0]['summary']['result'], 'ERROR')
        r = report()
        r['observed_at'] = '2000-01-02T00:00:00Z'
        with self.assertRaises(ValueError):
            observe(r)

    def test_unknown_source_time_is_explicit_unknown(self):
        r = report()
        r['source_updated_at'] = None
        r['source_freshness'] = 'unknown'
        result = observe(r)
        self.assertEqual(result['events'][0]['summary']['result'], 'UNKNOWN')
        ack(result)
        r['source_freshness'] = 'fresh'
        with self.assertRaises(ValueError):
            observe(r)

    def test_scope_not_mutated_by_caller(self):
        r = report()
        result = observe(r)
        r['scope']['task'] = 'other'
        self.assertEqual(result['candidate_cursor']['scope'], SCOPE)


class CursorTests(unittest.TestCase):
    def restore(self, c, **kwargs):
        args = dict(expected_scope=SCOPE, now=NOW, max_age_seconds=100, verified_evidence=[RECEIPT])
        args.update(kwargs)
        return eff.restore(c, **args)

    def test_eff06_integrity_scope_age_and_evidence(self):
        c = ack(observe())
        broken = copy.deepcopy(c)
        broken['health'] = 'error'
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.restore(broken)
        for key in SCOPE:
            expected = dict(SCOPE)
            expected[key] = 'sha256:' + 'f' * 64 if key == 'contract_digest' else 'different'
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.restore(c, expected_scope=expected)
        with self.assertRaisesRegex(ValueError, 'expired'):
            self.restore(c, now='2000-01-01T01:00:00Z')
        with self.assertRaisesRegex(ValueError, 'evidence'):
            self.restore(c, verified_evidence=[])
        c['last_observed']['semantic']['entities'] = []
        with self.assertRaises(ValueError):
            self.restore(eff.seal(c))

    def test_eff07_saved_before_report_replays_pending_not_business_write(self):
        first = observe()
        saved = json.loads(eff.canonical(first['candidate_cursor']))
        recovered = observe(cursor=saved)
        self.assertEqual(recovered['events'], first['events'])
        self.assertTrue(recovered['delivery_uncertain'])
        self.assertEqual(recovered['candidate_cursor']['last_acknowledged'], 0)
        self.assertNotIn('commands', eff.canonical(recovered))
        confirmed = ack(recovered)
        self.assertEqual(confirmed['pending_events'], [])
        self.assertEqual(observe(cursor=confirmed)['action'], 'continue')
        with self.assertRaises(ValueError):
            eff.acknowledge(confirmed, first['events'][0]['id'], expected_scope=SCOPE, now=NOW,
                            max_age_seconds=100, verified_evidence=[RECEIPT])

    def test_missing_pending_event_rejected_even_with_new_checksum(self):
        c = observe()['candidate_cursor']
        c['pending_events'] = []
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.restore(eff.seal(c))

    def test_cursor_large_sequence_and_missing_summary_fields_fail_closed(self):
        c = observe()['candidate_cursor']
        c['next_sequence'] = 9007199254740991
        with self.assertRaises(ValueError):
            self.restore(eff.seal(c))
        c = observe()['candidate_cursor']
        del c['pending_events'][0]['summary']['coverage']
        with self.assertRaises(ValueError):
            self.restore(eff.seal(c))

    def test_canonical_unicode_and_numeric_rules(self):
        self.assertEqual(eff.digest({'é':1, 'a':2}), eff.digest({'a':2, 'é':1}))
        for v in (float('nan'), 1.5, 2**54, '\ud800'):
            with self.assertRaises((ValueError, UnicodeError)):
                eff.canonical(v)
        self.assertNotEqual(eff.digest({'v': True}), eff.digest({'v': 1}))


class PolicyTests(unittest.TestCase):
    def decision(self, **kwargs):
        args = dict(now_ms=100, deadline_ms=200, report_deadline_ms=180, observation_timeout_ms=90,
                    cancelled=False, capabilities=dict(bounded_wait=True, cancel=True, reuse_handle=True))
        args.update(kwargs)
        return eff.batch_decision(**args)

    def test_eff08_limits_cancel_report(self):
        self.assertEqual(self.decision()['timeout_ms'], 80)
        self.assertEqual(self.decision(cancelled=True)['reason'], 'cancelled')
        self.assertEqual(self.decision(now_ms=181)['reason'], 'periodic_report_due')
        self.assertEqual(self.decision(deadline_ms=90)['reason'], 'batch_deadline')

    def test_eff09_no_automatic_retry_or_repair_authority(self):
        for code in ('syntax', 'argument', 'binding', 'network', 'pending', 'unknown', 'permission'):
            result = eff.classify_error(dict(code=code, host_retried=True))
            self.assertFalse(result['automatic_retry'])
        self.assertEqual(eff.classify_error(dict(code='pending', message='SyntaxError'))['category'], 'business_wait')
        self.assertEqual(eff.classify_error(dict(message='SyntaxError'))['category'], 'deterministic')
        self.assertIn('host_retry', eff.classify_error(dict(code='network', host_retried=True))['next'])

    def test_eff10_explicit_degradation(self):
        self.assertEqual(self.decision(capabilities=dict(bounded_wait=False, cancel=False, reuse_handle=False))['action'], 'degraded')

    def test_eff11_task_isolation(self):
        r = report()
        r['scope']['task'] = 'other'
        with self.assertRaisesRegex(ValueError, 'scope'):
            observe(r=r, cursor=ack(observe()))

    def test_eff12_core_import_has_no_file_tool_or_network_dependencies(self):
        import ast
        tree = ast.parse((ROOT / 'scripts/littlepowers_efficiency.py').read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(x.name for x in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module)
        self.assertLessEqual(imported, {'__future__','copy','hashlib','json','re','sys','datetime'})

    def test_cli_json_scalars_return_structured_error(self):
        for raw in ('null', 'true', 'false', '1', '"text"'):
            with self.subTest(raw=raw):
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/littlepowers_efficiency.py')],
                                        input=raw, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                error = json.loads(result.stdout)
                self.assertEqual(error['result'], 'ERROR')
                self.assertFalse(error['evidence_complete'])
                self.assertEqual(result.stderr, '')

    def test_cli_duplicate_keys_and_malformed_input_fail_closed(self):
        for raw in ('{}', '{"operation":"pack","operation":"observe"}', '[]', '{"bad":NaN}'):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/littlepowers_efficiency.py')],
                                    input=raw, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['result'], 'ERROR')


if __name__ == '__main__':
    unittest.main()
