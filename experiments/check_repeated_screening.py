"""Reproduce two finite bounds and independent gate checks without downloads.

Run: python -B -S -m experiments.check_repeated_screening --out fresh.json
The protocol records a fixed calculation after exploration, not preregistration.
"""
import argparse
from dataclasses import asdict
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

from goodhart_audit import screening, screening_math

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'experiments/repeated_screening_protocol.json'
CANONICAL = {
    'version': 1,
    'scope': 'Finite ideal-channel theory; exploratory example selection; no LLM measurements or independent proof review.',
    'log_series_terms': 64,
    'gate_heights': [0, 32],
    'score_denominator': 16,
    'examples': [
        {'name': 'wide-margin finite example', 'N': 13000, 'c': 64,
         'tau': '1/64', 'epsilon': '9/640', 'delta': '1/20', 'nu': '1/200',
         'K': 4, 'p': '0', 'pp': '5/256', 'cap': None},
        {'name': 'small-relative-margin example', 'N': 70000000, 'c': 8192,
         'tau': '1/512', 'epsilon': '1/8192', 'delta': '1/20', 'nu': '1/10000000',
         'K': 52, 'p': '59/32768', 'pp': '65/32768', 'cap': '48'},
    ],
}
SOURCES = (
    'experiments/check_repeated_screening.py',
    'experiments/repeated_screening_protocol.json',
    'goodhart_audit/screening.py', 'goodhart_audit/screening_math.py',
    'docs/repeated-screening-theorem.md',
    'tests/test_screening.py', 'tests/test_screening_math.py',
    'tests/test_screening_checker.py',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate protocol key: {key}')
        result[key] = value
    return result


def load_protocol(path=PROTOCOL):
    value = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_unique_pairs)
    # Serialization distinguishes 1, 1.0 and True, unlike Python equality.
    require(json.dumps(value, sort_keys=True) == json.dumps(CANONICAL, sort_keys=True),
            'protocol differs from the fixed schema')
    return value


def source_pins():
    require(Path(screening.__file__).resolve() == ROOT/'goodhart_audit/screening.py', 'unexpected auditor module')
    require(Path(screening_math.__file__).resolve() == ROOT/'goodhart_audit/screening_math.py', 'unexpected mathematics module')
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}


def absorbing_solution(up, down, height, hitting):
    """Solve the tridiagonal recurrence; no closed-form gate identity is used."""
    if height == 0:
        return F(1) if hitting else F(0)
    diagonal = [up+down for _ in range(height)]
    rhs = [F(0) if hitting else F(1) for _ in range(height)]
    if hitting:
        rhs[-1] += up
    for i in range(1, height):
        multiplier = -down/diagonal[i-1]
        diagonal[i] -= multiplier*(-up)
        rhs[i] -= multiplier*rhs[i-1]
    values = [F(0)]*height
    values[-1] = rhs[-1]/diagonal[-1]
    for i in reversed(range(height-1)):
        values[i] = (rhs[i]+up*values[i+1])/diagonal[i]
    return values[0]


def gate_checks():
    count = 0
    for height in range(33):
        for numerator in range(17):
            score = F(numerator, 16)
            q = F(1, 4)+score/2
            up, down = F(3, 4)*q, F(1, 4)*(1-q)
            hit = absorbing_solution(up, down, height, True)
            duration = absorbing_solution(up, down, height, False)
            ratio = down/up
            require(hit == 1/sum((ratio**i for i in range(height+1)), F(0)), 'gate hitting law')
            require(q*hit*screening.correction_probability(score, height) == F(2, 3)*score, 'corrected emission law')
            require(q*hit <= F(2, 3)*score+F(1, 4*(height+1)), 'exact purchase bound')
            require(q*duration <= F(2*height, 3)+F(8*(height+1)**2, 27)*score, 'sharper paid-rating bound')
            if score == 0:
                require(q*duration == F(2*height, 3), 'fair lazy walk endpoint')
            count += 1
    return count


def illustrative_traces():
    """Scripted possible branches; RNG is intentionally not a uniform source."""
    rows = []
    cases = [
        ('all reports zero', 2, 0, 0, F(0), None),
        ('cache reused', 2, 0, 1, F(0), None),
        ('safe boundary census', 1, 0, 1, F(1,64), None),
        ('all up walk', 1, 4, 1, F(0), None),
        ('cap during walk', 2, 4, 1, F(0), 3),
    ]
    for name, population, height, report, score, cap in cases:
        result = screening.audit(lambda i: report, lambda i: score,
                                 population=population, exact_cost=64,
                                 tau=F(1,64), epsilon=F(9,640), delta=F(1,20),
                                 gate_height=height, randbelow=lambda n: 0,
                                 max_ratings=cap)
        rows.append(dict(name=name, **asdict(result)))
    return rows


def build_document():
    before = source_pins()
    protocol = load_protocol()
    examples = []
    for raw in protocol['examples']:
        args = dict(raw)
        for name in ['tau', 'epsilon', 'delta', 'nu', 'p', 'pp']:
            args[name] = F(args[name])
        args['cap'] = None if args['cap'] is None else F(args['cap'])
        examples.append(screening_math.certificate(**args))
    document = dict(
        scope=protocol['scope'],
        logarithm_method='64-term rational atanh series after dyadic reduction, with geometric tail enclosure',
        gate_cases=gate_checks(), examples=examples,
        illustrative_trace_scope='Scripted conformance paths; not Monte Carlo or evidence of statistical calibration.',
        illustrative_traces=illustrative_traces(), source_sha256=before,
    )
    require(source_pins() == before, 'scientific sources changed during calculation')
    return document


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        require(not args.out.exists(), 'output already exists; choose a fresh path')
        document = build_document()
        serialized = json.dumps(document, indent=2, sort_keys=True)+'\n'
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(serialized)
    except (ValueError, OSError) as error:
        print(f'repeated-screening checks: {error}', file=sys.stderr)
        return 2
    print(f'Passed {document["gate_cases"]} gate cases and two finite separations; wrote {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
