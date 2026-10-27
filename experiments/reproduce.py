"""Verify published evidence or reproduce its numerical artifacts offline.

``--verify-only`` uses the standard library and does not import NumPy/SciPy.
It checks saved-artifact integrity; it does not recompute the tables or prove
the mathematical claims.
``--out NEWDIR`` needs the already-installed experiment dependencies, runs the
full test suite, and regenerates the studies without figures. Exact bytes need
the recorded Python, NumPy, SciPy, and platform environment; a mismatch fails
instead of being silently accepted as a successful reproduction.
"""

import argparse
import hashlib
from importlib import metadata, util
import json
from pathlib import Path
import platform
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
STUDIES = (
    ("fixed", "results", "experiments.verify_results", "experiments.run_study"),
    ("anytime", "results/anytime", "experiments.verify_anytime_results", "experiments.run_anytime_study"),
    ("design", "results/design", "experiments.verify_design_results", "experiments.run_design_study"),
)
SHARP = ROOT / "results/theory/sharp_envelope.json"
# SHA-256 of the exact blob at e589045:results/theory/sharp_envelope.json.
# Pin the artifact itself: its embedded source hashes do not protect its values.
SHARP_SHA256 = "e2090da8ae9261a3506f8615521284e3bb77943f70987733b5be69f136320052"


