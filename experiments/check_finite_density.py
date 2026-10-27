"""Bounded exact checks for finite-density fixed-table certification.

Standard library only. Binary enumeration is a finite proof-device prior,
not sampled study labels. Large populations remain symbolic. Arithmetic
checks do not establish concentration, priority, or useful finite savings.
"""

import argparse
from fractions import Fraction as F
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
log_interval = sharp.log_interval
fraction_text = sharp.fraction_text
LOG_TERMS, ROUND_BITS = sharp.LOG_TERMS, sharp.ROUND_BITS
MAX_PROTOCOL_BYTES = 16384
CANONICAL_PROTOCOL = {
    "version": 1,
    "title": "Finite-density nonzero minimax certification and prefix-census limits",
    "status": "Fixed after exploratory proof and separate agent review, before the saved broader calculation; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": {
        "objective": "One globally delta-valid, all-safe-complete auditor; worst-case expected distinct labels over fixed tables with max R_n <= tau-epsilon",
        "range": "0<tau<=1/8; 0<epsilon<=tau/16; 0<delta<=1/4",
        "lower_density": "Pm/max(K)>=4*tau*log(4/delta)/epsilon^2",
        "lower_constant": 16384,
        "statistical_upper_constant": 49152,
        "prefix_upper": "P*k_epsilon, where k_epsilon is the shortest prefix with C(m-k,min(K))/C(m,min(K))<=epsilon",
        "scope": "Arbitrary nonempty declared grids; global certification, fixed labels, supplied margin. No universal min(census,Z*tau*log(1/delta)/epsilon^2) lower law.",
    },
    "abel_max_pool_size": 24, "abel_prompt_counts": [1, 3],
    "binary_max_pool_size": 6, "binary_prompt_counts": [1, 2], "binary_max_items": 10,
    "binary_lemma_parameters": {"tau": "1/4", "epsilon": "1/8", "p": "1/8", "scope": "Standalone monotone-row lemma, outside the minimax theorem parameter range"},
    "certificate_taus": ["1/8", "1/16"], "relative_margins": ["1/16", "1/64"],
    "certificate_deltas": ["1/4", "1/20"],
    "symbolic_geometries": [{"prompts": 1, "max_budget": 16}, {"prompts": 32, "max_budget": 64}],
    "profile_construction": "m=ceil(N*4*tau*log_upper(4/delta)/(P*epsilon^2)); product-prior p=tau-2epsilon, q=p+12epsilon; kappa=256epsilon^2/tau; band cap B=ceil(log(1/delta)/(2kappa))",
    "tail_max_pool_size": 32, "tail_margins": ["1/8", "1/32", "1/128"],
    "counterexample_exponents": [8, 12, 16, 24],
    "counterexample_construction": "P=1; m=2^(3k); K={m/2}; epsilon=2^-k; tau=1/8; delta=1/4; query first k ranks then census fallback",
    "practical_case": {"prompts": 32, "pool_size": 64, "budgets": [1, 2, 4, 8, 16, 32, 64], "tau": "1/10", "epsilon": "1/160", "delta": "1/20"},
    "log_series_terms": 32, "dyadic_rounding_bits": 80,
    "claim_boundary": "Finite arithmetic checks support implementation, not stochastic concentration, novelty, practical savings, real-model usefulness, or independent human ownership. Existing CLI and frozen paper snapshots remain unchanged.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact finite-density check failed: "+message)


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name+" must be an exact integer or Fraction")
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 256:
        raise ValueError(name+" exceeds the exact-number bit limit")
    return value


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def validate_protocol(protocol):
    """Accept only the complete frozen matrix, including its claim metadata."""
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


def log_bounds(delta):
    """Enclose log(1/delta); the frozen helper itself accepts delta <= 1/4.

    In particular log(5/4) takes delta=4/5 here, and is enclosed as
    log(5)-log(4), with lower-minus-upper and upper-minus-lower endpoints.
    """
    delta = _fraction(delta, "log reciprocal argument")
    if not 0 < delta <= 1:
        raise ValueError("log reciprocal argument must lie in (0,1]")
    if delta == 1:
        return F(0), F(0)
    if delta <= F(1, 4):
        return log_interval(delta)
    lo, hi = log_interval(delta/4)
    four_lo, four_hi = log_interval(F(1, 4))
    return lo-four_hi, hi-four_lo


