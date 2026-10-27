"""Bounded callback implementation of the cached likelihood audit.

Only one certificate for the originally declared budget family is issued.
Statistical validity assumes fixed correct losses and independent uniform
random draws. The executable domain is exact int/Fraction losses with the
documented denominator limit; it does not implement an all-real oracle.
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
import secrets

from .cached_math import CachedDesign, MAX_LOSS_DENOMINATOR, design


@dataclass(frozen=True)
class Acquisition:
    """One first acquisition; callback indices are zero based."""

    prompt_index: int
    rank_index: int
    loss: Fraction
    phase: str
    budget: int | None
    proposal_index: int | None


@dataclass(frozen=True)
class BudgetResult:
    """Final state of one original budget; score uses design.log_scale."""

    budget: int
    status: str
    pass_reason: str | None
    proposals: int
    log_score: int
    exact_risk: Fraction | None


@dataclass(frozen=True)
class AuditResult:
    """Immutable charged trace and whole-family decision.

    ``expected_label_bound`` applies uniformly only when every original risk
    is at most tau-epsilon. It is not a maximum realized acquisition count.
    An unsafe table can pass a statistical test with probability <=delta.
    Callback or RNG failures raise an exception instead of returning a result.
    """

    status: str
    design: CachedDesign
    acquisitions: tuple[Acquisition, ...]
    budget_results: tuple[BudgetResult, ...]
    fallback_reason: str | None
    fallback_budget: int | None

    @property
    def proposals(self) -> int:
        return sum(row.proposals for row in self.budget_results)

    @property
    def distinct_labels(self) -> int:
        return len(self.acquisitions)

    @property
    def mode(self) -> str:
        return self.design.mode

    @property
    def expected_label_bound(self) -> Fraction:
        return self.design.expected_label_bound


def audit(
    prompts: int,
    pool_size: int,
    budgets: tuple[int, ...] | list[int],
    tau: int | Fraction,
    epsilon: int | Fraction,
    delta: int | Fraction,
    oracle: Callable[[int, int], int | Fraction],
    eta: int | Fraction = Fraction(1),
    randbelow: Callable[[int], int] | None = None,
) -> AuditResult:
    """Acquire fixed exact labels and decide the entire declared family.

    ``budgets`` is a nonempty tuple or list of distinct integer budgets;
    the design normalizes its order. ``oracle(prompt_index, rank_index)``
    is called once per acquired item.
    Every proposal draws a new rank ticket, prompt index, and Bernoulli coin;
    coins with parameter zero or one need no RNG call. Cache hits still use
    fresh coins. Injected ``randbelow(upper)`` must return strict integers in
    ``range(upper)``; reproducible deterministic draws do not themselves
    provide the independent-uniform assumption of the statistical theorem.

    Unsupported designs are rejected before oracle calls. All safe tables
    in the supported rational-label domain finish through finite proposal
    caps and fully charged deterministic fallback, including the boundary.
    Proposal caps do not bound RNG internal rejection bits or oracle latency.
    """
    plan = design(prompts, pool_size, budgets, tau, epsilon, delta, eta)
    generator = secrets.randbelow if randbelow is None else randbelow
    if not callable(oracle):
        raise ValueError("oracle must be callable")
    if not callable(generator):
        raise ValueError("randbelow must be callable")

    count = len(plan.budgets)
    cache: dict[tuple[int, int], Fraction] = {}
    trace: list[Acquisition] = []
    known = [Fraction(0) for _ in plan.budgets]
    missing = [Fraction(1) for _ in plan.budgets]
    support_remaining = [plan.prompts * (plan.pool_size-n+1) for n in plan.budgets]
    proposals = [0] * count
    scores = [0] * count
    statuses = ["not_reached"] * count
    reasons: list[str | None] = [None] * count
    fallback_reason = None
    fallback_budget = None

    def draw(upper: int) -> int:
        value = generator(upper)
        if type(value) is not int or not 0 <= value < upper:
            raise ValueError("randbelow must return an integer in the requested range")
        return value

    def acquire(prompt: int, rank: int, phase: str,
                budget: int | None = None, proposal_index: int | None = None) -> Fraction:
        identity = (prompt, rank)
        if identity in cache:
            return cache[identity]
        raw = oracle(prompt, rank)
        if isinstance(raw, bool) or not isinstance(raw, (int, Fraction)):
            raise ValueError("oracle loss must be an int or Fraction in [0, 1]")
        loss = Fraction(raw)
        if not 0 <= loss <= 1 or loss.denominator > MAX_LOSS_DENOMINATOR:
            raise ValueError("oracle loss is outside the supported range or denominator limit")
        cache[identity] = loss
        trace.append(Acquisition(prompt, rank, loss, phase, budget, proposal_index))
        # Only first acquisitions update exact aggregates. Cache hits are O(1).
        for index, weights in enumerate(plan.winner_weights):
            weight = weights[rank]
            if weight:
                mass = weight / plan.prompts
                known[index] += mass * loss
                missing[index] -= mass
                support_remaining[index] -= 1
        return loss

    def finish(status: str) -> AuditResult:
        rows = []
        for index, budget in enumerate(plan.budgets):
            exact = known[index] if support_remaining[index] == 0 else None
            # A prior statistical pass cannot override now-known unsafety.
            if known[index] > plan.tau:
                statuses[index], reasons[index] = "unsafe", None
                status = "not_certified"
            rows.append(BudgetResult(budget, statuses[index], reasons[index],
                                     proposals[index], scores[index], exact))
        return AuditResult(status, plan, tuple(trace), tuple(rows),
                           fallback_reason, fallback_budget)

    def complete_deterministically() -> AuditResult:
        for rank in range(plan.prefix_cutoff):
            for prompt in range(plan.prompts):
                acquire(prompt, rank, "prefix")
        if all(value + unseen <= plan.tau for value, unseen in zip(known, missing)):
            for index in range(count):
                if statuses[index] != "passed":
                    statuses[index], reasons[index] = "passed", "prefix"
            return finish("certified")
        union_cutoff = plan.pool_size - min(plan.budgets) + 1
        for rank in range(union_cutoff):
            for prompt in range(plan.prompts):
                acquire(prompt, rank, "census")
        for index, risk in enumerate(known):
            safe = risk <= plan.tau
            statuses[index] = "passed" if safe else "unsafe"
            reasons[index] = "census" if safe else None
        return finish("certified" if all(status == "passed" for status in statuses)
                      else "not_certified")

    if plan.mode == "prefix":
        return complete_deterministically()

    for index, budget in enumerate(plan.budgets):
        if support_remaining[index] == 0:
            if known[index] > plan.tau:
                statuses[index] = "unsafe"
                return finish("not_certified")
            statuses[index], reasons[index] = "passed", "exact_support"
            continue
        while proposals[index] < plan.proposal_cap:
            ticket = draw(plan.rank_mass_denominators[index])
            rank = bisect_right(plan.rank_cumulative_masses[index], ticket)
            prompt = draw(plan.prompts)
            proposal_index = proposals[index] + 1
            loss = acquire(prompt, rank, "proposal", budget, proposal_index)
            coin = loss == 1 or (loss != 0 and draw(loss.denominator) < loss.numerator)
            proposals[index] = proposal_index
            scores[index] += plan.one_increment if coin else plan.zero_increment
            # Exact knowledge wins a simultaneous statistical crossing.
            if support_remaining[index] == 0:
                if known[index] > plan.tau:
                    statuses[index] = "unsafe"
                    return finish("not_certified")
                statuses[index], reasons[index] = "passed", "exact_support"
                break
            if scores[index] >= plan.log_threshold:
                statuses[index], reasons[index] = "passed", "likelihood"
                break
        if statuses[index] != "passed":
            fallback_reason, fallback_budget = "proposal_cap", budget
            return complete_deterministically()
    return finish("certified")