def run_command(arguments):
    """Run an argument vector without a shell; preserve diagnostics on failure."""
    completed = subprocess.run(
        arguments, cwd=ROOT, shell=False, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    return {"command": list(arguments), "stdout": completed.stdout, "stderr": completed.stderr}


def compare_artifact(published, reproduced, label):
    """Compare the actual bytes, with checksum pairs for the saved report."""
    original, regenerated = Path(published).read_bytes(), Path(reproduced).read_bytes()
    return {
        "label": label, "published": str(published), "reproduced": str(reproduced),
        "published_sha256": hashlib.sha256(original).hexdigest(),
        "reproduced_sha256": hashlib.sha256(regenerated).hexdigest(),
        "equal": original == regenerated,
    }


def verify_sharp(path, root):
    """Validate the pinned artifact and its sources, without recomputation/proof."""
    raw = Path(path).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SHARP_SHA256:
        raise ValueError("sharp-envelope artifact checksum differs from the published release")
    artifact = json.loads(raw)
    sources = artifact["source_sha256"]
    if not isinstance(sources, dict) or not sources:
        raise ValueError("sharp-envelope source hashes are missing")
    root = Path(root).resolve()
    for name, expected in sources.items():
        source = (root / name).resolve()
        if not source.is_relative_to(root):
            raise ValueError("sharp-envelope source path is outside the repository")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError("sharp-envelope source checksum mismatch: " + name)
    return {
        "source_count": len(sources), "artifact_sha256": actual,
        "published_artifact_sha256": SHARP_SHA256,
        "scope": "saved-artifact and source integrity; no numerical recomputation or mathematical proof",
    }


def _validate_output(out):
    out = Path(out).resolve()
    if out.is_relative_to((ROOT / "results").resolve()):
        raise ValueError("output must be outside the published results directory")
    if out.exists():
        raise ValueError("output directory must not already exist: " + str(out))
    return out


def _python_module(module, *arguments):
    # Preserve a caller's standard-library-only invocation in every child.
    no_site = ["-S"] if sys.flags.no_site else []
    return [sys.executable, "-B", *no_site, "-m", module, *map(str, arguments)]


def reproduce(out=None, *, verify_only=False):
    """Return a JSON-safe report; failed checks stop the run and set status=failed.

    Full mode creates only a new output directory. Its report is also saved
    there, including on failures after creation; preflight failures write none.
    The design generator deliberately uses its pinned published base, not the
    newly generated anytime directory.
    """
    report = {
        "schema_version": 1, "mode": "verify-only" if verify_only else "full",
        "status": "failed", "reproduction_status": "not_run",
        "figures_rerun": False, "manifest_bytes_compared": False,
        "comparison_scope": "manifest-listed CSVs, designs.json, and sharp-envelope JSON bytes",
        "verification_scope": "Saved-artifact and source integrity checks; verification alone is not numerical recomputation or mathematical proof.",
        "environment_note": "Exact byte reproduction requires the recorded Python, NumPy, SciPy, and platform environment. Figures are not rerun; manifest bytes are not compared because paths and environment can differ.",
        "current_environment": {"python": platform.python_version(), "platform": platform.platform()},
        "recorded_environments": {}, "checks": [], "checksum_pairs": [],
    }
    created = False
    step = "output_preflight"
    try:
        if verify_only:
            if out is not None:
                raise ValueError("verify-only cannot be combined with an output directory")
        elif out is None:
            raise ValueError("full reproduction requires a new output directory")
        else:
            out = _validate_output(out)
            report["output_directory"] = str(out)
            report["checks"].append({"name": step, "status": "passed"})

        manifests = {}
        for name, published, verifier, _ in STUDIES:
            step = "verify_published_" + name
            checked = run_command(_python_module(verifier, "--results", ROOT / published))
            report["checks"].append({"name": step, "status": "passed", **checked})
            manifest = json.loads((ROOT / published / "manifest.json").read_text(encoding="utf-8"))
            manifests[name] = manifest
            report["recorded_environments"][name] = {
                key: manifest[key] for key in ("python", "numpy", "scipy", "platform") if key in manifest
            }
        step = "verify_published_sharp_sources"
        checked = verify_sharp(SHARP, ROOT)
        report["checks"].append({"name": step, "status": "passed", **checked})
        report["recorded_environments"]["sharp"] = json.loads(SHARP.read_text(encoding="utf-8"))["runtime"]
        if verify_only:
            report["status"] = "verified"
            return report

        step = "installed_dependencies"
        for package in ("numpy", "scipy"):
            if util.find_spec(package) is None:
                raise RuntimeError(package + " must already be installed; this command never installs dependencies")
            report["current_environment"][package] = metadata.version(package)
        report["checks"].append({"name": step, "status": "passed"})
        step = "full_test_suite"
        checked = run_command(_python_module("unittest", "discover", "-s", "tests", "-v"))
        count = re.search(r"Ran (\d+) tests?", checked["stderr"] + checked["stdout"])
        if count is None or int(count.group(1)) == 0:
            raise RuntimeError("test discovery did not report any executed tests")
        report["checks"].append({"name": step, "status": "passed", "tests_run": int(count.group(1)), **checked})

        # Recheck after preflight/tests so a newly occupied destination is never reused.
        step = "create_output"
        out = _validate_output(out)
        out.mkdir(parents=True, exist_ok=False)
        created = True
        report["reproduction_status"] = "in_progress"
        for name, _, _, generator in STUDIES:
            step = "rerun_" + name
            arguments = ["--out", out / name]
            if name != "design":
                arguments.append("--no-plots")
            checked = run_command(_python_module(generator, *arguments))
            report["checks"].append({"name": step, "status": "passed", **checked})
        step = "rerun_sharp"
        checked = run_command(_python_module("experiments.check_sharp_envelope", "--out", out / "sharp-envelope.json"))
        report["checks"].append({"name": step, "status": "passed", **checked})

        for name, _, verifier, _ in STUDIES:
            step = "verify_reproduced_" + name
            checked = run_command(_python_module(verifier, "--results", out / name))
            report["checks"].append({"name": step, "status": "passed", **checked})
        step = "verify_reproduced_sharp_sources"
        checked = verify_sharp(out / "sharp-envelope.json", ROOT)
        report["checks"].append({"name": step, "status": "passed", **checked})
        step = "exact_artifact_comparison"
        for name, published, _, _ in STUDIES:
            for filename, expected in manifests[name]["outputs_sha256"].items():
                if Path(filename).suffix != ".csv" and not (name == "design" and filename == "designs.json"):
                    continue
                pair = compare_artifact(ROOT / published / filename, out / name / filename, name + "/" + filename)
                report["checksum_pairs"].append(pair)
                if pair["published_sha256"] != expected:
                    raise ValueError("published artifact changed during reproduction: " + pair["label"])
        sharp_pair = compare_artifact(SHARP, out / "sharp-envelope.json", "sharp-envelope.json")
        report["checksum_pairs"].append(sharp_pair)
        if sharp_pair["published_sha256"] != SHARP_SHA256 or sharp_pair["reproduced_sha256"] != SHARP_SHA256:
            raise ValueError("sharp-envelope artifact checksum differs from the published release at final comparison")
        if not report["checksum_pairs"] or not all(pair["equal"] for pair in report["checksum_pairs"]):
            raise ValueError("reproduced artifact bytes differ; inspect checksum pairs and the recorded environment")
        report["checks"].append({"name": step, "status": "passed"})
        report["status"] = "reproduced"
        report["reproduction_status"] = "exact_match"
    except Exception as error:
        failure = {"name": step, "status": "failed", "error": str(error)}
        if isinstance(error, subprocess.CalledProcessError):
            failure.update(command=error.cmd, returncode=error.returncode,
                           stdout=error.stdout or "", stderr=error.stderr or "")
        report["checks"].append(failure)
        report["reproduction_status"] = "failed" if not verify_only else "not_run"
    if created:
        try:
            (out / "reproduction-report.json").write_text(
                json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        except OSError as error:
            report["status"] = "failed"
            report["reproduction_status"] = "failed"
            report["checks"].append({"name": "save_report", "status": "failed", "error": str(error)})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-only", action="store_true")
    modes.add_argument("--out", type=Path, help="new directory outside published results; must not exist")
    args = parser.parse_args()
    report = reproduce(args.out, verify_only=args.verify_only)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
