"""Exact finite checks and rational all-zero cost certificates, offline.

Uses only the standard library. Finite checks do not replace the proof in
docs/zero-cost-theorem.md or establish novelty. The cost certificates concern
independent NEGEXP inclusion, not the repository's anytime betting engine.
No labels, sampling runs, numerical logarithms, or numerical exponentials enter
the calculation. Decimal displays summarize the accompanying exact fractions.
"""

if not __debug__:
    raise RuntimeError("zero-cost checks require assertions; rerun Python without -O or -OO")

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform


ROOT = Path(__file__).resolve().parents[1]
FAMILY_TYPES = ("full", "powers_four_plus_max", "dyadic_plus_max")
EXP_TERMS = 32
THEOREM_SCHEMA = {
    "factor": 160,
    "maximum_risk_threshold": "1/8",
    "maximum_error_probability": "1/4",
    "budget_family_requirement": "Contains every positive integer power 4^j up to its maximum, including 4^0=1",
    "objective": "Expected distinct unit-cost queries on the all-zero fixed-label table",
    "decision": "All declared target risks are at most a predeclared threshold, or abstain",
    "comparator": "All nonanticipating adaptive audits uniformly valid over fixed labels in [0,1], with almost-sure finite certification at the all-zero table",
}


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive integer")
    return value


def _probability(value, name):
    if isinstance(value, bool):
        raise ValueError(name + " must be strictly between zero and one")
    try:
        value = F(value)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        raise ValueError(name + " must be a rational probability") from None
    if not 0 < value < 1:
        raise ValueError(name + " must be strictly between zero and one")
    return value


def _powers(base, maximum):
    result, value = [], 1
    while value <= maximum:
        result.append(value)
        value *= base
    return tuple(result)


def budget_family(pool_size, max_budget, kind):
    _positive_integer(pool_size, "pool size")
    _positive_integer(max_budget, "maximum budget")
    if max_budget > pool_size or kind not in FAMILY_TYPES:
        raise ValueError("invalid maximum budget or family type")
    if kind == "full":
        return tuple(range(1, max_budget+1))
    base = 4 if kind == "powers_four_plus_max" else 2
    return tuple(sorted(set((*_powers(base, max_budget), max_budget))))


