"""Reproducible exact support for the attributed budget-coverage note."""
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

from goodhart_audit import coverage

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT/'experiments/grid_coverage_protocol.json'
SOURCE_PATHS = (
    'goodhart_audit/coverage.py', 'tests/test_coverage.py',
    'experiments/check_grid_coverage.py', 'tests/test_grid_coverage.py',
    'experiments/grid_coverage_protocol.json', 'docs/grid-coverage.md',
)
PROTOCOL = {
    'version': 1,
    'title': 'Exact deterministic coverage between finite best-of-n budgets',
    'status': 'Specified after exploratory derivation and floating LP screens, before the saved exhaustive run; not external preregistration',
    'evidence_type': 'exact_arithmetic_and_synthetic_witnesses_not_model_data',
    'pascal_max_pool': 64, 'chord_max_pool': 24, 'binary_subset_max_pool': 8,
    'shortest_path_max_pool': 96,
    'grid_levels': [['0','0'],['1/10','1/10'],['3/32','1/10'],['1/16','1/8']],
    'profile_pools': [64,128,1024,100000],
    'original_pool': 64, 'original_prompts': 32,
    'original_grid': [1,2,4,8,16,32,64],
    'certified_level': '3/32', 'target_level': '1/10',
    'fractional_witness': {'rank_1_mean':'3/32','rank_2_mean':'189/1024','other_means':'0'},
    'binary_witness': {'positive_rank_1_prompts':3,'positive_rank_2_prompts':5,'other_labels':0},
    'source_pins': 6,
    'claim_boundary': 'Attributed convexity application; exact integer interpolation and witnesses. Grid minimality only under the displayed sufficient rule. No label-cost improvement, new generic convexity, actual-model evidence, automatic full-family auditor completeness, scientific priority, or fellowship outcome.',
}


def require(condition, message):
    if not condition:
        raise RuntimeError('grid coverage check failed: '+message)


def _exact_json(value):
    if isinstance(value,F):
        return str(value)
    if type(value) in (int,str,bool) or value is None:
        return value
    if isinstance(value,(tuple,list)):
        return [_exact_json(x) for x in value]
    if isinstance(value,dict) and all(type(key) is str for key in value):
        return {key:_exact_json(x) for key,x in value.items()}
    raise TypeError('evidence must contain exact rational values, not '+type(value).__name__)


def encode(value):
    return (json.dumps(_exact_json(value),sort_keys=True,indent=2)+'\n').encode('utf-8')


def _unique_object(pairs):
    obj={}
    for key,value in pairs:
        if key in obj:
            raise ValueError('duplicate protocol key')
        obj[key]=value
    return obj


def read_protocol(path):
    with Path(path).open('rb') as source:
        data=source.read(16385)
    if len(data)>16384:
        raise ValueError('protocol exceeds size cap')
    obj=json.loads(data,object_pairs_hook=_unique_object)
    try:
        canonical=encode(obj)
    except TypeError as error:
        raise ValueError('protocol contains nonexact values') from error
    if canonical != encode(PROTOCOL):
        raise ValueError('only the fixed canonical protocol is supported')
    return obj


def source_snapshot():
    paths={name:ROOT/name for name in SOURCE_PATHS}
    paths['goodhart_audit/coverage.py']=Path(coverage.__file__).resolve()
    return {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in paths.items()}


@lru_cache(maxsize=None)
def weights(m,n):
    return tuple(F(comb(m-r,n-1),comb(m,n)) if m-r>=n-1 else F(0)
                 for r in range(1,m+1))


def _curve(means):
    m=len(means)
    return [sum((a*y for a,y in zip(weights(m,n),means)),F(0)) for n in range(1,m+1)]


