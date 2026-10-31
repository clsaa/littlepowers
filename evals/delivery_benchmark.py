#!/usr/bin/env python3
"""Paired measurement. Writes one new report; no models, installs or network."""
import argparse
import json
from pathlib import Path
import platform
import statistics
import tempfile
import time

from delivery_fixture import CASES, CLAIMS, learning_demo, run_variant


def benchmark(runs=3, count=6000):
    if type(runs) is not int or not 1 <= runs <= 20 or not 3 <= count <= 100000:
        raise ValueError('runs must be 1..20; count must be 3..100000')
    started = time.perf_counter_ns()
    pairs = []
    with tempfile.TemporaryDirectory(prefix='littlepowers-delivery-') as directory:
        base = Path(directory)
        for index in range(runs):
            order = ['baseline', 'candidate'] if index % 2 == 0 else ['candidate', 'baseline']
            pair = dict(order=order)
            for variant in order:
                pair[variant] = run_variant(base / f'{index}-{variant}', variant, count)
            for left, right in zip(pair['baseline']['cases'], pair['candidate']['cases']):
                assert left['case'] == right['case']
                assert left['covered'] == right['covered'] == sorted(CLAIMS)
                assert left['failed'] == right['failed'], 'changed defect detection'
            pair['learning'] = learning_demo(base / f'{index}-candidate', pair['baseline'], pair['candidate'])
            pairs.append(pair)
    totals = {variant: statistics.median(pair[variant]['total_ms'] for pair in pairs)
              for variant in ('baseline', 'candidate')}
    return dict(evidence_level='local deterministic fixture', python=platform.python_version(),
        runs=runs, cases=CASES, pairs=pairs, median_total_ms=totals,
        candidate_faster_in_this_fixture=totals['candidate'] < totals['baseline'],
        report_elapsed_ms=(time.perf_counter_ns() - started) / 1_000_000,
        model_tokens=None, authenticated_other_hosts=False, long_term_rework=None,
        limits='Temporary evidence was verified during each run; original payloads are embedded. '
               'No model-speed, host-certification or long-term rework claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--records', type=int, default=6000)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output must be a new path; preserve earlier evidence')
    result = benchmark(args.runs, args.records)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(dict(output=str(args.output.resolve()), runs=args.runs,
        median_total_ms=result['median_total_ms'],
        check_executions={k: result['pairs'][0][k]['check_executions'] for k in ('baseline', 'candidate')},
        candidate_faster_in_this_fixture=result['candidate_faster_in_this_fixture'])))


if __name__ == '__main__':
    main()
