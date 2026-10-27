"""Anytime inference for fixed bounded labels sampled without replacement.

The acquisition rule must select each unseen item with probability
proportional to its fixed proposal mass. This specializes established
weighted-without-replacement betting martingales; it is not a population
generalization guarantee. See docs/anytime-related-work.md for attribution.
"""

from __future__ import annotations

from collections.abc import Sequence
import heapq
import math
from numbers import Real
import random


DEFAULT_BETS = (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125)


def _unit(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{name} must be a finite number in [0, 1]") from None
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    return number


def _integer(value: int, name: str, minimum: int | None = None,
             maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, not a boolean")
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        raise ValueError(f"{name} is out of range")
    return value


def _probabilities(values: Sequence[float], name: str) -> tuple[float, ...]:
    try:
        copied = tuple(_unit(value, name) for value in values)
    except TypeError:
        raise ValueError(f"{name} must be a probability vector") from None
    total = math.fsum(copied)
    if not copied or not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f"{name} must be a nonempty probability vector summing to 1")
    return tuple(value / total for value in copied)


class _MassTree:
    """Compensated nonnegative sum with O(log D) updates and no cancellation."""

    def __init__(self, values: Sequence[float]):
        self._size = 1 << (len(values) - 1).bit_length()
        self._nodes = [0.0] * (2 * self._size)
        self._errors = [0.0] * (2 * self._size)
        self._nodes[self._size:self._size + len(values)] = values
        for index in range(self._size - 1, 0, -1):
            self._combine(index)

    def _combine(self, node: int) -> None:
        terms = (self._nodes[2 * node], self._errors[2 * node],
                 self._nodes[2 * node + 1], self._errors[2 * node + 1])
        self._nodes[node] = math.fsum(terms)
        self._errors[node] = math.fsum((*terms, -self._nodes[node]))

    @property
    def total(self) -> float:
        return self._nodes[1]

    @property
    def components(self) -> tuple[float, float]:
        return self._nodes[1], self._errors[1]

    def set(self, index: int, value: float) -> None:
        node = self._size + index
        self._nodes[node] = value
        self._errors[node] = 0.0
        node //= 2
        while node:
            self._combine(node)
            node //= 2


def _log_add(left: float, right: float) -> float:
    high, low = max(left, right), min(left, right)
    if high == -math.inf:
        return high
    return high + math.log1p(math.exp(low - high))


class FinitePoolAudit:
    """Directional mixture confidence sequences for K finite weighted risks.

    Targets and proposal are copied and normalized within a 1e-12 rounding
    tolerance. Targets, proposal, bet fractions, and delta must be frozen
    before acquisition. Each observe call reveals one new fixed label in
    [0,1]; the caller must follow the weighted-WoR sampling design.

    Each directional process is the uniform mixture of fixed-fraction bets
    in ``bets`` (distinct values in (0,1]). The crossing threshold is
    2*K/delta. Intervals invert the *current* wealth and intersect current
    deterministic missing-label bounds; they are not running intersections.
    This still covers all targets at all stopping times with probability
    at least 1-delta under the stated design.

    Storage is O(K*D + K*B), observe is amortized O(K*log D), and inversion
    costs O(K*B*len(bets)) per bisection iteration. Bounds use floating-point
    arithmetic and return conservative outer brackets after 64 iterations.
    Endpoint roundoff is checked in original risk units before division by
    a possibly tiny remaining scale; this is not an arbitrary-precision engine.
    """

    def __init__(
        self,
        targets: Sequence[Sequence[float]],
        proposal: Sequence[float],
        delta: float = 0.05,
        bets: Sequence[float] = DEFAULT_BETS,
    ):
        self.proposal = _probabilities(proposal, "proposal")
        try:
            self.targets = tuple(_probabilities(target, "target") for target in targets)
        except TypeError:
            raise ValueError("targets must be a nonempty sequence of probability vectors") from None
        if not self.targets or any(len(target) != len(self.proposal) for target in self.targets):
            raise ValueError("targets must be nonempty and have the same length as proposal")
        self.delta = _unit(delta, "delta")
        if not 0 < self.delta < 1:
            raise ValueError("delta must be strictly between 0 and 1")
        try:
            self.bets = tuple(_unit(bet, "bet") for bet in bets)
        except TypeError:
            raise ValueError("bets must be a nonempty sequence") from None
        if not self.bets or any(bet == 0 for bet in self.bets) or len(set(self.bets)) != len(self.bets):
            raise ValueError("bets must be distinct fractions in (0, 1]")
        self._log_bets = tuple(math.log(bet) for bet in self.bets)
        self._log_complements = tuple(math.log1p(-bet) if bet < 1 else -math.inf for bet in self.bets)
        self._threshold = math.log(2) + math.log(len(self.targets)) - math.log(self.delta)
        self._seen = [False] * len(self.proposal)
        self._proposal_remaining = _MassTree(self.proposal)
        self._remaining = [_MassTree(target) for target in self.targets]
        self._known = [_MassTree([0.0] * len(self.proposal)) for _ in self.targets]
        self._ratios = []
        self._heaps = []
        self._min_heaps = []
        for target in self.targets:
            ratios = []
            for mass, probability in zip(target, self.proposal):
                if mass > 0 and probability == 0:
                    raise ValueError("proposal must be positive wherever any target is positive")
                ratio = mass / probability if probability else 0.0
                if not math.isfinite(ratio):
                    raise ValueError("target/proposal ratio exceeds floating-point range")
                ratios.append(ratio)
            self._ratios.append(tuple(ratios))
            heap = [(-ratio, index) for index, ratio in enumerate(ratios) if ratio > 0]
            heapq.heapify(heap)
            self._heaps.append(heap)
            min_heap = [(ratio, index) for index, ratio in enumerate(ratios) if self.proposal[index] > 0]
            heapq.heapify(min_heap)
            self._min_heaps.append(min_heap)
        self._histories: list[list[tuple[float, float, float, float, float]]] = [[] for _ in self.targets]
        self.label_count = 0

    def observe(self, index: int, loss: float) -> None:
        """Record one previously unseen, supported item without drawing it."""
        index = _integer(index, "index", 0, len(self.proposal) - 1)
        loss = _unit(loss, "loss")
        if self._seen[index]:
            raise ValueError("an item may be observed only once")
        if self.proposal[index] == 0:
            raise ValueError("observed item has zero proposal probability")
        remaining_proposal = self._proposal_remaining.total
        pending = []
        for k, heap in enumerate(self._heaps):
            while heap and self._seen[heap[0][1]]:
                heapq.heappop(heap)
            if not heap:
                pending.append(None)
                continue
            min_heap = self._min_heaps[k]
            while min_heap and self._seen[min_heap[0][1]]:
                heapq.heappop(min_heap)
            maximum_ratio = -heap[0][0]
            remaining_target = self._remaining[k].total
            constant_ratio = min_heap[0][0] == maximum_ratio
            # Constant remaining a/h gives c=sum_unseen a exactly. Recognize
            # this from prior history, never from the newly observed loss.
            scale = remaining_target if constant_ratio else remaining_proposal * maximum_ratio
            if not math.isfinite(scale) or scale <= 0:
                raise ValueError("remaining target scale is outside floating-point range")
            observation = loss if constant_ratio else (self._ratios[k][index] / maximum_ratio) * loss
            pending.append((self._known[k].total, scale, observation,
                            self._identification(k)[1], remaining_target))
        # Validation precedes mutation, so rejected observations do not consume labels.
        for k, target in enumerate(self.targets):
            if pending[k] is not None:
                self._histories[k].append(pending[k])
            self._remaining[k].set(index, 0.0)
            self._known[k].set(index, target[index] * loss)
        self._proposal_remaining.set(index, 0.0)
        self._seen[index] = True
        self.label_count += 1

    def _identification(self, target: int) -> tuple[float, float]:
        if self.label_count == 0:
            return 0.0, 1.0
        lower = min(1.0, self._known[target].total)
        remaining = self._remaining[target].total
        if remaining == 0:
            return lower, lower
        upper = math.fsum((*self._known[target].components, *self._remaining[target].components))
        return lower, min(1.0, upper)

    def _candidate(self, target: int, candidate: float) -> float:
        candidate = _unit(candidate, "candidate")
        lower, upper = self._identification(target)
        lower_tolerance = 16 * max(math.ulp(candidate), math.ulp(lower))
        upper_tolerance = 16 * max(math.ulp(candidate), math.ulp(upper))
        if candidate < lower - lower_tolerance or candidate > upper + upper_tolerance:
            raise ValueError("candidate must lie within the current identification interval")
        # Allow different summation orders to describe the same endpoint.
        return min(upper, max(lower, candidate))

    def _log_wealth(self, target: int, candidate: float, direction: str) -> float:
        logs = [0.0] * len(self.bets)
        for previous_known, scale, observation, previous_upper, remaining_mass in self._histories[target]:
            from_lower = candidate - previous_known
            from_upper = previous_upper - candidate
            lower_tolerance = 8 * (math.ulp(candidate) + math.ulp(previous_known))
            upper_tolerance = 8 * (math.ulp(candidate) + math.ulp(previous_upper))
            if from_lower < -lower_tolerance or from_upper < -upper_tolerance:
                raise ValueError("candidate mean is outside the feasible betting range")
            from_lower, from_upper = max(0.0, from_lower), max(0.0, from_upper)
            # Evaluate from the closer deterministic endpoint. The upper
            # denominator uses c-R + (ID_upper-candidate), avoiding a second
            # cancellation in 1-m. Every endpoint choice is predictable.
            if from_upper < from_lower:
                risk_numerator = math.fsum((remaining_mass, -from_upper))
                complement_numerator = math.fsum((scale, -remaining_mass, from_upper))
            else:
                risk_numerator = from_lower
                complement_numerator = math.fsum((scale, -from_lower))
            if risk_numerator < 0 or complement_numerator < 0:
                raise ValueError("candidate mean is outside the feasible betting range")
            numerator, denominator = (
                (1 - observation, complement_numerator / scale) if direction == "upper"
                else (observation, risk_numerator / scale)
            )
            if denominator == 0:
                if numerator == 0:
                    continue  # Consistent degenerate null: every bet has factor one.
                raise ValueError("positive betting numerator with zero denominator")
            log_ratio = math.log(numerator) - math.log(denominator) if numerator else -math.inf
            for j, (log_bet, log_complement) in enumerate(zip(self._log_bets, self._log_complements)):
                logs[j] += _log_add(log_complement, log_bet + log_ratio)
        maximum = max(logs)
        if maximum == -math.inf:
            return -math.inf
        return maximum + math.log(math.fsum(math.exp(value - maximum) for value in logs)) - math.log(len(logs))

    def log_wealth(self, target: int, candidate: float, direction: str) -> float:
        """Return log mixture wealth at a currently feasible candidate risk.

        ``direction`` is "upper" or "lower". Consistent endpoint 0/0 factors
        are one; contradictory positive/0 factors raise ValueError. Wealth
        from earlier steps remains available after a target is fully known.
        """
        target = _integer(target, "target", 0, len(self.targets) - 1)
        if direction not in ("upper", "lower"):
            raise ValueError("direction must be 'upper' or 'lower'")
        return self._log_wealth(target, self._candidate(target, candidate), direction)

    def _invert(self, target: int, lower: float, upper: float, direction: str) -> float | None:
        left_wealth = self._log_wealth(target, lower, direction)
        right_wealth = self._log_wealth(target, upper, direction)
        if direction == "upper":
            if left_wealth > self._threshold:
                return None
            if right_wealth <= self._threshold:
                return upper
        else:
            if right_wealth > self._threshold:
                return None
            if left_wealth <= self._threshold:
                return lower
        for _ in range(64):
            midpoint = lower + (upper - lower) / 2
            if midpoint == lower or midpoint == upper:
                break
            rejected = self._log_wealth(target, midpoint, direction) > self._threshold
            if rejected == (direction == "upper"):
                upper = midpoint
            else:
                lower = midpoint
        # Outer, rejected-side endpoints enclose the acceptance set.
        return upper if direction == "upper" else lower

    def bounds(self) -> list[dict[str, int | float | bool | None]]:
        """Return current simultaneous intervals and deterministic bounds.

        An empty acceptance set has interval_conflict=True and lower=upper=None;
        no numerical upper bound may then be used to certify a target. Once a
        target has no unseen positive mass, its deterministic singleton is
        returned even if earlier statistical intervals conflicted.
        """
        rows = []
        for k in range(len(self.targets)):
            id_lower, id_upper = self._identification(k)
            if self._remaining[k].total == 0:
                lower, upper = id_lower, id_upper
            else:
                lower = self._invert(k, id_lower, id_upper, "lower")
                upper = self._invert(k, id_lower, id_upper, "upper")
            conflict = lower is None or upper is None or lower > upper
            rows.append({
                "target_index": k,
                "lower": None if conflict else lower,
                "upper": None if conflict else upper,
                "identification_lower": id_lower,
                "identification_upper": id_upper,
                "interval_conflict": conflict,
                "label_count": self.label_count,
            })
        return rows

    def upper_certificates(self, threshold: float) -> list[dict[str, int | float | bool | None]]:
        """Apply the declared directional upper test at a fixed risk threshold.

        Certification holds if the deterministic upper bound is at most the
        threshold, or if its upper-direction wealth reaches 2*K/delta while
        the threshold is feasible. A known lower bound above the threshold
        cannot certify. This valid directional rule is intentionally
        independent of whether the two-sided interval has a conflict.

        ``log_wealth`` is None outside the current identification interval;
        with a single all-in bet it can be negative infinity inside it.
        """
        threshold = _unit(threshold, "threshold")
        rows = []
        for k in range(len(self.targets)):
            lower, upper = self._identification(k)
            wealth = self._log_wealth(k, threshold, "upper") if lower <= threshold <= upper else None
            certified = upper <= threshold or (
                lower <= threshold and wealth is not None and wealth >= self._threshold
            )
            rows.append({
                "target_index": k,
                "upper_test_certified": certified,
                "threshold": threshold,
                "identification_lower": lower,
                "identification_upper": upper,
                "log_wealth": wealth,
            })
        return rows


def weighted_order(proposal: Sequence[float], seed: int, count: int | None = None) -> list[int]:
    """Draw a seeded weighted-WoR prefix by independent exponential races.

    Log race times avoid overflow for very small positive proposal masses.
    Zero-mass items are never returned. A count of None returns all support.
    """
    probabilities = _probabilities(proposal, "proposal")
    seed = _integer(seed, "seed")
    support = sum(probability > 0 for probability in probabilities)
    count = support if count is None else _integer(count, "count", 0, support)
    generator = random.Random(seed)
    races = []
    for index, probability in enumerate(probabilities):
        if probability:
            exponential = -math.log1p(-generator.random())
            log_time = math.log(exponential) - math.log(probability) if exponential else -math.inf
            races.append((log_time, index))
    races.sort()
    return [index for _, index in races[:count]]
