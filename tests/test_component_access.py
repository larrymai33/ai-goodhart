"""Regression checks for the component-access countermodel."""
from fractions import Fraction as F
import unittest

from experiments.check_component_access import raw_component_upper, risks, verify


class ComponentAccessTests(unittest.TestCase):
    def test_raw_access_bounds_for_both_published_parameter_sets(self):
        self.assertEqual(raw_component_upper(13000,64,F(1,64),F(9,640),F(1,20)),285)
        self.assertEqual(raw_component_upper(70000000,8192,F(1,512),F(1,8192),F(1,20)),767339)
        self.assertEqual(raw_component_upper(1,1,F(1,64),F(9,640),F(1,20)),1)

    def test_same_component_mean_can_have_different_program_risk(self):
        self.assertEqual(risks([16]+[0]*15,16),(F(1,16),F(1,16)))
        self.assertEqual(risks([1]*16,16),(F(1,16),F(1)))

    def test_exact_small_profiles_and_symbolic_counterexamples(self):
        result=verify()
        self.assertEqual(result['small_profiles_checked'],16)
        self.assertEqual(result['examples'][0]['program_failure_at_margin'],'1/10')
        self.assertEqual(result['examples'][1]['program_failure_at_margin'],'1')

    def test_invalid_costs_parameters_and_counts_are_rejected(self):
        for n,c,tau,eps,delta in [(True,64,F(1,64),F(9,640),F(1,20)),
                (1,0,F(1,64),F(9,640),F(1,20)),(1,64,.01,F(9,640),F(1,20)),
                (1,64,F(1,64),F(1,64),F(1,20))]:
            with self.subTest(n=n,c=c),self.assertRaises((TypeError,ValueError)):
                raw_component_upper(n,c,tau,eps,delta)
        for counts,c in [([],3),([True],3),([4],3),([-1],3),([1],0)]:
            with self.subTest(counts=counts,c=c),self.assertRaises((TypeError,ValueError)):
                risks(counts,c)


if __name__=='__main__':
    unittest.main()
