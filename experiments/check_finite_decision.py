"""Exact finite lower certificate for the original whole-grid decision.

Standard library only. The Bellman program solves a relaxed fixed-prior
testing problem to lower-bound every valid auditor. Its minimizing policies
are not asserted to be valid fixed-table auditors. No model labels or
population-sized oracle tables are generated for the 1024-cell calculation.
"""

import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from math import comb
from pathlib import Path
import sys

from experiments import check_sharp_cost as sharp


ROOT = Path(__file__).resolve().parents[1]
IMPORTED_HELPER_PATH = Path(sharp.__file__).resolve()
exact_weights = sharp.exact_weights
MAX_PROTOCOL_BYTES = 16384
MAX_POPULATION = 1024
MAX_MULTIPLIER = 8192
MAX_INTEGER_BITS = 4096
DECIMAL_DIGITS = 9
CANONICAL_PROTOCOL = {
    "version": 1,
    "title": "A finite expected-label lower certificate for the original whole-grid decision",
    "status": "Fixed after exploratory dual calculations and independent agent checks, before the saved production calculation; not external preregistration",
    "evidence_type": "deterministic_exact_integer_dynamic_program_and_independent_finite_oracles",
    "objective": "One globally delta-valid, all-safe-complete auditor; worst-case expected distinct labels over fixed tables with all originally declared risks at most tau-epsilon",
    "geometry": {
        "prompts": 32, "pool_size": 64, "budgets": [1, 2, 4, 8, 16, 32, 64],
        "tau": "1/10", "epsilon": "1/160", "delta": "1/20",
        "tail_first_rank": 33, "tail_last_rank": 64,
        "tail_population": 1024, "null_count": 192, "alternative_count": 205,
        "outside_loss": 0,
    },
    "domination_check": "Check all integer budgets 1..64 at ranks 33..64; this contains every originally declared budget and does not change the original decision",
    "multipliers": [512, 1024, 2048, 4096, 8192],
    "selection": "Largest exact lower bound among only the five registered multipliers; no globally optimal multiplier claim",
    "stopping_oracle": {"maximum_population": 5, "multipliers": [0, 1, 2, 4, 8], "matrix": "N=2..5; all 0<=k<k+d<=N; exhaustive deterministic stopping choices with dominated zero-error continuations and null-impossible certification pruned"},
    "coordinate_oracle": {"maximum_population": 8, "multipliers": [1, 3, 10, 100], "matrix": "N=2..8; all k>=0,d>=1,k+d<=floor(N/2); enumerate support subsets and optimize over every coordinate choice"},
    "hand_cases": "N=1..8 and lambda in {0,1,3,10,100}: k=0,kalt=1 gives min(lambda,N); k=0,kalt=N gives min(lambda,1); N=2,k=1,kalt=2,lambda=2 gives 3/2",
    "maximum_population": 1024,
    "maximum_multiplier": 8192,
    "maximum_integer_bits": 4096,
    "arithmetic": "Exact rolling Pascal coefficients and integer Bellman values, expected costs, alternative error masses, and null-certificate masses; no logarithms or floating-point decision arithmetic",
    "state_checksum": "SHA-256 of N,k,d,lambda followed by each null-possible state in decreasing t and increasing s, fields t,s,A,B,W,cost,error,null_certificate; each nonnegative integer is unsigned big-endian bytes preceded by its four-byte byte-length",
    "state_weight_warning": "A and B are masses of one ordered history, not aggregate masses of every history with the same t,s; no binomial(t,s) factor is inserted",
    "decimal_digits": 9,
    "rounding": "Lower certificate decimal rounded down; census-to-lower competitive ratio rounded up; exact fractions and integer residuals retained",
    "claim_boundary": "A same-decision finite minimax lower certificate and a census comparison, not a new Bellman algorithm, an optimal auditor, a model study, a global multiplier optimization, scientific priority, or independent human review. Existing source-pinned files and the audit engine remain unchanged.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact finite-decision check failed: "+message)


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name+" must be an exact integer or Fraction")
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 8192:
        raise ValueError(name+" exceeds the rational bit limit")
    return value


def _counts(size, count, added, multiplier=0, maximum=MAX_POPULATION):
    _integer(size, "population", 1, maximum)
    _integer(count, "null count", 0, size-1)
    _integer(added, "added count", 1, size-count)
    _integer(multiplier, "multiplier", 0, MAX_MULTIPLIER)


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def validate_protocol(protocol):
    if _canonical(protocol) != _canonical(CANONICAL_PROTOCOL):
        raise ValueError("protocol differs from the exact canonical frozen protocol")
    _require(MAX_POPULATION == 1024 and MAX_MULTIPLIER == 8192 and MAX_INTEGER_BITS == 4096,
             "registered computational caps")
    return protocol