def flattened_weights(prompts, m, n):
    _integer(prompts, "prompts", 1, 3)
    _integer(m, "pool size", 1, 64)
    _integer(n, "budget", 1, m)
    row = tuple(exact_weights(m, n))
    _require(len(row) == m and sum(row, F(0)) == 1, "normalized rank weights")
    _require(all(x >= y >= 0 for x, y in zip(row, row[1:])), "decreasing nonnegative rank weights")
    _require(row[0] == F(n, m), "leading rank atom")
    _require(all(x > 0 for x in row[:m-n+1]) and all(x == 0 for x in row[m-n+1:]), "terminal rank support")
    return tuple(weight/prompts for weight in row for _ in range(prompts))


def abel_identity(weights, increments, epsilon, effective_population):
    if not isinstance(weights, (tuple, list)) or not 1 <= len(weights) <= 192:
        raise ValueError("Abel row must contain between one and 192 cells")
    weights = tuple(_fraction(x, "weight") for x in weights)
    if not isinstance(increments, (tuple, list)) or len(increments) != len(weights):
        raise ValueError("signed increments must match the weight row")
    increments = tuple(_fraction(x, "signed increment") for x in increments)
    epsilon = _fraction(epsilon, "epsilon")
    population = _fraction(effective_population, "effective population")
    if not (sum(weights, F(0)) == 1 and weights[-1] >= 0
            and all(x >= y for x, y in zip(weights, weights[1:]))
            and 0 < epsilon <= 1 and population > 0 and population*weights[0] <= 1):
        raise ValueError("requires a decreasing probability row, positive margin, and valid atom cap")
    coefficients = tuple(weights[k]-(weights[k+1] if k+1 < len(weights) else 0)
                         for k in range(len(weights)))
    suffix = F(0)
    for k in reversed(range(len(weights))):
        suffix += coefficients[k]
        _require(suffix == weights[k], "Abel matrix column, including terminal zeros")
    _require(sum(coefficients, F(0)) == weights[0], "Abel coefficient mass")
    _require(sum(((k+1)*v for k, v in enumerate(coefficients)), F(0)) == 1, "Abel first moment")
    partial = F(0)
    prefix_sum = F(0)
    for coefficient, value in zip(coefficients, increments):
        partial += value
        prefix_sum += coefficient*partial
    weighted_sum = sum((weight*value for weight, value in zip(weights, increments)), F(0))
    _require(weighted_sum == prefix_sum, "signed summation-by-parts identity")
    boundary = sum((coefficient*epsilon*(k+1+population)/2
                    for k, coefficient in enumerate(coefficients)), F(0))
    _require(boundary == epsilon*(1+population*weights[0])/2 <= epsilon, "linear-boundary transfer")
    return {"coefficients": coefficients, "weighted_sum": weighted_sum,
            "prefix_sum": prefix_sum, "boundary_value": boundary}


def abel_checks(maximum, prompt_counts):
    _integer(maximum, "Abel maximum", 1, 24)
    if list(prompt_counts) != [1, 3]:
        raise ValueError("Abel prompt counts must be [1,3]")
    cases = columns = terminal_zeros = noninteger = 0
    for m in range(1, maximum+1):
        for prompts in prompt_counts:
            for n in range(1, m+1):
                weights = flattened_weights(prompts, m, n)
                population = F(prompts*m, n)
                increments = tuple(F((-1)**k*(k+1), len(weights)+1) for k in range(len(weights)))
                abel_identity(weights, increments, F(1, 8), population)
                cases += 1
                columns += len(weights)
                terminal_zeros += sum(weight == 0 for weight in weights)
                noninteger += population.denominator != 1
    return {"maximum_pool_size": maximum, "prompt_counts": list(prompt_counts), "cases": cases,
            "matrix_columns": columns, "signed_identity_cases": cases, "linear_boundary_cases": cases,
            "terminal_zero_cells": terminal_zeros, "noninteger_effective_population_cases": noninteger}


