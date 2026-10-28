"""Exact diagnostics for docs/repeated-screening-bundling.md.

Run with python -B -S -m experiments.check_screening_bundling.
Outputs JSON to stdout; no downloads, output files, or third-party dependencies.
The recurrence checks do not establish scientific novelty or prove all cases.
"""
from fractions import Fraction as F
import json

from experiments.check_repeated_screening import absorbing_solution


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_bundle(height):
    if type(height) is not int:
        raise TypeError('height must be an integer, excluding bool')
    require(height >= 0, 'height must be nonnegative')
    n = height+1
    g0 = F(1, 4*n)
    g1 = F(2, 3)/(1-F(1,9)**n)
    t0 = 1+F(2*height, 3)
    t1 = 1+F(4, 3)*(F(n)/(1-F(1,9)**n)-F(9,8))
    return dict(height=height, g0=g0, g1=g1, t0=t0, t1=t1,
                price=1+F(4*height,3),
                postprocess_0=(3*g0-g1)/2,
                postprocess_1=(3*g1-g0)/2,
                reverse_postprocess_1=(F(3,4)*(1-g0)-F(1,4)*(1-g1))/(g1-g0))


def verify():
    count = 0
    for height in range(53):
        row = binary_bundle(height)
        if height:
            require(row['postprocess_0'] < 0, 'bundle could be a garbling of one primitive report')
            require(row['reverse_postprocess_1'] > 1, 'primitive could be a garbling of the binary bundle')
            require(row['t0'] < row['t1'] < row['price'], 'label-dependent expected costs or price bound')
        for numerator in range(17):
            y = F(numerator,16)
            q = F(1,4)+y/2
            up, down = F(3,4)*q, F(1,4)*(1-q)
            hit = absorbing_solution(up, down, height, True)
            duration = absorbing_solution(up, down, height, False)
            cost = 1+q*duration
            require(cost <= row['price'], 'uniform expected-price bound')
            if numerator in (0,16):
                suffix = '0' if numerator == 0 else '1'
                require(q*hit == row['g'+suffix], 'closed-form bundled channel')
                require(cost == row['t'+suffix], 'closed-form paid duration')
            count += 1
    examples = []
    for height in (0,1,4,52):
        row = binary_bundle(height)
        examples.append({k: str(v) if isinstance(v,F) else v for k,v in row.items()})
    return dict(scope='Exact diagnostics for a report-interface comparison; no novelty or real-model claim.',
                gate_cases=count, examples=examples)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
