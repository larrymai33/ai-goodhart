"""Render the saved monotone-placement certificates without recalculating them."""

import argparse
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_RESULT_BYTES = 16 * 1024 * 1024
BUDGETS = [1, 2, 4, 8, 16, 32, 64]
MULTIPLIERS = [2048, 4096]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_data(data):
    """Check the plotted matrix and its exact selection; do not replay the DP."""
    geometry = data["protocol"]["geometry"]
    expected = {"prompts": 32, "pool_size": 64, "budgets": BUDGETS,
                "tau": "1/10", "epsilon": "1/160", "delta": "1/20"}
    require(all(geometry[key] == value for key, value in expected.items()), "original decision geometry required")
    require(data["protocol"]["multipliers"] == MULTIPLIERS, "registered multipliers required")
    require((data["frontier_geometry_count"], data["registered_frontier_dual_count"],
             data["total_actual_geometry_dual_count"]) == (193, 386, 387), "complete registered matrix required")
    frontiers = data["frontiers"]
    require(len(frontiers) == 193, "expected 193 frontier records")
    curves, populations, certificates = {penalty: [] for penalty in MULTIPLIERS}, [], []
    for k, row in enumerate(frontiers):
        size, head, fixed = row["unknown_population"], row["head_zeros"], row["fixed_bottom_ones"]
        require(row["null_unknown_ones"] == k and fixed == 192-k and size+head+fixed == 2048
                and size >= k+13 and head >= 0, "frontier count or placement mismatch")
        require(row["all_original_targets_margin_safe"] is True and row["original_declared_budgets"] == BUDGETS,
                "whole-grid margin-safe frontier required")
        rows = row["registered_dual_certificates"]
        require(len(rows) == 2 and [item["multiplier"] for item in rows] == MULTIPLIERS,
                "each frontier requires both registered multipliers")
        populations.append(size)
        for item in rows:
            require(item["null_unknown_ones"] == k and item["unknown_population"] == size
                    and F(item["delta"]) == F(1, 20), "certificate placement or error scope mismatch")
            lower = F(item["dual_lower_exact"])
            require(item["denominator"] > 0 and lower == F(item["value_numerator"], item["denominator"])
                    - F(item["multiplier"], 20), "dual fraction does not match its integer certificate")
            curves[item["multiplier"]].append(lower)
            certificates.append(item)
    best = max(certificates, key=lambda item: F(item["dual_lower_exact"]))
    selected = data["selected_registered_certificate"]
    require(selected["globally_optimized_prior_or_multiplier"] is False, "selection is restricted to the registered family")
    require(all(selected[key] == best[key] for key in ("null_unknown_ones", "unknown_population", "multiplier"))
            and F(selected["dual_lower_exact"]) == F(best["dual_lower_exact"]), "selected record differs from the exact registered maximum")
    return list(range(193)), populations, curves, selected


def source_hashes(data):
    hashes = data["source_sha256"]
    require(isinstance(hashes, dict) and len(hashes) == 7, "seven saved calculation source pins required")
    for name, expected in hashes.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "source pin must stay within the repository")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, "saved source pin mismatch: " + name)


