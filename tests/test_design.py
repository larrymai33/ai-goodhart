"""Independent objective and dual checks for the optional design optimizer."""

import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
except ImportError:
    raise unittest.SkipTest("Design tests need already-installed NumPy and SciPy")

from goodhart_audit.design import optimize_design


def objective(weights, proposal, rho):
    values = []
    for row in weights:
        variance = math.fsum(a * a / q for a, q in zip(row, proposal) if a > 0)
        maximum = max((a / q for a, q in zip(row, proposal) if a > 0), default=0)
        values.append(variance + rho * maximum)
    return max(values)


def dual_objective(weights, records, rho):
    mixture = []
    for j in range(len(weights[0])):
        value = math.fsum(
            record["weight"] * (
                weights[record["target"]][j] ** 2
                + (rho * weights[record["target"]][j] if record["coordinate"] == j else 0)
            )
            for record in records
        )
        mixture.append(value)
    return math.fsum(math.sqrt(value) for value in mixture) ** 2


class DesignTests(unittest.TestCase):
    def check_bracket(self, weights, rho, result, tolerance):
        proposal = result["proposal"]
        records = result["dual_weights"]
        self.assertEqual(len(proposal), len(weights[0]))
        self.assertAlmostEqual(math.fsum(proposal), 1, places=12)
        for j, q in enumerate(proposal):
            if any(row[j] > 0 for row in weights):
                self.assertGreater(q, 0)
            else:
                self.assertEqual(q, 0)
        self.assertTrue(records)
        self.assertAlmostEqual(math.fsum(record["weight"] for record in records), 1, places=12)
        for record in records:
            self.assertGreater(record["weight"], 0)
            self.assertIsInstance(record["target"], int)
            self.assertTrue(0 <= record["target"] < len(weights))
            if rho == 0:
                self.assertIsNone(record["coordinate"])
            else:
                self.assertIsInstance(record["coordinate"], int)
                self.assertTrue(0 <= record["coordinate"] < len(proposal))
        primal = objective(weights, proposal, rho)
        dual = dual_objective(weights, records, rho)
        self.assertAlmostEqual(result["primal_value"], primal, places=10)
        self.assertAlmostEqual(result["dual_value"], dual, places=10)
        self.assertGreaterEqual(primal + 1e-12, dual)
        gap = max(0.0, (primal - dual) / dual)
        self.assertAlmostEqual(result["relative_gap"], gap, places=11)
        self.assertLessEqual(gap, tolerance)
        self.assertIsInstance(result["iterations"], int)
        self.assertGreaterEqual(result["iterations"], 0)

    def test_identical_rows_have_known_optimal_proposal_and_value(self):
        weights = [[0.2, 0.3, 0.5], [0.2, 0.3, 0.5]]
        for rho in [0.0, 0.2, 2.0]:
            with self.subTest(rho=rho):
                result = optimize_design(weights, rho=rho)
                self.check_bracket(weights, rho, result, 1e-5)
                for q, a in zip(result["proposal"], weights[0]):
                    self.assertAlmostEqual(q, a, places=5)
                self.assertAlmostEqual(result["primal_value"], 1 + rho, places=5)

    def test_disjoint_targets_allocate_equal_total_mass_to_each_target(self):
        weights = [[0.25, 0.75, 0, 0], [0, 0, 0.4, 0.6]]
        for rho in [0.0, 0.25]:
            with self.subTest(rho=rho):
                result = optimize_design(weights, rho=rho)
                self.check_bracket(weights, rho, result, 1e-5)
                self.assertAlmostEqual(sum(result["proposal"][:2]), 0.5, places=5)
                self.assertAlmostEqual(result["primal_value"], 2 * (1 + rho), places=5)

    def test_nontrivial_primal_dual_bracket_is_independently_checkable(self):
        weights = [[0.6, 0.3, 0.1], [0.1, 0.2, 0.7], [0.4, 0.4, 0.2]]
        for rho in [0.0, 1 / 48, 0.5]:
            with self.subTest(rho=rho):
                result = optimize_design(weights, rho=rho, tolerance=2e-6)
                self.check_bracket(weights, rho, result, 2e-6)
                self.assertGreater(result["iterations"], 0)

    def test_unsupported_columns_stay_zero_and_dual_indices_refer_to_original_columns(self):
        weights = [[0, 0.75, 0, 0.25, 0], [0, 0.2, 0, 0.8, 0]]
        result = optimize_design(weights, rho=0.1)
        self.check_bracket(weights, 0.1, result, 1e-5)
        self.assertTrue(all(record["coordinate"] in (1, 3) for record in result["dual_weights"]))

    def test_repeated_columns_keep_symmetry_and_a_valid_original_dimension_dual(self):
        weights = [[0.15, 0.35, 0.15, 0.35], [0.4, 0.1, 0.4, 0.1]]
        result = optimize_design(weights, rho=0.1)
        self.check_bracket(weights, 0.1, result, 1e-5)
        self.assertAlmostEqual(result["proposal"][0], result["proposal"][2], places=14)
        self.assertAlmostEqual(result["proposal"][1], result["proposal"][3], places=14)

    def test_small_row_sum_roundoff_is_normalized_without_mutating_inputs(self):
        weights = [[0.3, 0.7000000000001], [0.8, 0.2]]
        copied = [row[:] for row in weights]
        result = optimize_design(weights)
        normalized = [[value / math.fsum(row) for value in row] for row in weights]
        self.check_bracket(normalized, 0.0, result, 1e-5)
        self.assertEqual(weights, copied)

    def test_solver_success_flag_cannot_bypass_the_reported_gap(self):
        # An external solver can terminate without closing the dual gap.
        # Returning its unchanged feasible point must not count as convergence.
        def unchanged_solution(function, initial, **kwargs):
            return SimpleNamespace(x=initial.copy(), nit=0, success=True)

        weights = [[0.6, 0.3, 0.1], [0.1, 0.2, 0.7], [0.4, 0.4, 0.2]]
        with patch("goodhart_audit.design.minimize", side_effect=unchanged_solution), \
                patch("goodhart_audit.design.minimize_scalar", return_value=SimpleNamespace(x=0.0)):
            with self.assertRaisesRegex(RuntimeError, "did not reach relative gap"):
                optimize_design(weights)

    def test_invalid_inputs_fail_explicitly(self):
        for weights in [[], [[]], [[0, 0]], [[0.2, 0.2]], [[1], [0.5, 0.5]],
                        [[True]], [[math.nan]], [[math.inf]], [[-0.1, 1.1]], [["1"]]]:
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                optimize_design(weights)
        for rho in [-1, True, math.nan, math.inf, "0.1"]:
            with self.subTest(rho=rho), self.assertRaises(ValueError):
                optimize_design([[1]], rho=rho)
        for tolerance in [0, -1, 1, True, math.nan, math.inf, "0.1"]:
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                optimize_design([[1]], tolerance=tolerance)


if __name__ == "__main__":
    unittest.main()
