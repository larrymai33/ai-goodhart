"""Optional score-only proposal optimization using existing NumPy and SciPy.

This module is separate from the dependency-free audit engine. Its outputs
are numerical primal/dual brackets, not machine-verified certificates.
"""

from __future__ import annotations

import math
from numbers import Real
from collections.abc import Sequence

import numpy as np
from scipy.optimize import minimize, minimize_scalar

__all__ = ["optimize_design"]


def _number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number, not a boolean")
    try:
        result = float(value)
    except (ValueError, OverflowError):
        raise ValueError(f"{name} must be a finite number") from None
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _weights(values: Sequence[Sequence[float]]) -> np.ndarray:
    try:
        rows = [[_number(value, "weight") for value in row] for row in values]
    except TypeError:
        raise ValueError("weights must be a nonempty rectangular array") from None
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("weights must be a nonempty rectangular array")
    for row in rows:
        if any(value < 0 or value > 1 for value in row):
            raise ValueError("weights must be in [0, 1]")
        total = math.fsum(row)
        if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("each weight row must sum to 1")
        row[:] = [value / total for value in row]
    return np.asarray(rows, dtype=float)


def _group_columns(weights: np.ndarray) -> tuple[np.ndarray, list[list[int]]]:
    """Identical columns can share mass without changing either objective."""
    groups_by_values: dict[tuple[float, ...], list[int]] = {}
    for index, column in enumerate(weights.T):
        if np.any(column > 0):
            groups_by_values.setdefault(tuple(column), []).append(index)
    groups = list(groups_by_values.values())
    grouped = np.column_stack([weights[:, indices[0]] * len(indices) for indices in groups])
    return grouped, groups


def _result(weights: np.ndarray, proposal: list[float], records: list[dict],
            rho: float, iterations: int) -> dict:
    """Recompute the bracket from the actual returned full-dimension objects."""
    q_total = math.fsum(proposal)
    proposal = [value / q_total for value in proposal]
    total = math.fsum(record["weight"] for record in records)
    records = [dict(record, weight=record["weight"] / total) for record in records if record["weight"] > 0]
    rows = weights.tolist()
    values = []
    for row in rows:
        variance = math.fsum(a * a / q for a, q in zip(row, proposal) if a > 0)
        maximum = max(a / q for a, q in zip(row, proposal) if a > 0)
        values.append(variance + rho * maximum)
    primal = max(values)
    target_mix = [math.fsum(record["weight"] for record in records if record["target"] == k)
                  for k in range(len(rows))]
    coordinate_mix: dict[tuple[int, int], float] = {}
    if rho:
        for record in records:
            key = record["target"], record["coordinate"]
            coordinate_mix[key] = coordinate_mix.get(key, 0.0) + record["weight"]
    mixture = []
    for j in range(len(proposal)):
        terms = [target_mix[k] * row[j] ** 2 for k, row in enumerate(rows)]
        if rho:
            terms.extend(rho * coordinate_mix.get((k, j), 0.0) * row[j] for k, row in enumerate(rows))
        mixture.append(math.fsum(terms))
    dual = math.fsum(math.sqrt(value) for value in mixture) ** 2
    if not math.isfinite(primal) or not math.isfinite(dual) or dual <= 0:
        raise RuntimeError("optimization bracket is outside floating-point range")
    if primal < dual - 128 * np.finfo(float).eps * max(primal, dual):
        raise RuntimeError("numerical primal/dual ordering failed")
    gap = max(0.0, (primal - dual) / dual)
    return {"proposal": proposal, "dual_weights": records, "primal_value": primal,
            "dual_value": dual, "relative_gap": gap, "iterations": int(iterations)}


