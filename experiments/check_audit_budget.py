"""Exact one-label benchmark and a constructed matched-budget comparison.

python -B -S -m experiments.check_audit_budget
python -B -m experiments.check_audit_budget --autograd
No downloads, model weights, or external verifier calls.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
import math

from experiments.check_audit_cache import AuditCache
from experiments.check_audit_surrogate import rational, require


def hazards(p, T, kind):
    """Deterministic fresh-query probabilities, indexed from round one."""
    p = rational(p)
    require(0 < p < 1, 'final purchase probability must lie in (0,1)')
    if type(T) is not int or T < 1:
        raise ValueError('round count must be a positive integer, excluding bool')
    if kind == 'inverse_survival':
        return tuple(p/(T*(1-p)+t*p) for t in range(1, T+1))
    if kind == 'equal_time':
        return tuple(p/(T-(t-1)*p) for t in range(1, T+1))
    raise ValueError('unknown schedule kind')


def moments(probabilities, d=1):
    """Enumerate first-query times, including never, with exact arithmetic."""
    qs, d = tuple(map(rational, probabilities)), rational(d)
    require(bool(qs) and all(0 < q < 1 for q in qs), 'nonempty probabilities in (0,1) required')
    T = len(qs)
    survival, masses = F(1), []
    for q in qs:
        masses.append(survival*q)
        survival *= 1-q
    masses.append(survival)
    require(sum(masses) == 1, 'first-query mass mismatch')
    means = [F(0)]*T
    cross = [[F(0) for _ in qs] for _ in qs]
    summed = F(0)
    for query_time, probability in enumerate(masses):
        errors = tuple(F(0) if t > query_time else (d*(1/qs[t]-1) if t == query_time else -d)
                       for t in range(T))
        summed += probability*sum(errors)**2
        for i in range(T):
            means[i] += probability*errors[i]
            for j in range(T):
                cross[i][j] += probability*errors[i]*errors[j]
    return dict(purchase_probability=1-survival, first_query_masses=tuple(masses),
                mean_errors=tuple(means), error_cross_moments=tuple(map(tuple, cross)),
                sum_step_mse=sum(cross[t][t] for t in range(T)), summed_error_mse=summed)


def verify():
    schedule_cases = allocation_cases = 0
    for T, p, d, kind in product(range(1, 7), [F(1, 10), F(1, 4), F(1, 2), F(3, 4), F(9, 10)],
                                 [-2, F(1, 3), 1], ['inverse_survival', 'equal_time']):
        qs = hazards(p, T, kind)
        result = moments(qs, d)
        bound = d*d*T*T*(1-p)/p
        expected = bound + (d*d*p*(T*T-1)/3 if kind == 'equal_time' else 0)
        require(result['purchase_probability'] == p, 'budget mismatch')
        require(result['sum_step_mse'] == result['summed_error_mse'] == expected, 'MSE formula mismatch')
        require(all(x == 0 for x in result['mean_errors']), 'mean mismatch')
        require(all(result['error_cross_moments'][i][j] == 0 for i in range(T) for j in range(T) if i != j),
                'martingale cross moments are nonzero')
        schedule_cases += 1
    # Allocate a fixed precision-increment budget in every positive integer
    # composition of eight into up to four parts. This is not a proof over
    # all algorithms; it checks nonuniform examples of the analytical bound.
    for T in range(1, 5):
        for parts in product(range(1, 9), repeat=T):
            if sum(parts) != 8:
                continue
            for p in [F(1, 4), F(1, 2), F(3, 4)]:
                precision, qs = F(1), []
                for part in parts:
                    increment = p/(1-p)*F(part, 8)
                    precision += increment
                    qs.append(increment/precision)
                result = moments(qs)
                bound = T*T*(1-p)/p
                require(result['purchase_probability'] == p and result['sum_step_mse'] >= bound,
                        'allocation lower bound mismatch')
                require((result['sum_step_mse'] == bound) == (len(set(parts)) == 1),
                        'allocation equality condition mismatch')
                allocation_cases += 1
    return dict(scope='Finite algebra checks for the separately proved one-label benchmark; no training optimality claim.',
                schedule_cases=schedule_cases, allocation_cases=allocation_cases,
                example=dict(T=3, p='1/2', inverse_survival=['1/4', '1/5', '1/6'],
                             equal_time=['1/6', '1/5', '1/4'], sharp_sum_mse='9',
                             equal_time_sum_mse='31/3', reused_sum_step_mse='3',
                             reused_summed_error_mse='9'))


def compare_training(*, learning_rates=(0.05, 0.2, 0.8),
                     budgets=((F(1, 4), F(1, 8)), (F(1, 2), F(1, 4)), (F(3, 4), F(1, 2)))):
    """All branches of the declared two-group, three-update bandit experiment.

    Report accuracy of raw gradients at each method's visited parameters.
    Reward is the defined synthetic bandit reward, not an LLM outcome.
    The theorem's optimum assumes constant discrepancy; no such assumption
    is made for this comparison, and no method is required to win.
    """
    import torch

    dtype = torch.float64
    features = torch.tensor([[1., 0.5], [-0.25, 1.]], dtype=dtype)
    weak = torch.tensor([[0., 1., -1.], [1., -1., 0.]], dtype=dtype)
    full = torch.tensor([[1., -1., 0.], [-2., 1., 1.]], dtype=dtype)
    targets = ((1., -1., 0.), (-2., 1., 1.))
    T = 3

    def gradient(values, decisions=None):
        parameter = torch.nn.Parameter(values.clone())
        ratio = (features @ parameter).softmax(dim=-1)*3
        def clipped(advantages):
            return torch.minimum(ratio*advantages, ratio.clamp(0.8, 1.2)*advantages)
        if decisions is None:
            value = clipped(full).mean()
        else:
            # Full targets above are evaluator-only. The estimator obtains
            # its target values exclusively through the audit decisions.
            weak_terms = clipped(weak)
            groups = []
            for g, decision in enumerate(decisions):
                if decision.full_advantages is None:
                    groups.append(weak_terms[g])
                else:
                    a = torch.tensor(decision.full_advantages, dtype=dtype)
                    f = torch.minimum(ratio[g]*a, ratio[g].clamp(0.8, 1.2)*a)
                    groups.append(weak_terms[g]+float(decision.weight)*(f-weak_terms[g]))
            value = torch.stack(groups).mean()
        derivative = torch.autograd.grad(value, parameter)[0].detach()
        return parameter, derivative

    def run(purchases, rate, mode):
        schedules = [hazards(p, T, mode if mode != 'reuse' else 'inverse_survival') for p in purchases]
        stats = dict(gradient_mse=[0.]*T, conditional_bias_squared=[0.]*T,
                     summed_error_mse=0., expected_final_full_reward=0., leaves=0, conditional_states=0)
        marginal_errors = [torch.zeros((2, 3), dtype=dtype) for _ in range(T)]
        expected_cost = mass = F(0)

        def visit(values, cache, step, path_probability, error_sum, frozen=None):
            nonlocal expected_cost, mass
            if step == T:
                stats['leaves'] += 1
                mass += path_probability
                expected_cost += path_probability*3*cache.purchases
                stats['summed_error_mse'] += float(path_probability)*float((error_sum**2).sum())
                reward = ((features @ values).softmax(dim=-1)*full).sum(dim=-1).mean().item()
                stats['expected_final_full_reward'] += float(path_probability)*reward
                return
            stats['conditional_states'] += 1
            _, reference = gradient(values)
            probabilities = {g: (purchases[g] if mode == 'reuse' else schedules[g][step]) for g in range(2)}
            unknown = (() if mode == 'reuse' and step > 0 else
                       tuple(g for g in range(2) if g not in cache.known_groups))
            expected_error = torch.zeros_like(values)
            conditional_mse, branch_mass = 0., F(0)
            for choices in product([False, True], repeat=len(unknown)):
                selected = dict(zip(unknown, choices))
                probability = F(math.prod(probabilities[g] if z else 1-probabilities[g]
                                          for g, z in selected.items()))
                branch_mass += probability
                branch = deepcopy(cache)
                if mode != 'reuse' or step == 0:
                    branch.begin_update(probabilities, lambda g, q: selected[g], lambda g: targets[g])
                    decisions = tuple(branch.decision(g) for g in range(2))
                    branch.end_update()
                else:
                    decisions = frozen
                parameter, actual = gradient(values, decisions)
                error = actual-reference
                expected_error += float(probability)*error
                conditional_mse += float(probability)*float((error**2).sum())
                optimizer = torch.optim.SGD([parameter], lr=rate, maximize=True)
                parameter.grad = actual.clone()
                optimizer.step()
                visit(parameter.detach().clone(), branch, step+1, path_probability*probability,
                      error_sum+error, decisions if mode == 'reuse' else None)
            require(branch_mass == 1, 'conditional branch mass mismatch')
            stats['gradient_mse'][step] += float(path_probability)*conditional_mse
            stats['conditional_bias_squared'][step] += float(path_probability)*float((expected_error**2).sum())
            marginal_errors[step] += float(path_probability)*expected_error

        zero = torch.zeros((2, 3), dtype=dtype)
        visit(zero, AuditCache(), 0, F(1), zero)
        require(mass == 1 and expected_cost == 3*sum(purchases), 'matched total budget mismatch')
        cross_term = stats['summed_error_mse']-sum(stats['gradient_mse'])
        if mode != 'reuse':
            require(max(stats['conditional_bias_squared']) < 1e-24, 'conditional bias in fresh rule')
            require(abs(cross_term) < 1e-10, 'fresh-rule martingale identity mismatch')
        return dict(expected_distinct_labels=str(expected_cost),
                    marginal_gradient_bias_norm=[x.norm().item() for x in marginal_errors],
                    error_cross_term=cross_term, **stats)

    settings = []
    for rate, purchases in product(learning_rates, budgets):
        require(type(rate) in (int, float) and math.isfinite(rate) and rate > 0, 'positive finite rate required')
        purchases = tuple(map(rational, purchases))
        require(len(purchases) == 2, 'exactly two group budgets required')
        settings.append(dict(learning_rate=rate, final_purchase_probabilities=list(map(str, purchases)),
                             methods={mode: run(purchases, rate, mode)
                                      for mode in ('reuse', 'equal_time', 'inverse_survival')}))
    return dict(scope='Declared constructed settings; exact audit enumeration, floating-point gradients; no LLM benefit claim.',
                torch_version=str(torch.__version__), dtype='float64', device='cpu',
                updates=T, settings=settings)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--autograd', action='store_true', help='run the installed-PyTorch matched-budget comparison')
    args = parser.parse_args()
    result = verify()
    if args.autograd:
        result['tensor_comparison'] = compare_training()
    print(json.dumps(result, indent=2, sort_keys=True))
