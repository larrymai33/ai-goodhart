"""Exact report-reduction checks, not a test of scientific novelty."""
from fractions import Fraction as F
import unittest

from experiments.check_screening_bundling import binary_bundle, verify


class ScreeningBundlingTests(unittest.TestCase):
    def test_zero_height_is_the_primitive_report(self):
        result = binary_bundle(0)
        self.assertEqual((result['g0'], result['g1']), (F(1,4), F(3,4)))
        self.assertEqual((result['t0'], result['t1'], result['price']), (1,1,1))
        self.assertEqual((result['postprocess_0'], result['postprocess_1']), (0,1))

    def test_one_state_has_hand_computed_geometric_costs(self):
        result = binary_bundle(1)
        self.assertEqual((result['g0'], result['g1']), (F(1,8), F(27,40)))
        self.assertEqual((result['t0'], result['t1']), (F(5,3), F(11,5)))
        self.assertEqual(result['postprocess_0'], -F(3,20))
        self.assertEqual(result['reverse_postprocess_1'], F(23,22))
        self.assertEqual(result['price'], F(7,3))

    def test_every_positive_height_excludes_one_primitive_postprocessing(self):
        for height in range(1,53):
            with self.subTest(height=height):
                result = binary_bundle(height)
                self.assertGreater(result['g1']/result['g0'], 3)
                self.assertLess(result['postprocess_0'], 0)
                self.assertGreater(result['reverse_postprocess_1'], 1)
                self.assertLess(result['t0'], result['t1'])
                self.assertLess(result['t1'], result['price'])

    def test_independent_chain_recurrences_cover_fractional_scores(self):
        result = verify()
        self.assertEqual(result['gate_cases'], 901)
        self.assertEqual([row['height'] for row in result['examples']], [0,1,4,52])
        self.assertEqual(result['examples'][2]['g0'], '1/20')
        self.assertEqual(result['examples'][2]['t1'], '45517/7381')

    def test_invalid_heights_are_not_coerced(self):
        for height in [-1,True,1.0,F(1),None]:
            with self.subTest(height=height), self.assertRaises((TypeError,ValueError)):
                binary_bundle(height)


if __name__ == '__main__':
    unittest.main()
