"""Conservative exact design for a computation-bounded cached likelihood audit.

The mathematical construction is classical likelihood testing with shared
fixed labels and a charged prefix fallback. This bounded rational reference
implements the scope described in docs/cached-reference-numerics.md.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb, isqrt

MAX_POOL_SIZE = 1024
MAX_ITEMS = 100000
MAX_RANK_TARGET_PAIRS = 250000
MAX_TOTAL_PROPOSALS = 2000000
MAX_PARAMETER_BITS = 64
MAX_LOG_BITS = 320
MAX_INTERMEDIATE_BITS = 131072
MAX_LOSS_DENOMINATOR = 1000000


def _integer(value, name, maximum, minimum=1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{name} must be an integer in [{minimum},{maximum}]')
    return value


def _fraction(value, name, bits=MAX_INTERMEDIATE_BITS):
    if isinstance(value,bool) or not isinstance(value,(int,F)):
        raise ValueError(name+' must be an exact integer or Fraction')
    result=F(value)
    if max(abs(result.numerator).bit_length(),result.denominator.bit_length()) > bits:
        raise ValueError(name+' exceeds the rational bit limit')
    return result


def _ceil(value):
    return -((-value.numerator)//value.denominator)


def _atanh_log(z, terms):
    power,total,square=z,F(0),z*z
    for j in range(terms):
        total += power/(2*j+1)
        power *= square
        _fraction(power,'log intermediate')
        _fraction(total,'log intermediate')
    lower=2*total
    return lower,lower+2*power/((2*terms+1)*(1-square))


def log_interval(value, bits=96):
    """Enclose log(value) with rational width <= 2**(-bits), without floats."""
    value=_fraction(value,'log argument',4096)
    _integer(bits,'log precision',MAX_LOG_BITS,16)
    if value <= 0:
        raise ValueError('log argument must be positive')
    if value == 1:
        return F(0),F(0)
    if value < 1:
        lower,upper=log_interval(1/value,bits)
        return -upper,-lower
    k=value.numerator.bit_length()-value.denominator.bit_length()
    if value.numerator < value.denominator << k:
        k-=1
    y=value/F(1 << k)
    terms=(bits+(k+1).bit_length()+8+2)//3
    lo2,hi2=_atanh_log(F(1,3),terms)
    loy,hiy=_atanh_log((y-1)/(y+1),terms)
    lower,upper=k*lo2+loy,k*hi2+hiy
    scale=1 << (bits+2)
    lower=F((lower.numerator*scale)//lower.denominator,scale)
    upper=F(_ceil(upper*scale),scale)
    if not 0 <= upper-lower <= F(1,1 << bits):
        raise RuntimeError('log enclosure failed its width check')
    return lower,upper


def sqrt_upper(value, bits=96):
    """Smallest upper square-root enclosure on the dyadic grid 2**(-bits)."""
    value=_fraction(value,'square-root argument',4096)
    _integer(bits,'square-root precision',MAX_LOG_BITS,16)
    if value < 0:
        raise ValueError('square-root argument must be nonnegative')
    scaled=value.numerator << (2*bits)
    integer=isqrt(scaled//value.denominator)
    if integer*integer*value.denominator < scaled:
        integer+=1
    return F(integer,1 << bits)


@dataclass(frozen=True)
class CachedDesign:
    prompts: int
    pool_size: int
    budgets: tuple
    tau: F
    epsilon: F
    delta: F
    eta: F
    theta: F
    winner_weights: tuple
    rank_cumulative_masses: tuple
    rank_mass_denominators: tuple
    log_scale: int
    log_threshold: int
    zero_increment: int
    one_increment: int
    proposal_cap: int
    mode: str
    prefix_cutoff: int
    expected_proposals: F
    statistical_label_bound: F
    expected_label_bound: F
    factor_guarantee: str | None


def design(prompts, pool_size, budgets, tau, epsilon, delta, eta=F(1)):
    """Build an immutable design, rejecting excessive work before any labels.

    Generic validity requires 0<epsilon<tau<1 and 0<delta<1. The optional
    factor label additionally requires the v0.13 range and separated grid.
    A prefix design executes no likelihood proposals. A chosen likelihood
    design exceeding the proposal cap is rejected, never silently replaced
    by a more expensive design with an understated bound.
    """
    prompts=_integer(prompts,'prompt count',MAX_ITEMS)
    m=_integer(pool_size,'pool size',MAX_POOL_SIZE)
    if prompts*m > MAX_ITEMS:
        raise ValueError('total items exceed the resource limit')
    if not isinstance(budgets,(tuple,list)) or not budgets or len(budgets)>m:
        raise ValueError('budgets must be a bounded nonempty tuple or list')
    grid=tuple(_integer(n,'budget',m) for n in budgets)
    if len(set(grid)) != len(grid):
        raise ValueError('budgets must be distinct')
    grid=tuple(sorted(grid))
    if m*len(grid)>MAX_RANK_TARGET_PAIRS:
        raise ValueError('rank-target work exceeds the resource limit')
    tau,epsilon,delta,eta=(_fraction(x,name,MAX_PARAMETER_BITS) for x,name in
        ((tau,'tau'),(epsilon,'epsilon'),(delta,'delta'),(eta,'eta')))
    if not 0 < epsilon < tau < 1 or not 0 < delta < 1 or eta <= 0:
        raise ValueError('requires 0<epsilon<tau<1, 0<delta<1, and eta>0')
    theta=tau-epsilon
    factor_scope=(tau<=F(1,8) and epsilon<=tau/16 and delta<=F(1,4)
                  and all(b>=2*a for a,b in zip(grid,grid[1:])))

    # Refinement is bounded. All checks refer to the implemented lower walk.
    for bits in range(32,257,32):
        scale=1 << bits
        u_lo,u_hi=log_interval((1-theta)/(1-tau),bits+16)
        v_lo,v_hi=log_interval(tau/theta,bits+16)
        l_lo,l_hi=log_interval(1/delta,bits+16)
        up=(u_lo.numerator*scale)//u_lo.denominator
        down=-_ceil(v_hi*scale)
        threshold=_ceil(l_hi*scale)
        drift=(1-theta)*up+theta*down
        if up<=0 or down>=0 or threshold<=0 or drift<=0:
            continue
        c=F(threshold+up)/drift
        if factor_scope and c>F(17,8)*tau*l_lo/epsilon**2:
            continue
        inflation=1/(1-F(1,scale))
        phi=(sqrt_upper(theta*tau,bits)+sqrt_upper((1-theta)*(1-tau),bits))*inflation
        a0=sqrt_upper(1/delta,bits)*inflation
        if phi>=1:
            continue
        if (u_hi-F(up,scale)>F(2,scale) or -v_lo-F(down,scale)>F(2,scale)
                or F(threshold,scale)-l_lo>F(2,scale)):
            raise RuntimeError('rounded likelihood error exceeded its bound')
        break
    else:
        raise ValueError('likelihood design exceeds the refinement limit')

    rows,cumulative,denominators=[],[],[]
    for n in grid:
        denominator=comb(m,n)
        counts=[comb(m-r-1,n-1) if m-r>=n else 0 for r in range(m)]
        running=0
        totals=[]
        for count in counts:
            running+=count
            totals.append(running)
        if running!=denominator:
            raise RuntimeError('winner mass identity failed')
        denominators.append(denominator)
        cumulative.append(tuple(totals))
        rows.append(tuple(F(count,denominator) for count in counts))
    remaining=F(1)
    cutoff=0
    while remaining>epsilon:
        remaining-=rows[0][cutoff]
        cutoff+=1
    prefix=prompts*cutoff
    statistical=sum((min(F(prompts),c*sum(column,F(0))) for column in zip(*rows)),F(0))
    mode='prefix' if prefix<=statistical+eta else 'likelihood'
    cap=0
    bound=F(prefix)
    if mode=='likelihood':
        log_r_hi=log_interval(prefix*len(grid)*a0/eta,bits+16)[1]
        log_phi_hi=log_interval(phi,bits+16)[1]
        if log_phi_hi>=0:
            raise RuntimeError('proposal-tail contraction was not certified')
        cap=max(1,_ceil(log_r_hi/(-log_phi_hi)))
        if log_r_hi+cap*log_phi_hi>0:
            raise RuntimeError('proposal cap inequality failed')
        if cap*len(grid)>MAX_TOTAL_PROPOSALS:
            raise ValueError('likelihood proposal count exceeds the resource limit')
        bound=statistical+eta
    return CachedDesign(prompts,m,grid,tau,epsilon,delta,eta,theta,tuple(rows),
        tuple(cumulative),tuple(denominators),scale,threshold,up,down,cap,mode,
        cutoff,c,statistical,bound,'17F + eta' if factor_scope else None)
