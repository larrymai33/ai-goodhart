"""Validate saved outputs, aggregation, and analytic importance-sampling MSE.

Uses only the standard library. This is a reproducibility check, not a substitute
for rerunning the Monte Carlo experiment or reviewing its scientific assumptions.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from collections import defaultdict


def verify(directory):
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    for name, digest in manifest['outputs_sha256'].items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f'output checksum mismatch: {name}')
    for name, digest in manifest['source_sha256'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'source checksum mismatch: {name}; rerun the study after code changes')
    protocol = manifest['protocol']
    encoded = json.dumps(protocol, sort_keys=True, separators=(',', ':')).encode()
    if hashlib.sha256(encoded).hexdigest() != manifest['protocol_sha256']:
        raise ValueError('protocol checksum mismatch')
    groups = defaultdict(list)
    with (directory / 'replicates.csv').open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            groups[row['scenario'], row['method'], row['draws']].append(row)
    metrics = protocol['primary_metrics'] + protocol['secondary_metrics']
    with (directory / 'summary.csv').open(newline='', encoding='utf-8') as stream:
        summaries = list(csv.DictReader(stream))
    expected_groups = len(protocol['scenarios']) * len(protocol['methods']) * len(protocol['draw_counts'])
    if len(groups) != expected_groups or len(summaries) != expected_groups:
        raise ValueError('missing experiment groups')
    def numeric(value):
        return {'True': 1., 'False': 0.}.get(value, value)
    for summary in summaries:
        rows = groups[summary['scenario'], summary['method'], summary['draws']]
        if len(rows) != protocol['replicates'] or len({r['replicate'] for r in rows}) != len(rows):
            raise ValueError('missing or duplicate replicates')
        for metric in metrics:
            mean = math.fsum(float(numeric(r[metric])) for r in rows) / len(rows)
            if not math.isclose(mean, float(summary[metric]), rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError(f'aggregation mismatch: {metric}')
    from goodhart_audit.core import rank_weights, envelope_proposal
    m = protocol['pool_size']
    weights = [rank_weights(m, n) for n in protocol['budgets']]
    q, _ = envelope_proposal(m, protocol['budgets'])
    expected_ratio = max(w / probability for row in weights for w, probability in zip(row, q))
    if not math.isclose(expected_ratio, manifest['proposal_max_weights']['envelope'], rel_tol=1e-10):
        raise ValueError('envelope ratio mismatch')
    # Aggregate MSE must equal the arithmetic mean of the per-budget MSEs.
    per_budget = defaultdict(list)
    with (directory / 'per_budget.csv').open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            per_budget[row['scenario'], row['method'], row['draws']].append(row)
    for summary in summaries:
        rows = per_budget[summary['scenario'], summary['method'], summary['draws']]
        if len(rows) != len(protocol['budgets']):
            raise ValueError('missing per-budget outputs')
        mse = math.fsum(float(r['mse']) for r in rows) / len(rows)
        if not math.isclose(mse, float(summary['curve_mse']), rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError('per-budget MSE aggregation mismatch')
    # For binary top-only loss, at n=m the exact per-draw variance is 1/q(1)-1.
    top = next(r for r in per_budget['top_failure', 'envelope', str(protocol['draw_counts'][0])]
               if int(r['budget']) == m)
    analytic = (1 / q[0] - 1) / int(top['draws'])
    if not math.isclose(analytic, float(top['analytic_mse']), rel_tol=1e-10):
        raise ValueError('analytic top-rank MSE identity mismatch')
    return sum(len(rows) for rows in groups.values()), len(summaries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results')
    args = parser.parse_args()
    count, groups = verify(args.results)
    print(f'Verified checksums, {count} audit evaluations, {groups} aggregates, per-budget MSE, and analytic top-rank variance.')


if __name__ == '__main__':
    main()
