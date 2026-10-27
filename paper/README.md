# Research note

The [current sharp-cost manuscript](sharp-cost/README.md) consolidates the later v0.7 theorem and counterexample with complete proofs. This directory's original source, renderer, PDF, and integrity manifest remain the frozen v0.3 paper described below.

[Read the seven-page PDF](paper.pdf) or [Markdown source](paper.md). The note consolidates the v0.3 finite-pool theory and synthetic evidence frozen at commit `e589045`. It is an AI-assisted research artifact, with no external peer review or real-model validation. See the [review guide](../docs/review-guide.md) for claims, evidence, and unresolved questions.

## Render with existing libraries

The renderer uses Python, ReportLab, Matplotlib, and Pillow already available in the environment. It neither installs dependencies nor downloads fonts, models, data, or a TeX distribution. From the repository root:

```console
python paper/build_pdf.py --out artifacts/local/rebuilt-paper.pdf
```

Math is rendered with Matplotlib's bundled STIX fonts at 240 DPI. Prose and links remain text in the PDF; equations are images. The Markdown source preserves the mathematical notation for searching and reuse. Intermediate images go under the ignored `artifacts/local/paper-build/math` directory. Rendering can differ across library versions, and the PDF contains build metadata; byte-identical PDF rebuilds are not required or claimed. The artifact manifest records the distributed PDF, its two source files, the numerical evidence hashes, and the rendering-library versions.

## Reproduce numerical evidence

```console
python -m experiments.reproduce --verify-only
python -m experiments.reproduce --out artifacts/local/paper-reproduction
```

These commands do not rebuild the PDF. Verification uses only the standard library and checks saved-artifact integrity. Full reproduction needs existing NumPy and SciPy, runs the test suite and all three numerical studies plus the theorem checker, and compares ten numerical artifacts. Choose a new output directory each time. Figures and manifest bytes are excluded from the rerun comparison. A mismatch fails explicitly and leaves a diagnostic report.

The [compact execution record](reproduction-summary.json) reports the actual full-run outcome, driver hash, environment, test count, and ten checksum pairs. The full reproduction was run within the same assisted development session. It is not an external human replication. The manuscript's 105-test count describes the frozen v0.3 release; v0.3.1 adds ten reproduction-driver tests, for 115 tests in total.
