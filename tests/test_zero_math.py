"""Independent exact checks for the conservative zero-only sampling design."""

from decimal import Decimal, localcontext
from fractions import Fraction as F
import itertools
import json
import unittest
from unittest.mock import patch

from goodhart_audit import zero_math


class ZeroMathTests(unittest.TestCase):
    def setUp(self):
        self.module = zero_math

    @staticmethod
    def enumerated_weights(m, n):
        counts = [0]*m
        subsets = list(itertools.combinations(range(m), n))
        for subset in subsets:
            counts[min(subset)] += 1
        return tuple(F(count, len(subsets)) for count in counts)

    def test_rank_envelope_matches_independently_enumerated_winners(self):
        record, probabilities = self.module.design_probabilities(
            6, [6, 1, 4], 2, F(1, 8), F(1, 4))
        rows = [self.enumerated_weights(6, n) for n in (1, 4, 6)]
        expected = tuple(max(row[r] for row in rows)/2 for r in range(6))
        self.assertEqual(tuple(map(F, record['rank_envelope_masses'])), expected)
        self.assertEqual(record['budgets'], [1, 4, 6])
        self.assertEqual(record['cost_factor'], 160)
        self.assertEqual(tuple(map(F, record['rank_inclusion_probabilities'])), probabilities)
        self.assertEqual(F(record['expected_zero_cost']), 2*sum(probabilities))
        self.assertEqual(json.loads(json.dumps(record)), record)

    def test_sparse_grids_use_only_declared_targets_and_extended_cost_factor(self):
        for m, budgets in [(7, [7, 1, 3]), (64, [63, 1])]:
            with self.subTest(m=m, budgets=budgets):
                record, probabilities = self.module.design_probabilities(
                    m, budgets, 2, F(1, 8), F(1, 4))
                rows = [self.enumerated_weights(m, n) for n in budgets]
                expected = tuple(max(row[r] for row in rows)/2 for r in range(m))
                self.assertEqual(tuple(map(F, record['rank_envelope_masses'])), expected)
                self.assertEqual(record['budgets'], sorted(budgets))
                self.assertEqual(record['cost_factor'], 320)
                self.assertEqual(F(record['expected_zero_cost']), 2*sum(probabilities))

    def test_old_grid_condition_retains_the_sharper_factor(self):
        for m, budgets in [(1, [1]), (3, [1, 3]), (7, [7, 4, 1]),
                           (31, [1, 2, 4, 8, 16, 31])]:
            with self.subTest(m=m, budgets=budgets):
                record, _ = self.module.design_probabilities(m, budgets, 2, F(1, 8), F(1, 4))
                self.assertEqual(record['cost_factor'], 160)

    def test_log_enclosures_and_probability_sandwich_against_decimal_oracle(self):
        cases = [(1, [1], 1, F(1, 8), F(1, 4)),
                 (8, [1, 2, 4, 8], 2, F(1, 8), F(1, 4)),
                 (64, [1, 2, 4, 8, 16, 32, 64], 32, F(1, 10), F(1, 20)),
                 (7, [1, 3, 7], 8, F(1, 8), F(1, 4)),
                 (64, [1, 63], 2, F(1, 10), F(1, 20)),
                 (4, [1, 4], 2, F(1, 10**70), F(1, 10**70)),
                 (4, [1, 4], 2, F(1, 8), F(1, 4)-F(1, 10**70))]
        with localcontext() as context:
            context.prec = 100
            def decimal(value):
                return Decimal(value.numerator)/Decimal(value.denominator)
            for m, budgets, prompts, tau, delta in cases:
                with self.subTest(m=m, prompts=prompts, tau=tau, delta=delta):
                    record, probabilities = self.module.design_probabilities(m, budgets, prompts, tau, delta)
                    lo, hi = (F(record['log_interval'][key]) for key in ('lower', 'upper'))
                    true_log = -decimal(delta).ln()
                    self.assertLessEqual(decimal(lo), true_log)
                    self.assertGreaterEqual(decimal(hi), true_log)
                    scale = 1 << record['log_interval']['dyadic_scale_exponent']
                    self.assertEqual((lo*scale).denominator, 1)
                    self.assertEqual((hi*scale).denominator, 1)
                    for mass, probability in zip(map(F, record['rank_envelope_masses']), probabilities):
                        self.assertLessEqual(probability, min(F(1), lo*mass/tau))
                        exponent = true_log*decimal(mass/tau)
                        ideal = 1-(-exponent).exp()
                        self.assertGreaterEqual(decimal(probability), ideal)
                        self.assertGreater(probability, 0)
                        self.assertLessEqual(probability, 1)

    def test_every_unsafe_binary_table_has_small_miss_probability_under_subset_law(self):
        # Eight items: this exposes nontrivial randomized inclusions without
        # relying on a simulation, floating probabilities, or the design's rows.
        m, prompts, tau, delta = 4, 2, F(1, 8), F(1, 4)
        record, rank_probabilities = self.module.design_probabilities(m, [1, 4], prompts, tau, delta)
        probabilities = rank_probabilities*prompts
        targets = [tuple(w/prompts for w in self.enumerated_weights(m, n))*prompts for n in (1, 4)]
        law = {}
        for queried in range(1 << (m*prompts)):
            probability = F(1)
            for i, inclusion in enumerate(probabilities):
                probability *= inclusion if queried >> i & 1 else 1-inclusion
            if probability:
                law[queried] = probability
        self.assertGreater(len(law), 1)
        self.assertEqual(sum(law.values()), 1)
        expected_cost = sum((F(mask.bit_count())*probability for mask, probability in law.items()), F(0))
        self.assertEqual(expected_cost, F(record['expected_zero_cost']))
        for failures in range(1 << (m*prompts)):
            if any(sum((mass for i, mass in enumerate(row) if failures >> i & 1), F(0)) > tau
                   for row in targets):
                missed = sum((probability for queried, probability in law.items() if not queried & failures), F(0))
                self.assertLessEqual(missed, delta, failures)

    def test_single_item_is_an_exact_census(self):
        record, probabilities = self.module.design_probabilities(1, [1], 1, F(1, 8), F(1, 4))
        self.assertEqual(probabilities, (F(1),))
        self.assertEqual(F(record['expected_zero_cost']), 1)
        self.assertEqual(record['random_draw_width_sum'], 0)

    def test_rejection_sampler_retries_without_modulo_bias(self):
        draws, widths = iter([7, 5, 4]), []
        def bits(width):
            widths.append(width)
            return next(draws)
        self.assertEqual(self.module.exact_randbelow(5, bits), 4)
        self.assertEqual(widths, [3, 3, 3])
        for n in range(2, 10):
            width = (n-1).bit_length()
            for accepted in range(n):
                def accepted_bits(requested, value=accepted):
                    self.assertEqual(requested, width)
                    return value
                self.assertEqual(self.module.exact_randbelow(n, accepted_bits), accepted)

    def test_singleton_sampler_consumes_no_entropy(self):
        def unexpected(_):
            self.fail('a deterministic draw must not consume random bits')
        self.assertEqual(self.module.exact_randbelow(1, unexpected), 0)

    def test_invalid_sampler_bounds_and_bit_source_outputs_fail(self):
        for n in (0, -1, True, 1.5):
            with self.subTest(n=n), self.assertRaises(ValueError):
                self.module.exact_randbelow(n, lambda width: 0)
        for value in (-1, 8, True, 1.5, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.module.exact_randbelow(5, lambda width: value)
        with self.assertRaises(ValueError):
            self.module.exact_randbelow(3, None)

    def test_theorem_restrictions_and_exact_parameter_types_are_enforced(self):
        args = dict(m=8, budgets=[1, 4, 8], P=2, tau=F(1, 8), delta=F(1, 4))
        variants = [('m', 0), ('m', True), ('P', 0), ('P', 2.0),
                    ('budgets', []), ('budgets', [2]), ('budgets', [2, 4, 8]),
                    ('budgets', [1, 4, 9]),
                    ('budgets', [1, 4, 4]), ('budgets', [True, 4]), ('budgets', None),
                    ('tau', F(0)), ('tau', F(1, 2)), ('tau', 0.1), ('tau', True),
                    ('delta', F(0)), ('delta', F(1, 2)), ('delta', 0.05)]
        for key, value in variants:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.module.design_probabilities(**{**args, key: value})

    def test_resource_limits_reject_before_unbounded_expansion(self):
        cases = [(1025, [1], 1, F(1, 8), F(1, 4)),
                 (1, [1], 100001, F(1, 8), F(1, 4)),
                 (501, list(range(1, 502)), 1, F(1, 8), F(1, 4)),
                 (1, [1], 1, F(1, 1 << 256), F(1, 4)),
                 (1, [1], 1, F(1, 8), F(1, 1 << 256))]
        for args in cases:
            with self.subTest(m=args[0], P=args[2]), self.assertRaises(ValueError):
                self.module.design_probabilities(*args)

    def test_rational_and_tape_caps_fail_instead_of_rounding_probabilities(self):
        with patch.object(self.module, 'MAX_SERIALIZED_BITS', 4), self.assertRaises(ValueError):
            self.module.design_probabilities(4, [1, 4], 2, F(1, 8), F(1, 4))
        with patch.object(self.module, 'MAX_DRAW_WIDTH_SUM', 1), self.assertRaises(ValueError):
            self.module.design_probabilities(4, [1, 4], 2, F(1, 8), F(1, 4))


if __name__ == '__main__':
    unittest.main()
