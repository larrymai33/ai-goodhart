"""Exact finite-checkpoint certificate and frozen-runner regressions."""
from contextlib import redirect_stderr
from fractions import Fraction as F
import hashlib
import importlib
import io
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

try:
    check = importlib.import_module('experiments.check_finite_checkpoint')
except ModuleNotFoundError as error:
    if error.name != 'experiments.check_finite_checkpoint':
        raise
    check = None

ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/'experiments/finite_checkpoint_protocol.json').read_text())


def observed_law(size, omitted, total):
    """Independent observed-subset count, not the omitted-count helper."""
    ones = total.numerator//total.denominator
    fraction = total-ones
    zeros = size-ones-int(bool(fraction))
    sample = size-omitted
    masses = []
    for acquired_fraction in range(1+int(bool(fraction))):
        for k in range(max(0, sample-acquired_fraction-zeros),
                       min(ones, sample-acquired_fraction)+1):
            masses.append((F(k)+acquired_fraction*fraction,
                           comb(ones, k)*comb(zeros, sample-acquired_fraction-k)))
    return tuple(sorted(masses)), comb(size, sample)


def independent_shortfall(law, alpha):
    masses, denominator = law
    mass, moment, answer = 0, F(0), None
    for value, count in masses:
        candidate = value-(value*mass-moment)/(alpha*denominator)
        answer = candidate if answer is None else max(answer, candidate)
        mass += count
        moment += value*count
    return answer


def independent_upper(law, cutoff):
    masses, denominator = law
    if cutoff > masses[-1][0]:
        return F(0)
    candidates = [F(1)]
    for value, _ in masses:
        if value < cutoff:
            candidates.append(sum((max(x-value, 0)*count for x, count in masses), F(0))
                              /(denominator*(cutoff-value)))
    return min(candidates)


class FiniteCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, 'finite-checkpoint checker is missing')

    def test_every_registered_bin_matches_independent_observed_subset_arithmetic(self):
        result = check.checkpoint_certificate(protocol())
        count = 0
        for stage in result['stages']:
            alpha, omitted = F(stage['alpha']), stage['omitted']
            total = F(0)
            for target in stage['targets']:
                budget = target['budget']
                cap = F(comb(31, budget-1), 32*comb(64, budget))
                gap = F(1,160)/cap
                lower = gap
                best = F(0)
                first = None
                self.assertEqual(target['bin_count'], {1:192, 2:196, 4:425}[budget])
                for index, row in enumerate(target['bins']):
                    upper = min(lower+1, F(1,10)/cap)
                    self.assertEqual((F(row['lower']), F(row['upper'])), (lower, upper))
                    null_law = observed_law(1024, omitted, lower)
                    margin_law = observed_law(1024, omitted, upper-gap)
                    self.assertEqual(sum(c for _, c in null_law[0]), null_law[1])
                    cutoff = independent_shortfall(null_law, alpha)
                    beta = independent_upper(margin_law, cutoff)
                    self.assertEqual(F(row['cutoff']), cutoff)
                    self.assertEqual(F(row['nonpass_upper']), beta)
                    self.assertEqual(F(row['margin_maximum']), margin_law[0][-1][0])
                    if first is None or beta > best:
                        best, first = beta, index
                    lower = upper
                    count += 1
                self.assertEqual(F(target['nonpass_upper']), best)
                self.assertEqual(target['first_maximizing_bin'], first)
                total += best
            self.assertEqual(F(stage['nonpass_upper']), min(F(1), total))
        self.assertEqual(count, 2439)
        beta = [F(row['nonpass_upper']) for row in result['stages']]
        self.assertLess(beta[0], F(689,1000))
        self.assertLess(beta[1], F(311,1000))
        self.assertEqual(beta[2], 0)
        self.assertGreater(F(result['final_minimum_support_clearance']), 0)
        self.assertEqual(F(result['evidence_expected_upper']), 2000+16*sum(beta))
        self.assertLess(F(result['evidence_expected_upper']), 2016)
        self.assertEqual(F(result['mixed_conservative_upper']), F(383040,199))
        self.assertEqual(F(result['improvement_over_previous_upper']), F(9329,995))

    def test_independent_finite_checks_include_fractional_laws_and_unsafe_atom(self):
        result = check.independent_checks(protocol())
        self.assertEqual(result['direct_subset_laws'], 475)
        self.assertEqual(result['fractional_populations'], 456)
        self.assertEqual(result['convex_hinge_checks'], 18356)
        self.assertEqual(result['tail_checks'], 5547)
        atom = result['unsafe_atom_regression']
        self.assertGreater(F(atom['actual_total']), F(atom['null_total']))
        self.assertEqual(F(atom['strict_false_pass']), 0)
        self.assertEqual(F(atom['weak_false_pass']), F(1,2))
        self.assertGreater(F(atom['weak_false_pass']), F(atom['alpha']))

    def test_seeded_examples_are_charged_reproducible_and_disclosed(self):
        result = check.compute_examples(protocol())
        self.assertEqual(result, check.compute_examples(protocol()))
        self.assertIn('not empirical', result['interpretation'])
        self.assertEqual(len(result['runs']), 11)
        for run in result['runs']:
            if run['case'] == 'blind':
                self.assertEqual((run['reason'], run['acquired_count'], run['certified']), ('blind',0,1))
            elif run['case'] == 'unsafe':
                self.assertEqual((run['reason'], run['acquired_count'], run['certified']), ('census_unsafe',2048,0))
            elif run['case'] == 'boundary':
                self.assertEqual((run['reason'], run['acquired_count'], run['certified']), ('census_safe',2048,1))
            else:
                self.assertEqual(run['certified'], 1)
                self.assertIn(run['acquired_count'], (2000,2016,2032))
            self.assertEqual(len(run['acquisition_sha256']), 64)
        encoded = json.dumps(result, allow_nan=False)
        self.assertNotIn('0.05', encoded)

    def test_canonical_protocol_rejects_expansion_nonexact_types_and_duplicates(self):
        for key, value in (('version', True), ('version',1.0), ('bin_width','1/2'),
                           ('example_seeds',[7,29,31]), ('small_population_max',7)):
            altered = protocol()
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check.validate_protocol(altered)
        for raw in (b'{"version":1,"version":1}', b'{"x":NaN}', b'{"x":Infinity}',
                    b' '*16385, b'[]'):
            with self.subTest(raw=raw[:30]), self.assertRaises(ValueError):
                check.parse_protocol(raw)
        self.assertEqual(check.validate_protocol(protocol()), protocol())

    def fixture(self, directory):
        root = Path(directory)
        relatives = ('goodhart_audit/checkpoint_math.py', 'goodhart_audit/checkpoint.py',
                     'experiments/check_finite_checkpoint.py', 'tests/test_checkpoint_math.py',
                     'tests/test_checkpoint.py', 'tests/test_finite_checkpoint.py',
                     'docs/finite-checkpoint-theorem.md')
        for relative in relatives:
            path = root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Temporary source fixture.\n')
        path = root/'experiments/finite_checkpoint_protocol.json'
        path.write_text(json.dumps(protocol()))
        return root, path

    def fixture_patches(self, root):
        return (patch.object(check, 'ROOT', root),
                patch.object(check, '__file__', str(root/'experiments/check_finite_checkpoint.py')),
                patch.object(check.arithmetic, '__file__', str(root/'goodhart_audit/checkpoint_math.py')),
                patch.object(check.reference, '__file__', str(root/'goodhart_audit/checkpoint.py')))

    def test_eight_source_pins_use_bounded_protocol_snapshot_and_detect_each_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def bounded(candidate):
                if candidate == path:
                    self.fail('protocol must be read with a bounded stream')
                return original_read(candidate)
            contexts = self.fixture_patches(root)
            with contexts[0], contexts[1], contexts[2], contexts[3], \
                 patch.object(Path, 'read_bytes', bounded), \
                 patch.object(check, 'calculate', return_value={'fixture':1}):
                result = check.build_results(None, path)
            self.assertEqual(len(result['source_sha256']), 8)
            self.assertEqual(result['protocol_sha256'], hashlib.sha256(original_read(path)).hexdigest())
            for relative in result['source_sha256']:
                source = root/relative
                original = source.read_bytes()
                def mutate(_protocol):
                    source.write_bytes(original+b'\n')
                    return {'fixture':1}
                contexts = self.fixture_patches(root)
                with contexts[0], contexts[1], contexts[2], contexts[3], \
                     patch.object(check, 'calculate', side_effect=mutate):
                    with self.subTest(source=relative), self.assertRaisesRegex(RuntimeError, 'changed'):
                        check.build_results(None, path)
                source.write_bytes(original)

    def test_pins_reject_an_unexpected_loaded_scientific_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            contexts = self.fixture_patches(root)
            with contexts[0], contexts[1], contexts[2], contexts[3], \
                 patch.object(check.reference, '__file__', str(root/'other.py')):
                with self.assertRaisesRegex(RuntimeError, 'import'):
                    check.build_results(None, path)

    def test_existing_output_invalid_protocol_and_creation_race_preserve_files(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            root, path = self.fixture(directory)
            out = root/'result.json'
            out.write_bytes(b'preserve')
            with patch.object(check, 'build_results', side_effect=AssertionError('work started')):
                self.assertNotEqual(check.main(['--protocol',str(path),'--out',str(out)]),0)
            self.assertEqual(out.read_bytes(),b'preserve')
            invalid = root/'invalid.json'
            invalid.write_text('{"invalid":1}')
            absent = root/'new-parent/result.json'
            self.assertNotEqual(check.main(['--protocol',str(invalid),'--out',str(absent)]),0)
            self.assertFalse(absent.parent.exists())
            race = root/'race.json'
            def race_result(_supplied, _path):
                race.write_bytes(b'preserve race')
                return {'fixture':1}
            with patch.object(check, 'build_results', side_effect=race_result):
                self.assertNotEqual(check.main(['--protocol',str(path),'--out',str(race)]),0)
            self.assertEqual(race.read_bytes(),b'preserve race')

    def test_exact_certificate_checks_survive_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_finite_checkpoint as c\n"
                "bad=c.arithmetic.ExtremalLaw(((F(0),1),),2)\n"
                "with patch.object(c.arithmetic,'extremal_law',return_value=bad):\n"
                "    c.checkpoint_certificate(c.CANONICAL_PROTOCOL)\n")
        run = subprocess.run([sys.executable,'-B','-S','-O','-c',code],cwd=ROOT,
                             capture_output=True,text=True,timeout=30)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('RuntimeError',run.stderr)
        self.assertIn('mass',run.stderr)


if __name__ == '__main__':
    unittest.main()
