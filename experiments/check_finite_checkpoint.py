"""Exact finite-checkpoint certificate, independent checks, and reference traces."""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from fractions import Fraction as F
import hashlib
from itertools import combinations, combinations_with_replacement
import json
from math import comb
from pathlib import Path
import random
import sys

from goodhart_audit import checkpoint as reference
from goodhart_audit import checkpoint_math as arithmetic

ROOT = Path(__file__).resolve().parents[1]
MAX_PROTOCOL_BYTES = 16384
CANONICAL_PROTOCOL = {
    'version': 1,
    'title': 'Exact scheduled finite-population upper certificate for the original audit decision',
    'status': 'Fixed after exploratory mathematics and schedule searches, before the saved full calculation; not external preregistration',
    'geometry': {'prompts':32, 'pool_size':64, 'head_ranks':32, 'suffix_population':1024,
                 'budgets':[1,2,4,8,16,32,64], 'tau':'1/10', 'epsilon':'1/160', 'margin_threshold':'3/32'},
    'head_order': 'Prompt-major: prompts 0 through 31, then ranks 1 through 32 within each prompt; all 1024 acquired labels are charged',
    'suffix_order': 'One prospective uniform permutation, implemented by uniform swap-pop draws from prompt-major suffix identities; checkpoints use nested prefixes',
    'statistical_budgets': [1,2,4],
    'schedule': [{'omitted':48,'alpha':'1/250'}, {'omitted':32,'alpha':'3/4000'}, {'omitted':16,'alpha':'1/4000'}],
    'bin_width': '1',
    'bin_rule': 'Intervals [g+i,min(g+i+1,top)) with the final right endpoint included; g=epsilon/c and top=min(tau/c,1024); use lower endpoint for the cutoff and upper endpoint minus g for margin nonpass',
    'pass_rule': 'Strict observed normalized suffix sum < lower alpha expected shortfall; every target passes at the same checkpoint, and acquired risk cannot exceed tau',
    'deterministic_rule': 'Check the actual acquired head h plus full unobserved suffix weight q <= tau for every target',
    'fallback_rule': 'An unresolved target outside budgets 1,2,4 or outside its registered head range goes to census; otherwise census after the final checkpoint if needed; certify all seven exact census risks <= tau',
    'evidence_error': '1/200',
    'conservative_stage_nonpass': ['689/1000','311/1000','0'],
    'conservative_evidence_cost': '2016',
    'blind_probability': '9/199',
    'mixed_error': '1/20',
    'conservative_mixed_cost': '383040/199',
    'previous_mixed_upper': '9671/5',
    'total_registered_bins': 2439,
    'target_bin_counts': [192,196,425],
    'small_population_max': 6,
    'small_loss_denominator': 4,
    'small_alphas': ['1/20','1/5','1/2'],
    'independent_checks': 'Direct subset laws for population sizes 1..6, all omitted counts and quarter-grid extremal totals; sorted quarter-grid populations of sizes 2..6, all nontrivial sample sizes, convex upper/lower hinges, and strict lower-tail/weak upper-tail checks',
    'example_seeds': [7,29],
    'example_cases': ['zero','margin','boundary','unsafe','tailbinary'],
    'example_definition': 'Fixed rational tables: zero; constant 3/32; constant 1/10; constant one; ones at ranks 59..64 and zero elsewhere. Each uses the evidence branch and random.Random(seed).randrange. An additional scripted zero mixture draw demonstrates the blind path without any oracle call',
    'example_interpretation': 'Illustrative deterministic conformance traces, not empirical calibration, a model study, or evidence for a uniform expected-cost theorem; supplied RNG validity requires independent uniform conditional draws',
    'maximum_label_denominator': 1000000,
    'reference_scope': 'The mathematical theorem covers arbitrary fixed real losses in [0,1]; the executable accepts exact integers or Fractions in [0,1] with denominator at most 1000000, independent of the audit randomness',
    'arithmetic': 'Python standard-library exact integers and Fraction arithmetic only; all scientific probabilities, thresholds, and costs are rational strings; no floating decision arithmetic',
    'source_pins': 'Pin checker, actual imported arithmetic and auditor modules, their three tests, protocol snapshot, and theorem before and after calculation; refuse drift and existing outputs',
    'claim_boundary': 'A modest finite-instance upper-constant improvement using an explicitly disclosed blind branch, not an evidence-only bound below 1934.2, an exact minimax solution, an optimized schedule, practical model savings, scientific priority, or independent human verification',
}


