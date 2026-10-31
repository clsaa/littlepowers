#!/usr/bin/env python3
"""Bounded delivery proposals. No filesystem, command, network or ledger access."""
from __future__ import annotations

import copy
import json
import sys

from littlepowers_efficiency import (
    HEX, MAX_BYTES, canonical, digest, evidence, integer, no_duplicates,
    require, string, strings, timestamp,
)
from littlepowers_state import StateError, normalize_verification_inputs

STAGES = {'development', 'integration', 'release'}
STATES = {'candidate', 'trial', 'active', 'retired'}
CATEGORIES = {'planning', 'design', 'implementation', 'testing', 'acceptance', 'recovery'}
SAFE_CHANGES = {'group_tasks', 'add_preflight', 'reorder_checks', 'reuse_preparation',
                'reuse_evidence', 'improve_recovery'}


def record(value, required, optional=()):
    require(isinstance(value, dict) and set(required) <= set(value)
            and set(value) <= set(required) | set(optional), 'invalid record fields')
    return value


def bounded(value):
    require(len(canonical(value).encode('utf-8')) <= MAX_BYTES, 'input exceeds 2 MiB')


def items(value, label, maximum):
    require(isinstance(value, list) and len(value) <= maximum, 'invalid ' + label)
    return value


def names(value, label, maximum=256):
    items(value, label, maximum)
    return strings(value, label)


def boolean(value, label):
    require(type(value) is bool, label + ' must be boolean')
    return value


def sha(value, label):
    require(isinstance(value, str) and HEX.fullmatch(value), 'invalid ' + label)
    return value


def evidence_rows(value):
    rows = items(value, 'evidence', 256)
    for row in rows:
        evidence(row)
    require(len({row['ref'] for row in rows}) == len(rows), 'duplicate evidence ref')
    return rows


def evidence_valid(rows, observed):
    return bool(rows) and all(row['saved'] and row['upstream_complete']
                             and row in observed for row in rows)


def check_record(value):
    record(value, {'id', 'version', 'command', 'covers', 'boundaries', 'requires',
                   'mandatory', 'inputs', 'samples_ms', 'stages', 'live', 'max_age_seconds'})
    for key in ('id', 'version', 'command'):
        string(value[key], key)
    for key in ('covers', 'boundaries', 'requires', 'inputs', 'stages'):
        names(value[key], key)
    require(value['covers'] and value['boundaries'] and value['stages'], 'empty check scope')
    require(set(value['stages']) <= STAGES, 'invalid check stage')
    boolean(value['mandatory'], 'mandatory')
    boolean(value['live'], 'live')
    for cost in items(value['samples_ms'], 'cost samples', 5):
        integer(cost, 'sample duration')
    if value['max_age_seconds'] is not None:
        integer(value['max_age_seconds'], 'max age', 1)
    # Use the existing safe path grammar; these placeholders never become evidence.
    if value['inputs']:
        normalize_verification_inputs({'mode': 'files', 'manual_reason': None,
            'files': [{'path': path, 'sha256': 'sha256:' + '0' * 64} for path in value['inputs']]})
    return value


def check_digest(check):
    check_record(check)
    return digest({key: value for key, value in check.items() if key != 'samples_ms'})


def conditions(value):
    require(isinstance(value, dict) and 0 < len(value) <= 32, 'invalid conditions')
    for key, val in value.items():
        string(key, 'condition key')
        string(val, 'condition value')
    return value


def trial_token(row, trial):
    return digest({'id': row['id'], 'conditions': row['conditions'],
                   'policy_digest': row['policy_digest'], 'change': row['change'],
                   'hypothesis': row['hypothesis'],
                   'trial': {k: v for k, v in trial.items() if k != 'token'}})


