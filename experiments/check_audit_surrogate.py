"""Exact audit-correction examples, not an LLM experiment or trainer.

python -B -S -m experiments.check_audit_surrogate
See docs/audit-surrogate-contract.md for the conditional guarantees.
"""
from fractions import Fraction as F
from itertools import product
import argparse
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value):
    if type(value) not in (int, F):
        raise TypeError('expected int or Fraction, excluding bool')
    return F(value)


def clip_parameters(ratio, advantage, epsilon):
    ratio, advantage, epsilon = map(rational, (ratio, advantage, epsilon))
    require(ratio > 0 and 0 < epsilon < 1, 'positive ratio and 0 < epsilon < 1 required')
    return ratio, advantage, epsilon


def surrogate(ratio, advantage, epsilon):
    ratio, advantage, epsilon = clip_parameters(ratio, advantage, epsilon)
    clipped = min(max(ratio, 1-epsilon), 1+epsilon)
    return min(ratio*advantage, clipped*advantage)


def ratio_gradient(ratio, advantage, epsilon):
    ratio, advantage, epsilon = clip_parameters(ratio, advantage, epsilon)
    require(ratio not in (1-epsilon, 1+epsilon), 'clip-knot derivative convention is unspecified')
    if (advantage > 0 and ratio > 1+epsilon) or (advantage < 0 and ratio < 1-epsilon):
        return F(0)
    return advantage


def correction(weak, full, q, selected):
    weak, full, q = map(rational, (weak, full, q))
    require(0 < q <= 1, 'audit probability must lie in (0,1]')
    if type(selected) is not int or selected not in (0, 1):
        raise ValueError('selected must be integer 0 or 1, excluding bool')
    return weak + F(selected, 1)/q*(full-weak)


def positive_gap(weak, full, q):
    weak, full, q = map(rational, (weak, full, q))
    audited = correction(weak, full, q, 1)
    return (1-q)*max(weak, 0) + q*max(audited, 0) - max(full, 0)


def reuse_example():
    """Enumerate two ascent updates for a valid two-action categorical policy.

    pi_theta(1)=theta**2/2, pi_theta(2)=1-theta**2/2; theta_old=1.
    Fixed batch contains each action once. Weak centered A=(0,0), full
    centered A=(-1,1). The second update remains strictly inside clipping.
    """
    q, rate, epsilon = F(1, 2), F(1, 100), F(1, 5)
    first = reused = full_visited = fresh_cached = audits = F(0)
    ratios = []
    for z1, probability in [(0, 1-q), (1, q)]:
        g1 = correction(0, -2, q, z1)
        theta = 1 + rate*g1
        r1, r2 = theta*theta, 2-theta*theta
        require(1-epsilon < r1 < 1+epsilon and 1-epsilon < r2 < 1+epsilon,
                'the example must stay inside the ratio clip interval')
        ratios.extend([r1, r2])
        # Chain rule through both ratios and the mean over the two responses.
        full_g = (ratio_gradient(r1, -1, epsilon)*2*theta
                  + ratio_gradient(r2, 1, epsilon)*(-2*theta))/2
        first += probability*g1
        reused += probability*correction(0, full_g, q, z1)
        full_visited += probability*full_g
        if z1:
            fresh_cached += probability*full_g
            audits += probability
        else:
            for z2, second_probability in [(0, 1-q), (1, q)]:
                fresh_cached += probability*second_probability*correction(0, full_g, q, z2)
                audits += probability*second_probability*z2
    return dict(first_expected_gradient=first, reused_second_expected_gradient=reused,
                full_at_visited_expected_gradient=full_visited,
                fresh_or_cached_second_expected_gradient=fresh_cached,
                expected_distinct_group_audits=audits, second_ratios=ratios)


