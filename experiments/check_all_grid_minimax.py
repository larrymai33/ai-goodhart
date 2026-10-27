"""Bounded exact support for the all-grid finite minimax proof.

No model labels or actual P*m tables are allocated. Finite arithmetic checks
do not establish a universal theorem, scientific priority, or model usefulness.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sys

from experiments import check_sharp_cost as exact_helper

exact_weights, log_interval = exact_helper.exact_weights, exact_helper.log_interval

ROOT = Path(__file__).resolve().parents[1]
IMPORTED_HELPER_PATH = Path(exact_helper.__file__).resolve()
MAX_PROTOCOL_BYTES = 16384
MAX_POOL = 128
MAX_PROMPTS = 2**40
SOURCE_PATHS = (
    'experiments/check_all_grid_minimax.py', 'tests/test_all_grid_minimax.py',
    'experiments/all_grid_minimax_protocol.json', 'docs/all-grid-minimax-theorem.md',
    'docs/cached-likelihood-audit.md', 'docs/finite-saturation-theorem.md',
    'docs/finite-density-theorem.md', 'docs/nonzero-minimax-theorem.md',
    'experiments/check_sharp_cost.py',
)
CANONICAL_PROTOCOL = {
    'version': 1,
    'title': 'Universal finite-grid minimax geometry and cached likelihood cost',
    'status': 'Fixed after exploratory proof derivation and targeted checks, before the saved full matrix; not external preregistration',
    'evidence_type': 'deterministic_exact_rational_checks_not_model_measurements',
    'theorem': {'lower_factor': 2**38, 'upper_factor': 2**16,
                'separated_grid_upper_factor': 17, 'separation': 2,
                'tau_max': '1/8', 'relative_margin_max': '1/16', 'delta_max': '1/4',
                'scope': 'Every finite nonempty declared BoN grid; fixed fractional losses; global whole-family validity; all-safe almost-sure completeness; worst expected distinct-label cost over the supplied-margin class'},
    'grid_max_pool': 10,
    'grid_matrix': 'Every nonempty subset of {1,...,m}, m=1..10',
    'larger_pools': [16, 32, 64, 128],
    'larger_grid_matrix': 'Every singleton, the full grid, the dyadic grid, the interval {floor(m/4),...,m}, and {1,m},{1,max(1,m//3),m},{max(1,m//8),m}; deduplicate within each pool',
    'prompts': [1, 64, 1048576], 'tau': '1/8', 'relative_margins': ['1/16', '1/64'],
    'log_inverse_deltas': ['3/2', '12'],
    'log_interpretation': 'These exact rational L values correspond to delta=exp(-L); no rounded delta is substituted. All are at least log(4).',
    'mixture_max_pool': 32,
    'mixture_matrix': 'All nonempty factor-2 and factor-4 separated subsets through pool size32, at every rank; include zero support and rank one',
    'conditional_identity_max_pool': 128,
    'conditional_identity_matrix': 'Every m=5..128 and 1<=a<m/4, all conditional ranks, using k0=floor(m/(a+1))',
    'slice_max_population': 256, 'slice_taus': ['1/8', '1/32'],
    'slice_tail_masses': ['1/4', '1/2', '1'],
    'slice_matrix': 'N=3..256, both taus and relative margins, both L values, each q, and distinct s in {8epsilon,16epsilon,1/4,1/2,1} with 8epsilon<=s<=q',
    'original_profile': {'prompts': 32, 'pool_size': 64, 'budgets': [1,2,4,8,16,32,64],
                         'tau': '1/10', 'epsilon': '1/160', 'delta': '1/20'},
    'maximum_pool': MAX_POOL, 'maximum_prompts': MAX_PROMPTS,
    'maximum_rational_input_bits': 256,
    'maximum_derived_scale_bits': 1024,
    'source_pins': 9,
    'claim_boundary': 'Finite checks support implementation and proof arithmetic, not the universal quantifiers by themselves. Constants are loose. No new production audit CLI, measured efficiency, new generic likelihood-ratio method, scientific priority, human verification, or fellowship outcome is claimed.',
}


def require(condition, message):
    if not condition:
        raise RuntimeError('all-grid exact check failed: '+message)


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low},{high}]')
    return value


def fraction(value, name, max_bits=256):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name+' must be an exact integer or Fraction')
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > max_bits:
        raise ValueError(name+' exceeds the rational input cap')
    return value


def parameters(tau, epsilon, log_inverse):
    tau, epsilon, log_inverse = (fraction(tau, 'tau'), fraction(epsilon, 'epsilon'),
                                 fraction(log_inverse, 'log inverse delta'))
    if not 0 < tau <= F(1,8) or not 0 < epsilon <= tau/16 or log_inverse < F(3,2):
        raise ValueError('requires tau<=1/8, epsilon<=tau/16, and rational L>=3/2')
    return tau, epsilon, log_inverse


def grid_tuple(budgets, maximum=MAX_POOL):
    if not isinstance(budgets, (tuple, list)) or not budgets:
        raise ValueError('budgets must be a nonempty tuple or list')
    values = tuple(integer(n, 'budget', 1, maximum) for n in budgets)
    if tuple(sorted(set(values))) != values:
        raise ValueError('budgets must be strictly increasing and distinct')
    return values


def representatives(budgets, factor=4):
    budgets = grid_tuple(budgets)
    if type(factor) is not int or factor not in (2,4):
        raise ValueError('representative factor must be 2 or 4')
    result = []
    for n in budgets:
        if not result or n >= factor*result[-1]:
            result.append(n)
    return tuple(result)


def tail_cutoff(weights, epsilon):
    remaining = sum(weights, F(0))
    for k in range(len(weights)+1):
        if remaining <= epsilon:
            return k
        remaining -= weights[k]
    raise RuntimeError('tail cutoff missing')


def mixture_check(m, budgets, rank, factor=4):
    integer(m, 'pool size', 1, MAX_POOL)
    integer(rank, 'rank', 1, m)
    budgets = grid_tuple(budgets, m)
    if type(factor) is not int or factor not in (2,4) or any(b < factor*a for a,b in zip(budgets,budgets[1:])):
        raise ValueError('requires the stated separated grid')
    values = tuple(exact_weights(m,n)[rank-1] for n in budgets)
    total, maximum = sum(values,F(0)), max(values)
    constant = F(14,3) if factor == 4 else F(8)
    require(total <= constant*maximum, 'pointwise geometric-mixture bound')
    return {'sum':total, 'maximum':maximum, 'ratio':total/maximum if maximum else F(0)}


@lru_cache(maxsize=256,typed=True)
def conditional_tail_geometry(m, budget, prompts, epsilon, scale):
    integer(m, 'pool size', 1, MAX_POOL)
    integer(budget, 'smallest budget', 2, m)
    integer(prompts, 'prompts', 1, MAX_PROMPTS)
    epsilon, scale = fraction(epsilon,'epsilon'), fraction(scale,'derived scale',1024)
    if not budget < F(m,4) or not 0 < epsilon <= F(1,128) or scale <= 0:
        raise ValueError('conditional geometry requires 2<=a<m/4, epsilon<=1/128, H>0')
    head = m//(budget+1)
    remaining = m-head
    original, v = exact_weights(m,budget), exact_weights(remaining,budget)
    q = sum(original[head:],F(0))
    require(q >= F(1,4), 'domination tail mass')
    require(original[head:] == tuple(q*x for x in v), 'exact conditional BoN law')
    ell = remaining//budget
    support = remaining-budget+1
    half = (support+1)//2
    blocks = half//ell
    require(ell >= 3 and blocks >= 1 and half <= F(remaining,2), 'conditional block endpoints')
    mass = tuple(ell*v[j*ell-1] for j in range(1,blocks+1))
    require(mass[0] >= F(1,4), 'first conditional block mass')
    require(all(b <= F(8,11)*a for a,b in zip(mass,mass[1:])), 'block endpoint decay')
    for j in range(1,blocks+1):
        require(all(w <= 27*v[j*ell-1] for w in v[(j-1)*ell:j*ell]), 'within-block comparability')
    for r in range(1,half+1):
        require(v[2*r-2] <= v[r-1]**2/v[0], 'log-concave rank pairing')
    ep, hp, population = epsilon/q, scale*q*q, prompts*ell
    retained = sum(s >= 8*ep for s in mass)
    require(retained >= 1, 'nonempty retained conditional blocks')
    all_cost = sum((min(population,hp*s*s) for s in mass),F(0))
    cost = sum((min(population,hp*s*s) for s in mass[:retained]),F(0))
    clipped = sum((min(prompts,hp*w) for w in v),F(0))
    cutoff = tail_cutoff(v,ep)
    functional = min(prompts*cutoff,clipped)
    require(clipped <= 2048*all_cost, 'paired block sum')
    require(functional <= 8192*cost, 'conditional clipped-or-prefix bound')
    require(all(q*s >= 8*epsilon for s in mass[:retained]), 'original block mass threshold')
    if hp*(8*ep)**2 <= population:
        require(all_cost-cost <= 3*cost, 'small discarded block cost')
    else:
        require(cost == retained*population, 'all retained blocks saturated')
        require(prompts*cutoff <= 7*cost, 'saturated deterministic tail cap')
    return {'head_cutoff':head, 'conditional_pool':remaining, 'tail_mass':q,
            'block_length':ell, 'block_population':population, 'blocks':blocks,
            'retained_blocks':retained, 'minimum_masses':tuple(q*s for s in mass[:retained]),
            'conditional_margin':ep, 'conditional_scale':hp, 'conditional_G':clipped,
            'conditional_prefix':cutoff, 'conditional_F':functional, 'A':cost}


def centered_slice_check(size,tau,epsilon,tail_mass,minimum_mass,log_inverse_delta):
    integer(size,'symbolic block population',3,MAX_POOL*MAX_PROMPTS)
    tau,epsilon,log_inverse_delta = parameters(tau,epsilon,log_inverse_delta)
    q,s = fraction(tail_mass,'tail mass'),fraction(minimum_mass,'minimum mass')
    if not F(1,4) <= q <= 1 or not 8*epsilon <= s <= q:
        raise ValueError('requires q>=1/4 and 8epsilon<=s<=q')
    p0 = (tau-epsilon)/q
    k = (size*tau/8).__floor__()
    d = (2*epsilon*size/s).__floor__()+1
    require(0 <= k < k+d <= F(size,2), 'finite-slice admissible counts')
    require(0 <= p0-F(k,2*size) and p0+F(size-k,2*size) <= 1, 'affine labels lie in [0,1]')
    require(s*d/(2*size) > epsilon, 'every alternative strictly unsafe')
    h = tau*log_inverse_delta/epsilon**2
    information = F(size*(k+1),d*d)*log_inverse_delta
    target = min(size,h*s*s)
    require(min(size,information) >= target/128, 'centered-slice rate comparison')
    return {'population':size,'null_count':k,'added_count':d,'safe_level':p0,
            'risk_increment':s*d/(2*size),'slice_information':information,'target':target}


def family_profile(m,prompts,budgets,tau,epsilon,log_inverse_delta):
    integer(m,'pool size',1,MAX_POOL)
    integer(prompts,'prompts',1,MAX_PROMPTS)
    budgets = grid_tuple(budgets,m)
    tau,epsilon,L = parameters(tau,epsilon,log_inverse_delta)
    rows = tuple(exact_weights(m,n) for n in budgets)
    a, h = budgets[0], tau*L/epsilon**2
    envelope = tuple(map(max,zip(*rows)))
    clipped = sum((min(prompts,h*w) for w in envelope),F(0))
    cutoff = tail_cutoff(rows[0],epsilon)
    functional = min(prompts*cutoff,clipped)
    reps = representatives(budgets)
    broad = tuple(n for n in reps if F(prompts*m,n) >= 32*h)
    residual_prefix = (8*h/prompts).__floor__()
    result = {'pool_size':m,'prompts':prompts,'budgets':budgets,'tau':tau,'epsilon':epsilon,
              'log_inverse_delta':L,'H':h,'G':clipped,'F':functional,'prefix_cutoff':cutoff,
              'representatives':reps,'broad_count':len(broad),'residual_prefix':residual_prefix}
    if broad:
        require(functional <= 37*h*len(broad),'broad-group envelope accounting')
        require(residual_prefix < m,'random suffix exists')
        rho = F(1,prompts*(residual_prefix+1))
        require(rho < 1/(8*h),'residual atom cap')
        require(all(row[residual_prefix]/prompts <= rho for row in rows),'all original residual atoms')
        for n in broad:
            left,right = m//(4*n)+1,m//n
            require(left > residual_prefix,'broad band is entirely in random suffix')
            require(sum(exact_weights(m,n)[left-1:right],F(0)) > F(1,4),'broad band mass')
        branch,lower = 'broad_bands',h*len(broad)/4096
    else:
        singleton_g = sum((min(prompts,h*w) for w in rows[0]),F(0))
        singleton_f = min(prompts*cutoff,singleton_g)
        size_scale = F(prompts*m,a)
        require(singleton_g >= min(size_scale,h) and size_scale < 32*h,'smallest-scale bound')
        require(functional <= 33*singleton_f,'reduction to smallest target')
        if 4*a >= m:
            branch,lower = 'high_budget',functional/2**21
        elif a == 1:
            tail_population = prompts*(m-m//2)
            q = F(m-m//2,m)
            block_cost = min(tail_population,h*q*q)
            require(tail_population >= 3 and q >= F(1,2),'uniform-tail endpoints')
            require(block_cost >= min(prompts*m,h)/4,'uniform-tail cost comparison')
            centered_slice_check(tail_population,tau,epsilon,q,q,L)
            branch,lower = 'uniform_tail',block_cost/2**17
        else:
            tail = conditional_tail_geometry(m,a,prompts,epsilon,h)
            for minimum_mass in tail['minimum_masses']:
                centered_slice_check(tail['block_population'],tau,epsilon,tail['tail_mass'],minimum_mass,L)
            require(cutoff == tail['head_cutoff']+tail['conditional_prefix'],'original and conditional cutoffs')
            require(tail['A'] >= size_scale/8192,'initial tail block pays for head')
            require(singleton_f <= prompts*tail['head_cutoff']+4*tail['conditional_F'],'conditional scaling comparison')
            require(singleton_f <= 40960*tail['A'],'smallest-target functional comparison')
            require(functional <= 1351680*tail['A'],'all-grid saturated accounting')
            branch,lower = 'tail_blocks',tail['A']/2**17
            result['conditional_tail'] = tail
    separated = all(b >= 2*a for a,b in zip(budgets,budgets[1:]))
    upper = min(prompts*cutoff,(17 if separated else 61440)*clipped)
    require(lower >= functional/2**38 and upper <= 2**16*functional,'universal theorem constants')
    result.update(lower_branch=branch,proved_lower=lower,proved_upper=upper,
                  separated_grid=separated, universal_lower=functional/2**38,
                  interpretation='Exact values of proof functionals and conservative theorem bounds, not measured query costs or exact minimax values')
    return result


def likelihood_checks():
    count = comparison = 0
    for tau in (F(1,8),F(1,32)):
        for relative in (F(1,16),F(1,64)):
            epsilon,p = tau*relative,tau*(1-relative)
            one,zero = p/tau,(1-p)/(1-tau)
            require(0 < one < 1 < zero,'positive-error likelihood multipliers')
            for risk in (F(0),p,tau,(1+tau)/2,F(1)):
                expectation = risk*one+(1-risk)*zero
                require((expectation <= 1) == (risk >= tau),'exact composite-null multiplier expectation')
                count += 1
            # Since log(one)<log(zero), expected log gain decreases with risk.
            require(one < zero,'safe-side log drift monotonicity')
            for L in (F(3,2),F(12)):
                h = tau*L/epsilon**2
                coefficient_bound = (L+epsilon/(1-tau))/(epsilon**2/(2*tau))
                require(coefficient_bound <= F(17,8)*h,'conservative expected-proposal coefficient')
                comparison += 1
    return {'multiplier_checks':count,'proposal_coefficient_checks':comparison,
            'interpretation':'Multiplier expectations and rational coefficient comparisons; the stopped-process and caching conclusions require the companion proof'}


def json_value(value):
    if isinstance(value,F):
        return str(value)
    if isinstance(value,dict):
        return {str(k):json_value(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [json_value(v) for v in value]
    return value


def canonical(value):
    try:
        return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    except (TypeError,ValueError,RecursionError,UnicodeError) as error:
        raise ValueError('invalid bounded protocol values') from error


def parse_protocol(data):
    if len(data) > MAX_PROTOCOL_BYTES:
        raise ValueError('protocol exceeds 16 KiB')
    def unique(pairs):
        out = {}
        for key,value in pairs:
            if key in out:
                raise ValueError('duplicate protocol key: '+key)
            out[key] = value
        return out
    def invalid(value):
        raise ValueError('invalid protocol constant: '+value)
    try:
        return json.loads(data,object_pairs_hook=unique,parse_constant=invalid)
    except (UnicodeError,RecursionError) as error:
        raise ValueError('invalid protocol JSON') from error


def validate_protocol(protocol):
    if canonical(protocol) != canonical(CANONICAL_PROTOCOL):
        raise ValueError('protocol differs from the canonical frozen matrix')
    return protocol


def separated_grids(m,factor,start=1,prefix=()):
    for n in range(start,m+1):
        grid = prefix+(n,)
        yield grid
        yield from separated_grids(m,factor,factor*n,grid)


def larger_grids(m):
    values = {(n,) for n in range(1,m+1)}
    values.update((tuple(range(1,m+1)), tuple(2**j for j in range(m.bit_length()) if 2**j<=m),
                   tuple(range(m//4,m+1)),(1,m),tuple(sorted({1,max(1,m//3),m})),(max(1,m//8),m)))
    return sorted(values)


def calculate(protocol):
    validate_protocol(protocol)
    digest = hashlib.sha256()
    def record(kind,value):
        data = canonical(json_value(value))
        digest.update(kind.encode('ascii')+len(data).to_bytes(8,'big')+data)
    grid_count = profile_count = 0
    branches = Counter()
    largest_ratio = F(0)
    configurations = itertools.product(protocol['prompts'],protocol['relative_margins'],protocol['log_inverse_deltas'])
    configurations = tuple(configurations)
    family_sets = [(m,[tuple(n for n in range(1,m+1) if mask & (1 << (n-1)))
                       for mask in range(1,1 << m)]) for m in range(1,protocol['grid_max_pool']+1)]
    family_sets += [(m,larger_grids(m)) for m in protocol['larger_pools']]
    for m,grids in family_sets:
        for grid in grids:
            grid_count += 1
            for prompts,relative,L in configurations:
                tau = F(protocol['tau'])
                row = family_profile(m,prompts,grid,tau,tau*F(relative),F(L))
                record('profile',row)
                branches[row['lower_branch']] += 1
                largest_ratio = max(largest_ratio,row['F']/row['proved_lower'])
                profile_count += 1
    require(set(branches) == {'broad_bands','high_budget','uniform_tail','tail_blocks'},'all lower-proof branches exercised')
    mixture_counts,mixture_maxima = {},{}
    for factor in (2,4):
        count,maximum = 0,F(0)
        for m in range(1,protocol['mixture_max_pool']+1):
            for grid in separated_grids(m,factor):
                for rank in range(1,m+1):
                    row = mixture_check(m,grid,rank,factor)
                    record('mixture',(m,grid,rank,factor,row))
                    maximum = max(maximum,row['ratio'])
                    count += 1
        mixture_counts[str(factor)],mixture_maxima[str(factor)] = count,maximum
    identities = 0
    for m in range(5,protocol['conditional_identity_max_pool']+1):
        for a in range(1,(m-1)//4+1):
            head = m//(a+1)
            weights = exact_weights(m,a)
            q = sum(weights[head:],F(0))
            require(q >= F(1,4),'conditional identity tail mass')
            for r,w in enumerate(exact_weights(m-head,a),start=1):
                require(weights[head+r-1] == q*w,'conditional rank identity')
                identities += 1
            record('conditional_identity',(m,a,head,q))
    slices = 0
    for size in range(3,protocol['slice_max_population']+1):
        for tau_s,relative,q_s,L_s in itertools.product(protocol['slice_taus'],protocol['relative_margins'],
                                                       protocol['slice_tail_masses'],protocol['log_inverse_deltas']):
            tau,q,L = F(tau_s),F(q_s),F(L_s)
            epsilon = tau*F(relative)
            for s in sorted({8*epsilon,16*epsilon,F(1,4),F(1,2),F(1)}):
                if s <= q:
                    row = centered_slice_check(size,tau,epsilon,q,s,L)
                    record('centered_slice',(tau,epsilon,q,s,L,row))
                    slices += 1
    likelihood = likelihood_checks()
    record('likelihood',likelihood)
    examples = []
    for m,prompts,grid in ((8,1,(2,8)),(9,1,(2,9)),(16,2**20,(1,2,4,8,16)),
                           (128,1,(1,128)),(128,1,(8,128)),(128,2**20,(1,7,64,128))):
        examples.append(family_profile(m,prompts,grid,F(1,8),F(1,128),F(3,2)))
    original = protocol['original_profile']
    low,high = log_interval(F(original['delta']))
    originals = [family_profile(original['pool_size'],original['prompts'],tuple(original['budgets']),
                               F(original['tau']),F(original['epsilon']),L) for L in (low,high)]
    require(originals[0]['F'] == originals[1]['F'] == 2048,'original F exact at both rigorous log endpoints')
    return json_value({'finite_matrix':{'distinct_grids':grid_count,'family_configurations':profile_count,
                        'lower_branch_counts':dict(sorted(branches.items())),
                        'largest_checked_F_to_proved_lower':largest_ratio,
                        'mixture_rank_checks':mixture_counts,'largest_mixture_ratios':mixture_maxima,
                        'conditional_rank_identities':identities,'centered_slice_configurations':slices},
                       'likelihood_checks':likelihood,'matrix_sha256':digest.hexdigest(),
                       'illustrative_profiles':examples,'original_log_interval':(low,high),
                       'original_profiles_at_log_endpoints':originals,
                       'interpretation':'The finite matrix and checksums support the implementation. Proofs supply universal quantifiers; theorem constants remain loose.'})


def build_results(protocol,protocol_path):
    path = Path(protocol_path).resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError('protocol exceeds 16 KiB')
    with path.open('rb') as stream:
        raw = stream.read(MAX_PROTOCOL_BYTES+1)
    snapshot = validate_protocol(parse_protocol(raw))
    if protocol is not None and canonical(protocol) != canonical(snapshot):
        raise ValueError('protocol differs from the file snapshot')
    source_files = [ROOT/name for name in SOURCE_PATHS]
    source_files[2],source_files[-1] = path,IMPORTED_HELPER_PATH
    def key(source):
        source=source.resolve()
        return source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else str(source)
    files=[(key(source),source) for source in source_files]
    hashes = {name:hashlib.sha256(raw if source==path else source.read_bytes()).hexdigest() for name,source in files}
    require(len(hashes)==9,'nine distinct scientific source pins')
    result = {'schema_version':1,'description':__doc__,'dependencies':'Python standard library only',
              'protocol':snapshot,'protocol_sha256':hashlib.sha256(raw).hexdigest(),
              'source_sha256':hashes,**calculate(snapshot),'claim_boundary':snapshot['claim_boundary']}
    for name,source in files:
        if source==path:
            with source.open('rb') as stream:
                data=stream.read(MAX_PROTOCOL_BYTES+1)
        else:
            data=source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=hashes[name]:
            raise RuntimeError('a pinned source changed during calculation: '+name)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,default=ROOT/'experiments/all_grid_minimax_protocol.json')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.out.exists():
            raise ValueError('output already exists; choose a fresh path')
        result=build_results(None,args.protocol)
        encoded=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(encoded)
    except (ValueError,RuntimeError,OSError) as error:
        print('all-grid checks: '+str(error),file=sys.stderr)
        return 2
    print('Passed the registered all-grid exact matrix; saved '+str(args.out)+'.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