def improvement_record(value):
    record(value, {'id', 'revision', 'state', 'category', 'problem', 'hypothesis',
                   'change', 'fallback', 'conditions', 'policy_digest', 'evidence',
                   'trial', 'history'})
    for key in ('id', 'problem', 'hypothesis', 'fallback'):
        string(value[key], key)
    integer(value['revision'], 'improvement revision', 1)
    require(value['state'] in STATES and value['category'] in CATEGORIES, 'invalid learning state/category')
    record(value['change'], {'kind', 'description'})
    string(value['change']['kind'], 'change kind')
    string(value['change']['description'], 'change description')
    conditions(value['conditions'])
    sha(value['policy_digest'], 'policy digest')
    evidence_rows(value['evidence'])
    previous = None
    edges = {('candidate', 'trial'), ('trial', 'active'), ('trial', 'retired'),
             ('active', 'active'), ('active', 'retired')}
    for event in items(value['history'], 'history', 16):
        record(event, {'from', 'to', 'reason', 'at', 'evidence'})
        require((event['from'], event['to']) in edges, 'invalid history transition')
        string(event['reason'], 'history reason')
        timestamp(event['at'])
        evidence_rows(event['evidence'])
        if previous is not None:
            require(previous['to'] == event['from']
                    and timestamp(previous['at']) <= timestamp(event['at']), 'inconsistent history')
        previous = event
    trial = value['trial']
    if trial is not None:
        record(trial, {'metric', 'direction', 'baseline', 'minimum_gain', 'invariants',
                       'stop_condition', 'workflow_id', 'started_at', 'token'})
        string(trial['metric'], 'metric')
        require(trial['direction'] in {'decrease', 'increase'}, 'invalid metric direction')
        integer(trial['baseline'], 'baseline')
        integer(trial['minimum_gain'], 'minimum gain', 1)
        names(trial['invariants'], 'invariants')
        require(trial['invariants'], 'trial needs invariants')
        string(trial['stop_condition'], 'stop condition')
        string(trial['workflow_id'], 'trial workflow')
        timestamp(trial['started_at'])
        sha(trial['token'], 'trial token')
        require(trial['token'] == trial_token(value, trial), 'trial criteria changed')
    require(value['state'] not in {'trial', 'active'} or trial is not None, 'missing trial')
    if value['state'] == 'candidate':
        require(trial is None and not value['history'], 'candidate cannot carry trial history')
    else:
        require(previous is not None and previous['to'] == value['state']
                and len(value['history']) < value['revision'], 'state disagrees with history')
        if trial is not None:
            require(timestamp(trial['started_at']) <= timestamp(previous['at']), 'history predates trial')
    if value['state'] == 'trial':
        require(previous['from'] == 'candidate'
                and previous['at'] == trial['started_at'], 'invalid trial history')
    if value['state'] == 'active':
        require(previous['reason'] == 'observed benefit and invariants supported'
                and previous['evidence'] and all(e in value['evidence'] for e in previous['evidence']),
                'active strategy lacks promotion evidence')
    return value


def validate_profile(profile):
    bounded(profile)
    record(profile, {'profile_version', 'project_id', 'revision', 'boundaries', 'checks',
                     'improvements'}, {'observations'})
    require(type(profile['profile_version']) is int and profile['profile_version'] == 1,
            'unsupported profile version')
    string(profile['project_id'], 'project ID')
    integer(profile['revision'], 'profile revision')
    boundary_ids = set()
    for boundary in items(profile['boundaries'], 'boundaries', 128):
        record(boundary, {'id', 'consumers', 'complete'})
        string(boundary['id'], 'boundary ID')
        require(boundary['id'] not in boundary_ids, 'duplicate boundary')
        boundary_ids.add(boundary['id'])
        names(boundary['consumers'], 'consumers', 128)
        boolean(boundary['complete'], 'boundary completeness')
    for boundary in profile['boundaries']:
        require(set(boundary['consumers']) <= boundary_ids, 'unknown consumer')
    checks = items(profile['checks'], 'checks', 128)
    for check in checks:
        check_record(check)
        require(set(check['boundaries']) <= boundary_ids, 'unknown check boundary')
    require(len({c['id'] for c in checks}) == len(checks), 'duplicate check ID')
    improvements = items(profile['improvements'], 'improvements', 64)
    for row in improvements:
        improvement_record(row)
    require(len({r['id'] for r in improvements}) == len(improvements), 'duplicate improvement ID')
    for row in items(profile.get('observations', []), 'observations', 64):
        record(row, {'kind', 'note', 'evidence'})
        string(row['kind'], 'observation kind')
        string(row['note'], 'observation note')
        evidence_rows(row['evidence'])
    return profile