def _require(condition, message):
    if not condition:
        raise RuntimeError('finite-checkpoint certificate: '+message)


def _canonical(value):
    """Restrict protocols and saved evidence to exact JSON types."""
    def validate(item):
        if type(item) in (int,str):
            return
        if type(item) is list:
            for child in item:
                validate(child)
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for child in item.values():
                validate(child)
            return
        raise ValueError('only exact integer, string, list, and object values are allowed')
    validate(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def validate_protocol(protocol):
    if _canonical(protocol) != _canonical(CANONICAL_PROTOCOL):
        raise ValueError('protocol differs from the canonical frozen protocol')
    return protocol


def parse_protocol(raw):
    if type(raw) is not bytes or len(raw)>MAX_PROTOCOL_BYTES:
        raise ValueError('protocol must be bytes within the 16 KiB limit')
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:
                raise ValueError('duplicate protocol key: '+key)
            result[key]=value
        return result
    def invalid_constant(value):
        raise ValueError('nonstandard JSON number: '+value)
    try:
        result=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid_constant)
    except (UnicodeDecodeError,json.JSONDecodeError,RecursionError) as error:
        raise ValueError('invalid protocol JSON') from error
    return validate_protocol(result)


def _read_protocol_bytes(path):
    with path.open('rb') as stream:
        raw=stream.read(MAX_PROTOCOL_BYTES+1)
    if len(raw)>MAX_PROTOCOL_BYTES:
        raise ValueError('protocol exceeds the 16 KiB limit')
    return raw


def _weights(budget):
    return tuple(F(comb(64-r,budget-1),comb(64,budget)) if 64-r>=budget-1 else F(0)
                 for r in range(1,65))


def _checked_law(size, omitted, total):
    law=arithmetic.extremal_law(size,omitted,total)
    _require(law.denominator==comb(size,omitted) and
             sum(count for _,count in law.masses)==law.denominator,
             'extremal law mass normalization')
    _require(all(type(count) is int and count>0 and isinstance(value,F)
                 for value,count in law.masses),'positive exact extremal masses')
    _require(all(left[0]<right[0] for left,right in zip(law.masses,law.masses[1:])),
             'ordered distinct extremal support')
    _require(sum((value*count for value,count in law.masses),F(0))
             ==F(size-omitted,size)*total*law.denominator,'extremal sample mean')
    return law


