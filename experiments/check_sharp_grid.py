"""Exact arbitrary-grid rank checks and symbolic monotone-family boundaries.

Reuses the frozen sharp-cost rational arithmetic. Populations in analytical
certificates are symbolic counts, never expanded into label tables. Finite
checks support the proof and implementation; they establish neither novelty
nor empirical usefulness. All decimal bounds are rounded outward.
"""

import argparse
from collections.abc import Sequence
from fractions import Fraction as F
import hashlib
import json
from math import comb
from pathlib import Path
import re
import sys

from experiments import check_sharp_cost as arithmetic


exact_weights = arithmetic.exact_weights
log_interval = arithmetic.log_interval
finite_lower_bound = arithmetic.finite_lower_bound
round_down, round_up = arithmetic.round_down, arithmetic.round_up
fraction_text = arithmetic.fraction_text
ROOT = Path(__file__).resolve().parents[1]
MAX_PROTOCOL_BYTES = 1024*1024
MAX_POOL_SIZE = 128
MAX_CERTIFICATE_K = 512
MAX_GRID_K = 64
MAX_COUNTEREXAMPLE_K = 64
MIN_CERTIFICATE_DELTA, MAX_DELTA = F(1, 20), F(1, 4)
THEOREM_SCHEMA = {
    "budget_family": "Every nonempty subset K of {1,...,m}; N=max K",
    "confidence_range": "0<delta<=1/4",
    "limit": "tau tends to zero and rho=log(1/delta)*N/(P*m*tau) tends to zero",
    "conclusion": "OPT_0 and C_NEG are asymptotic to log(1/delta)*Z_K/tau uniformly in the other parameters",
    "objective": "Expected distinct unit-cost queries on the all-zero fixed-loss table; validity for every fixed table and almost-sure finite zero-table certification",
}
PROTOCOL_METADATA = {
    "version": 1,
    "title": "Sharp audit cost for arbitrary budget grids and a monotone-family boundary",
    "status": "Fixed after exploratory proof and small-grid checks, before the saved broader calculation; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": THEOREM_SCHEMA,
    "certificate_construction": "tau=1/k^3, epsilon=eta=1/k, kappa=k, P=ceil(3*N*k^4/m); no P*m table is allocated",
    "counterexample_construction": "tau=1/k, beta=1/k^2, H=J=k^3, tail lengths H*2^j for j=0,...,J, plus a uniform baseline; D is a symbolic formula and is never expanded",
    "counterexample_delta": "1/4",
    "log_series_terms": 32,
    "dyadic_rounding_bits": 80,
    "claim_boundary": "Analytical finite checks support proofs and implementation, not novelty, empirical model usefulness, nonzero-table efficiency, or a general monotone-family sharp theorem. Sparse grids use their exact Z_K, not log(N)/e. No CLI limits or supported grid domain are changed.",
}
PROTOCOL_VARIABLE_KEYS = {
    "tail_max_pool_size", "tail_epsilons", "grid_max_pool_size", "grid_k",
    "certificate_geometries", "certificate_k", "certificate_deltas", "counterexample_k",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact sharp-grid check failed: " + message)


def _integer(value, name, maximum, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _exact(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name + " must be an exact integer or Fraction")
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 64:
        raise ValueError(name + " exceeds the rational bit limit")
    return value


def _parse_fraction(text):
    if (not isinstance(text, str) or len(text) > 64 or
            re.fullmatch(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", text) is None):
        raise ValueError("rational text must use bounded ASCII integer/fraction notation")
    try:
        value = _exact(F(text), "rational parameter")
    except (ValueError, ZeroDivisionError):
        raise ValueError("invalid bounded rational parameter") from None
    if str(value) != text:
        raise ValueError("rational text must be canonical and reduced")
    return value


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def _bounded_list(value, name, maximum):
    if not isinstance(value, list) or not 1 <= len(value) <= maximum:
        raise ValueError(name + " must be a nonempty bounded list")
    return value


def _budgets(m, budgets):
    _integer(m, "pool size", MAX_POOL_SIZE)
    if not isinstance(budgets, Sequence) or isinstance(budgets, (str, bytes)) or not 1 <= len(budgets) <= m:
        raise ValueError("budgets must be a nonempty bounded sequence")
    for n in budgets:
        _integer(n, "budget", m)
    if len(set(budgets)) != len(budgets):
        raise ValueError("budgets must be distinct")
    return tuple(sorted(budgets))


def validate_protocol(protocol):
    if not isinstance(protocol, dict) or set(protocol) != set(PROTOCOL_METADATA) | PROTOCOL_VARIABLE_KEYS:
        raise ValueError("protocol must have exactly the canonical schema keys")
    for key, expected in PROTOCOL_METADATA.items():
        if _canonical(protocol[key]) != _canonical(expected):
            raise ValueError("protocol metadata differs from canonical schema: " + key)
    _integer(protocol["tail_max_pool_size"], "tail maximum pool size", 64)
    _integer(protocol["grid_max_pool_size"], "grid maximum pool size", 10)
    epsilons = [_parse_fraction(text) for text in _bounded_list(protocol["tail_epsilons"], "tail epsilons", 3)]
    if len(set(epsilons)) != len(epsilons) or any(not 0 < epsilon <= 1 for epsilon in epsilons):
        raise ValueError("tail epsilons must be distinct and lie in (0,1]")
    for name, maximum, minimum, count in [("grid_k", MAX_GRID_K, 4, 3),
                                          ("certificate_k", MAX_CERTIFICATE_K, 8, 4),
                                          ("counterexample_k", MAX_COUNTEREXAMPLE_K, 2, 6)]:
        values = _bounded_list(protocol[name], name, count)
        for value in values:
            _integer(value, name, maximum, minimum)
        if values != sorted(set(values)):
            raise ValueError(name + " must be sorted and distinct")
    deltas = [_parse_fraction(text) for text in _bounded_list(protocol["certificate_deltas"], "certificate deltas", 2)]
    if len(set(deltas)) != len(deltas) or any(not MIN_CERTIFICATE_DELTA <= delta <= MAX_DELTA for delta in deltas):
        raise ValueError("certificate deltas must be distinct and lie in [1/20,1/4]")
    seen = set()
    for case in _bounded_list(protocol["certificate_geometries"], "certificate geometries", 8):
        if not isinstance(case, dict) or set(case) != {"pool_size", "budgets"}:
            raise ValueError("invalid certificate geometry schema")
        budgets = _budgets(case["pool_size"], case["budgets"])
        if list(budgets) != case["budgets"]:
            raise ValueError("certificate budgets must be a sorted list")
        encoded = _canonical(case)
        if encoded in seen:
            raise ValueError("duplicate certificate geometry")
        seen.add(encoded)
    return protocol


def tail_checks(maximum, epsilons):
    _integer(maximum, "tail maximum pool size", 64)
    if not isinstance(epsilons, (list, tuple)) or not 1 <= len(epsilons) <= 3:
        raise ValueError("epsilons must be a nonempty bounded list")
    epsilons = [_exact(epsilon, "epsilon") for epsilon in epsilons]
    if len(set(epsilons)) != len(epsilons) or any(not 0 < epsilon <= 1 for epsilon in epsilons):
        raise ValueError("epsilons must be distinct and lie in (0,1]")
    identity_checks = empty_checks = small_tail_checks = 0
    for m in range(1, maximum+1):
        for n in range(1, m+1):
            row = exact_weights(m, n)
            denominator = comb(m, n)
            running = F(0)
            _require(sum(row, F(0)) == 1, "normalized rank law")
            for r in range(m, 0, -1):
                running += row[r-1]
                direct = F(comb(m-r+1, n), denominator) if m-r+1 >= n else F(0)
                _require(running == direct == F(m-r+1, n)*row[r-1], "exact row-tail identity")
                identity_checks += 1
            _require(sum(row[m:], F(0)) == 0, "empty row-tail endpoint")
            empty_checks += 1
            for epsilon in epsilons:
                tail = sum((weight for weight in row if weight < epsilon*n/m), F(0))
                _require(tail < epsilon, "mass below epsilon times the row peak")
                small_tail_checks += 1
    return {"maximum_pool_size": maximum, "tail_identity_checks": identity_checks,
            "empty_tail_checks": empty_checks, "small_weight_tail_checks": small_tail_checks}


def grid_structure(m, budgets, k):
    """Check the declared skeleton, witness charges, and positive-support bins."""
    budgets = _budgets(m, budgets)
    _integer(k, "grid k", MAX_CERTIFICATE_K, minimum=4)
    epsilon, eta, tau = F(1, k), F(1, k), F(1, k**3)
    rows = {n: exact_weights(m, n) for n in budgets}
    envelope, witnesses = [], []
    for r in range(m):
        witness = max(budgets, key=lambda n: rows[n][r])
        envelope.append(rows[witness][r])
        witnesses.append(witness)
    support = m-min(budgets)+1
    _require(envelope[0] == F(max(budgets), m), "declared envelope peak")
    _require(all(weight > 0 for weight in envelope[:support]) and all(weight == 0 for weight in envelope[support:]),
             "positive support excludes exactly the trailing zeros")
    _require(all(a >= b for a, b in zip(envelope, envelope[1:])), "monotone envelope")
    z = sum(envelope, F(0))
    representatives, owner = [], {}
    for n in budgets:
        if not representatives or n >= 4*representatives[-1]:
            representatives.append(n)
        owner[n] = representatives[-1]
    covered, block_rank_checks = set(), 0
    for n in representatives:
        ranks = set(range(m//(4*n)+1, m//n+1))
        _require(ranks and not covered.intersection(ranks), "nonempty disjoint skeleton blocks")
        _require(len(ranks) >= F(m, 2*n), "skeleton block size bound")
        for r in ranks:
            _require(len(ranks)*rows[n][r-1] > F(1, 4), "skeleton block density")
            block_rank_checks += 1
        covered.update(ranks)
    _require(len(representatives) < 4*z, "skeleton packing J<4Z")
    for n in budgets:
        h = owner[n]
        _require(h <= n < 4*h, "fourfold representative ownership")
        _require(all(rows[n][r] <= 4*rows[h][r] for r in range(m)), "representative row domination")
    row_tails = {n: sum((weight for weight in rows[n] if weight < epsilon*n/m), F(0)) for n in representatives}
    _require(all(tail < epsilon for tail in row_tails.values()), "representative low-weight tails")
    good = [any(epsilon*n/m <= weight <= F(4*n, m) for n in representatives) for weight in envelope]
    bad_mass = sum((weight for weight, is_good in zip(envelope, good) if not is_good), F(0))
    charges = {n: F(0) for n in representatives}
    bad_rank_checks = 0
    for r in range(support):
        if good[r]:
            continue
        h = owner[witnesses[r]]
        _require(rows[h][r] <= envelope[r] <= 4*rows[h][r] and envelope[r] < epsilon*h/m,
                 "bad envelope rank charges to its witness representative tail")
        charges[h] += envelope[r]
        bad_rank_checks += 1
    _require(sum(charges.values(), F(0)) == bad_mass, "bad-rank charge accounting")
    _require(all(charges[n] <= 4*row_tails[n] for n in representatives), "charged tail mass bound")
    _require(bad_mass <= 4*epsilon*len(representatives) <= 16*epsilon*z, "aggregate bad envelope mass")
    bins, start = [], 0
    while start < support:
        stop = start
        while stop+1 < support and envelope[start] <= (1+eta)*envelope[stop+1]:
            stop += 1
        endpoint = envelope[stop]
        witness = witnesses[stop]
        _require(rows[witness][stop] == endpoint and all(rows[witness][r] >= endpoint for r in range(start, stop+1)),
                 "declared endpoint witness covers its bin")
        _require(envelope[start] <= (1+eta)*endpoint, "bin endpoint ratio")
        if stop+1 < support:
            _require(envelope[start] > (1+eta)*envelope[stop+1], "maximal bin and separated starts")
        minimum_mass = (stop-start+1)*endpoint
        bins.append({"first_rank": start+1, "last_rank": stop+1, "witness_budget": witness,
                     "endpoint_envelope": fraction_text(endpoint), "minimum_mass": fraction_text(minimum_mass),
                     "meets_good_rank": any(good[start:stop+1]), "retained": minimum_mass >= k*tau})
        start = stop+1
    _require(sum(bin["last_rank"]-bin["first_rank"]+1 for bin in bins) == support, "positive-support partition")
    windows, window_union = [], set()
    for n in representatives:
        indices = {i for i, bin in enumerate(bins)
                   if epsilon*n/m <= envelope[bin["first_rank"]-1] <= 4*(1+eta)*n/m}
        count = len(indices)
        if count:
            _require((1+eta)**(count-1) <= 4*(1+eta)/epsilon, "per-window geometric bin count")
        windows.append({"representative": n, "count": count})
        window_union.update(indices)
    good_bins = {i for i, bin in enumerate(bins) if bin["meets_good_rank"]}
    _require(good_bins <= window_union, "every good-intersecting bin start belongs to a representative window")
    _require(len(good_bins) <= sum(window["count"] for window in windows), "window count covers good bins")
    retained, dropped_good, dropped_bad = F(0), F(0), F(0)
    for bin in bins:
        mass = F(bin["minimum_mass"])
        if bin["retained"]:
            retained += mass
        elif bin["meets_good_rank"]:
            dropped_good += mass
        else:
            dropped_bad += mass
    total = sum((F(bin["minimum_mass"]) for bin in bins), F(0))
    _require(total == retained+dropped_good+dropped_bad, "retained-mass decomposition")
    _require(total >= z/(1+eta), "bin minimum masses capture the envelope")
    _require(dropped_bad <= bad_mass and dropped_good <= len(good_bins)*k*tau, "two discarded-mass bounds")
    counted_lower = z/(1+eta)-16*epsilon*z-sum(window["count"] for window in windows)*k*tau
    _require(retained >= counted_lower, "retained-mass lower bound using counted windows")
    return {
        "pool_size": m, "budgets": list(budgets), "k": k, "epsilon": fraction_text(epsilon),
        "eta": fraction_text(eta), "tau": fraction_text(tau), "kappa": k,
        "representatives": representatives, "positive_support_size": support,
        "envelope_normalizer": fraction_text(z), "bad_envelope_mass": fraction_text(bad_mass),
        "bins": bins, "good_bin_count": len(good_bins), "window_bin_counts": windows,
        "retained_minimum_mass": fraction_text(retained), "dropped_good_bin_mass": fraction_text(dropped_good),
        "dropped_bad_bin_mass": fraction_text(dropped_bad), "retained_mass_counted_lower": fraction_text(counted_lower),
        "checks": {"skeleton_blocks": len(representatives), "skeleton_rank_density_checks": block_rank_checks,
                   "row_domination_checks": m*len(budgets), "representative_tail_checks": len(representatives),
                   "bad_rank_witness_checks": bad_rank_checks, "bin_checks": len(bins),
                   "bin_rank_witness_checks": support, "window_count_checks": len(windows),
                   "retained_mass_checks": 1, "nontrivial_bad_mass_bound_cases": int(16*epsilon < 1),
                   "positive_bad_mass_cases": int(bad_mass > 0)},
    }


def cost_certificate(m, budgets, k, delta):
    budgets = _budgets(m, budgets)
    _integer(k, "certificate k", MAX_CERTIFICATE_K, minimum=8)
    delta = _exact(delta, "delta")
    if not MIN_CERTIFICATE_DELTA <= delta <= MAX_DELTA:
        raise ValueError("certificate delta must lie in [1/20,1/4]")
    structure = grid_structure(m, budgets, k)
    lo, hi = log_interval(delta)
    _require(hi <= 3, "certificate logarithm bound")
    n, tau = max(budgets), F(1, k**3)
    prompts = (3*n*k**4+m-1)//m
    items = prompts*m
    a = F(n, items)/tau
    _require(a <= F(1, 3*k) and hi*a <= F(1, k) and k > 1+a, "dense-regime construction")
    lower, retained_count = F(0), 0
    for bin in structure["bins"]:
        if not bin["retained"]:
            continue
        retained_count += 1
        count = bin["last_rank"]-bin["first_rank"]+1
        d, v = prompts*count, F(bin["endpoint_envelope"])/prompts
        b = tau//v+1
        _require(1 <= b < d and b*v > tau, "strictly unsafe retained b-subsets")
        _require(F(b, d) <= (1+a)/k and lo/b <= hi*a, "retained block scale bounds")
        exact_lower = finite_lower_bound(d, b, lo)
        rounded = round_down(exact_lower)
        _require(0 <= exact_lower-rounded < arithmetic.ROUND_UNIT, "per-block lower rounding")
        lower += rounded
    z = F(structure["envelope_normalizer"])
    upper = round_up(hi*z/tau)
    _require(0 < lower <= upper, "conservative cost bracket")
    ratio = upper/lower
    return {
        "pool_size": m, "budgets": list(budgets), "maximum_budget": n, "k": k,
        "prompts": prompts, "items": items, "positive_support_size": structure["positive_support_size"],
        "tau": fraction_text(tau), "epsilon": fraction_text(F(1, k)), "eta": fraction_text(F(1, k)),
        "kappa": k, "delta": fraction_text(delta), "a": fraction_text(a), "rho_upper": fraction_text(hi*a),
        "log_interval": {"lower": fraction_text(lo), "upper": fraction_text(hi)},
        "envelope_normalizer": fraction_text(z), "representatives": structure["representatives"],
        "bin_count": len(structure["bins"]), "retained_bin_count": retained_count,
        "bad_envelope_mass": structure["bad_envelope_mass"], "retained_minimum_mass": structure["retained_minimum_mass"],
        "dropped_good_bin_mass": structure["dropped_good_bin_mass"], "dropped_bad_bin_mass": structure["dropped_bad_bin_mass"],
        "lower_rounding_error_upper": fraction_text(retained_count*arithmetic.ROUND_UNIT),
        "lower_bound": fraction_text(lower), "upper_bound": fraction_text(upper), "ratio_upper": fraction_text(ratio),
        "display": {"lower_bound": arithmetic._display(lower), "upper_bound": arithmetic._display(upper, upward=True),
                    "ratio_upper": arithmetic._display(ratio, upward=True)},
        "structure_checks": structure["checks"],
        "interpretation": "lower <= OPT_0 <= C_NEG <= upper for the unchanged declared grid; analytical bounds, not exact optima or sampled costs. P*m is not allocated.",
    }


def tiny_counter_rows(head_size, tail_levels, beta, tau):
    """Only for tiny finite fixtures; never expand symbolic counterexamples."""
    _integer(head_size, "tiny head size", 4)
    _integer(tail_levels, "tiny tail levels", 3, minimum=0)
    beta, tau = _exact(beta, "beta"), _exact(tau, "tau")
    if not 0 < beta <= F(1, 2) or not beta < tau < 1:
        raise ValueError("tiny fixture requires 0<beta<=1/2 and beta<tau<1")
    items = head_size*(1+(1 << tail_levels))
    if items > 16:
        raise ValueError("tiny counterexample fixtures are capped at sixteen items")
    rows = []
    for j in range(tail_levels+1):
        tail_size = head_size*(1 << j)
        row = tuple([(1-beta)/head_size]*head_size+[beta/tail_size]*tail_size+[F(0)]*(items-head_size-tail_size))
        _require(sum(row, F(0)) == 1 and all(a >= b >= 0 for a, b in zip(row, row[1:])),
                 "normalized monotone counterexample row")
        rows.append(row)
    uniform = tuple([F(1, items)]*items)
    head = tuple([F(1, head_size)]*head_size+[F(0)]*(items-head_size))
    rows.append(uniform)
    return {"items": items, "family_rows": tuple(rows), "head_target": head, "uniform_target": uniform,
            "head_threshold": (tau-beta)/(1-beta), "risk_threshold": tau}


def counterexample_certificate(k):
    """Check algebraic counterexample bounds without constructing 2**(k**3)."""
    _integer(k, "counterexample k", MAX_COUNTEREXAMPLE_K, minimum=2)
    h = levels = k**3
    tau, beta = F(1, k), F(1, k**2)
    lo, hi = log_interval(F(1, 4))
    _require(0 < beta < tau < 1 and beta <= F(1, 2), "counterexample parameter range")
    head_threshold = (tau-beta)/(1-beta)
    _require(head_threshold == F(1, k+1), "head audit threshold")
    z_lower = (1-beta)+beta*(1+F(levels, 2))
    _require(z_lower == 1+F(k, 2), "dyadic-tail envelope mass lower bound")
    comparator_over_l = 1/head_threshold+1/tau
    _require(comparator_over_l == 2*k+1, "conjoined head and uniform audit cost")
    correction = 1-hi/F(2*k**2)
    _require(correction > 0 and F(1, h)/tau == F(1, k**2), "small-atom NEGEXP lower bound")
    exact_ratio_lower = correction*k*z_lower/comparator_over_l
    ratio_lower = round_down(exact_ratio_lower)
    _require(0 <= exact_ratio_lower-ratio_lower < arithmetic.ROUND_UNIT, "counterexample downward rounding")
    return {
        "k": k, "head_size": h, "tail_levels": levels, "population_symbolic": "H*(1+2^J)",
        "tau": fraction_text(tau), "beta": fraction_text(beta), "delta": "1/4",
        "head_threshold": fraction_text(head_threshold), "envelope_normalizer_lower": fraction_text(z_lower),
        "maximum_item_mass_upper": fraction_text(F(1, h)), "rho_upper": fraction_text(hi/k**2),
        "log_interval": {"lower": fraction_text(lo), "upper": fraction_text(hi)},
        "comparator_cost_upper_divided_by_L": fraction_text(comparator_over_l),
        "ratio_lower": fraction_text(ratio_lower), "display": {"ratio_lower": arithmetic._display(ratio_lower)},
        "interpretation": "C_NEG/OPT_0 is at least this bound for a constructed monotone family with a uniform baseline. A conjunction of head and uniform audits is valid for fractional losses; both tests may use delta. The exponential population is not expanded.",
    }


def _grid_checks(maximum, ks):
    totals = {"grids": 0, "grid_scale_cases": 0}
    for m in range(1, maximum+1):
        for mask in range(1, 1 << m):
            budgets = [n for n in range(1, m+1) if mask & (1 << (n-1))]
            totals["grids"] += 1
            for k in ks:
                result = grid_structure(m, budgets, k)
                totals["grid_scale_cases"] += 1
                for key, value in result["checks"].items():
                    totals[key] = totals.get(key, 0)+value
    totals["scope"] = "Every nonempty declared grid in the finite range; zero envelope support is excluded from bins, and no targets are added."
    return totals


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate protocol key: " + key)
        result[key] = value
    return result


def _parse_protocol(data):
    if len(data) > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 1 MiB limit")
    def invalid(value):
        raise ValueError("nonfinite protocol value: " + value)
    return json.loads(data, object_pairs_hook=_unique_object, parse_constant=invalid)


def build_results(protocol, protocol_path):
    path = Path(protocol_path).resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 1 MiB limit")
    protocol_bytes = path.read_bytes()
    snapshot = _parse_protocol(protocol_bytes)
    if protocol is not None and _canonical(protocol) != _canonical(snapshot):
        raise ValueError("supplied protocol differs from its file snapshot")
    protocol = validate_protocol(snapshot)
    files = [Path(__file__).resolve(), ROOT/"tests/test_sharp_grid.py", path,
             ROOT/"docs/sharp-grid-structure.md", ROOT/"docs/sharp-cost-theorem.md",
             ROOT/"docs/sparse-grid-theorem.md", Path(arithmetic.__file__).resolve()]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    tails = tail_checks(protocol["tail_max_pool_size"], [_parse_fraction(text) for text in protocol["tail_epsilons"]])
    grids = _grid_checks(protocol["grid_max_pool_size"], protocol["grid_k"])
    certificates = [cost_certificate(case["pool_size"], case["budgets"], k, _parse_fraction(text))
                    for case in protocol["certificate_geometries"] for k in protocol["certificate_k"]
                    for text in protocol["certificate_deltas"]]
    counters = [counterexample_certificate(k) for k in protocol["counterexample_k"]]
    result = {
        "schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
        "protocol": protocol, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "source_sha256": sources, "tail_checks": tails, "grid_checks": grids,
        "cost_certificates": certificates, "monotone_counterexamples": counters,
        "certificate_checks": {"certificates": len(certificates),
                               "retained_unsafe_subset_checks": sum(row["retained_bin_count"] for row in certificates),
                               "bin_checks": sum(row["bin_count"] for row in certificates)},
        "rounding": {"bits": arithmetic.ROUND_BITS, "log_series_terms": arithmetic.LOG_TERMS,
                     "lower": "Each bin lower bound rounds down before summation; counterexample ratios round down.",
                     "upper": "Linear total cost rounds up; upper decimal bounds round up and lower decimal bounds round down."},
        "claim_boundary": protocol["claim_boundary"],
    }
    current = {key(file): hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
    if current != sources:
        raise RuntimeError("a pinned checker, helper, test, protocol, or proof source changed during calculation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/sharp_grid_protocol.json")
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
        print("sharp-grid checks: " + str(error), file=sys.stderr)
        return 2
    print(f"Passed {result['grid_checks']['grid_scale_cases']:,} grid-scale checks; "
          f"saved {len(result['cost_certificates'])} cost certificates to {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
