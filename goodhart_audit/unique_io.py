"""Score-only, without-replacement planning and anytime prefix reporting."""

import math

from .anytime import DEFAULT_BETS, FinitePoolAudit, weighted_order
from .core import envelope_proposal, rank_weights
from .io import _number, pool_fingerprint


METHODS = ('uniform', 'budget_mixture', 'dyadic_mixture', 'max_uniform', 'envelope')


def rank_proposal(m, budgets, method):
    """Return a fixed rank proposal without inspecting any loss labels."""
    envelope, _ = envelope_proposal(m, budgets)  # Validates sizes/grid.
    if method == 'envelope':
        return envelope
    if method == 'uniform':
        return [1 / m] * m
    if method == 'max_uniform':
        full = rank_weights(m, m)
        return [0.5 / m + 0.5 * value for value in full]
    if method in ('budget_mixture', 'dyadic_mixture'):
        grid = (range(1, m + 1) if method == 'budget_mixture' else
                sorted(set([2 ** j for j in range(m.bit_length()) if 2 ** j <= m] + [m])))
        rows = [rank_weights(m, n) for n in grid]
        return [math.fsum(row[r] for row in rows) / len(rows) for r in range(m)]
    raise ValueError(f'method must be one of {METHODS}')


def make_unique_plan(pools, budgets, labels, seed, method='envelope', delta=0.05):
    if not pools:
        raise ValueError('pools must not be empty')
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError('seed must be a nonnegative integer')
    if isinstance(labels, bool) or not isinstance(labels, int) or labels < 1:
        raise ValueError('labels must be a positive integer')
    _number(delta, 'delta', True)
    if not 0 < delta < 1:
        raise ValueError('delta must be strictly between zero and one')
    p, m = len(pools), len(pools[0]['candidates'])
    q = rank_proposal(m, budgets, method)
    proposal = [value / p for _ in pools for value in q]
    if labels > sum(value > 0 for value in proposal):
        raise ValueError('label count exceeds supported unique candidates')
    order = weighted_order(proposal, seed, labels)
    queries = []
    for index in order:
        prompt, rank = divmod(index, m)
        candidate = pools[prompt]['candidates'][rank]
        query = {'index': index, 'prompt_id': pools[prompt]['prompt_id'],
                 'candidate_id': candidate['candidate_id'], 'rank': rank,
                 'proxy': candidate['proxy'], 'loss': None}
        if 'text' in candidate:
            query['text'] = candidate['text']
        queries.append(query)
    return {'schema_version': 2, 'inference': 'without_replacement_fractional_betting',
            'estimand': 'conditional_finite_pool', 'pool_sha256': pool_fingerprint(pools),
            'prompt_count': p, 'pool_size': m, 'budgets': list(budgets),
            'max_labels': labels, 'seed': seed, 'method': method,
            'delta': delta, 'bet_fractions': list(DEFAULT_BETS),
            'rank_proposal': q, 'queries': queries}


def unique_report(pools, plan, threshold=0.1, rule='interval'):
    """Analyze any contiguous prefix, including one selected by optional stopping.

    All unobserved queries must have null losses. The order and inference
    parameters are replayed from the original score-only plan.
    """
    _number(threshold, 'threshold', True)
    if rule not in ('interval', 'upper-test'):
        raise ValueError('certification rule must be interval or upper-test')
    if not isinstance(plan, dict):
        raise ValueError('audit plan must be an object')
    if plan.get('pool_sha256') != pool_fingerprint(pools):
        raise ValueError('pool fingerprint differs from the audit plan')
    try:
        expected = make_unique_plan(pools, plan['budgets'], plan['max_labels'],
                                    plan['seed'], plan['method'], plan['delta'])
        if not isinstance(plan['queries'], list) or len(plan['queries']) != len(expected['queries']):
            raise ValueError('query list differs from original plan')
        clean = dict(plan)
        clean['queries'] = []
        observations, missing = [], False
        for query in plan['queries']:
            query_copy = dict(query)
            label = query_copy.get('loss')
            if label is None:
                missing = True
            else:
                if missing:
                    raise ValueError('labels must form a contiguous prefix of the planned order')
                observations.append((query['index'], _number(label, 'queried loss label', True)))
            query_copy['loss'] = None
            clean['queries'].append(query_copy)
        if clean != expected:
            raise ValueError('audit plan or order changed; edit only the prefix query losses')
    except (KeyError, TypeError) as exc:
        raise ValueError('malformed unique-label audit plan') from exc
    p, m = len(pools), plan['pool_size']
    targets = [[value / p for _ in pools for value in rank_weights(m, n)] for n in plan['budgets']]
    proposal = [value / p for _ in pools for value in plan['rank_proposal']]
    audit = FinitePoolAudit(targets, proposal, delta=plan['delta'], bets=plan['bet_fractions'])
    for index, label in observations:
        audit.observe(index, label)
    curve = []
    directional = audit.upper_certificates(threshold)
    for budget, row, upper_test in zip(plan['budgets'], audit.bounds(), directional):
        row = dict(row)
        row['budget'] = budget
        row['upper_test_certified'] = upper_test['upper_test_certified']
        row['certified'] = (row['upper_test_certified'] if rule == 'upper-test' else
                            not row['interval_conflict'] and row['upper'] <= threshold)
        curve.append(row)
    certified = [row['budget'] for row in curve if row['certified']]
    return {'schema_version': 2, 'estimand': 'conditional_finite_pool', 'anytime_valid': True,
            'inference': plan['inference'], 'pool_sha256': plan['pool_sha256'],
            'delta': plan['delta'], 'threshold': threshold, 'method': plan['method'],
            'certification_rule': rule,
            'unique_labels': len(observations), 'draw_count': len(observations),
            'planned_labels_remaining': plan['max_labels'] - len(observations),
            'curve': curve, 'certified_budgets': certified,
            'largest_certified_budget': max(certified, default=None),
            'assumptions': ['The frozen weighted-random query order was followed.',
                            'Queried labels are fixed correct values in [0,1].',
                            'The probability guarantee covers all prefix lengths and target budgets.',
                            'Certification applies only to the fixed pools and label definition.',
                            'No new-prompt, labeler-validity, or latent noisy-label guarantee.']}
