"""Verify reuse, optimization brackets, and measurements without NumPy/SciPy."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from goodhart_audit.core import rank_weights
from experiments.verify_anytime_results import verify as verify_measurements


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read_rows(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def check_design(weights, design, tolerance):
    q, rho = design['proposal'], design['rho']
    if len(q) != len(weights[0]) or any(not math.isfinite(x) or x <= 0 for x in q):
        raise ValueError('rank proposal must have full positive support')
    if not math.isclose(math.fsum(q), 1., abs_tol=1e-12, rel_tol=0):
        raise ValueError('proposal not normalized')
    if not math.isfinite(rho) or rho < 0:
        raise ValueError('invalid rho')
    records = design['dual_weights']
    if not records or any(not math.isfinite(r['weight']) or r['weight'] < 0 for r in records):
        raise ValueError('invalid dual simplex weights')
    if not math.isclose(math.fsum(r['weight'] for r in records), 1., abs_tol=1e-12, rel_tol=0):
        raise ValueError('dual weights not normalized')
    moments = [math.fsum(a*a/qi for a, qi in zip(row, q)) for row in weights]
    upper = max(v + rho*max(a/qi for a, qi in zip(row, q)) for v, row in zip(moments, weights))
    columns = [[] for _ in q]
    for record in records:
        k, i, probability = record['target'], record['coordinate'], record['weight']
        if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k < len(weights):
            raise ValueError('invalid dual target')
        if (rho == 0 and i is not None) or (rho > 0 and (isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(q))):
            raise ValueError('invalid dual coordinate')
        for j, a in enumerate(weights[k]):
            columns[j].append(probability * (a*a + (rho*a if i == j else 0.)))
    lower = math.fsum(math.sqrt(math.fsum(column)) for column in columns)**2
    gap = (upper-lower)/lower
    if gap < -1e-10 or gap > tolerance + 1e-10:
        raise ValueError('optimization bracket exceeds tolerance')
    for key, value in [('primal_value', upper), ('dual_value', lower), ('relative_gap', gap)]:
        if not math.isclose(value, design[key], rel_tol=1e-9, abs_tol=1e-10):
            raise ValueError('optimization value mismatch: ' + key)
    return upper, lower


def verify(out):
    out = Path(out)
    counts = verify_measurements(out)
    manifest = json.loads((out / 'manifest.json').read_text())
    followup, combined = manifest['followup_protocol'], manifest['protocol']
    if canonical_hash(followup) != manifest['followup_protocol_sha256']:
        raise ValueError('follow-up protocol checksum mismatch')
    base = Path(followup['base_results'])
    verify_measurements(base)
    base_manifest = json.loads((base / 'manifest.json').read_text())
    if hashlib.sha256((base / 'manifest.json').read_bytes()).hexdigest() != manifest['base_manifest_sha256']:
        raise ValueError('base manifest differs')
    if manifest['base_manifest_sha256'] != followup['base_manifest_sha256']:
        raise ValueError('base release pin differs')
    base_config = json.loads(Path(followup['base_protocol']).read_text())
    if base_config != base_manifest['protocol'] or combined != {**base_config, 'methods': base_config['methods'] + followup['new_methods']}:
        raise ValueError('combined protocol differs from the fixed base')
    original = read_rows(base / 'replicates.csv')
    reused = [row for row in read_rows(out / 'replicates.csv') if row['method'] in base_config['methods']]
    if reused != original:
        raise ValueError('reused measurements changed')
    designs = json.loads((out / 'designs.json').read_text())
    if set(designs) != set(followup['new_methods']):
        raise ValueError('missing optimized design')
    weights = [rank_weights(combined['pool_size'], n) for n in combined['budgets']]
    for method, design in designs.items():
        if design['rho'] != followup['rho'][method]:
            raise ValueError('rho differs from protocol')
        check_design(weights, design, followup['relative_optimization_gap'])
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results/design')
    args = parser.parse_args()
    paths, checkpoints, groups = verify(args.results)
    print(f'Verified reuse, numerical primal-dual brackets, {paths} paths, {checkpoints} checkpoints, {groups} aggregates.')


if __name__ == '__main__':
    main()
