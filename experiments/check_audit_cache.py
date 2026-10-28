"""Enumerated audit-cache experiment, not a production trainer or LLM study.

python -B -S -m experiments.check_audit_cache
python -B -m experiments.check_audit_cache --autograd
"""
import argparse
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
import json
import math

from experiments.check_audit_surrogate import rational, require


@dataclass(frozen=True)
class Decision:
    full_advantages: tuple | None
    weight: F


class AuditCache:
    """One immutable batch's targets; a fresh instance is needed for a new batch.

    The caller supplies a correctly randomized draw(group, probability) and an
    immutable-reference audit(group). Deterministic draws below enumerate that
    design. This class does not certify a caller's sampling law. Audit callback
    errors abort the experiment; external purchases are not transactional.
    """

    def __init__(self):
        self._labels = {}
        self._decisions = None

    @property
    def purchases(self):
        return len(self._labels)

    @property
    def known_groups(self):
        return frozenset(self._labels)

    def begin_update(self, probabilities, draw, audit):
        if self._decisions is not None:
            raise RuntimeError('finish the current optimizer update first')
        probabilities = {g: rational(q) for g, q in probabilities.items()}
        for q in probabilities.values():
            require(0 < q <= 1, 'audit probabilities must lie in (0,1]')
        decisions, new_labels = {}, {}
        for group, q in probabilities.items():
            if group in self._labels:
                decisions[group] = Decision(self._labels[group], F(1))
                continue
            selected = draw(group, q)
            if type(selected) is not bool:
                raise TypeError('the draw must return a bool')
            require(q != 1 or selected, 'probability-one audit cannot be unselected')
            if selected:
                labels = tuple(audit(group))
                require(bool(labels), 'full advantages must be nonempty')
                if any(type(a) not in (int, float, F) for a in labels):
                    raise TypeError('advantages must be plain finite scalar values')
                labels = tuple(float(a) for a in labels)
                require(all(math.isfinite(a) for a in labels), 'nonfinite full advantage')
                new_labels[group] = labels
                decisions[group] = Decision(labels, 1/q)
            else:
                decisions[group] = Decision(None, F(0))
        # Cache visibility and this update's weight are deliberately separate.
        self._labels.update(new_labels)
        self._decisions = decisions

    def decision(self, group):
        if self._decisions is None:
            raise RuntimeError('no optimizer update is active')
        return self._decisions[group]

    def end_update(self):
        if self._decisions is None:
            raise RuntimeError('no optimizer update is active')
        self._decisions = None


def microbatch_example():
    """Two chunks of one group: zero weak gradient and unit full gradient each."""
    q = F(1, 4)
    correct = premature = purchases = F(0)
    for selected, probability in [(False, 1-q), (True, q)]:
        cache = AuditCache()
        cache.begin_update({'group': q}, lambda *args: selected, lambda g: [-1, 1])
        first = cache.decision('group').weight
        second = cache.decision('group').weight
        correct += probability*(first+second)
        # Incorrect: treat the newly bought target as pre-existing in chunk 2.
        premature += probability*(first + int('group' in cache.known_groups))
        purchases += probability*cache.purchases
        cache.end_update()
    require(correct == 2 and premature == F(5, 4), 'microbatch counterexample')
    return dict(full_gradient=F(2), frozen_update_weight_mean=correct,
                premature_cache_switch_mean=premature, expected_group_purchases=purchases)


