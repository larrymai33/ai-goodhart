"""Annotate hand-authored integer-addition fixtures; never evaluate Python code.

This helper is an example rubric implementation, not a safety-label oracle or
an audit verifier. The separate zero report command verifies the committed plan.
"""

import argparse
import json
from pathlib import Path
import re


EQUATION = re.compile(r"([+-]?[0-9]{1,100}) \+ ([+-]?[0-9]{1,100}) = ([+-]?[0-9]{1,100})")
MAX_JSON_BYTES = 64 * 1024 * 1024


def unique_object(pairs):
    """Reject ambiguous JSON objects, including inside otherwise unused metadata."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_noninteger_number(token):
    """Unannotated plans store exact noninteger metadata as fraction strings."""
    raise ValueError(f"unexpected noninteger JSON number in unannotated plan: {token}")


def annotate_plan(plan):
    """Fill null losses using exact integer addition; retain other plan values."""
    if not isinstance(plan, dict) or not isinstance(plan.get("queries"), list):
        raise ValueError("expected a plan object with a queries list")
    losses = []
    for query in plan["queries"]:
        if not isinstance(query, dict) or not isinstance(query.get("text"), str):
            raise ValueError("each selected query must contain equation text")
        if "loss" not in query or query["loss"] is not None:
            raise ValueError("only an unannotated plan with null query losses is accepted")
        match = EQUATION.fullmatch(query["text"])
        if match is None:
            raise ValueError("malformed equation: require signed ASCII integers as 'A + B = C'")
        left, right, result = map(int, match.groups())
        losses.append(int(left + right != result))
    for query, loss in zip(plan["queries"], losses):
        query["loss"] = loss
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True,
                        help="unannotated zero-workflow plan")
    parser.add_argument("--out", type=Path, required=True,
                        help="new annotated JSON file; never overwritten")
    args = parser.parse_args()
    try:
        if args.plan.stat().st_size > MAX_JSON_BYTES:
            raise ValueError(f"plan exceeds the {MAX_JSON_BYTES}-byte input limit")
        plan = json.loads(args.plan.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object,
                          parse_float=reject_noninteger_number,
                          parse_constant=reject_noninteger_number)
        annotated = annotate_plan(plan)
        payload = json.dumps(annotated, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
        if len(payload.encode("utf-8")) > MAX_JSON_BYTES:
            raise ValueError(f"annotated plan exceeds the {MAX_JSON_BYTES}-byte output limit")
        with args.out.open("x", encoding="utf-8", newline="\n") as output:
            output.write(payload)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"Annotated {len(annotated['queries'])} selected equations; report verification is still required.")


if __name__ == "__main__":
    main()
