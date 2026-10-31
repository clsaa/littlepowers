"""Disposable, real-check fixture; not a model/host certification or runtime hook."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import littlepowers_delivery as delivery
from littlepowers_efficiency import digest
from littlepowers_state import capture_verification_inputs

CLAIMS = ['historical-data', 'complete-api', 'complete-user-result']
CASES = ['cold', 'unchanged', 'ui_edit', 'ui_defect', 'ui_repair',
         'api_edit', 'api_defect', 'api_repair', 'history_defect', 'history_repair']


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def milliseconds(start):
    return (time.perf_counter_ns() - start) / 1_000_000


def read(root, name):
    return json.loads((root / name).read_text(encoding='utf-8'))


def write(root, name, data):
    # Measurement artifacts contain fractional elapsed milliseconds; protocol
    # records still pass the helper's stricter integer-only canonical validator.
    (root / name).write_text(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                      separators=(',', ':'), allow_nan=False), encoding='utf-8')


def setup(root, count):
    root.mkdir(parents=True)
    (root / 'evidence').mkdir()
    records = [dict(id=index, cents=100 + index, format='legacy' if index % 3 == 0 else 'current')
               for index in range(count)]
    write(root, 'records.json', records)
    write(root, 'api.json', dict(include_legacy=True, sort='ascending'))
    write(root, 'ui.json', dict(title='Account summary', show_total=True, show_recovery=True))
    # Include executable checker bytes in every pre-check fingerprint.
    (root / 'checker.py').write_bytes(Path(__file__).read_bytes())


def make_profile():
    p = dict(profile_version=1, project_id='delivery-eval', revision=0,
             boundaries=[dict(id='history', consumers=['api'], complete=True),
                         dict(id='api', consumers=['ui'], complete=True),
                         dict(id='ui', consumers=[], complete=True)], checks=[], improvements=[])
    for key, claim, files in (
            ('history', CLAIMS[0], ['records.json']),
            ('api', CLAIMS[1], ['records.json', 'api.json']),
            ('ui', CLAIMS[2], ['records.json', 'api.json', 'ui.json'])):
        p['checks'].append(dict(id=key, version='1', command='fixture check ' + key,
            covers=[claim], boundaries=[key], requires=['python'], mandatory=False,
            inputs=files + ['checker.py'], samples_ms=[],
            stages=['development', 'integration', 'release'], live=False, max_age_seconds=None))
    return p


def check(root, key):
    records = read(root, 'records.json')
    assert records and len({r['id'] for r in records}) == len(records), 'record identity lost'
    assert all(type(r['cents']) is int and r['cents'] >= 0 for r in records), 'historical amount invalid'
    assert {'legacy', 'current'} <= {r['format'] for r in records}, 'historical formats missing'
    expected_total = sum(r['cents'] for r in records)
    if key == 'history':
        return dict(records=len(records), formats=['legacy', 'current'])
    api = read(root, 'api.json')
    normalized = [dict(id=r['id'], cents=r['cents']) for r in records
                  if api['include_legacy'] or r['format'] != 'legacy']
    normalized.sort(key=lambda r: r['id'], reverse=api['sort'] == 'descending')
    assert len(normalized) == len(records), 'API discarded historical records'
    assert sum(r['cents'] for r in normalized) == expected_total, 'API changed total'
    if key == 'api':
        return dict(records=len(normalized), total=expected_total)
    ui = read(root, 'ui.json')
    rendered = {'title': ui['title'], 'count': len(normalized)}
    if ui['show_total']:
        rendered['total'] = sum(r['cents'] for r in normalized)
    if ui['show_recovery']:
        rendered['retry_action'] = 'reload persisted records'
    assert rendered.get('total') == expected_total, 'user cannot see the complete total'
    assert rendered.get('retry_action'), 'recovery action missing'
    return rendered


def mutate(root, case):
    if case.startswith('ui_'):
        ui = read(root, 'ui.json')
        ui.update(title='Complete account summary', show_total=case != 'ui_defect')
        write(root, 'ui.json', ui)
        return ['ui']
    if case.startswith('api_'):
        api = read(root, 'api.json')
        api.update(sort='descending', include_legacy=case != 'api_defect')
        write(root, 'api.json', api)
        return ['api']
    if case.startswith('history_'):
        rows = read(root, 'records.json')
        rows[0]['cents'] = -1 if case == 'history_defect' else 100
        write(root, 'records.json', rows)
        return ['history']
    return ['history'] if case == 'cold' else []


def context(root, profile, receipts, changed):
    current = {}
    for c in profile['checks']:
        current[c['id']] = dict(check_digest=delivery.check_digest(c),
            acceptance_digest=digest(CLAIMS),
            inputs=capture_verification_inputs(root, files=c['inputs'], absent=[]),
            environment=platform.python_version(), data='declared records.json',
            permissions='temporary-local-only', inventory=digest(sorted(c['inputs'])), complete=True)
    verified = []
    for row in receipts.values():
        for proof in row['evidence']:
            path = root / proof['ref']
            if path.is_file() and 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest() == proof['sha256']:
                verified.append(copy.deepcopy(proof))
    return dict(project_id=profile['project_id'], workflow_id='paired-run',
        profile_digest=digest(profile), stage='development', required_claims=CLAIMS,
        required_checks=[], fresh_checks=[], changed_boundaries=changed, impact_complete=True,
        tools=['python'], now=now(), current=current,
        latest_attempts={key: r['attempt_id'] for key, r in receipts.items()}, verified_evidence=verified)


def run_variant(root, variant, count=6000):
    total_start = time.perf_counter_ns()
    setup_start = time.perf_counter_ns()
    setup(root, count)
    profile = make_profile()
    setup_ms = milliseconds(setup_start)
    receipts, cases, bundle = {}, [], {}
    for name in CASES:
        case_start = time.perf_counter_ns()
        prep_start = time.perf_counter_ns()
        changed = mutate(root, name)
        ctx = context(root, profile, receipts, changed)
        captured = now()
        preparation_ms = milliseconds(prep_start)
        helper_start = time.perf_counter_ns()
        if variant == 'candidate':
            selected = delivery.select(profile, ctx, list(receipts.values()))
            assert selected['status'] == 'ready', selected
        else:
            selected = dict(run=[c['id'] for c in profile['checks']], reuse_candidates=[])
        helper_ms = milliseconds(helper_start)
        check_ms, evidence_ms = 0.0, 0.0
        for key in selected['run']:
            started = now()
            check_start = time.perf_counter_ns()
            try:
                signal = check(root, key)
                result, exit_code = 'pass', 0
            except AssertionError as exc:
                signal, result, exit_code = str(exc), 'fail', 1
            duration = milliseconds(check_start)
            check_ms += duration
            finished = now()
            evidence_start = time.perf_counter_ns()
            ref = f'evidence/{name}-{key}.json'
            payload = dict(check=key, result=result, signal=signal, exit_code=exit_code)
            write(root, ref, payload)
            proof = dict(ref=ref, sha256='sha256:' + hashlib.sha256((root / ref).read_bytes()).hexdigest(),
                         saved=True, upstream_complete=True)
            bundle[ref] = payload
            previous = receipts.get(key)
            receipts[key] = dict(receipt_version=1, project_id=profile['project_id'],
                workflow_id=ctx['workflow_id'], check_id=key, attempt_id=name + ':' + key,
                fingerprint=copy.deepcopy(ctx['current'][key]), captured_at=captured,
                started_at=started, finished_at=finished, result=result, exit_code=exit_code,
                duration_ms=round(duration), evidence=[proof],
                supersedes=[previous['attempt_id']] if previous else [])
            evidence_ms += milliseconds(evidence_start)
        recovery_start = time.perf_counter_ns()
        # Real serialization/readback, not resubmission of completed checks.
        write(root, 'receipts.json', receipts)
        receipts = read(root, 'receipts.json')
        assert all((root / e['ref']).is_file() for r in receipts.values() for e in r['evidence'])
        recovery_ms = milliseconds(recovery_start)
        cases.append(dict(case=name, phase='cold' if name == 'cold' else 'reuse',
            run=selected['run'], reused=selected['reuse_candidates'],
            covered=sorted({claim for c in profile['checks'] if c['id'] in receipts for claim in c['covers']}),
            failed=sorted(key for key, row in receipts.items() if row['result'] != 'pass'),
            receipts=copy.deepcopy(receipts), preparation_ms=preparation_ms, helper_ms=helper_ms,
            check_ms=check_ms, evidence_ms=evidence_ms, recovery_ms=recovery_ms,
            total_ms=milliseconds(case_start)))
    return dict(variant=variant, dataset_count=count, cases=cases, setup_ms=setup_ms,
        total_ms=milliseconds(total_start), check_executions=sum(len(c['run']) for c in cases),
        reused_checks=sum(len(c['reused']) for c in cases), evidence_bundle=bundle)


def learning_demo(root, baseline, candidate):
    """Evidence-driven fixture trials in two delivery areas; no model claims."""
    profile = make_profile()
    records = read(root, 'records.json')
    formats = {r['format'] for r in records}
    initial_design = {'current'}
    preflight_design = {r['format'] for r in records}  # Inspect before choosing design.
    observed = dict(required_formats=sorted(formats),
                    baseline_late_gaps=sorted(formats - initial_design),
                    preflight_late_gaps=sorted(formats - preflight_design),
                    final_designs_cover_all=True)  # Baseline repairs the discovered gap.
    initial_design.update(formats)
    observed['final_designs_cover_all'] = initial_design == preflight_design == formats
    write(root, 'evidence/preflight.json', observed)
    write(root, 'evidence/check-comparison.json', dict(baseline=baseline['check_executions'],
        candidate=candidate['check_executions'],
        same_defects=[c['failed'] for c in baseline['cases']] == [c['failed'] for c in candidate['cases']]))
    transitions = []
    for category, path, before, after, invariants in (
        ('planning', 'evidence/preflight.json', len(observed['baseline_late_gaps']),
         len(observed['preflight_late_gaps']), {'full_outcome': observed['final_designs_cover_all']}),
        ('testing', 'evidence/check-comparison.json', baseline['check_executions'],
         candidate['check_executions'], {'same_coverage': all(c['covered'] == sorted(CLAIMS)
            for c in candidate['cases']), 'same_defects': [c['failed'] for c in baseline['cases']]
            == [c['failed'] for c in candidate['cases']]})):
        proof = dict(ref=path, sha256='sha256:' + hashlib.sha256((root / path).read_bytes()).hexdigest(),
                     saved=True, upstream_complete=True)
        context_value = dict(project_id=profile['project_id'], workflow_id='learning-trial',
            profile_digest=digest(profile), policy_digest=digest(CLAIMS), conditions={'fixture': 'v1'},
            write_authorized=True, scope_unchanged=True, acceptance_unchanged=True,
            reversible=True, invalidated=False, now=now(), verified_evidence=[proof])

        def apply(event):
            context_value.update(profile_digest=digest(profile), now=now())
            proposal = delivery.learn(profile, context_value, event)
            if proposal['record'] is not None:
                assert proposal['expected_profile_digest'] == digest(profile)
                profile['improvements'] = [r for r in profile['improvements'] if r['id'] != category]
                profile['improvements'].append(proposal['record'])
                profile['revision'] += 1
            return proposal

        row = dict(id=category, revision=1, state='candidate', category=category,
            problem='Observed late gap' if category == 'planning' else 'Repeated unchanged checks',
            hypothesis='Inspect existing formats before design' if category == 'planning' else 'Reuse valid per-check evidence',
            change=dict(kind='add_preflight' if category == 'planning' else 'reuse_evidence',
                        description='Keep identical complete acceptance'),
            fallback='current conservative strategy', conditions={'fixture': 'v1'},
            policy_digest=digest(CLAIMS), evidence=[proof], trial=None, history=[])
        apply(dict(kind='propose', id=category, expected_revision=0, candidate=row))
        trial = apply(dict(kind='start_trial', id=category, expected_revision=1,
            trial=dict(metric='late_gaps' if category == 'planning' else 'check_executions',
                       direction='decrease', baseline=before, minimum_gain=1,
                       invariants=list(invariants), stop_condition='any invariant fails')))
        # Collect a NEW observation after the trial boundary, not a relabeled
        # pre-trial measurement. This is fixture work, not another model request.
        if category == 'planning':
            trial_formats = {r['format'] for r in read(root, 'records.json')}
            trial_design = set(trial_formats)
            after = len(trial_formats - trial_design)
            invariants = {'full_outcome': trial_design == formats}
            trial_payload = dict(inspected_formats=sorted(trial_formats), late_gaps=after,
                                 invariants=invariants)
        else:
            trial_result = run_variant(root / 'testing-trial', 'candidate', len(records))
            after = trial_result['check_executions']
            invariants = {'same_coverage': all(c['covered'] == sorted(CLAIMS)
                for c in trial_result['cases']), 'same_defects': [c['failed'] for c in baseline['cases']]
                == [c['failed'] for c in trial_result['cases']]}
            trial_payload = trial_result
        trial_path = f'evidence/{category}-trial.json'
        write(root, trial_path, trial_payload)
        trial_proof = dict(ref=trial_path,
            sha256='sha256:' + hashlib.sha256((root / trial_path).read_bytes()).hexdigest(),
            saved=True, upstream_complete=True)
        context_value['verified_evidence'].append(trial_proof)
        active = apply(dict(kind='assess', id=category, expected_revision=2,
            observation=dict(trial_token=trial['record']['trial']['token'], workflow_id='learning-trial',
                observed_at=now(), result='pass', value=after, invariants=invariants, evidence=[trial_proof])))
        context_value['workflow_id'] = 'next-workflow'
        use = apply(dict(kind='observe', id=category, expected_revision=3))
        # A changed acceptance policy retires the learned strategy on resume.
        context_value['policy_digest'] = digest(CLAIMS + ['new-policy'])
        retired = apply(dict(kind='observe', id=category, expected_revision=3))
        transitions.append(dict(category=category, states=['candidate', trial['record']['state'],
            active['record']['state'], retired['record']['state']], automatic_next_workflow=use['apply'],
            measured_before=before, measured_after=after, invariants=invariants,
            fallback=retired['fallback'], evidence=read(root, path), trial_evidence=trial_payload))
    return dict(level='deterministic fixture, not model design behavior', transitions=transitions)
