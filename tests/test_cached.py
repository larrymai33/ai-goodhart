"""Exact sampling, stopping, and charging tests for the callback auditor."""

from dataclasses import FrozenInstanceError, dataclass
from fractions import Fraction
import itertools
import importlib
import math
import unittest
from unittest.mock import patch

try:
    cached = importlib.import_module("goodhart_audit.cached")
except ModuleNotFoundError as error:
    if error.name != "goodhart_audit.cached":
        raise
    cached = None


@dataclass(frozen=True)
class EngineDesign:
    """A small exact dependency fixture; does not assert a statistical bound."""

    prompts: int
    pool_size: int
    budgets: tuple
    tau: Fraction
    epsilon: Fraction
    delta: Fraction
    eta: Fraction
    theta: Fraction
    winner_weights: tuple
    rank_cumulative_masses: tuple
    rank_mass_denominators: tuple
    log_scale: int = 1
    log_threshold: int = 100
    zero_increment: int = 1
    one_increment: int = -1
    proposal_cap: int = 2
    mode: str = "likelihood"
    prefix_cutoff: int = 1
    expected_label_bound: Fraction = Fraction(4)
    factor_guarantee: str | None = None
    expected_proposals: Fraction = Fraction(2)
    statistical_label_bound: Fraction = Fraction(3)


def engine_design(prompts=1, pool_size=3, budgets=(1,), **options):
    tau = options.pop("tau", Fraction(1, 2))
    epsilon = options.pop("epsilon", Fraction(1, 4))
    weights, cumulative, denominators = [], [], []
    for budget in budgets:
        denominator = math.comb(pool_size, budget)
        masses = [math.comb(pool_size-r-1, budget-1)
                  if pool_size-r >= budget else 0 for r in range(pool_size)]
        denominators.append(denominator)
        weights.append(tuple(Fraction(value, denominator) for value in masses))
        cumulative.append(tuple(itertools.accumulate(masses)))
    return EngineDesign(prompts, pool_size, tuple(budgets), tau, epsilon,
                        Fraction(1, 20), Fraction(1), tau-epsilon,
                        tuple(weights), tuple(cumulative), tuple(denominators),
                        **options)


class Draws:
    def __init__(self, values):
        self.values = iter(values)
        self.bounds = []

    def __call__(self, upper):
        self.bounds.append(upper)
        return next(self.values)


class CachedEngineTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(cached, "callback auditor module is not implemented")

    def run_fixture(self, plan, losses, draws=None):
        calls = []

        def oracle(prompt, rank):
            calls.append((prompt, rank))
            return losses[prompt][rank]

        with patch.object(cached, "design", return_value=plan):
            result = cached.audit(plan.prompts, plan.pool_size, plan.budgets,
                                  plan.tau, plan.epsilon, plan.delta, oracle,
                                  eta=plan.eta, randbelow=draws or (lambda upper: 0))
        return result, calls

    def test_prefix_checks_whole_family_and_counts_each_label(self):
        plan = engine_design(2, 3, (1, 2), mode="prefix", prefix_cutoff=2)
        result, calls = self.run_fixture(plan, [[0, 0, 1], [0, 0, 1]])
        self.assertEqual(result.status, "certified")
        self.assertEqual(calls, [(0, 0), (1, 0), (0, 1), (1, 1)])
        self.assertEqual(result.distinct_labels, 4)
        self.assertEqual(result.proposals, 0)
        self.assertEqual(result.mode, "prefix")
        self.assertIsNone(result.fallback_reason)
        self.assertEqual([row.pass_reason for row in result.budget_results],
                         ["prefix", "prefix"])
        self.assertEqual(result.expected_label_bound, plan.expected_label_bound)

    def test_prefix_census_preserves_safe_boundary(self):
        plan = engine_design(1, 3, (1, 2), mode="prefix")
        result, calls = self.run_fixture(plan, [[Fraction(1, 2)] * 3])
        self.assertEqual(result.status, "certified")
        self.assertEqual(calls, [(0, 0), (0, 1), (0, 2)])
        self.assertEqual([entry.phase for entry in result.acquisitions],
                         ["prefix", "census", "census"])
        self.assertEqual([row.exact_risk for row in result.budget_results],
                         [Fraction(1, 2)] * 2)

    def test_census_only_acquires_union_positive_support(self):
        plan = engine_design(1, 4, (2, 4), mode="prefix")
        result, calls = self.run_fixture(plan, [[1, 1, 1, "never queried"]])
        self.assertEqual(result.status, "not_certified")
        self.assertEqual(calls, [(0, 0), (0, 1), (0, 2)])
        self.assertTrue(all(row.status == "unsafe" for row in result.budget_results))

    def test_exact_ticket_boundaries_and_prompt_draw(self):
        # Budget2 on m3 has rank masses(2,1,0), tickets0,1,2.
        plan = engine_design(2, 3, (2,), log_threshold=1, proposal_cap=1)
        for ticket, rank in [(0, 0), (1, 0), (2, 1)]:
            draws = Draws([ticket, 1])
            result, calls = self.run_fixture(plan, [[0]*3, [0]*3], draws)
            self.assertEqual(calls, [(1, rank)])
            self.assertEqual(draws.bounds, [3, 2])
            self.assertEqual(result.budget_results[0].pass_reason, "likelihood")
            entry = result.acquisitions[0]
            self.assertEqual((entry.budget, entry.proposal_index), (2, 1))

    def test_cached_fractional_label_receives_fresh_coin(self):
        plan = engine_design(1, 3, (1,), log_threshold=1, proposal_cap=3)
        # Same item; first coin one -> score -1; then two zeros -> score +1.
        draws = Draws([0, 0, 0, 0, 0, 1, 0, 0, 1])
        result, calls = self.run_fixture(plan, [[Fraction(1, 2), 0, 0]], draws)
        self.assertEqual(calls, [(0, 0)])
        self.assertEqual(draws.bounds, [3, 1, 2] * 3)
        self.assertEqual((result.proposals, result.distinct_labels), (3, 1))
        self.assertEqual(result.budget_results[0].log_score, 1)
        self.assertIsNone(result.fallback_reason)

    def test_later_unsafe_budget_prevents_whole_family_certificate(self):
        plan = engine_design(1, 2, (1, 2), log_threshold=1)
        # Uniform budget passes from rank1's zero; budget2 reads rank0's one.
        result, calls = self.run_fixture(plan, [[1, 0]], Draws([1, 0, 0, 0]))
        self.assertEqual(calls, [(0, 1), (0, 0)])
        self.assertEqual(result.status, "not_certified")
        self.assertEqual([row.status for row in result.budget_results],
                         ["passed", "unsafe"])
        self.assertEqual(result.budget_results[1].exact_risk, 1)

    def test_complete_cached_later_support_consumes_no_proposals(self):
        plan = engine_design(1, 2, (1, 2), log_threshold=1)
        result, calls = self.run_fixture(plan, [[0, 0]], Draws([0, 0]))
        self.assertEqual(calls, [(0, 0)])
        self.assertEqual([row.proposals for row in result.budget_results], [1, 0])
        self.assertEqual(result.budget_results[1].pass_reason, "exact_support")

    def test_exact_unsafe_completion_precedes_statistical_crossing(self):
        plan = engine_design(1, 1, (1,), tau=Fraction(1, 4),
                             epsilon=Fraction(1, 8), log_threshold=1)
        result, _ = self.run_fixture(plan, [[Fraction(1, 2)]], Draws([0, 0, 1]))
        self.assertEqual(result.budget_results[0].log_score, 1)
        self.assertEqual(result.status, "not_certified")
        self.assertEqual(result.budget_results[0].exact_risk, Fraction(1, 2))

    def test_cap_fallback_charges_missing_prefix_once(self):
        plan = engine_design(1, 4, (1, 2), prefix_cutoff=2, proposal_cap=2)
        # Both proposals hit cached rank0; fallback adds only rank1.
        result, calls = self.run_fixture(plan, [[0]*4], Draws([0, 0]*2))
        self.assertEqual(result.status, "certified")
        self.assertEqual(calls, [(0, 0), (0, 1)])
        self.assertEqual(result.fallback_reason, "proposal_cap")
        self.assertEqual(result.fallback_budget, 1)
        self.assertEqual([entry.phase for entry in result.acquisitions],
                         ["proposal", "prefix"])
        self.assertEqual(result.proposals, 2)

    def test_cap_census_completes_boundary_safe_with_repeating_rng(self):
        plan = engine_design(2, 3, (1, 2), proposal_cap=2)
        result, calls = self.run_fixture(plan, [[Fraction(1, 2)]*3]*2)
        self.assertEqual(result.status, "certified")
        self.assertEqual(len(calls), 6)
        self.assertEqual(len(set(calls)), 6)
        self.assertEqual(result.proposals, 2)
        self.assertTrue(all(row.exact_risk == Fraction(1, 2)
                            for row in result.budget_results))

    def test_census_overrides_a_previous_statistical_pass(self):
        plan = engine_design(1, 3, (1, 2), log_threshold=1, proposal_cap=1)
        # Budget1 passes at zero rank2; budget2 sees rank0=1 and caps.
        result, _ = self.run_fixture(plan, [[1, 1, 0]], Draws([2, 0, 0, 0]))
        self.assertEqual(result.status, "not_certified")
        self.assertTrue(all(row.status == "unsafe" for row in result.budget_results))
        self.assertTrue(all(row.pass_reason is None for row in result.budget_results))

    def test_invalid_losses_raise_without_returning_certificate(self):
        plan = engine_design(1, 1, (1,), mode="prefix")
        for value in (True, False, .0, "0", None, -1, 2, Fraction(1, 1000001)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_fixture(plan, [[value]])

    def test_invalid_rng_values_are_rejected_before_acquisition(self):
        plan = engine_design()
        for value in (True, False, .0, -1, 3, None):
            calls = []
            with self.subTest(value=value), patch.object(cached, "design", return_value=plan):
                with self.assertRaises(ValueError):
                    cached.audit(1, 3, (1,), plan.tau, plan.epsilon, plan.delta,
                                 lambda p, r: calls.append((p, r)) or 0,
                                 randbelow=lambda n: value)
                self.assertEqual(calls, [])

    def test_invalid_coin_draw_is_rejected_after_one_charged_oracle_call(self):
        plan = engine_design()
        calls = []
        with patch.object(cached, "design", return_value=plan), self.assertRaises(ValueError):
            cached.audit(1, 3, (1,), plan.tau, plan.epsilon, plan.delta,
                         lambda p, r: calls.append((p, r)) or Fraction(1, 2),
                         randbelow=Draws([0, 0, 2]))
        self.assertEqual(calls, [(0, 0)])

    def test_callback_callability_rejected_before_oracle_calls(self):
        plan = engine_design()
        calls = []
        with patch.object(cached, "design", return_value=plan):
            with self.assertRaises(ValueError):
                cached.audit(1, 3, (1,), plan.tau, plan.epsilon, plan.delta, None)
            with self.assertRaises(ValueError):
                cached.audit(1, 3, (1,), plan.tau, plan.epsilon, plan.delta,
                             lambda p, r: calls.append((p, r)) or 0, randbelow=4)
        self.assertEqual(calls, [])

    def test_design_rejection_precedes_oracle_or_randomness(self):
        calls = []
        with patch.object(cached, "design", side_effect=ValueError("unsupported")):
            with self.assertRaisesRegex(ValueError, "unsupported"):
                cached.audit(1, 3, (1,), Fraction(1, 2), Fraction(1, 4),
                             Fraction(1, 20), lambda p, r: calls.append("oracle"),
                             randbelow=lambda n: calls.append("rng"))
        self.assertEqual(calls, [])

    def test_result_and_nested_trace_are_immutable(self):
        plan = engine_design(1, 1, (1,), mode="prefix")
        result, _ = self.run_fixture(plan, [[0]])
        for obj, name, value in ((result, "status", "changed"),
                                 (result.acquisitions[0], "loss", Fraction(1)),
                                 (result.budget_results[0], "status", "changed")):
            with self.assertRaises(FrozenInstanceError):
                setattr(obj, name, value)
        self.assertIsInstance(result.acquisitions, tuple)
        self.assertIsInstance(result.budget_results, tuple)

    def test_real_design_prefix_end_to_end(self):
        calls = []
        result = cached.audit(2, 4, (4, 1, 2), Fraction(1, 10), Fraction(1, 160),
                              Fraction(1, 20),
                              lambda p, r: calls.append((p, r)) or Fraction(1, 10))
        self.assertEqual(result.mode, "prefix")
        self.assertEqual(result.status, "certified")
        self.assertEqual(result.distinct_labels, 8)
        self.assertEqual(tuple(row.budget for row in result.budget_results), (1, 2, 4))
        self.assertEqual(len(calls), 8)

    def test_real_likelihood_design_reuses_labels_and_stops_statistically(self):
        calls = []
        result = cached.audit(8, 1, (1,), Fraction(3, 4), Fraction(1, 2),
                              Fraction(1, 4), lambda p, r: calls.append((p, r)) or 0,
                              eta=Fraction(1, 10), randbelow=lambda n: 0)
        self.assertEqual(result.mode, "likelihood")
        self.assertEqual(result.status, "certified")
        self.assertEqual(result.budget_results[0].pass_reason, "likelihood")
        self.assertEqual(result.proposals, 2)
        self.assertEqual(result.distinct_labels, 1)
        self.assertEqual(calls, [(0, 0)])

    def test_fractional_coin_enumeration_uses_exact_numerator(self):
        plan = engine_design(1, 2, (1,), log_threshold=1, proposal_cap=1)
        scores = []
        for coin_ticket in range(3):
            result, _ = self.run_fixture(plan, [[Fraction(2, 3), 0]],
                                         Draws([0, 0, coin_ticket]))
            scores.append(result.budget_results[0].log_score)
        self.assertEqual(scores, [-1, -1, 1])

    def test_real_prefix_matches_exact_family_on_small_fractional_tables(self):
        # Independent three-rank formulas, including nonuniform unsafe cases.
        for losses in itertools.product((Fraction(0), Fraction(1, 2), Fraction(1)),
                                        repeat=3):
            result = cached.audit(1, 3, (1, 2, 3), Fraction(1, 2),
                                  Fraction(1, 4), Fraction(1, 20),
                                  lambda p, r: losses[r])
            risks = (sum(losses)/3, (2*losses[0]+losses[1])/3, losses[0])
            expected = "certified" if max(risks) <= Fraction(1, 2) else "not_certified"
            with self.subTest(losses=losses):
                self.assertEqual(result.mode, "prefix")
                self.assertEqual(result.status, expected)
                self.assertEqual(tuple(row.exact_risk for row in result.budget_results), risks)

    def test_denominator_limit_is_inclusive_and_oracle_errors_propagate(self):
        plan = engine_design(1, 1, (1,), mode="prefix")
        result, _ = self.run_fixture(plan, [[Fraction(1, 1000000)]])
        self.assertEqual(result.status, "certified")
        self.assertEqual(result.acquisitions[0].loss, Fraction(1, 1000000))
        with patch.object(cached, "design", return_value=plan):
            def broken_oracle(prompt, rank):
                raise RuntimeError("label service failed")
            with self.assertRaisesRegex(RuntimeError, "label service failed"):
                cached.audit(1, 1, (1,), plan.tau, plan.epsilon, plan.delta, broken_oracle)


if __name__ == "__main__":
    unittest.main()
