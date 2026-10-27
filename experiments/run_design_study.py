"""Compare attributed optimized proposals with the frozen v0.2 audit study."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy

from goodhart_audit.core import rank_weights
from goodhart_audit.design import optimize_design
from experiments.run_study import make_scenarios, wilson
from experiments.run_anytime_study import race_orders, simulate_paths, SOURCE_FILES as BASE_SOURCES
from experiments.verify_anytime_results import verify as verify_base


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def inputs(config):
    base = Path(config['base_results'])
    files = list(BASE_SOURCES) + ['goodhart_audit/design.py', 'experiments/run_design_study.py',
                                'experiments/verify_anytime_results.py', 'experiments/verify_design_results.py',
                                str(config['base_protocol'])]
    files.extend(str(base / name) for name in ['manifest.json', 'replicates.csv', 'summary.csv'])
    return {name: digest(name) for name in files}


def read_rows(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def flag(value):
    if value in (True, 'True'):
        return True
    if value in (False, 'False'):
        return False
    raise ValueError('invalid boolean measurement')


def summarize(rows, config):
    """Same reported outcomes as v0.2, accepting original CSV or fresh rows."""
    summaries = []
    for case in config['scenarios']:
        for method in config['methods']:
            for labels in config['label_checkpoints']:
                group = [r for r in rows if r['scenario'] == case and r['method'] == method and int(r['labels']) == labels]
                if len(group) != config['replicates']:
                    raise ValueError('incorrect number of paired repetitions')
                summary = {'scenario': case, 'method': method, 'labels': labels,
                           'replicates': len(group), 'truly_safe_count': int(group[0]['truly_safe_count'])}
                for metric in ['ever_miscoverage', 'ever_false_certification', 'certified_count',
                               'ever_certified_count', 'certified_safe_count']:
                    binary = metric in ('ever_miscoverage', 'ever_false_certification')
                    values = np.array([flag(r[metric]) if binary else float(r[metric]) for r in group], dtype=float)
                    summary[metric] = float(values.mean())
                    summary[metric + '_mcse'] = float(values.std(ddof=1) / math.sqrt(len(values)))
                    if binary:
                        lower, upper = wilson(int(values.sum()), len(values))
                        summary[metric + '_wilson_low'], summary[metric + '_wilson_high'] = lower, upper
                stopping = [int(r['first_full_budget_certified']) for r in group
                            if r['first_full_budget_certified'] not in ('', None)]
                summary['full_budget_certification_rate'] = len(stopping) / len(group)
                summary['median_labels_among_full_budget_successes'] = float(np.median(stopping)) if stopping else None
                summary['full_budget_truly_safe'] = flag(group[0]['full_budget_truly_safe'])
                summaries.append(summary)
    return summaries


def run(followup, out):
    starting = inputs(followup)
    base = Path(followup['base_results'])
    out = Path(out)
    # Refuse overwrites before measurement: an after-write hash check cannot
    # protect frozen evidence if the caller points --out at an old release.
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('output directory must be new or empty; preserve existing evidence')
    planned = [(out / name).resolve() for name in ['replicates.csv', 'summary.csv', 'designs.json', 'manifest.json']]
    if set(planned) & {Path(name).resolve() for name in starting}:
        raise ValueError('output collides with a measured input')
    if digest(base / 'manifest.json') != followup['base_manifest_sha256']:
        raise ValueError('base manifest does not match the prespecified release pin')
    verify_base(base)
    base_manifest = json.loads((base / 'manifest.json').read_text())
    config = json.loads(Path(followup['base_protocol']).read_text())
    if config != base_manifest['protocol']:
        raise ValueError('base protocol does not match verified base results')
    new_methods = followup['new_methods']
    if (not new_methods or len(set(new_methods)) != len(new_methods) or
            set(new_methods) & set(config['methods'])):
        raise ValueError('new methods must be distinct and absent from base results')
    if followup['certification_rule'] != 'upper-test':
        raise ValueError('the frozen engine measures only the directional upper-test rule')
    tolerance = followup['relative_optimization_gap']
    p, m = config['prompts'], config['pool_size']
    weights = np.array([rank_weights(m, n) for n in config['budgets']])
    designs = {}
    for method in new_methods:
        rho = followup['rho'][method]
        design = optimize_design(weights, rho=rho, tolerance=tolerance)
        designs[method] = {'rho': rho, **design}
        print(f'Design {method}: relative primal-dual gap {design["relative_gap"]:.3g}', flush=True)
    cases = make_scenarios(p, m, config['seed'])
    rows = read_rows(base / 'replicates.csv')
    for case_index, name in enumerate(config['scenarios']):
        loss = cases[name]
        if digest_label_table(loss) != base_manifest['loss_table_sha256'][name]:
            raise ValueError('synthetic table differs from base study')
        rng = np.random.default_rng(np.random.SeedSequence([config['seed'], case_index]))
        uniforms = rng.random((config['replicates'], p * m))
        for method, design in designs.items():
            q = np.array(design['proposal'])
            order = race_orders(q, p, uniforms)
            measured = simulate_paths(loss, weights, q, order, config['label_checkpoints'],
                                      config['delta'], config['risk_threshold'], config['bet_fractions'])
            rows.extend({'scenario': name, 'method': method, **row} for row in measured)
        print(f'Completed {name}: {config["replicates"]} paired paths per new method', flush=True)
    combined = {**config, 'methods': config['methods'] + new_methods}
    summaries = summarize(rows, combined)
    if inputs(followup) != starting:
        raise RuntimeError('source or reused evidence changed during the study; freeze and rerun')
    out.mkdir(parents=True, exist_ok=True)
    for name, values in [('replicates.csv', rows), ('summary.csv', summaries)]:
        with (out / name).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows(values)
    (out / 'designs.json').write_text(json.dumps(designs, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    if inputs(followup) != starting:
        raise RuntimeError('source or reused evidence changed while writing results; freeze and rerun')
    manifest = {'protocol': combined, 'protocol_sha256': canonical_hash(combined),
                'followup_protocol': followup, 'followup_protocol_sha256': canonical_hash(followup),
                'base_manifest_sha256': starting[str(base / 'manifest.json')],
                'source_sha256': starting,
                'outputs_sha256': {name: digest(out / name) for name in ['replicates.csv', 'summary.csv', 'designs.json']},
                'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': scipy.__version__,
                'platform': platform.platform(), 'true_risks': base_manifest['true_risks'],
                'loss_table_sha256': base_manifest['loss_table_sha256'],
                'reused_method_paths': len(config['scenarios']) * len(config['methods']) * config['replicates'],
                'new_method_paths': len(config['scenarios']) * len(new_methods) * config['replicates'],
                'evaluation_scope': 'Frozen v0.2 upper-test rule; previously observed synthetic scenarios, not a new holdout.'}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return summaries


def digest_label_table(loss):
    return hashlib.sha256(loss.astype('uint8').tobytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=Path('experiments/design_protocol.json'))
    parser.add_argument('--out', type=Path, default=Path('results/design'))
    args = parser.parse_args()
    start = time.monotonic()
    run(json.loads(args.protocol.read_text()), args.out)
    print(f'Finished in {time.monotonic() - start:.1f}s; outputs: {args.out}')


if __name__ == '__main__':
    main()
