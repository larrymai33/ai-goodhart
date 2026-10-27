"""Independent finite checks for deterministic budget-coverage helpers."""
from fractions import Fraction as F
import importlib
import itertools
import unittest

try:
    coverage = importlib.import_module('goodhart_audit.coverage')
except ModuleNotFoundError as error:
    if error.name != 'goodhart_audit.coverage':
        raise
    coverage = None


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(coverage, 'coverage helpers missing')

    def test_integer_factor_is_attained_and_adjacent_intervals_have_no_penalty(self):
        for a in range(1, 12):
            for b in range(a+1, 25):
                expected = max(F(n*(a+b-n), a*b) for n in range(a,b+1))
                self.assertEqual(coverage.interval_factor(a,b), expected)
                if b == a+1:
                    self.assertEqual(expected,1)
        self.assertEqual(coverage.interval_factor(32,64), F(9,8))

    def test_interpolation_has_correct_endpoints_and_clamps_at_one(self):
        self.assertEqual(coverage.interpolate_upper(2,8,2,F(1,4),F(1,2)),F(1,4))
        self.assertEqual(coverage.interpolate_upper(2,8,8,F(1,4),F(1,2)),F(1,2))
        self.assertEqual(coverage.interpolate_upper(32,64,48,F(3,32),F(3,32)),F(27,256))
        self.assertEqual(coverage.interpolate_upper(1,8,4,1,1),1)
        self.assertEqual(coverage.interpolate_upper(1,8,4,0,0),0)

    def test_subset_oracle_supports_every_small_binary_curve(self):
        for m in range(3,7):
            subsets={n:list(itertools.combinations(range(m),n)) for n in range(1,m+1)}
            for y in itertools.product((0,1),repeat=m):
                risks={n:F(sum(y[min(s)] for s in rows),len(rows)) for n,rows in subsets.items()}
                for a,n,b in itertools.combinations(range(1,m+1),3):
                    self.assertLessEqual(risks[n],coverage.interpolate_upper(a,b,n,risks[a],risks[b]))

    def test_documented_grid_and_extreme_levels(self):
        self.assertEqual(coverage.covering_grid(64,F(3,32),F(1,10)),
                         (1,2,3,5,8,13,21,35,58,64))
        self.assertEqual(coverage.covering_grid(1,0,0),(1,))
        self.assertEqual(coverage.covering_grid(13,0,0),(1,13))
        self.assertEqual(coverage.covering_grid(13,F(1,10),F(1,10)),tuple(range(1,14)))
        self.assertEqual(coverage.covering_grid(100000,0,1),(1,100000))

    def test_greedy_cardinality_matches_independent_shortest_path(self):
        for m in range(1,33):
            for s,tau in ((F(0),F(0)),(F(1,10),F(1,10)),(F(3,32),F(1,10)),(F(1,16),F(1,8))):
                shortest=[0]*(m+1)
                shortest[1]=1
                for b in range(2,m+1):
                    shortest[b]=min(shortest[a]+1 for a in range(1,b)
                        if all(s*F(n*(a+b-n),a*b)<=tau for n in range(a,b+1)))
                grid=coverage.covering_grid(m,s,tau)
                self.assertEqual(len(grid),shortest[m])
                self.assertEqual(grid[0],1)
                self.assertEqual(grid[-1],m)
                self.assertTrue(all(s*coverage.interval_factor(a,b)<=tau for a,b in zip(grid,grid[1:])))

    def test_rejects_invalid_endpoint_inputs_and_nonexact_types(self):
        for args in ((0,2),(2,2),(3,2),(True,2),(1,2.0),(1,100001)):
            with self.assertRaises(ValueError):
                coverage.interval_factor(*args)
        for args in ((1,3,0,0,0),(1,3,4,0,0),(1,3,True,0,0),
                     (1,3,2,-1,0),(1,3,2,0,F(3,2)),(1,3,2,0.1,0),
                     (1,3,2,True,0)):
            with self.assertRaises(ValueError):
                coverage.interpolate_upper(*args)

    def test_rejects_invalid_grid_levels_and_pool_sizes(self):
        for args in ((0,0,1),(100001,0,1),(True,0,1),(3.0,0,1),
                     (3,-1,1),(3,1,0),(3,0,2),(3,0.1,1),(3,0,True)):
            with self.assertRaises(ValueError):
                coverage.covering_grid(*args)


if __name__ == '__main__':
    unittest.main()
