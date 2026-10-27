"""Exact monotone-placement prior certificates for the original full grid.

Only the registered placement family and multipliers are compared. The
integer Bellman optimizers are relaxed prior-pair tests, not valid auditors.
Standard library only; actual populations are kept symbolic.
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
import time

from experiments import check_finite_decision as previous

ROOT = Path(__file__).resolve().parents[1]
IMPORTED_DECISION_PATH = Path(previous.__file__).resolve()
IMPORTED_HELPER_PATH = Path(previous.IMPORTED_HELPER_PATH).resolve()
exact_weights = previous.exact_weights
MAX_PROTOCOL_BYTES = 16384
MAX_POPULATION = 2048
MAX_MULTIPLIER = 8192
MAX_INTEGER_BITS = 8192
DECIMAL_DIGITS = 9
CANONICAL_PROTOCOL = {
    "version": 1,
    "title": "Monotone placement and a stronger lower certificate for the original whole-grid decision",
    "status": "Fixed after exploratory mathematics and prior-pair screens, before the saved registered calculation; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_and_integer_dynamic_program",
    "geometry": {"prompts": 32, "pool_size": 64, "budgets": [1, 2, 4, 8, 16, 32, 64], "tau": "1/10", "epsilon": "1/160", "delta": "1/20", "total_items": 2048, "total_null_ones": 192, "added_unknown_ones": 13},
    "frontier_null_counts": {"first": 0, "last": 192},
    "frontier_definition": "For k=0..192 set b=192-k, fix the first H cells to zero and final b cells to one, and choose the smallest H with N=2048-H-b>=k+13 and fixed-bottom mass plus the first k unknown weights <=3/32 for every original target. Verify H-1 is infeasible whenever H>0.",
    "multipliers": [2048, 4096],
    "registered_frontier_evaluations": 386,
    "selection": "Largest exact dual lower bound among only the 193 maximal-unknown-population frontiers and two registered multipliers; no optimality claim over other priors or all multipliers",
    "clean_witness": {"head_zeros": 288, "fixed_bottom_ones": 112, "unknown_population": 1648, "null_unknown_ones": 80, "added_unknown_ones": 13, "multiplier": 4096, "integer_certificate_left": 5, "integer_certificate_right": 6524, "strict_expected_cost_lower": 1100},
    "sorting_max_items": 7,
    "sorting_weight_alphabet": [0, 1, 2],
    "sorting_matrix": "M=1..7, all decreasing rows from combinations_with_replacement({0,1,2},M), all assignments in {fixed-zero,unknown,fixed-one}^M, and all k=0..number-of-unknowns. Check sorting head zeros and bottom ones does not increase the worst k-subset risk.",
    "latent_max_population": 12,
    "latent_matrix": "larger=1..12, smaller=1..larger, q=0..smaller: C(larger,smaller)C(smaller,q)=C(larger,q)C(larger-q,smaller-q)",
    "zero_error_arithmetic": {"scope_delta": "0", "constant_fractional_loss": "3/32", "unseen_infeasible": 15, "unseen_feasible": 14, "randomized_lower": 2034, "deterministic_exact": 2036, "required_observed_zeros_binary": 1844, "adversarial_tail_ones": 192, "omitted_last_rank_cells": 12},
    "blind_mixture_arithmetic": {"scope_delta": "1/20", "zero_error_cost": 2036, "immediate_certificate_probability": "1/20", "expected_upper": "9671/5", "interpretation": "All allowed error is spent on blind immediate certification; this is an admissible comparison, not evidence-based efficiency."},
    "maximum_population": 2048,
    "maximum_multiplier": 8192,
    "maximum_integer_bits": 8192,
    "decimal_digits": 9,
    "arithmetic": "Exact rational placement constraints and independently implemented rolling Pascal/integer Bellman values, null-completion masses, costs, errors, and per-state checksums. No floating-point decision arithmetic or expanded actual population tables.",
    "state_checksum": "Same length-prefixed unsigned-big-endian SHA-256 state encoding as the frozen finite-decision checker; compare common-size cases in tests without mutating its population cap.",
    "progress": "Informational stderr progress every 16 completed frontier geometries once calculation exceeds 60 seconds; elapsed time is not stored in results.",
    "claim_boundary": "A lower-certificate improvement within a registered monotone prior-placement family, not a new Bellman algorithm, an optimal auditor, a globally optimal prior or multiplier, a model study, scientific priority, or independent human review. Zero-error and positive-error objectives are explicitly distinct; all older source-pinned files remain unchanged.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact monotone-placement check failed: "+message)


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


def validate_protocol(protocol):
    if _canonical(protocol) != _canonical(CANONICAL_PROTOCOL):
        raise ValueError("protocol differs from the exact canonical frozen protocol")
    _require(MAX_POPULATION == 2048 and MAX_MULTIPLIER == 8192 and MAX_INTEGER_BITS == 8192,
             "registered computational caps")
    return protocol


def _prefix_rows(rows):
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= 64:
        raise ValueError("requires one to 64 bounded monotone weight rows")
    size = len(rows[0])
    _integer(size, "row width", 1, 2048)
    prefixes = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != size:
            raise ValueError("weight rows must have equal bounded length")
        row = tuple(_fraction(value, "weight") for value in row)
        if row[-1] < 0 or any(x < y for x, y in zip(row, row[1:])):
            raise ValueError("weight rows must be nonnegative and decreasing")
        prefix = [F(0)]
        for weight in row:
            prefix.append(prefix[-1]+weight)
        prefixes.append(tuple(prefix))
    return tuple(prefixes)


def _worst_risks(prefixes, head, fixed, count):
    size = len(prefixes[0])-1
    return tuple(row[size]-row[size-fixed]+row[head+count]-row[head] for row in prefixes)


def _minimal_head_prefixes(prefixes, total_ones, count, added, threshold):
    size = len(prefixes[0])-1
    _integer(total_ones, "total null ones", 0, size-1)
    _integer(count, "unknown null ones", 0, total_ones)
    _integer(added, "added unknown ones", 1, size-total_ones)
    threshold = _fraction(threshold, "risk threshold")
    if threshold < 0:
        raise ValueError("risk threshold must be nonnegative")
    fixed = total_ones-count
    lower, upper = 0, size-total_ones-added
    if any(risk > threshold for risk in _worst_risks(prefixes, upper, fixed, count)):
        raise ValueError("no admissible head satisfies all row constraints")
    while lower < upper:
        middle = (lower+upper)//2
        if all(risk <= threshold for risk in _worst_risks(prefixes, middle, fixed, count)):
            upper = middle
        else:
            lower = middle+1
    risks = _worst_risks(prefixes, lower, fixed, count)
    predecessor = _worst_risks(prefixes, lower-1, fixed, count) if lower else None
    _require(all(risk <= threshold for risk in risks), "minimal head is feasible")
    _require(predecessor is None or any(risk > threshold for risk in predecessor), "head predecessor is infeasible")
    unknown = size-lower-fixed
    _require(unknown >= count+added, "alternative count fits the unknown population")
    return {"head_zeros": lower, "fixed_bottom_ones": fixed, "unknown_population": unknown,
            "null_unknown_ones": count, "added_unknown_ones": added, "worst_risks": risks,
            "predecessor_worst_risks": predecessor,
            "predecessor_infeasible": True if predecessor is not None else None}


def minimal_head(rows, total_ones, count, added, threshold):
    return _minimal_head_prefixes(_prefix_rows(rows), total_ones, count, added, threshold)


@lru_cache(maxsize=1)
def _original_prefixes():
    geometry = CANONICAL_PROTOCOL["geometry"]
    prompts, size = geometry["prompts"], geometry["pool_size"]
    rows = []
    for budget in geometry["budgets"]:
        weights = tuple(exact_weights(size, budget))
        _require(len(weights) == size and sum(weights, F(0)) == 1 and weights[0] == F(budget, size),
                 "normalized original winning-rank weights")
        rows.append(tuple(weight/prompts for weight in weights for _ in range(prompts)))
    prefixes = _prefix_rows(tuple(rows))
    _require(all(row[-1] == 1 for row in prefixes), "normalized original item weights")
    return prefixes


def placement_geometry(head, count):
    geometry = CANONICAL_PROTOCOL["geometry"]
    size, total, added = geometry["total_items"], geometry["total_null_ones"], geometry["added_unknown_ones"]
    _integer(count, "unknown null ones", 0, total)
    _integer(head, "fixed zero head", 0, size-total-added)
    fixed = total-count
    risks = _worst_risks(_original_prefixes(), head, fixed, count)
    threshold = F(geometry["tau"])-F(geometry["epsilon"])
    _require(F(total, size) == threshold, "null uniform risk equals the supplied margin threshold")
    excess = F(total+added, size)-F(geometry["tau"])
    _require(excess > 0, "alternative violates the originally declared uniform target")
    return {"head_zeros": head, "fixed_bottom_ones": fixed, "unknown_population": size-head-fixed,
            "null_unknown_ones": count, "added_unknown_ones": added,
            "alternative_unknown_ones": count+added,
            "null_worst_risks": {str(n): str(risk) for n, risk in zip(geometry["budgets"], risks)},
            "all_original_targets_margin_safe": all(risk <= threshold for risk in risks),
            "null_uniform_risk": str(threshold), "alternative_uniform_excess": str(excess),
            "original_declared_budgets": list(geometry["budgets"])}


def frontier_for_count(count):
    geometry = CANONICAL_PROTOCOL["geometry"]
    _integer(count, "frontier null count", 0, geometry["total_null_ones"])
    threshold = F(geometry["tau"])-F(geometry["epsilon"])
    raw = _minimal_head_prefixes(_original_prefixes(), geometry["total_null_ones"], count,
                                 geometry["added_unknown_ones"], threshold)
    result = placement_geometry(raw["head_zeros"], count)
    _require(result["all_original_targets_margin_safe"], "frontier whole-grid margin safety")
    predecessor = raw["predecessor_worst_risks"]
    result.update(predecessor_infeasible=raw["predecessor_infeasible"],
                  predecessor_worst_risks={str(n): str(risk) for n, risk in zip(geometry["budgets"], predecessor)} if predecessor else None,
                  predecessor_violation_budgets=[n for n, risk in zip(geometry["budgets"], predecessor) if risk > threshold] if predecessor else [])
    return result


def sorting_worst_case(weights, assignment, count):
    if not isinstance(weights, (tuple, list)) or not 1 <= len(weights) <= 7:
        raise ValueError("sorting row must have one to seven entries")
    if any(isinstance(w, bool) or not isinstance(w, (int, F)) for w in weights):
        raise ValueError("sorting weights must be exact integers or Fractions")
    if weights[-1] < 0 or any(x < y for x, y in zip(weights, weights[1:])):
        raise ValueError("sorting row must be nonnegative and decreasing")
    if not isinstance(assignment, (tuple, list)) or len(assignment) != len(weights):
        raise ValueError("assignment length must match the weights")
    for code in assignment:
        _integer(code, "assignment code", 0, 2)
    unknown = [weight for weight, code in zip(weights, assignment) if code == 1]
    _integer(count, "unknown positive count", 0, len(unknown))
    head, fixed = assignment.count(0), assignment.count(2)
    original = sum(weight for weight, code in zip(weights, assignment) if code == 2)+sum(unknown[:count])
    sorted_worst = (sum(weights[len(weights)-fixed:]) if fixed else 0)+sum(weights[head:head+count])
    _require(sorted_worst <= original, "monotone sorting does not increase worst-case risk")
    return {"original_worst": original, "sorted_worst": sorted_worst}


def latent_subset_identity(larger, smaller, positives):
    _integer(larger, "larger latent population", 1, 12)
    _integer(smaller, "smaller latent population", 1, larger)
    _integer(positives, "latent positive count", 0, smaller)
    left = comb(larger, smaller)*comb(smaller, positives)
    right = comb(larger, positives)*comb(larger-positives, smaller-positives)
    _require(left == right, "latent-subset uniform marginal identity")
    return {"left_count": left, "right_count": right}


def structural_checks(protocol):
    sorting = zero_count = all_count = 0
    for size in range(1, protocol["sorting_max_items"]+1):
        for ascending in itertools.combinations_with_replacement(protocol["sorting_weight_alphabet"], size):
            weights = tuple(reversed(ascending))
            for assignment in itertools.product(range(3), repeat=size):
                unknown = assignment.count(1)
                for count in range(unknown+1):
                    sorting_worst_case(weights, assignment, count)
                    sorting += 1
                    zero_count += count == 0
                    all_count += count == unknown
    latent = 0
    for larger in range(1, protocol["latent_max_population"]+1):
        for smaller in range(1, larger+1):
            for positives in range(smaller+1):
                latent_subset_identity(larger, smaller, positives)
                latent += 1
    return {"sorting_inequality_checks": sorting, "zero_unknown_positive_boundary_checks": zero_count,
            "all_unknown_positive_boundary_checks": all_count, "latent_subset_identity_checks": latent,
            "interpretation": "Finite arithmetic support for the sorting and latent-mixture proofs; no finite matrix establishes the universal structural theorem by itself."}


def zero_error_certificates():
    geometry = CANONICAL_PROTOCOL["geometry"]
    size = geometry["total_items"]
    p0 = F(geometry["tau"])-F(geometry["epsilon"])
    epsilon = F(geometry["epsilon"])
    fifteen, fourteen = 15*(1-p0)/size, 14*(1-p0)/size
    _require(fifteen > epsilon >= fourteen, "constant-fractional zero-error completion boundary")
    required_zeros = size-(F(geometry["tau"])*size).__floor__()
    _require(required_zeros == 1844 and 192+required_zeros == 2036, "deterministic zero-error adversarial count arithmetic")
    adversary = placement_geometry(1024, 192)
    _require(adversary["all_original_targets_margin_safe"], "every deterministic tail-adversary completion is safe for the original grid")
    omitted = 12
    _require(F(omitted, size) < epsilon, "uniform omitted mass fits margin")
    for budget in geometry["budgets"]:
        omitted_mass = omitted*exact_weights(geometry["pool_size"], budget)[-1]/geometry["prompts"]
        _require(omitted_mass <= epsilon, "last-rank omission valid for every original budget")
    zero_error_upper = size-omitted
    positive_delta = F(geometry["delta"])
    mixture = (1-positive_delta)*zero_error_upper
    _require(mixture == F(9671, 5), "exact blind error-spending comparison")
    return {"zero_error_scope_delta": "0", "randomized_zero_error_lower": size-14,
            "deterministic_zero_error_exact": zero_error_upper,
            "fifteen_unseen_uniform_risk_increase": str(fifteen),
            "fourteen_unseen_uniform_risk_increase": str(fourteen),
            "required_observed_zeros_binary": required_zeros, "adversarial_tail_ones": 192,
            "deterministic_adversary_geometry": adversary,
            "omitted_last_rank_cells": omitted, "maximum_omitted_target_mass": str(F(omitted, size)),
            "blind_mixture_scope_delta": str(positive_delta), "blind_delta_mixture_expected_upper": str(mixture),
            "interpretation": "These are exact arithmetic checks of the separately proved zero-error and blind-mixture statements. The randomized zero-error lower and deterministic exact result do not apply as lower bounds at positive delta."}


def select_registered(rows):
    if not rows:
        raise ValueError("registered result list must be nonempty")
    best = max(rows, key=lambda row: F(row["dual_lower_exact"]))
    lower = F(best["dual_lower_exact"])
    result = {"multiplier": best["multiplier"], "dual_lower_exact": best["dual_lower_exact"],
              "dual_lower_decimal_down": best["dual_lower_decimal_down"],
              "globally_optimized_prior_or_multiplier": False,
              "selection_scope": "Only registered maximal-unknown-population frontiers and registered multipliers; separate clean witness excluded",
              "blind_mixture_expected_upper": "9671/5",
              "blind_mixture_to_lower_ratio_upper": decimal_bound(F(9671, 5)/lower, upward=True) if lower > 0 else None}
    for key in ("head_zeros", "fixed_bottom_ones", "null_unknown_ones", "unknown_population"):
        if key in best:
            result[key] = best[key]
    return result


def calculate(protocol):
    validate_protocol(protocol)
    structures = structural_checks(protocol)
    zero_error = zero_error_certificates()
    geometry = protocol["geometry"]
    frontiers, all_rows = [], []
    start = time.monotonic()
    first, last = protocol["frontier_null_counts"]["first"], protocol["frontier_null_counts"]["last"]
    for count in range(first, last+1):
        frontier = frontier_for_count(count)
        certificates = []
        for multiplier in protocol["multipliers"]:
            row = dual_certificate(frontier["unknown_population"], count, geometry["added_unknown_ones"],
                                   multiplier, F(geometry["delta"]), geometry["total_items"])
            row.update(head_zeros=frontier["head_zeros"], fixed_bottom_ones=frontier["fixed_bottom_ones"],
                       unknown_population=frontier["unknown_population"], null_unknown_ones=count)
            certificates.append(row)
            all_rows.append(row)
        frontier["registered_dual_certificates"] = certificates
        frontiers.append(frontier)
        completed = count-first+1
        if completed % 16 == 0 and time.monotonic()-start >= 60:
            print(f"monotone-placement progress: {completed}/{last-first+1} frontier geometries, {len(all_rows)} registered duals", file=sys.stderr, flush=True)
    _require(len(all_rows) == protocol["registered_frontier_evaluations"], "complete registered frontier matrix")
    witness = protocol["clean_witness"]
    clean_geometry = placement_geometry(witness["head_zeros"], witness["null_unknown_ones"])
    _require(clean_geometry["all_original_targets_margin_safe"] and clean_geometry["unknown_population"] == witness["unknown_population"]
             and clean_geometry["fixed_bottom_ones"] == witness["fixed_bottom_ones"], "separate clean witness geometry")
    clean = dual_certificate(witness["unknown_population"], witness["null_unknown_ones"], witness["added_unknown_ones"],
                             witness["multiplier"], F(geometry["delta"]), geometry["total_items"])
    residual = witness["integer_certificate_left"]*clean["value_numerator"]-witness["integer_certificate_right"]*clean["denominator"]
    _require(residual > 0 and F(clean["dual_lower_exact"]) > witness["strict_expected_cost_lower"], "strict clean-witness integer lower certificate")
    clean.update(integer_certificate_left=witness["integer_certificate_left"], integer_certificate_right=witness["integer_certificate_right"],
                 strict_integer_residual=residual, strict_expected_cost_lower=witness["strict_expected_cost_lower"],
                 excluded_from_registered_frontier_selection=True)
    return {"structural_checks": structures, "zero_error_and_blind_mixture_checks": zero_error,
            "frontier_geometry_count": len(frontiers), "registered_frontier_dual_count": len(all_rows),
            "total_actual_geometry_dual_count": len(all_rows)+1, "frontiers": frontiers,
            "separate_clean_witness": {"geometry": clean_geometry, "dual_certificate": clean},
            "selected_registered_certificate": select_registered(all_rows)}


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
    files = [Path(__file__).resolve(), ROOT/"tests/test_monotone_placement.py", path,
             ROOT/"docs/monotone-placement-theorem.md", ROOT/"docs/finite-decision-theorem.md",
             IMPORTED_DECISION_PATH, IMPORTED_HELPER_PATH]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest() for file in files}
    _require(len(sources) == 7, "seven distinct direct and transitive source pins")
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
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/monotone_placement_protocol.json")
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
        print("monotone-placement checks: "+str(error), file=sys.stderr)
        return 2
    print("Passed exact monotone-placement checks; saved registered frontier certificates to "+str(args.out)+".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
