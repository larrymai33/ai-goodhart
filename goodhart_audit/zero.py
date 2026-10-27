"""Standalone score-only planning and reporting for a zero-only audit.

Run ``python -m goodhart_audit.zero plan --help`` or ``report --help``.
The only mutable plan fields are selected queries' losses. Record the printed
plan commitment outside the editable annotation file before acquiring labels.
This companion does not modify or invoke the earlier inference workflows.
"""

import argparse
from decimal import Decimal, DecimalException
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import secrets
import sys

from .io import _number, load_pool, pool_fingerprint
from .zero_math import (MAX_ITEMS, MAX_PARAMETER_BITS, MAX_POOL_SIZE,
                        MAX_SERIALIZED_BITS, design_probabilities, exact_randbelow)


MAX_JSON_BYTES = 64*1024*1024
SCHEMA_VERSION = 1


def _text(value, name, *, allow_empty=False):
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(name + " must be a string" + ("" if allow_empty else " with nonwhitespace content"))
    try:
        if len(value) > MAX_JSON_BYTES or len(value.encode("utf-8")) > MAX_JSON_BYTES:
            raise ValueError(name + " exceeds the JSON size limit")
    except UnicodeError:
        raise ValueError(name + " must be valid UTF-8 text") from None
    return value


def _canonical_pools(pools):
    """Match the frozen loader's public geometry while ignoring source losses."""
    if not isinstance(pools, (list, tuple)) or not 1 <= len(pools) <= MAX_ITEMS:
        raise ValueError("pools must be a nonempty bounded list")
    result, prompt_ids, size = [], set(), None
    for pool in pools:
        if not isinstance(pool, dict):
            raise ValueError("each pool must be an object")
        pid = _text(pool.get("prompt_id"), "prompt_id")
        if pid in prompt_ids:
            raise ValueError("duplicate prompt_id")
        prompt_ids.add(pid)
        candidates = pool.get("candidates")
        if not isinstance(candidates, (list, tuple)) or not 1 <= len(candidates) <= MAX_POOL_SIZE:
            raise ValueError("candidate count exceeds the pool resource limit")
        if size is None:
            size = len(candidates)
            if len(pools)*size > MAX_ITEMS:
                raise ValueError("pool geometry exceeds the item resource limit")
        elif len(candidates) != size:
            raise ValueError("all prompts must have equal pool sizes")
        clean, ids = [], set()
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise ValueError("each candidate must be an object")
            cid = _text(candidate.get("candidate_id"), "candidate_id")
            if cid in ids:
                raise ValueError("duplicate candidate_id within prompt")
            ids.add(cid)
            item = {"candidate_id": cid, "proxy": _number(candidate.get("proxy"), "proxy")}
            if "text" in candidate:
                item["text"] = _text(candidate["text"], "candidate text", allow_empty=True)
            clean.append(item)
        clean.sort(key=lambda candidate: (-candidate["proxy"], candidate["candidate_id"]))
        result.append({"prompt_id": pid, "candidates": clean})
    result.sort(key=lambda pool: pool["prompt_id"])
    return result


def _exact_parameter(value, name):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal, Fraction)):
        raise ValueError(name + " must be an exact rational string, integer, Decimal, or Fraction")
    try:
        if isinstance(value, str):
            if len(value) > 1024:
                raise ValueError(name + " exceeds the parameter input limit")
            value = value.strip()
            if "/" in value:
                value = Fraction(value)
            else:
                value = Decimal(value)
        if isinstance(value, Decimal):
            if not value.is_finite():
                raise ValueError(name + " must be finite")
            _, digits, exponent = value.as_tuple()
            # Guard huge decimal exponents before Fraction expands powers of ten.
            if abs(exponent) > MAX_PARAMETER_BITS+len(digits) or len(digits) > 1024:
                raise ValueError(name + " exceeds the parameter bit limit")
        value = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError, DecimalException):
        raise ValueError(name + " must be a bounded exact rational parameter") from None
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_PARAMETER_BITS:
        raise ValueError(name + " exceeds the parameter bit limit")
    return value


def _json_bytes(value, *, pretty=False):
    """Bound serialized size before creating an output file."""
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=False, allow_nan=False,
                               indent=2 if pretty else None,
                               separators=None if pretty else (",", ":"))
    chunks, count = [], 0
    try:
        for chunk in encoder.iterencode(value):
            encoded = chunk.encode("utf-8")
            count += len(encoded)
            if count > MAX_JSON_BYTES-1:
                raise ValueError("JSON exceeds the 64 MiB size limit")
            chunks.append(encoded)
    except (TypeError, OverflowError, RecursionError, UnicodeError) as error:
        raise ValueError("immutable metadata must use bounded canonical JSON values") from error
    return b"".join(chunks)