def checkpoint_certificate(protocol):
    """Recompute all registered bins; no file output or random sampling."""
    validate_protocol(protocol)
    geometry=protocol['geometry']
    budgets=geometry['budgets']
    tau,epsilon=F(geometry['tau']),F(geometry['epsilon'])
    weights=tuple(_weights(n) for n in budgets)
    caps=tuple(row[32]/32 for row in weights)
    tails=tuple(sum(row[32:],F(0)) for row in weights)
    schedule=tuple((row['omitted'],F(row['alpha'])) for row in protocol['schedule'])
    _require(reference.BUDGETS==tuple(budgets) and reference.WEIGHTS==weights and
             reference.CAPS==caps and reference.TAIL_MASS==tails,
             'auditor weights match independently calculated original geometry')
    _require((reference.PROMPTS,reference.POOL,reference.HEAD,reference.TAIL_SIZE)==(32,64,32,1024)
             and reference.TAU==tau and reference.EPSILON==epsilon and reference.SCHEDULE==schedule
             and reference.MAX_LABEL_DENOMINATOR==protocol['maximum_label_denominator'],
             'auditor constants match the registered decision')
    _require(all(sum(row,F(0))==1 for row in weights),'normalized original weights')
    deterministic=[]
    for n,tail in zip(budgets,tails):
        if n not in protocol['statistical_budgets']:
            _require(tail<=epsilon,'high-budget suffix mass fits margin')
            deterministic.append({'budget':n,'suffix_weight':str(tail)})
    stages=[]
    bin_total=0
    final_clearance=None
    for omitted,alpha in schedule:
        targets=[]
        for n in protocol['statistical_budgets']:
            index=budgets.index(n)
            cap=caps[index]
            gap=epsilon/cap
            top=min(tau/cap,F(1024))
            lower=gap
            rows=[]
            best,first=None,None
            while lower<top:
                upper=min(lower+1,top)
                null_law=_checked_law(1024,omitted,lower)
                margin_law=_checked_law(1024,omitted,upper-gap)
                cutoff=arithmetic.lower_shortfall(null_law,alpha)
                beta=arithmetic.upper_tail(margin_law,cutoff)
                _require(isinstance(cutoff,F) and isinstance(beta,F) and 0<=beta<=1,
                         'exact cutoff and probability bound')
                maximum=margin_law.masses[-1][0]
                if omitted==16:
                    clearance=cutoff-maximum
                    final_clearance=clearance if final_clearance is None else min(final_clearance,clearance)
                if best is None or beta>best:
                    best,first=beta,len(rows)
                rows.append({'lower':str(lower),'upper':str(upper),'cutoff':str(cutoff),
                             'nonpass_upper':str(beta),'margin_maximum':str(maximum)})
                lower=upper
            expected=protocol['target_bin_counts'][protocol['statistical_budgets'].index(n)]
            _require(len(rows)==expected,'complete target head-bin coverage')
            bin_total+=len(rows)
            targets.append({'budget':n,'cap':str(cap),'suffix_weight':str(tails[index]),
                            'gap':str(gap),'top':str(top),'bin_count':len(rows),'bins':rows,
                            'nonpass_upper':str(best),'first_maximizing_bin':first})
        total=min(F(1),sum((F(row['nonpass_upper']) for row in targets),F(0)))
        stages.append({'omitted':omitted,'alpha':str(alpha),'acquired_count':2048-omitted,
                       'targets':targets,'nonpass_upper':str(total)})
    _require(bin_total==protocol['total_registered_bins'],'complete registered matrix')
    betas=[F(row['nonpass_upper']) for row in stages]
    _require(betas[0]<F(protocol['conservative_stage_nonpass'][0]) and
             betas[1]<F(protocol['conservative_stage_nonpass'][1]) and betas[2]==0,
             'conservative checkpoint nonpass certificate')
    _require(final_clearance>0,'strict support separation at final margin checkpoint')
    # Charge every next checkpoint and the final census, including its zero margin probability.
    increments=[stages[i]['omitted']-(stages[i+1]['omitted'] if i+1<len(stages) else 0)
                for i in range(len(stages))]
    cost=F(stages[0]['acquired_count'])+sum((increment*beta for increment,beta in zip(increments,betas)),F(0))
    alpha=sum((row[1] for row in schedule),F(0))
    conservative=F(protocol['conservative_evidence_cost'])
    blind=F(protocol['blind_probability'])
    mixture=(1-blind)*cost
    rounded_mixture=(1-blind)*conservative
    previous=F(protocol['previous_mixed_upper'])
    _require(alpha==F(protocol['evidence_error']) and cost<conservative,'evidence error and charged cost')
    _require(blind+(1-blind)*alpha==F(protocol['mixed_error']),'mixed global error')
    _require(rounded_mixture==F(protocol['conservative_mixed_cost'])<previous,'improved mixed upper certificate')
    return {'registered_bin_count':bin_total,'deterministic_margin_targets':deterministic,
            'stages':stages,'charged_increments':increments,
            'final_minimum_support_clearance':str(final_clearance),
            'evidence_error':str(alpha),'evidence_expected_upper':str(cost),
            'evidence_conservative_upper':str(conservative),'blind_probability':str(blind),
            'mixed_error':str(blind+(1-blind)*alpha),'mixed_expected_upper':str(mixture),
            'mixed_conservative_upper':str(rounded_mixture),
            'previous_mixed_upper':str(previous),'improvement_over_previous_upper':str(previous-rounded_mixture)}


def _direct_values(population, omitted):
    return [sum((population[i] for i in subset),F(0))
            for subset in combinations(range(len(population)),len(population)-omitted)]


def _variational_shortfall(masses, denominator, alpha):
    return max(value-sum((max(value-x,0)*count for x,count in masses),F(0))/(alpha*denominator)
               for value,_ in masses)


def _direct_upper(masses, denominator, cutoff):
    candidates=[F(1)]
    if cutoff>masses[-1][0]:
        candidates.append(F(0))
    for value,_ in masses:
        if value<cutoff:
            candidates.append(sum((max(x-value,0)*count for x,count in masses),F(0))/(denominator*(cutoff-value)))
    return min(candidates)


