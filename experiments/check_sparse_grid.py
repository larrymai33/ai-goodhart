"""Bounded exact checks for arbitrary budget grids containing budget 1.

Uses only the Python standard library. Finite checks support the implementation
and algebra; they do not prove the unbounded theorem or establish novelty.
The cost expression checked is a deterministic upper bound on NEGEXP expected
zero-table cost, not a sampled cost or the exact adaptive optimum. Counterexample
confidence levels are symbolic: no enormous powers of four are constructed.
"""

import argparse
from collections.abc import Sequence
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_PROTOCOL_BYTES = 1024*1024
MAX_EXHAUSTIVE_POOL = 12
MAX_GEOMETRY_POOL = 128
MAX_PROMPTS = 32
MAX_COUNTEREXAMPLE_J = 320
MAX_BINARY_ENUMERATION_J = 4
THEOREM_SCHEMA = {
    "factor": 320,
    "envelope_cost_factor": 8,
    "lower_cost_denominator": 40,
    "maximum_risk_threshold": "1/8",
    "maximum_error_probability": "1/4",
    "budget_family_requirement": "Any subset of 1,...,m containing 1",
    "objective": "Expected distinct unit-cost queries at the all-zero fixed-label table",
    "decision": "One certificate for the entire originally declared family, or abstention",
}
PROTOCOL_METADATA = {
    "version": 1,
    "title": "Arbitrary budget grids with baseline 1: exact finite checks",
    "status": "Fixed before the saved run, after exploratory proof checks; not external preregistration",
    "evidence_type": "deterministic_exact_arithmetic_checks",
    "theorem": THEOREM_SCHEMA,
    "counterexample_confidence": "delta_j = 4^(-binom(10*j,j)); represented symbolically to avoid exponential allocation",
    "claim_boundary": "Finite checks support implementation and algebra, not an unbounded proof, novelty, real-model usefulness, or exact optimality of NEGEXP. The missing-baseline separation varies confidence at fixed threshold.",
}
PROTOCOL_VARIABLE_KEYS = {
    "exhaustive_max_pool_size", "prompt_counts", "cost_scales", "additional_geometries",
    "counterexample_j", "counterexample_binary_enumeration_max_j",
}


def _require(condition, message):
    # Explicit checks remain active under python -O and -OO.
    if not condition:
        raise RuntimeError("exact sparse-grid check failed: " + message)


