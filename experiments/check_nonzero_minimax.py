"""Bounded exact finite checks for nonzero-table minimax certification.

Standard library only; no audit, labels, model calls, or expanded populations.
Finite arithmetic checks support the implementation, not the concentration
theorem, novelty, or useful finite savings. All reported bounds are outward.
"""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

from experiments import check_sharp_cost as sharp


ROOT = Path(__file__).resolve().parents[1]
IMPORTED_HELPER_PATH = Path(sharp.__file__).resolve()
exact_weights = sharp.exact_weights
log_interval = sharp.log_interval
round_down, round_up = sharp.round_down, sharp.round_up
fraction_text = sharp.fraction_text
LOG_TERMS, ROUND_BITS = sharp.LOG_TERMS, sharp.ROUND_BITS
MAX_PROTOCOL_BYTES = 16384
CANONICAL_PROTOCOL = {
    "version": 1,
    "title": "Nonzero finite-table minimax certification for arbitrary best-of-N grids",
    "status": "Fixed after exploratory proof and small-grid checks, before the saved broader calculation; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": {
        "objective": "One globally delta-valid, all-safe-complete auditor; worst-case expected distinct labels over fixed tables with max R_n <= tau-epsilon",
        "range": "0<tau<=1/8; 0<epsilon<=tau/16; 0<delta<=1/4",
        "lower_replication": "P>=log(1/delta)/epsilon^2; not required for the upper bound",
        "lower_constant": 12000, "upper_constant": 49152, "stage_constant": 4096,
        "scope": "Arbitrary nonempty declared grids use their exact Z; global certification does not provide selectable simultaneous confidence bands",
    },
    "ratio_max_pool_size": 48,
    "grid_max_pool_size": 10,
    "conditional_prompt_counts": [16, 32, 64, 128],
    "conditional_count_range": "1<=k<=P/8; k<q_count<=3P/16; 0<=t<=floor(k/2); 0<=s<=t",
    "certificate_taus": ["1/8", "1/16"],
    "relative_margins": ["1/16", "1/64"],
    "certificate_deltas": ["1/4", "1/20"],
    "replication_multipliers": [1, 4],
    "stages": 16,
    "profile_construction": "P=ceil(multiplier*log_upper(1/delta)/epsilon^2); pP=floor(P*(tau-epsilon)); (q-p)P=ceil(8*P*epsilon); b=floor(pP/2)",
    "practical_case": {"prompts": 32, "pool_size": 64, "budgets": [1, 2, 4, 8, 16, 32, 64], "tau": "1/10", "epsilon": "1/160", "delta": "1/20"},
    "log_series_terms": 32, "dyadic_rounding_bits": 80,
    "claim_boundary": "Finite arithmetic supports implementation, not the probabilistic concentration theorem, novelty, practical savings, real-model usefulness, or independent human ownership. The existing CLI and frozen paper snapshots remain unchanged.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact nonzero-minimax check failed: "+message)


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name+" must be an exact integer or Fraction")
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 256:
        raise ValueError(name+" exceeds the exact-number bit limit")
    return F(value)


def _parameters(tau, epsilon, delta):
    tau, epsilon, delta = (_fraction(x, name) for x, name in
                           [(tau, "tau"), (epsilon, "epsilon"), (delta, "delta")])
    if not (0 < tau <= F(1, 8) and 0 < epsilon <= tau/16 and 0 < delta <= F(1, 4)):
        raise ValueError("parameters must satisfy the stated theorem range")
    return tau, epsilon, delta


