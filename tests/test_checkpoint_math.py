"""Exact distribution and atom-sensitive checks for finite checkpoints."""
from collections import Counter
from fractions import Fraction as F
import importlib
from itertools import combinations, combinations_with_replacement
from math import comb
import unittest

try:
    math = importlib.import_module('goodhart_audit.checkpoint_math')
except ModuleNotFoundError as error:
    if error.name != 'goodhart_audit.checkpoint_math':
        raise
    math = None


class CheckpointMathTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(math, 'checkpoint arithmetic missing')

    def test_extremal_law_matches_direct_subsets_including_integer_endpoints(self):
        for n in range(1,8):
            for u in range(n+1):
                for quarter in range(4*n+1):
                    total=F(quarter,4)
                    j=total.numerator//total.denominator
                    population=[F(1)]*j
                    if total>j:
                        population.append(total-j)
                    population += [F(0)]*(n-len(population))
                    counts=Counter(sum((population[i] for i in ix),F(0))
                                   for ix in combinations(range(n),n-u))
                    law=math.extremal_law(n,u,total)
                    self.assertEqual(dict(law.masses),dict(counts))
                    self.assertEqual(law.denominator,comb(n,u))

    def test_lower_shortfall_matches_variational_formula(self):
        for total in (F(0),F(3,4),F(5,2),F(4)):
            law=math.extremal_law(4,2,total)
            for alpha in (F(1,20),F(1,3),F(1)):
                expected=max(v-sum((max(v-x,0)*c for x,c in law.masses),F(0))
                             /(alpha*law.denominator) for v,_ in law.masses)
                self.assertEqual(math.lower_shortfall(law,alpha),expected)

    def test_upper_tail_matches_direct_hinge_optimization(self):
        law=math.extremal_law(6,2,F(11,4))
        for quarter in range(-1,15):
            cutoff=F(quarter,4)
            candidates=[F(1)]
            if cutoff>law.masses[-1][0]:
                candidates.append(F(0))
            for v,_ in law.masses:
                if v<cutoff:
                    candidates.append(sum((max(x-v,0)*c for x,c in law.masses),F(0))
                                      /(law.denominator*(cutoff-v)))
            actual=math.upper_tail(law,cutoff)
            self.assertEqual(actual,min(candidates))
            true=F(sum(c for x,c in law.masses if x>=cutoff),law.denominator)
            self.assertGreaterEqual(actual,true)

    def test_strict_cutoff_and_fractional_convex_hinges(self):
        # At a support atom the non-strict version can falsely pass surely.
        zero=math.extremal_law(4,2,F(0))
        self.assertEqual(math.lower_shortfall(zero,F(1,20)),0)
        self.assertEqual(math.upper_tail(zero,F(0)),1)
        for pop in combinations_with_replacement((F(0),F(1,2),F(1)),4):
            values=[sum((pop[i] for i in ix),F(0)) for ix in combinations(range(4),2)]
            law=math.extremal_law(4,2,sum(pop,F(0)))
            for v in (F(0),F(1,2),F(1),F(3,2),F(2)):
                for direction in (-1,1):
                    actual=sum((max(direction*(x-v),0) for x in values),F(0))/6
                    bound=sum((max(direction*(x-v),0)*c for x,c in law.masses),F(0))/law.denominator
                    self.assertLessEqual(actual,bound)

    def test_head_bins_assign_shared_boundaries_and_include_top(self):
        gap,top=F(2,3),F(8,3)
        for total,expected in [(gap,(gap,gap+1)),(gap+1,(gap+1,top)),(top,(gap+1,top))]:
            self.assertEqual(math.head_bin(total,gap,top),expected)
        self.assertEqual(math.head_bin(F(7,3),gap,F(7,3)),(gap+1,F(7,3)))
        self.assertEqual(math.head_bin(gap,gap,gap),(gap,gap))

    def test_rejects_nonexact_or_out_of_domain_inputs(self):
        for args in [(True,0,F(0)),(0,0,F(0)),(2049,0,F(0)),(4,True,F(0)),
                     (4,-1,F(0)),(4,5,F(0)),(4,2,0.5),(4,2,True),(4,2,F(-1)),(4,2,F(5))]:
            with self.assertRaises(ValueError): math.extremal_law(*args)
        law=math.extremal_law(4,2,F(1))
        for alpha in (0,F(-1),F(2),0.5,True):
            with self.assertRaises(ValueError): math.lower_shortfall(law,alpha)
        for args in [(F(0),F(1),F(2)),(F(3),F(1),F(2)),(F(1),F(2),F(1))]:
            with self.assertRaises(ValueError): math.head_bin(*args)


if __name__=='__main__':
    unittest.main()