def draw(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ks, populations, curves, selected = validate_data(data)
    style = {"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
             "axes.spines.right": False, "svg.fonttype": "none", "svg.hashsalt": "monotone-placement-v1"}
    with plt.rc_context(style):
        fig, axes = plt.subplots(2, 1, figsize=(8, 7.2), sharex=True)
        fig.subplots_adjust(left=0.12, right=0.97, top=0.87, bottom=0.14, hspace=0.29)
        fig.suptitle("Monotone placement strengthens the cost lower bound", x=0.12, y=0.97, ha="left", fontsize=14)
        fig.text(0.12, 0.925, "Original seven budgets · 2,048 cells · τ = 0.1 · ε = 1/160 · δ = 0.05", fontsize=10)
        axes[0].plot(ks, populations, color="#275d86", linewidth=1.8)
        axes[0].set(title="A   Largest feasible unknown block for each null count", ylabel="Unknown cells, N")
        colors = {2048: "#275d86", 4096: "#bf6516"}
        for penalty in MULTIPLIERS:
            axes[1].plot(ks, [float(value) for value in curves[penalty]], color=colors[penalty],
                         linewidth=1.8, label=f"λ = {penalty:,}")
        axes[1].set(title="B   Exact dual certificates from the registered multipliers",
                    xlabel="Null positives in the unknown block, k", ylabel="Expected-query lower bound")
        best_k, best_value = selected["null_unknown_ones"], F(selected["dual_lower_exact"])
        for axis in axes:
            axis.axvline(best_k, color="#8b202b", linestyle=":", linewidth=1, alpha=0.65)
            axis.grid(axis="y", alpha=0.18)
            axis.set_xlim(0, 192)
        axes[1].scatter([best_k], [float(best_value)], s=85, color="#8b202b", edgecolor="white", zorder=4)
        floor_millis = best_value.numerator*1000//best_value.denominator
        label = (f"Registered maximum\nk = {best_k}, λ = {selected['multiplier']:,}\n"
                 f"lower ≥ {floor_millis//1000:,}.{floor_millis%1000:03d}")
        axes[1].annotate(label, (best_k, float(best_value)), xytext=(20, -56), textcoords="offset points",
                         fontsize=9, color="#691b25", arrowprops={"arrowstyle": "-", "color": "#8b202b"})
        axes[1].legend(frameon=False, loc="lower right")
        axes[1].set_xticks([0, 32, 64, 96, 128, 160, 192])
        fig.text(0.12, 0.045, "Selection covers 193 frontier placements × 2 multipliers; the separate clean witness is excluded.\n"
                 "This is a cost lower certificate, not a globally optimal prior or a valid auditing policy.", fontsize=8.5, color="#444444")
        svg, png = BytesIO(), BytesIO()
        try:
            fig.savefig(svg, format="svg", metadata={"Date": None, "Creator": "plot_monotone_placement.py"})
            fig.savefig(png, format="png", dpi=160, metadata={"Software": "plot_monotone_placement.py"})
        finally:
            plt.close(fig)
    return svg.getvalue(), png.getvalue(), matplotlib.__version__


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True, help="ignored PNG path under artifacts/local")
    parser.add_argument("--manifest", type=Path, help="optional separate result/renderer/SVG provenance record")
    args = parser.parse_args(argv)
    try:
        paths = [path.resolve() for path in (args.svg, args.preview, args.manifest) if path is not None]
        require(len(set(paths)) == len(paths) and all(not path.exists() for path in paths), "choose distinct fresh output paths")
        require(all(path.is_relative_to(ROOT) for path in paths), "outputs must be within this repository")
        require(args.preview.resolve().is_relative_to(ROOT / "artifacts/local"), "PNG preview must remain under ignored artifacts/local")
        require(args.svg.suffix.lower() == ".svg" and args.preview.suffix.lower() == ".png", "SVG and PNG extensions required")
        with args.result.open("rb") as stream:
            raw = stream.read(MAX_RESULT_BYTES+1)
        require(len(raw) <= MAX_RESULT_BYTES, "result exceeds the 16 MiB renderer limit")
        data = json.loads(raw)
        source_hashes(data)
        validate_data(data)
        renderer = Path(__file__).resolve()
        renderer_bytes = renderer.read_bytes()
        svg, png, version = draw(data)
        source_hashes(data)
        require(args.result.read_bytes() == raw and renderer.read_bytes() == renderer_bytes, "result or renderer changed during drawing")
        def key(path):
            return path.resolve().relative_to(ROOT).as_posix()
        manifest = {"schema_version": 1, "description": "Presentation of saved exact certificates; no dynamic program rerun",
                    "frontier_geometry_count": 193, "registered_frontier_dual_count": 386,
                    "selected_registered_certificate": data["selected_registered_certificate"],
                    "matplotlib_version": version, "floating_point_scope": "Drawing only; exact fractions validate values and selection",
                    "source_sha256": {key(args.result): hashlib.sha256(raw).hexdigest(),
                                      key(renderer): hashlib.sha256(renderer_bytes).hexdigest(),
                                      key(args.svg): hashlib.sha256(svg).hexdigest()}}
        outputs = [(args.svg, svg), (args.preview, png)]
        if args.manifest:
            outputs.append((args.manifest, (json.dumps(manifest, indent=2, sort_keys=True)+"\n").encode("utf-8")))
        for path, contents in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(contents)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("monotone-placement figure: " + str(error), file=sys.stderr)
        return 2
    print("Saved SVG, ignored PNG preview" + (", and separate figure manifest." if args.manifest else "."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