def parse_profile(markdown):
    """Parse one explicit project artifact supplied by the caller, without reading it."""
    start, end = '<!-- littlepowers:delivery-profile:v1 -->', '<!-- /littlepowers:delivery-profile -->'
    require(isinstance(markdown, str) and len(markdown.encode('utf-8')) <= MAX_BYTES,
            'invalid profile document')
    require(markdown.count(start) == markdown.count(end) == 1, 'expected one profile block')
    body = markdown.split(start, 1)[1].split(end, 1)[0].strip()
    require(body.startswith('```json\n') and body.endswith('\n```'), 'invalid profile fence')
    return validate_profile(json.loads(body[8:-4], object_pairs_hook=no_duplicates))


def fingerprint(value):
    record(value, {'check_digest', 'acceptance_digest', 'inputs', 'environment', 'data',
                   'permissions', 'inventory', 'complete'})
    for key in ('check_digest', 'acceptance_digest'):
        sha(value[key], key)
    normalize_verification_inputs(value['inputs'])
    for key in ('environment', 'data', 'permissions', 'inventory'):
        if value[key] is not None:
            string(value[key], key)
    boolean(value['complete'], 'fingerprint completeness')
    return value


def receipt_record(value):
    record(value, {'receipt_version', 'project_id', 'workflow_id', 'check_id', 'attempt_id',
                   'fingerprint', 'captured_at', 'started_at', 'finished_at', 'result',
                   'exit_code', 'duration_ms', 'evidence', 'supersedes'})
    require(type(value['receipt_version']) is int and value['receipt_version'] == 1,
            'unsupported receipt version')
    for key in ('project_id', 'workflow_id', 'check_id', 'attempt_id'):
        string(value[key], key)
    fingerprint(value['fingerprint'])
    require(timestamp(value['captured_at']) <= timestamp(value['started_at']),
            'inputs captured after check started')
    if value['finished_at'] is not None:
        require(timestamp(value['started_at']) <= timestamp(value['finished_at']), 'invalid check ordering')
    require(value['result'] in {'pass', 'fail', 'blocked', 'running', 'timeout', 'unknown'}, 'invalid result')
    if value['exit_code'] is not None:
        require(type(value['exit_code']) is int, 'invalid exit code')
    if value['duration_ms'] is not None:
        integer(value['duration_ms'], 'duration')
    evidence_rows(value['evidence'])
    names(value['supersedes'], 'superseded attempts', 64)
    return value


def validate_context(profile, context):
    record(context, {'project_id', 'workflow_id', 'profile_digest', 'stage', 'required_claims',
                     'required_checks', 'fresh_checks', 'changed_boundaries', 'impact_complete',
                     'tools', 'now', 'current', 'latest_attempts', 'verified_evidence'})
    require(context['project_id'] == profile['project_id'], 'wrong project')
    require(context['profile_digest'] == digest(profile), 'profile changed; reconcile')
    string(context['workflow_id'], 'workflow ID')
    require(context['stage'] in STAGES, 'invalid stage')
    for key in ('required_claims', 'required_checks', 'fresh_checks', 'changed_boundaries', 'tools'):
        names(context[key], key)
    boolean(context['impact_complete'], 'impact completeness')
    timestamp(context['now'])
    require(isinstance(context['current'], dict) and len(context['current']) <= 128, 'invalid current inputs')
    for key, value in context['current'].items():
        string(key, 'check ID')
        fingerprint(value)
    require(isinstance(context['latest_attempts'], dict) and len(context['latest_attempts']) <= 128,
            'invalid attempt observations')
    for key, value in context['latest_attempts'].items():
        string(key, 'check ID')
        string(value, 'attempt ID')
    evidence_rows(context['verified_evidence'])


