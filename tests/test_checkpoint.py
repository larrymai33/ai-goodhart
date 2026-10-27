"""Charged callback conformance for the original finite decision."""
from fractions import Fraction as F
import importlib
import random
import unittest
from unittest.mock import patch

try:
    audit_module=importlib.import_module('goodhart_audit.checkpoint')
except ModuleNotFoundError as error:
    if error.name!='goodhart_audit.checkpoint':
        raise
    audit_module=None


class TailOrder:
    """Scripted permutations test branches; they are not random evidence."""
    def __init__(self, positives_first):
        self.remaining=[(p,r) for p in range(32) for r in range(33,65)]
        positives=[cell for cell in self.remaining if cell[1]>=59]
        zeros=[cell for cell in self.remaining if cell[1]<59]
        self.order=iter(positives[:positives_first]+zeros+positives[positives_first:])

    def __call__(self,bound):
        if bound!=len(self.remaining):
            raise AssertionError('unexpected RNG bound')
        index=self.remaining.index(next(self.order))
        self.remaining[index],self.remaining[-1]=self.remaining[-1],self.remaining[index]
        self.remaining.pop()
        return index


class CheckpointAuditTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(audit_module,'checkpoint callback missing')

    def run_table(self,oracle,**kwargs):
        calls=[]
        def checked(p,r):
            self.assertTrue(0<=p<32 and 1<=r<=64)
            self.assertNotIn((p,r),calls)
            calls.append((p,r))
            return oracle(p,r)
        result=audit_module.audit(checked,**kwargs)
        self.assertEqual(calls,[(a.prompt,a.rank) for a in result.acquisitions])
        self.assertLessEqual(len(calls),2048)
        return result

    def test_zero_table_stops_at_first_checkpoint_with_all_labels_charged(self):
        result=self.run_table(lambda p,r:F(0),randbelow=random.Random(11).randrange)
        self.assertTrue(result.certified)
        self.assertEqual(result.reason,'checkpoint')
        self.assertEqual(len(result.acquisitions),2000)
        self.assertEqual(result.error_bound,F(1,200))
        self.assertFalse(result.allow_blind)
        self.assertTrue(all(t.passed for t in result.checkpoints[-1].targets))

    def test_scripted_margin_tables_exercise_all_three_stopping_checkpoints(self):
        for first,cost in ((184,2000),(188,2016),(192,2032)):
            result=self.run_table(lambda p,r:int(r>=59),randbelow=TailOrder(first))
            self.assertTrue(result.certified)
            self.assertEqual(result.reason,'checkpoint')
            self.assertEqual(len(result.acquisitions),cost)
            self.assertEqual(result.checkpoints[-1].acquired_count,cost)
            self.assertEqual(result.checkpoints[-1].omitted,2048-cost)

    def test_constant_margin_finishes_by_last_checkpoint(self):
        for seed in (11,29,47):
            result=self.run_table(lambda p,r:F(3,32),randbelow=random.Random(seed).randrange)
            self.assertTrue(result.certified)
            self.assertLessEqual(len(result.acquisitions),2032)

    def test_boundary_safe_table_goes_to_census_and_certifies(self):
        def no_rng(bound):
            raise AssertionError('unsupported head must go directly to census')
        result=self.run_table(lambda p,r:F(1,10),randbelow=no_rng)
        self.assertTrue(result.certified)
        self.assertEqual(result.reason,'census_safe')
        self.assertEqual(len(result.acquisitions),2048)
        self.assertEqual(result.full_risks,(F(1,10),)*7)
        self.assertEqual(result.checkpoints,())

    def test_unsafe_and_heterogeneous_boundary_tables_have_exact_final_decision(self):
        unsafe=self.run_table(lambda p,r:F(17,160),randbelow=lambda n:0)
        self.assertFalse(unsafe.certified)
        self.assertEqual(unsafe.reason,'census_unsafe')
        self.assertEqual(len(unsafe.acquisitions),2048)
        # One prompt at loss 1, others at 11/155 gives every risk exactly .1.
        boundary=self.run_table(lambda p,r:F(1) if p==0 else F(11,155),randbelow=lambda n:0)
        self.assertTrue(boundary.certified)
        self.assertEqual(boundary.full_risks,(F(1,10),)*7)

    def test_blind_mode_is_explicit_and_charges_no_unasked_labels(self):
        def forbidden(p,r):
            raise AssertionError('blind branch must not access labels')
        result=audit_module.audit(forbidden,allow_blind=True,randbelow=lambda bound:8)
        self.assertTrue(result.certified)
        self.assertEqual(result.reason,'blind')
        self.assertEqual(result.acquisitions,())
        self.assertEqual(result.error_bound,F(1,20))
        bounds=[]
        def rng(bound):
            bounds.append(bound)
            return 9 if len(bounds)==1 else 0
        evidence=self.run_table(lambda p,r:0,allow_blind=True,randbelow=rng)
        self.assertEqual(bounds[0],199)
        self.assertEqual(evidence.reason,'checkpoint')
        self.assertEqual(len(evidence.acquisitions),2000)

    def test_equality_with_cutoff_does_not_pass(self):
        with patch.object(audit_module,'lower_shortfall',return_value=F(0)):
            result=self.run_table(lambda p,r:0,randbelow=lambda n:0)
        self.assertEqual(result.reason,'census_safe')
        self.assertEqual(len(result.checkpoints),3)
        self.assertEqual(len(result.acquisitions),2048)
        self.assertTrue(all(not t.passed for stage in result.checkpoints for t in stage.targets))

    def test_bad_configuration_labels_and_rng_raise_without_certificate(self):
        for kwargs in ({'allow_blind':1},{'randbelow':7}):
            with self.assertRaises(ValueError): audit_module.audit(lambda p,r:0,**kwargs)
        with self.assertRaises(ValueError): audit_module.audit(None)
        for value in (True,0.5,'0',F(-1),F(2),F(1,1000001)):
            with self.assertRaises(ValueError): audit_module.audit(lambda p,r:value)
        for value in (True,-1,199,0.5):
            with self.assertRaises(ValueError):
                audit_module.audit(lambda p,r:0,allow_blind=True,randbelow=lambda bound:value)
        with self.assertRaises(ValueError):
            audit_module.audit(lambda p,r:0,randbelow=lambda bound:bound)
        def broken(p,r): raise RuntimeError('label unavailable')
        with self.assertRaisesRegex(RuntimeError,'label unavailable'):
            audit_module.audit(broken)


if __name__=='__main__':
    unittest.main()
