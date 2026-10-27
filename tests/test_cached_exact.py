"""Small exact stopped-process checks independent of the callback engine."""
from fractions import Fraction as F
from functools import lru_cache
import itertools
import unittest

from goodhart_audit.cached import audit
from goodhart_audit.cached_math import design


ARGS=(8,1,(1,),F(3,4),F(1,2),F(1,4))
ETA=F(1,10)


def binary_recurrence(plan, positives):
    """Sum exact uniform-item probabilities; do not import engine helpers."""
    size=plan.prompts
    safe=F(positives,size)<=plan.tau

    @lru_cache(None)
    def value(time, seen_zero, seen_one, ones):
        acquired=seen_zero+seen_one
        score=(time-ones)*plan.zero_increment+ones*plan.one_increment
        if acquired==size:
            return F(safe),F(size)
        if score>=plan.log_threshold:
            return F(1),F(acquired)
        if time==plan.proposal_cap:
            return F(safe),F(size)
        certificate=cost=F(0)
        transitions=((seen_zero,0,0,0),(size-positives-seen_zero,1,0,0),
                     (seen_one,0,0,1),(positives-seen_one,0,1,1))
        if sum(t[0] for t in transitions)!=size:
            raise RuntimeError('independent transition partition failed')
        for count,dz,do,coin in transitions:
            if count:
                chance=F(count,size)
                passed,labels=value(time+1,seen_zero+dz,seen_one+do,ones+coin)
                certificate+=chance*passed
                cost+=chance*labels
        return certificate,cost
    return value(0,0,0,0)


class CachedExactTests(unittest.TestCase):
    def test_later_budget_partial_evidence_overrides_an_earlier_statistical_pass(self):
        args=(4,9,(1,2),F(3,4),F(1,2),F(1,4))
        plan=design(*args,ETA)
        self.assertEqual(plan.mode,'likelihood')
        draws=[0,0,0,0]  # Budget 1 passes after two zero coins on the same item.
        cumulative=plan.rank_cumulative_masses[1]
        for rank in tuple(range(1,8))+(0,):
            for prompt in range(4):
                draws.extend((cumulative[rank-1] if rank else 0,prompt))
                if rank==1:
                    draws.append(0)  # Fresh Bernoulli(6/7) coin equals one.
        draws=iter(draws)
        result=audit(*args,lambda p,r:F(0) if r==0 else F(6,7) if r==1 else F(1),
                     eta=ETA,randbelow=lambda upper:next(draws))
        self.assertEqual(result.status,'not_certified')
        self.assertEqual((result.proposals,result.distinct_labels),(34,32))
        self.assertEqual(result.budget_results[0].status,'unsafe')
        self.assertIsNone(result.budget_results[0].exact_risk)
        self.assertEqual(result.budget_results[1].exact_risk,F(3,4))
        known=sum(row.loss*plan.winner_weights[0][row.rank_index]/plan.prompts
                  for row in result.acquisitions)
        self.assertEqual(known,F(16,21))
        self.assertGreater(known,plan.tau)

    def test_real_engine_zero_table_matches_full_two_proposal_enumeration(self):
        total=0
        for first,second in itertools.product(range(8),repeat=2):
            values=iter((0,first,0,second))
            result=audit(*ARGS,lambda p,r:0,eta=ETA,randbelow=lambda upper:next(values))
            self.assertEqual(result.status,'certified')
            self.assertEqual(result.proposals,2)
            self.assertEqual(result.distinct_labels,1+(first!=second))
            total+=result.distinct_labels
        self.assertEqual(F(total,64),F(15,8))

    def test_exact_binary_safe_class_completes_with_certified_expected_cost(self):
        plan=design(*ARGS,ETA)
        for positives in (0,1,2):
            probability,cost=binary_recurrence(plan,positives)
            self.assertEqual(probability,1)
            self.assertLessEqual(cost,plan.expected_label_bound)
        self.assertEqual(binary_recurrence(plan,0)[1],F(15,8))

    def test_exact_binary_unsafe_probabilities_respect_delta(self):
        plan=design(*ARGS,ETA)
        for positives in (7,8):
            probability,cost=binary_recurrence(plan,positives)
            self.assertLessEqual(probability,plan.delta)
            self.assertLessEqual(cost,8)
        self.assertEqual(binary_recurrence(plan,8)[0],0)

    def test_exact_boundary_completion_does_not_rely_on_positive_log_drift(self):
        plan=design(*ARGS,ETA)
        probability,cost=binary_recurrence(plan,6)
        self.assertEqual(probability,1)
        self.assertLessEqual(cost,8)


if __name__=='__main__':
    unittest.main()