def independent_checks(protocol):
    """Finite direct-enumeration evidence, distinct from the general proof."""
    validate_protocol(protocol)
    maximum=protocol['small_population_max']
    denominator=protocol['small_loss_denominator']
    alphas=tuple(F(x) for x in protocol['small_alphas'])
    laws=populations=hinges=tails=0
    for size in range(1,maximum+1):
        for omitted in range(size+1):
            for numerator in range(denominator*size+1):
                total=F(numerator,denominator)
                ones=total.numerator//total.denominator
                values=[F(1)]*ones+([total-ones] if total>ones else [])
                values += [F(0)]*(size-len(values))
                actual=Counter(_direct_values(values,omitted))
                law=_checked_law(size,omitted,total)
                _require(dict(law.masses)==dict(actual),'independent direct-subset extremal law')
                for alpha in alphas:
                    _require(arithmetic.lower_shortfall(law,alpha)==
                             _variational_shortfall(tuple(sorted(actual.items())),sum(actual.values()),alpha),
                             'independent variational lower shortfall')
                laws+=1
    alphabet=tuple(F(j,denominator) for j in range(denominator+1))
    for size in range(2,maximum+1):
        for population in combinations_with_replacement(alphabet,size):
            populations+=1
            for omitted in range(1,size):
                values=_direct_values(population,omitted)
                law=_checked_law(size,omitted,sum(population,F(0)))
                for value in {x for x,_ in law.masses}|set(values):
                    for sign in (-1,1):
                        actual=sum((max(sign*(x-value),0) for x in values),F(0))/len(values)
                        bound=sum((max(sign*(x-value),0)*count for x,count in law.masses),F(0))/law.denominator
                        _require(actual<=bound,'fractional convex hinge domination')
                        hinges+=1
                for alpha in alphas:
                    cutoff=arithmetic.lower_shortfall(law,alpha)
                    lower=F(sum(x<cutoff for x in values),len(values))
                    upper=F(sum(x>=cutoff for x in values),len(values))
                    bound=arithmetic.upper_tail(law,cutoff)
                    _require(bound==_direct_upper(law.masses,law.denominator,cutoff),
                             'independent upper hinge optimization')
                    _require(lower<=alpha and upper<=bound,'strict lower and weak upper tail checks')
                    tails+=1
    atom_values=_direct_values((F(1),F(1,2),F(0),F(0)),3)
    cutoff=arithmetic.lower_shortfall(_checked_law(4,3,F(1)),F(1,20))
    strict=F(sum(x<cutoff for x in atom_values),len(atom_values))
    weak=F(sum(x<=cutoff for x in atom_values),len(atom_values))
    _require(cutoff==0 and strict==0 and weak==F(1,2)>F(1,20),'unsafe atom strictness regression')
    return {'direct_subset_laws':laws,'fractional_populations':populations,'convex_hinge_checks':hinges,
            'tail_checks':tails,'unsafe_atom_regression':{'population':["1","1/2","0","0"],
            'omitted':3,'null_total':'1','actual_total':'3/2','alpha':'1/20','cutoff':str(cutoff),
            'strict_false_pass':str(strict),'weak_false_pass':str(weak)},
            'interpretation':'Finite implementation checks support, but do not establish, the universal convex-order theorem'}


def _exact_record(value):
    if is_dataclass(value):
        return _exact_record(asdict(value))
    if isinstance(value,F):
        return str(value)
    if type(value) is bool:
        return int(value)
    if type(value) in (int,str):
        return value
    if type(value) in (tuple,list):
        return [_exact_record(x) for x in value]
    if type(value) is dict:
        return {key:_exact_record(x) for key,x in value.items()}
    raise ValueError('unsupported or inexact result value')


def _trace(case, seed, result, queried):
    acquisitions=_exact_record(result.acquisitions)
    _require(len(queried)==len(result.acquisitions)==len(set(queried))<=2048,
             'every example label is charged exactly once')
    _require(queried==[(x.prompt,x.rank) for x in result.acquisitions],'callback identities equal charged transcript')
    return {'case':case,'seed':seed,'certified':int(result.certified),'reason':result.reason,
            'allow_blind':int(result.allow_blind),'error_bound':str(result.error_bound),
            'acquired_count':len(acquisitions),
            'acquisition_sha256':hashlib.sha256(_canonical(acquisitions).encode('utf-8')).hexdigest(),
            'checkpoints':_exact_record(result.checkpoints),
            'deterministic_budgets':list(result.deterministic_budgets),
            'full_risks':_exact_record(result.full_risks) if result.full_risks is not None else []}