def optimize_design(weights: Sequence[Sequence[float]], rho: float = 0.0,
                    tolerance: float = 1e-5) -> dict:
    """Minimize max_k [sum_i a_ki**2/q_i + rho*max_i a_ki/q_i].

    Inputs contain only known probability rows, never losses. Rows must sum
    to one within 1e-12 and are copied and normalized. The proposal is zero
    outside the union of row supports and positive everywhere in that union.

    For rho>0, dual_weights is a sparse list of {target, coordinate, weight}
    records for atoms B_(k,i),j=a_kj**2+rho*a_ki*1[j=i]. Coordinates refer to
    original input columns. For rho=0, coordinate is None and there is one
    possible atom per target. The records form a feasible simplex mixture;
    its dual value is (sum_j sqrt(sum_atom lambda_atom B_atom,j))**2.

    SLSQP optimizes a growing active set of dual atoms. A tiny fixed mixture
    of initial atoms protects union support during numerical optimization.
    Repeated columns are grouped exactly and expanded in the returned dual.
    ``iterations`` counts SLSQP iterations plus fallback line-search steps.
    The final relative gap is (primal_value-dual_value)/dual_value, clipped
    at zero only for roundoff. A result is returned only when this directly
    recomputed gap is <= tolerance; otherwise RuntimeError is raised.
    """
    original = _weights(weights)
    rho = _number(rho, "rho")
    tolerance = _number(tolerance, "tolerance")
    if rho < 0:
        raise ValueError("rho must be nonnegative")
    if not 0 < tolerance < 1:
        raise ValueError("tolerance must be strictly between 0 and 1")

    # A single distinct target has q=a and objective 1+rho analytically.
    if np.all(original == original[0]):
        if rho:
            records = [{"target": 0, "coordinate": j, "weight": float(value)}
                       for j, value in enumerate(original[0]) if value > 0]
        else:
            records = [{"target": 0, "coordinate": None, "weight": 1.0}]
        result = _result(original, original[0].tolist(), records, rho, 0)
        if result["relative_gap"] <= tolerance:
            return result
        raise RuntimeError("requested tolerance is below the numerical bracket gap")

    a, groups = _group_columns(original)
    target_count, dimension = a.shape
    scale = max(1.0, rho)
    base = np.square(a) / scale
    if np.any((a > 0) & (base == 0)):
        raise ValueError("positive weights are below floating-point squared-weight resolution")
    range_scale = rho / scale
    active = [(k, None if rho == 0 else int(np.argmax(a[k]))) for k in range(target_count)]
    atom_set = set(active)

    def atom_rows():
        matrix = np.array([base[k].copy() for k, _ in active])
        if rho:
            for j, (k, coordinate) in enumerate(active):
                matrix[j, coordinate] += range_scale * a[k, coordinate]
        return matrix

    atoms = atom_rows()
    anchor = np.mean(atoms, axis=0)
    anchor_weights = np.full(target_count, 1 / target_count)
    floor = min(1e-10, max(1e-14, tolerance * 1e-3))
    x = np.full(target_count, 1 / target_count)
    iterations = 0
    last_gap = math.inf

    for _ in range(128):
        def evaluate(z):
            mixture = (1 - floor) * (z @ atoms) + floor * anchor
            if np.any(mixture <= 0) or not np.all(np.isfinite(mixture)):
                raise RuntimeError("dual mixture lost positive union support")
            roots = np.sqrt(mixture)
            normalizer = float(np.sum(roots))
            q = roots / normalizer
            dual = normalizer * normalizer
            gradient = (1 - floor) * (atoms @ (1 / q))
            return -dual, -gradient

        solution = minimize(evaluate, x, method="SLSQP", jac=True,
                            bounds=[(0.0, 1.0)] * len(x),
                            constraints={"type": "eq", "fun": lambda z: float(np.sum(z) - 1),
                                         "jac": lambda z: np.ones(len(z))},
                            options={"ftol": min(1e-12, max(1e-14, tolerance * tolerance * 0.01)),
                                     "maxiter": 1000, "disp": False})
        iterations += int(solution.nit)
        if not np.all(np.isfinite(solution.x)):
            raise RuntimeError("numerical optimizer returned nonfinite dual weights")
        x = np.maximum(solution.x, 0.0)
        total = float(np.sum(x))
        if total <= 0:
            raise RuntimeError("numerical optimizer returned an empty dual mixture")
        x /= total
        lam = (1 - floor) * x
        lam[:target_count] += floor * anchor_weights
        mixture = lam @ atoms
        roots = np.sqrt(mixture)
        q = roots / np.sum(roots)
        if np.any(q <= 0) or not np.all(np.isfinite(q)):
            raise RuntimeError("proposal lost positive union support")
        variance = np.sum(base / q, axis=1)
        gradient_grid = variance[:, None] + range_scale * a / q if rho else variance[:, None]
        primal = float(np.max(gradient_grid))
        dual = float(np.sum(roots)) ** 2
        last_gap = max(0.0, (primal - dual) / dual)

        if last_gap <= tolerance:
            proposal = [0.0] * original.shape[1]
            for group_index, indices in enumerate(groups):
                for index in indices:
                    proposal[index] = float(q[group_index]) / len(indices)
            records = []
            for (k, coordinate), value in zip(active, lam):
                if value <= 0:
                    continue
                if coordinate is None:
                    records.append({"target": k, "coordinate": None, "weight": float(value)})
                else:
                    for index in groups[coordinate]:
                        records.append({"target": k, "coordinate": index,
                                        "weight": float(value) / len(groups[coordinate])})
            result = _result(original, proposal, records, rho, iterations)
            if result["relative_gap"] <= tolerance:
                return result
            last_gap = result["relative_gap"]

        # Add the most violated omitted atoms; no dense K*D by D tensor.
        additions = []
        for flat in np.argsort(-gradient_grid, axis=None, kind="stable"):
            k, coordinate = divmod(int(flat), gradient_grid.shape[1])
            atom = (k, coordinate if rho else None)
            if gradient_grid[k, coordinate] <= dual * (1 + tolerance * 0.25):
                break
            if atom not in atom_set and (not rho or a[k, coordinate] > 0):
                additions.append(atom)
                atom_set.add(atom)
                if len(additions) == 32:
                    break
        if additions:
            active.extend(additions)
            x = np.pad(x, (0, len(additions)))
            atoms = atom_rows()
            continue

        # A feasible line search can recover from an imperfect SLSQP status.
        worst_flat = int(np.argmax(gradient_grid))
        worst_k, worst_coordinate = divmod(worst_flat, gradient_grid.shape[1])
        worst_atom = (worst_k, worst_coordinate if rho else None)
        if worst_atom not in atom_set:
            raise RuntimeError("violated dual atom was not added")
        vertex = np.zeros_like(x)
        vertex[active.index(worst_atom)] = 1.0
        line = minimize_scalar(lambda step: evaluate((1 - step) * x + step * vertex)[0],
                               bounds=(0.0, 1.0), method="bounded",
                               options={"xatol": 1e-14, "maxiter": 100})
        iterations += 1
        candidate = (1 - float(line.x)) * x + float(line.x) * vertex
        if evaluate(candidate)[0] >= evaluate(x)[0] - 4 * np.finfo(float).eps * max(1.0, dual):
            break
        x = candidate
    raise RuntimeError(f"optimization did not reach relative gap {tolerance:g}; last gap {last_gap:.6g}")
