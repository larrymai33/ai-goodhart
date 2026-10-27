"""Exact finite-population arithmetic for the fixed checkpoint reference.

Convex-order extremal laws control hinge expectations, not raw tail
probabilities. See docs/finite-checkpoint-theorem.md for the distinction.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb

MAX_POPULATION = 2048


def _rational(value, name):
    if isinstance(value,bool) or not isinstance(value,(int,F)):
        raise ValueError(name+' must be an integer or Fraction')
    return F(value)


@dataclass(frozen=True)
class ExtremalLaw:
    """Sorted (sample sum, integer mass) pairs and their common denominator."""
    masses: tuple
    denominator: int


def extremal_law(population, omitted, total):
    """Law of an observed sample from floor(total) ones, a remainder, zeros.

    The observed subset is uniform of size population-omitted. Input sizes
    are bounded; total must be exact. The returned law is immutable.
    """
    if type(population) is not int or not 1<=population<=MAX_POPULATION:
        raise ValueError('population must be an integer in [1,2048]')
    if type(omitted) is not int or not 0<=omitted<=population:
        raise ValueError('omitted must be an integer in [0,population]')
    total=_rational(total,'total')
    if not 0<=total<=population:
        raise ValueError('total must lie in [0,population]')
    j=total.numerator//total.denominator
    remainder=total-j
    masses=[]
    if not remainder:
        for z in range(max(0,omitted-(population-j)),min(j,omitted)+1):
            masses.append((F(j-z),comb(j,z)*comb(population-j,omitted-z)))
    else:
        zeros=population-j-1
        # Fractional entry omitted, then acquired.
        for z in range(max(0,omitted-1-zeros),min(j,omitted-1)+1):
            masses.append((F(j-z),comb(j,z)*comb(zeros,omitted-1-z)))
        for z in range(max(0,omitted-zeros),min(j,omitted)+1):
            masses.append((F(j-z)+remainder,comb(j,z)*comb(zeros,omitted-z)))
    return ExtremalLaw(tuple(sorted(masses)),comb(population,omitted))


def lower_shortfall(law, alpha):
    """Mean of the lower alpha probability mass, including partial atoms.

    law must be an ExtremalLaw produced by extremal_law. Passing at this
    cutoff requires STRICT sample_sum < cutoff.
    """
    alpha=_rational(alpha,'alpha')
    if not 0<alpha<=1:
        raise ValueError('alpha must lie in (0,1]')
    remaining=alpha*law.denominator
    numerator=F(0)
    for value,count in law.masses:
        take=min(F(count),remaining)
        numerator+=take*value
        remaining-=take
        if remaining==0:
            break
    return numerator/(alpha*law.denominator)


def upper_tail(law, cutoff):
    """Best upper hinge bound on P(sample_sum >= cutoff), capped at one.

    law must be an ExtremalLaw produced by extremal_law. No substitution
    of a raw extremal tail probability for the hinge bound is valid.
    """
    cutoff=_rational(cutoff,'cutoff')
    if cutoff>law.masses[-1][0]:
        return F(0)
    remaining_mass=law.denominator
    remaining_sum=sum((value*count for value,count in law.masses),F(0))
    if cutoff*law.denominator<=remaining_sum:
        return F(1)
    best=F(1)
    for value,count in law.masses:
        remaining_mass-=count
        remaining_sum-=value*count
        if value<cutoff:
            best=min(best,(remaining_sum-value*remaining_mass)
                     /(law.denominator*(cutoff-value)))
    return best


def head_bin(total, gap, top):
    """Unit-width bin of a fixed head statistic; top belongs to the last bin."""
    total=_rational(total,'head statistic')
    gap=_rational(gap,'gap')
    top=_rational(top,'top')
    if not 0<=gap<=total<=top:
        raise ValueError('require 0 <= gap <= head statistic <= top')
    if gap==top:
        return (gap,top)
    span=top-gap
    count=(span.numerator+span.denominator-1)//span.denominator
    offset=total-gap
    index=min(offset.numerator//offset.denominator,count-1)
    lower=gap+index
    return lower,min(lower+1,top)