def parse_protocol(data):
    if len(data) > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 16 KiB limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate protocol key: "+key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("invalid protocol number: "+value)
    try:
        return json.loads(data, object_pairs_hook=unique, parse_constant=invalid)
    except (UnicodeError, RecursionError) as error:
        raise ValueError("invalid bounded protocol JSON") from error


def _choose(size, count):
    return comb(size, count) if 0 <= count <= size else 0


def ordered_masses(size, count, added, queried, seen):
    _counts(size, count, added)
    _integer(queried, "query count", 0, size)
    _integer(seen, "observed successes", 0, queried)
    null_total, alternative_total = comb(size, count), comb(size, count+added)
    return {"null_mass": _choose(size-queried, count-seen)*alternative_total,
            "alternative_mass": _choose(size-queried, count+added-seen)*null_total,
            "denominator": null_total*alternative_total}


def _hash_integers(digest, values):
    for value in values:
        encoded = value.to_bytes(max(1, (value.bit_length()+7)//8), "big")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)


def exact_dual(size, count, added, multiplier):
    """Exact min(E_null T + lambda*Q(certificate)) for the relaxed pair.

    Loss-free outside information is identical under the priors. Rejecting
    is allowed only at null-impossible histories; the represented policy
    certifies with probability one under the null. Each A/B is the mass of
    one ordered prefix, making the continuation term A+W0+W1 exact.
    """
    _counts(size, count, added, multiplier)
    alternative_count = count+added
    null_total, alternative_total = comb(size, count), comb(size, alternative_count)
    denominator = null_total*alternative_total
    peak = max(denominator.bit_length(), (multiplier*denominator).bit_length())
    _require(peak <= MAX_INTEGER_BITS, "initial integer bit cap")
    coefficients = [1]+[0]*alternative_count
    next_values = [0]*(count+2)
    next_costs, next_errors, next_certified = next_values.copy(), next_values.copy(), next_values.copy()
    digest = hashlib.sha256()
    _hash_integers(digest, (size, count, added, multiplier))
    states = stops = continuations = certificate_checks = 0
    for remaining in range(size+1):
        if remaining:
            for successes in range(min(remaining, alternative_count), 0, -1):
                coefficients[successes] += coefficients[successes-1]
                peak = max(peak, coefficients[successes].bit_length())
        queried = size-remaining
        values = [0]*(count+2)
        costs, errors, certified = values.copy(), values.copy(), values.copy()
        for seen in range(max(0, count-remaining), min(count, queried)+1):
            a = coefficients[count-seen]*alternative_total
            b = coefficients[alternative_count-seen]*null_total
            states += 1
            if not b:
                certified[seen] = a
                stops += 1
            else:
                continued_cost = a+next_costs[seen]+next_costs[seen+1]
                continued_error = next_errors[seen]+next_errors[seen+1]
                continued = a+next_values[seen]+next_values[seen+1]
                stopped = multiplier*b
                completed_null = next_certified[seen]+next_certified[seen+1]
                _require(completed_null == a, "continuation preserves certain null certification")
                peak = max(peak, continued.bit_length(), stopped.bit_length(), continued_cost.bit_length(),
                           continued_error.bit_length(), completed_null.bit_length(),
                           (multiplier*continued_error).bit_length())
                # Minimize alternative error on a value tie; this chooses a
                # diagnostic relaxed policy, not a globally valid auditor.
                if (continued, continued_error) < (stopped, b):
                    values[seen], costs[seen], errors[seen] = continued, continued_cost, continued_error
                    certified[seen] = completed_null
                    continuations += 1
                else:
                    values[seen], errors[seen], certified[seen] = stopped, b, a
                    stops += 1
            objective = costs[seen]+multiplier*errors[seen]
            peak = max(peak, a.bit_length(), b.bit_length(), objective.bit_length(), (remaining*a).bit_length())
            _require(peak <= MAX_INTEGER_BITS, "intermediate integer bit cap")
            _require(values[seen] == objective, "policy Lagrange identity")
            _require(certified[seen] == a, "null certification probability is one at every possible state")
            _require(0 <= costs[seen] <= remaining*a and 0 <= errors[seen] <= b, "policy cost/error mass bounds")
            _require(values[seen] <= min(multiplier*b, remaining*a), "stop and full-census Bellman upper bounds")
            certificate_checks += 1
            _hash_integers(digest, (queried, seen, a, b, values[seen], costs[seen], errors[seen], certified[seen]))
        next_values, next_costs, next_errors, next_certified = values, costs, errors, certified
    _require(states == (count+1)*(size-count+1), "all and only null-possible count states")
    _require(next_certified[0] == denominator, "root null completeness")
    return {"population": size, "null_count": count, "added_count": added, "alternative_count": alternative_count,
            "multiplier": multiplier, "denominator": denominator, "value_numerator": next_values[0],
            "policy_cost_numerator": next_costs[0], "policy_error_numerator": next_errors[0],
            "null_certificate_numerator": next_certified[0], "null_possible_states": states,
            "stop_states": stops, "continue_states": continuations,
            "certified_null_state_checks": certificate_checks, "maximum_integer_bits": peak,
            "rolling_vector_length": count+2,
            "rolling_integer_array_slots_bound": 8*(count+2)+alternative_count+1,
            "state_sha256": digest.hexdigest(), "population_table_allocated": False}


def stopping_policy_pairs(size, count, added):
    """Tiny exhaustive stopping choices with dominated continuations pruned."""
    _counts(size, count, added, maximum=5)
    null = tuple(frozenset(s) for s in itertools.combinations(range(size), count))
    alternative = tuple(frozenset(s) for s in itertools.combinations(range(size), count+added))
    def visit(prefix):
        def mass(tables):
            return F(sum(all((i in table) == bit for i, bit in enumerate(prefix)) for table in tables), len(tables))
        a, b = mass(null), mass(alternative)
        if not a or not b:
            return {(F(0), F(0))}
        pairs = {(F(0), b)}
        if len(prefix) < size:
            left, right = visit(prefix+(False,)), visit(prefix+(True,))
            pairs.update((a+c0+c1, q0+q1) for (c0, q0), (c1, q1) in itertools.product(left, right))
        return pairs
    return visit(())


def explicit_coordinate_value(size, count, added, multiplier):
    """Independent support-set oracle retaining every coordinate action."""
    _counts(size, count, added, multiplier, maximum=8)
    null = tuple(sum(1 << i for i in s) for s in itertools.combinations(range(size), count))
    alternative = tuple(sum(1 << i for i in s) for s in itertools.combinations(range(size), count+added))
    null_masks = tuple(sum(1 << j for j, table in enumerate(null) if table >> i & 1) for i in range(size))
    alternative_masks = tuple(sum(1 << j for j, table in enumerate(alternative) if table >> i & 1) for i in range(size))
    coefficient = F(multiplier*len(null), len(alternative))
    @lru_cache(maxsize=None)
    def visit(p_support, q_support):
        if not p_support or not q_support:
            return F(0)
        best = coefficient*q_support.bit_count()
        for coordinate in range(size):
            p_one, q_one = p_support & null_masks[coordinate], q_support & alternative_masks[coordinate]
            p_zero, q_zero = p_support ^ p_one, q_support ^ q_one
            if (p_one, q_one) == (p_support, q_support) or (p_zero, q_zero) == (p_support, q_support):
                continue
            best = min(best, p_support.bit_count()+visit(p_zero, q_zero)+visit(p_one, q_one))
        return best
    return visit((1 << len(null))-1, (1 << len(alternative))-1)/len(null)


def decimal_bound(value, upward=False):
    value = _fraction(value, "decimal input")
    scale = 10**DECIMAL_DIGITS
    numerator = value.numerator*scale
    rounded = -((-numerator)//value.denominator) if upward else numerator//value.denominator
    sign = "-" if rounded < 0 else ""
    whole, remainder = divmod(abs(rounded), scale)
    return f"{sign}{whole}.{remainder:0{DECIMAL_DIGITS}d}"


def dual_certificate(size, count, added, multiplier, delta, census_cost):
    delta = _fraction(delta, "delta")
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0,1)")
    _integer(census_cost, "census cost", size, 1000000)
    row = exact_dual(size, count, added, multiplier)
    denominator, value_numerator = row["denominator"], row["value_numerator"]
    value = F(value_numerator, denominator)
    lower = value-multiplier*delta
    scale = 10**DECIMAL_DIGITS
    rounded = lower.numerator*scale//lower.denominator
    penalty_scaled = multiplier*delta*scale
    if penalty_scaled.denominator == 1:
        left, right = scale, rounded+penalty_scaled.numerator
    else:
        left, right = scale*delta.denominator, rounded*delta.denominator+multiplier*delta.numerator*scale
    residual = left*value_numerator-right*denominator
    _require(residual >= 0, "integer certificate for downward lower rounding")
    row.update(delta=str(delta), lagrange_value_exact=str(value), dual_lower_exact=str(lower),
               dual_lower_decimal_down=decimal_bound(lower),
               minimizing_policy_cost_exact=str(F(row["policy_cost_numerator"], denominator)),
               minimizing_policy_error_exact=str(F(row["policy_error_numerator"], denominator)),
               minimizing_policy_scope="Diagnostic optimizer of the prior-pair relaxation; not asserted to be a valid fixed-table auditor",
               rounded_lower_integer_left_multiplier=left, rounded_lower_integer_right_multiplier=right,
               rounded_lower_integer_residual=residual, census_cost=census_cost,
               census_to_lower_ratio_exact=str(F(census_cost)/lower) if lower > 0 else None,
               census_to_lower_ratio_upper=decimal_bound(F(census_cost)/lower, upward=True) if lower > 0 else None)
    return row


def geometry_certificate(geometry):
    if _canonical(geometry) != _canonical(CANONICAL_PROTOCOL["geometry"]):
        raise ValueError("geometry differs from the original fixed declared decision")
    prompts, size = geometry["prompts"], geometry["pool_size"]
    first, last = geometry["tail_first_rank"], geometry["tail_last_rank"]
    checks = 0
    for budget in range(1, size+1):
        weights = tuple(exact_weights(size, budget))
        _require(len(weights) == size and sum(weights, F(0)) == 1, "normalized finite target weights")
        for rank in range(first, last+1):
            _require(0 <= weights[rank-1] <= F(1, size), "all-budget domination by the uniform tail target")
            checks += 1
    cells, count, alternative = prompts*(last-first+1), geometry["null_count"], geometry["alternative_count"]
    null_risk, alt_risk = F(count, prompts*size), F(alternative, prompts*size)
    tau, epsilon = F(geometry["tau"]), F(geometry["epsilon"])
    _require(cells == geometry["tail_population"] and null_risk == tau-epsilon and alt_risk > tau,
             "common whole-grid safe prior and strictly unsafe original uniform target")
    return {"prompts": prompts, "pool_size": size, "declared_budgets": list(geometry["budgets"]),
            "tail_first_rank": first, "tail_last_rank": last, "tail_cells": cells,
            "null_count": count, "alternative_count": alternative,
            "null_uniform_risk": str(null_risk), "alternative_uniform_risk": str(alt_risk),
            "alternative_excess_above_tau": str(alt_risk-tau), "domination_atom_checks": checks,
            "census_cost": prompts*size, "different_declared_grid_from_original_study": False,
            "interpretation": "Every null table is in the original whole-grid margin class; every alternative violates its originally declared n=1 target."}


def tiny_stopping_checks(spec):
    comparisons = pairs_count = hand_count = 0
    for size in range(1, 9):
        for multiplier in (0, 1, 3, 10, 100):
            for added, expected in ((1, min(multiplier, size)), (size, min(multiplier, 1))):
                row = exact_dual(size, 0, added, multiplier)
                _require(F(row["value_numerator"], row["denominator"]) == expected, "hand-computed extreme count pair")
                hand_count += 1
    row = exact_dual(2, 1, 1, 2)
    _require(F(row["value_numerator"], row["denominator"]) == F(3, 2), "two-cell fractional expected query cost")
    hand_count += 1
    for size in range(2, spec["maximum_population"]+1):
        for count in range(size):
            for added in range(1, size-count+1):
                pairs = stopping_policy_pairs(size, count, added)
                pairs_count += len(pairs)
                for multiplier in spec["multipliers"]:
                    expected = min(cost+multiplier*error for cost, error in pairs)
                    row = exact_dual(size, count, added, multiplier)
                    _require(F(row["value_numerator"], row["denominator"]) == expected, "independent stopping-choice enumeration")
                    comparisons += 1
    return {"hand_comparisons": hand_count, "stopping_value_comparisons": comparisons,
            "distinct_cost_error_pairs_after_dominance_pruning": pairs_count,
            "interpretation": "Exhaustive deterministic stopping choices on explicit subsets, with dominated zero-error continuations and null-impossible certification pruned."}


def arbitrary_coordinate_checks(spec):
    comparisons = 0
    for size in range(2, spec["maximum_population"]+1):
        for count in range(size//2):
            for added in range(1, size//2-count+1):
                for multiplier in spec["multipliers"]:
                    expected = explicit_coordinate_value(size, count, added, multiplier)
                    row = exact_dual(size, count, added, multiplier)
                    _require(F(row["value_numerator"], row["denominator"]) == expected, "arbitrary-coordinate support-set oracle")
                    comparisons += 1
    return {"comparisons": comparisons,
            "interpretation": "Independent explicit-support Bellman oracle optimizes all coordinate choices; this checks the exchangeable-state compression on the registered small populations."}


def select_registered(rows):
    if not rows:
        raise ValueError("registered result list must be nonempty")
    best = max(rows, key=lambda row: F(row["dual_lower_exact"]))
    return {"multiplier": best["multiplier"], "dual_lower_exact": best["dual_lower_exact"],
            "dual_lower_decimal_down": best["dual_lower_decimal_down"],
            "census_cost": best["census_cost"], "census_to_lower_ratio_upper": best["census_to_lower_ratio_upper"],
            "globally_optimized_multiplier": False,
            "selection_scope": "Largest exact lower bound among only the registered multipliers"}


def calculate(protocol):
    validate_protocol(protocol)
    geometry = geometry_certificate(protocol["geometry"])
    tiny = tiny_stopping_checks(protocol["stopping_oracle"])
    coordinate = arbitrary_coordinate_checks(protocol["coordinate_oracle"])
    source = protocol["geometry"]
    rows = [dual_certificate(source["tail_population"], source["null_count"],
                             source["alternative_count"]-source["null_count"], multiplier,
                             F(source["delta"]), geometry["census_cost"]) for multiplier in protocol["multipliers"]]
    values = [F(row["lagrange_value_exact"]) for row in rows]
    errors = [F(row["minimizing_policy_error_exact"]) for row in rows]
    slopes = [(v1-v0)/(r1["multiplier"]-r0["multiplier"]) for r0, r1, v0, v1 in zip(rows, rows[1:], values, values[1:])]
    _require(all(v0 <= v1 for v0, v1 in zip(values, values[1:])), "Lagrange value monotonicity")
    _require(all(x >= y for x, y in zip(slopes, slopes[1:])) and all(0 <= x <= 1 for x in slopes), "Lagrange value concavity")
    _require(all(x >= y for x, y in zip(errors, errors[1:])), "minimizing policy error decreases with multiplier")
    return {"geometry_certificate": geometry, "tiny_stopping_checks": tiny,
            "arbitrary_coordinate_checks": coordinate, "registered_multiplier_results": rows,
            "registered_value_shape_checks": {"monotone": True, "concave": True, "policy_errors_nonincreasing": True},
            "selected_registered_certificate": select_registered(rows)}


def build_results(protocol, protocol_path):
    path = Path(protocol_path).resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 16 KiB limit")
    with path.open("rb") as stream:
        protocol_bytes = stream.read(MAX_PROTOCOL_BYTES+1)
    snapshot = parse_protocol(protocol_bytes)
    if protocol is not None and _canonical(protocol) != _canonical(snapshot):
        raise ValueError("supplied protocol differs from its file snapshot")
    snapshot = validate_protocol(snapshot)
    files = [Path(__file__).resolve(), ROOT/"tests/test_finite_decision.py", path,
             ROOT/"docs/finite-decision-theorem.md", ROOT/"docs/nonzero-minimax-theorem.md", IMPORTED_HELPER_PATH]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest() for file in files}
    _require(len(sources) == 6, "six distinct source pins")
    result = {"schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
              "protocol": snapshot, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "source_sha256": sources, **calculate(snapshot), "claim_boundary": snapshot["claim_boundary"]}
    current = {}
    for file in files:
        if file == path:
            with file.open("rb") as stream:
                data = stream.read(MAX_PROTOCOL_BYTES+1)
        else:
            data = file.read_bytes()
        current[key(file)] = hashlib.sha256(data).hexdigest()
    if current != sources:
        raise RuntimeError("a pinned checker, test, protocol, proof, or imported helper source changed during calculation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/finite_decision_protocol.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.exists():
            raise ValueError("output already exists; choose a new artifact path")
        result = build_results(None, args.protocol)
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
    except (ValueError, RuntimeError, OSError) as error:
        print("finite-decision checks: "+str(error), file=sys.stderr)
        return 2
    print("Passed exact finite-decision checks; saved registered lower certificate to "+str(args.out)+".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