def _integer(value, name, maximum, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _budgets(m, budgets):
    if not isinstance(budgets, Sequence) or isinstance(budgets, (str, bytes)) or not 1 <= len(budgets) <= m:
        raise ValueError("budgets must be a nonempty bounded sequence")
    for n in budgets:
        _integer(n, "budget", m)
    if len(set(budgets)) != len(budgets) or 1 not in budgets:
        raise ValueError("budgets must be distinct and contain 1")
    return tuple(sorted(budgets))


def _scale(value):
    if isinstance(value, bool) or not isinstance(value, (int, F)) or not F(1, 16) <= value <= 1024:
        raise ValueError("cost scale must be an exact rational in [1/16,1024]")
    value = F(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > 64:
        raise ValueError("cost scale exceeds the rational bit limit")
    return value


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def validate_protocol(protocol):
    """Validate all metadata and work bounds before beginning any checks."""
    if not isinstance(protocol, dict) or set(protocol) != set(PROTOCOL_METADATA) | PROTOCOL_VARIABLE_KEYS:
        raise ValueError("protocol must have exactly the canonical schema keys")
    for key, expected in PROTOCOL_METADATA.items():
        if _canonical(protocol[key]) != _canonical(expected):
            raise ValueError("protocol metadata differs from canonical schema: " + key)
    _integer(protocol["exhaustive_max_pool_size"], "exhaustive maximum", MAX_EXHAUSTIVE_POOL)
    for name, maximum, count in [("prompt_counts", MAX_PROMPTS, 3),
                                 ("counterexample_j", MAX_COUNTEREXAMPLE_J, 8)]:
        values = protocol[name]
        if not isinstance(values, list) or not 1 <= len(values) <= count:
            raise ValueError(name + " must be a nonempty bounded list")
        for value in values:
            _integer(value, name, maximum)
        if values != sorted(set(values)):
            raise ValueError(name + " must be sorted and distinct")
    _integer(protocol["counterexample_binary_enumeration_max_j"], "binary enumeration maximum",
             MAX_BINARY_ENUMERATION_J, minimum=0)
    scales = protocol["cost_scales"]
    if not isinstance(scales, list) or not 1 <= len(scales) <= 10:
        raise ValueError("cost scales must be a nonempty list of at most ten rational strings")
    parsed = []
    for text in scales:
        if not isinstance(text, str) or len(text) > 64:
            raise ValueError("cost scales must be short exact rational strings")
        # Fraction accepts exponent notation and would expand huge powers of
        # ten before the later value/bit checks. Canonical output never uses it.
        if re.fullmatch(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", text) is None:
            raise ValueError("cost scales must use integer or integer/fraction notation")
        try:
            parsed.append(_scale(F(text)))
        except (ValueError, ZeroDivisionError):
            raise ValueError("invalid exact rational cost scale") from None
        if str(parsed[-1]) != text:
            raise ValueError("cost scale strings must be canonical reduced fractions")
    if parsed != sorted(set(parsed)):
        raise ValueError("cost scales must be sorted and distinct")
    geometries = protocol["additional_geometries"]
    if not isinstance(geometries, list) or not 1 <= len(geometries) <= 5:
        raise ValueError("additional geometries must be a nonempty list of at most five cases")
    seen = set()
    for case in geometries:
        if not isinstance(case, dict) or set(case) != {"prompts", "pool_size", "budgets"}:
            raise ValueError("invalid additional geometry schema")
        _integer(case["prompts"], "prompt count", MAX_PROMPTS)
        _integer(case["pool_size"], "pool size", MAX_GEOMETRY_POOL)
        budgets = _budgets(case["pool_size"], case["budgets"])
        if list(budgets) != case["budgets"]:
            raise ValueError("additional budgets must be a sorted list")
        encoded = _canonical(case)
        if encoded in seen:
            raise ValueError("duplicate additional geometry")
        seen.add(encoded)
    return protocol


@lru_cache(maxsize=1024, typed=True)
def exact_weights(m, n):
    _integer(m, "pool size", 10*MAX_COUNTEREXAMPLE_J)
    _integer(n, "budget", m)
    denominator = comb(m, n)
    return tuple(F(comb(m-r, n-1), denominator) if m-r >= n-1 else F(0)
                 for r in range(1, m+1))


def greedy_blocks(m, budgets):
    """Keep the smallest budget and each next budget at least fourfold larger.

    Each retained row contributes (floor(m/(4n)), floor(m/n)] in rank space.
    The resulting disjoint blocks need not cover all ranks.
    """
    _integer(m, "pool size", MAX_GEOMETRY_POOL)
    budgets = _budgets(m, budgets)
    retained = []
    for n in budgets:
        if not retained or n >= 4*retained[-1]:
            retained.append(n)
    return [{"budget": n, "first_rank": m//(4*n)+1, "last_rank": m//n}
            for n in retained]


def _structure(m, budgets):
    blocks = greedy_blocks(m, budgets)
    budgets = _budgets(m, budgets)
    covered, density_checks = set(), 0
    minimum = F(1)
    for block in blocks:
        n, start, stop = block["budget"], block["first_rank"], block["last_rank"]
        count = stop-start+1
        _require(count > 0 and count >= F(m, 2*n), "nonempty block and size lower bound")
        ranks = set(range(start, stop+1))
        _require(not covered.intersection(ranks), "representative blocks are disjoint")
        covered.update(ranks)
        row = exact_weights(m, n)
        local_minimum = F(1)
        for r in range(start, stop+1):
            density = count*row[r-1]
            _require(density > F(1, 4), "strict block target density")
            local_minimum = min(local_minimum, density)
            density_checks += 1
        minimum = min(minimum, local_minimum)
        block["rank_count"] = count
        block["minimum_scaled_target_density"] = str(local_minimum)
    _require(blocks[0]["budget"] == 1 and blocks[0]["rank_count"] >= F(3*m, 4),
             "baseline block covers at least three quarters of the ranks")
    for n in budgets:
        representative = max(block["budget"] for block in blocks if block["budget"] <= n)
        _require(representative <= n < 4*representative, "every declared budget has a coarse representative")
    rows = [exact_weights(m, n) for n in budgets]
    envelope = tuple(max(row[r] for row in rows) for r in range(m))
    return {"budgets": budgets, "blocks": blocks, "envelope": envelope,
            "density_checks": density_checks, "minimum_density": minimum}


def _display(value):
    value = F(value)
    with localcontext() as context:
        context.prec = 40
        return format(Decimal(value.numerator)/Decimal(value.denominator), ".9f")


def _cost(m, structure, prompts, scale):
    envelope_cost = prompts*sum((min(F(1), scale*w/prompts) for w in structure["envelope"]), F(0))
    block_scale = sum((min(F(prompts*block["rank_count"]), scale)
                       for block in structure["blocks"]), F(0))
    _require(block_scale > 0 and envelope_cost > 0, "positive cost scales")
    _require(envelope_cost <= 8*block_scale, "envelope cost S <= 8 A")
    return {"pool_size": m, "budgets": list(structure["budgets"]), "prompts": prompts,
            "cost_scale": str(scale), "envelope_cost_upper": str(envelope_cost),
            "block_scale": str(block_scale), "ratio": str(envelope_cost/block_scale)}


def check_geometry(m, budgets, prompts, scale):
    """Check the block lemmas and exact rational S<=8A for one geometry."""
    _integer(prompts, "prompt count", MAX_PROMPTS)
    scale = _scale(scale)
    structure = _structure(m, budgets)
    return {**_cost(m, structure, prompts, scale), "blocks": structure["blocks"]}


def counterexample(j, *, enumerate_binary=False):
    """Check a confidence-varying obstruction without constructing 4**C_j."""
    _integer(j, "counterexample index", MAX_COUNTEREXAMPLE_J)
    if not isinstance(enumerate_binary, bool) or (enumerate_binary and j > MAX_BINARY_ENUMERATION_J):
        raise ValueError("binary enumeration is limited to j<=4")
    m, n, tau = 10*j, 9*j, F(1, 8)
    denominator = comb(m, n)
    weights = exact_weights(m, n)
    positive = tuple(w for w in weights if w > 0)
    _require(weights[0] == F(9, 10) > tau, "counterexample top singleton is unsafe")
    _require(sum(weights[1:], F(0)) == F(1, 10) < tau, "counterexample tail is safe")
    _require(sum(weights, F(0)) == 1, "counterexample target is normalized")
    _require(len(positive) == j+1 and all(weights[r] > 0 for r in range(j+1)),
             "counterexample positive support")
    _require(min(positive) == F(1, denominator), "counterexample minimum positive mass")
    checked = 0
    if enumerate_binary:
        for mask in range(1 << len(positive)):
            risk = sum((w for r, w in enumerate(positive) if mask & (1 << r)), F(0))
            _require((risk > tau) == bool(mask & 1), "binary unsafe iff support contains rank 1")
            checked += 1
    lower = F((j+1)*65535, 65536)
    return {"j": j, "pool_size": m, "budgets": [n], "prompts": 1, "tau": str(tau),
            "support_size": len(positive), "top_weight": str(weights[0]),
            "tail_weight": str(sum(weights[1:], F(0))),
            "minimum_positive_weight": str(min(positive)),
            "delta_symbolic": {"base": 4, "negative_exponent": str(denominator)},
            "optimal_zero_cost_symbolic": "1 - delta_j",
            "individual_inclusion_lower": "65535/65536",
            "competitive_ratio_lower": str(lower), "competitive_ratio_lower_display": _display(lower),
            "binary_support_tables_checked": checked,
            "fractional_label_scope": "Unsafe fractional labels must have positive rank-1 loss; positive rank-1 loss alone need not be unsafe.",
            "interpretation": "The ratio is strictly greater than the reported rational lower bound. Confidence varies at fixed tau=1/8; this is not a fixed-confidence separation or failure of every grid without 1."}


def _run_checks(protocol):
    scales = [F(text) for text in protocol["cost_scales"]]
    counts = {"exhaustive_families": 0, "additional_geometries": 0, "geometry_cases": 0,
              "block_checks": 0, "rank_density_checks": 0, "representative_budget_checks": 0,
              "cost_scale_checks": 0, "cost_rank_terms": 0}
    maximum, witness, minimum_density = F(0), None, F(1)
    additional_results = []

    def inspect(m, budgets, prompts, additional=False):
        nonlocal maximum, witness, minimum_density
        structure = _structure(m, budgets)
        counts["additional_geometries" if additional else "exhaustive_families"] += 1
        counts["block_checks"] += len(structure["blocks"])
        counts["rank_density_checks"] += structure["density_checks"]
        counts["representative_budget_checks"] += len(structure["budgets"])
        minimum_density = min(minimum_density, structure["minimum_density"])
        records = []
        for p in prompts:
            counts["geometry_cases"] += 1
            for scale in scales:
                result = _cost(m, structure, p, scale)
                ratio = F(result["ratio"])
                if ratio > maximum:
                    maximum = ratio
                    witness = {key: result[key] for key in ("pool_size", "budgets", "prompts", "cost_scale")}
                counts["cost_scale_checks"] += 1
                counts["cost_rank_terms"] += m
                records.append(result)
        if additional:
            additional_results.append({"pool_size": m, "budgets": list(structure["budgets"]),
                                       "prompts": prompts[0], "blocks": structure["blocks"], "cost_checks": records})

    for m in range(1, protocol["exhaustive_max_pool_size"]+1):
        for mask in range(1 << (m-1)):
            budgets = [1]+[n for n in range(2, m+1) if mask & (1 << (n-2))]
            inspect(m, budgets, protocol["prompt_counts"])
    for case in protocol["additional_geometries"]:
        inspect(case["pool_size"], case["budgets"], [case["prompts"]], additional=True)
    counts["minimum_scaled_target_density"] = str(minimum_density)
    counts["maximum_observed_ratio"] = {
        "value": str(maximum), "display": _display(maximum), "witness": witness,
        "interpretation": "Finite-grid diagnostic maximum S/A, not a universal constant or exact NEGEXP/OPT0 ratio."}
    counts["prompt_cancellation"] = "The checked rank density |I| w_n(r) equals (P|I|)(w_n(r)/P)."
    return counts, additional_results


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
    def invalid_constant(value):
        raise ValueError("nonfinite protocol value: " + value)
    return json.loads(data, object_pairs_hook=_unique_object, parse_constant=invalid_constant)


def build_results(protocol, protocol_path):
    """Pin one protocol snapshot, validate it, check, then recheck source pins."""
    path = Path(protocol_path).resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 1 MiB limit")
    protocol_bytes = path.read_bytes()
    snapshot = _parse_protocol(protocol_bytes)
    if protocol is not None and _canonical(protocol) != _canonical(snapshot):
        raise ValueError("supplied protocol differs from its file snapshot")
    protocol = validate_protocol(snapshot)
    files = [Path(__file__).resolve(), ROOT/"tests/test_sparse_grid.py", path,
             ROOT/"docs/sparse-grid-theorem.md"]
    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)
    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    checks, additional = _run_checks(protocol)
    cases = [counterexample(j, enumerate_binary=j <= protocol["counterexample_binary_enumeration_max_j"])
             for j in protocol["counterexample_j"]]
    result = {"schema_version": 1, "description": __doc__, "dependencies": "Python standard library only",
              "protocol": protocol, "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "source_sha256": sources, "checks": checks, "additional_geometry_results": additional,
              "missing_baseline_counterexamples": cases,
              "binary_support_tables_checked": sum(case["binary_support_tables_checked"] for case in cases),
              "claim_boundary": protocol["claim_boundary"]}
    current = {key(file): hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
    if current != sources:
        raise RuntimeError("a pinned checker, test, protocol, or proof source changed during calculation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"experiments/sparse_grid_protocol.json")
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
        print("sparse-grid checks: " + str(error), file=sys.stderr)
        return 2
    print(f"Passed {result['checks']['cost_scale_checks']:,} exact cost checks; saved {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