def binary_case(prompts, m, tau, epsilon, p):
    _integer(prompts, "binary prompts", 1, 2)
    _integer(m, "binary pool size", 1, 6)
    d = prompts*m
    _integer(d, "binary items", 1, 10)
    tau, epsilon, p = (_fraction(v, name) for v, name in
                       ((tau, "tau"), (epsilon, "epsilon"), (p, "p")))
    if not (0 < p <= tau <= 1 and 0 < epsilon <= min(1, 2*tau)):
        raise ValueError("parameters must satisfy the standalone Bernoulli lemma")
    rows = tuple(flattened_weights(prompts, m, n) for n in range(1, m+1))
    population = F(prompts)  # N=m; this one event controls every budget.
    boundary_counts, risk_counts = [0]*(d+1), [0]*(d+1)
    tables = 0
    for labels in itertools.product((0, 1), repeat=d):
        partial = F(0)
        boundary_bad = False
        for k, label in enumerate(labels, start=1):
            partial += label-p
            boundary_bad |= partial > epsilon*(k+population)/2
        risk_bad = any(sum((weight*label for weight, label in zip(row, labels)), F(0)) > p+epsilon
                       for row in rows)
        _require(not risk_bad or boundary_bad, "one boundary event controls all declared risks")
        boundary_counts[sum(labels)] += boundary_bad
        risk_counts[sum(labels)] += risk_bad
        tables += 1
    def probability(counts):
        return sum((count*p**s*(1-p)**(d-s) for s, count in enumerate(counts)), F(0))
    boundary_probability, risk_probability = probability(boundary_counts), probability(risk_counts)
    _require(risk_probability <= boundary_probability <= 1, "exact prior event probabilities")
    return {"prompts": prompts, "pool_size": m, "items": d, "budgets": list(range(1, m+1)),
            "tables_enumerated": tables, "boundary_failure_counts_by_ones": boundary_counts,
            "risk_failure_counts_by_ones": risk_counts,
            "boundary_failure_probability": fraction_text(boundary_probability),
            "risk_failure_probability": fraction_text(risk_probability),
            "bound_exponent": fraction_text(population*epsilon**2/(4*tau)),
            "exponential_bound_numerically_checked": False,
            "interpretation": "Exact event implication and prior probability counts only; not a numerical verification of the exponential maximal inequality."}


def binary_checks(protocol):
    params = protocol["binary_lemma_parameters"]
    tau, epsilon, p = (F(params[key]) for key in ("tau", "epsilon", "p"))
    cases = [binary_case(prompts, m, tau, epsilon, p)
             for m in range(1, protocol["binary_max_pool_size"]+1)
             for prompts in protocol["binary_prompt_counts"]
             if prompts*m <= protocol["binary_max_items"]]
    return {"parameters": params, "geometries": len(cases),
            "tables_enumerated": sum(row["tables_enumerated"] for row in cases), "cases": cases}


def product_parameters(tau, epsilon):
    tau, epsilon = _fraction(tau, "tau"), _fraction(epsilon, "epsilon")
    if not 0 < tau <= F(1, 8) or not 0 < epsilon <= tau/16:
        raise ValueError("parameters must satisfy the minimax theorem range")
    p, q, kappa = tau-2*epsilon, tau+10*epsilon, 256*epsilon**2/tau
    majorant = (q-p)**2/(q*(1-q))
    _require(7*tau/8 <= p < q <= 13*tau/8 < F(1, 4), "product-prior parameter bounds")
    _require(p+12*epsilon/4 == tau+epsilon, "strict band mass gives positive unsafe margin")
    _require(majorant < kappa <= tau <= F(1, 8), "rational Bernoulli KL majorant")
    return p, q, kappa, majorant


