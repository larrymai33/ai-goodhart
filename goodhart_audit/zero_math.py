"""Exact arithmetic for a conservative zero-only finite-pool audit.

The probabilities are rational upper approximations to classical NEGEXP.
Certified log intervals and a checked upper sandwich preserve the finite-pool
expected-cost proofs: factor 160 on grids containing every power of four
through their maximum, or 320 on other grids containing budget 1. No numerical
logarithms, exponentials, or pseudorandom seeds are used. See
docs/zero-workflow-numerics.md and docs/sparse-grid-theorem.md.
"""

from collections.abc import Sequence
from fractions import Fraction as F


MAX_POOL_SIZE = 1024
MAX_ITEMS = 100000
MAX_RANK_TARGET_PAIRS = 250000
MAX_PARAMETER_BITS = 256
MAX_SERIALIZED_BITS = 12000
MAX_DRAW_WIDTH_SUM = 64000000


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + ' must be a positive integer')
    return value


def _parameter(value, name, maximum):
    if not isinstance(value, F) or not 0 < value <= maximum:
        raise ValueError(name + ' must be an exact Fraction in (0, ' + str(maximum) + ']')
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_PARAMETER_BITS:
        raise ValueError(name + ' exceeds the parameter bit limit')
    return value


def _fraction_text(value):
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_SERIALIZED_BITS:
        raise ValueError('a rational result exceeds the serialized bit limit')
    return str(value)


def _atanh_log_interval(z, terms):
    """Enclose log((1+z)/(1-z)) for 0<=z<=1/3 by positive terms."""
    power, total, square = z, F(0), z*z
    for j in range(terms):
        total += power/(2*j+1)
        power *= square
    lower = 2*total
    remainder = 2*power/((2*terms+1)*(1-square))
    return lower, lower+remainder


def _log_interval(delta, terms):
    # 1/delta = 2**k * y, with 1<=y<2. Integer comparisons avoid log2.
    numerator, denominator = delta.denominator, delta.numerator
    k = numerator.bit_length()-denominator.bit_length()
    if numerator < denominator << k:
        k -= 1
    y = F(numerator, denominator << k)
    two_lower, two_upper = _atanh_log_interval(F(1, 3), terms)
    y_lower, y_upper = _atanh_log_interval((y-1)/(y+1), terms)
    lower, upper = k*two_lower+y_lower, k*two_upper+y_upper
    # Outward dyadic rounding prevents the parameter's arbitrary denominator
    # from propagating into every inclusion probability and random draw.
    exponent = 4*terms+16
    scale = 1 << exponent
    lower = F((lower.numerator*scale)//lower.denominator, scale)
    upper = F((upper.numerator*scale+upper.denominator-1)//upper.denominator, scale)
    return lower, upper, exponent


def _rank_envelope(m, budgets, prompts):
    envelope = [F(0)]*m
    for n in budgets:
        weight = F(n, m)
        for index in range(m-n+1):
            envelope[index] = max(envelope[index], weight)
            if index < m-n:
                weight *= F(m-n-index, m-1-index)
    return tuple(weight/prompts for weight in envelope)


def _inclusion_upper(x):
    polynomial = x-x*x/2+x**3/6-x**4/24+x**5/120
    return min(F(1), polynomial)


def design_probabilities(m, budgets, P, tau, delta):
    """Return a JSON-ready design record and exact probabilities per rank.

    ``tau`` and ``delta`` must be Fraction objects. Each rank probability is
    reused in every prompt pool. All labels remain unobserved at design time.
    The bounded reference implementation rejects excessive input or output
    sizes instead of approximating the Bernoulli probabilities.
    """
    _positive_integer(m, 'pool size')
    _positive_integer(P, 'prompt count')
    if m > MAX_POOL_SIZE or P*m > MAX_ITEMS:
        raise ValueError('pool geometry exceeds the item resource limits')
    if not isinstance(budgets, Sequence) or isinstance(budgets, (str, bytes)) or not 1 <= len(budgets) <= m:
        raise ValueError('budgets must be a nonempty bounded sequence')
    if m*len(budgets) > MAX_RANK_TARGET_PAIRS:
        raise ValueError('rank-target work exceeds the resource limit')
    for n in budgets:
        _positive_integer(n, 'budget')
        if n > m:
            raise ValueError('budget exceeds pool size')
    if len(set(budgets)) != len(budgets):
        raise ValueError('budgets must be distinct')
    budgets = tuple(sorted(budgets))
    if budgets[0] != 1:
        raise ValueError('budgets must contain baseline budget 1')
    cost_factor = 160
    required = 1
    while required <= budgets[-1]:
        if required not in budgets:
            cost_factor = 320
            break
        required *= 4
    tau = _parameter(tau, 'tau', F(1, 8))
    delta = _parameter(delta, 'delta', F(1, 4))
    envelope = _rank_envelope(m, budgets, P)
    terms = 1
    while True:
        lower, upper, exponent = _log_interval(delta, terms)
        probabilities = tuple(_inclusion_upper(upper*mass/tau) for mass in envelope)
        if all(0 <= q <= min(F(1), lower*mass/tau) for q, mass in zip(probabilities, envelope)):
            break
        terms += 1
    draw_width_sum = P*sum((q.denominator-1).bit_length() for q in probabilities)
    if draw_width_sum > MAX_DRAW_WIDTH_SUM:
        raise ValueError('random draw-width sum exceeds the transcript resource limit')
    expected_cost = P*sum(probabilities, F(0))
    record = {
        'method': 'rational_upper_negexp_v1',
        'pool_size': m,
        'prompts': P,
        'items': P*m,
        'budgets': list(budgets),
        'tau': _fraction_text(tau),
        'delta': _fraction_text(delta),
        'log_interval': {'lower': _fraction_text(lower), 'upper': _fraction_text(upper),
                         'terms': terms, 'dyadic_scale_exponent': exponent},
        'rank_envelope_masses': [_fraction_text(mass) for mass in envelope],
        'rank_inclusion_probabilities': [_fraction_text(q) for q in probabilities],
        'expected_zero_cost': _fraction_text(expected_cost),
        'random_draw_width_sum': draw_width_sum,
        'cost_factor': cost_factor,
    }
    return record, probabilities


def exact_randbelow(n, bits_callable):
    """Draw uniformly below n by rejecting out-of-range independent bit words.

    Exactness assumes the callable supplies independent unbiased bits. For
    n>1 the expected number of words is less than two, with almost-sure finite
    termination. The accepted integer is sufficient for the workflow's tape;
    recording it does not establish that the randomness assumption held.
    """
    _positive_integer(n, 'random bound')
    if n.bit_length() > MAX_SERIALIZED_BITS:
        raise ValueError('random bound exceeds the serialized bit limit')
    if not callable(bits_callable):
        raise ValueError('a callable random-bit source is required')
    if n == 1:
        return 0
    width = (n-1).bit_length()
    while True:
        value = bits_callable(width)
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 1 << width:
            raise ValueError('random-bit source returned an invalid word')
        if value < n:
            return value
