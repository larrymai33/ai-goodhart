"""Exact finite all-passing cost benchmarks; no LLM or dataset execution.

Run with python -B -S -m experiments.check_program_audit.
The general allocation enumerator is for small instances only. The d=1
closed form does not enumerate profiles. See docs/program-audit-zero-cost.md.
"""
from fractions import Fraction as F
from itertools import combinations_with_replacement, product
from math import comb
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, name, minimum=1):
    if type(value) is not int:
        raise TypeError(f'{name} must be an integer, excluding bool')
    require(value >= minimum, f'{name} must be at least {minimum}')
    return value


def parameters(N, c, b, d):
    for name, value in [('N', N), ('c', c), ('b', b), ('d', d)]:
        integer(value, name)
    require(b <= N and d <= c, 'require b <= N and d <= c')


def error_probability(delta):
    if type(delta) not in (int, F):
        raise TypeError('delta must be an int or Fraction, excluding bool')
    delta = F(delta)
    require(0 <= delta <= 1, 'delta must lie in [0,1]')
    return delta


def _miss(profile, c, b, d):
    # Coefficient of z**b in product_i (1 + a_i*z), divided by C(N,b).
    coefficients = [F(1)] + [F(0)] * b
    denominator = comb(c, d)
    for k in profile:
        a = F(comb(c - k, d), denominator) if c - k >= d else F(0)
        for j in range(b, 0, -1):
            coefficients[j] += a * coefficients[j - 1]
    return coefficients[b] / comb(len(profile), b)


def miss_probability(queried, c, b, d=1):
    """Miss probability under b uniformly hidden rows, d hidden failures each."""
    profile = tuple(queried)
    parameters(len(profile), c, b, d)
    for k in profile:
        integer(k, 'queried count', minimum=0)
        require(k <= c, 'queried count exceeds row size')
    return _miss(profile, c, b, d)


def zero_cost(N, c, b, delta, d=1):
    """Return exact all-zero optimum and a <=2-profile randomized witness.

    A profile is symmetrized by uniform row permutations and uniform column
    subsets. It certifies on all passes; otherwise full census decides.
    Validity assumes every nonzero row has at least d failing components.
    """
    parameters(N, c, b, d)
    delta = error_probability(delta)
    require(N * c <= 128 and comb(N + c, N) <= 20000,
            'small-instance enumeration limit exceeded')
    best = {}
    for profile in combinations_with_replacement(range(c + 1), N):
        cost, risk = sum(profile), _miss(profile, c, b, d)
        if cost not in best or risk < best[cost][0]:
            best[cost] = (risk, profile)

    # Lower convex envelope of (number of queries, missed-unsafe probability).
    hull = []
    for cost in sorted(best):
        risk, profile = best[cost]
        point = (cost, risk, profile)
        while len(hull) >= 2:
            x0, y0, _ = hull[-2]
            x1, y1, _ = hull[-1]
            if (risk - y1) * (x1 - x0) > (y1 - y0) * (cost - x1):
                break
            hull.pop()
        hull.append(point)
        if risk == 0:
            break
    for cost, risk, profile in hull:
        if risk == delta:
            return F(cost), ((F(1), profile),)
    for (x0, y0, p0), (x1, y1, p1) in zip(hull, hull[1:]):
        if y0 > delta > y1:
            weight = (delta - y1) / (y0 - y1)
            return weight * x0 + (1 - weight) * x1, ((weight, p0), (1 - weight, p1))
    raise RuntimeError('convex envelope failed to bracket delta')


def singleton_zero_cost(N, c, b, delta):
    """Closed form when a bad row may contain only one failing test (d=1)."""
    parameters(N, c, b, 1)
    delta = error_probability(delta)
    if delta == 1:
        return F(0)
    if delta == 0:
        return F(c * (N - b + 1))
    h = F(1)
    for k in range(N - b + 1):
        following = h * F(N - b - k, N - k)
        if h >= delta >= following:
            return c * (k + (h - delta) / (h - following))
        h = following
    raise RuntimeError('hypergeometric curve failed to bracket delta')


def verify():
    checked = 0
    for N, c in product(range(1, 5), repeat=2):
        for b in range(1, N + 1):
            minima = {}
            for p in combinations_with_replacement(range(c + 1), N):
                m, risk = sum(p), _miss(p, c, b, 1)
                minima[m] = min(minima.get(m, F(1)), risk)
                checked += 1
            for m, risk in minima.items():
                k, r = divmod(m, c)
                concentrated = (c,) * k + ((r,) if r else ())
                concentrated += (0,) * (N - len(concentrated))
                require(risk == _miss(concentrated, c, b, 1), 'concentration identity')
            for delta in [F(0), F(1, 20), F(1, 4), F(1, 2), F(1)]:
                require(zero_cost(N, c, b, delta)[0] == singleton_zero_cost(N, c, b, delta),
                        'closed form versus convex envelope')

    cost, mixture = zero_cost(2, 4, 1, F(1, 4), d=2)
    off_promise = sum(w * miss_probability(p, 4, 1, d=1) for w, p in mixture)
    require(cost == F(7, 2) and off_promise == F(9, 16), 'density example')
    zero = singleton_zero_cost(100, 20, 6, F(1, 20))
    boundary_lower = (1 - F(1, 20)) * 20 * (100 - 6 + 1)
    require(zero == F(239936300, 313113) and boundary_lower == 1805, 'boundary example')
    return dict(scope='Exact all-zero-input benchmark under a fixed binary test table; no measured LLM result.',
                singleton_allocation_profiles_checked=checked,
                boundary_example=dict(N=100, c=20, b=6, delta='1/20',
                    all_zero_optimum=str(zero), all_zero_cost_ceiling=-(-zero.numerator // zero.denominator),
                    boundary_safe_lower=str(boundary_lower), full_table_cost=2000),
                dense_example=dict(N=2, c=4, b=1, d=2, delta='1/4',
                    optimum=str(cost), complete_rows_optimum='9/2',
                    singleton_optimum=str(singleton_zero_cost(2, 4, 1, F(1, 4))),
                    mixture=[dict(weight=str(w), queries=list(p)) for w, p in mixture],
                    false_certification_if_density_promise_fails=str(off_promise)))


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
