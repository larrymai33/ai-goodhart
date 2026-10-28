"""Exact finite inequalities, conditional on the accompanying analytic proof.

Every bound is a Fraction; no floating-point quantity controls a certificate.
Failure to obtain a positive enclosure raises, rather than rounding a small
denominator to zero. This is numerical certification, not formal proof checking.
"""
from fractions import Fraction as F


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value):
    if type(value) not in (int, F):
        raise TypeError('expected int or Fraction, excluding bool')
    return F(value)


def _series_log(x):
    z = (x-1)/(x+1)
    lo = 2*sum((z**(2*k+1)/F(2*k+1) for k in range(64)), F(0))
    error = 2*z**129/(F(129)*(1-z*z))
    return lo, lo+error


_LOG2 = _series_log(F(2))


def log_bounds(x):
    """Enclose ln(x) by dyadic reduction and a 64-term rational atanh series."""
    x = rational(x)
    require(x > 0, 'positive logarithm argument required')
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    while x < 1:
        x *= 2
        power -= 1
    lo, hi = _series_log(x)
    if power >= 0:
        return lo+power*_LOG2[0], hi+power*_LOG2[1]
    return lo+power*_LOG2[1], hi+power*_LOG2[0]


def kl_bounds(p, q):
    p, q = rational(p), rational(q)
    require(0 <= p <= 1 and 0 < q < 1, 'Bernoulli KL domain')
    if p == q:
        return F(0), F(0)
    lo = hi = F(0)
    for weight, reference in [(p, q), (1-p, 1-q)]:
        if weight:
            a, b = log_bounds(weight/reference)
            lo += weight*a
            hi += weight*b
    require(lo > 0, 'KL enclosure not strictly positive; parameters too close for this precision')
    return lo, hi


def _posterior(p, z):
    ratio = F(3) if z else F(1, 3)
    return ratio*p/(1+(ratio-1)*p)


def _information_upper(p, pp, c):
    values = [kl_bounds(F(1, 4)+p/2, F(1, 4)+pp/2)[1], kl_bounds(p, pp)[1]/c]
    values.extend(kl_bounds(_posterior(p, z), _posterior(pp, z))[1]/c for z in [0, 1])
    return max(values)


def _upper_bound(c, tau, epsilon, delta, height):
    p0, p1 = F(2, 3)*tau, F(2, 3)*(tau-epsilon)
    duration = (log_bounds(1/delta)[1]+log_bounds((1-p1)/(1-p0))[1])/kl_bounds(p1, p0)[0]
    theta = tau-epsilon
    work = 1+F(2*height, 3)+F(8*(height+1)**2, 27)*theta+c*F(2, 3)*theta+F(c, 4*(height+1))
    return duration*work


def certificate(name, N, c, tau, epsilon, delta, nu, K, p, pp, cap):
    """Verify sufficient conditions and return outward-rounded strict bounds.

    cap=None selects the p=0 argument. Positive p requires a positive rational
    census-cap multiplier. Failed or vacuous lower bounds never become savings.
    This helper is for the finite constructions stated in the theorem only.
    """
    for value, minimum in [(N, 1), (c, 1), (K, 0)]:
        if type(value) is not int:
            raise TypeError('N, c and K must be integers, excluding bool')
        require(value >= minimum, 'invalid population, cost or height')
    tau, epsilon, delta, nu, p, pp = map(rational, (tau, epsilon, delta, nu, p, pp))
    require(0 < epsilon < tau <= F(1, 8), 'risk parameters')
    require(0 < delta <= F(1, 4) and 0 < nu < 1 and 1-nu > delta+nu, 'error parameters')
    require(0 <= p < tau-epsilon < tau < pp < 1, 'prior parameters')
    require((tau*c).denominator == 1 and (2*tau*c).denominator == 1, 'unsafe alternative score grid')
    target = log_bounds(1/nu)[1]
    require(N*kl_bounds(tau, pp)[0] >= target, 'alternative prior tail condition fails')
    info = _information_upper(p, pp, c)
    if p == 0:
        require(cap is None, 'zero null needs no fallback penalty')
        D = log_bounds(1/(delta+nu))[0]
        single = D/info
        exact = c*D/kl_bounds(p, pp)[1]
        safe = F(0)
    else:
        require(cap is not None, 'positive null requires a census cap')
        cap = rational(cap)
        require(cap > 0, 'positive census cap required')
        require(N*kl_bounds(tau-epsilon, p)[0] >= target, 'null prior tail condition fails')
        D = kl_bounds(1-nu, delta+nu)[0]
        penalty = nu*(cap+1)*c*N
        factor = 1+1/cap
        single = (D/info-penalty)/factor
        exact = (c*D/kl_bounds(p, pp)[1]-penalty)/factor
        safe = tau-epsilon
    require((safe*c).denominator == 1, 'cheap-only safe score grid')
    q = F(1, 4)+safe/2
    noise_info = F(N-1, N)*kl_bounds(q, F(1, 4)+tau/2)[1]+F(1, N)*kl_bounds(q, F(1, 4)+tau)[1]
    cheap = log_bounds(1/delta)[0]/noise_info
    upper = _upper_bound(c, tau, epsilon, delta, K)
    require(min(single, exact, cheap) > upper > 0, 'strict separation fails or lower bound is vacuous')
    U = -((-upper.numerator)//upper.denominator)
    S, E, C = [x.numerator//x.denominator for x in (single, exact, cheap)]
    require(U < min(S, E, C), 'outward-rounded strict separation fails')
    return dict(name=name, N=N, exact_cost=c, tau=str(tau), epsilon=str(epsilon),
                margin_class_risk_max=str(tau-epsilon), delta=str(delta), nu=str(nu),
                gate_height=K, prior_p=str(p), prior_p_alternate=str(pp),
                census_cap_multiplier=None if cap is None else str(cap),
                upper_integer=U, one_report_lower_integer=S,
                exact_only_lower_integer=E, cheap_only_lower_integer=C,
                guaranteed_reduction_fraction_at_least=str(F(min(S,E,C)-U, min(S,E,C))),
                tail_checks_passed=True, small_relative_margin_regime=epsilon <= tau/16)