def rank_blocks(pool_size, budgets):
    """Partition ranks; reject a family missing a required fourfold witness."""
    _positive_integer(pool_size, "pool size")
    budgets = tuple(budgets)
    if not budgets or len(set(budgets)) != len(budgets):
        raise ValueError("budgets must be nonempty and distinct")
    for n in budgets:
        _positive_integer(n, "budget")
        if n > pool_size:
            raise ValueError("budget exceeds pool size")
    powers = _powers(4, max(budgets))
    if not set(powers) <= set(budgets):
        raise ValueError("budget family must contain every power of four up to its maximum")
    return [{"budget": n,
             "first_rank": pool_size//(4*n)+1 if j < len(powers)-1 else 1,
             "last_rank": pool_size//n}
            for j, n in enumerate(powers)]


@lru_cache(maxsize=512, typed=True)
def exact_weights(pool_size, budget):
    _positive_integer(pool_size, "pool size")
    _positive_integer(budget, "budget")
    if budget > pool_size:
        raise ValueError("budget exceeds pool size")
    denominator = math.comb(pool_size, budget)
    return tuple(F(math.comb(pool_size-r, budget-1), denominator)
                 if pool_size-r >= budget-1 else F(0)
                 for r in range(1, pool_size+1))


def hypergeometric_miss(size, failures, inspected):
    _positive_integer(size, "block size")
    _positive_integer(failures, "failure count")
    if failures > size or isinstance(inspected, bool) or not isinstance(inspected, int) or not 0 <= inspected <= size:
        raise ValueError("invalid hypergeometric counts")
    if size-inspected < failures:
        return F(0)
    return F(math.comb(size-inspected, failures), math.comb(size, failures))


def inverse_miss_bound(size, failures, delta):
    """Exact inverse of the convex piecewise-linear miss function (eq. 38)."""
    delta = _probability(delta, "delta")
    hypergeometric_miss(size, failures, 0)  # Validate counts before searching.
    low, high = 0, size-failures+1
    while high-low > 1:
        middle = (low+high)//2
        if hypergeometric_miss(size, failures, middle) <= delta:
            high = middle
        else:
            low = middle
    left = hypergeometric_miss(size, failures, high-1)
    right = hypergeometric_miss(size, failures, high)
    assert left > delta >= right and left > right
    return F(high-1) + (left-delta)/(left-right)


def log_upper_certificate(delta):
    """Return integer c>=log(1/delta), certified by a positive exp series."""
    delta = _probability(delta, "delta")
    c = 1
    while True:
        term, total = F(1), F(1)
        for k in range(1, EXP_TERMS+1):
            term *= F(c, k)
            total += term
        if total >= 1/delta:
            return {"bound": c, "partial_sum": total, "degree": EXP_TERMS}
        c += 1


def inclusion_upper(x):
    """Rational upper bound U5(x) from the signed Taylor remainder (eq. 40)."""
    x = F(x)
    if x < 0:
        raise ValueError("inclusion exponent must be nonnegative")
    polynomial = x-x*x/2+x**3/6-x**4/24+x**5/120
    assert polynomial >= 0
    return min(F(1), polynomial)


def _display(value):
    value = F(value)
    with localcontext() as context:
        context.prec = 40
        return format(Decimal(value.numerator)/Decimal(value.denominator), ".6f")


def _envelope(pool_size, budgets):
    rows = [exact_weights(pool_size, n) for n in budgets]
    return tuple(max(row[r] for row in rows) for r in range(pool_size))


def cost_certificate(case):
    """Exact lower <= OPT0 <= C_NEG <= upper for one fixed score geometry."""
    p = _positive_integer(case["prompts"], "prompt count")
    m = _positive_integer(case["pool_size"], "pool size")
    budgets = budget_family(m, case["max_budget"], case["family"])
    tau = _probability(case["tau"], "tau")
    delta = _probability(case["delta"], "delta")
    if tau > F(1, 8) or delta > F(1, 4):
        raise ValueError("cost certificate requires tau<=1/8 and delta<=1/4")
    blocks, lower = [], F(0)
    for block in rank_blocks(m, budgets):
        size = p*(block["last_rank"]-block["first_rank"]+1)
        minimum = exact_weights(m, block["budget"])[block["last_rank"]-1]/p
        failures = tau//minimum+1
        assert 1 <= failures <= size and failures*minimum > tau
        bound = inverse_miss_bound(size, failures, delta)
        lower += bound
        crossing = math.ceil(bound)
        blocks.append({**block, "size": size, "minimum_target_mass": str(minimum),
                       "unsafe_subset_size": failures, "lower_cost": str(bound),
                       "crossing_integer": crossing,
                       "miss_before_crossing": str(hypergeometric_miss(size, failures, crossing-1)),
                       "miss_at_crossing": str(hypergeometric_miss(size, failures, crossing))})
    log_bound = log_upper_certificate(delta)
    envelope = _envelope(m, budgets)
    upper = p*sum((inclusion_upper(log_bound["bound"]*s/(p*tau)) for s in envelope), F(0))
    assert 0 < lower <= upper <= p*m
    return {**case, "budgets": list(budgets), "items": p*m, "blocks": blocks,
            "log_upper_certificate": {"integer_bound": log_bound["bound"],
                                      "positive_series_degree": log_bound["degree"],
                                      "positive_series_sum": str(log_bound["partial_sum"])},
            "lower": str(lower), "upper": str(upper), "ratio_upper": str(upper/lower),
            "combined_ratio_upper": str(min(F(160), upper/lower)),
            "display": {"lower": _display(lower), "upper": _display(upper),
                        "ratio_upper": _display(upper/lower)},
            "interpretation": "Exact rational bounds, not exact OPT or exact NEGEXP cost; decimal displays are rounded."}


def high_threshold_case(pool_size, delta):
    _positive_integer(pool_size, "pool size")
    if pool_size < 2:
        raise ValueError("counterexample needs at least two ranks")
    delta = _probability(delta, "delta")
    tau = 1-F(1, 2*pool_size)
    rows = [exact_weights(pool_size, n) for n in range(1, pool_size+1)]
    assert rows[-1][0] == 1 > tau
    assert all(sum(row[1:], F(0)) <= 1-F(1, pool_size) < tau for row in rows)
    z = sum((max(row[r] for row in rows) for r in range(pool_size)), F(0))
    return {"pool_size": pool_size, "tau": str(tau), "delta": str(delta),
            "binary_unsafe_iff_contains_top_rank": True, "optimal_cost": str(1-delta),
            "envelope_normalizer": str(z), "competitive_ratio_lower": str(z),
            "competitive_ratio_lower_display": _display(z),
            "reason": "A missing top rank bounds every risk by 1-1/m; concavity gives C_NEG >= (1-delta)*Z."}


def check_blocks(max_pool, family_types):
    _positive_integer(max_pool, "maximum pool size")
    if not family_types or len(set(family_types)) != len(family_types) or any(kind not in FAMILY_TYPES for kind in family_types):
        raise ValueError("invalid block family types")
    family_cases = rank_checks = block_checks = 0
    minimum_density, maximum_envelope = F(1), F(0)
    for m in range(1, max_pool+1):
        rows = [exact_weights(m, n) for n in range(1, m+1)]
        running = {kind: [F(0)]*m for kind in FAMILY_TYPES}
        powers_four, powers_two = set(_powers(4, m)), set(_powers(2, m))
        for n in range(1, m+1):
            row = rows[n-1]
            for kind in FAMILY_TYPES:
                if kind == "full" or n in (powers_four if kind == "powers_four_plus_max" else powers_two):
                    running[kind] = [max(a, b) for a, b in zip(running[kind], row)]
            for kind in family_types:
                family = budget_family(m, n, kind)
                envelope = [max(a, b) for a, b in zip(running[kind], row)]
                covered = []
                for block in rank_blocks(m, family):
                    start, end = block["first_rank"], block["last_rank"]
                    size = end-start+1
                    assert size > 0
                    for r in range(start, end+1):
                        density = size*rows[block["budget"]-1][r-1]
                        scaled = size*envelope[r-1]
                        assert density > F(1, 4) and scaled <= 4
                        minimum_density = min(minimum_density, density)
                        maximum_envelope = max(maximum_envelope, scaled)
                        covered.append(r)
                        rank_checks += 1
                    block_checks += 1
                assert sorted(covered) == list(range(1, m+1))
                family_cases += 1
    return {"maximum_pool_size": max_pool, "family_types": list(family_types),
            "family_cases": family_cases, "block_checks": block_checks, "rank_checks": rank_checks,
            "minimum_block_size_times_target_mass": str(minimum_density),
            "maximum_block_size_times_envelope_mass": str(maximum_envelope),
            "prompt_extension": "Multiplication by P cancels division by P exactly in both checked inequalities."}


def check_hypergeometric(max_size, thresholds, errors):
    _positive_integer(max_size, "maximum block size")
    thresholds = [_probability(tau, "tau") for tau in thresholds]
    errors = [_probability(delta, "delta") for delta in errors]
    if not thresholds or not errors or len(set(thresholds)) != len(thresholds) or len(set(errors)) != len(errors):
        raise ValueError("threshold and error grids must be nonempty and distinct")
    if any(tau > F(1, 8) for tau in thresholds) or any(delta > F(1, 4) for delta in errors):
        raise ValueError("hypergeometric protocol lies outside theorem conditions")
    # Integer numerators share C(D,b), so signs and the second-difference
    # identity can be checked exactly without millions of reduced Fractions.
    pascal = [[math.comb(n, k) for k in range(n+1)] for n in range(max_size+1)]
    def choose(n, k):
        return pascal[n][k] if 0 <= k <= n else 0
    convexity = factor_bounds = rounding = danger_sizes = inverses = 0
    for size in range(1, max_size+1):
        for failures in range(1, size+1):
            for inspected in range(size-1):
                difference = choose(size-inspected-2, failures)-2*choose(size-inspected-1, failures)+choose(size-inspected, failures)
                assert difference == (choose(size-inspected-2, failures-2) if failures >= 2 else 0) >= 0
                convexity += 1
            if size >= 8 and 4*failures <= 3*size:
                # Worst integer z and smallest factor denominator control all
                # factors in eq.27: v<=1/2 and 1/(D-u)<=4/D.
                assert F(size//8, size-failures+1) <= F(1, 2)
                assert F(1, size-failures+1) <= F(4, size)
                factor_bounds += 1
        if size >= 8:
            assert math.ceil(F(size, 16)) <= F(size, 8)
            rounding += 1
        for tau in thresholds:
            failures = (4*tau*size)//1+1
            assert 1 <= failures <= size
            if size >= 8:
                assert failures <= F(3*size, 4)
            danger_sizes += 1
            for delta in errors:
                bound = inverse_miss_bound(size, failures, delta)
                left = math.floor(bound)
                if bound == left:
                    interpolated = hypergeometric_miss(size, failures, left)
                else:
                    f0, f1 = hypergeometric_miss(size, failures, left), hypergeometric_miss(size, failures, left+1)
                    interpolated = f0+(bound-left)*(f1-f0)
                assert interpolated == delta
                inverses += 1
    return {"maximum_block_size": max_size, "convexity_checks": convexity,
            "log_factor_algebra_checks": factor_bounds, "rounding_checks": rounding,
            "unsafe_subset_size_checks": danger_sizes, "exact_inverse_checks": inverses,
            "scope": "Exact finite identities and algebraic prerequisites; analytic log/exponential/Jensen steps remain proof obligations."}


def build_results(protocol, protocol_path):
    protocol_path = Path(protocol_path).resolve()
    # Parse and initially hash the same snapshot. Separate reads could bind an
    # old parsed protocol to the checksum of newly changed file contents.
    protocol_bytes = protocol_path.read_bytes()
    if json.loads(protocol_bytes) != protocol:
        raise ValueError("supplied protocol differs from the pinned protocol file")
    theorem = protocol.get("theorem")
    if theorem != THEOREM_SCHEMA or type(theorem["factor"]) is not int:
        raise ValueError("protocol theorem metadata must match the canonical checked theorem schema")
    if not protocol["cost_cases"] or not protocol["high_threshold_pool_sizes"]:
        raise ValueError("cost and counterexample cases must be nonempty")
    names = [case["name"] for case in protocol["cost_cases"]]
    if len(set(names)) != len(names):
        raise ValueError("cost case names must be distinct")
    files = [Path(__file__).resolve(), ROOT/"tests/test_zero_cost.py", protocol_path,
             ROOT/"docs/zero-cost-theorem.md"]
    sources = {path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path):
               hashlib.sha256(protocol_bytes if path == protocol_path else path.read_bytes()).hexdigest()
               for path in files}
    encoded = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema_version": 1, "description": __doc__, "protocol": protocol,
        "protocol_sha256": hashlib.sha256(encoded).hexdigest(), "source_sha256": sources,
        "runtime": {"python": platform.python_version(), "dependencies": "Python standard library only"},
        "block_checks": check_blocks(protocol["block_check_max_pool_size"], protocol["block_family_types"]),
        "hypergeometric_checks": check_hypergeometric(protocol["hypergeometric_check_max_block_size"],
                                                       protocol["risk_thresholds"], protocol["error_probabilities"]),
        "cost_certificates": [cost_certificate(case) for case in protocol["cost_cases"]],
        "high_threshold_counterexamples": [high_threshold_case(m, F(1, 4)) for m in protocol["high_threshold_pool_sizes"]],
        "claim_boundary": "Finite exact checks and geometry-specific rational certificates support the implementation; they do not prove the unrestricted theorem or establish priority."
    }
    if sources != {path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path):
                   hashlib.sha256(path.read_bytes()).hexdigest() for path in files}:
        raise RuntimeError("a pinned checker or protocol source changed during calculation")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/zero_cost_protocol.json")
    parser.add_argument("--out", type=Path, default=ROOT/"artifacts/local/zero-cost-candidate.json")
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output already exists; choose a fresh artifact path")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = build_results(protocol, args.protocol)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an artifact created while checks ran.
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(f"Passed {result['block_checks']['family_cases']:,} family cases and "
          f"{result['hypergeometric_checks']['convexity_checks']:,} convexity checks; "
          f"saved {len(result['cost_certificates'])} rational cost certificates to {args.out}.")


if __name__ == "__main__":
    main()
