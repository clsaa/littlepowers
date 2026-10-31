"""Behavioral tests for delivery selection, receipts and bounded learning."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import littlepowers_delivery as delivery
from littlepowers_efficiency import digest

NOW = '2026-10-31T00:00:10Z'
PROBLEM = dict(ref='evidence/problem.json', sha256=digest('problem'), saved=True, upstream_complete=True)
PROOF = dict(ref='evidence/trial.json', sha256=digest('trial'), saved=True, upstream_complete=True)


def check(key, boundary, claim, *, mandatory=False, stages=None, cost=10):
    return dict(id=key, version='1', command='python -m unittest ' + key, covers=[claim],
                boundaries=[boundary], requires=['python'], mandatory=mandatory,
                inputs=[key + '.py'], samples_ms=[] if cost is None else [cost],
                stages=stages or ['development', 'integration', 'release'],
                live=False, max_age_seconds=None)


def profile():
    return dict(profile_version=1, project_id='example', revision=0,
                boundaries=[dict(id='api', consumers=['ui'], complete=True),
                            dict(id='ui', consumers=[], complete=True),
                            dict(id='docs', consumers=[], complete=True)],
                checks=[check('api', 'api', 'stored-result'), check('ui', 'ui', 'user-goal', cost=50),
                        check('release', 'api', 'package', stages=['release'], cost=500)],
                improvements=[])


def fingerprint(check):
    return dict(check_digest=delivery.check_digest(check), acceptance_digest=digest(check['covers']),
                inputs=dict(mode='files', manual_reason=None,
                            files=[dict(path=p, sha256=digest(p)) for p in check['inputs']]),
                environment='python-local', data='fixture-v1', permissions='local',
                inventory='declared-input-membership-v1', complete=True)


def context(p=None):
    p = p or profile()
    return dict(project_id=p['project_id'], workflow_id='current-workflow', profile_digest=digest(p),
                stage='development', required_claims=['stored-result', 'user-goal'], required_checks=[],
                fresh_checks=[], changed_boundaries=['api'], impact_complete=True, tools=['python'],
                now=NOW, current={c['id']: fingerprint(c) for c in p['checks']},
                latest_attempts={}, verified_evidence=[])


def receipt(c, ctx, *, attempt='attempt-1', result='pass'):
    proof = dict(ref='evidence/' + c['id'] + '.json', sha256=digest(c['id']),
                 saved=True, upstream_complete=True)
    return dict(receipt_version=1, project_id=ctx['project_id'], workflow_id='previous-workflow',
                check_id=c['id'], attempt_id=attempt, fingerprint=copy.deepcopy(ctx['current'][c['id']]),
                captured_at='2026-10-31T00:00:00Z', started_at='2026-10-31T00:00:01Z',
                finished_at='2026-10-31T00:00:02Z', result=result, exit_code=0 if result == 'pass' else 1,
                duration_ms=10, evidence=[proof], supersedes=[])


def saved(p, ctx):
    rows = [receipt(c, ctx) for c in p['checks']]
    ctx['latest_attempts'] = {r['check_id']: r['attempt_id'] for r in rows}
    ctx['verified_evidence'] = [e for r in rows for e in r['evidence']]
    return rows


def candidate(category='testing'):
    return dict(id='I1', revision=1, state='candidate', category=category,
                problem='Repeated preparation or late discovery', hypothesis='Move the relevant check earlier',
                change=dict(kind='reorder_checks' if category == 'testing' else 'add_preflight',
                            description='Use the same required checks at the relevant boundary'),
                fallback='current approved conservative strategy', conditions={'boundary': 'api'},
                policy_digest=digest('current-approval'), evidence=[copy.deepcopy(PROBLEM)],
                trial=None, history=[])


def learning_context(p):
    return dict(project_id=p['project_id'], workflow_id='trial-workflow', profile_digest=digest(p),
                policy_digest=digest('current-approval'), conditions={'boundary': 'api'},
                write_authorized=True, scope_unchanged=True, acceptance_unchanged=True,
                reversible=True, invalidated=False, now=NOW, verified_evidence=[PROBLEM, PROOF])


def apply_proposal(p, result):
    # Test-only coordinator: the production helper cannot persist its own proposal.
    if result['record'] is not None:
        assert result['expected_profile_digest'] == digest(p)
        row = result['record']
        p['improvements'] = [r for r in p['improvements'] if r['id'] != row['id']] + [row]
        p['revision'] += 1


def trial_profile(category='testing'):
    p = profile()
    apply_proposal(p, delivery.learn(p, learning_context(p),
        dict(kind='propose', id='I1', expected_revision=0, candidate=candidate(category))))
    apply_proposal(p, delivery.learn(p, learning_context(p), dict(kind='start_trial', id='I1',
        expected_revision=1, trial=dict(metric='repeated_work', direction='decrease', baseline=10,
        minimum_gain=1, invariants=['coverage', 'defect_detection'], stop_condition='any regression'))))
    return p


def assessment(p, **updates):
    row = p['improvements'][0]
    obs = dict(trial_token=row['trial']['token'], workflow_id='trial-workflow', observed_at=NOW,
               result='pass', value=5, invariants={'coverage': True, 'defect_detection': True}, evidence=[PROOF])
    obs.update(updates)
    return dict(kind='assess', id='I1', expected_revision=row['revision'], observation=obs)


class SelectionTests(unittest.TestCase):
    def test_affected_consumers_and_stage_without_full_suite(self):
        p, ctx = profile(), context()
        result = delivery.select(p, ctx, [])
        self.assertEqual(result['run'], ['api', 'ui'])
        self.assertEqual(result['not_applicable'], ['release'])
        self.assertEqual(result['affected_boundaries'], ['api', 'ui'])
        self.assertEqual(result['status'], 'ready')

    def test_mandatory_and_current_required_cannot_be_optimized_away(self):
        p = profile()
        p['checks'][2]['mandatory'] = True
        ctx = context(p)
        self.assertIn('release', delivery.select(p, ctx, [])['run'])
        ctx['required_checks'] = ['missing']
        self.assertEqual(delivery.select(p, ctx, [])['status'], 'blocked')

    def test_valid_reuse_and_changed_inputs_only_invalidate_affected_check(self):
        p, ctx = profile(), context()
        rows = saved(p, ctx)
        ctx['current']['api']['inputs']['files'][0]['sha256'] = digest('new implementation')
        result = delivery.select(p, ctx, rows)
        self.assertEqual(result['run'], ['api'])
        self.assertEqual(result['reuse_candidates'], ['ui'])
        self.assertTrue(delivery.reuse(p, ctx, rows[1])['reusable'])

    def test_each_context_and_evidence_dimension_invalidates(self):
        for dimension in ('environment', 'data', 'permissions', 'inventory', 'acceptance_digest', 'complete'):
            p, ctx = profile(), context()
            rows = saved(p, ctx)
            ctx['current']['api'][dimension] = False if dimension == 'complete' else digest('changed')
            with self.subTest(dimension=dimension):
                self.assertIn('api', delivery.select(p, ctx, rows)['run'])
        p, ctx = profile(), context()
        rows = saved(p, ctx)
        ctx['verified_evidence'] = []
        self.assertEqual(delivery.select(p, ctx, rows)['reuse_candidates'], [])

    def test_new_input_or_consumer_cannot_hide_behind_old_hashes(self):
        p, ctx = profile(), context()
        rows = saved(p, ctx)
        ctx['current']['api']['inputs']['files'].append(dict(path='new.py', sha256=digest('new')))
        self.assertIn('api', delivery.select(p, ctx, rows)['run'])
        ctx['changed_boundaries'].append('new-consumer')
        result = delivery.select(p, ctx, rows)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['reuse_candidates'], [])

    def test_unknown_impact_and_missing_capabilities_are_not_waivers(self):
        for change in ('incomplete', 'boundary', 'tool', 'coverage'):
            p, ctx = profile(), context()
            if change == 'incomplete': ctx['impact_complete'] = False
            if change == 'boundary':
                p['boundaries'][0]['complete'] = False
                ctx['profile_digest'] = digest(p)
            if change == 'tool': ctx['tools'] = []
            if change == 'coverage': ctx['required_claims'].append('historical-data')
            with self.subTest(change=change):
                self.assertEqual(delivery.select(p, ctx, [])['status'], 'blocked')

    def test_requested_check_with_incomplete_graph_blocks_even_without_changes(self):
        p = profile()
        p['boundaries'][0]['complete'] = False
        ctx = context(p)
        ctx['changed_boundaries'] = []
        rows = saved(p, ctx)
        result = delivery.select(p, ctx, rows)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['reuse_candidates'], [])

    def test_failed_running_future_or_not_latest_receipts_not_reused(self):
        for change in ('fail', 'running', 'timeout', 'unknown', 'future', 'latest', 'order'):
            p, ctx = profile(), context()
            rows = saved(p, ctx)
            if change in ('fail', 'running', 'timeout', 'unknown'): rows[0]['result'] = change
            if change == 'future': rows[0]['finished_at'] = '2027-01-01T00:00:00Z'
            if change == 'latest': ctx['latest_attempts']['api'] = 'newer-failed-attempt'
            if change == 'order': rows[0]['captured_at'] = NOW
            with self.subTest(change=change):
                if change == 'order':
                    with self.assertRaises(ValueError): delivery.select(p, ctx, rows)
                else:
                    self.assertIn('api', delivery.select(p, ctx, rows)['run'])

    def test_live_expiry_and_fresh_run_mandate(self):
        p = profile()
        p['checks'][0].update(live=True, max_age_seconds=2)
        ctx = context(p)
        rows = saved(p, ctx)
        self.assertIn('api', delivery.select(p, ctx, rows)['run'])
        ctx['fresh_checks'] = ['ui']
        self.assertIn('ui', delivery.select(p, ctx, rows)['run'])
        rows[1]['workflow_id'] = ctx['workflow_id']
        self.assertIn('ui', delivery.select(p, ctx, rows)['reuse_candidates'])

    def test_cost_unknown_is_not_zero_and_profile_drift_blocks(self):
        p = profile()
        p['checks'][0]['samples_ms'] = []
        ctx = context(p)
        result = delivery.select(p, ctx, [])
        self.assertIsNone(result['estimated_run_ms'])
        self.assertEqual(result['unknown_costs'], ['api'])
        p['revision'] += 1
        with self.assertRaises(ValueError): delivery.select(p, ctx, [])

    def test_original_input_union_rejects_conflicts(self):
        p, ctx = profile(), context()
        rows = saved(p, ctx)[:2]
        merged = delivery.merge_inputs(rows)
        self.assertEqual(len(merged['files']), 2)
        rows[1]['fingerprint']['inputs']['files'] = [dict(path='api.py', sha256=digest('different'))]
        with self.assertRaises(ValueError): delivery.merge_inputs(rows)


class LearningTests(unittest.TestCase):
    def test_persisted_state_cannot_skip_promotion_or_disagree_with_history(self):
        p = trial_profile()
        p['improvements'][0]['state'] = 'active'
        with self.assertRaisesRegex(ValueError, 'history'):
            delivery.learn(p, learning_context(p), dict(kind='observe', id='I1', expected_revision=2))
        p = trial_profile()
        apply_proposal(p, delivery.learn(p, learning_context(p), assessment(p)))
        p['improvements'][0]['history'][-1]['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'promotion'):
            delivery.learn(p, learning_context(p), dict(kind='observe', id='I1', expected_revision=3))
        p = trial_profile()
        p['improvements'][0]['history'] = []
        with self.assertRaisesRegex(ValueError, 'history'):
            delivery.validate_profile(p)

    def test_planning_and_testing_complete_lifecycle(self):
        for category in ('planning', 'testing'):
            p = trial_profile(category)
            proposal = delivery.learn(p, learning_context(p), assessment(p))
            self.assertEqual(proposal['record']['state'], 'active')
            apply_proposal(p, proposal)
            result = delivery.learn(p, learning_context(p), dict(kind='observe', id='I1', expected_revision=3))
            self.assertTrue(result['apply'])
            ctx = learning_context(p)
            ctx['invalidated'] = True
            retired = delivery.learn(p, ctx, dict(kind='observe', id='I1', expected_revision=3))
            self.assertEqual(retired['record']['state'], 'retired')
            self.assertIsNotNone(retired['fallback'])
            self.assertEqual(retired['record']['history'][0]['to'], 'trial')

    def test_no_trial_or_missing_proof_cannot_promote(self):
        p = trial_profile()
        for change in (dict(result='unknown'), dict(result='running'), dict(evidence=[]), dict(value=None)):
            self.assertIsNone(delivery.learn(p, learning_context(p), assessment(p, **change))['record'])
        p['improvements'][0] = candidate()
        with self.assertRaises(ValueError): delivery.learn(p, learning_context(p),
            dict(kind='assess', id='I1', expected_revision=1, observation={}))

    def test_regression_timeout_and_negative_gain_retire(self):
        for change in (dict(result='fail'), dict(result='timeout'), dict(value=15),
                       dict(invariants={'coverage': False, 'defect_detection': True})):
            p = trial_profile()
            row = delivery.learn(p, learning_context(p), assessment(p, **change))['record']
            self.assertEqual(row['state'], 'retired')
            self.assertEqual(row['history'][-1]['evidence'], [PROOF])

    def test_stale_or_wrong_trial_observation_rejected(self):
        for change in (dict(trial_token=digest('wrong')), dict(workflow_id='other'),
                       dict(observed_at='2020-01-01T00:00:00Z')):
            p = trial_profile()
            with self.assertRaises(ValueError): delivery.learn(p, learning_context(p), assessment(p, **change))

    def test_trial_criteria_cannot_change_without_invalidating_token(self):
        p = trial_profile()
        p['improvements'][0]['trial']['baseline'] = 999
        with self.assertRaises(ValueError): delivery.learn(p, learning_context(p), assessment(p))

    def test_read_only_scope_and_policy_boundaries(self):
        for flag in ('write_authorized', 'scope_unchanged', 'acceptance_unchanged', 'reversible'):
            p = trial_profile()
            ctx = learning_context(p)
            ctx[flag] = False
            result = delivery.learn(p, ctx, assessment(p))
            self.assertFalse(result['apply'])
            self.assertIsNone(result['record'])
        p = trial_profile()
        ctx = learning_context(p)
        ctx['conditions']['boundary'] = 'unrelated'
        self.assertIsNone(delivery.learn(p, ctx, assessment(p))['record'])

    def test_recovery_revision_conflict_and_retired_non_resurrection(self):
        p = trial_profile()
        before = copy.deepcopy(p)
        ctx = learning_context(p)
        ctx['profile_digest'] = digest('stale')
        with self.assertRaises(ValueError): delivery.learn(p, ctx, assessment(p))
        self.assertEqual(p, before)
        apply_proposal(p, delivery.learn(p, learning_context(p), assessment(p, value=20)))
        self.assertFalse(delivery.learn(p, learning_context(p),
            dict(kind='observe', id='I1', expected_revision=3))['apply'])
        fresh = candidate()
        fresh['revision'] = 4
        with self.assertRaises(ValueError): delivery.learn(p, learning_context(p),
            dict(kind='propose', id='I1', expected_revision=3, candidate=fresh))


class ProtocolTests(unittest.TestCase):
    def test_profile_document_and_duplicate_keys(self):
        p = profile()
        markdown = '<!-- littlepowers:delivery-profile:v1 -->\n```json\n' + json.dumps(p) + '\n```\n<!-- /littlepowers:delivery-profile -->'
        self.assertEqual(delivery.parse_profile(markdown), p)
        with self.assertRaises(ValueError): delivery.parse_profile(markdown + markdown)
        with self.assertRaises(ValueError): delivery.parse_profile(markdown.replace('"revision": 0', '"revision": 0, "revision": 1'))

    def test_pure_operations_leave_inputs_untouched_and_do_not_execute_text(self):
        p = profile()
        p['checks'][0]['command'] = '$(touch /tmp/DO-NOT-EXECUTE-littlepowers)'
        ctx = context(p)
        before = copy.deepcopy((p, ctx))
        with patch('builtins.open', side_effect=AssertionError('filesystem access')), \
             patch('subprocess.run', side_effect=AssertionError('command execution')):
            delivery.select(p, ctx, [])
        self.assertEqual((p, ctx), before)

    def test_bounds_versions_and_duplicate_ids(self):
        for mutation in ('version', 'check', 'consumer', 'large'):
            p = profile()
            if mutation == 'version': p['profile_version'] = True
            if mutation == 'check': p['checks'].append(copy.deepcopy(p['checks'][0]))
            if mutation == 'consumer': p['boundaries'][0]['consumers'].append('unknown')
            if mutation == 'large': p['checks'] *= 50
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): delivery.validate_profile(p)

    def test_cli_structured_errors_and_size_bound(self):
        requests = ['{"operation":"select","operation":"learn"}', '{}', ' ' * (2 * 1024 * 1024 + 1)]
        p = profile()
        p['checks'][0]['inputs'] = ['../unsafe']
        requests.append(json.dumps(dict(operation='select', profile=p, context={}, receipts=[])))
        for request in requests:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/littlepowers_delivery.py')],
                                    input=request, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'invalid')
            self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
