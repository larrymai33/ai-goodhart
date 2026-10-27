"""Reproduce synthetic experiments with already-installed NumPy/Matplotlib.

No network requests, dependency installation, or model inference. Run from the
repository root: python -m experiments.run_study
"""

from __future__ import annotations

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

from goodhart_audit.core import envelope_proposal, full_envelope, rank_weights


def make_scenarios(prompts, m, seed):
    if prompts < 32 or m < 16:
        raise ValueError('study needs at least 32 prompts and 16 ranks')
    rng = np.random.default_rng(seed)
    shape = (prompts, m)
    cases = {}
    cases['rare_top'] = np.zeros(shape)
    cases['rare_top'][:max(1, prompts // 32), 0] = 1
    cases['top_failure'] = np.zeros(shape)
    cases['top_failure'][:, 0] = 1
    cases['interior_band'] = np.zeros(shape)
    cases['interior_band'][:prompts // 2, m // 4:m // 2] = 1
    cases['bottom_band'] = np.zeros(shape)
    cases['bottom_band'][:, 3 * m // 4:] = 1
    # Exactly the same prevalence at every rank, with diverse failing prompts.
    cases['flat_risk'] = np.zeros(shape)
    for rank in range(m):
        cases['flat_risk'][rng.choice(prompts, prompts // 8, replace=False), rank] = 1
    cases['goodhart_turn'] = np.zeros(shape)
    rates = np.full(m, 0.02)
    rates[:max(1, m // 32)] = 0.5
    rates[m // 3:] = 0.18
    for rank, rate in enumerate(rates):
        cases['goodhart_turn'][rng.choice(prompts, round(rate * prompts), replace=False), rank] = 1
    cases['prompt_cluster'] = np.zeros(shape)
    cases['prompt_cluster'][:prompts // 16, :] = 1
    cases['all_safe'] = np.zeros(shape)
    return cases


def proposals(m, budgets):
    all_weights = np.array([rank_weights(m, n) for n in range(1, m + 1)])
    dyadic = sorted(set([2 ** j for j in range(m.bit_length()) if 2 ** j <= m] + [m]))
    q, _ = envelope_proposal(m, budgets)
    uniform = np.ones(m) / m
    return {'uniform': uniform,
            'budget_mixture': all_weights.mean(axis=0),
            'dyadic_mixture': all_weights[np.array(dyadic) - 1].mean(axis=0),
            'max_uniform': 0.5 * uniform + 0.5 * all_weights[-1],
            'envelope': np.array(q)}


def wilson(successes, trials):
    if trials < 1:
        raise ValueError('trials must be positive')
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0., center - half), min(1., center + half)


def evaluate_draws(loss, weights, q, prompt_ids, ranks, delta, threshold):
    b = len(ranks)
    p, m = loss.shape
    observed = loss[prompt_ids, ranks]
    # Sufficient statistics avoid retaining a B x K importance matrix.
    sums_by_rank = np.bincount(ranks, weights=observed, minlength=m)
    squares_by_rank = np.bincount(ranks, weights=observed * observed, minlength=m)
    ratios = weights / q
    means = ratios @ sums_by_rank / b
    second = ratios ** 2 @ squares_by_rank
    variance = np.maximum(0., (second - b * means ** 2) / (b - 1))
    max_weight = ratios.max(axis=1)
    log_term = math.log(4 * len(weights) / delta)
    radius = np.sqrt(2 * variance * log_term / b) + 7 * max_weight * log_term / (3 * (b - 1))
    lower, upper = np.maximum(0., means - radius), np.minimum(1., means + radius)
    # Clip both endpoints to the feasible parameter space, retaining diagnostics.
    lower = np.minimum(1., lower)
    upper = np.maximum(0., upper)
    unique = np.unique(prompt_ids * m + ranks)
    unique_p, unique_r = unique // m, unique % m
    known_loss = np.bincount(unique_r, weights=loss[unique_p, unique_r], minlength=m)
    known_count = np.bincount(unique_r, minlength=m)
    identification_lower = weights @ known_loss / p
    identification_upper = identification_lower + weights @ (1 - known_count / p)
    combined_lower = np.maximum(lower, identification_lower)
    combined_upper = np.minimum(upper, identification_upper)
    truth = weights @ loss.mean(axis=0)
    naive_radius = 1.959963984540054 * np.sqrt(variance / b)
    naive_lower = np.clip(means - naive_radius, 0, 1)
    naive_upper = np.clip(means + naive_radius, 0, 1)
    covered = (lower <= truth + 1e-12) & (truth <= upper + 1e-12)
    combined_covered = (combined_lower <= truth + 1e-12) & (truth <= combined_upper + 1e-12)
    certified = (combined_upper <= threshold) & (combined_lower <= combined_upper)
    return {'estimate': means, 'lower': lower, 'upper': upper,
            'identification_lower': identification_lower, 'identification_upper': identification_upper,
            'naive_upper': naive_upper,
            'max_curve_error': float(np.max(np.abs(means - truth))),
            'curve_mse': float(np.mean((means - truth) ** 2)),
            'simultaneous_coverage': bool(covered.all()),
            'mean_width': float(np.mean(upper - lower)),
            'combined_coverage': bool(combined_covered.all()),
            'combined_width': float(np.mean(np.maximum(0, combined_upper - combined_lower))),
            'false_certification': bool(np.any(certified & (truth > threshold))),
            'unique_labels': len(unique), 'certified_count': int(certified.sum()),
            'naive_coverage': bool(np.all((naive_lower <= truth + 1e-12) & (truth <= naive_upper + 1e-12))),
            'naive_false_certification': bool(np.any((naive_upper <= threshold) & (truth > threshold)))}


def make_plots(out, aggregates, truths, budgets, scaling, config):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.hashsalt': 'rank-envelope-v1'})
    colors = {'uniform': '#64748b', 'budget_mixture': '#d97706',
              'dyadic_mixture': '#0891b2', 'max_uniform': '#a855f7', 'envelope': '#dc2626'}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    sizes = [r['pool_size'] for r in scaling]
    axes[0].plot(sizes, [r['normalizer'] for r in scaling], 'o-', color=colors['envelope'], label='Full-grid envelope Z')
    axes[0].plot(sizes, [r['harmonic_upper'] for r in scaling], '--', color='#475569', label='Harmonic upper bound')
    axes[0].plot(sizes, [r['lower_bound'] for r in scaling], ':', color='#0891b2', label='Exact lower bound')
    axes[0].set(xscale='log', xlabel='Maximum budget N = pool size M', ylabel='Worst-case importance weight', title='Logarithmic envelope overhead')
    axes[0].legend(frameon=False, fontsize=8)
    for name in [c for c in ['top_failure', 'goodhart_turn', 'interior_band', 'flat_risk'] if c in truths]:
        axes[1].plot(budgets, truths[name], 'o-', label=name.replace('_', ' '))
    axes[1].set(xscale='log', xlabel='Best-of-N budget', ylabel='Exact finite-pool loss', title='Constructed risks include nonmonotone curves')
    axes[1].legend(frameon=False, fontsize=8)
    fig.savefig(out / 'theory_and_risks.svg', metadata={'Date': None})
    fig.savefig(out / 'theory_and_risks.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.1), constrained_layout=True)
    plot_cases = [c for c in ['top_failure', 'flat_risk', 'bottom_band'] if c in config['scenarios']]
    if not plot_cases:
        plot_cases = config['scenarios'][:3]
    for ax, case in zip(axes, plot_cases):
        for method in config['methods']:
            rows = [a for a in aggregates if a['scenario'] == case and a['method'] == method]
            ax.plot([a['draws'] for a in rows], [a['curve_mse'] for a in rows], 'o-',
                    color=colors[method], label=method.replace('_', ' '))
        ax.set(xscale='log', yscale='log', xlabel='Fixed sampling draws', ylabel='Mean curve squared error', title=case.replace('_', ' '))
    for ax in axes[len(plot_cases):]:
        ax.set_visible(False)
    axes[len(plot_cases) - 1].legend(frameon=False, fontsize=8)
    fig.savefig(out / 'estimation_tradeoffs.svg', metadata={'Date': None})
    fig.savefig(out / 'estimation_tradeoffs.png', dpi=160)
    plt.close(fig)
    selected_draws = 256 if 256 in config['draw_counts'] else max(config['draw_counts'])
    cases = config['scenarios']
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), constrained_layout=True)
    for method in [m for m in ['uniform', 'dyadic_mixture', 'envelope'] if m in config['methods']]:
        rows = [next(a for a in aggregates if a['scenario'] == c and a['method'] == method and a['draws'] == selected_draws) for c in cases]
        axes[0].plot(range(len(cases)), [a['simultaneous_coverage'] for a in rows], 'o-', color=colors[method], label=method.replace('_', ' '))
        axes[1].plot(range(len(cases)), [a['naive_coverage'] for a in rows], 'o-', color=colors[method], label=method.replace('_', ' '))
    for ax in axes:
        ax.axhline(0.95, color='#111827', linestyle='--', linewidth=1)
        ax.set_xticks(range(len(cases)), [c.replace('_', '\n') for c in cases], fontsize=8)
        ax.set(ylim=(-0.04, 1.04), ylabel='Fraction covering every target budget')
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_title(f'Simultaneous empirical Bernstein bands ({selected_draws} draws)')
    axes[1].set_title('Naive pointwise normal bands (invalid reference)')
    fig.savefig(out / 'coverage.svg', metadata={'Date': None})
    fig.savefig(out / 'coverage.png', dpi=160)
    plt.close(fig)


def run(config, out, plots=True):
    p, m = config['prompts'], config['pool_size']
    budgets = config['budgets']
    if 1 not in budgets or m not in budgets:
        raise ValueError('the synthetic study requires baseline budget 1 and the full-pool budget')
    if any(isinstance(b, bool) or not isinstance(b, int) or b < 2 for b in config['draw_counts']):
        raise ValueError('draw counts must be integers >=2')
    if not config['draw_counts'] or len(set(config['draw_counts'])) != len(config['draw_counts']):
        raise ValueError('draw counts must be nonempty and unique')
    if not isinstance(config['replicates'], int) or config['replicates'] < 2:
        raise ValueError('at least two replicates are required')
    if not 0 < config['delta'] < 1 or not 0 <= config['risk_threshold'] <= 1:
        raise ValueError('invalid confidence level or risk threshold')
    weights = np.array([rank_weights(m, n) for n in budgets])
    available_methods = proposals(m, budgets)
    selected = config['methods']
    if not selected or len(set(selected)) != len(selected) or any(x not in available_methods for x in selected):
        raise ValueError('methods must be nonempty, unique, known proposal names')
    methods = {name: available_methods[name] for name in selected}
    available_cases = make_scenarios(p, m, config['seed'])
    selected_cases = config['scenarios']
    if not selected_cases or len(set(selected_cases)) != len(selected_cases) or any(x not in available_cases for x in selected_cases):
        raise ValueError('scenarios must be nonempty, unique, known scenario names')
    cases = {name: available_cases[name] for name in selected_cases}
    out.mkdir(parents=True, exist_ok=True)
    truths = {name: (weights @ loss.mean(axis=0)).tolist() for name, loss in cases.items()}
    metrics = config['primary_metrics'] + config['secondary_metrics']
    records = []
    per_budget = []
    for case_index, name in enumerate(config['scenarios']):
        loss = cases[name]
        sums = {(method, b): np.zeros(len(budgets)) for method in methods for b in config['draw_counts']}
        sums_sq = {key: np.zeros(len(budgets)) for key in sums}
        for replicate in range(config['replicates']):
            rng = np.random.default_rng(np.random.SeedSequence([config['seed'], case_index, replicate]))
            prompt_ids = rng.integers(0, p, max(config['draw_counts']))
            uniforms = rng.random(max(config['draw_counts']))
            for method, q in methods.items():
                cumulative = np.cumsum(q)
                cumulative[-1] = 1.
                ranks = np.searchsorted(cumulative, uniforms)
                for b in config['draw_counts']:
                    result = evaluate_draws(loss, weights, q, prompt_ids[:b], ranks[:b],
                                            config['delta'], config['risk_threshold'])
                    record = {'scenario': name, 'method': method, 'draws': b, 'replicate': replicate}
                    record.update({key: result[key] for key in metrics})
                    records.append(record)
                    error = result['estimate'] - np.array(truths[name])
                    sums[method, b] += result['estimate']
                    sums_sq[method, b] += error ** 2
        for (method, b), total in sums.items():
            q = methods[method]
            for i, n in enumerate(budgets):
                true_risk = truths[name][i]
                variance = float(np.sum(weights[i] ** 2 * loss.mean(axis=0) / q) - true_risk ** 2)
                per_budget.append({'scenario': name, 'method': method, 'draws': b, 'budget': n,
                                   'truth': true_risk, 'mean_estimate': float(total[i] / config['replicates']),
                                   'mse': float(sums_sq[method, b][i] / config['replicates']),
                                   'analytic_mse': max(0., variance) / b})
        print(f'Completed {name}: {config["replicates"]} paired replicates', flush=True)
    aggregates = []
    for name in config['scenarios']:
        for method in methods:
            for b in config['draw_counts']:
                rows = [r for r in records if r['scenario'] == name and r['method'] == method and r['draws'] == b]
                row = {'scenario': name, 'method': method, 'draws': b, 'replicates': len(rows)}
                for metric in metrics:
                    values = np.array([r[metric] for r in rows], dtype=float)
                    row[metric] = float(values.mean())
                    row[metric + '_mcse'] = float(values.std(ddof=1) / math.sqrt(len(rows)))
                    if metric.endswith('coverage') or metric.endswith('certification'):
                        low, high = wilson(int(values.sum()), len(rows))
                        row[metric + '_wilson_low'] = low
                        row[metric + '_wilson_high'] = high
                aggregates.append(row)
    scaling = []
    for size in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096]:
        _, z = full_envelope(size)
        harmonic = sum(1 / n for n in range(1, size + 1))
        lower = 1 + sum(math.exp((n - 1) * math.log1p(-1 / n)) / n for n in range(2, size + 1))
        scaling.append({'pool_size': size, 'normalizer': z, 'lower_bound': lower,
                        'harmonic_upper': harmonic, 'uniform_max_weight': size})
    output_names = []
    for filename, rows in [('replicates.csv', records), ('summary.csv', aggregates),
                           ('per_budget.csv', per_budget), ('scaling.csv', scaling)]:
        with (out / filename).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        output_names.append(filename)
    if plots:
        make_plots(out, aggregates, truths, budgets, scaling, config)
        output_names.extend(stem + extension for stem in ['theory_and_risks', 'estimation_tradeoffs', 'coverage']
                            for extension in ['.svg', '.png'])
    normalized_config = json.dumps(config, sort_keys=True, separators=(',', ':'))
    manifest = {'protocol': config, 'protocol_sha256': hashlib.sha256(normalized_config.encode()).hexdigest(),
                'python': sys.version.split()[0], 'numpy': np.__version__, 'platform': platform.platform(),
                'source_sha256': {str(path).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in [Path('goodhart_audit/core.py'), Path('experiments/run_study.py')]},
                'pool_loss_sha256': {name: hashlib.sha256(loss.astype('uint8').tobytes()).hexdigest()
                                     for name, loss in cases.items()},
                'true_risk_curves': truths,
                'proposal_max_weights': {name: float(np.max(weights / q)) for name, q in methods.items()},
                'outputs_sha256': {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                                   for name in sorted(output_names)}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return aggregates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=Path('experiments/protocol.json'))
    parser.add_argument('--out', type=Path, default=Path('results'))
    parser.add_argument('--replicates', type=int, help='Override for smoke test; recorded in manifest')
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.protocol.read_text(encoding='utf-8'))
    if args.replicates is not None:
        config['replicates'] = args.replicates
    if config['replicates'] < 2:
        parser.error('at least two replicates are required')
    started = time.monotonic()
    run(config, args.out, not args.no_plots)
    print(f'Finished in {time.monotonic() - started:.1f}s; outputs: {args.out}')


if __name__ == '__main__':
    main()
