"""Exact deterministic coverage between certified best-of-n budgets.

These helpers do not acquire labels or establish that the supplied risk bounds
are true. The implication uses fixed rankings and nonnegative losses in [0,1].
See docs/grid-coverage.md for attribution, proofs, and completeness limits.
"""
from fractions import Fraction

MAX_POOL = 100_000


def _integer(value, name):
    if type(value) is not int or not 1 <= value <= MAX_POOL:
        raise ValueError(f'{name} must be an integer in [1,{MAX_POOL}]')
    return value


def _level(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f'{name} must be an exact integer or Fraction')
    value = Fraction(value)
    if not 0 <= value <= 1:
        raise ValueError(f'{name} must lie in [0,1]')
    return value


def _endpoints(a, b):
    a, b = _integer(a, 'left endpoint'), _integer(b, 'right endpoint')
    if a >= b:
        raise ValueError('the left endpoint must precede the right endpoint')
    return a, b


def interval_factor(a, b):
    """Maximum integer-budget chord factor on the inclusive interval [a,b]."""
    a, b = _endpoints(a, b)
    return Fraction((a+b)**2//4, a*b)


def interpolate_upper(a, b, n, left_upper, right_upper):
    """Upper risk implication at n from valid upper bounds at a and b.

    Accepts integer budgets 1<=a<=n<=b<=100000, with a<b. The caller must
    establish the endpoint bounds for the same fixed candidate pools.
    """
    a, b = _endpoints(a, b)
    n = _integer(n, 'target budget')
    if not a <= n <= b:
        raise ValueError('the target budget must lie between the endpoints')
    left_upper = _level(left_upper, 'left upper bound')
    right_upper = _level(right_upper, 'right upper bound')
    upper = Fraction(n*(b-n), a*(b-a))*left_upper
    upper += Fraction(n*(n-a), b*(b-a))*right_upper
    return min(Fraction(1), upper)


def covering_grid(m, certified_level, target_level):
    """Fewest endpoints under the sufficient integer chord-factor rule.

    Includes 1 and m. Minimality is within this rule, not among all possible
    inference methods. All selected budgets must actually be certified at
    certified_level before asserting full-grid risk at target_level.
    """
    m = _integer(m, 'pool size')
    s = _level(certified_level, 'certified level')
    tau = _level(target_level, 'target level')
    if s > tau:
        raise ValueError('certified level must not exceed target level')
    if m == 1:
        return (1,)
    if s == 0:
        return (1, m)
    grid = [1]
    while grid[-1] < m:
        a = grid[-1]
        lo, hi = a+1, m
        while lo < hi:
            middle = (lo+hi+1)//2
            if s*Fraction((a+middle)**2//4, a*middle) <= tau:
                lo = middle
            else:
                hi = middle-1
        grid.append(lo)
    return tuple(grid)
