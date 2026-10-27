"""Exact finite-pool laws and design-based uncertainty for rank audits.

Rank zero is best. A target budget ``n`` selects the best of a uniformly
sampled n-subset of a fixed, totally ordered pool. These functions compute
that finite-pool estimand; they make no population-generalization claim.
"""

from __future__ import annotations

from collections.abc import Sequence
import math
from numbers import Real


def _integer(value: int, name: str, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, not a boolean or fractional value")
    if value < minimum or (maximum is not None and value > maximum):
        interval = f"[{minimum}, {maximum}]" if maximum is not None else f">= {minimum}"
        raise ValueError(f"{name} must be {interval}")
    return value


def _unit_value(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{name} must be a finite number in [0, 1]") from None
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    return number


def _probabilities(values: Sequence[float], name: str) -> list[float]:
    probabilities = [_unit_value(value, name) for value in values]
    if not probabilities or not math.isclose(
        math.fsum(probabilities), 1.0, rel_tol=1e-12, abs_tol=1e-12
    ):
        raise ValueError(f"{name} must be a nonempty probability vector summing to 1")
    return probabilities


def _budgets(m: int, budgets: Sequence[int]) -> list[int]:
    result = [_integer(n, "budget", 1, m) for n in budgets]
    if not result:
        raise ValueError("budgets must not be empty")
    if len(set(result)) != len(result):
        raise ValueError("budgets must not contain duplicates")
    return result


def rank_weights(m: int, n: int) -> list[float]:
    """Return the descending-rank winner probabilities of a uniform n-subset.

    At one-based rank r the exact law is C(m-r, n-1) / C(m, n).
    An adjacent-rank recurrence evaluates the law in O(m) time without
    constructing large binomial coefficients. Floating-point results are
    normalized to remove accumulated rounding error from the recurrence.
    """
    m = _integer(m, "m", 1)
    n = _integer(n, "n", 1, m)
    weights = [0.0] * m
    weights[0] = n / m
    for r in range(1, m - n + 1):
        weights[r] = weights[r - 1] * ((m - r - n + 1) / (m - r))
    total = math.fsum(weights)
    return [weight / total for weight in weights]


def envelope_proposal(m: int, budgets: Sequence[int]) -> tuple[list[float], float]:
    """Return q(r) proportional to max_n w_n(r), and its normalizer Z.

    The proposal minimizes the largest importance ratio over the supplied
    budgets. Z is that minimax ratio. Budgets must be distinct; zeros are
    allowed only at ranks outside the union of target supports. If a
    mathematically positive tail probability underflows, this function
    raises ValueError; full_envelope provides a positive-support alternative.
    """
    m = _integer(m, "m", 1)
    grid = _budgets(m, budgets)
    envelope = [0.0] * m
    for n in grid:
        weights = rank_weights(m, n)
        for r, weight in enumerate(weights):
            envelope[r] = max(envelope[r], weight)
    normalizer = math.fsum(envelope)
    proposal = [weight / normalizer for weight in envelope]
    if any(proposal[r] == 0.0 for r in range(m - min(grid) + 1)):
        raise ValueError("envelope probability underflow on target support; use full_envelope")
    return proposal, normalizer


def _rank_probability(m: int, n: int, r: int) -> float:
    """Evaluate one positive weight at a one-based rank using a short product."""
    probability = n / m
    if n <= r:
        for j in range(n - 1):
            probability *= (m - r - j) / (m - 1 - j)
    else:
        for j in range(r - 1):
            probability *= (m - n - j) / (m - 1 - j)
    return probability


def full_envelope(m: int, max_budget: int | None = None) -> tuple[list[float], float]:
    """Return the envelope for every integer budget 1 through max_budget.

    At one-based rank r, a maximizing budget is
    min(max_budget, floor((m+1)/r)), capped to [1, m]. Adjacent ranks with
    the same maximizer share a recurrence. Consequently this method avoids
    constructing the O(m * max_budget) matrix of all target laws.
    """
    m = _integer(m, "m", 1)
    cap = m if max_budget is None else _integer(max_budget, "max_budget", 1, m)
    envelope = []
    previous_budget = None
    previous_weight = 0.0
    for r in range(1, m + 1):
        n = min(cap, max(1, (m + 1) // r))
        if n == previous_budget:
            weight = previous_weight * ((m - r - n + 2) / (m - r + 1))
        else:
            weight = _rank_probability(m, n, r)
        envelope.append(weight)
        previous_budget, previous_weight = n, weight
    normalizer = math.fsum(envelope)
    return [weight / normalizer for weight in envelope], normalizer


def estimate_risk(
    ranks: Sequence[int],
    losses: Sequence[float],
    proposal: Sequence[float],
    budgets: Sequence[int],
    delta: float = 0.05,
) -> list[dict[str, int | float]]:
    """Estimate all requested risks with simultaneous empirical Bernstein CIs.

    Ranks are zero-based IID draws with replacement from the *fixed*
    proposal. Each observed loss is in [0, 1] from a fixed label oracle.
    For multiple pools, prompt selection must also be IID and uniform;
    loss can then vary between observations at the same rank. Repeated
    draws remain repeated observations even when their label is cached.

    With B >= 2 draws and K budgets, the two-sided union-bound radius is
    sqrt(2 s^2 log(4K/delta)/B) + 7 M log(4K/delta)/(3(B-1)), where s^2 is
    the unbiased sample variance of X = w_n(rank) * loss / q(rank), and
    M = max_rank w_n(rank)/q(rank). This is a finite-sample bound conditional
    on the fixed pools, proposal, budgets and label oracle. It does not
    apply to adaptive sampling or stochastic unrepeated label judgments.

    Intervals are clipped to [0, 1]; the unbiased point estimate is not.
    """
    q = _probabilities(proposal, "proposal")
    m = len(q)
    grid = _budgets(m, budgets)
    confidence = _unit_value(delta, "delta")
    if not 0.0 < confidence < 1.0:
        raise ValueError("delta must be strictly between 0 and 1")
    sampled_ranks = [_integer(rank, "rank", 0, m - 1) for rank in ranks]
    observed_losses = [_unit_value(loss, "loss") for loss in losses]
    draws = len(sampled_ranks)
    if draws != len(observed_losses):
        raise ValueError("ranks and losses must have the same length")
    if draws < 2:
        raise ValueError("at least two IID draws are required")
    if any(q[rank] == 0.0 for rank in sampled_ranks):
        raise ValueError("sampled ranks must have positive proposal probability")
    # Use combinatorial support, even if a tiny floating-point weight underflows.
    if any(q[r] == 0.0 for r in range(m - min(grid) + 1)):
        raise ValueError("proposal must be positive on every requested target support")
    # Taking logs separately also accommodates very small positive delta.
    log_factor = math.log(4.0) + math.log(len(grid)) - math.log(confidence)
    results = []
    for n in grid:
        weights = rank_weights(m, n)
        ratios = [weight / probability if probability else 0.0
                  for weight, probability in zip(weights, q)]
        maximum = max(ratios)
        if not math.isfinite(maximum):
            raise ValueError("importance ratios exceed floating-point range")
        observations = [ratios[rank] * loss
                        for rank, loss in zip(sampled_ranks, observed_losses)]
        # Scale the mean only by observed values: an enormous global M can
        # otherwise erase small, nonzero observations through underflow.
        observed_maximum = max(observations)
        estimate = (
            observed_maximum * (math.fsum(value / observed_maximum for value in observations) / draws)
            if observed_maximum else 0.0
        )
        # Scaling by M keeps the sample variance calculation in [0, 1].
        scaled = [value / maximum for value in observations]
        scaled_mean = math.fsum(scaled) / draws
        variance = math.fsum((value - scaled_mean) ** 2 for value in scaled) / (draws - 1)
        radius = maximum * (
            math.sqrt(2.0 * variance * log_factor / draws)
            + 7.0 * log_factor / (3.0 * (draws - 1))
        )
        if not math.isfinite(radius):
            raise ValueError("confidence radius exceeds floating-point range")
        results.append({
            "budget": n,
            "estimate": estimate,
            "lower": max(0.0, min(1.0, estimate - radius)),
            "upper": max(0.0, min(1.0, estimate + radius)),
            "radius": radius,
            "max_weight": maximum,
        })
    return results


def partial_bounds(
    labels: Sequence[float | None], weights: Sequence[float]
) -> tuple[float, float]:
    """Give the exact range over all [0,1] completions of missing labels.

    ``None`` denotes a missing label, and weights are a probability vector.
    Unlike confidence bounds, these are deterministic identification bounds.
    """
    probabilities = _probabilities(weights, "weights")
    observed = [None if label is None else _unit_value(label, "label") for label in labels]
    if len(observed) != len(probabilities):
        raise ValueError("labels and weights must have the same length")
    lower = math.fsum(weight * label for label, weight in zip(observed, probabilities)
                      if label is not None)
    missing = math.fsum(weight for label, weight in zip(observed, probabilities)
                        if label is None)
    return lower, lower + missing
