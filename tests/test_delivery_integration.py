"""Exercise delivery proposals against unchanged real Outcome Lock gates."""
import copy
import hashlib
import json
import unittest

import test_delivery as sample
import test_outcome_gates as gates
import littlepowers_delivery as delivery
import littlepowers_state as state


class DeliveryIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = gates.OutcomeGateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root = self.fixture.root

    def bundle(self, host='codex'):
        p = sample.profile()
        p['checks'] = p['checks'][:1]
        p['checks'][0]['inputs'] = ['implementation.py']
        ctx = sample.context(p)
        ctx['required_claims'] = ['stored-result']
        # Capture BEFORE the assertion and persist actual fixture evidence.
        ctx['current']['api']['inputs'] = state.capture_verification_inputs(
            self.root, files=['implementation.py'], absent=[])
        ctx['current']['api']['environment'] = host + ':fixture-runtime'
        self.assertEqual((self.root / 'implementation.py').read_text(), 'value = 1\n')
        proof = self.root / 'artifacts/evidence/delivery.json'
        proof.write_text(json.dumps({'check': 'api', 'value': 1, 'passed': True}))
        row = sample.receipt(p['checks'][0], ctx)
        row['evidence'] = [dict(ref='artifacts/evidence/delivery.json',
            sha256='sha256:' + hashlib.sha256(proof.read_bytes()).hexdigest(),
            saved=True, upstream_complete=True)]
        ctx['latest_attempts'] = {'api': row['attempt_id']}
        ctx['verified_evidence'] = copy.deepcopy(row['evidence'])
        return p, ctx, row

    def evidence(self, rows, **verdicts):
        record = gates.verification_record(**verdicts)
        record['inputs'] = delivery.merge_inputs(rows)
        self.fixture.evidence_path.write_text(gates.block('verification', record))

    def finish(self, current):
        return state.command_finish(self.fixture.writer(current), self.root, 'complete')

    def test_reused_original_inputs_pass_existing_gates_without_helper_writes(self):
        current = self.fixture.ready_for_verify()
        p, ctx, row = self.bundle()
        before = state.state_path(self.root).read_bytes()
        self.assertEqual(delivery.select(p, ctx, [row])['reuse_candidates'], ['api'])
        self.evidence([row])
        self.assertEqual(state.state_path(self.root).read_bytes(), before)
        current = self.fixture.record_verification(current)
        self.assertEqual(self.finish(current)['status'], 'complete')

    def test_stale_original_cannot_be_laundered_through_union(self):
        current = self.fixture.ready_for_verify()
        p, ctx, row = self.bundle()
        (self.root / 'implementation.py').write_text('value = 2\n')
        ctx['current']['api']['inputs'] = state.capture_verification_inputs(
            self.root, files=['implementation.py'], absent=[])
        self.assertEqual(delivery.select(p, ctx, [row])['run'], ['api'])
        self.evidence([row])  # Even a coordinator ignoring the proposal stays blocked.
        before = state.state_path(self.root).read_bytes()
        with self.assertRaisesRegex(state.StateError, 'inputs changed'):
            self.fixture.record_verification(current)
        self.assertEqual(state.state_path(self.root).read_bytes(), before)

    def test_proposal_does_not_clear_failed_acceptance(self):
        current = self.fixture.ready_for_verify()
        p, ctx, row = self.bundle()
        self.assertEqual(delivery.select(p, ctx, [row])['status'], 'ready')
        self.evidence([row], second_status='fail', outcome_fidelity='fail')
        current = self.fixture.record_verification(current)
        before = state.state_path(self.root).read_bytes()
        with self.assertRaises(state.StateError):
            self.finish(current)
        self.assertEqual(state.state_path(self.root).read_bytes(), before)

    def test_ready_selection_cannot_bypass_unapproved_plan(self):
        current = self.fixture.bind()
        p, ctx, row = self.bundle()
        self.assertEqual(delivery.select(p, ctx, [row])['status'], 'ready')
        with self.assertRaises(state.StateError):
            self.fixture.validate_plan(current, approve=False)

    def test_four_hosts_use_same_protocol_but_environment_change_invalidates(self):
        for host in ('codex', 'claude-code', 'qoder', 'opencode'):
            with self.subTest(host=host):
                p, ctx, row = self.bundle(host)
                self.assertTrue(delivery.reuse(p, ctx, row)['reusable'])
                ctx['current']['api']['environment'] += ':new-runtime'
                self.assertFalse(delivery.reuse(p, ctx, row)['reusable'])

    def test_union_rejects_mixed_projects_failed_and_incomplete_receipts(self):
        _, _, original = self.bundle()
        for key, value in (('project_id', 'another-project'), ('exit_code', 1),
                           ('finished_at', None), ('result', 'timeout')):
            row = copy.deepcopy(original)
            row[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                delivery.merge_inputs([original, row])

    def test_union_does_not_weaken_existing_256_file_limit(self):
        _, _, original = self.bundle()
        rows = []
        for start in (0, 200):
            row = copy.deepcopy(original)
            row['fingerprint']['inputs']['files'] = [
                dict(path=f'input-{index}.py', sha256=sample.digest(index))
                for index in range(start, start + 200)]
            rows.append(row)
        with self.assertRaises(state.StateError):
            delivery.merge_inputs(rows)

    def test_live_evidence_cannot_bypass_baseline_or_new_input_gate(self):
        current = self.fixture.ready_for_verify()
        _, _, row = self.bundle()
        self.evidence([row], outcome_fidelity='blocked', blockers=['baseline unavailable'])
        current = self.fixture.record_verification(current)
        with self.assertRaises(state.StateError):
            self.finish(current)


if __name__ == '__main__':
    unittest.main()