def density_certificate(tau, epsilon, delta, geometry):
    p, q, kappa, majorant = product_parameters(tau, epsilon)
    delta = _fraction(delta, "delta")
    if not 0 < delta <= F(1, 4):
        raise ValueError("delta must lie in (0,1/4]")
    if not isinstance(geometry, dict) or set(geometry) != {"prompts", "max_budget"}:
        raise ValueError("symbolic geometry must supply prompts and max_budget")
    prompts = _integer(geometry["prompts"], "symbolic prompts", 1, 32)
    n = _integer(geometry["max_budget"], "maximum budget", 1, 64)
    lo, hi = log_bounds(delta)
    density_lo, density_hi = log_bounds(delta/4)
    two_lo, two_hi = (value/2 for value in log_bounds(F(1, 4)))
    leakage_lo, leakage_hi = log_bounds(F(4, 5))
    required_lo, required_hi = 4*tau*density_lo/epsilon**2, 4*tau*density_hi/epsilon**2
    m = ceil_fraction(n*required_hi/prompts)
    population = F(prompts*m, n)
    _require(m >= n and population >= required_hi, "outward density condition")
    _require(F(prompts*(m-1), n) < required_hi, "construction uses the upper endpoint ceiling")
    cap_lo, cap_hi = ceil_fraction(lo/(2*kappa)), ceil_fraction(hi/(2*kappa))
    _require(1 <= cap_lo <= cap_hi, "positive bracketed cap")
    _require(kappa <= lo/8 and kappa*cap_hi <= 5*lo/8, "rounded cap divergence budget")
    information_lower = 3*(lo-leakage_hi)/4-two_hi
    information_upper = 3*kappa*cap_hi/16
    _require(information_lower >= hi/8, "binary data-processing lower certificate")
    _require(information_upper < lo/8, "small-cost capped transcript contradiction")
    _require(delta/4 <= F(1, 16), "safe-prior exceptional mass bound")
    _require(F(15, 16)*F(7, 8) > F(3, 4), "certificate event probability gap")
    _require(population*epsilon**2/(4*tau) >= density_hi, "safe maximal exponent dominates log(4/delta)")
    _require(population*epsilon**2/(2*q) >= density_hi, "unsafe-tail exponent dominates log(4/delta)")
    return {"tau": fraction_text(tau), "epsilon": fraction_text(epsilon), "delta": fraction_text(delta),
            "prompts": prompts, "max_budget": n, "pool_size": m,
            "effective_population": fraction_text(population),
            "required_population_lower": fraction_text(required_lo), "required_population_upper": fraction_text(required_hi),
            "log_lower": fraction_text(lo), "log_upper": fraction_text(hi),
            "log_four_over_delta_lower": fraction_text(density_lo), "log_four_over_delta_upper": fraction_text(density_hi),
            "log_five_fourths_lower": fraction_text(leakage_lo), "log_five_fourths_upper": fraction_text(leakage_hi),
            "log_two_lower": fraction_text(two_lo), "log_two_upper": fraction_text(two_hi),
            "safe_mean": fraction_text(p), "alternative_band_mean": fraction_text(q),
            "kl_majorant": fraction_text(majorant), "kappa": fraction_text(kappa),
            "cap_lower": cap_lo, "cap_upper": cap_hi,
            "ceiling_status": "resolved" if cap_lo == cap_hi else "explicit_interval",
            "information_lower": fraction_text(information_lower),
            "information_upper_if_small_cost": fraction_text(information_upper),
            "band_cost_lower": fraction_text(F(cap_lo, 8)),
            "density_condition_verified": True,
            "interpretation": "Symbolic density and finite-transcript inequalities; no population table, audit trajectory, or concentration experiment is generated."}


def exact_tail(m, n, k):
    _integer(m, "tail pool size", 1, 64)
    _integer(n, "tail budget", 1, m)
    _integer(k, "tail prefix", 0, m)
    return F(comb(m-k, n), comb(m, n)) if m-k >= n else F(0)


def minimal_prefix(m, n, epsilon):
    epsilon = _fraction(epsilon, "tail margin")
    if not 0 < epsilon < 1:
        raise ValueError("tail margin must lie in (0,1)")
    for k in range(m+1):
        if exact_tail(m, n, k) <= epsilon:
            return k
    raise RuntimeError("a complete prefix must have zero tail")


def tail_checks(maximum, margins):
    _integer(maximum, "tail maximum", 1, 32)
    if list(margins) != [F(1, 8), F(1, 32), F(1, 128)]:
        raise ValueError("tail margins differ from the fixed matrix")
    rows = []
    count = 0
    for m in range(1, maximum+1):
        for n in range(1, m+1):
            weights = exact_weights(m, n)
            for k in range(m+1):
                tail = exact_tail(m, n, k)
                _require(tail == sum(weights[k:], F(0)), "binomial tail equals unobserved rank mass")
                if n < m:
                    _require(exact_tail(m, n+1, k) <= tail, "larger budgets have no larger tail")
                count += 1
            for epsilon in margins:
                k = minimal_prefix(m, n, epsilon)
                after, before = exact_tail(m, n, k), exact_tail(m, n, k-1)
                _require(after <= epsilon < before, "shortest prefix threshold and predecessor")
                rows.append({"pool_size": m, "budget": n, "epsilon": fraction_text(epsilon),
                             "prefix_ranks": k, "tail_after": fraction_text(after), "tail_before": fraction_text(before)})
    return {"maximum_pool_size": maximum, "tail_identities": count,
            "minimal_prefix_cases": len(rows), "prefixes": rows}


def counterexample(k):
    _integer(k, "counterexample exponent", 8, 24)
    if k not in (8, 12, 16, 24):
        raise ValueError("counterexample exponent must belong to the frozen matrix")
    m, n, epsilon = 2**(3*k), 2**(3*k-1), F(1, 2**k)
    tail = F(1)
    for r in range(k):
        factor = F(m-n-r, m-r)
        _require(0 <= factor <= F(1, 2), "half-budget tail product factor")
        tail *= factor
    _require(tail <= epsilon, "short prefix controls the remaining mass")
    lo, hi = log_bounds(F(1, 4))
    h_lo, h_hi = lo/(8*epsilon**2), hi/(8*epsilon**2)
    support = m-n+1
    _require(h_hi < support, "symbolic support exceeds statistical baseline")
    return {"exponent": k, "prompts": 1, "pool_size": m, "budget": n, "epsilon": fraction_text(epsilon),
            "tau": "1/8", "delta": "1/4", "envelope_normalizer": "1", "positive_support": support,
            "prefix_ranks": k, "product_factors": k, "tail_after_prefix": fraction_text(tail),
            "baseline_lower": fraction_text(h_lo), "baseline_upper": fraction_text(h_hi),
            "baseline_to_prefix_ratio_lower": fraction_text(h_lo/k),
            "baseline_to_prefix_ratio_upper": fraction_text(h_hi/k),
            "interpretation": "Exact k-factor tail product; neither large binomial coefficients nor a population table are constructed."}