def _unlabeled(plan):
    if not isinstance(plan, dict) or not isinstance(plan.get("queries"), list):
        raise ValueError("plan must be an object with a query list")
    if len(plan["queries"]) > MAX_ITEMS:
        raise ValueError("query count exceeds the item limit")
    clean = dict(plan)
    clean["queries"] = []
    for query in plan["queries"]:
        if not isinstance(query, dict) or "loss" not in query:
            raise ValueError("every query must retain its loss field")
        copied = dict(query)
        copied["loss"] = None
        clean["queries"].append(copied)
    return clean


def plan_sha256(plan):
    """Hash all immutable plan content; normalize existing loss values to null."""
    return hashlib.sha256(_json_bytes(_unlabeled(plan))).hexdigest()


def _prepare(pools, budgets, threshold, delta, rubric):
    rubric = _text(rubric, "rubric")
    clean = _canonical_pools(pools)
    # The frozen fingerprint serializer allocates its whole JSON result.
    # Bound aggregate text first, including direct API inputs sharing strings.
    _json_bytes(clean)
    tau, error = _exact_parameter(threshold, "threshold"), _exact_parameter(delta, "delta")
    count, size = len(clean), len(clean[0]["candidates"])
    design, probabilities = design_probabilities(size, budgets, count, tau, error)
    base = {"schema_version": SCHEMA_VERSION, "inference": "conservative_rational_negexp",
            "estimand": "conditional_finite_pool", "decision": "whole_declared_family",
            "pool_sha256": pool_fingerprint(clean), "prompt_count": count, "pool_size": size,
            "budgets": design["budgets"], "threshold": str(tau), "delta": str(error),
            "rubric": rubric, "design": design, "rank_origin": 1,
            "randomness": {"source": "os_random_bits", "integer_sampler": "uniform_rejection_v1",
                           "assumption": "independent uniform bits"}}
    return clean, base, probabilities


def _assemble(pools, base, probabilities, tape):
    count, size = base["prompt_count"], base["pool_size"]
    if not isinstance(tape, list) or len(tape) != count*size:
        raise ValueError("random tape must contain exactly one draw for every item")
    queries = []
    for index, token in enumerate(tape):
        if not isinstance(token, str) or not 1 <= len(token) <= (MAX_SERIALIZED_BITS+3)//4:
            raise ValueError("invalid or oversized hexadecimal random draw")
        if re.fullmatch(r"0|[1-9a-f][0-9a-f]*", token) is None:
            raise ValueError("random draws must be canonical lowercase hexadecimal")
        prompt, rank = divmod(index, size)
        probability = probabilities[rank]
        draw = int(token, 16)
        if draw >= probability.denominator:
            raise ValueError("random draw lies outside its uniform-integer range")
        if draw < probability.numerator:
            pool = pools[prompt]
            candidate = pool["candidates"][rank]
            query = {"index": index, "prompt_id": pool["prompt_id"],
                     "candidate_id": candidate["candidate_id"], "rank": rank+1,
                     "proxy": repr(candidate["proxy"]), "loss": None}
            if "text" in candidate:
                query["text"] = candidate["text"]
            queries.append(query)
    return {**base, "random_tape_hex": list(tape), "queries": queries}


def make_zero_plan(pools, budgets, threshold, delta, rubric):
    """Plan distinct inspections using scores and fresh OS random bits only.

    Threshold/confidence strings are parsed exactly. Source losses are ignored.
    Empty selections are preserved. Do not reroll or select among generated
    plans; record the returned plan's commitment before obtaining annotations.
    """
    clean, base, probabilities = _prepare(pools, budgets, threshold, delta, rubric)
    # Bound every possible realized plan before consuming random bits. A size
    # rejection based on the realized subset could otherwise filter outcomes.
    maximal = _assemble(clean, base, probabilities, ["0"]*(len(clean)*len(probabilities)))
    maximal["random_tape_hex"] = [format(probability.denominator-1, "x")
                                  for _ in clean for probability in probabilities]
    _json_bytes(maximal, pretty=True)
    del maximal
    tape = [format(exact_randbelow(probability.denominator, secrets.randbits), "x")
            for _ in clean for probability in probabilities]
    plan = _assemble(clean, base, probabilities, tape)
    _json_bytes(plan, pretty=True)
    return plan


def _loss(value):
    if value is None:
        return None
    # Floats may already have underflowed before this API sees them. Callers
    # must supply exact values; read_plan preserves JSON decimal tokens.
    if isinstance(value, bool) or not isinstance(value, (int, Decimal, Fraction)):
        raise ValueError("loss must be an exact integer, Decimal, Fraction, or null")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError("loss must be finite")
    if not 0 <= value <= 1:
        raise ValueError("loss must be in [0,1]")
    return value > 0


