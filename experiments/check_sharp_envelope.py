"""Reproduce the sharp-envelope exact sweep and numerical tables offline.

Uses only the Python standard library and the existing full_envelope routine.
Exact finite checks support the algebra; they do not replace its proof.
Reported asymptotic constants are approximations, not certified enclosures.
"""

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from goodhart_audit.core import full_envelope


SOURCE_PATHS = (
    "goodhart_audit/core.py",
    "experiments/check_sharp_envelope.py",
)
EXACT_MAX_POOL = 200
DIAGONAL_SIZES = (10, 100, 1_000, 10_000, 100_000, 1_000_000)
PROFILE_POOL = 100_000
PROFILE_DIVISORS = (10, 4, 2, 1)
CONSTANT_CUTOFF = 1_000_000


def source_hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in SOURCE_PATHS
    }


def choose(a, b):
    return 0 if b < 0 or b > a else math.comb(a, b)


def exact_increment(m, n):
    """Independent rational CDF-crossing expression, with no core calls."""
    k = (m + 1) // n
    crossing = (
        Fraction(choose(m - k, n - 1), math.comb(m, n - 1))
        - Fraction(choose(m - k, n), math.comb(m, n))
    )
    # The two exact product forms are algebraically equivalent. Use the
    # shorter form so the full rational sweep stays small and fast.
    if n - 1 <= k - 1:
        product = Fraction(k, m - n + 1)
        for j in range(n - 1):
            product *= Fraction(m - k - j, m - j)
    else:
        product = Fraction(k, m)
        for j in range(1, k):
            product *= Fraction(m - n + 1 - j, m - j)
    if crossing != product:
        raise AssertionError(f"crossing/product mismatch: m={m}, n={n}")
    return crossing


def exact_sweep():
    pairs = 0
    for m in range(2, EXACT_MAX_POOL + 1):
        for n in range(2, m + 1):
            v = exact_increment(m, n)
            ell = Fraction((n - 1) ** (n - 1), n ** n)
            conditions = {
                "continuous_lower": v >= ell,
                "product_upper": (m - n + 1) * v <= m * ell,
                "deletion_upper": n * v <= 1,
                "sharp_increment_upper": v - ell <= (1 - ell) / (m + 1),
            }
            for name, passed in conditions.items():
                if not passed:
                    raise AssertionError(f"{name} failed: m={m}, n={n}")
            pairs += 1
    expected_pairs = EXACT_MAX_POOL * (EXACT_MAX_POOL - 1) // 2
    if pairs != expected_pairs or pairs != 19_900:
        raise AssertionError("unexpected exact-sweep size")

    ell_two = Fraction(1, 4)
    gap_two = exact_increment(2, 2) - ell_two
    bound_two = (1 - ell_two) / 3
    if gap_two != bound_two:
        raise AssertionError("m=N=2 should attain the sharp bridge bound")
    return {
        "arithmetic": "fractions.Fraction; no floating-point tolerances",
        "pool_sizes": {"minimum": 2, "maximum": EXACT_MAX_POOL},
        "budget_rule": "every integer 2 <= n <= m",
        "passed_pairs": pairs,
        "all_passed": True,
        "checks_per_pair": [
            "CDF-crossing expression equals an independent exact product form",
            "ell_n <= v_mn",
            "(m-n+1) v_mn <= m ell_n",
            "n v_mn <= 1",
            "v_mn-ell_n <= (1-ell_n)/(m+1)",
        ],
        "attained_case": {
            "pool_size": 2,
            "max_budget": 2,
            "finite_correction_exact": str(gap_two),
            "sharp_bound_exact": str(bound_two),
        },
        "scope": "Finite arithmetic checks are not a universal mathematical proof.",
    }


@lru_cache(maxsize=None)
def continuous_normalizer(n):
    return 1.0 + math.fsum(
        math.exp((j - 1) * math.log1p(-1.0 / j)) / j
        for j in range(2, n + 1)
    )


