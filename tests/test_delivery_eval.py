"""Evaluate actual results, not keyword presence or claimed fixture pass flags."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
from delivery_benchmark import benchmark
from delivery_fixture import CASES, CLAIMS


class DeliveryEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = benchmark(runs=3, count=90)

    def test_alternating_identical_inputs_and_complete_coverage(self):
        self.assertEqual([p['order'][0] for p in self.report['pairs']], ['baseline', 'candidate', 'baseline'])
        for pair in self.report['pairs']:
            self.assertEqual([c['case'] for c in pair['candidate']['cases']], CASES)
            for old, new in zip(pair['baseline']['cases'], pair['candidate']['cases']):
                self.assertEqual(old['covered'], sorted(CLAIMS))
                self.assertEqual(new['covered'], old['covered'])
                self.assertEqual({k: r['fingerprint'] for k, r in old['receipts'].items()},
                                 {k: r['fingerprint'] for k, r in new['receipts'].items()})

    def test_actual_defects_detected_and_repairs_rerun(self):
        expected = {'ui_defect': ['ui'], 'api_defect': ['api', 'ui'],
                    'history_defect': ['api', 'history', 'ui']}
        for pair in self.report['pairs']:
            for old, new in zip(pair['baseline']['cases'], pair['candidate']['cases']):
                self.assertEqual(old['failed'], expected.get(old['case'], []))
                self.assertEqual(new['failed'], old['failed'])
                if 'repair' in new['case']:
                    self.assertTrue(new['run'])

    def test_reuse_reduces_real_execution_without_assuming_latency(self):
        for pair in self.report['pairs']:
            self.assertEqual(pair['baseline']['check_executions'], 30)
            self.assertLess(pair['candidate']['check_executions'], 30)
            self.assertEqual(len(pair['candidate']['cases'][0]['run']), 3)
            self.assertEqual(pair['candidate']['cases'][1]['run'], [])
            for variant in ('baseline', 'candidate'):
                for case in pair[variant]['cases']:
                    for key in ('preparation_ms', 'helper_ms', 'check_ms', 'evidence_ms', 'recovery_ms', 'total_ms'):
                        self.assertGreaterEqual(case[key], 0)
        self.assertIsNone(self.report['model_tokens'])
        self.assertFalse(self.report['authenticated_other_hosts'])

    def test_learning_preflight_and_testing_promote_apply_and_retire(self):
        for pair in self.report['pairs']:
            for row in pair['learning']['transitions']:
                self.assertEqual(row['states'], ['candidate', 'trial', 'active', 'retired'])
                self.assertTrue(row['automatic_next_workflow'])
                self.assertLess(row['measured_after'], row['measured_before'])
                self.assertTrue(all(row['invariants'].values()))
                self.assertEqual(row['fallback'], 'last_still_valid_strategy_or_conservative_default')


if __name__ == '__main__':
    unittest.main()