def _ceil(value):
    return -((-value.numerator)//value.denominator)


def _log_two():
    lo, hi = log_interval(F(1, 4))
    return lo/2, hi/2


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def validate_protocol(protocol):
    """Only this complete frozen matrix is accepted; there are no work knobs."""
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


def likelihood_ratios(m, a, n):
    """Ratios on the representative's positive support, including target zeros."""
    _integer(m, "pool size", 1, 64)
    _integer(a, "representative", 1, m)
    _integer(n, "group budget", a, min(m, 4*a-1))
    base, row = exact_weights(m, a), exact_weights(m, n)
    _require(len(base) == len(row) == m, "weight row lengths")
    _require(sum(base, F(0)) == sum(row, F(0)) == 1, "exact weight normalizations")
    support = m-a+1
    _require(all(v > 0 for v in base[:support]) and all(v == 0 for v in base[support:]),
             "representative terminal support")
    _require(all(v == 0 for v in row[m-n+1:]) and all(v > 0 for v in row[:m-n+1]),
             "target terminal support")
    h = tuple(row[r]/base[r] for r in range(support))
    _require(h[0] == F(n, a), "leading likelihood ratio")
    _require(all(0 <= v <= F(n, a) <= 4 for v in h), "bounded likelihood ratios")
    _require(all(x >= y for x, y in zip(h, h[1:])), "decreasing likelihood ratios")
    return h


def layer_cake(h):
    """Exact nonnegative prefix coefficients, including the terminal term."""
    if not 1 <= len(h) <= 64:
        raise ValueError("layer cake requires between one and 64 ranks")
    h = tuple(_fraction(x, "likelihood ratio") for x in h)
    if not all(0 <= x <= 4 for x in h) or not all(x >= y for x, y in zip(h, h[1:])):
        raise ValueError("layer cake requires nonincreasing ratios in [0,4]")
    coefficients = tuple(h[i]-(h[i+1] if i+1 < len(h) else 0) for i in range(len(h)))
    _require(sum(coefficients, F(0)) == h[0] <= 4, "layer-cake coefficient mass")
    # Each column is a unit signed increment and its cumulative step vector.
    # Equality on this basis verifies the full summation-by-parts linear map.
    suffix = F(0)
    for i in reversed(range(len(h))):
        suffix += coefficients[i]
        _require(suffix == h[i], "summation-by-parts matrix column")
    return coefficients


def ratio_checks(maximum):
    _integer(maximum, "ratio maximum", 1, 48)
    cases = columns = terminal_zeros = 0
    for m in range(1, maximum+1):
        for a in range(1, m+1):
            for n in range(a, min(m+1, 4*a)):
                h = likelihood_ratios(m, a, n)
                layer_cake(h)
                cases += 1
                columns += len(h)
                terminal_zeros += sum(x == 0 for x in h)
    return {"maximum_pool_size": maximum, "ratio_cases": cases,
            "summation_by_parts_columns": columns, "target_terminal_zeros": terminal_zeros}


def grid_geometry(m, budgets):
    _integer(m, "pool size", 1, 64)
    if not isinstance(budgets, (list, tuple)) or not budgets:
        raise ValueError("declared grid must be nonempty")
    for n in budgets:
        _integer(n, "budget", 1, m)
    if list(budgets) != sorted(set(budgets)):
        raise ValueError("declared grid must be sorted and distinct")
    rows = {n: exact_weights(m, n) for n in budgets}
    envelope = tuple(max(rows[n][r] for n in budgets) for r in range(m))
    z = sum(envelope, F(0))
    representatives, groups = [], []
    for n in budgets:
        if not representatives or n >= 4*representatives[-1]:
            representatives.append(n)
            groups.append([])
        groups[-1].append(n)
    bands, used = [], set()
    for a, group in zip(representatives, groups):
        first, last = m//(4*a)+1, m//a
        ranks = set(range(first, last+1))
        _require(bool(ranks) and not used.intersection(ranks), "nonempty disjoint witness bands")
        used.update(ranks)
        mass = sum((rows[a][r-1] for r in ranks), F(0))
        _require(mass > F(1, 4), "strict band mass")
        for n in group:
            _require(all(rows[n][r] <= 4*rows[a][r] for r in range(m)), "group envelope dominance")
        bands.append({"representative": a, "budgets": group, "first_rank": first,
                      "last_rank": last, "mass": fraction_text(mass)})
    j = len(representatives)
    _require(z/4 <= j <= 4*z, "two-sided representative count")
    _require(all(envelope[r] <= 4*sum((rows[a][r] for a in representatives), F(0))
                 for r in range(m)), "envelope dominated by representative mixture")
    return {"pool_size": m, "budgets": list(budgets), "envelope_normalizer": fraction_text(z),
            "representatives": representatives, "group_count": j, "bands": bands}


def grid_checks(maximum):
    _integer(maximum, "grid maximum", 1, 10)
    count = bands = without_one = 0
    for m in range(1, maximum+1):
        for mask in range(1, 1 << m):
            budgets = [n for n in range(1, m+1) if mask & (1 << (n-1))]
            geometry = grid_geometry(m, budgets)
            count += 1
            bands += geometry["group_count"]
            without_one += budgets[0] != 1
    return {"maximum_pool_size": maximum, "nonempty_grids": count,
            "strict_disjoint_bands": bands, "grids_without_budget_one": without_one}


def conditional_probabilities(prompts, k, q_count, t, s):
    """Two exact next-query laws for a positive-probability safe prefix."""
    _integer(prompts, "prompts", 2, 128)
    _integer(k, "safe count", 1, prompts-1)
    _integer(q_count, "alternative count", k+1, prompts-1)
    _integer(t, "previous queries at rank", 0, prompts-1)
    _integer(s, "previous successes", 0, t)
    if s > k or t-s > prompts-q_count:
        raise ValueError("prefix must be possible under both fixed-count laws")
    return F(k-s, prompts-t), F(q_count-s, prompts-t)


def conditional_kl_majorant(prompts, k, q_count, t, s):
    u, v = conditional_probabilities(prompts, k, q_count, t, s)
    if not 0 < v < 1:
        raise ValueError("alternative success probability must be interior")
    return (u-v)**2/(v*(1-v))


def conditional_checks(prompt_counts):
    if not isinstance(prompt_counts, (list, tuple)) or not prompt_counts or len(prompt_counts) > 4:
        raise ValueError("at most four conditional populations are supported")
    comparisons = boundaries = 0
    for prompts in prompt_counts:
        if type(prompts) is not int or prompts not in (16, 32, 64, 128):
            raise ValueError("conditional population must be 16, 32, 64, or 128")
        for k in range(1, prompts//8+1):
            p = F(k, prompts)
            for q_count in range(k+1, 3*prompts//16+1):
                q, increment = F(q_count, prompts), F(q_count-k, prompts)
                for t in range(k//2+1):
                    for s in range(t+1):
                        u, v = conditional_probabilities(prompts, k, q_count, t, s)
                        _require(0 < u < v < 1 and v >= p/2 and v <= 2*q <= F(3, 8),
                                 "hypergeometric support and probability bounds")
                        _require(v-u <= 2*increment, "conditional probability difference")
                        majorant = conditional_kl_majorant(prompts, k, q_count, t, s)
                        _require(majorant <= 16*increment**2/p, "rational binary-KL majorant")
                        comparisons += 1
                        boundaries += t == k//2
    return {"prompt_counts": list(prompt_counts), "comparisons": comparisons,
            "cap_boundary_comparisons": boundaries,
            "interpretation": "Checks the rational upper bound (u-v)^2/[v(1-v)], not numerical logarithmic KL or an iid approximation."}


def profile_counts(prompts, tau, epsilon):
    _integer(prompts, "symbolic prompts", 1, 10**12)
    tau, epsilon, _ = _parameters(tau, epsilon, F(1, 4))
    k = (prompts*(tau-epsilon)).numerator//(prompts*(tau-epsilon)).denominator
    increment = _ceil(8*prompts*epsilon)
    _require(0 <= k < k+increment <= prompts, "feasible fixed profile counts")
    return {"prompts": prompts, "safe_count": k, "increment_count": increment,
            "unsafe_count": k+increment, "cap": k//2}


def lower_certificate(tau, epsilon, delta, multiplier):
    tau, epsilon, delta = _parameters(tau, epsilon, delta)
    _integer(multiplier, "replication multiplier", 1, 4)
    lo, hi = log_interval(delta)
    _, log_two_hi = _log_two()
    counts = profile_counts(_ceil(multiplier*hi/epsilon**2), tau, epsilon)
    prompts, k, b = counts["prompts"], counts["safe_count"], counts["cap"]
    p, increment, q = (F(counts[key], prompts) for key in ("safe_count", "increment_count", "unsafe_count"))
    _require(prompts*epsilon**2 >= hi and prompts*epsilon >= 1 and k >= 4, "replication and count prerequisites")
    _require(tau-2*epsilon <= p <= tau-epsilon and p >= 7*tau/8, "safe fixed profile")
    _require(8*epsilon <= increment <= 9*epsilon and q <= F(3, 2)*tau <= F(3, 16), "rounded alternative bounds")
    _require(p+increment/4 >= tau, "band mass strictly above one quarter makes alternative strictly unsafe")
    _require(b >= F(k, 4), "floor cap lower bound")
    denominator = 1296*epsilon**2/p+hi/b
    finite = round_down((lo-log_two_hi)/denominator)
    target = round_up(tau*hi/(3000*epsilon**2))
    _require(finite >= target, "conservative finite band lower bound implies theorem constant")
    return {**counts, "tau": fraction_text(tau), "epsilon": fraction_text(epsilon),
            "delta": fraction_text(delta), "replication_multiplier": multiplier,
            "safe_risk": fraction_text(p), "increment": fraction_text(increment), "alternative_rank_risk": fraction_text(q),
            "log_interval": {"lower": fraction_text(lo), "upper": fraction_text(hi)},
            "log_two_upper": fraction_text(log_two_hi), "finite_band_lower": fraction_text(finite),
            "theorem_band_target_upper": fraction_text(target), "lower_constant_verified": True,
            "interpretation": "Symbolic fixed-count permutation populations; no P-by-m table is allocated. Strict unsafety uses each band's mass > 1/4."}


def stage_certificate(tau, epsilon, delta, stages=16):
    tau, epsilon, delta = _parameters(tau, epsilon, delta)
    _integer(stages, "stages", 1, 16)
    lo, hi = log_interval(delta)
    two_lo, two_hi = _log_two()
    a = 4096*tau/epsilon**2
    result = []
    for j in range(1, stages+1):
        xlo, xhi = lo+(j+2)*two_lo, hi+(j+2)*two_hi
        tlo, thi = _ceil(a*xlo), _ceil(a*xhi)
        v = xhi/tlo
        slack = epsilon/8-2*v
        left, right = 16*tau*v, slack**2
        _require(slack > 0 and left < right, "strict radius below epsilon/8 by exact squaring")
        _require(tlo*tau >= 4*xhi, "unsafe high-risk Chernoff branch")
        result.append({"stage": j, "alpha": fraction_text(delta/F(2**j)),
                       "x_lower": fraction_text(xlo), "x_upper": fraction_text(xhi),
                       "draws_lower": tlo, "draws_upper": thi,
                       "ceiling_status": "resolved" if tlo == thi else "explicit_interval",
                       "radius_linear_slack": fraction_text(slack),
                       "radius_squared_left": fraction_text(left), "radius_squared_right": fraction_text(right)})
    expected = result[0]["draws_upper"]+delta*_ceil(a*two_hi)
    theorem_lower = 3*a*lo
    _require(expected <= theorem_lower, "infinite-stage expected proposal bound <= 3 A L")
    return {"A": fraction_text(a), "stages": result, "expected_draws_upper": fraction_text(expected),
            "three_A_L_lower": fraction_text(theorem_lower),
            "increment_draws_upper": _ceil(a*two_hi),
            "error_spending_sum": fraction_text(delta),
            "interpretation": "The infinite sum uses sum_j delta*2^(-j)=delta and increments <= ceil(A log 2). Listed stages are finite arithmetic examples, not a proof of concentration."}


def practical_case(case):
    if _canonical(case) != _canonical(CANONICAL_PROTOCOL["practical_case"]):
        raise ValueError("practical case differs from the frozen geometry")
    tau, epsilon, delta = (F(case[key]) for key in ("tau", "epsilon", "delta"))
    lo, hi = log_interval(delta)
    geometry = grid_geometry(case["pool_size"], case["budgets"])
    stage = stage_certificate(tau, epsilon, delta, 1)
    z, d = F(geometry["envelope_normalizer"]), case["prompts"]*case["pool_size"]
    _require(case["prompts"]*epsilon**2 < lo, "practical lower replication condition fails")
    first = stage["stages"][0]
    _require(first["draws_lower"] > d, "census cap before first stage")
    return {**case, "envelope_normalizer": fraction_text(z), "representatives": geometry["representatives"],
            "lower_replication_condition_holds": False,
            "required_prompts_lower": fraction_text(lo/epsilon**2),
            "required_prompts_upper": fraction_text(hi/epsilon**2),
            "census_cap": d, "first_stage_draws_lower": first["draws_lower"],
            "first_stage_draws_upper": first["draws_upper"], "census_before_first_stage": True,
            "uncapped_theorem_cost_upper": fraction_text(round_up(49152*z*tau*hi/epsilon**2)),
            "cost_upper_with_census": fraction_text(min(F(d), round_up(49152*z*tau*hi/epsilon**2))),
            "interpretation": "This proof-device geometry falls back to census; no model measurements or useful finite savings are reported."}


def calculate(protocol):
    validate_protocol(protocol)
    ratios = ratio_checks(protocol["ratio_max_pool_size"])
    grids = grid_checks(protocol["grid_max_pool_size"])
    conditional = conditional_checks(protocol["conditional_prompt_counts"])
    certificates = []
    schedule_count = stage_count = 0
    for tau_text in protocol["certificate_taus"]:
        for margin_text in protocol["relative_margins"]:
            for delta_text in protocol["certificate_deltas"]:
                tau, delta = F(tau_text), F(delta_text)
                epsilon = tau*F(margin_text)
                schedule = stage_certificate(tau, epsilon, delta, protocol["stages"])
                schedule_count += 1
                stage_count += len(schedule["stages"])
                for multiplier in protocol["replication_multipliers"]:
                    certificates.append({**lower_certificate(tau, epsilon, delta, multiplier),
                                         "relative_margin": margin_text, "stage_certificate": schedule})
    return {"ratio_checks": ratios, "grid_checks": grids, "conditional_checks": conditional,
            "analytical_certificates": certificates, "certificate_count": len(certificates),
            "certificate_checks": {"symbolic_profile_certificates": len(certificates),
                                   "distinct_stage_schedules": schedule_count, "stage_checks": stage_count,
                                   "stored_stage_entries": sum(len(row["stage_certificate"]["stages"]) for row in certificates)},
            "practical_case": practical_case(protocol["practical_case"])}


def build_results(protocol, protocol_path):
    path = Path(protocol_path).resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 16 KiB limit")
    # One bounded snapshot drives parsing, validation, computation and its pin.
    # The later read is solely the drift check, never a second source of inputs.
    with path.open("rb") as stream:
        protocol_bytes = stream.read(MAX_PROTOCOL_BYTES+1)
    snapshot = parse_protocol(protocol_bytes)
    if protocol is not None and _canonical(protocol) != _canonical(snapshot):
        raise ValueError("supplied protocol differs from its file snapshot")
    snapshot = validate_protocol(snapshot)
    files = [Path(__file__).resolve(), ROOT/"tests/test_nonzero_minimax.py", path,
             ROOT/"docs/nonzero-minimax-theorem.md", IMPORTED_HELPER_PATH]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    _require(len(sources) == 5, "five distinct source pins")
    calculations = calculate(snapshot)
    result = {"schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
              "protocol": snapshot, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "source_sha256": sources, **calculations,
              "rounding": {"bits": ROUND_BITS, "log_series_terms": LOG_TERMS,
                           "lower": "Finite (G) numerator uses L_lo-log(2)_hi; denominator uses L_hi; final fraction rounds down.",
                           "comparison": "The band target uses L_hi and rounds up. Stage ceilings are resolved by both endpoints or explicitly bracketed.",
                           "upper": "Expected-stage upper bounds use upper logarithm endpoints and compare against 3 A L_lo."},
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
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/nonzero_minimax_protocol.json")
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
        print("nonzero-minimax checks: "+str(error), file=sys.stderr)
        return 2
    print(f"Passed bounded exact checks; saved {result['certificate_count']} analytical certificates to {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
