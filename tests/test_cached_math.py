"""Independent numerical and domain checks for the cached reference design."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import importlib
from math import comb
import unittest
from unittest.mock import patch

try:
    math = importlib.import_module('goodhart_audit.cached_math')
except ModuleNotFoundError as error:
    if error.name != 'goodhart_audit.cached_math':
        raise
    math = None


class CachedMathTests(unittest.TestCase):
    def test_log_enclosures_and_reciprocal_symmetry(self):
        with localcontext() as context:
            context.prec = 100
            for x in (F(1), F(2), F(3, 2), F(1, 20), F(1, 2**40), F(1234567, 891011)):
                lo, hi = math.log_interval(x, 96)
                exact = (Decimal(x.numerator)/Decimal(x.denominator)).ln()
                self.assertLessEqual(Decimal(lo.numerator)/Decimal(lo.denominator), exact)
                self.assertGreaterEqual(Decimal(hi.numerator)/Decimal(hi.denominator), exact)
                self.assertLessEqual(hi-lo, F(1, 2**96))
                inverse = math.log_interval(1/x, 96)
                self.assertEqual(inverse, (-hi, -lo))

    def test_square_root_upper_is_exact_and_within_one_grid_unit(self):
        for x in (F(0), F(1), F(2), F(1, 20), F(65537, 17)):
            root = math.sqrt_upper(x, 64)
            self.assertGreaterEqual(root*root, x)
            if root:
                self.assertLess((root-F(1, 2**64))**2, x)

    def test_all_sampling_rows_match_binomial_counts(self):
        result = math.design(3, 8, (1, 3, 8), F(1,8), F(1,128), F(1,20))
        self.assertEqual(result,math.design(3,8,(8,1,3),F(1,8),F(1,128),F(1,20)))
        for n, row, cumulative, denominator in zip(result.budgets, result.winner_weights,
                result.rank_cumulative_masses, result.rank_mass_denominators):
            numerators = [comb(8-r-1,n-1) if 8-r-1 >= n-1 else 0 for r in range(8)]
            self.assertEqual(denominator, comb(8,n))
            self.assertEqual(row, tuple(F(k,denominator) for k in numerators))
            self.assertEqual(cumulative, tuple(sum(numerators[:r+1]) for r in range(8)))
            self.assertEqual(sum(row),1)

    def test_rounded_steps_and_threshold_have_conservative_directions(self):
        result = math.design(8,1,(1,),F(3,4),F(1,2),F(1,4),F(1,10))
        self.assertEqual(result.mode,'likelihood')
        scale=result.log_scale
        u=math.log_interval((1-result.theta)/(1-result.tau),160)
        v=math.log_interval(result.tau/result.theta,160)
        ell=math.log_interval(1/result.delta,160)
        self.assertLessEqual(F(result.zero_increment,scale),u[0])
        self.assertLessEqual(F(result.one_increment,scale),-v[1])
        self.assertGreaterEqual(F(result.log_threshold,scale),ell[1])
        self.assertLessEqual(u[1]-F(result.zero_increment,scale),F(2,scale))
        self.assertLessEqual(-v[0]-F(result.one_increment,scale),F(2,scale))
        self.assertLessEqual(F(result.log_threshold,scale)-ell[0],F(2,scale))
        drift=(1-result.theta)*result.zero_increment+result.theta*result.one_increment
        self.assertGreater(drift,0)
        self.assertEqual(result.expected_proposals,F(result.log_threshold+result.zero_increment)/drift)

    def test_cap_log_inequality_and_cost_are_recomputable(self):
        result=math.design(8,1,(1,),F(3,4),F(1,2),F(1,4),F(1,10))
        scale=result.log_scale
        psi=math.sqrt_upper(result.theta*result.tau,scale.bit_length()-1)+math.sqrt_upper((1-result.theta)*(1-result.tau),scale.bit_length()-1)
        phi=psi/(1-F(1,scale))
        a0=math.sqrt_upper(1/result.delta,scale.bit_length()-1)/(1-F(1,scale))
        multiplier=result.prompts*result.prefix_cutoff*len(result.budgets)*a0/result.eta
        self.assertLess(phi,1)
        self.assertLessEqual(math.log_interval(multiplier,160)[1]+result.proposal_cap*math.log_interval(phi,160)[1],0)
        self.assertEqual(result.expected_label_bound,result.statistical_label_bound+result.eta)
        self.assertLessEqual(result.proposal_cap*len(result.budgets),math.MAX_TOTAL_PROPOSALS)

    def test_original_auto_mode_reports_prefix_without_claimed_improvement(self):
        result=math.design(32,64,(1,2,4,8,16,32,64),F(1,10),F(1,160),F(1,20))
        self.assertEqual((result.mode,result.prefix_cutoff,result.proposal_cap),('prefix',64,0))
        self.assertEqual(result.expected_label_bound,2048)
        self.assertEqual(result.factor_guarantee,'17F + eta')

    def test_larger_separated_design_certifies_factor_and_resource_budget(self):
        result=math.design(1024,64,(1,2,4,8,16,32,64),F(1,10),F(1,160),F(1,20),F(100))
        self.assertEqual(result.mode,'likelihood')
        self.assertEqual(result.factor_guarantee,'17F + eta')
        self.assertLess(result.expected_label_bound,40000)
        self.assertLessEqual(7*result.proposal_cap,math.MAX_TOTAL_PROPOSALS)
        lo=math.log_interval(20,160)[0]
        self.assertLessEqual(result.expected_proposals,F(17,8)*result.tau*lo/result.epsilon**2)

    def test_factor_scope_is_not_assigned_outside_its_domain(self):
        result=math.design(3,4,(1,2,3,4),F(1,8),F(1,128),F(1,20))
        self.assertIsNone(result.factor_guarantee)
        result=math.design(8,1,(1,),F(3,4),F(1,2),F(1,4),F(1,10))
        self.assertIsNone(result.factor_guarantee)

    def test_validation_and_likelihood_resource_rejection(self):
        valid=[8,1,(1,),F(3,4),F(1,2),F(1,4),F(1,10)]
        for index,value in ((0,True),(0,100001),(1,1025),(2,(1,1)),(2,()),(3,0.75),(4,True),(4,F(3,4)),(5,1),(6,0),(6,F(1,2**65))):
            args=valid.copy();args[index]=value
            with self.subTest(index=index,value=value),self.assertRaises(ValueError):math.design(*args)
        with patch.object(math,'MAX_TOTAL_PROPOSALS',1):
            with self.assertRaisesRegex(ValueError,'proposal'):math.design(*valid)
        for function in (math.log_interval,math.sqrt_upper):
            with self.assertRaises(ValueError):function(0.5)


if __name__=='__main__':
    unittest.main()