def compute_examples(protocol):
    validate_protocol(protocol)
    runs=[]
    for case in protocol['example_cases']:
        for seed in protocol['example_seeds']:
            queried=[]
            def oracle(prompt,rank):
                queried.append((prompt,rank))
                if case=='tailbinary':
                    return int(rank>=59)
                return {'zero':F(0),'margin':F(3,32),'boundary':F(1,10),'unsafe':F(1)}[case]
            result=reference.audit(oracle,randbelow=random.Random(seed).randrange)
            _require(result.certified==(case!='unsafe'),'illustrative fixed-table certificate decision')
            if case in ('boundary','unsafe'):
                _require(len(result.acquisitions)==2048,'boundary/unsafe example census')
            else:
                _require(len(result.acquisitions) in (2000,2016,2032),'margin example checkpoint completion')
            runs.append(_trace(case,seed,result,queried))
    def forbidden_oracle(_prompt,_rank):
        raise RuntimeError('blind example must not acquire a label')
    def blind_draw(bound):
        _require(bound==199,'blind example mixture denominator')
        return 0
    blind=reference.audit(forbidden_oracle,allow_blind=True,randbelow=blind_draw)
    _require(blind.certified and blind.reason=='blind' and not blind.acquisitions,'explicit empty-query blind example')
    runs.append(_trace('blind','scripted zero draw',blind,[]))
    return {'interpretation':protocol['example_interpretation'],
            'acquisition_digest':'SHA-256 of compact sorted-key JSON acquisition dataclasses; rational losses are exact strings',
            'runs':runs}


def calculate(protocol):
    validate_protocol(protocol)
    result={'checkpoint_certificate':checkpoint_certificate(protocol),
            'independent_checks':independent_checks(protocol),'illustrative_examples':compute_examples(protocol)}
    _canonical(result)
    return result


def _source_files(protocol_path):
    actual=(Path(arithmetic.__file__).resolve(),Path(reference.__file__).resolve(),Path(__file__).resolve())
    expected=tuple((ROOT/name).resolve() for name in
                   ('goodhart_audit/checkpoint_math.py','goodhart_audit/checkpoint.py','experiments/check_finite_checkpoint.py'))
    _require(actual==expected,'actual imported scientific modules must have their registered paths')
    files=list(actual)+[ROOT/'tests/test_checkpoint_math.py',ROOT/'tests/test_checkpoint.py',
                        ROOT/'tests/test_finite_checkpoint.py',protocol_path,ROOT/'docs/finite-checkpoint-theorem.md']
    _require(len(set(files))==8,'eight distinct scientific source paths')
    return files


def build_results(supplied_protocol, protocol_path):
    path=Path(protocol_path).resolve()
    raw=_read_protocol_bytes(path)
    snapshot=parse_protocol(raw)
    if supplied_protocol is not None and _canonical(validate_protocol(supplied_protocol))!=_canonical(snapshot):
        raise ValueError('supplied protocol differs from its file snapshot')
    files=_source_files(path)
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources={key(file):hashlib.sha256(raw if file==path else file.read_bytes()).hexdigest() for file in files}
    result={'schema_version':1,'description':__doc__,'dependencies':'Python standard library only',
            'protocol':snapshot,'protocol_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':sources,
            **calculate(snapshot),'claim_boundary':snapshot['claim_boundary']}
    current={key(file):hashlib.sha256(_read_protocol_bytes(file) if file==path else file.read_bytes()).hexdigest()
             for file in files}
    _require(current==sources,'a pinned scientific source changed during calculation')
    _canonical(result)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,default=ROOT/'experiments/finite_checkpoint_protocol.json')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.out.exists():
            raise ValueError('output already exists; choose a fresh artifact path')
        result=build_results(None,args.protocol)
        encoded=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(encoded)
    except (ValueError,RuntimeError,OSError) as error:
        print('finite-checkpoint checks: '+str(error),file=sys.stderr)
        return 2
    print('Passed exact finite-checkpoint checks; saved evidence to '+str(args.out)+'.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
