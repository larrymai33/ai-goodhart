"""Exact arithmetic checks of the finite/continuous envelope bridge.

These finite checks are regression evidence for the algebra in
docs/sharp-envelope.md, not substitutes for its universal proof.
"""

from fractions import Fraction
from math import comb
import unittest

from goodhart_audit.core import full_envelope


def _choose(a, b):
    return 0 if b < 0 or b > a else comb(a, b)


def _rank_law(m, n):
    denominator = comb(m, n)
    return [Fraction(_choose(m - r, n - 1), denominator)
            for r in range(1, m + 1)]


class SharpEnvelopeTests(unittest.TestCase):
    def test_exact_rank_laws_verify_bridge_for_every_cap_through_sixty(self):
        for m in range(1, 61):
            previous = _rank_law(m, 1)
            maxima = previous.copy()
            continuous = Fraction(1)
            tv_envelope = Fraction(1)
            self.assertEqual(sum(maxima), 1)

            for n in range(2, m + 1):
                current = _rank_law(m, n)
                direct_tv = sum(abs(a - b) for a, b in
                                zip(current, previous)) / 2
                k = (m + 1) // n
                crossing_tv = (
                    Fraction(_choose(m - k, n - 1), comb(m, n - 1))
                    - Fraction(_choose(m - k, n), comb(m, n))
                )
                ell = Fraction((n - 1) ** (n - 1), n ** n)
                maxima = [max(a, b) for a, b in zip(maxima, current)]
                direct_envelope = sum(maxima)
                continuous += ell
                tv_envelope += direct_tv

                with self.subTest(m=m, n=n):
                    self.assertEqual(direct_tv, crossing_tv)
                    self.assertEqual(direct_envelope, tv_envelope)
                    self.assertGreaterEqual(direct_tv, ell)
                    self.assertLessEqual((m - n + 1) * direct_tv, m * ell)
                    self.assertLessEqual(n * direct_tv, 1)
                    self.assertLessEqual(
                        direct_tv - ell, (1 - ell) / (m + 1))
                    self.assertGreaterEqual(direct_envelope, continuous)
                    self.assertLessEqual(
                        direct_envelope - continuous,
                        (n - continuous) / (m + 1),
                    )
                previous = current

    def test_bound_includes_one_budget_and_is_attained_at_two(self):
        for m in range(1, 61):
            self.assertEqual(sum(_rank_law(m, 1)), 1)
        continuous = Fraction(5, 4)
        exact = sum(max(a, b) for a, b in
                    zip(_rank_law(2, 1), _rank_law(2, 2)))
        self.assertEqual(exact, Fraction(3, 2))
        self.assertEqual(exact - continuous, (2 - continuous) / 3)

    def test_frozen_numerical_envelope_matches_independent_exact_laws(self):
        for m in (1, 2, 7, 20, 60):
            maxima = [Fraction(0)] * m
            for n in range(1, m + 1):
                maxima = [max(a, b) for a, b in
                          zip(maxima, _rank_law(m, n))]
                _, actual = full_envelope(m, n)
                with self.subTest(m=m, n=n):
                    self.assertAlmostEqual(actual, float(sum(maxima)), places=13)


if __name__ == "__main__":
    unittest.main()