def reuse_reason(check, receipt, context):
    """Return None only for a candidate supported by explicit caller observations."""
    if receipt is None:
        return 'no_receipt'
    receipt_record(receipt)
    if receipt['check_id'] != check['id'] or receipt['project_id'] != context['project_id']:
        return 'receipt_scope_changed'
    if context['latest_attempts'].get(check['id']) != receipt['attempt_id']:
        return 'latest_attempt_unknown_or_different'
    if receipt['result'] != 'pass' or receipt['exit_code'] not in (None, 0) or receipt['finished_at'] is None:
        return 'no_completed_pass'
    if timestamp(receipt['finished_at']) > timestamp(context['now']):
        return 'future_receipt'
    if check['id'] in context['fresh_checks'] and receipt['workflow_id'] != context['workflow_id']:
        return 'fresh_run_required'
    current = context['current'].get(check['id'])
    if current is None or not current['complete'] or not context['impact_complete']:
        return 'incomplete_dependency_observation'
    if any(current[k] is None for k in ('environment', 'data', 'permissions', 'inventory')):
        return 'unknown_context'
    if current['check_digest'] != check_digest(check):
        return 'check_definition_changed'
    files = {r['path'] for r in current['inputs']['files']}
    if not set(check['inputs']) <= files:
        return 'missing_declared_input'
    if receipt['fingerprint'] != current:
        return 'inputs_or_context_changed'
    if not evidence_valid(receipt['evidence'], context['verified_evidence']):
        return 'evidence_unavailable_or_changed'
    age = timestamp(context['now']) - timestamp(receipt['finished_at'])
    if check['live'] and (check['max_age_seconds'] is None or age > check['max_age_seconds']):
        return 'live_observation_stale_or_unbounded'
    return None


