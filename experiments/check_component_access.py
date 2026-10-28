"""Exact checks for the component-access scope counterexample.

python -B -S -m experiments.check_component_access
No real benchmark is run. No population is allocated for the large examples.
"""
from fractions import Fraction as F
from itertools import product
import json

from goodhart_audit.screening_math import kl_bounds, log_bounds, rational


def require(condition,message):
    if not condition:
        raise ValueError(message)


def positive_integer(value):
    if type(value) is not int:
        raise TypeError('expected an integer, excluding bool')
    require(value>0,'expected a positive integer')
    return value


def raw_component_upper(N,c,tau,epsilon,delta):
    """Ceiling of a likelihood/census upper bound with unit-cost raw access."""
    N,c=positive_integer(N),positive_integer(c)
    tau,epsilon,delta=map(rational,(tau,epsilon,delta))
    require(0<epsilon<tau<=F(1,8) and 0<delta<=F(1,4),'risk/error parameters')
    theta=tau-epsilon
    numerator=log_bounds(1/delta)[1]+log_bounds((1-theta)/(1-tau))[1]
    bound=numerator/kl_bounds(theta,tau)[0]
    return min(N*c,-((-bound.numerator)//bound.denominator))


def risks(failure_counts,c):
    """Uniform component and any-failure program risks from exact row counts."""
    c=positive_integer(c)
    counts=tuple(failure_counts)
    require(bool(counts),'nonempty population required')
    for count in counts:
        if type(count) is not int:
            raise TypeError('failure counts must be integers, excluding bool')
        require(0<=count<=c,'failure count outside [0,c]')
    return F(sum(counts),len(counts)*c),F(sum(x>0 for x in counts),len(counts))


def verify():
    profiles=0
    for counts in product(range(4),repeat=2):
        component,program=risks(counts,3)
        require(component<=program<=min(3*component,1),'mean-to-program-risk inequality')
        profiles+=1
    rows=[]
    examples=[('wide',13000,64,F(1,64),F(9,640),1300,1),
              ('small relative margin',70000000,8192,F(1,512),F(1,8192),70000000,15)]
    for name,N,c,tau,eps,bad_programs,failures_per_bad in examples:
        component=F(bad_programs*failures_per_bad,N*c)
        program=F(bad_programs,N)
        require(component==tau-eps,'symbolic margin counterexample')
        require(program>tau,'program risk must exceed the component threshold')
        rows.append(dict(name=name,N=N,components=c,tau=str(tau),epsilon=str(eps),
                         raw_component_cost_upper=raw_component_upper(N,c,tau,eps,F(1,20)),
                         failing_programs=bad_programs,failures_per_bad_program=failures_per_bad,
                         component_failure_at_margin=str(component),program_failure_at_margin=str(program)))
    return dict(scope='A stronger raw-component oracle and a different program-risk estimand; no measured LLM result.',
                small_profiles_checked=profiles,examples=rows)


if __name__=='__main__':
    print(json.dumps(verify(),indent=2,sort_keys=True))