def verify_training_loop():
    """Enumerate all conditional audit branches of three actual CPU SGD steps.

    Advantages, old policy and batch weights are fixed. Groups share model
    parameters. Full-reference gradients are evaluated at each visited state,
    not along a separate full-audit trajectory. No stochastic text generation.
    """
    import torch

    dtype = torch.float64
    features = torch.tensor([[1.0, 0.5], [-0.25, 1.0]], dtype=dtype)
    old = torch.full((2, 3), 1/3, dtype=dtype)  # frozen uniform sampling policy
    weak = ((0., 1., -1.), (1., -1., 0.))
    full = ((1., -1., 0.), (-2., 1., 1.))
    probabilities = {0: F(1, 2), 1: F(1, 4)}
    rows = tuple(product(range(2), range(3)))
    partitions = ((rows,), (rows[:3], rows[3:]),
                  (((1, 2), (0, 0)), ((0, 2), (1, 0)), ((1, 1), (0, 1))))
    updates, learning_rate = 3, 0.8
    stats = dict(conditional_states=0, leaves=0, clipping_active_states=0,
                 maximum_conditional_gradient_error=0.0,
                 maximum_conditional_objective_error=0.0,
                 maximum_partition_gradient_error=0.0,
                 maximum_finite_difference_error=0.0)
    expected_labels, total_probability = F(0), F(0)

    def ell(ratio, advantage):
        return torch.minimum(ratio*advantage, ratio.clamp(0.8, 1.2)*advantage)

    def objective(parameters, chunk, cache=None):
        ratios = (features @ parameters).softmax(dim=-1)/old
        terms = []
        for group, action in chunk:
            r = ratios[group, action]
            if cache is None:
                term = ell(r, full[group][action])
            else:
                d = cache.decision(group)
                w = ell(r, weak[group][action])
                term = w if d.full_advantages is None else (
                    w + float(d.weight)*(ell(r, d.full_advantages[action])-w))
            terms.append(term/len(rows))  # fixed full-batch denominator
        return torch.stack(terms).sum()

    def accumulated(parameters, partition, cache=None):
        parameters.grad = None
        value = 0.0
        for chunk in partition:
            contribution = objective(parameters, chunk, cache)
            contribution.backward()
            value += contribution.item()
        return value, parameters.grad.detach().clone()

    def visit(values, cache, step, path_probability):
        nonlocal expected_labels, total_probability
        if step == updates:
            stats['leaves'] += 1
            expected_labels += path_probability*3*cache.purchases
            total_probability += path_probability
            return
        stats['conditional_states'] += 1
        parameters = torch.nn.Parameter(values.clone())
        target_value, target_gradient = accumulated(parameters, partitions[0])
        ratios = ((features @ values).softmax(dim=-1)/old).detach()
        full_tensor = torch.tensor(full, dtype=dtype)
        if bool(((full_tensor > 0) & (ratios > 1.2)
                 | (full_tensor < 0) & (ratios < 0.8)).any()):
            stats['clipping_active_states'] += 1
        # Central differences use the independently evaluated full objective.
        h = 1e-6
        require(float(torch.minimum(abs(ratios-0.8), abs(ratios-1.2)).min()) > 1e-4,
                'finite differences require distance from clipping knots')
        for index in product(range(2), range(3)):
            plus, minus = values.clone(), values.clone()
            plus[index] += h
            minus[index] -= h
            numerical = (objective(plus, rows).item()-objective(minus, rows).item())/(2*h)
            stats['maximum_finite_difference_error'] = max(
                stats['maximum_finite_difference_error'], abs(numerical-target_gradient[index].item()))

        unknown = tuple(g for g in probabilities if g not in cache.known_groups)
        expected_value, expected_gradient = 0.0, torch.zeros_like(values)
        branch_mass = F(0)
        for choices in product([False, True], repeat=len(unknown)):
            selected = dict(zip(unknown, choices))
            probability = math.prod(probabilities[g] if z else 1-probabilities[g]
                                    for g, z in selected.items())
            probability = F(probability)
            branch_mass += probability
            branch = deepcopy(cache)
            branch.begin_update(probabilities, lambda g, q: selected[g], lambda g: full[g])
            branch_parameters = torch.nn.Parameter(values.clone())
            actual_value, actual_gradient = accumulated(branch_parameters, partitions[0], branch)
            for partition in partitions[1:]:
                other_value, other_gradient = accumulated(branch_parameters, partition, branch)
                require(abs(actual_value-other_value) < 1e-12, 'partition objective mismatch')
                stats['maximum_partition_gradient_error'] = max(
                    stats['maximum_partition_gradient_error'],
                    (actual_gradient-other_gradient).abs().max().item())
            expected_value += float(probability)*actual_value
            expected_gradient += float(probability)*actual_gradient
            # Plain SGD has no optimizer state to carry between tree nodes.
            optimizer = torch.optim.SGD([branch_parameters], lr=learning_rate, maximize=True)
            branch_parameters.grad = actual_gradient.clone()
            optimizer.step()
            branch.end_update()
            visit(branch_parameters.detach().clone(), branch, step+1, path_probability*probability)
        require(branch_mass == 1, 'conditional branch probabilities do not sum to one')
        stats['maximum_conditional_objective_error'] = max(
            stats['maximum_conditional_objective_error'], abs(expected_value-target_value))
        stats['maximum_conditional_gradient_error'] = max(
            stats['maximum_conditional_gradient_error'],
            (expected_gradient-target_gradient).abs().max().item())

    visit(torch.zeros((2, 3), dtype=dtype), AuditCache(), 0, F(1))
    require(total_probability == 1, 'leaf probabilities do not sum to one')
    analytic_cost = 3*sum(1-(1-q)**updates for q in probabilities.values())
    require(expected_labels == analytic_cost == F(279, 64), 'distinct-label cost mismatch')
    for key in ('maximum_conditional_gradient_error', 'maximum_conditional_objective_error',
                'maximum_partition_gradient_error'):
        require(stats[key] < 1e-12, key)
    require(stats['maximum_finite_difference_error'] < 1e-8, 'finite-difference mismatch')
    require(stats['clipping_active_states'] > 0, 'the experiment must exercise clipping')
    return dict(scope='Constructed categorical policy; no LLM training benefit or novelty claim.',
                torch_version=str(torch.__version__), device='cpu', dtype='float64',
                optimizer='SGD ascent, no momentum', learning_rate=learning_rate,
                optimizer_updates_per_path=updates, expected_distinct_labels=str(expected_labels),
                **stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--autograd', action='store_true', help='run the installed-PyTorch experiment')
    args = parser.parse_args()
    result = {'microbatch_example': {k: str(v) for k, v in microbatch_example().items()}}
    if args.autograd:
        result['tensor_training_loop'] = verify_training_loop()
    print(json.dumps(result, indent=2, sort_keys=True))
