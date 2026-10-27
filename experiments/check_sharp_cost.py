"""Exact finite checks and conservative sharp zero-table cost certificates.

Standard library only. No labels, sampled model data, or expanded P*m item
tables are used. Lower bounds concern every admissible adaptive zero-table
auditor; upper bounds concern the linear envelope upper bound on NEGEXP cost.
Finite checks support the implementation and proof, not novelty or empirical
usefulness. Every serialized rounding direction is conservative.
"""

import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
LOG_TERMS = 32
ROUND_BITS = 80
ROUND_SCALE = 1 << ROUND_BITS
ROUND_UNIT = F(1, ROUND_SCALE)
MAX_SERIALIZED_BITS = 2048
MAX_PROTOCOL_BYTES = 1024*1024
MAX_POOL_SIZE = 128
MAX_K = 2048
MAX_SYMBOLIC_ITEMS = 3*MAX_POOL_SIZE*MAX_K**4+MAX_POOL_SIZE
MIN_DELTA, MAX_DELTA, MIN_CERTIFICATE_DELTA = F(1, 1000), F(1, 4), F(1, 20)
THEOREM_SCHEMA = {
    "budget_family": "Full prefix 1,...,N with 1<=N<=m",
    "confidence_range": "0<delta<=1/4",
    "limit": "tau tends to zero and rho=log(1/delta)*N/(P*m*tau) tends to zero",
    "conclusion": "OPT_0 / (log(1/delta)*Z_mN/tau) and C_NEG / (log(1/delta)*Z_mN/tau) tend to one uniformly in the other parameters",
    "objective": "Expected distinct unit-cost queries at the all-zero fixed-label table; validity against every fixed table and almost-sure zero-table certification",
}
PROTOCOL_METADATA = {
    "version": 1,
    "title": "Sharp zero-table cost: exact finite bounds and dense-regime certificates",
    "status": "Fixed after exploratory proof checks and before the saved run; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": THEOREM_SCHEMA,
    "certificate_construction": "tau=1/k^3, eta=1/k, kappa=k, P=ceil(3*N*k^4/m); no P*m table is allocated",
    "log_series_terms": LOG_TERMS,
    "dyadic_rounding_bits": ROUND_BITS,
    "claim_boundary": "Finite checks support the proof and implementation, not novelty, real-model usefulness, a nonzero-table cost guarantee, or practical optimality at the earlier tau=.1 study. Counts are symbolic analytical geometries, not sampled model data.",
}
PROTOCOL_VARIABLE_KEYS = {
    "inverse_max_block_size", "inverse_deltas", "large_inverse_cases",
    "certificate_geometries", "certificate_k", "certificate_deltas",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("exact sharp-cost check failed: " + message)


def _integer(value, name, maximum, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _exact(value, name, bits=MAX_SERIALIZED_BITS):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError(name + " must be an exact integer or Fraction")
    value = F(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > bits:
        raise ValueError(name + " exceeds the rational bit limit")
    return value


def _probability(value):
    value = _exact(value, "delta", bits=64)
    if not 0 < value <= MAX_DELTA:
        raise ValueError("delta must lie in (0,1/4]")
    return value


def _parse_probability(text, certificate=False):
    # Reject exponent notation before Fraction can expand powers of ten.
    if (not isinstance(text, str) or len(text) > 64 or
            re.fullmatch(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", text) is None):
        raise ValueError("delta must use bounded ASCII integer/fraction notation")
    try:
        value = _probability(F(text))
    except (ValueError, ZeroDivisionError):
        raise ValueError("invalid bounded rational delta") from None
    if str(value) != text or value < (MIN_CERTIFICATE_DELTA if certificate else MIN_DELTA):
        raise ValueError("delta must be canonical and within the protocol range")
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


def validate_protocol(protocol):
    """Validate all claims, exact-number syntax, and work caps before work."""
    if not isinstance(protocol, dict) or set(protocol) != set(PROTOCOL_METADATA) | PROTOCOL_VARIABLE_KEYS:
        raise ValueError("protocol must have exactly the canonical schema keys")
    for key, expected in PROTOCOL_METADATA.items():
        if _canonical(protocol[key]) != _canonical(expected):
            raise ValueError("protocol metadata differs from canonical schema: " + key)
    _integer(protocol["inverse_max_block_size"], "inverse maximum block size", 64)
    for name, count, certificate in [("inverse_deltas", 5, False), ("certificate_deltas", 2, True)]:
        values = [_parse_probability(text, certificate) for text in _bounded_list(protocol[name], name, count)]
        if len(set(values)) != len(values):
            raise ValueError(name + " must be distinct")
    seen = set()
    for case in _bounded_list(protocol["large_inverse_cases"], "large inverse cases", 4):
        if not isinstance(case, dict) or set(case) != {"block_size", "bad_subset_size", "delta"}:
            raise ValueError("invalid large inverse case schema")
        _integer(case["block_size"], "block size", 1000000)
        _integer(case["bad_subset_size"], "bad subset size", min(case["block_size"], 1000))
        _parse_probability(case["delta"])
        encoded = _canonical(case)
        if encoded in seen:
            raise ValueError("duplicate large inverse case")
        seen.add(encoded)
    seen = set()
    for case in _bounded_list(protocol["certificate_geometries"], "certificate geometries", 4):
        if not isinstance(case, dict) or set(case) != {"pool_size", "maximum_budget"}:
            raise ValueError("invalid certificate geometry schema")
        _integer(case["pool_size"], "pool size", MAX_POOL_SIZE)
        _integer(case["maximum_budget"], "maximum budget", case["pool_size"])
        encoded = _canonical(case)
        if encoded in seen:
            raise ValueError("duplicate certificate geometry")
        seen.add(encoded)
    ks = _bounded_list(protocol["certificate_k"], "certificate k values", 7)
    for k in ks:
        _integer(k, "certificate k", MAX_K, minimum=8)
    if ks != sorted(set(ks)):
        raise ValueError("certificate k values must be sorted and distinct")
    return protocol


def round_down(value):
    value = _exact(value, "rounding input", bits=65536)
    return F((value.numerator*ROUND_SCALE)//value.denominator, ROUND_SCALE)


def round_up(value):
    value = _exact(value, "rounding input", bits=65536)
    return F(-((-value.numerator*ROUND_SCALE)//value.denominator), ROUND_SCALE)


def fraction_text(value):
    """Serialize only bounded exact fractions; never silently approximate."""
    return str(_exact(value, "serialized fraction"))


def _display(value, *, upward=False):
    """Direct exact decimal rounding, with no intermediate rounded quotient."""
    value = F(value)
    scale = 10**9
    numerator = value.numerator*scale
    integer = -((-numerator)//value.denominator) if upward else numerator//value.denominator
    sign = "-" if integer < 0 else ""
    whole, remainder = divmod(abs(integer), scale)
    return f"{sign}{whole}.{remainder:09d}"


def _atanh_interval(z):
    power, square, lower = z, z*z, F(0)
    for j in range(LOG_TERMS):
        lower += 2*power/(2*j+1)
        power *= square
    upper = lower+2*power/((2*LOG_TERMS+1)*(1-square))
    return lower, upper


@lru_cache(maxsize=32, typed=True)
def log_interval(delta):
    """Enclose log(1/delta) by positive atanh series and outward dyadics."""
    delta = _probability(delta)
    numerator, denominator = delta.denominator, delta.numerator
    exponent = numerator.bit_length()-denominator.bit_length()
    if numerator < denominator << exponent:
        exponent -= 1
    y = F(numerator, denominator << exponent)
    _require(1 <= y < 2, "scaled reciprocal lies in [1,2)")
    low2, high2 = _atanh_interval(F(1, 3))
    lowy, highy = _atanh_interval((y-1)/(y+1))
    lower, upper = exponent*low2+lowy, exponent*high2+highy
    lo, hi = round_down(lower), round_up(upper)
    _require(0 < lo <= lower <= upper <= hi, "outward logarithm enclosure")
    return lo, hi


def _inverse_counts(d, b):
    _integer(d, "block size", 1000000)
    _integer(b, "bad subset size", min(d, 1000))


def exact_inverse(d, b, delta):
    """Invert the convex linear interpolation of C(d-x,b)/C(d,b)."""
    _inverse_counts(d, b)
    delta = _probability(delta)
    denominator = comb(d, b)
    def miss(x):
        return F(comb(d-x, b), denominator) if d-x >= b else F(0)
    low, high = 0, d-b+1
    while high-low > 1:
        middle = (low+high)//2
        if miss(middle) <= delta:
            high = middle
        else:
            low = middle
    left, right = miss(high-1), miss(high)
    _require(left > delta >= right and left > right, "exact inverse crossing")
    inverse = F(high-1)+(left-delta)/(left-right)
    _require(left+(inverse-(high-1))*(right-left) == delta, "inverse interpolation identity")
    return inverse


def finite_lower_bound(d, b, log_lower):
    _integer(d, "symbolic block size", MAX_SYMBOLIC_ITEMS)
    _integer(b, "bad subset size", d)
    log_lower = _exact(log_lower, "logarithm lower bound")
    if log_lower <= 0:
        raise ValueError("logarithm lower bound must be positive")
    return log_lower*(d-b)/(b+log_lower)


@lru_cache(maxsize=512, typed=True)
def exact_weights(m, n):
    _integer(m, "pool size", MAX_POOL_SIZE)
    _integer(n, "budget", m)
    denominator = comb(m, n)
    return tuple(F(comb(m-r, n-1), denominator) if m-r >= n-1 else F(0)
                 for r in range(1, m+1))


def _envelope(m, n):
    _integer(m, "pool size", MAX_POOL_SIZE)
    _integer(n, "maximum budget", m)
    rows = [exact_weights(m, budget) for budget in range(1, n+1)]
    envelope, witnesses = [], []
    for r in range(m):
        witness = max(range(n), key=lambda budget: rows[budget][r])
        envelope.append(rows[witness][r])
        witnesses.append(witness+1)
    _require(envelope[0] == F(n, m) and envelope[-1] == F(1, m), "full-prefix envelope endpoints")
    _require(all(a >= b > 0 for a, b in zip(envelope, envelope[1:])), "positive decreasing envelope")
    return tuple(envelope), tuple(witnesses)


def value_bins(m, n, eta):
    """Maximal consecutive endpoint-value bins and their declared witnesses."""
    eta = _exact(eta, "eta", bits=64)
    if not 0 < eta <= 1:
        raise ValueError("eta must lie in (0,1]")
    envelope, witnesses = _envelope(m, n)
    result, start = [], 0
    while start < m:
        stop = start
        while stop+1 < m and envelope[start] <= (1+eta)*envelope[stop+1]:
            stop += 1
        endpoint = envelope[stop]
        witness = witnesses[stop]
        row = exact_weights(m, witness)
        _require(envelope[start] <= (1+eta)*endpoint, "bin endpoint ratio")
        _require(row[stop] == endpoint and all(row[r] >= endpoint for r in range(start, stop+1)),
                 "last-rank target witnesses the entire bin")
        if stop+1 < m:
            _require(envelope[start] > (1+eta)*envelope[stop+1], "bin is maximal")
        result.append({"first_rank": start+1, "last_rank": stop+1, "witness_budget": witness,
                       "endpoint_envelope": fraction_text(endpoint)})
        start = stop+1
    _require(sum(bin["last_rank"]-bin["first_rank"]+1 for bin in result) == m, "bins partition ranks")
    _require((1+eta)**(len(result)-1) <= n, "geometric bin-count bound without logarithms")
    minimum_mass = sum(((bin["last_rank"]-bin["first_rank"]+1)*F(bin["endpoint_envelope"])
                        for bin in result), F(0))
    _require(minimum_mass >= sum(envelope, F(0))/(1+eta), "bin minimum masses capture the envelope")
    return result


def cost_certificate(m, n, k, delta):
    """Construct a symbolic dense geometry and conservative cost bracket."""
    _integer(m, "pool size", MAX_POOL_SIZE)
    _integer(n, "maximum budget", m)
    _integer(k, "certificate k", MAX_K, minimum=8)
    delta = _probability(delta)
    if delta < MIN_CERTIFICATE_DELTA:
        raise ValueError("certificate delta must lie in [1/20,1/4]")
    lo, hi = log_interval(delta)
    _require(hi <= 3, "certificate logarithm upper bound is at most three")
    tau, eta = F(1, k**3), F(1, k)
    prompts = (3*n*k**4+m-1)//m
    items = prompts*m
    _require(items <= MAX_SYMBOLIC_ITEMS, "symbolic population cap")
    a = F(n, items)/tau
    rho_lo, rho_hi = lo*a, hi*a
    _require(a <= F(1, 3*k) and rho_hi <= F(1, k), "constructed dense-regime bounds")
    _require(k > 1+a, "retention threshold makes unsafe subset size feasible")
    envelope, _ = _envelope(m, n)
    z = sum(envelope, F(0))
    bins = value_bins(m, n, eta)
    retained_mass, dropped_mass, lower = F(0), F(0), F(0)
    retained_count = 0
    for bin in bins:
        count = bin["last_rank"]-bin["first_rank"]+1
        endpoint = F(bin["endpoint_envelope"])
        capacity = count*endpoint
        if capacity < k*tau:
            dropped_mass += capacity
            continue
        retained_count += 1
        retained_mass += capacity
        d, v = prompts*count, endpoint/prompts
        b = tau//v+1
        _require(1 <= b < d and b*v > tau, "every retained b-subset is strictly unsafe")
        _require(F(b, d) <= (1+a)/k and lo/b <= rho_hi, "retained block scales")
        exact_lower = finite_lower_bound(d, b, lo)
        rounded = round_down(exact_lower)
        _require(0 <= exact_lower-rounded < ROUND_UNIT, "per-block lower rounding")
        # Round each block before addition: summing exact denominators would
        # create a large least common multiple without improving the bound.
        lower += rounded
    _require(retained_mass+dropped_mass >= z/(1+eta), "total captured envelope mass")
    _require(dropped_mass <= len(bins)*k*tau, "dropped bin mass bound")
    upper = round_up(hi*z/tau)
    _require(0 < lower <= upper, "nonempty conservative cost bracket")
    ratio = upper/lower
    return {
        "pool_size": m, "maximum_budget": n, "k": k, "prompts": prompts, "items": items,
        "tau": fraction_text(tau), "eta": fraction_text(eta), "kappa": k, "delta": fraction_text(delta),
        "a": fraction_text(a), "rho_lower": fraction_text(rho_lo), "rho_upper": fraction_text(rho_hi),
        "log_interval": {"lower": fraction_text(lo), "upper": fraction_text(hi)},
        "envelope_normalizer": fraction_text(z), "bin_count": len(bins),
        "retained_bin_count": retained_count, "dropped_bin_count": len(bins)-retained_count,
        "rank_witness_checks": m, "maximal_boundary_checks": len(bins)-1,
        "unsafe_subset_checks": retained_count,
        "retained_minimum_mass": fraction_text(retained_mass), "dropped_minimum_mass": fraction_text(dropped_mass),
        "lower_rounding_error_upper": fraction_text(retained_count*ROUND_UNIT),
        "lower_bound": fraction_text(lower), "upper_bound": fraction_text(upper),
        "ratio_upper": fraction_text(ratio),
        "display": {"lower_bound": _display(lower), "upper_bound": _display(upper, upward=True),
                    "ratio_upper": _display(ratio, upward=True)},
        "interpretation": "lower <= OPT_0 <= C_NEG <= upper; bounds are conservative, not exact OPT or exact NEGEXP cost. P*m is symbolic and no item table is allocated.",
    }


def _inverse_checks(maximum, deltas):
    comparisons = endpoint_cases = 0
    for d in range(1, maximum+1):
        for b in range(1, d+1):
            for delta in deltas:
                lo, _ = log_interval(delta)
                inverse = exact_inverse(d, b, delta)
                bound = finite_lower_bound(d, b, lo)
                _require(inverse >= bound, "finite lower bound versus exact hypergeometric inverse")
                comparisons += 1
                endpoint_cases += b == d
    return {"maximum_block_size": maximum, "comparisons": comparisons,
            "full_block_endpoint_cases": endpoint_cases,
            "log_bound_used": "rigorous lower endpoint; finite_lower_bound is increasing in L"}


def _large_inverse_case(case):
    d, b, delta = case["block_size"], case["bad_subset_size"], _parse_probability(case["delta"])
    lo, hi = log_interval(delta)
    inverse = exact_inverse(d, b, delta)
    exact_bound = finite_lower_bound(d, b, lo)
    _require(exact_bound <= inverse, "large exact inverse comparison")
    bound = round_down(exact_bound)
    inverse_lo, inverse_hi = round_down(inverse), round_up(inverse)
    return {**case, "log_interval": {"lower": fraction_text(lo), "upper": fraction_text(hi)},
            "finite_lemma_lower": fraction_text(bound),
            "exact_inverse_enclosure": {"lower": fraction_text(inverse_lo), "upper": fraction_text(inverse_hi)},
            "lemma_over_inverse_lower": fraction_text(bound/inverse_hi),
            "display": {"finite_lemma_lower": _display(bound), "inverse_lower": _display(inverse_lo),
                        "inverse_upper": _display(inverse_hi, upward=True),
                        "lemma_over_inverse_lower": _display(bound/inverse_hi)},
            "interpretation": "The inverse was computed exactly; its serialized enclosure is outward dyadic to avoid enormous fractions."}


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
    files = [Path(__file__).resolve(), ROOT/"tests/test_sharp_cost.py", path,
             ROOT/"docs/sharp-cost-theorem.md", ROOT/"docs/sharp-envelope.md"]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    inverse_checks = _inverse_checks(protocol["inverse_max_block_size"],
                                     [_parse_probability(text) for text in protocol["inverse_deltas"]])
    large = [_large_inverse_case(case) for case in protocol["large_inverse_cases"]]
    certificates = [cost_certificate(case["pool_size"], case["maximum_budget"], k, _parse_probability(text, True))
                    for case in protocol["certificate_geometries"] for k in protocol["certificate_k"]
                    for text in protocol["certificate_deltas"]]
    result = {
        "schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
        "protocol": protocol, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "source_sha256": sources, "inverse_checks": inverse_checks, "large_inverse_checks": large,
        "cost_certificates": certificates,
        "certificate_checks": {"certificates": len(certificates),
                               "rank_witness_checks": sum(row["rank_witness_checks"] for row in certificates),
                               "bin_checks": sum(row["bin_count"] for row in certificates),
                               "unsafe_subset_checks": sum(row["unsafe_subset_checks"] for row in certificates)},
        "rounding": {"bits": ROUND_BITS, "log_series_terms": LOG_TERMS,
                     "lower": "Each block is rounded down before summation.",
                     "upper": "The total L_hi*Z/tau is rounded up.",
                     "decimal_displays": "Lower bounds round down and upper bounds round up, using exact integer division at nine decimal places.",
                     "serialization_bit_cap": MAX_SERIALIZED_BITS},
        "claim_boundary": protocol["claim_boundary"],
    }
    current = {key(file): hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
    if current != sources:
        raise RuntimeError("a pinned checker, test, protocol, or proof source changed during calculation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/sharp_cost_protocol.json")
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
        print("sharp-cost checks: " + str(error), file=sys.stderr)
        return 2
    print(f"Passed {result['inverse_checks']['comparisons']:,} inverse checks; "
          f"saved {len(result['cost_certificates'])} analytical certificates to {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
