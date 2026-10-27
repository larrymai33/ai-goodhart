"""Check the saved anytime study using only Python's standard library."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path


def _read(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def _bool(value):
    if value not in ('True', 'False'):
        raise ValueError('invalid boolean in result table')
    return value == 'True'


def verify(out):
    out = Path(out)
    manifest = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
    protocol = manifest['protocol']
    encoded = json.dumps(protocol, sort_keys=True, separators=(',', ':')).encode()
    if hashlib.sha256(encoded).hexdigest() != manifest['protocol_sha256']:
        raise ValueError('protocol checksum mismatch')
    for name, digest in manifest['source_sha256'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError('source checksum mismatch: ' + name)
    for name, digest in manifest['outputs_sha256'].items():
        if hashlib.sha256((out / name).read_bytes()).hexdigest() != digest:
            raise ValueError('output checksum mismatch: ' + name)
    rows = _read(out / 'replicates.csv')
    summaries = _read(out / 'summary.csv')
    grouped, paths = defaultdict(list), defaultdict(list)
    expected = {(case, method, str(labels)) for case in protocol['scenarios']
                for method in protocol['methods'] for labels in protocol['label_checkpoints']}
    for row in rows:
        key = row['scenario'], row['method'], row['labels']
        if key not in expected:
            raise ValueError('unexpected result setting')
        grouped[key].append(row)
        paths[row['scenario'], row['method'], row['replicate']].append(row)
        certified = int(row['certified_count'])
        certified_safe = int(row['certified_safe_count'])
        truly_safe = int(row['truly_safe_count'])
        if not 0 <= certified_safe <= min(certified, truly_safe) <= len(protocol['budgets']):
            raise ValueError('inconsistent certification counts')
        first = row['first_full_budget_certified']
        if first:
            if not 1 <= int(first) <= int(row['labels']):
                raise ValueError('stopping time outside observed prefix')
            if not _bool(row['full_budget_truly_safe']) and not _bool(row['ever_false_certification']):
                raise ValueError('unsafe full-budget success without recorded error')
    if set(grouped) != expected or len(summaries) != len(expected):
        raise ValueError('missing result settings')
    for path in paths.values():
        path.sort(key=lambda row: int(row['labels']))
        if [int(row['labels']) for row in path] != protocol['label_checkpoints']:
            raise ValueError('missing or duplicate checkpoint in a path')
        for metric in ['ever_miscoverage', 'ever_false_certification']:
            observed = [_bool(row[metric]) for row in path]
            if observed != sorted(observed):
                raise ValueError('ever-event decreased over time')
        first_times = [int(row['first_full_budget_certified']) for row in path if row['first_full_budget_certified']]
        if first_times and len(set(first_times)) != 1:
            raise ValueError('first certification time changed')
    metrics = ['ever_miscoverage', 'ever_false_certification', 'certified_count',
               'ever_certified_count', 'certified_safe_count']
    for summary in summaries:
        group = grouped[summary['scenario'], summary['method'], summary['labels']]
        if len(group) != protocol['replicates'] or {int(row['replicate']) for row in group} != set(range(protocol['replicates'])):
            raise ValueError('incorrect repetition count or duplicate ID')
        for metric in metrics:
            values = [float(_bool(row[metric])) if metric in metrics[:2] else float(row[metric]) for row in group]
            mean = math.fsum(values) / len(values)
            if not math.isclose(mean, float(summary[metric]), rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError('aggregate mismatch: ' + metric)
        successes = sorted(int(row['first_full_budget_certified']) for row in group if row['first_full_budget_certified'])
        rate = len(successes) / len(group)
        if not math.isclose(rate, float(summary['full_budget_certification_rate']), abs_tol=1e-12):
            raise ValueError('censoring/certification rate mismatch')
        if successes:
            n = len(successes)
            median = (successes[(n - 1) // 2] + successes[n // 2]) / 2
            if median != float(summary['median_labels_among_full_budget_successes']):
                raise ValueError('conditional median mismatch')
        elif summary['median_labels_among_full_budget_successes']:
            raise ValueError('censored runs must not be reported as successful stopping')
    return len(paths), len(rows), len(summaries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results/anytime')
    args = parser.parse_args()
    paths, rows, groups = verify(args.results)
    print(f'Verified hashes, {paths} method paths, {rows} checkpoints, {groups} aggregates, and censoring/event invariants.')


if __name__ == '__main__':
    main()
