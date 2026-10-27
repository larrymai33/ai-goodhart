"""Bounded exact checks for high-budget finite-table saturation.

Standard library only. Fixed-count priors are proof devices, not sampled
model labels. Large prompt populations and confidence examples remain
symbolic. Finite arithmetic does not prove concentration, novelty, or
practical savings. Every logarithmic comparison uses outward endpoints.
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
exact_weights, log_interval = sharp.exact_weights, sharp.log_interval
fraction_text = sharp.fraction_text
LOG_TERMS, ROUND_BITS = sharp.LOG_TERMS, sharp.ROUND_BITS
MAX_PROTOCOL_BYTES = 16384
CANONICAL_PROTOCOL = {
    "version": 1,
    "title": "Finite saturation for high-budget best-of-n grids",
    "status": "Fixed after exploratory proof and agent review, before the saved full calculation; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": {
        "objective": "One globally delta-valid, all-safe-complete auditor; worst-case expected distinct labels over fixed tables with max R_n <= tau-epsilon",
        "range": "0<tau<=1/8; 0<epsilon<=tau/16; 0<delta<=1/4; min(K)>=m/4; every integer P>=1",
        "rate": "F=min(P*k_epsilon,sum_r min(P,H*e_r)); H=tau*log(1/delta)/epsilon^2; e_r=max_n w_n(r)",
        "lower_constant": 2097152,
        "upper_constant": 12288,
        "slice_lower_constant": 1024,
        "rank_lower_constant": 32768,
        "geometry_constant": 40,
        "scope": "Every originally declared target is retained; no density or replication condition; no claim for grids with min(K)<m/4",
    },
    "reciprocal_max_population": 32,
    "reciprocal_matrix": "N=2..maximum; k=0..floor(N/2); t=0..floor(N/4); exact hypergeometric expectation",
    "conditional_populations": [8, 16, 32, 64],
    "conditional_matrix": "k>=0,d>=1,k+d<=N/2; t in {0,floor(N/4)}; every feasible null success count",
    "slice_populations": [16, 64, 512, 4096],
    "slice_matrix": "k in {0,N//32,N//8}; d in {1,max(1,N//64),N//4}; skip duplicates and k+d>N/2; preserve both floor endpoints",
    "grid_max_pool_size": 10,
    "grid_matrix": "All nonempty subsets of {ceil(m/4),...,m}, for every m=1..maximum",
    "prompt_counts": [1, 32, 64, 1000000],
    "taus": ["1/8", "1/16"],
    "relative_margins": ["1/16", "1/64"],
    "deltas": ["1/4", "1/20"],
    "grid_checks": "Outward F_upper<=40*A16_lower; exact clipping/prefix identity; envelope pairing; 6/7 weight ratios for m>=5; 3/4 tail ratios; m<=4 and n/a=4 endpoints; fractional fixed-count priors and small-P*tau hidden subsets",
    "selected_prior_witnesses": [
        {"prompts": 1, "tau": "1/8", "epsilon": "1/128", "weight": "1/4", "delta": "1/4"},
        {"prompts": 31, "tau": "1/8", "epsilon": "1/128", "weight": "1/4", "delta": "1/4"},
        {"prompts": 32, "tau": "1/8", "epsilon": "1/128", "weight": "1/4", "delta": "1/4"},
        {"prompts": 63, "tau": "1/16", "epsilon": "1/256", "weight": "1/4", "delta": "1/20"},
        {"prompts": 64, "tau": "1/16", "epsilon": "1/256", "weight": "1/4", "delta": "1/20"},
        {"prompts": 1000000, "tau": "1/8", "epsilon": "1/512", "weight": "1/4", "delta": "1/20"},
    ],
    "confidence_cap_exponents": [7, 12, 20, 32],
    "confidence_cap_construction": "P=1,tau=1/8,epsilon=1/128,L=4^j,m=2^(3j),n=m/2; exact seven-factor tail and first j rank weights prove C*<=7 and G>=j; never construct exp(-L) or a population table",
    "practical_case": {"prompts": 32, "pool_size": 64, "budgets": [16, 32, 64], "tau": "1/10", "epsilon": "1/160", "delta": "1/20", "different_declared_grid_from_original_study": True},
    "log_series_terms": 32,
    "dyadic_rounding_bits": 80,
    "claim_boundary": "Finite arithmetic checks support the proof implementation, not concentration, scientific priority, useful numerical constants, real-model performance, or independent human review. All pre-existing source-pinned files and the audit engine remain unchanged.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact finite-saturation check failed: "+message)


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name+" must be an exact integer or Fraction")
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 256:
        raise ValueError(name+" exceeds the rational bit limit")
    return value


def _parameters(tau, epsilon, delta):
    tau, epsilon, delta = (_fraction(x, name) for x, name in
                           ((tau, "tau"), (epsilon, "epsilon"), (delta, "delta")))
    if not (0 < tau <= F(1, 8) and 0 < epsilon <= tau/16 and 0 < delta <= F(1, 4)):
        raise ValueError("parameters must satisfy the finite-saturation theorem range")
    return tau, epsilon, delta


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def validate_protocol(protocol):
    if _canonical(protocol) != _canonical(CANONICAL_PROTOCOL):
        raise ValueError("protocol differs from the exact canonical frozen protocol")
    _require(LOG_TERMS == 32 and ROUND_BITS == 80, "frozen helper rounding constants")
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


def ceil_fraction(value):
    return -((-value.numerator)//value.denominator)


def floor_interval(lo, hi, divisor=1):
    lo, hi = _fraction(lo, "lower endpoint"), _fraction(hi, "upper endpoint")
    _integer(divisor, "floor divisor", 1, 1024)
    if not 0 <= lo <= hi:
        raise ValueError("floor endpoints must satisfy 0<=lower<=upper")
    left, right = lo//divisor, hi//divisor
    return left, right, "resolved" if left == right else "explicit_interval"


def reciprocal_expectation(size, ones, queried):
    _integer(size, "hypergeometric population", 2, 64)
    _integer(ones, "success count", 0, size)
    _integer(queried, "query count", 0, size)
    denominator = comb(size, queried)
    value = sum((F(comb(ones, seen)*comb(size-ones, queried-seen),
                   denominator*(ones-seen+1))
                 for seen in range(max(0, queried-(size-ones)), min(ones, queried)+1)), F(0))
    bound = F(size+1, (ones+1)*(size+1-queried))
    _require(value <= bound, "reciprocal hypergeometric expectation")
    return value


def conditional_majorant(size, ones, added, queried, seen):
    _integer(size, "conditional population", 2, 4096)
    _integer(ones, "null count", 0, size//2)
    _integer(added, "added count", 1, size//2-ones)
    _integer(queried, "queries before observation", 0, size//4)
    _integer(seen, "observed successes", max(0, queried-(size-ones)), min(ones, queried))
    u, v = F(ones-seen, size-queried), F(ones+added-seen, size-queried)
    majorant = (v-u)**2/(v*(1-v))
    bound = F(4*added**2, size*(ones+added-seen))
    _require(majorant <= bound, "conditional rational Bernoulli KL majorant")
    return {"null_probability": fraction_text(u), "alternative_probability": fraction_text(v),
            "bernoulli_kl_majorant": fraction_text(majorant), "reciprocal_majorant": fraction_text(bound)}


def slice_certificate(size, ones, added, delta):
    _integer(size, "slice population", 2, 1000000)
    _integer(ones, "null count", 0, size//2)
    _integer(added, "added count", 1, size//2-ones)
    delta = _fraction(delta, "delta")
    if not 0 < delta <= F(1, 4):
        raise ValueError("delta must lie in (0,1/4]")
    lo, hi = log_interval(delta)
    rate_lo, rate_hi = min(F(size), F(size*(ones+1), added**2)*lo), min(F(size), F(size*(ones+1), added**2)*hi)
    left, right, status = floor_interval(rate_lo, rate_hi, 128)
    result = {"population": size, "null_count": ones, "added_count": added, "delta": str(delta),
              "log_lower": fraction_text(lo), "log_upper": fraction_text(hi),
              "rate_lower": fraction_text(rate_lo), "rate_upper": fraction_text(rate_hi),
              "cap_lower": left, "cap_upper": right, "floor_status": status,
              "expected_queries_lower": fraction_text(rate_lo/1024)}
    if rate_hi < 256:
        _require(F(3, 4) >= rate_hi/1024, "zero-query lower bound covers small rate")
        result["branch"] = "zero-query argument"
    elif rate_lo >= 256:
        upper = F(8*added**2*right, size*(ones+1))
        log_two_hi = log_interval(F(1, 4))[1]/2
        lower = 3*lo/4-log_two_hi
        _require(F(left) >= rate_hi/256 and F(right) <= F(size, 128), "outward finite cap geometry")
        # An unresolved floor is retained only if these conservative bounds
        # still certify the contradiction; otherwise the check aborts.
        _require(upper <= hi/16 and lower > upper, "outward finite transcript information contradiction")
        result.update(branch="finite transcript cap", transcript_kl_upper=fraction_text(upper),
                      binary_information_lower=fraction_text(lower))
    else:
        # Preserve an ambiguous boundary rather than choosing a branch from a rounded log.
        _require(F(3, 4) >= rate_hi/1024, "zero-query bound covers bracket around 256")
        result["branch"] = "explicit threshold interval"
    return result


@lru_cache(maxsize=2048)
def _geometry(size, budgets):
    rows = tuple(tuple(exact_weights(size, n)) for n in budgets)
    for n, row in zip(budgets, rows):
        _require(len(row) == size and sum(row, F(0)) == 1 and row[0] == F(n, size), "normalized original target row")
        _require(all(x >= y >= 0 for x, y in zip(row, row[1:])), "monotone original target weights")
    envelope = tuple(max(row[r] for row in rows) for r in range(size))
    tails = tuple(sum(rows[0][k:], F(0)) for k in range(size+1))
    for row in rows:
        _require(all(sum(row[k:], F(0)) <= tails[k] for k in range(size+1)), "original minimum budget controls tail")
        ratios = tuple(weight/base for weight, base in zip(row, rows[0]) if base)
        _require(all(0 <= x <= 4 for x in ratios), "single group includes n/a=4 endpoint")
        _require(all(x >= y for x, y in zip(ratios, ratios[1:])), "original target likelihood ratios decrease")
    for r in range(size):
        if 2*r < size:
            _require(envelope[2*r] <= 4*envelope[r]**2, "envelope pairing inequality")
    _require(all(y <= 3*x/4 for x, y in zip(tails, tails[1:])), "three-quarter tail probability ratio")
    adjacent = tuple(y/x for x, y in zip(envelope, envelope[1:]) if x)
    if size >= 5:
        _require(all(ratio <= F(6, 7) for ratio in adjacent), "six-sevenths envelope weight ratio")
    else:
        _require(all(weight >= F(1, 6) for weight in envelope if weight), "small-pool positive weight endpoint")
    return envelope, tails, max(adjacent, default=F(0))


def _grid_inputs(prompts, size, budgets):
    _integer(prompts, "prompts", 1, 1000000)
    _integer(size, "pool size", 1, 64)
    if not isinstance(budgets, (list, tuple)) or not 1 <= len(budgets) <= size:
        raise ValueError("budgets must be a nonempty bounded sequence")
    for n in budgets:
        _integer(n, "budget", 1, size)
    if list(budgets) != sorted(set(budgets)) or 4*budgets[0] < size:
        raise ValueError("budgets must be distinct increasing and satisfy min(K)>=m/4")
    return tuple(budgets)


def rank_prior_case(prompts, tau, epsilon, weight, delta):
    _integer(prompts, "prompts", 1, 1000000)
    tau, epsilon, delta = _parameters(tau, epsilon, delta)
    weight = _fraction(weight, "rank weight")
    if not 16*epsilon <= weight <= 1:
        raise ValueError("rank weight must lie in [16epsilon,1]")
    lo, hi = log_interval(delta)
    p0 = tau-epsilon
    h_lo, h_hi = tau*lo/epsilon**2, tau*hi/epsilon**2
    result = {"prompts": prompts, "tau": str(tau), "epsilon": str(epsilon), "weight": str(weight), "delta": str(delta),
              "null_rank_average": fraction_text(p0),
              "rank_lower_target_upper": fraction_text(min(F(prompts), h_hi*weight**2)/32768)}
    if prompts*tau >= 4:
        count = ceil_fraction(prompts*p0)
        amplitude = prompts*p0/count
        added = ceil_fraction(2*epsilon*prompts/(amplitude*weight))
        increase = amplitude*weight*added/prompts
        _require(amplitude >= F(3, 4) and count+added < F(prompts, 2), "rounded null/alternative count feasibility")
        _require(amplitude*count/prompts == p0 and increase >= 2*epsilon, "exact safe profile and unsafe increase")
        raw_lower = min(F(prompts), F(prompts*(count+1), added**2)*lo)/1024
        _require(raw_lower >= min(F(prompts), h_hi*weight**2)/32768, "slice bound implies rank lower bound")
        result.update(branch="fixed-count fractional prior", null_count=count, added_count=added,
                      alternative_count=count+added, amplitude=fraction_text(amplitude),
                      risk_increase=fraction_text(increase), slice_cost_lower=fraction_text(raw_lower))
    else:
        amplitude = 1-p0
        subset = (epsilon*prompts/(amplitude*weight)).numerator//(epsilon*prompts/(amplitude*weight)).denominator+1
        increase = amplitude*weight*subset/prompts
        _require(1 <= subset <= prompts and increase > epsilon, "strict hidden-subset alternative")
        raw_lower = min(F(prompts), F(prompts, subset)*lo)/256
        b_lo, b_hi = min(F(prompts), lo*weight/epsilon), min(F(prompts), hi*weight/epsilon)
        _require(raw_lower >= b_hi/1024, "hidden-subset rounding constant")
        _require(min(F(prompts), h_hi*weight**2) <= 3*b_lo, "small-population transfer to squared weight")
        result.update(branch="constant-table hidden subset", hidden_subset_size=subset,
                      risk_increase=fraction_text(increase), hidden_subset_cost_lower=fraction_text(raw_lower))
    return result


def dense_grid_case(prompts, size, budgets, tau, epsilon, delta):
    budgets = _grid_inputs(prompts, size, budgets)
    tau, epsilon, delta = _parameters(tau, epsilon, delta)
    envelope, tails, ratio = _geometry(size, budgets)
    lo, hi = log_interval(delta)
    h_lo, h_hi = tau*lo/epsilon**2, tau*hi/epsilon**2
    prefix = next(k for k, tail in enumerate(tails) if tail <= epsilon)
    retained = tuple(weight for weight in envelope if weight >= 16*epsilon)
    _require(retained and prefix <= 16*len(retained), "deterministic cap versus retained rank count")
    clipped_lo = sum((min(F(prompts), h_lo*w) for w in envelope), F(0))
    clipped_hi = sum((min(F(prompts), h_hi*w) for w in envelope), F(0))
    for h, clipped in ((h_lo, clipped_lo), (h_hi, clipped_hi)):
        objective = min(F(prompts*k)+h*sum(envelope[k:], F(0)) for k in range(size+1))
        _require(clipped == objective, "exact clipped envelope equals optimal prefix objective")
        squares = sum((min(F(prompts), h*w*w) for w in envelope), F(0))
        _require(clipped <= 8*squares, "paired squared-envelope comparison")
    a_lo = sum((min(F(prompts), h_lo*w*w) for w in retained), F(0))
    a_hi = sum((min(F(prompts), h_hi*w*w) for w in retained), F(0))
    f_lo, f_hi = min(F(prompts*prefix), clipped_lo), min(F(prompts*prefix), clipped_hi)
    _require(f_hi <= 40*a_lo, "outward capped geometry F_upper<=40*A16_lower")
    large = small = 0
    for weight in retained:
        prior = rank_prior_case(prompts, tau, epsilon, weight, delta)
        large += prior["branch"] == "fixed-count fractional prior"
        small += prior["branch"] == "constant-table hidden subset"
    return {"prompts": prompts, "pool_size": size, "budgets": list(budgets), "tau": str(tau), "epsilon": str(epsilon), "delta": str(delta),
            "envelope": list(map(fraction_text, envelope)), "maximum_adjacent_weight_ratio": fraction_text(ratio),
            "prefix_ranks": prefix, "prefix_label_cost": prompts*prefix, "retained_ranks": len(retained),
            "H_lower": fraction_text(h_lo), "H_upper": fraction_text(h_hi),
            "clipped_lower": fraction_text(clipped_lo), "clipped_upper": fraction_text(clipped_hi),
            "F_lower": fraction_text(f_lo), "F_upper": fraction_text(f_hi),
            "A16_lower": fraction_text(a_lo), "A16_upper": fraction_text(a_hi),
            "fixed_count_rank_checks": large, "hidden_subset_rank_checks": small,
            "clipped_strictly_below_prefix": clipped_hi < prompts*prefix,
            "geometry_certified_outward": True}


def confidence_counterexample(exponent):
    _integer(exponent, "confidence exponent", 7, 32)
    size, log_confidence = 2**(3*exponent), 4**exponent
    budget = size//2
    tail = F(1)
    for r in range(7):
        tail *= F(budget-r, size-r)
    _require(tail <= F(1, 128), "seven queried ranks certify every margin table")
    weight = F(1, 2)
    h = 2048*log_confidence
    for rank in range(1, exponent+1):
        _require(h*weight >= 1, "each checked rank contributes one to clipped cost")
        if rank < exponent:
            weight *= F(size-rank-budget+1, size-rank)
    return {"exponent": exponent, "prompts": 1, "pool_size": size, "budget": budget,
            "tau": "1/8", "epsilon": "1/128", "confidence_log_exact": log_confidence,
            "confidence": "delta=exp(-L), represented only through exact L",
            "delta_numerically_constructed": False, "population_table_allocated": False,
            "prefix_product_factors": 7, "tail_after_seven_ranks": fraction_text(tail),
            "prefix_cost_upper": 7, "rank_weights_checked": exponent, "clipped_cost_lower": exponent,
            "last_checked_weight_lower": fraction_text(sharp.round_down(weight)),
            "clipped_to_prefix_ratio_lower": fraction_text(F(exponent, 7))}


def reciprocal_checks(maximum):
    _integer(maximum, "reciprocal maximum", 2, 32)
    cases = zero_count = 0
    for size in range(2, maximum+1):
        for ones in range(size//2+1):
            for queried in range(size//4+1):
                value = reciprocal_expectation(size, ones, queried)
                _require(value <= F(2, ones+1), "reciprocal expectation within factor two")
                cases += 1
                zero_count += ones == 0
    return {"cases": cases, "zero_success_count_cases": zero_count, "maximum_population": maximum}


def conditional_checks(populations):
    cases = zero_remaining = 0
    for size in populations:
        for ones in range(size//2):
            for added in range(1, size//2-ones+1):
                for queried in sorted({0, size//4}):
                    for seen in range(max(0, queried-(size-ones)), min(ones, queried)+1):
                        conditional_majorant(size, ones, added, queried, seen)
                        cases += 1
                        zero_remaining += seen == ones
    return {"populations": list(populations), "feasible_histories": cases, "zero_remaining_null_success_histories": zero_remaining,
            "interpretation": "Exact rational majorants; no numerical evaluation of KL or stochastic transcript simulation"}


def slice_checks(protocol):
    cases = []
    for size in protocol["slice_populations"]:
        for ones in sorted({0, size//32, size//8}):
            for added in sorted({1, max(1, size//64), size//4}):
                if ones+added <= size//2:
                    for delta in map(F, protocol["deltas"]):
                        cases.append(slice_certificate(size, ones, added, delta))
    return {"cases": len(cases), "finite_cap_cases": sum(x["branch"] == "finite transcript cap" for x in cases),
            "zero_query_cases": sum(x["branch"] == "zero-query argument" for x in cases),
            "threshold_interval_cases": sum(x["branch"] == "explicit threshold interval" for x in cases),
            "unresolved_floor_intervals": sum(x["floor_status"] != "resolved" for x in cases),
            "selected_certificates": [x for x in cases if x["population"] == 4096 and x["null_count"] in (0, 128) and x["added_count"] == 1]}


def grid_checks(protocol):
    counts = {"grids": 0, "parameter_cases": 0, "n_over_a_four_endpoint_grids": 0,
              "small_pool_grids": 0, "fixed_count_rank_checks": 0, "hidden_subset_rank_checks": 0,
              "clipped_strictly_below_prefix_cases": 0, "outward_geometry_certificates": 0}
    profiles = tuple((prompts, F(tau), F(tau)*F(relative), F(delta))
                     for prompts, tau, relative, delta in itertools.product(
                         protocol["prompt_counts"], protocol["taus"], protocol["relative_margins"], protocol["deltas"]))
    for size in range(1, protocol["grid_max_pool_size"]+1):
        candidates = tuple(range((size+3)//4, size+1))
        for length in range(1, len(candidates)+1):
            for budgets in itertools.combinations(candidates, length):
                counts["grids"] += 1
                counts["n_over_a_four_endpoint_grids"] += budgets[-1] == 4*budgets[0]
                counts["small_pool_grids"] += size <= 4
                for prompts, tau, epsilon, delta in profiles:
                    case = dense_grid_case(prompts, size, budgets, tau, epsilon, delta)
                    counts["parameter_cases"] += 1
                    for key in ("fixed_count_rank_checks", "hidden_subset_rank_checks"):
                        counts[key] += case[key]
                    counts["clipped_strictly_below_prefix_cases"] += case["clipped_strictly_below_prefix"]
                    counts["outward_geometry_certificates"] += case["geometry_certified_outward"]
    _require(counts["clipped_strictly_below_prefix_cases"] > 0, "symbolic prompt counts reach the statistical regime")
    return counts


def practical_case(parameters):
    if _canonical(parameters) != _canonical(CANONICAL_PROTOCOL["practical_case"]):
        raise ValueError("practical case differs from the restricted declared grid")
    result = dense_grid_case(parameters["prompts"], parameters["pool_size"], parameters["budgets"],
                             F(parameters["tau"]), F(parameters["epsilon"]), F(parameters["delta"]))
    result.update(different_declared_grid_from_original_study=True,
                  theorem_lower=fraction_text(F(result["F_lower"])/2097152),
                  available_upper=fraction_text(min(F(result["prefix_label_cost"]), 12288*F(result["clipped_upper"]))),
                  interpretation="This declared grid [16,32,64] is different from the original study's full grid; its certificate does not certify omitted budgets.")
    return result


def calculate(protocol):
    validate_protocol(protocol)
    witnesses = [rank_prior_case(case["prompts"], F(case["tau"]), F(case["epsilon"]), F(case["weight"]), F(case["delta"]))
                 for case in protocol["selected_prior_witnesses"]]
    return {"reciprocal_checks": reciprocal_checks(protocol["reciprocal_max_population"]),
            "conditional_majorant_checks": conditional_checks(protocol["conditional_populations"]),
            "slice_cap_checks": slice_checks(protocol), "dense_grid_checks": grid_checks(protocol),
            "selected_rounded_prior_witnesses": witnesses,
            "confidence_cap_counterexamples": [confidence_counterexample(j) for j in protocol["confidence_cap_exponents"]],
            "practical_restricted_grid": practical_case(protocol["practical_case"])}


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
    files = [Path(__file__).resolve(), ROOT/"tests/test_finite_saturation.py", path,
             ROOT/"docs/finite-saturation-theorem.md", ROOT/"docs/nonzero-minimax-theorem.md", IMPORTED_HELPER_PATH]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest() for file in files}
    _require(len(sources) == 6, "six distinct source pins")
    result = {"schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
              "protocol": snapshot, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(), "source_sha256": sources,
              **calculate(snapshot),
              "rounding": {"bits": ROUND_BITS, "log_series_terms": LOG_TERMS,
                           "geometry": "F_upper uses H_upper; A16_lower uses H_lower, so the checked inequality is conservative.",
                           "caps": "Both floor endpoints are retained. Unresolved brackets are explicit when conservative inequalities certify the argument; otherwise the calculation aborts.",
                           "priors": "All counts, amplitudes, and alternative risk shifts are exact fractions; comparisons use lower cost and upper target endpoints.",
                           "counterexample": "L=4^j is exact; delta=exp(-L) is never numerically constructed; the final checked weight is rounded down for display."},
              "claim_boundary": snapshot["claim_boundary"]}
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
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/finite_saturation_protocol.json")
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
        print("finite-saturation checks: "+str(error), file=sys.stderr)
        return 2
    print(f"Passed bounded exact checks; saved {result['dense_grid_checks']['parameter_cases']} dense-grid cases to {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
