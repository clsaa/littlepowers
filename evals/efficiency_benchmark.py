#!/usr/bin/env python3
"""Explicit local synthetic A/B run; never accesses host logs, models or sessions."""
import argparse
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time

from efficiency_host_fixture import atomic_save, verify_receipt
import littlepowers_efficiency as eff

SCOPE = dict(session='synthetic', task='benchmark', target='page', environment='fixture-v1',
             observer_version='v1', contract_digest=None)
NOW = '2000-01-01T00:00:01Z'


def synthetic_tool(index, payload_chars):
    """Same checks, changes and business wait (zero) in both arms."""
    return {'required': ['C1', 'C2'], 'checks': [{'id':'C1','result':'PASS'}, {'id':'C2','result':'PASS'}],
            'findings': [], 'entities': [{'id':'job', 'fields':{'state':'ready', 'version':index // 10}}],
            'raw_log': 'synthetic detail ' * (payload_chars // 17), 'sample_clock': index}


def distribution(values):
    ordered = sorted(values)
    return dict(total=sum(values), count=len(values), min=min(values), median=statistics.median(values),
                p95=ordered[min(len(ordered)-1, int(.95 * len(ordered)))], max=max(values))


def run_arm(mode, count, payload_chars):
    total_start = time.perf_counter()
    tool_seconds = helper_seconds = save_seconds = recovery_seconds = 0.0
    text_chars, calls, checks_checked = [], 0, 0
    cursor = None
    with tempfile.TemporaryDirectory(prefix='lp-synthetic-') as directory:
        root = Path(directory)
        setup_seconds = time.perf_counter() - total_start
        loop_start = time.perf_counter()
        for index in range(count):
            before = time.perf_counter()
            raw = synthetic_tool(index, payload_chars)
            tool_seconds += time.perf_counter() - before
            calls += 1
            checks_checked += len(raw['checks'])
            before = time.perf_counter()
            receipt = atomic_save(root / ('sample-%d.json' % index), raw)
            save_seconds += time.perf_counter() - before
            if mode == 'full':
                text_chars.append(len(eff.canonical(raw)))
                continue
            before = time.perf_counter()
            report = dict(schema_version=1, scope=SCOPE, result='PASS', observed_at=NOW,
                          source_updated_at=NOW, source_freshness='fresh', required=raw['required'],
                          checks=raw['checks'], findings=raw['findings'], evidence=[receipt], visual_refs=[])
            observed = dict(schema_version=1, required_fields=['state','version'], entities=raw['entities'])
            prior = cursor['last_observed']['evidence'] if cursor else []
            verified = [verify_receipt(root / r['ref'], r) for r in prior]
            result = eff.observe(report, observed, cursor, now=NOW, max_source_age_seconds=10,
                                 max_cursor_age_seconds=100, verified_evidence=verified, budget_chars=8000)
            helper_seconds += time.perf_counter() - before
            cursor = result['candidate_cursor']
            if result['events']:
                before = time.perf_counter()
                atomic_save(root / 'cursor.json', cursor)
                save_seconds += time.perf_counter() - before
                # Measure a real save/reload/receipt verification recovery, before reporting.
                if index == 0:
                    before = time.perf_counter()
                    recovered = json.loads((root / 'cursor.json').read_text())
                    eff.restore(recovered, SCOPE, NOW, 100, [verify_receipt(root / receipt['ref'], receipt)])
                    recovery_seconds += time.perf_counter() - before
                text_chars.append(len(eff.canonical(result['events'])))
                before = time.perf_counter()
                cursor = eff.acknowledge(cursor, result['events'][-1]['id'], expected_scope=SCOPE,
                                         now=NOW, max_age_seconds=100, verified_evidence=[receipt])
                helper_seconds += time.perf_counter() - before
            else:
                text_chars.append(0)  # host retains continue locally within this synthetic batch
        loop_seconds = time.perf_counter() - loop_start
        total_seconds = time.perf_counter() - total_start
    return dict(mode=mode, observations=calls, checked_checks=checks_checked, business_wait_seconds=0,
                new_text_characters=distribution(text_chars), text_per_observation=text_chars,
                image_count=0, image_bytes=0, model_requests=None, model_requests_reason='no host model logs',
                context_tokens=None, compression_events=None, token_measurement=None,
                tool_seconds=tool_seconds, helper_seconds=helper_seconds, evidence_save_seconds=save_seconds,
                setup_seconds=setup_seconds, fix_seconds=0, recovery_seconds=recovery_seconds,
                loop_wall_seconds=loop_seconds, total_wall_seconds=total_seconds,
                total_scope='setup + measured loop including recovery; excludes temporary-directory cleanup',
                fixed_errors=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--samples', type=int, default=40)
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--payload-chars', type=int, default=20000)
    args = parser.parse_args()
    if not (1 <= args.samples <= 1000 and 1 <= args.runs <= 20 and 100 <= args.payload_chars <= 1000000):
        parser.error('bounded synthetic parameters required')
    start = time.perf_counter()
    rows = []
    for run in range(args.runs):
        order = ['full','summary'] if run % 2 == 0 else ['summary','full']
        for mode in order:
            rows.append(dict(run=run+1, **run_arm(mode, args.samples, args.payload_chars)))
    result = dict(schema_version=1, experiment='local synthetic evidence-preserving full vs summary',
                  python=sys.version.split()[0], samples=args.samples, runs=args.runs, results=rows,
                  experiment_wall_seconds=time.perf_counter()-start,
                  limitations=['No real model or browser calls; model/context/compression metrics unknown.',
                    'No image workload; visual-reference retention has separate tests.',
                    'Zero business wait is identical in both arms; no long-run compression claim.',
                    'Tool metric is synthetic callable execution, not a host API.',
                    'Development/setup debugging outside this executable is not benchmark time.'])
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'runs': len(rows),
                      'experiment_wall_seconds': result['experiment_wall_seconds']}))


if __name__ == '__main__':
    main()