def verify():
    cases = 0
    e = F(1, 5)
    for weak, full, q, r in product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2],
                                  [F(1, 10), F(1, 4), F(1, 2), F(1)],
                                  [F(1, 2), F(4, 5), F(1), F(6, 5), F(3, 2), F(2)]):
        audited = correction(weak, full, q, 1)
        gap = positive_gap(weak, full, q)
        direct = (1-q)*surrogate(r, weak, e) + q*surrogate(r, audited, e)
        distance = max(1-e-r, r-1-e, F(0))
        require(gap >= 0 and direct == surrogate(r, full, e)-distance*gap, 'surrogate gap identity')
        w, f = surrogate(r, weak, e), surrogate(r, full, e)
        require((1-q)*w + q*correction(w, f, q, 1) == f, 'loss correction identity')
        if r not in (1-e, 1+e):
            w_grad, f_grad = ratio_gradient(r, weak, e), ratio_gradient(r, full, e)
            expected_grad = (1-q)*w_grad + q*ratio_gradient(r, audited, e)
            side = 1 if r > 1+e else (-1 if r < 1-e else 0)
            require(expected_grad == f_grad-side*gap, 'gradient gap identity')
            require((1-q)*w_grad+q*correction(w_grad, f_grad, q, 1) == f_grad,
                    'fixed-state gradient correction identity')
        cases += 1
    reused = reuse_example()
    require(reused['reused_second_expected_gradient'] == F(-48, 25), 'reused-mask example')
    require(reused['full_at_visited_expected_gradient'] == F(-49, 25), 'visited-state target')
    require(reused['fresh_or_cached_second_expected_gradient'] == F(-49, 25), 'fresh-or-cached example')
    return dict(scope='Constructed fixed-batch algebra and a two-action example; no LLM training or measured outcome claim.',
                fixed_ratio_cases=cases,
                clipping_example=dict(weak='1', full='-1', q='1/4', ratio='3/2', epsilon='1/5',
                    expected_plugin_surrogate='-69/40', full_surrogate='-3/2',
                    expected_plugin_ratio_gradient='-7/4', full_ratio_gradient='-1', positive_gap='3/4'),
                reuse_example={k:([str(v) for v in value] if isinstance(value, list) else str(value))
                               for k, value in reused.items()})


def verify_autograd():
    """Optional CPU float64 check using an already-installed PyTorch runtime."""
    import torch

    def tensor(value):
        return torch.tensor(float(value), dtype=torch.float64, device='cpu', requires_grad=True)

    def ell(r, a):
        return torch.minimum(r*float(a), torch.clamp(r, 0.8, 1.2)*float(a))

    maximum_error, cases = 0.0, 0
    e = F(1, 5)
    for weak, full, q, r in product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2],
                                  [F(1, 10), F(1, 4), F(1, 2), F(1)],
                                  [F(1, 2), F(1), F(3, 2), F(2)]):
        x = tensor(r)
        audited = correction(weak, full, q, 1)
        weak_loss, full_loss = ell(x, weak), ell(x, full)
        plugin = float(1-q)*weak_loss + float(q)*ell(x, audited)
        after_loss = float(1-q)*weak_loss + float(q)*(weak_loss+(full_loss-weak_loss)/float(q))
        exact_plugin = (1-q)*surrogate(r, weak, e)+q*surrogate(r, audited, e)
        exact_plugin_gradient = (1-q)*ratio_gradient(r, weak, e)+q*ratio_gradient(r, audited, e)
        for actual, value, derivative in [(plugin, exact_plugin, exact_plugin_gradient),
                                         (after_loss, surrogate(r, full, e), ratio_gradient(r, full, e))]:
            actual_gradient = torch.autograd.grad(actual, x, retain_graph=True)[0].item()
            maximum_error = max(maximum_error, abs(actual.item()-float(value)),
                                abs(actual_gradient-float(derivative)))
        cases += 1

    def full_objective(theta):
        return (ell(theta*theta, -1)+ell(2-theta*theta, 1))/2

    reused = full_visited = 0.0
    for z in [0, 1]:
        theta0 = tensor(1)
        g1 = torch.autograd.grad((2*z)*full_objective(theta0), theta0)[0].item()
        theta1 = tensor(1+g1/100)  # optimizer step is detached, not meta-differentiated
        reference = full_objective(theta1)
        reused += torch.autograd.grad((2*z)*reference, theta1, retain_graph=True)[0].item()/2
        full_visited += torch.autograd.grad(reference, theta1)[0].item()/2
    maximum_error = max(maximum_error, abs(reused-float(F(-48, 25))),
                        abs(full_visited-float(F(-49, 25))))
    require(maximum_error < 1e-12, 'PyTorch does not match the exact reference within tolerance')
    return dict(torch_version=str(torch.__version__), dtype='float64', device='cpu',
                fixed_ratio_cases=cases, maximum_absolute_error=maximum_error,
                reused_second_expected_gradient=reused,
                full_at_visited_expected_gradient=full_visited)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--autograd', action='store_true', help='also check an already-installed PyTorch runtime')
    args = parser.parse_args()
    result = verify()
    if args.autograd:
        result['optional_autograd'] = verify_autograd()
    print(json.dumps(result, indent=2, sort_keys=True))
