#!/usr/bin/env python3
"""Pure execution-efficiency proposals. No tools, filesystem reads or ledger writes.

See references/execution-efficiency.md for the adapter/authority contract.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from datetime import datetime

SCHEMA = 1
MAX_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 64
SCOPE_KEYS = {'session', 'task', 'target', 'environment', 'observer_version', 'contract_digest'}
RESULTS = {'PASS', 'FAIL', 'ERROR', 'UNKNOWN', 'WAIT', 'ACTION_REQUIRED'}
HEX = re.compile(r'sha256:[0-9a-f]{64}\Z')


def canonical(value):
    """UTF-8, scalar code-point keys; safe integers only, no locale or floats."""
    def check(v):
        if v is None or type(v) is bool:
            return
        if type(v) is int and abs(v) <= 9007199254740991:
            return
        if isinstance(v, str):
            v.encode('utf-8', errors='strict')
            return
        if isinstance(v, list):
            for item in v:
                check(item)
            return
        if isinstance(v, dict) and all(isinstance(k, str) for k in v):
            for k, item in v.items():
                check(k)
                check(item)
            return
        raise ValueError('canonical JSON requires scalar strings and safe integers; no floats')
    check(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return 'sha256:' + hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def string(value, label):
    require(isinstance(value, str) and bool(value) and len(value) <= 2048, 'invalid ' + label)
    value.encode('utf-8')
    return value


def integer(value, label, minimum=0):
    require(type(value) is int and minimum <= value <= 9007199254740991, 'invalid ' + label)
    return value


def strings(value, label):
    require(isinstance(value, list), label + ' must be a list')
    for item in value:
        string(item, label)
    require(len(value) == len(set(value)), 'duplicate ' + label)
    return value


def scope(value):
    require(isinstance(value, dict) and set(value) == SCOPE_KEYS, 'invalid scope fields')
    for key in SCOPE_KEYS - {'contract_digest'}:
        string(value[key], key)
    require(value['contract_digest'] is None or
            isinstance(value['contract_digest'], str) and HEX.fullmatch(value['contract_digest']),
            'invalid contract_digest')
    return copy.deepcopy(value)


def timestamp(value):
    string(value, 'timestamp')
    require(value.endswith('Z'), 'timestamp must be UTC ending Z')
    parsed = datetime.fromisoformat(value[:-1] + '+00:00')
    return parsed.timestamp()


def evidence(value):
    require(isinstance(value, dict) and set(value) == {'ref', 'sha256', 'saved', 'upstream_complete'},
            'invalid evidence receipt')
    string(value['ref'], 'evidence ref')
    require(type(value['saved']) is bool and type(value['upstream_complete']) is bool,
            'evidence flags must be boolean')
    require(value['sha256'] is None or isinstance(value['sha256'], str) and HEX.fullmatch(value['sha256']),
            'invalid evidence digest')
    require(not value['saved'] or value['sha256'] is not None, 'saved evidence needs digest')
    return value


def validate_report(report):
    require(isinstance(report, dict) and type(report.get('schema_version')) is int and report.get('schema_version') == SCHEMA, 'invalid report schema')
    scope(report.get('scope'))
    timestamp(report.get('observed_at'))
    require('source_updated_at' in report, 'missing source_updated_at')
    if report['source_updated_at'] is None:
        require(report.get('source_freshness') == 'unknown', 'unknown source time needs unknown freshness')
    else:
        timestamp(report['source_updated_at'])
    require(report.get('result') in RESULTS, 'invalid result')
    require(report.get('source_freshness') in {'fresh', 'stale', 'unknown'}, 'invalid freshness')
    required = strings(report.get('required'), 'required check IDs')
    checks = report.get('checks')
    require(isinstance(checks, list), 'checks must be a list')
    ids = []
    for check in checks:
        require(isinstance(check, dict), 'invalid check')
        ids.append(string(check.get('id'), 'check ID'))
        require(check.get('result') in RESULTS, 'invalid check result')
    require(len(ids) == len(set(ids)) and set(ids) <= set(required), 'duplicate or unplanned check')
    findings = report.get('findings')
    require(isinstance(findings, list), 'findings must be a list')
    fids = []
    for finding in findings:
        require(isinstance(finding, dict), 'invalid finding')
        fids.append(string(finding.get('id'), 'finding ID'))
        require(finding.get('check_id') in required, 'finding needs planned check ID')
        require(finding.get('severity') in {'critical', 'error', 'warning', 'info'}, 'invalid severity')
        string(finding.get('message'), 'finding message')
    require(len(fids) == len(set(fids)), 'duplicate finding ID')
    receipts = report.get('evidence')
    require(isinstance(receipts, list), 'evidence must be a list')
    for item in receipts:
        evidence(item)
    require(len({r['ref'] for r in receipts}) == len(receipts), 'duplicate evidence refs')
    visual = strings(report.get('visual_refs'), 'visual refs')
    require(set(visual) <= {r['ref'] for r in receipts}, 'visual reference has no receipt')
    canonical(report)
    return report


def pack(report, budget_chars):
    """Adapter must save original bytes BEFORE calling; receipts are assertions."""
    validate_report(report)
    integer(budget_chars, 'budget_chars', 1)
    required, checks = report['required'], report['checks']
    unknown = sorted(set(required) - {c['id'] for c in checks if c['result'] != 'UNKNOWN'})
    complete = bool(report['evidence']) and all(r['saved'] and r['upstream_complete'] for r in report['evidence'])
    result = report['result']
    statuses = {c['result'] for c in checks} | {result}
    severities = {f['severity'] for f in report['findings']}
    if not complete or 'ERROR' in statuses:
        result = 'ERROR'
    elif 'ACTION_REQUIRED' in statuses:
        result = 'ACTION_REQUIRED'
    elif statuses & {'FAIL'} or severities & {'critical', 'error'}:
        result = 'FAIL'
    elif unknown or report['source_freshness'] != 'fresh':
        result = 'UNKNOWN'
    elif 'WAIT' in statuses:
        result = 'WAIT'
    summary = {
        'schema_version': SCHEMA, 'scope': copy.deepcopy(report['scope']), 'result': result,
        'observed_at': report['observed_at'], 'source_updated_at': report['source_updated_at'],
        'source_freshness': report['source_freshness'],
        'coverage': {'required': len(required), 'checked': len(required) - len(unknown), 'unknown': len(unknown)},
        'required': required[:], 'checks': [{'id': c['id'], 'result': c['result']} for c in checks],
        'unknown_checks': unknown, 'changed_fields': [], 'findings': copy.deepcopy(report['findings']),
        'artifact_refs': [r['ref'] for r in report['evidence']], 'visual_refs': report['visual_refs'][:],
        'evidence_complete': complete, 'summary_has_more': False, 'supplemental_reads': [],
        'issues': [], 'budget_exceeded': False,
    }
    if not complete:
        summary['issues'].append('evidence_missing_unsaved_or_upstream_truncated')
    if len(canonical(summary)) > budget_chars or any(set(c) - {'id', 'result'} for c in checks):
        omitted = [f['id'] for f in summary['findings'] if f['severity'] not in {'critical', 'error'}]
        summary['findings'] = [f for f in summary['findings'] if f['severity'] in {'critical', 'error'}]
        # Check details and visual artifacts remain addressable even when no findings were omitted.
        summary['summary_has_more'] = True
        summary['supplemental_reads'] = [{'artifact_refs': summary['artifact_refs'][:],
                                         'finding_ids': omitted, 'check_ids': required[:],
                                         'reason': 'inspect full evidence and required visuals'}]
    summary['budget_exceeded'] = len(canonical(summary)) > budget_chars
    # Essential coverage/errors may exceed a soft budget. Host must not truncate them.
    return summary



def validate_summary(summary, receipts, expected_scope):
    require(isinstance(summary, dict) and summary.get('scope') == expected_scope, 'invalid event scope')
    report = {key: summary.get(key) for key in ('schema_version', 'scope', 'result', 'observed_at',
              'source_updated_at', 'source_freshness', 'required', 'checks', 'findings', 'visual_refs')}
    report['evidence'] = receipts
    expected = pack(report, MAX_BYTES)
    for key in ('coverage', 'unknown_checks', 'artifact_refs', 'evidence_complete', 'result'):
        require(summary.get(key) == expected[key], 'invalid event summary ' + key)
    strings(summary.get('changed_fields'), 'changed fields')
    strings(summary.get('issues'), 'issues')
    for key in ('summary_has_more', 'budget_exceeded', 'evidence_complete'):
        require(type(summary.get(key)) is bool, 'invalid summary flag')
    require(isinstance(summary.get('supplemental_reads'), list), 'invalid supplemental reads')


def semantic(observation):
    require(isinstance(observation, dict) and type(observation.get('schema_version')) is int and observation.get('schema_version') == SCHEMA,
            'invalid observation schema')
    required = strings(observation.get('required_fields'), 'required semantic fields')
    require({'state', 'version'} <= set(required), 'state and version are required')
    entities = observation.get('entities')
    require(isinstance(entities, list), 'entities missing or collection failed; not an empty list')
    result = {}
    for entity in entities:
        require(isinstance(entity, dict) and set(entity) == {'id', 'fields'}, 'invalid entity')
        key = string(entity['id'], 'stable entity ID')
        require(key not in result, 'duplicate entity ID')
        fields = entity['fields']
        require(isinstance(fields, dict) and set(required) <= set(fields), 'missing required semantic field')
        require(all(fields[k] is not None for k in required), 'null required semantic field')
        result[key] = copy.deepcopy(fields)
    canonical(result)
    return {'required_fields': sorted(required), 'entities': result}


def differences(before, after, path=''):
    """JSON Pointer paths; additions, deletions and values (including optional fields)."""
    if isinstance(before, dict) and isinstance(after, dict):
        changed = []
        for key in sorted(set(before) | set(after)):
            child = path + '/' + key.replace('~', '~0').replace('/', '~1')
            if key not in before or key not in after:
                changed.append(child)
            else:
                changed.extend(differences(before[key], after[key], child))
        return changed
    return [] if canonical(before) == canonical(after) else [path or '/']


def seal(cursor):
    body = copy.deepcopy(cursor)
    body.pop('integrity', None)
    body['integrity'] = digest(body)
    return body


def restore(cursor, expected_scope, now, max_age_seconds, verified_evidence):
    """Only explicit root-verified receipts; never follows a reference or opens a file."""
    scope(expected_scope)
    integer(max_age_seconds, 'max_age_seconds', 1)
    now_seconds = timestamp(now)
    require(isinstance(cursor, dict), 'cursor must be an object')
    expected_keys = {'schema_version', 'scope', 'updated_at', 'last_observed', 'pending_events',
                     'last_acknowledged', 'next_sequence', 'health', 'integrity'}
    require(set(cursor) == expected_keys and type(cursor['schema_version']) is int and
            cursor['schema_version'] == SCHEMA, 'invalid cursor schema')
    require(cursor['integrity'] == seal(cursor)['integrity'], 'cursor integrity mismatch')
    require(scope(cursor['scope']) == expected_scope, 'cursor scope mismatch; explicit new baseline required')
    age = now_seconds - timestamp(cursor['updated_at'])
    require(0 <= age <= max_age_seconds, 'cursor expired or future dated')
    require(cursor['health'] in {'healthy', 'error'}, 'invalid cursor health')
    acknowledged = integer(cursor['last_acknowledged'], 'last_acknowledged')
    sequence = integer(cursor['next_sequence'], 'next_sequence', 1)
    require(acknowledged < sequence, 'invalid acknowledged sequence')
    pending = cursor['pending_events']
    require(isinstance(pending, list) and len(pending) <= MAX_EVENTS, 'invalid pending events')
    require(sequence - acknowledged - 1 == len(pending) and
            all(isinstance(e, dict) and type(e.get('sequence')) is int and
                e['sequence'] == acknowledged + i + 1 for i, e in enumerate(pending)),
            'pending events missing or reordered')
    require(isinstance(verified_evidence, list), 'verified_evidence must be explicit')
    verified = {}
    for receipt in verified_evidence:
        evidence(receipt)
        require(receipt['saved'], 'verified evidence not saved')
        require(receipt['ref'] not in verified, 'duplicate verified receipt')
        verified[receipt['ref']] = receipt['sha256']

    def check_receipts(receipts):
        require(isinstance(receipts, list), 'invalid cursor evidence')
        for receipt in receipts:
            evidence(receipt)
            if receipt['saved']:
                require(verified.get(receipt['ref']) == receipt['sha256'], 'cursor evidence unavailable or changed')

    for event in pending:
        require(set(event) == {'sequence', 'id', 'kind', 'summary', 'evidence'}, 'invalid event fields')
        require(event['kind'] in {'baseline', 'changed', 'recovered', 'error', 'periodic'}, 'invalid event kind')
        require(event['id'] == digest({'scope': expected_scope, 'sequence': event['sequence']}), 'invalid event ID')
        summary = event['summary']
        validate_summary(summary, event['evidence'], expected_scope)
        require(timestamp(summary['observed_at']) <= timestamp(cursor['updated_at']), 'future event')
        check_receipts(event['evidence'])
    last = cursor['last_observed']
    if last is not None:
        require(isinstance(last, dict) and set(last) == {'semantic', 'signature', 'observed_at', 'evidence'},
                'invalid last observation')
        state = last['semantic']
        require(isinstance(state, dict) and set(state) == {'required_fields', 'entities'} and
                isinstance(state['entities'], dict), 'invalid semantic baseline')
        semantic({'schema_version': SCHEMA, 'required_fields': state['required_fields'],
                  'entities': [{'id': k, 'fields': v} for k, v in state['entities'].items()]})
        require(last['signature'] == digest(state), 'invalid semantic signature')
        require(timestamp(last['observed_at']) <= timestamp(cursor['updated_at']), 'invalid baseline time')
        check_receipts(last['evidence'])
        require(bool(last['evidence']) and all(r['saved'] and r['upstream_complete'] for r in last['evidence']),
                'incomplete baseline evidence')
    require(last is not None or cursor['health'] == 'error', 'healthy cursor without baseline')
    return copy.deepcopy(cursor)


def observe(report, observation, cursor, *, now, max_source_age_seconds,
            max_cursor_age_seconds, verified_evidence, budget_chars=8000, report_due=False):
    """Propose a cursor. Persisting it is NOT delivery. Pending events return first."""
    summary = pack(report, budget_chars)
    integer(max_source_age_seconds, 'max_source_age_seconds', 1)
    require(type(report_due) is bool, 'report_due must be boolean')
    current_time = timestamp(now)
    require(timestamp(report['observed_at']) <= current_time, 'collection timestamp is in the future')
    if cursor is not None:
        candidate = restore(cursor, report['scope'], now, max_cursor_age_seconds, verified_evidence)
        if candidate['pending_events']:
            return {'action': 'report', 'delivery_uncertain': True,
                    'events': copy.deepcopy(candidate['pending_events']), 'candidate_cursor': candidate}
    else:
        candidate = {'schema_version': SCHEMA, 'scope': copy.deepcopy(report['scope']), 'updated_at': now,
                     'last_observed': None, 'pending_events': [], 'last_acknowledged': 0,
                     'next_sequence': 1, 'health': 'error'}
    state = None
    try:
        state = semantic(observation)
    except (ValueError, TypeError, UnicodeError) as exc:
        summary['result'] = 'ERROR'
        summary['issues'].append(str(exc))
    age = (current_time - timestamp(report['source_updated_at'])
           if report['source_updated_at'] is not None else 0)
    if not 0 <= age <= max_source_age_seconds:
        summary['source_freshness'] = 'stale'
        summary['result'] = 'UNKNOWN' if summary['result'] not in {'ERROR', 'FAIL', 'ACTION_REQUIRED'} else summary['result']
        summary['issues'].append('source stale or future dated')
    healthy = (state is not None and summary['evidence_complete'] and
               summary['coverage']['unknown'] == 0 and summary['source_freshness'] == 'fresh' and
               summary['result'] in {'PASS', 'WAIT'})
    last = candidate['last_observed']
    if last and state and last['semantic']['required_fields'] != state['required_fields']:
        summary['result'] = 'ERROR'
        summary['issues'].append('semantic schema changed without observer_version change')
        healthy = False
    if not healthy:
        kind = 'error'
        candidate['health'] = 'error'
    else:
        summary['changed_fields'] = differences(last['semantic'], state) if last else ['/']
        kind = ('baseline' if last is None else 'recovered' if candidate['health'] == 'error'
                else 'changed' if summary['changed_fields'] else 'periodic' if report_due else None)
        candidate['last_observed'] = {'semantic': state, 'signature': digest(state),
                                      'observed_at': report['observed_at'], 'evidence': copy.deepcopy(report['evidence'])}
        candidate['health'] = 'healthy'
    candidate['updated_at'] = now
    if kind:
        sequence = candidate['next_sequence']
        candidate['pending_events'].append({'sequence': sequence,
            'id': digest({'scope': report['scope'], 'sequence': sequence}), 'kind': kind,
            'summary': summary, 'evidence': copy.deepcopy(report['evidence'])})
        candidate['next_sequence'] += 1
    candidate = seal(candidate)
    return {'action': 'report' if kind else 'continue', 'delivery_uncertain': False,
            'events': copy.deepcopy(candidate['pending_events']), 'candidate_cursor': candidate}


def acknowledge(cursor, event_id, *, expected_scope, now, max_age_seconds, verified_evidence):
    """Root calls only with confirmed report receipt, at an existing normal boundary."""
    candidate = restore(cursor, expected_scope, now, max_age_seconds, verified_evidence)
    matches = [e['sequence'] for e in candidate['pending_events'] if e['id'] == event_id]
    require(len(matches) == 1, 'acknowledgment does not name a pending event')
    candidate['last_acknowledged'] = matches[0]
    candidate['pending_events'] = [e for e in candidate['pending_events'] if e['sequence'] > matches[0]]
    candidate['updated_at'] = now
    return seal(candidate)


def classify_error(error):
    require(isinstance(error, dict), 'error must be an object')
    code = error.get('code')
    groups = {'syntax': 'deterministic', 'argument': 'deterministic', 'binding': 'deterministic',
              'timeout': 'transient', 'network': 'transient', 'rate_limit': 'transient',
              'pending': 'business_wait', 'permission': 'authorization'}
    category = groups.get(code)
    if category is None and code is None:
        message = str(error.get('message', '')).lower()
        category = 'deterministic' if any(x in message for x in ('syntaxerror', 'nameerror', 'invalid argument')) else 'unknown'
    category = category or 'unknown'
    builtin = error.get('host_retried', False)
    require(type(builtin) is bool, 'host_retried must be boolean')
    return {'category': category, 'automatic_retry': False,
            'next': {'deterministic': 'substantively_correct_then_minimal_validation',
                     'business_wait': 'reuse_host_handle_and_bounded_wait',
                     'authorization': 'preserve_blocker_no_permission_escalation',
                     'unknown': 'diagnose_no_repair_authority',
                     'transient': 'inspect_host_retry_and_remaining_task_budget' if builtin else
                                  'host_may_retry_only_with_explicit_risk_and_time_budget'}[category]}


def batch_decision(*, now_ms, deadline_ms, report_deadline_ms, observation_timeout_ms,
                   cancelled, capabilities):
    """A pure host proposal, never a scheduler. All times use the same monotonic clock."""
    for key, value in [('now_ms', now_ms), ('deadline_ms', deadline_ms),
                       ('report_deadline_ms', report_deadline_ms), ('observation_timeout_ms', observation_timeout_ms)]:
        integer(value, key, 1 if key == 'observation_timeout_ms' else 0)
    require(type(cancelled) is bool, 'cancelled must be boolean')
    require(isinstance(capabilities, dict) and set(capabilities) == {'bounded_wait', 'cancel', 'reuse_handle'},
            'explicit host capabilities required')
    require(all(type(v) is bool for v in capabilities.values()), 'invalid capability flags')
    if cancelled:
        return {'action': 'return', 'reason': 'cancelled'}
    if now_ms >= report_deadline_ms:
        return {'action': 'return', 'reason': 'periodic_report_due'}
    if now_ms >= deadline_ms:
        return {'action': 'return', 'reason': 'batch_deadline'}
    if not all(capabilities.values()):
        return {'action': 'degraded', 'reason': 'host_cannot_guarantee_bounded_wait_cancel_or_handle_reuse',
                'zero_model_monitoring': False}
    return {'action': 'observe', 'timeout_ms': min(observation_timeout_ms, deadline_ms - now_ms,
                                                report_deadline_ms - now_ms)}


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, 'input exceeds 2 MiB')
        data = json.loads(raw, object_pairs_hook=no_duplicates)
        canonical(data)
        operation = data.pop('operation')
        functions = {'pack': pack, 'observe': observe, 'acknowledge': acknowledge,
                     'restore': restore, 'classify_error': classify_error, 'batch_decision': batch_decision}
        require(operation in functions, 'unknown operation')
        result = functions[operation](**data)
        print(canonical(result))
        return 0
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError, UnicodeError) as exc:
        print(json.dumps({'result': 'ERROR', 'evidence_complete': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
