"""Repeated screening for the ideal channel q(y)=1/4+y/2.

This is a research reference implementation. The caller supplies independent
ratings of a fixed table, exact grid scores, and independent uniform randomness.
Runtime validation cannot establish those statistical assumptions. See
docs/repeated-screening-theorem.md for the conditional guarantees.
"""
from dataclasses import dataclass
from fractions import Fraction
from secrets import randbelow as system_randbelow


def _integer(value, name, minimum=0):
    if type(value) is not int:
        raise TypeError(f'{name} must be an integer, excluding bool')
    if value < minimum:
        raise ValueError(f'{name} must be at least {minimum}')
    return value


def _rational(value, name):
    if type(value) not in (int, Fraction):
        raise TypeError(f'{name} must be int or Fraction, excluding bool')
    return Fraction(value)


def correction_probability(score, gate_height):
    """Coin probability after reaching the upper gate and buying this score."""
    score = _rational(score, 'score')
    _integer(gate_height, 'gate_height')
    if not 0 <= score <= 1:
        raise ValueError('score must be in [0,1]')
    q = Fraction(1, 4) + score/2
    ratio = (1-q)/(3*q)
    return 1-ratio**(gate_height+1)


@dataclass(frozen=True)
class ScreeningResult:
    status: str
    reason: str
    ratings: int
    adjudications: int
    payment: int
    proposals: int
    corrected_ones: int
    corrected_zeros: int


def audit(rating, adjudicate, *, population, exact_cost, tau, epsilon, delta,
          gate_height, randbelow=None, max_ratings=None):
    """Audit a fixed 1/exact_cost-grid table through two callbacks.

    `rating(i)` must return an int 0 or 1; `adjudicate(i)` returns an int or
    Fraction score. Items have indices 0,...,population-1. Exact scores are
    bought at most once. `randbelow(n)` must return independent uniform ints
    in range(n); default secrets.randbelow. It also supplies auxiliary coins.

    With max_ratings=None the theorem gives almost-sure safe completion.
    A nonnegative cap returns inconclusive before exceeding that many paid
    ratings. It does not cap free proposals or total computation. Callback
    errors propagate; an exception never returns a certificate. Payment
    counts successful valid callbacks, not any external cost incurred by a
    failing callback. No model calls or network operations occur here.
    """
    _integer(population, 'population', 1)
    _integer(exact_cost, 'exact_cost', 1)
    _integer(gate_height, 'gate_height')
    tau, epsilon, delta = (_rational(x, n) for x, n in
                           [(tau, 'tau'), (epsilon, 'epsilon'), (delta, 'delta')])
    if not 0 < epsilon < tau <= Fraction(1, 8):
        raise ValueError('require 0 < epsilon < tau <= 1/8')
    if not 0 < delta <= Fraction(1, 4):
        raise ValueError('require 0 < delta <= 1/4')
    if max_ratings is not None:
        _integer(max_ratings, 'max_ratings')
    random_source = system_randbelow if randbelow is None else randbelow
    if not all(callable(x) for x in (rating, adjudicate, random_source)):
        raise TypeError('oracles and randbelow must be callable')

    def draw(bound):
        value = random_source(bound)
        _integer(value, 'randbelow result')
        if value >= bound:
            raise ValueError('randbelow result out of range')
        return value

    def coin(probability):
        if probability == 0:
            return 0
        if probability == 1:
            return 1
        return int(draw(probability.denominator) < probability.numerator)

    cache = {}
    exact_sum = Fraction(0)
    ratings = proposals = ones = zeros = 0
    wealth = Fraction(1)
    p0, p1 = Fraction(2, 3)*tau, Fraction(2, 3)*(tau-epsilon)
    multiplier = ((1-p1)/(1-p0), p1/p0)

    def finish(status, reason):
        return ScreeningResult(status, reason, ratings, len(cache),
                               ratings+exact_cost*len(cache), proposals, ones, zeros)

    def paid_rating(item):
        nonlocal ratings
        value = rating(item)
        if type(value) is not int:
            raise TypeError('rating must be an int 0 or 1, excluding bool')
        if value not in (0, 1):
            raise ValueError('rating must be 0 or 1')
        ratings += 1
        return value

    while True:
        item = draw(population)
        proposals += 1
        if item in cache:
            emitted = coin(Fraction(2, 3)*cache[item])
        else:
            if max_ratings is not None and ratings >= max_ratings:
                return finish('inconclusive', 'rating_limit')
            initial = paid_rating(item)
            position = 0 if initial else -1
            while 0 <= position < gate_height:
                if max_ratings is not None and ratings >= max_ratings:
                    return finish('inconclusive', 'rating_limit')
                if paid_rating(item):
                    position += coin(Fraction(3, 4))
                else:
                    position -= coin(Fraction(1, 4))
            if position < 0:
                emitted = 0
            else:
                score = _rational(adjudicate(item), 'adjudicated score')
                if not 0 <= score <= 1 or (score*exact_cost).denominator != 1:
                    raise ValueError('adjudicated score must lie on the 1/exact_cost grid in [0,1]')
                cache[item] = score
                exact_sum += score
                if len(cache) == population:
                    return finish('certified' if exact_sum <= population*tau else 'rejected', 'census')
                emitted = coin(correction_probability(score, gate_height))
        ones += emitted
        zeros += 1-emitted
        wealth *= multiplier[emitted]
        if wealth*delta >= 1:
            return finish('certified', 'likelihood')
