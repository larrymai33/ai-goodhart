"""Offline, paired comparison of anytime audits at equal unique-label cost."""

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

from goodhart_audit.core import rank_weights
from goodhart_audit.unique_io import rank_proposal
from experiments.run_study import make_scenarios, wilson


SOURCE_FILES = ['goodhart_audit/core.py', 'goodhart_audit/anytime.py', 'goodhart_audit/unique_io.py',
                'experiments/run_study.py', 'experiments/run_anytime_study.py']


def source_hashes():
    return {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def race_orders(q, prompts, uniforms):
    """Independent exponential races; each row is one complete distinct order."""
    rates = np.tile(q / prompts, prompts)
    if uniforms.ndim != 2 or uniforms.shape[1] != len(rates):
        raise ValueError('uniform matrix has the wrong candidate dimension')
    if np.any(rates <= 0) or np.any((uniforms < 0) | (uniforms >= 1)):
        raise ValueError('study requires positive support and uniforms in [0,1)')
    times = -np.log1p(-uniforms) / rates
    return np.argsort(times, axis=1, kind='stable')


def _logmean(logs):
    if np.any(np.isnan(logs)):
        raise ArithmeticError('NaN in betting log wealth')
    maximum = logs.max(axis=-1)
    finite_maximum = np.where(np.isfinite(maximum), maximum, 0.)
    with np.errstate(divide='ignore', over='ignore'):
        result = finite_maximum + np.log(np.exp(logs - finite_maximum[..., None]).mean(axis=-1))
    return np.where(np.isneginf(maximum), -np.inf, np.where(np.isposinf(maximum), np.inf, result))


def _update(logs, numerator, denominator, active, fractions):
    """Increment fractional wealth; an inactive target leaves wealth unchanged."""
    positive = denominator > 0
    # A zero denominator at a feasible endpoint has a zero numerator.
    if np.any(active & ~positive & (numerator > 0)):
        raise ArithmeticError('incompatible endpoint in betting update')
    with np.errstate(divide='ignore'):
        log_ratio = np.log(numerator) - np.log(np.where(positive, denominator, 1.))
        log_ratio = np.where(~positive & (numerator == 0), 0., log_ratio)
        increments = np.logaddexp(np.log1p(-fractions), np.log(fractions) + log_ratio[..., None])
    logs += np.where(active[..., None], increments, 0.)


def _conditional_denominators(candidate, known, id_upper, remaining, ranges, active):
    """Use only prior-history endpoints; never condition rounding on the label."""
    from_lower = candidate - known
    from_upper = id_upper - candidate
    lower_tolerance = 8 * (np.spacing(candidate) + np.spacing(known))
    upper_tolerance = 8 * (np.spacing(candidate) + np.spacing(id_upper))
    if np.any(active & ((from_lower < -lower_tolerance) | (from_upper < -upper_tolerance))):
        raise ArithmeticError('candidate mean outside feasible betting range')
    from_lower, from_upper = np.maximum(0., from_lower), np.maximum(0., from_upper)
    closer_to_upper = from_upper < from_lower
    risk_numerator = np.where(closer_to_upper, remaining - from_upper, from_lower)
    complement_numerator = np.where(closer_to_upper, (ranges - remaining) + from_upper, ranges - from_lower)
    if np.any(active & ((risk_numerator < 0) | (complement_numerator < 0))):
        raise ArithmeticError('negative conditional risk or complement')
    mean, complement = np.zeros_like(known), np.ones_like(known)
    np.divide(risk_numerator, ranges, out=mean, where=active)
    np.divide(complement_numerator, ranges, out=complement, where=active)
    return mean, complement


def simulate_paths(loss, weights, q, orders, checkpoints, delta, threshold, bets, diagnostics=False):
    """Vectorize independent random paths, checking error events at every draw.

    Truth is used solely to evaluate coverage. Acquisition orders are supplied
    independently of labels. Every proposal uses the same target-wise scaling.
    """
    p, m = loss.shape
    q = np.asarray(q, dtype=float)
    q = q / math.fsum(q.tolist())
    weights = np.array([row / math.fsum(row.tolist()) for row in weights])
    repetitions = orders.shape[0]
    k = len(weights)
    max_labels = max(checkpoints)
    if max_labels > orders.shape[1] or max_labels > p * m:
        raise ValueError('checkpoints exceed available unique candidates')
    if np.any(q <= 0):
        raise ValueError('experiment requires full proposal support')
    for order in orders[:, :max_labels]:
        if len(np.unique(order)) != max_labels or np.any((order < 0) | (order >= p * m)):
            raise ValueError('each path must contain valid distinct candidate indices')
    fractions = np.array(bets, dtype=float)
    if np.any((fractions <= 0) | (fractions > 1)):
        raise ValueError('bet fractions must lie in (0,1]')
    threshold_log = math.log(2 * k / delta)
    truth = weights @ loss.mean(axis=0)
    ratios = weights / q
    priority = np.argsort(-ratios, axis=1, kind='stable')
    min_priority = np.argsort(ratios, axis=1, kind='stable')
    pointers = np.zeros((repetitions, k), dtype=int)
    min_pointers = pointers.copy()
    remaining_counts = np.full((repetitions, m), p, dtype=int)
    observed_loss_by_rank = np.zeros((repetitions, m))
    remaining_h = remaining_counts @ q / p
    known = np.zeros((repetitions, k))
    remaining_target = np.ones((repetitions, k))
    id_upper = np.ones((repetitions, k))
    upper_truth = np.zeros((repetitions, k, len(bets)))
    lower_truth = upper_truth.copy()
    upper_threshold = upper_truth.copy()
    failed = np.zeros(repetitions, dtype=bool)
    false_certificate = failed.copy()
    certified_ever = np.zeros((repetitions, k), dtype=bool)
    first_full = np.full(repetitions, -1, dtype=int)
    output = []
    rows = np.arange(repetitions)
    targets = np.arange(k)
    full_index = k - 1  # Validated ascending budget grid, ending at the pool size.
    for t in range(1, max_labels + 1):
        top_ranks = priority[targets[None, :], pointers]
        exhausted_top = remaining_counts[rows[:, None], top_ranks] == 0
        while np.any(exhausted_top & (pointers < m - 1)):
            pointers += exhausted_top & (pointers < m - 1)
            top_ranks = priority[targets[None, :], pointers]
            exhausted_top = remaining_counts[rows[:, None], top_ranks] == 0
        maximum = ratios[targets[None, :], top_ranks]
        bottom_ranks = min_priority[targets[None, :], min_pointers]
        exhausted_bottom = remaining_counts[rows[:, None], bottom_ranks] == 0
        while np.any(exhausted_bottom & (min_pointers < m - 1)):
            min_pointers += exhausted_bottom & (min_pointers < m - 1)
            bottom_ranks = min_priority[targets[None, :], min_pointers]
            exhausted_bottom = remaining_counts[rows[:, None], bottom_ranks] == 0
        minimum = ratios[targets[None, :], bottom_ranks]
        constant_ratio = minimum == maximum
        active = (maximum > 0) & ~exhausted_top
        ranges = np.where(constant_ratio, remaining_target, remaining_h[:, None] * maximum)
        indices = orders[:, t - 1]
        prompt_ids, ranks = indices // m, indices % m
        observed = loss[prompt_ids, ranks]
        y = np.zeros((repetitions, k))
        np.divide(ratios[:, ranks].T, maximum,
                  out=y, where=active)
        y *= observed[:, None]
        y = np.where(constant_ratio & active, observed[:, None], y)
        m_truth, complement_truth = _conditional_denominators(truth, known, id_upper, remaining_target, ranges, active)
        _update(upper_truth, 1 - y, complement_truth, active, fractions)
        _update(lower_truth, y, m_truth, active, fractions)
        # A false threshold can leave the deterministic domain on this draw.
        # Its wealth is then unnecessary (and an endpoint ratio can diverge).
        # Compute the new domain first, but all surviving factors still use
        # only the prior-history conditional means and scales.
        observed_loss_by_rank[rows, ranks] += observed
        remaining_counts[rows, ranks] -= 1
        next_known = observed_loss_by_rank @ weights.T / p
        next_remaining = remaining_counts @ weights.T / p
        next_h = remaining_counts @ q / p
        next_upper = np.minimum(1., (observed_loss_by_rank + remaining_counts) @ weights.T / p)
        feasible_threshold = active & (next_known <= threshold) & (threshold <= next_upper)
        _, complement_threshold = _conditional_denominators(threshold, known, id_upper, remaining_target, ranges, feasible_threshold)
        _update(upper_threshold, 1 - y, complement_threshold, feasible_threshold, fractions)
        known, remaining_target, remaining_h, id_upper = next_known, next_remaining, next_h, next_upper
        log_upper = _logmean(upper_truth)
        log_lower = _logmean(lower_truth)
        failed |= np.any((log_upper >= threshold_log) | (log_lower >= threshold_log) |
                         (known > truth + 1e-10) | (id_upper < truth - 1e-10), axis=1)
        threshold_log_wealth = _logmean(upper_threshold)
        threshold_feasible_now = (known <= threshold) & (threshold <= id_upper)
        certified = (id_upper <= threshold) | (threshold_feasible_now & (threshold_log_wealth >= threshold_log))
        false_certificate |= np.any(certified & (truth > threshold), axis=1)
        certified_ever |= certified
        new_full = (first_full < 0) & certified[:, full_index]
        first_full[new_full] = t
        if t in checkpoints:
            for repetition in range(repetitions):
                row = {'replicate': repetition, 'labels': t,
                       'ever_miscoverage': bool(failed[repetition]),
                       'ever_false_certification': bool(false_certificate[repetition]),
                       'certified_count': int(certified[repetition].sum()),
                       'ever_certified_count': int(certified_ever[repetition].sum()),
                       'truly_safe_count': int(np.sum(truth <= threshold)),
                       'certified_safe_count': int(np.sum(certified[repetition] & (truth <= threshold))),
                       'first_full_budget_certified': int(first_full[repetition]) if first_full[repetition] >= 0 else None,
                       'full_budget_truly_safe': bool(truth[full_index] <= threshold)}
                if diagnostics:
                    row['diagnostics'] = {'log_upper_truth': log_upper[repetition].tolist(),
                                          'log_lower_truth': log_lower[repetition].tolist(),
                                          'log_upper_threshold': threshold_log_wealth[repetition].tolist(),
                                          'known': known[repetition].tolist(),
                                          'remaining': remaining_target[repetition].tolist()}
                output.append(row)
    return output


def plots(out, summaries, config):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.hashsalt': 'rank-envelope-anytime-v1'})
    colors = {'uniform': '#64748b', 'budget_mixture': '#d97706',
              'dyadic_mixture': '#0891b2', 'max_uniform': '#a855f7', 'envelope': '#dc2626'}
    cases = [name for name in ['rare_top', 'bottom_band', 'all_safe'] if name in config['scenarios']]
    if not cases:
        cases = config['scenarios'][:3]
    fig, axes = plt.subplots(1, len(cases), figsize=(4.4 * len(cases), 4.2), constrained_layout=True, squeeze=False)
    for ax, case in zip(axes[0], cases):
        for method in config['methods']:
            rows = [r for r in summaries if r['scenario'] == case and r['method'] == method]
            ax.plot([r['labels'] for r in rows], [r['certified_safe_count'] for r in rows],
                    'o-', color=colors[method], label=method.replace('_', ' '))
        ax.axhline(rows[0]['truly_safe_count'], color='#334155', linestyle='--', linewidth=1)
        ax.set(xscale='log', xlabel='Distinct labels acquired', ylabel='Mean safe budgets certified',
               title=case.replace('_', ' '), ylim=(-.1, len(config['budgets']) + .3))
    axes[0, -1].legend(frameon=False, fontsize=8)
    names = []
    for ext in ['png', 'svg']:
        name = 'unique_label_certification.' + ext
        fig.savefig(out / name, dpi=160, metadata={'Date': None} if ext == 'svg' else None)
        names.append(name)
    plt.close(fig)
    return names


def run(config, out, draw_plots=True):
    starting_sources = source_hashes()
    p, m = config['prompts'], config['pool_size']
    budgets = config['budgets']
    if budgets != sorted(set(budgets)) or not budgets or budgets[0] != 1 or budgets[-1] != m:
        raise ValueError('study budgets must be sorted and unique, from baseline 1 to full-pool m')
    checkpoints = config['label_checkpoints']
    if checkpoints != sorted(set(checkpoints)) or not checkpoints or checkpoints[0] < 1:
        raise ValueError('label checkpoints must be positive, sorted and unique')
    if checkpoints[-1] != config['max_labels'] or config['max_labels'] > p * m:
        raise ValueError('last checkpoint must equal max_labels and not exceed the candidate count')
    if not isinstance(config['replicates'], int) or config['replicates'] < 2:
        raise ValueError('at least two replicates are required')
    if not 0 < config['delta'] < 1 or not 0 <= config['risk_threshold'] <= 1:
        raise ValueError('invalid delta or risk threshold')
    methods = config['methods']
    if not methods or len(set(methods)) != len(methods):
        raise ValueError('methods must be nonempty and unique')
    proposals = {name: np.array(rank_proposal(m, budgets, name)) for name in methods}
    all_cases = make_scenarios(p, m, config['seed'])
    if not config['scenarios'] or len(set(config['scenarios'])) != len(config['scenarios']):
        raise ValueError('scenarios must be nonempty and unique')
    cases = {name: all_cases[name] for name in config['scenarios']}
    weights = np.array([rank_weights(m, n) for n in budgets])
    out.mkdir(parents=True, exist_ok=True)
    records = []
    truths = {}
    for case_index, (name, loss) in enumerate(cases.items()):
        truths[name] = (weights @ loss.mean(axis=0)).tolist()
        rng = np.random.default_rng(np.random.SeedSequence([config['seed'], case_index]))
        uniforms = rng.random((config['replicates'], p * m))
        for method, q in proposals.items():
            order = race_orders(q, p, uniforms)
            results = simulate_paths(loss, weights, q, order, checkpoints, config['delta'],
                                      config['risk_threshold'], config['bet_fractions'])
            records.extend({'scenario': name, 'method': method, **row} for row in results)
        print(f'Completed {name}: {config["replicates"]} paired unique-label paths per method', flush=True)
    summaries = []
    for name in cases:
        for method in methods:
            for labels in checkpoints:
                rows = [r for r in records if r['scenario'] == name and r['method'] == method and r['labels'] == labels]
                summary = {'scenario': name, 'method': method, 'labels': labels, 'replicates': len(rows),
                           'truly_safe_count': rows[0]['truly_safe_count']}
                for metric in ['ever_miscoverage', 'ever_false_certification', 'certified_count',
                               'ever_certified_count', 'certified_safe_count']:
                    values = np.array([r[metric] for r in rows], dtype=float)
                    summary[metric] = float(values.mean())
                    summary[metric + '_mcse'] = float(values.std(ddof=1) / math.sqrt(len(values)))
                    if metric.startswith('ever_') and metric != 'ever_certified_count':
                        lower, upper = wilson(int(values.sum()), len(values))
                        summary[metric + '_wilson_low'] = lower
                        summary[metric + '_wilson_high'] = upper
                stopping = [r['first_full_budget_certified'] for r in rows if r['first_full_budget_certified'] is not None]
                summary['full_budget_certification_rate'] = len(stopping) / len(rows)
                summary['median_labels_among_full_budget_successes'] = float(np.median(stopping)) if stopping else None
                summary['full_budget_truly_safe'] = rows[0]['full_budget_truly_safe']
                summaries.append(summary)
    if source_hashes() != starting_sources:
        raise RuntimeError('sources changed during the study; freeze them and rerun')
    files = []
    for name, rows in [('replicates.csv', records), ('summary.csv', summaries)]:
        with (out / name).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        files.append(name)
    if draw_plots:
        files.extend(plots(out, summaries, config))
    if source_hashes() != starting_sources:
        raise RuntimeError('sources changed while writing results; freeze them and rerun')
    manifest = {'protocol': config,
                'protocol_sha256': hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                'python': sys.version.split()[0], 'numpy': np.__version__, 'platform': platform.platform(),
                'source_sha256': starting_sources,
                'outputs_sha256': {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in files},
                'loss_table_sha256': {name: hashlib.sha256(loss.astype('uint8').tobytes()).hexdigest() for name, loss in cases.items()},
                'true_risks': truths,
                'evaluation_scope': 'All times up to each checkpoint and all target budgets within one method run.'}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=Path('experiments/anytime_protocol.json'))
    parser.add_argument('--out', type=Path, default=Path('results/anytime'))
    parser.add_argument('--replicates', type=int)
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.protocol.read_text())
    if args.replicates is not None:
        config['replicates'] = args.replicates
    start = time.monotonic()
    run(config, args.out, not args.no_plots)
    print(f'Finished in {time.monotonic() - start:.1f}s; outputs: {args.out}')


if __name__ == '__main__':
    main()
