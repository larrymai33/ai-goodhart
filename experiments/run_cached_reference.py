"""Frozen synthetic software demonstration of the cached reference auditor.

The fixed seeds illustrate execution and charged label counts; they do not
estimate power, prove a false-certificate rate, or measure any real model.
"""

import argparse
from fractions import Fraction as F
import hashlib
import importlib
import json
from math import comb
from pathlib import Path
import random
import sys

from goodhart_audit import cached

ROOT = Path(__file__).resolve().parents[1]
IMPORTED_ENGINE_PATH = Path(cached.__file__).resolve()
IMPORTED_MATH_PATH = Path(importlib.import_module(cached.design.__module__).__file__).resolve()
MAX_PROTOCOL_BYTES = 16384
CANONICAL_PROTOCOL = {
    "version": 1,
    "release": "0.13.1",
    "title": "Frozen software demonstration of the cached likelihood reference auditor",
    "evidence_type": "seeded_synthetic_fixed_table_software_demonstration",
    "status": "Fixed before the saved demonstration runs, after implementation tests; not external preregistration or an independent experiment",
    "prompts": [1, 32, 1024],
    "pool_size": 64,
    "budgets": [1, 2, 4, 8, 16, 32, 64],
    "tau": "1/10", "epsilon": "1/160", "delta": "1/20", "eta": "1",
    "seeds": [11, 29, 47],
    "scenarios": ["all_zero", "constant_margin", "rare_top", "boundary_constant", "unsafe_constant"],
    "scenario_definitions": {
        "all_zero": {"loss": "0", "support": "all_ranks"},
        "constant_margin": {"loss": "3/32", "support": "all_ranks"},
        "rare_top": {"loss": "3/32", "support": "rank_zero_only"},
        "boundary_constant": {"loss": "1/10", "support": "all_ranks"},
        "unsafe_constant": {"loss": "17/160", "support": "all_ranks"},
    },
    "prompt_pattern": "Every prompt has the same declared rank pattern; no model, annotation service, or fresh-prompt population is sampled",
    "registered_runs": 45,
    "run_order": "prompts, then scenarios, then seeds, in their listed orders",
    "randomness": "Create a new Python random.Random(seed) for every run and pass its randrange method as randbelow; seeds are reused across scenarios and geometries",
    "truth": "Compute exact risks independently from the fixed rank pattern and binomial winner weights, outside the engine; reveal labels to the engine only through its oracle callback",
    "trace_hash": "SHA-256 streamed over acquisition-order UTF-8 JSON records, sorted keys and compact separators, followed by one LF per record; fields prompt_index,rank_index,loss,phase,budget,proposal_index; loss is str(Fraction), indices/counts are integers, absent values are null",
    "source_pin_count": 10,
    "output": "One deterministic JSON artifact with 45 rows, source pins, exact truths and charged counts; no full acquisition traces or runtime measurements",
    "checks": "One oracle call per item; exact trace and charge agreement; finite proposal caps; no certificate contradicting observed risk; all supported safe tables in this matrix complete; source bytes unchanged during calculation",
    "claim_boundary": "Illustrative seeded software runs on synthetic fixed rational tables, not a power study, an independent experiment, model efficiency evidence, a new generic testing method, or an improved original-instance minimax bound. Per-run counts need not be below expected bounds. Unsafe tables may validly receive statistical false certificates within the theorem's error allowance; observed false-certificate counts do not establish a general error rate.",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("cached reference check failed: " + message)


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as error:
        raise ValueError("protocol must contain bounded JSON values") from error


def parse_protocol(data):
    if len(data) > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 16 KiB limit")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate protocol key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("invalid protocol number: " + value)

    try:
        return json.loads(data, object_pairs_hook=unique, parse_constant=invalid)
    except (UnicodeError, RecursionError) as error:
        raise ValueError("invalid bounded protocol JSON") from error


def validate_protocol(protocol):
    if _canonical(protocol) != _canonical(CANONICAL_PROTOCOL):
        raise ValueError("protocol differs from the frozen cached reference matrix")
    return protocol


def _independent_weights(pool_size, budget):
    denominator = comb(pool_size, budget)
    return tuple(F(comb(pool_size-rank-1, budget-1), denominator)
                 if pool_size-rank >= budget else F(0)
                 for rank in range(pool_size))


def run_case(protocol, prompts, scenario, seed):
    """Run one predeclared case; exact table truth is never passed to audit."""
    m, budgets = protocol["pool_size"], tuple(protocol["budgets"])
    tau, epsilon, delta, eta = (F(protocol[name]) for name in ("tau", "epsilon", "delta", "eta"))
    specification = protocol["scenario_definitions"][scenario]
    value = F(specification["loss"])
    pattern = tuple(value if specification["support"] == "all_ranks" or rank == 0
                    else F(0) for rank in range(m))
    weights = tuple(_independent_weights(m, budget) for budget in budgets)
    truths = tuple(sum((mass*loss for mass, loss in zip(row, pattern)), F(0))
                   for row in weights)
    safe, margin = max(truths) <= tau, max(truths) <= tau-epsilon
    called = set()

    def oracle(prompt, rank):
        _require(type(prompt) is int and type(rank) is int and
                 0 <= prompt < prompts and 0 <= rank < m, "oracle item indices")
        item = (prompt, rank)
        _require(item not in called, "each item must call the oracle only once")
        called.add(item)
        return pattern[rank]

    generator = random.Random(seed)
    result = cached.audit(prompts, m, budgets, tau, epsilon, delta, oracle,
                          eta=eta, randbelow=generator.randrange)
    plan = result.design
    _require((plan.prompts, plan.pool_size, plan.budgets) == (prompts, m, budgets),
             "engine retained the original geometry and whole family")
    _require(result.status in ("certified", "not_certified"), "recognized whole-family status")
    _require(result.distinct_labels == len(called), "trace count equals charged oracle calls")
    _require(result.distinct_labels <= prompts*(m-min(budgets)+1), "positive union support count")
    _require(len(result.budget_results) == len(budgets), "every original budget has a result")
    total_cap = plan.proposal_cap*len(budgets)
    _require(result.proposals <= total_cap, "finite total proposal cap")
    if result.mode == "prefix":
        _require(result.proposals == 0, "prefix mode uses no virtual proposals")
    trace_items, rank_sums = set(), [F(0)]*m
    digest = hashlib.sha256()
    phases = {"proposal": 0, "prefix": 0, "census": 0}
    for entry in result.acquisitions:
        item = (entry.prompt_index, entry.rank_index)
        _require(item in called and item not in trace_items, "unique acquired trace identities")
        _require(entry.loss == pattern[entry.rank_index], "trace loss equals callback loss")
        _require(entry.phase in phases, "recognized acquisition phase")
        trace_items.add(item)
        rank_sums[entry.rank_index] += entry.loss
        phases[entry.phase] += 1
        digest.update(_canonical({"prompt_index": entry.prompt_index,
                                  "rank_index": entry.rank_index,
                                  "loss": str(entry.loss), "phase": entry.phase,
                                  "budget": entry.budget,
                                  "proposal_index": entry.proposal_index}) + b"\n")
    _require(trace_items == called, "trace covers every charged oracle call")
    observed = tuple(sum((mass*loss/prompts for mass, loss in zip(row, rank_sums)), F(0))
                     for row in weights)
    if result.status == "certified":
        _require(max(observed) <= tau, "certificate cannot contradict observed risk")
        _require(all(row.status == "passed" for row in result.budget_results),
                 "whole-family certificate requires every budget to pass")
    _require(not safe or result.status == "certified", "all supported safe matrix tables complete")
    budget_rows = []
    for budget, truth, row in zip(budgets, truths, result.budget_results):
        _require(row.budget == budget, "original budget result order")
        _require(0 <= row.proposals <= plan.proposal_cap, "finite per-budget proposal cap")
        if row.exact_risk is not None:
            _require(row.exact_risk == truth, "engine exact risk equals independent truth")
        budget_rows.append({"budget": budget, "status": row.status,
                            "pass_reason": row.pass_reason, "proposals": row.proposals,
                            "exact_risk": None if row.exact_risk is None else str(row.exact_risk)})
    return {"prompts": prompts, "pool_size": m, "budgets": list(budgets),
            "scenario": scenario, "seed": seed, "mode": result.mode,
            "status": result.status, "proposals": result.proposals,
            "distinct_labels": result.distinct_labels, "oracle_calls": len(called),
            "exact_truth_risks": {str(n): str(risk) for n, risk in zip(budgets, truths)},
            "whole_family_safe": safe, "margin_safe": margin,
            "false_certificate": result.status == "certified" and not safe,
            "expected_label_bound": str(result.expected_label_bound),
            "factor_guarantee": plan.factor_guarantee,
            "proposal_cap_per_budget": plan.proposal_cap, "total_proposal_cap": total_cap,
            "prefix_cutoff": plan.prefix_cutoff, "fallback_reason": result.fallback_reason,
            "fallback_budget": result.fallback_budget, "budget_results": budget_rows,
            "phase_counts": phases, "acquisition_trace_sha256": digest.hexdigest()}


def calculate(protocol):
    validate_protocol(protocol)
    runs = []
    for prompts in protocol["prompts"]:
        for scenario in protocol["scenarios"]:
            for seed in protocol["seeds"]:
                runs.append(run_case(protocol, prompts, scenario, seed))
                if protocol["registered_runs"] > 5:
                    print(f"cached reference: {len(runs)}/{protocol['registered_runs']} "
                          f"completed (P={prompts}, {scenario}, seed={seed})",
                          file=sys.stderr, flush=True)
    _require(len(runs) == protocol["registered_runs"], "complete registered run matrix")
    return {"run_count": len(runs), "runs": runs,
            "all_safe_matrix_runs_certified": all(row["status"] == "certified"
                                                  for row in runs if row["whole_family_safe"]),
            "observed_false_certificates": sum(row["false_certificate"] for row in runs)}


def build_results():
    path = (ROOT/"experiments/cached_reference_protocol.json").resolve()
    if path.stat().st_size > MAX_PROTOCOL_BYTES:
        raise ValueError("protocol exceeds the 16 KiB limit")
    with path.open("rb") as stream:
        protocol_bytes = stream.read(MAX_PROTOCOL_BYTES+1)
    snapshot = validate_protocol(parse_protocol(protocol_bytes))
    files = [Path(__file__).resolve(), path, IMPORTED_ENGINE_PATH, IMPORTED_MATH_PATH,
             ROOT/"tests/test_cached.py", ROOT/"tests/test_cached_math.py",
             ROOT/"tests/test_cached_exact.py", ROOT/"tests/test_cached_reference_runner.py",
             ROOT/"docs/cached-reference-numerics.md", ROOT/"docs/cached-likelihood-audit.md"]

    def key(file):
        return file.relative_to(ROOT).as_posix() if file.is_relative_to(ROOT) else str(file)

    sources = {key(file): hashlib.sha256(protocol_bytes if file == path else file.read_bytes()).hexdigest()
               for file in files}
    _require(len(sources) == snapshot["source_pin_count"], "ten distinct direct and imported source pins")
    result = {"schema_version": 1, "release": snapshot["release"],
              "description": __doc__, "dependencies": "Python standard library only",
              "evidence_type": snapshot["evidence_type"], "protocol": snapshot,
              "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
              "source_sha256": sources, **calculate(snapshot),
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
        raise RuntimeError("a pinned engine, helper, protocol, runner, test, or proof changed during calculation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.exists():
            raise ValueError("output already exists; choose a new artifact path")
        result = build_results()
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
    except (ValueError, RuntimeError, OSError) as error:
        print("cached reference: " + str(error), file=sys.stderr)
        return 2
    print("Saved the frozen synthetic cached-auditor demonstration to " + str(args.out) + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
