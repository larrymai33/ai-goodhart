"""Independent finite checks for the all-grid cost proof implementation."""
from fractions import Fraction as F
import hashlib
import importlib
import itertools
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

try:
    check = importlib.import_module('experiments.check_all_grid_minimax')
except ModuleNotFoundError as error:
    if error.name != 'experiments.check_all_grid_minimax':
        raise
    check = None

ROOT = Path(__file__).resolve().parents[1]


def weights(m, n):
    return tuple(F(comb(m-r, n-1), comb(m, n)) if m-r >= n-1 else F(0)
                 for r in range(1, m+1))


class AllGridMinimaxTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, 'all-grid checker implementation missing')

    def test_representatives_preserve_arbitrary_gaps_and_original_budgets(self):
        self.assertEqual(check.representatives((1, 2, 3, 4, 15, 16)), (1, 4, 16))
        self.assertEqual(check.representatives((3, 5, 17, 80)), (3, 17, 80))
        self.assertEqual(check.representatives((1, 2, 4, 8), factor=2), (1, 2, 4, 8))
        for invalid in ((), (1, 1), (2, 1), (True, 4)):
            with self.assertRaises(ValueError):
                check.representatives(invalid)

    def test_functional_matches_independent_prefix_and_grid_enumeration(self):
        for m in range(1, 6):
            for mask in range(1, 1 << m):
                grid = tuple(n for n in range(1, m+1) if mask & (1 << (n-1)))
                rows = [weights(m, n) for n in grid]
                envelope = tuple(map(max, zip(*rows)))
                tau, epsilon, log_inv = F(1, 8), F(1, 128), F(3, 2)
                h = tau*log_inv/epsilon**2
                cost = min(3*k+h*sum(envelope[k:], F(0)) for k in range(m+1))
                cutoff = next(k for k in range(m+1) if sum(rows[0][k:], F(0)) <= epsilon)
                actual = check.family_profile(m, 3, grid, tau, epsilon, log_inv)
                self.assertEqual(actual['G'], cost)
                self.assertEqual(actual['prefix_cutoff'], cutoff)
                self.assertEqual(actual['F'], min(3*cutoff, cost))

    def test_all_lower_proof_branches_and_residual_band_boundaries(self):
        args = (F(1, 8), F(1, 128), F(3, 2))
        examples = [(8, 1, (1, 8), 'uniform_tail'),
                    (8, 1, (2, 8), 'high_budget'),
                    (9, 1, (2, 9), 'tail_blocks'),
                    (16, 2**20, (1, 2, 4, 8, 16), 'broad_bands')]
        for m, prompts, grid, branch in examples:
            row = check.family_profile(m, prompts, grid, *args)
            self.assertEqual(row['lower_branch'], branch)
            self.assertGreaterEqual(row['proved_lower'], row['F']/2**38)
            self.assertLessEqual(row['proved_upper'], 2**16*row['F'])
        edge = check.family_profile(16, 6144, (1, 4, 16), *args)
        self.assertEqual(edge['broad_count'], 1)
        self.assertEqual(edge['residual_prefix'], 4)

    def test_conditional_tail_identity_and_length_three_geometry(self):
        for m, n in ((9, 2), (10, 2), (13, 3), (33, 7), (64, 2)):
            row = check.conditional_tail_geometry(m, n, 1, F(1, 128), F(3072))
            original, conditional = weights(m, n), weights(row['conditional_pool'], n)
            self.assertEqual(original[row['head_cutoff']:], tuple(row['tail_mass']*x for x in conditional))
            self.assertGreaterEqual(row['retained_blocks'], 1)
            self.assertLessEqual(row['conditional_F'], 8192*row['A'])
        self.assertEqual(check.conditional_tail_geometry(9, 2, 1, F(1, 128), F(3072))['block_length'], 3)

    def test_bound_arithmetic_and_serialized_profiles_never_use_floats(self):
        def no_float(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for item in value.values():
                    no_float(item)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    no_float(item)
        args = (F(1, 8), F(1, 128), F(3, 2))
        for m, prompts, grid in ((8,1,(2,8)), (9,1,(2,9)), (9,1,(1,)),
                                 (16,2**20,(1,2,4,8,16))):
            with self.subTest(grid=grid):
                row = check.family_profile(m,prompts,grid,*args)
                no_float(row)
                no_float(json.loads(json.dumps(check.json_value(row))))
                self.assertEqual(row['universal_lower'], F(row['F'])/2**38)
        uniform = check.family_profile(9,1,(1,),*args)
        self.assertIsInstance(uniform['F']/uniform['proved_lower'], F)
        self.assertEqual(uniform['F']/uniform['proved_lower'], F(1179648,5))
        saturated = check.centered_slice_check(3,*args[:2],F(1),F(1),args[2])
        self.assertIsInstance(saturated['target'], F)

    def test_exact_serializer_rejects_nested_floating_values(self):
        for value in (0.5, {'bound': [0.5]}, {'bound': float('nan')}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'float'):
                check.json_value(value)

    def test_cached_geometry_revalidates_equal_but_invalid_types(self):
        check.conditional_tail_geometry(9, 2, 1, F(1,128), F(3072))
        for prompts, scale in ((True,F(3072)),(1,3072.0)):
            with self.assertRaises(ValueError):
                check.conditional_tail_geometry(9, 2, prompts, F(1,128), scale)

    def test_derived_scale_cap_does_not_depend_on_lower_proof_branch(self):
        for grid in ((2,), (3,)):
            row=check.family_profile(9,1,grid,F(1,8),F(1,2**200),F(3,2))
            self.assertEqual(row['F'],9-grid[0]+1)

    def test_centered_slice_counts_and_actual_fractional_label_maps(self):
        for size in (3, 4, 5, 64, 72, 128):
            tau, epsilon, q = F(1, 8), F(1, 128), F(1, 4)
            raw = tuple(F(size+i, 1) for i in range(size))
            item = tuple(q*x/sum(raw) for x in raw)
            minimum_mass = size*min(item)
            row = check.centered_slice_check(size, tau, epsilon, q, minimum_mass, F(3, 2))
            k, d, p0 = row['null_count'], row['added_count'], (tau-epsilon)/q
            for count in (k, k+d):
                for offset in (0, size//2):
                    positive = {(offset+j) % size for j in range(count)}
                    labels = [p0+min(item)/(2*w)*(int(i in positive)-F(k, size)) for i, w in enumerate(item)]
                    self.assertTrue(all(0 <= y <= 1 for y in labels))
                    risk = sum(w*y for w, y in zip(item, labels))
                    if count == k:
                        self.assertEqual(risk, tau-epsilon)
                    else:
                        self.assertGreater(risk, tau)
        boundary = check.centered_slice_check(3, F(1, 8), F(1, 128), F(1, 4), F(1, 16), F(3, 2))
        self.assertEqual((boundary['null_count'], boundary['added_count']), (0, 1))

    def test_geometric_mixture_uses_direct_weights_and_zero_support(self):
        for m, grid, factor in ((1, (1,), 4), (16, (1, 4, 16), 4),
                                (24, (2, 9), 4), (16, (1, 2, 4, 8, 16), 2)):
            rows = [weights(m, n) for n in grid]
            bound = F(14, 3) if factor == 4 else F(8)
            for rank in range(1, m+1):
                result = check.mixture_check(m, grid, rank, factor)
                values = [row[rank-1] for row in rows]
                self.assertEqual(result['sum'], sum(values, F(0)))
                self.assertLessEqual(result['sum'], bound*max(values))
        with self.assertRaises(ValueError):
            check.mixture_check(8, (2, 3), 1, 4)

    def test_likelihood_multiplier_and_predictable_acquisition_identity(self):
        tau, p = F(1, 8), F(15, 128)
        a, b = p/tau, (1-p)/(1-tau)
        self.assertEqual(tau*a+(1-tau)*b, 1)
        for risk in (tau, F(1, 2), F(1)):
            self.assertLessEqual(risk*a+(1-risk)*b, 1)
        # Stop at the first positive or after three proposals. The first item
        # has label 1, so stopping depends on the queried identity itself.
        probabilities = (F(1, 4), F(3, 4))
        expected_time = expected_first = F(0)
        for path in itertools.product(range(2), repeat=3):
            probability = F(1)
            for item in path:
                probability *= probabilities[item]
            length = next((i+1 for i, item in enumerate(path) if item == 0), 3)
            expected_time += probability*length
            expected_first += probability*sum(item == 0 for item in path[:length])
        self.assertEqual(expected_first, probabilities[0]*expected_time)
        self.assertGreater(check.likelihood_checks()['multiplier_checks'], 0)

    def test_protocol_rejects_resource_expansion_duplicates_and_types(self):
        protocol = json.loads((ROOT/'experiments/all_grid_minimax_protocol.json').read_bytes())
        for key, value in (('version', True), ('version', 1.0), ('grid_max_pool', 30), ('maximum_pool', 10000)):
            changed = dict(protocol)
            changed[key] = value
            with self.assertRaises(ValueError):
                check.validate_protocol(changed)
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b' '*16385):
            with self.assertRaises(ValueError):
                check.parse_protocol(raw)

    def test_nine_pins_and_every_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in check.SOURCE_PATHS:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                if name.endswith('_protocol.json'):
                    target.write_text(json.dumps(check.CANONICAL_PROTOCOL), encoding='utf-8')
                else:
                    target.write_bytes(b'Temporary source fixture.\n')
            path = root/'experiments/all_grid_minimax_protocol.json'
            with patch.object(check, 'ROOT', root), patch.object(check, 'IMPORTED_HELPER_PATH', root/check.SOURCE_PATHS[-1]), patch.object(check, 'calculate', return_value={}):
                result = check.build_results(None, path)
            self.assertEqual(len(result['source_sha256']), 9)
            for name in check.SOURCE_PATHS:
                target = root/name
                original = target.read_bytes()
                def mutate(_):
                    target.write_bytes(original+b'\n')
                    return {}
                with patch.object(check, 'ROOT', root), patch.object(check, 'IMPORTED_HELPER_PATH', root/check.SOURCE_PATHS[-1]), patch.object(check, 'calculate', side_effect=mutate):
                    with self.subTest(source=name), self.assertRaisesRegex(RuntimeError, 'changed'):
                        check.build_results(None, path)
                target.write_bytes(original)

    def test_actual_helper_and_external_protocol_paths_are_pinned(self):
        with tempfile.TemporaryDirectory() as directory:
            helper=Path(directory)/'loaded-helper.py'
            helper.write_bytes(b'Actual loaded helper fixture.\n')
            protocol=Path(directory)/'protocol.json'
            protocol.write_bytes((ROOT/'experiments/all_grid_minimax_protocol.json').read_bytes()+b'\n')
            with patch.object(check,'IMPORTED_HELPER_PATH',helper), patch.object(check,'calculate',return_value={}):
                result=check.build_results(None,protocol)
            hashes=result['source_sha256']
            self.assertEqual(hashes[str(helper.resolve())],hashlib.sha256(helper.read_bytes()).hexdigest())
            self.assertEqual(hashes[str(protocol.resolve())],hashlib.sha256(protocol.read_bytes()).hexdigest())
            self.assertNotIn('experiments/all_grid_minimax_protocol.json',hashes)

    def test_overwrite_guard_precedes_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/'result.json'
            out.write_bytes(b'preserve')
            with patch.object(check, 'build_results', side_effect=AssertionError('calculation started')):
                self.assertNotEqual(check.main(['--out', str(out)]), 0)
            self.assertEqual(out.read_bytes(), b'preserve')

    def test_invalid_inputs_and_optimized_checks_remain_active(self):
        args = (F(1, 8), F(1, 128), F(3, 2))
        for m, prompts, grid in ((129, 1, (1,)), (8, True, (1,)), (8, 1, (0, 4))):
            with self.assertRaises(ValueError):
                check.family_profile(m, prompts, grid, *args)
        command = 'from experiments.check_all_grid_minimax import require; require(False,"sentinel")'
        result = subprocess.run([sys.executable, '-B', '-S', '-O', '-c', command], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sentinel', result.stderr)


if __name__ == '__main__':
    unittest.main()
