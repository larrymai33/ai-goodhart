"""Possible scripted paths establish conformance, not statistical calibration."""
from fractions import Fraction as F
import unittest

from goodhart_audit.screening import audit, correction_probability


class ScreeningTests(unittest.TestCase):
    def run_audit(self, rating=lambda i: 0, exact=lambda i: 0, **changes):
        options = dict(population=2, exact_cost=64, tau=F(1, 64),
                       epsilon=F(9, 640), delta=F(1, 20), gate_height=0,
                       randbelow=lambda n: 0)
        options.update(changes)
        return audit(rating, exact, **options)

    def test_all_zero_reports_cross_at_first_exact_integer_threshold(self):
        # Zero multiplier = (1-1/960)/(1-1/96) = 959/950.
        self.assertLess(F(959, 950)**317, 20)
        self.assertGreaterEqual(F(959, 950)**318, 20)
        result = self.run_audit()
        self.assertEqual((result.status, result.reason), ('certified', 'likelihood'))
        self.assertEqual((result.ratings, result.adjudications, result.payment), (318, 0, 318))
        self.assertEqual((result.proposals, result.corrected_zeros, result.corrected_ones), (318, 318, 0))

    def test_cache_avoids_both_rerating_and_rebuying(self):
        calls = []
        def exact(i):
            calls.append(i)
            return 0
        result = self.run_audit(rating=lambda i: 1, exact=exact)
        self.assertEqual(calls, [0])
        self.assertEqual((result.ratings, result.adjudications, result.payment), (1, 1, 65))
        self.assertEqual(result.corrected_zeros, 318)

    def test_census_boundary_and_unsafe_decisions_precede_coin_emission(self):
        for value, status in [(F(1, 64), 'certified'), (1, 'rejected')]:
            with self.subTest(value=value):
                result = self.run_audit(rating=lambda i: 1, exact=lambda i: value, population=1)
                self.assertEqual((result.status, result.reason), (status, 'census'))
                self.assertEqual(result.payment, 65)
                self.assertEqual(result.corrected_ones + result.corrected_zeros, 0)

    def test_all_up_walk_charges_initial_and_every_step(self):
        result = self.run_audit(rating=lambda i: 1, population=1, gate_height=4)
        self.assertEqual((result.ratings, result.adjudications, result.payment), (5, 1, 69))

    def test_lower_exit_and_holding_steps_are_charged(self):
        for hold in [False, True]:
            with self.subTest(hold=hold):
                ratings = iter([1, 0, 0] if hold else [1, 0])
                coins = iter([0, 3, 0] if hold else [0, 0])
                result = self.run_audit(rating=lambda i: next(ratings, 0),
                                        randbelow=lambda n: next(coins, 0), gate_height=2)
                self.assertEqual(result.corrected_zeros, 318)
                self.assertEqual(result.ratings, 319 + int(hold))
                self.assertEqual(result.adjudications, 0)

    def test_purchased_nonzero_coin_uses_correction_then_census(self):
        draws = iter([(2, 0), (9, 0), (2, 1)])
        def rng(n):
            bound, value = next(draws)
            self.assertEqual(n, bound)
            return value
        result = self.run_audit(rating=lambda i: 1, exact=lambda i: 1-i, randbelow=rng)
        self.assertEqual((result.status, result.reason), ('rejected', 'census'))
        self.assertEqual((result.corrected_ones, result.corrected_zeros), (1, 0))
        self.assertEqual((result.ratings, result.adjudications, result.payment), (2, 2, 130))

    def test_nonzero_cached_coin_uses_two_thirds_score(self):
        draws = iter([(2, 0), (9, 8), (2, 0), (3, 1), (2, 1)])
        def rng(n):
            bound, value = next(draws)
            self.assertEqual(n, bound)
            return value
        result = self.run_audit(rating=lambda i: 1, exact=lambda i: 1-i, randbelow=rng)
        self.assertEqual((result.corrected_ones, result.corrected_zeros), (1, 1))
        self.assertEqual(result.payment, 130)

    def test_correction_probabilities_include_both_endpoints(self):
        self.assertEqual(correction_probability(F(0), 4), 0)
        self.assertEqual(correction_probability(F(1), 0), F(8, 9))
        self.assertEqual(correction_probability(F(1), 1), F(80, 81))
        self.assertEqual(correction_probability(F(1, 2), 1), F(8, 9))

    def test_rating_cap_never_certifies_without_completed_evidence(self):
        for cap, height in [(0, 0), (3, 4)]:
            with self.subTest(cap=cap):
                result = self.run_audit(rating=lambda i: 1, max_ratings=cap, gate_height=height)
                self.assertEqual((result.status, result.reason), ('inconclusive', 'rating_limit'))
                self.assertEqual(result.payment, cap)
                self.assertEqual(result.corrected_ones + result.corrected_zeros, 0)

    def test_bad_parameters_fail_before_callbacks(self):
        def untouched(*args):
            self.fail('callback before validation')
        bad = dict(population=[0, True, 1.0], exact_cost=[0, False, 64.0],
                   tau=[0, F(1, 4), .01, True], epsilon=[0, F(1, 64), .01],
                   delta=[0, F(1, 2), .05], gate_height=[-1, True, 1.0],
                   max_ratings=[-1, True, 1.0])
        for key, values in bad.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises((TypeError, ValueError)):
                    self.run_audit(rating=untouched, exact=untouched, **{key: value})

    def test_bad_callback_values_raise(self):
        for value in [True, 1.0, F(1), -1, 2, None]:
            with self.subTest(rating=value), self.assertRaises((TypeError, ValueError)):
                self.run_audit(rating=lambda i: value)
        for value in [True, 0.0, F(1, 3), -1, 2, None]:
            with self.subTest(exact=value), self.assertRaises((TypeError, ValueError)):
                self.run_audit(rating=lambda i: 1, exact=lambda i: value)
        for value in [True, 0.0, -1, 2, None]:
            with self.subTest(rng=value), self.assertRaises((TypeError, ValueError)):
                self.run_audit(randbelow=lambda n: value)

    def test_callback_exceptions_propagate_without_certificate(self):
        def broken(i):
            raise RuntimeError('oracle failed')
        with self.assertRaisesRegex(RuntimeError, 'oracle failed'):
            self.run_audit(rating=broken)
        with self.assertRaisesRegex(RuntimeError, 'oracle failed'):
            self.run_audit(rating=lambda i: 1, exact=broken)


if __name__ == '__main__':
    unittest.main()