def select(profile, context, receipts):
    bounded([profile, context, receipts])
    validate_profile(profile)
    validate_context(profile, context)
    for row in items(receipts, 'receipts', 128):
        receipt_record(row)
    require(len({r['check_id'] for r in receipts}) == len(receipts), 'ambiguous latest receipts')
    saved = {r['check_id']: r for r in receipts}
    graph = {b['id']: b for b in profile['boundaries']}
    affected, unknown = set(context['changed_boundaries']), []
    frontier = list(affected)
    while frontier:
        key = frontier.pop()
        if key not in graph or not graph[key]['complete']:
            unknown.append('unknown impact boundary: ' + key)
        if key in graph:
            for consumer in graph[key]['consumers']:
                if consumer not in affected:
                    affected.add(consumer)
                    frontier.append(consumer)
    if not context['impact_complete']:
        unknown.append('change inventory or impact is incomplete')
    required = set(context['required_checks']) | set(context['fresh_checks'])
    check_ids = {c['id'] for c in profile['checks']}
    unknown.extend('required check unavailable: ' + key for key in sorted(required - check_ids))
    # An unchanged-input observation is insufficient when a requested check's
    # dependency boundary is explicitly incomplete, even with an empty diff.
    for check in profile['checks']:
        requested = check['mandatory'] or check['id'] in required or (
            context['stage'] in check['stages']
            and bool(set(context['required_claims']).intersection(check['covers'])))
        if requested:
            unknown.extend('incomplete check boundary: ' + key for key in check['boundaries']
                           if not graph[key]['complete'])
    result = {'status': 'ready', 'proposal_only': True, 'profile_digest': digest(profile),
              'run': [], 'reuse_candidates': [], 'not_applicable': [], 'blocked': [],
              'coverage_missing': [], 'reasons': {}, 'affected_boundaries': sorted(affected)}
    covered, costs = set(), {}
    for check in profile['checks']:
        key = check['id']
        eligible = context['stage'] in check['stages']
        needed = check['mandatory'] or key in required or (eligible and
            (bool(unknown) or bool(affected.intersection(check['boundaries']))
             or bool(set(context['required_claims']).intersection(check['covers']))))
        if not needed:
            result['not_applicable'].append(key)
            result['reasons'][key] = 'outside_current_stage_or_declared_claims_and_impact'
            continue
        missing_tools = set(check['requires']) - set(context['tools'])
        if missing_tools:
            result['blocked'].append(key)
            result['reasons'][key] = 'missing capabilities: ' + ', '.join(sorted(missing_tools))
            continue
        covered.update(check['covers'])
        reason = reuse_reason(check, saved.get(key), context) if not unknown else 'unknown_impact'
        result['reasons'][key] = reason or 'unchanged_check_inputs_context_and_verified_evidence'
        result['run' if reason else 'reuse_candidates'].append(key)
        samples = sorted(check['samples_ms'])
        costs[key] = samples[len(samples) // 2] if samples else None
    result['run'].sort(key=lambda key: (costs[key] is None, costs[key] or 0, key))
    result['coverage_missing'] = sorted(set(context['required_claims']) - covered)
    result['issues'] = unknown
    result['status'] = 'blocked' if unknown or result['blocked'] or result['coverage_missing'] else 'ready'
    unknown_costs = [key for key in result['run'] if costs[key] is None]
    result['unknown_costs'] = unknown_costs
    result['estimated_run_ms'] = None if unknown_costs else sum(costs[k] for k in result['run'])
    return result


def reuse(profile, context, receipt):
    """Inspect one receipt under the same selection and capability rules."""
    result = select(profile, context, [receipt])
    key = receipt['check_id']
    require(any(c['id'] == key for c in profile['checks']), 'unknown receipt check')
    return {'proposal_only': True, 'check_id': key,
            'reusable': result['status'] == 'ready' and key in result['reuse_candidates'],
            'reason': result['reasons'].get(key), 'issues': result['issues']}


def merge_inputs(receipts):
    """Union original file receipts, never adopt current hashes to clear drift."""
    bounded(receipts)
    files, projects = {}, set()
    for row in items(receipts, 'receipts', 128):
        receipt_record(row)
        require(row['result'] == 'pass' and row['exit_code'] in (None, 0)
                and row['finished_at'] is not None and row['fingerprint']['complete']
                and evidence_valid(row['evidence'], row['evidence']),
                'only completed passing receipts can be aggregated')
        projects.add(row['project_id'])
        require(len(projects) == 1, 'mixed project receipts')
        inputs = normalize_verification_inputs(row['fingerprint']['inputs'])
        require(inputs['mode'] == 'files', 'manual claims require separate coordinator justification')
        for item in inputs['files']:
            key = item['path']
            require(key not in files or files[key] == item['sha256'], 'conflicting original inputs: ' + key)
            files[key] = item['sha256']
    return normalize_verification_inputs({'mode': 'files', 'manual_reason': None,
        'files': [{'path': key, 'sha256': value} for key, value in sorted(files.items())]})


def learn(profile, context, event):
    bounded([profile, context, event])
    validate_profile(profile)
    record(context, {'project_id', 'workflow_id', 'profile_digest', 'policy_digest', 'conditions',
                     'write_authorized', 'scope_unchanged', 'acceptance_unchanged', 'reversible',
                     'invalidated', 'now', 'verified_evidence'})
    require(context['project_id'] == profile['project_id'], 'wrong project')
    require(context['profile_digest'] == digest(profile), 'profile changed; reconcile')
    sha(context['policy_digest'], 'policy digest')
    string(context['workflow_id'], 'workflow ID')
    conditions(context['conditions'])
    timestamp(context['now'])
    evidence_rows(context['verified_evidence'])
    for key in ('write_authorized', 'scope_unchanged', 'acceptance_unchanged', 'reversible', 'invalidated'):
        boolean(context[key], key)
    record(event, {'kind', 'id', 'expected_revision'}, {'candidate', 'trial', 'observation'})
    require(event['kind'] in {'propose', 'start_trial', 'assess', 'observe'}, 'invalid learning event')
    string(event['id'], 'improvement ID')
    integer(event['expected_revision'], 'expected revision')
    previous = next((r for r in profile['improvements'] if r['id'] == event['id']), None)
    require(event['expected_revision'] == (previous['revision'] if previous else 0),
            'improvement changed; reconcile')
    out = {'proposal_only': True, 'status': 'noop', 'apply': False,
           'expected_profile_digest': digest(profile), 'expected_revision': event['expected_revision'],
           'record': None, 'reason': None, 'fallback': None}
    if not context['write_authorized']:
        return dict(out, status='read_only', reason='no project write authority')
    if event['kind'] == 'propose':
        row = copy.deepcopy(improvement_record(event['candidate']))
        require(row['id'] == event['id'] and row['state'] == 'candidate'
                and row['revision'] == event['expected_revision'] + 1
                and row['trial'] is None and not row['history'], 'invalid candidate')
        require(previous is None or previous['state'] == 'retired', 'existing improvement is not retired')
        require(previous is not None or len(profile['improvements']) < 64, 'improvement limit reached')
        require(evidence_valid(row['evidence'], context['verified_evidence']), 'candidate needs observed evidence')
        require(previous is None or any(e not in previous['evidence'] for e in row['evidence']),
                'retired improvement needs new evidence')
        return dict(out, status='proposed', record=row, reason='candidate recorded, not applied')
    require(previous is not None, 'unknown improvement')
    row = copy.deepcopy(previous)
    state = row['state']
    if state == 'retired':
        return dict(out, reason='retired; propose a new evidenced version')
    valid = evidence_valid(row['evidence'], context['verified_evidence'])
    invalid = context['invalidated'] or row['policy_digest'] != context['policy_digest'] or not valid
    applicable = all(context['conditions'].get(k) == v for k, v in row['conditions'].items())
    safe = row['change']['kind'] in SAFE_CHANGES and all(context[k] for k in
        ('scope_unchanged', 'acceptance_unchanged', 'reversible'))
    next_state, reason, proof = state, None, []
    if invalid and state in {'trial', 'active'}:
        next_state, reason = 'retired', 'evidence_or_policy_invalidated'
    elif invalid:
        return dict(out, status='blocked', reason='candidate evidence or policy is invalid')
    elif not applicable:
        return dict(out, reason='outside declared conditions')
    elif not safe:
        return dict(out, status='approval_required', reason='change is outside equivalent reversible authority')
    elif event['kind'] == 'start_trial':
        require(state == 'candidate', 'only a candidate can start a trial')
        spec = copy.deepcopy(event['trial'])
        record(spec, {'metric', 'direction', 'baseline', 'minimum_gain', 'invariants', 'stop_condition'})
        spec.update(workflow_id=context['workflow_id'], started_at=context['now'])
        spec['token'] = trial_token(row, spec)
        row['trial'] = spec
        next_state, reason = 'trial', 'bounded trial started with predeclared criteria'
    elif event['kind'] == 'assess':
        require(state in {'trial', 'active'}, 'no trial to assess')
        obs = event['observation']
        record(obs, {'trial_token', 'workflow_id', 'observed_at', 'result', 'value', 'invariants', 'evidence'})
        require(obs['trial_token'] == row['trial']['token']
                and obs['workflow_id'] == row['trial']['workflow_id'], 'observation belongs to another trial')
        require(timestamp(row['trial']['started_at']) <= timestamp(obs['observed_at'])
                <= timestamp(context['now']), 'invalid trial observation time')
        require(obs['result'] in {'pass', 'fail', 'unknown', 'running', 'timeout'}, 'invalid trial result')
        proof = evidence_rows(obs['evidence'])
        if obs['result'] in {'unknown', 'running'} or not evidence_valid(proof, context['verified_evidence']):
            return dict(out, reason='trial result or evidence is incomplete')
        record(obs['invariants'], set(row['trial']['invariants']))
        for value in obs['invariants'].values():
            boolean(value, 'invariant')
        gain = None
        if obs['value'] is not None:
            integer(obs['value'], 'observed value')
            gain = obs['value'] - row['trial']['baseline']
            if row['trial']['direction'] == 'decrease':
                gain = -gain
        if obs['result'] != 'pass' or not all(obs['invariants'].values()) or (gain is not None and gain < 0):
            next_state, reason = 'retired', 'failed_invariant_or_negative_trial'
        elif gain is None or gain < row['trial']['minimum_gain']:
            return dict(out, reason='declared benefit is not established')
        else:
            next_state, reason = 'active', 'observed benefit and invariants supported'
            row['evidence'] = list({e['ref']: e for e in row['evidence'] + proof}.values())
    elif event['kind'] == 'observe':
        return dict(out, apply=state == 'active', reason='applicable active strategy' if state == 'active'
                    else 'not active; no automatic application')
    if next_state == state and reason is None:
        return out
    row['state'] = next_state
    row['revision'] += 1
    row['history'] = (row['history'] + [{'from': state, 'to': next_state, 'reason': reason,
                                      'at': context['now'], 'evidence': proof}])[-16:]
    improvement_record(row)
    return dict(out, status='proposed', record=row, reason=reason, apply=False,
                fallback='last_still_valid_strategy_or_conservative_default' if next_state == 'retired' else None)


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, 'input exceeds 2 MiB')
        data = json.loads(raw, object_pairs_hook=no_duplicates)
        bounded(data)
        operation = data.pop('operation')
        functions = {'select': select, 'reuse': reuse, 'learn': learn, 'merge_inputs': merge_inputs,
                     'parse_profile': parse_profile}
        require(operation in functions, 'unknown operation')
        print(canonical(functions[operation](**data)))
        return 0
    except (ValueError, StateError, TypeError, KeyError, OverflowError, RecursionError, UnicodeError) as exc:
        print(json.dumps({'status': 'invalid', 'proposal_only': True, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