def zero_report(pools, plan, expected_plan_sha256):
    """Replay a committed plan; only its query loss values may have changed.

    Direct API labels must be int, Decimal, Fraction, or None; floats are
    rejected. Any positive label prevents this zero-only certificate even if
    other labels are missing. This outcome does not establish unsafe risk.
    """
    if not isinstance(expected_plan_sha256, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_plan_sha256) is None:
        raise ValueError("an externally recorded SHA-256 plan commitment is required")
    clean_plan = _unlabeled(plan)
    commitment = hashlib.sha256(_json_bytes(clean_plan)).hexdigest()
    if commitment != expected_plan_sha256.lower():
        raise ValueError("plan differs from the externally recorded commitment")
    try:
        clean_pool, base, probabilities = _prepare(pools, plan["budgets"], plan["threshold"],
                                                  plan["delta"], plan["rubric"])
        expected = _assemble(clean_pool, base, probabilities, plan["random_tape_hex"])
        if _json_bytes(clean_plan) != _json_bytes(expected):
            raise ValueError("immutable plan metadata, pool, or selected queries changed")
    except (KeyError, TypeError) as error:
        raise ValueError("malformed zero-only plan") from error
    observations = [_loss(query["loss"]) for query in plan["queries"]]
    positive = sum(value is True for value in observations)
    missing = sum(value is None for value in observations)
    status = "not_certified" if positive else "pending" if missing else "certified"
    certified = status == "certified"
    result = {
        "schema_version": SCHEMA_VERSION, "inference": base["inference"], "status": status,
        "certified": certified, "decision": base["decision"], "estimand": base["estimand"],
        "plan_sha256": commitment, "pool_sha256": base["pool_sha256"], "rubric": base["rubric"],
        "budgets": base["budgets"], "threshold": base["threshold"], "delta": base["delta"],
        "certified_budgets": base["budgets"] if certified else [],
        "expected_zero_table_labels": base["design"]["expected_zero_cost"],
        "selected_query_count": len(observations), "observed_query_count": len(observations)-missing,
        "remaining_query_count": missing, "positive_query_count": positive,
        "empty_selection": not observations,
        "assumptions": [
            "One plan was generated using independent uniform OS random bits before annotations; it was not rerolled or selected among alternatives.",
            "The plan commitment was recorded outside the editable annotation file before annotation.",
            "Queried losses are fixed correct exact values in [0,1] under the frozen rubric.",
            "The certificate concerns every declared target on these fixed pools; it does not cover new prompts or validate the labeler.",
            "An empty selected subset is an allowed randomized certificate with zero observed labels.",
            "Pending or not_certified does not establish that any target is unsafe.",
            "The recorded tape proves replay consistency, not the origin or independence of the randomness.",
        ],
    }
    _json_bytes(result, pretty=True)
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key: " + key)
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("nonfinite JSON number: " + value)


def read_plan(path):
    """Read annotations exactly, rejecting duplicate keys and nonfinite tokens."""
    path = Path(path)
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("plan exceeds the 64 MiB input limit")
    with path.open("rb") as stream:
        data = stream.read(MAX_JSON_BYTES+1)
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("plan exceeds the 64 MiB input limit")
    try:
        return json.loads(data, parse_float=Decimal, parse_constant=_reject_constant,
                          object_pairs_hook=_unique_object)
    except (DecimalException, UnicodeError, RecursionError) as error:
        raise ValueError("invalid exact annotation JSON") from error


def _write_new(path, value):
    data = _json_bytes(value, pretty=True)+b"\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan", help="Generate one score-only randomized plan")
    planning.add_argument("--pool", required=True, type=Path)
    planning.add_argument("--out", required=True, type=Path)
    planning.add_argument("--budgets", required=True)
    planning.add_argument("--threshold", required=True)
    planning.add_argument("--delta", required=True)
    planning.add_argument("--rubric", required=True)
    reporting = commands.add_parser("report", help="Replay the externally committed annotated plan")
    reporting.add_argument("--pool", required=True, type=Path)
    reporting.add_argument("--plan", required=True, type=Path)
    reporting.add_argument("--plan-sha256", required=True)
    reporting.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.out.exists():
            raise ValueError("output already exists; choose a new path")
        pools = load_pool(args.pool)
        if args.command == "plan":
            budgets = [int(value) for value in args.budgets.split(",")]
            result = make_zero_plan(pools, budgets, args.threshold, args.delta, args.rubric)
            _write_new(args.out, result)
            print(plan_sha256(result))
        else:
            result = zero_report(pools, read_plan(args.plan), args.plan_sha256)
            _write_new(args.out, result)
            print(result["status"])
    except (ValueError, OSError, DecimalException) as error:
        print("zero audit: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
