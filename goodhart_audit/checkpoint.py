"""Narrow, fully charged reference for the original 32-by-64 audit decision.

Default mode uses the evidence branch with error at most 1/200. Explicit
allow_blind=True adds an empty-query pass with probability 9/199, giving
the theoretical mixed benchmark at error 1/20. See the theorem and report.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb
import secrets

from .checkpoint_math import extremal_law, head_bin, lower_shortfall

PROMPTS = 32
POOL = 64
HEAD = 32
TAIL_SIZE = 1024
BUDGETS = (1,2,4,8,16,32,64)
TAU = F(1,10)
EPSILON = F(1,160)
SCHEDULE = ((48,F(1,250)),(32,F(3,4000)),(16,F(1,4000)))
MAX_LABEL_DENOMINATOR = 1_000_000
WEIGHTS = tuple(tuple(F(comb(POOL-r,n-1),comb(POOL,n)) if POOL-r>=n-1 else F(0)
                      for r in range(1,POOL+1)) for n in BUDGETS)
CAPS = tuple(row[HEAD]/PROMPTS for row in WEIGHTS)
TAIL_MASS = tuple(sum(row[HEAD:],F(0)) for row in WEIGHTS)


@dataclass(frozen=True)
class Acquisition:
    prompt: int
    rank: int
    loss: F


@dataclass(frozen=True)
class TargetCheck:
    budget: int
    bin_lower: F
    bin_upper: F
    observed: F
    cutoff: F
    passed: bool


@dataclass(frozen=True)
class Checkpoint:
    omitted: int
    alpha: F
    acquired_count: int
    targets: tuple


@dataclass(frozen=True)
class AuditResult:
    certified: bool
    reason: str
    allow_blind: bool
    acquisitions: tuple
    checkpoints: tuple
    error_bound: F
    deterministic_budgets: tuple
    full_risks: tuple | None


def audit(oracle, *, allow_blind=False, randbelow=None):
    """Audit fixed correct labels at prompts 0..31 and ranks 1..64.

    oracle(prompt,rank) is called once per acquired label. Return values
    must be integers or Fractions in [0,1], denominator <=1,000,000. Errors
    propagate without issuing a result. All safe supported tables finish.

    Default randomness uses secrets.randbelow. A supplied randbelow(bound)
    must return independent uniform integers in range(bound) for the
    theorem; runtime checks enforce its type/range, not its distribution.
    """
    if not callable(oracle):
        raise ValueError('oracle must be callable')
    if type(allow_blind) is not bool:
        raise ValueError('allow_blind must be a boolean')
    if randbelow is None:
        randbelow=secrets.randbelow
    if not callable(randbelow):
        raise ValueError('randbelow must be callable')
    acquisitions=[]
    checkpoints=[]
    acquired=[F(0)]*len(BUDGETS)
    deterministic=()
    error_bound=F(1,20) if allow_blind else F(1,200)

    def draw(bound):
        value=randbelow(bound)
        if type(value) is not int or not 0<=value<bound:
            raise ValueError('randbelow returned a noninteger or out-of-range value')
        return value

    def result(certified,reason,full_risks=None):
        return AuditResult(certified,reason,allow_blind,tuple(acquisitions),
                           tuple(checkpoints),error_bound,deterministic,full_risks)

    if allow_blind and draw(199)<9:
        return result(True,'blind')

    def acquire(prompt,rank):
        value=oracle(prompt,rank)
        if isinstance(value,bool) or not isinstance(value,(int,F)):
            raise ValueError('labels must be exact integers or Fractions')
        value=F(value)
        if not 0<=value<=1 or value.denominator>MAX_LABEL_DENOMINATOR:
            raise ValueError('label outside [0,1] or denominator above 1,000,000')
        acquisitions.append(Acquisition(prompt,rank,value))
        for index,row in enumerate(WEIGHTS):
            acquired[index]+=row[rank-1]*value/PROMPTS

    for prompt in range(PROMPTS):
        for rank in range(1,HEAD+1):
            acquire(prompt,rank)
    head=tuple(acquired)
    deterministic=tuple(n for index,n in enumerate(BUDGETS)
                        if head[index]+TAIL_MASS[index]<=TAU)
    remaining=[(p,r) for p in range(PROMPTS) for r in range(HEAD+1,POOL+1)]

    def census():
        for prompt,rank in remaining:
            acquire(prompt,rank)
        full=tuple(acquired)
        safe=all(risk<=TAU for risk in full)
        return result(safe,'census_safe' if safe else 'census_unsafe',full)

    bins={}
    for index,n in enumerate(BUDGETS):
        if n in deterministic:
            continue
        if n not in (1,2,4):
            return census()
        cap=CAPS[index]
        gap=EPSILON/cap
        statistic=(TAU-head[index])/cap
        top=min(TAU/cap,F(TAIL_SIZE))
        if not gap<=statistic<=top:
            return census()
        bins[index]=head_bin(statistic,gap,top)

    for omitted,alpha in SCHEDULE:
        while len(remaining)>omitted:
            index=draw(len(remaining))
            remaining[index],remaining[-1]=remaining[-1],remaining[index]
            acquire(*remaining.pop())
        targets=[]
        for index,(lower,upper) in bins.items():
            cutoff=lower_shortfall(extremal_law(TAIL_SIZE,omitted,lower),alpha)
            observed=(acquired[index]-head[index])/CAPS[index]
            targets.append(TargetCheck(BUDGETS[index],lower,upper,observed,
                                       cutoff,observed<cutoff))
        checkpoints.append(Checkpoint(omitted,alpha,len(acquisitions),tuple(targets)))
        if all(target.passed for target in targets) and all(risk<=TAU for risk in acquired):
            return result(True,'checkpoint')
    return census()
