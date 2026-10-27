"""Lossless layout normalization for the current manuscript's math subset."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'paper/finite-cost/format_math.py'
if PATH.exists():
    spec=importlib.util.spec_from_file_location('finite_cost_format',PATH)
    formatting=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formatting)
else:
    formatting=None


class FiniteCostFormatTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(formatting,'manuscript formatter missing')

    def test_alignment_splits_rows_and_preserves_every_relation(self):
        source=r'\begin{aligned} X&=a+b,\\ &\le c.\end{aligned}\tag{A17}'
        rows,tag=formatting.display_rows(source)
        self.assertEqual(rows,(r'X=a+b,',r'\leq c.'))
        self.assertEqual(tag,'A17')

    def test_atomic_tex_shorthand_has_explicit_groups(self):
        source=r'\binom mn+\binom Nt+\tfrac34+\mathbb E T+\mathbf1'
        self.assertEqual(formatting.normalize_math(source),
                         r'\binom{m}{n}+\binom{N}{t}+\frac{3}{4}+\mathbb{E} T+\mathbf{1}')

    def test_source_line_wrapping_does_not_reach_math_renderer(self):
        rows,tag=formatting.display_rows('x=1+\n2\n')
        self.assertEqual(rows,('x=1+ 2',))
        self.assertIsNone(tag)

    def test_end_of_proof_marker_is_explicit_text(self):
        self.assertEqual(formatting.normalize_math(r'\square'),r'\mathrm{QED}')

    def test_single_atom_radical_has_explicit_group(self):
        self.assertEqual(formatting.normalize_math(r'\sqrt2+\sqrt{pv}'),r'\sqrt{2}+\sqrt{pv}')

    def test_text_keeps_spaces_and_existing_groups_unchanged(self):
        self.assertEqual(formatting.normalize_math(r'\hbox{for every }n\in\mathcal K'),
                         r'\mathrm{for\ every\ }n\in\mathcal{K}')
        self.assertEqual(formatting.normalize_math(r'\frac{a+b}{c}\ge\operatorname{KL}(p,q)'),
                         r'\frac{a+b}{c}\geq\operatorname{KL}(p,q)')

    def test_unknown_environment_and_ambiguous_numbering_fail(self):
        for source in (r'\begin{array}a\end{array}',r'x\tag{A1}\tag{A2}',r'\begin{aligned}x'):
            with self.assertRaises(ValueError): formatting.display_rows(source)


if __name__=='__main__':
    unittest.main()