def practical_case(case):
    if _canonical(case) != _canonical(CANONICAL_PROTOCOL["practical_case"]):
        raise ValueError("practical case differs from the frozen geometry")
    tau, epsilon, delta = (F(case[key]) for key in ("tau", "epsilon", "delta"))
    prompts, m = case["prompts"], case["pool_size"]
    population = F(prompts*m, max(case["budgets"]))
    lo, hi = log_bounds(delta/4)
    required_lo, required_hi = 4*tau*lo/epsilon**2, 4*tau*hi/epsilon**2
    _require(population < required_lo, "practical density condition fails")
    k = minimal_prefix(m, min(case["budgets"]), epsilon)
    _require(k == m and prompts*k == 2048, "practical prefix is the full census")
    return {**case, "effective_population": fraction_text(population),
            "required_population_lower": fraction_text(required_lo), "required_population_upper": fraction_text(required_hi),
            "density_condition_holds": False, "prefix_ranks": k, "prefix_label_cost": prompts*k,
            "interpretation": "The lower theorem is inapplicable and the deterministic prefix upper bound is 2048 labels; no measured audit savings are asserted."}


def calculate(protocol):
    validate_protocol(protocol)
    abel = abel_checks(protocol["abel_max_pool_size"], protocol["abel_prompt_counts"])
    binary = binary_checks(protocol)
    profiles = []
    for tau_text in protocol["certificate_taus"]:
        for ratio_text in protocol["relative_margins"]:
            for delta_text in protocol["certificate_deltas"]:
                tau, epsilon, delta = F(tau_text), F(tau_text)*F(ratio_text), F(delta_text)
                profiles.append({"tau": tau_text, "relative_margin": ratio_text, "delta": delta_text,
                                 "geometries": [density_certificate(tau, epsilon, delta, geometry)
                                                for geometry in protocol["symbolic_geometries"]]})
    tails = tail_checks(protocol["tail_max_pool_size"], [F(text) for text in protocol["tail_margins"]])
    counterexamples = [counterexample(k) for k in protocol["counterexample_exponents"]]
    ratios = [F(row["baseline_to_prefix_ratio_lower"]) for row in counterexamples]
    _require(all(a < b for a, b in zip(ratios, ratios[1:])), "counterexample ratios strictly increase")
    return {"abel_checks": abel, "binary_checks": binary, "symbolic_profiles": profiles,
            "profile_count": len(profiles), "density_certificate_count": sum(len(row["geometries"]) for row in profiles),
            "tail_checks": tails, "counterexamples": counterexamples,
            "practical_case": practical_case(protocol["practical_case"])}


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
    files = [Path(__file__).resolve(), ROOT/"tests/test_finite_density.py", path,
             ROOT/"docs/finite-density-theorem.md", ROOT/"docs/nonzero-minimax-theorem.md", IMPORTED_HELPER_PATH]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    _require(len(sources) == 6, "six distinct source pins")
    calculations = calculate(snapshot)
    result = {"schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
              "protocol": snapshot, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "source_sha256": sources, **calculations,
              "rounding": {"bits": ROUND_BITS, "log_series_terms": LOG_TERMS,
                           "density": "Pool size uses the upper log(4/delta) endpoint; both required-population endpoints are retained.",
                           "cap": "Ceilings from both L endpoints are retained and unresolved brackets are explicit.",
                           "information": "Lower information uses L_lo, log(5/4)_hi, log(2)_hi; upper information uses the upper integer cap.",
                           "log_five_fourths": "Wrapper takes reciprocal argument 4/5 and subtracts log4 bounds from log5 bounds outward.",
                           "counterexample": "Baseline and ratio endpoints use lower and upper L without floating-point arithmetic."},
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
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/finite_density_protocol.json")
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
        print("finite-density checks: "+str(error), file=sys.stderr)
        return 2
    print(f"Passed bounded exact checks; saved {result['density_certificate_count']} density certificates to {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
