"""Offline, score-only audit planning and deterministic-label reporting."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random

from .core import envelope_proposal, estimate_risk, partial_bounds, rank_weights


def _number(value, name, bounded=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be a finite number')
    try:
        value = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f'{name} must be representable as a finite number') from None
    if not math.isfinite(value) or (bounded and not 0 <= value <= 1):
        raise ValueError(f'{name} must be finite' + (' and in [0,1]' if bounded else ''))
    return float(value)


def _identifier(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')
    return value


def load_pool(path):
    """Read equally sized pools; rank descending by score, then ascending ID.

    Source losses are validated but never used by planning or reporting.
    """
    path = Path(path)
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('pool file exceeds the 64 MiB input limit')
    pools, prompt_ids = [], set()
    with path.open(encoding='utf-8-sig') as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError('each pool must be an object')
                pid = _identifier(row.get('prompt_id'), 'prompt_id')
                if pid in prompt_ids:
                    raise ValueError('duplicate prompt_id')
                prompt_ids.add(pid)
                candidates = row.get('candidates')
                if not isinstance(candidates, list) or not candidates:
                    raise ValueError('candidates must be a nonempty list')
                ids, clean = set(), []
                for candidate in candidates:
                    if not isinstance(candidate, dict):
                        raise ValueError('candidate must be an object')
                    cid = _identifier(candidate.get('candidate_id'), 'candidate_id')
                    if cid in ids:
                        raise ValueError('duplicate candidate_id within prompt')
                    ids.add(cid)
                    item = {'candidate_id': cid,
                            'proxy': _number(candidate.get('proxy'), 'proxy')}
                    if 'text' in candidate:
                        if not isinstance(candidate['text'], str):
                            raise ValueError('text must be a string')
                        item['text'] = candidate['text']
                    if candidate.get('loss') is not None:
                        item['loss'] = _number(candidate['loss'], 'loss', True)
                    clean.append(item)
                clean.sort(key=lambda c: (-c['proxy'], c['candidate_id']))
                pools.append({'prompt_id': pid, 'candidates': clean})
            except (ValueError, TypeError) as exc:
                raise ValueError(f'pool line {line_number}: {exc}') from exc
    if not pools:
        raise ValueError('pool file is empty')
    pools.sort(key=lambda p: p['prompt_id'])
    m = len(pools[0]['candidates'])
    if any(len(p['candidates']) != m for p in pools):
        raise ValueError('all prompts must have the same number of candidates')
    return pools


def _public_pool(pools):
    return [{'prompt_id': p['prompt_id'], 'candidates': [
        {k: v for k, v in c.items() if k != 'loss'} for c in p['candidates']
    ]} for p in pools]


def pool_fingerprint(pools):
    data = json.dumps(_public_pool(pools), sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def make_plan(pools, budgets, draws, seed):
    """Fix IID (uniform prompt, envelope rank) draws before acquiring labels."""
    if isinstance(draws, bool) or not isinstance(draws, int) or not 2 <= draws <= 1_000_000:
        raise ValueError('draws must be an integer between 2 and 1000000')
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError('seed must be a nonnegative integer fixed before labeling')
    if not pools:
        raise ValueError('pools must not be empty')
    m = len(pools[0]['candidates'])
    q, normalizer = envelope_proposal(m, budgets)
    rng = random.Random(seed)
    draw_rows, queries, seen = [], [], set()
    for _ in range(draws):
        prompt_index = rng.randrange(len(pools))
        rank = rng.choices(range(m), weights=q, k=1)[0]
        p = pools[prompt_index]
        c = p['candidates'][rank]
        key = (p['prompt_id'], c['candidate_id'])
        draw_rows.append({'prompt_id': key[0], 'candidate_id': key[1], 'rank': rank})
        if key not in seen:
            seen.add(key)
            query = {'prompt_id': key[0], 'candidate_id': key[1], 'rank': rank,
                     'proxy': c['proxy'], 'loss': None}
            if 'text' in c:
                query['text'] = c['text']
            queries.append(query)
    return {'schema_version': 1, 'method': 'rank_envelope',
            'estimand': 'conditional_finite_pool', 'pool_sha256': pool_fingerprint(pools),
            'prompt_count': len(pools), 'pool_size': m, 'budgets': list(budgets),
            'draw_count': draws, 'seed': seed, 'proposal': q, 'normalizer': normalizer,
            'draws': draw_rows, 'queries': queries}


def audit_report(pools, plan, delta=0.05, threshold=0.1):
    """Report simultaneous sampling intervals and sharp finite-pool bounds.

    Only the unique-label table in the audit plan is trusted as annotation
    input. Original pool losses are deliberately ignored.
    """
    _number(threshold, 'threshold', True)
    if not isinstance(plan, dict):
        raise ValueError('audit plan must be an object')
    if plan.get('pool_sha256') != pool_fingerprint(pools):
        raise ValueError('pool fingerprint differs from the audit plan')
    try:
        expected = make_plan(pools, plan['budgets'], plan['draw_count'], plan['seed'])
        labels = {}
        queries = plan['queries']
        if not isinstance(queries, list) or len(queries) != len(expected['queries']):
            raise ValueError('query table differs from the original plan')
        unlabeled = dict(plan)
        unlabeled['queries'] = []
        for query in queries:
            clean = dict(query)
            labels[(query['prompt_id'], query['candidate_id'])] = _number(
                clean.get('loss'), 'queried loss label', True)
            clean['loss'] = None
            unlabeled['queries'].append(clean)
        if unlabeled != expected:
            raise ValueError('audit plan/proposal changed; only query loss fields may be edited')
    except (KeyError, TypeError) as exc:
        raise ValueError('malformed audit plan') from exc
    ranks = [d['rank'] for d in plan['draws']]
    observed = [labels[d['prompt_id'], d['candidate_id']] for d in plan['draws']]
    curve = estimate_risk(ranks, observed, plan['proposal'], plan['budgets'], delta)
    for entry in curve:
        weights = rank_weights(plan['pool_size'], entry['budget'])
        bounds = [partial_bounds([labels.get((p['prompt_id'], c['candidate_id']))
                                  for c in p['candidates']], weights) for p in pools]
        lower = sum(b[0] for b in bounds) / len(pools)
        upper = sum(b[1] for b in bounds) / len(pools)
        entry['identification_lower'] = lower
        entry['identification_upper'] = upper
        # The deterministic bounds remain valid if a statistical interval misses.
        entry['combined_lower'] = max(lower, entry['lower'])
        entry['combined_upper'] = min(upper, entry['upper'])
        entry['interval_conflict'] = entry['combined_lower'] > entry['combined_upper'] + 1e-12
        entry['certified'] = not entry['interval_conflict'] and entry['combined_upper'] <= threshold
    certified = [row['budget'] for row in curve if row['certified']]
    return {'schema_version': 1, 'estimand': 'conditional_finite_pool',
            'pool_sha256': plan['pool_sha256'], 'delta': delta, 'threshold': threshold,
            'draw_count': len(ranks), 'unique_labels': len(labels),
            'prompt_count': len(pools), 'pool_size': plan['pool_size'],
            'normalizer': plan['normalizer'], 'curve': curve,
            'certified_budgets': certified, 'largest_certified_budget': max(certified, default=None),
            'assumptions': ['Plan and number of draws fixed before observing labels.',
                            'All queried labels are fixed, correct values in [0,1].',
                            'Certification concerns these pools and this label definition only.',
                            'No optional stopping, adaptive proposal, or new-prompt guarantee.']}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                    encoding='utf-8')
