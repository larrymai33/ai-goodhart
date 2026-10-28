"""Rational enclosures checked against a separate high precision oracle."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import unittest

from goodhart_audit.screening_math import certificate, kl_bounds, log_bounds


class ScreeningMathTests(unittest.TestCase):
    def test_log_bounds_enclose_decimal_across_dyadic_reductions(self):
        with localcontext() as ctx:
            # Near-one inputs have interval widths below 1e-300; the reference
            # needs more precision than the enclosure it is checking.
            ctx.prec = 500
            for x in [F(1), F(2), F(1, 2), F(1, 10000000), F(20), F(959, 950), F(2**100), F(1, 2**100)]:
                with self.subTest(x=x):
                    lo, hi = log_bounds(x)
                    value = (Decimal(x.numerator) / Decimal(x.denominator)).ln()
                    self.assertLessEqual(Decimal(lo.numerator)/Decimal(lo.denominator), value)
                    self.assertGreaterEqual(Decimal(hi.numerator)/Decimal(hi.denominator), value)
                    self.assertLess(hi-lo, F(1, 10**55))

    def test_kl_endpoints_and_equal_parameters(self):
        self.assertEqual(kl_bounds(F(1, 3), F(1, 3)), (F(0), F(0)))
        self.assertEqual(kl_bounds(F(0), F(1, 2)), log_bounds(F(2)))
        self.assertEqual(kl_bounds(F(1), F(1, 2)), log_bounds(F(2)))
        with localcontext() as ctx:
            ctx.prec = 100
            p, q = F(59, 32768), F(65, 32768)
            a, b = Decimal(p.numerator)/Decimal(p.denominator), Decimal(q.numerator)/Decimal(q.denominator)
            value = a*(a/b).ln() + (1-a)*((1-a)/(1-b)).ln()
            lo, hi = kl_bounds(p, q)
            self.assertLess(Decimal(lo.numerator)/Decimal(lo.denominator), value)
            self.assertGreater(Decimal(hi.numerator)/Decimal(hi.denominator), value)

    def test_invalid_math_inputs_do_not_coerce_floats_or_bools(self):
        for value in [0, -1, 1.0, True]:
            with self.subTest(log=value), self.assertRaises((TypeError, ValueError)):
                log_bounds(value)
        for p, q in [(F(-1), F(1, 2)), (F(1, 2), 1), (0.0, F(1, 2)), (F(0), False)]:
            with self.subTest(p=p, q=q), self.assertRaises((TypeError, ValueError)):
                kl_bounds(p, q)

    def test_wide_certificate_has_outward_rounded_finite_gap(self):
        row = certificate('wide', 13000, 64, F(1,64), F(9,640), F(1,20), F(1,200), 4, F(0), F(5,256), None)
        self.assertEqual([row[k] for k in ['upper_integer', 'one_report_lower_integer', 'exact_only_lower_integer', 'cheap_only_lower_integer']], [2973, 3198, 9410, 18653])
        self.assertEqual(row['guaranteed_reduction_fraction_at_least'], '75/1066')
        self.assertFalse(row['small_relative_margin_regime'])

    def test_narrow_certificate_retains_original_margin(self):
        row = certificate('narrow', 70000000, 8192, F(1,512), F(1,8192), F(1,20), F(1,10000000), 52, F(59,32768), F(65,32768), F(48))
        self.assertEqual([row[k] for k in ['upper_integer', 'one_report_lower_integer', 'exact_only_lower_integer', 'cheap_only_lower_integer']], [98855201, 128874779, 2747662969, 302326524])
        self.assertTrue(row['small_relative_margin_regime'])

    def test_invalid_tail_condition_cannot_produce_certificate(self):
        with self.assertRaises(ValueError):
            certificate('too small', 10, 64, F(1,64), F(9,640), F(1,20), F(1,200), 4, F(0), F(5,256), None)


if __name__ == '__main__':
    unittest.main()