def original_witnesses():
    m,p=PROTOCOL['original_pool'],PROTOCOL['original_prompts']
    binary_table=[[int((r==0 and prompt<3) or (r==1 and prompt<5))
                   for r in range(m)] for prompt in range(p)]
    means=[sum(F(row[r],p) for row in binary_table) for r in range(m)]
    output={}
    for name,values in (('fractional',[F(3,32),F(189,1024)]+[F(0)]*62),('binary',means)):
        curve=_curve(values)
        maximum=max(curve)
        grid_risks=[curve[n-1] for n in PROTOCOL['original_grid']]
        require(max(grid_risks)<=F(3,32),'witness declared-grid premise')
        require(maximum>F(1,10),'witness omitted-budget violation')
        output[name]={'rank_means':values,'risk_curve':curve,'grid_risks':grid_risks,
                      'max_grid_risk':max(grid_risks),'max_full_risk':maximum,
                      'maximizers':[i+1 for i,x in enumerate(curve) if x==maximum]}
    output['binary']['positive_cells']=sum(map(sum,binary_table))
    require(output['fractional']['max_full_risk']==F(27,256),'sharp fractional maximum')
    require(output['binary']['max_full_risk']==F(2159,21504),'binary maximum')
    return output


def compute():
    counts={'pascal_identities':0,'coordinate_chords':0,'binary_tables':0,
            'binary_chords':0,'grid_shortest_paths':0,'shortest_path_edges':0}
    for m in range(3,PROTOCOL['pascal_max_pool']+1):
        for n in range(1,m-1):
            for r in range(1,m+1):
                actual=weights(m,n)[r-1]/n-2*weights(m,n+1)[r-1]/(n+1)+weights(m,n+2)[r-1]/(n+2)
                numerator=comb(m-n-2,r-3) if 0<=r-3<=m-n-2 else 0
                expected=F(numerator,m*comb(m-1,r-1))
                require(actual==expected>=0,'Pascal identity')
                counts['pascal_identities']+=1
    for m in range(3,PROTOCOL['chord_max_pool']+1):
        for a,n,b in itertools.combinations(range(1,m+1),3):
            for r in range(m):
                upper=coverage.interpolate_upper(a,b,n,weights(m,a)[r],weights(m,b)[r])
                require(weights(m,n)[r]<=upper,'coordinate chord')
                counts['coordinate_chords']+=1
    for m in range(1,PROTOCOL['binary_subset_max_pool']+1):
        subsets={n:tuple(itertools.combinations(range(m),n)) for n in range(1,m+1)}
        for table in itertools.product((0,1),repeat=m):
            curve={n:F(sum(table[min(indices)] for indices in samples),len(samples))
                   for n,samples in subsets.items()}
            counts['binary_tables']+=1
            for a,n,b in itertools.combinations(range(1,m+1),3):
                require(curve[n]<=coverage.interpolate_upper(a,b,n,curve[a],curve[b]),'subset chord')
                counts['binary_chords']+=1
    limit=PROTOCOL['shortest_path_max_pool']
    for s_string,tau_string in PROTOCOL['grid_levels']:
        s,tau=F(s_string),F(tau_string)
        shortest=[0]*(limit+1)
        shortest[1]=1
        for b in range(2,limit+1):
            candidates=[]
            for a in range(1,b):
                counts['shortest_path_edges']+=1
                if all(s*F(n*(a+b-n),a*b)<=tau for n in range(a,b+1)):
                    candidates.append(shortest[a]+1)
            shortest[b]=min(candidates)
        for m in range(1,limit+1):
            grid=coverage.covering_grid(m,s,tau)
            require(len(grid)==shortest[m],'greedy versus shortest path')
            counts['grid_shortest_paths']+=1
    profiles=[]
    for m in PROTOCOL['profile_pools']:
        grid=coverage.covering_grid(m,F(3,32),F(1,10))
        factors=[coverage.interval_factor(a,b) for a,b in zip(grid,grid[1:])]
        require(max(factors)*F(3,32)<=F(1,10),'profile coverage')
        profiles.append({'pool_size':m,'grid':grid,'grid_size':len(grid),
                         'interval_factors':factors,'full_risk_bound':max(factors)*F(3,32)})
    return {'counts':counts,'original_witnesses':original_witnesses(),'grid_profiles':profiles}


def run(out, protocol_path=DEFAULT_PROTOCOL):
    out=Path(out)
    if out.exists():
        raise FileExistsError(out)
    protocol=read_protocol(protocol_path)
    before=source_snapshot()
    result=compute()
    require(source_snapshot()==before,'source drift during run')
    result.update({'protocol':protocol,'source_sha256':before})
    data=encode(result)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as target:
        target.write(data)
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'counts':result.get('counts',{})}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.out),sort_keys=True))