def finite_normalizer(m, n):
    proposal, normalizer = full_envelope(m, n)
    del proposal
    return normalizer


def approximate_profile(m, n, c0):
    rho = n / m
    # Exact integer division avoids a floating-point floor at reciprocal
    # breakpoints of rho. Neighboring mathematical formulas agree there.
    k = m // n
    return (
        c0 + 1.0 / math.e - continuous_normalizer(k)
        - (1.0 - rho) ** k - math.log(rho) / math.e
    )


def build_results():
    hashes = source_hashes()
    exact = exact_sweep()
    diagonal = []
    for m in DIAGONAL_SIZES:
        z = finite_normalizer(m, m)
        continuous = continuous_normalizer(m)
        diagonal.append({
            "pool_size": m,
            "max_budget": m,
            "finite_normalizer_Z": z,
            "continuous_normalizer_L": continuous,
            "finite_correction_Z_minus_L": z - continuous,
            "Z_minus_log_budget_over_e": z - math.log(m) / math.e,
            "sharp_correction_upper": (m - continuous) / (m + 1),
        })

    c0 = continuous_normalizer(CONSTANT_CUTOFF) - math.log(CONSTANT_CUTOFF) / math.e
    profile = []
    for divisor in PROFILE_DIVISORS:
        n = PROFILE_POOL // divisor
        z = finite_normalizer(PROFILE_POOL, n)
        continuous = continuous_normalizer(n)
        correction = z - continuous
        limiting = approximate_profile(PROFILE_POOL, n, c0)
        profile.append({
            "pool_size": PROFILE_POOL,
            "max_budget": n,
            "budget_pool_ratio": n / PROFILE_POOL,
            "finite_normalizer_Z": z,
            "continuous_normalizer_L": continuous,
            "finite_correction_Z_minus_L": correction,
            "limiting_profile_G_approximation": limiting,
            "finite_correction_minus_profile": correction - limiting,
            "sharp_correction_upper": (n - continuous) / (PROFILE_POOL + 1),
        })

    if source_hashes() != hashes:
        raise RuntimeError("a pinned source changed during the check; rerun")
    return {
        "schema_version": 1,
        "description": "Offline reproduction of docs/sharp-envelope.md numerical evidence",
        "source_sha256": hashes,
        "runtime": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "dependencies": "Python standard library and local goodhart_audit.core",
        },
        "protocol": {
            "randomness": "none",
            "exact_max_pool_size": EXACT_MAX_POOL,
            "diagonal_pool_sizes": list(DIAGONAL_SIZES),
            "profile_pool_size": PROFILE_POOL,
            "profile_budget_divisors": list(PROFILE_DIVISORS),
            "constant_approximation_cutoff": CONSTANT_CUTOFF,
            "continuous_evaluation": "1 + fsum(exp((n-1)*log1p(-1/n))/n)",
            "finite_evaluation": "unmodified goodhart_audit.core.full_envelope",
        },
        "exact_sweep": exact,
        "constants": {
            "status": "floating-point approximations, not certified decimal enclosures",
            "c0_approximation": c0,
            "G_at_one_approximation": c0 - 1.0 + 1.0 / math.e,
            "diagonal_constant_approximation": 2.0 * c0 - 1.0 + 1.0 / math.e,
            "method": "c0 approximated by L_cutoff-log(cutoff)/e; other values use exact limiting identities",
        },
        "diagonal_table": diagonal,
        "profile_table": profile,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "results" / "theory" / "sharp_envelope.json",
        help="JSON output path (default: results/theory/sharp_envelope.json)",
    )
    args = parser.parse_args()
    results = build_results()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(results, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    try:
        display_path = args.out.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_path = str(args.out.resolve())
    print(
        f"Passed {results['exact_sweep']['passed_pairs']:,} exact pairs; "
        f"saved {len(results['diagonal_table'])} diagonal and "
        f"{len(results['profile_table'])} profile rows to {display_path}."
    )


if __name__ == "__main__":
    main()
