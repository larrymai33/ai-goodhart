# Contributing

Useful contributions include a counterexample to a stated theorem, closer prior art, independent reproduction, better audit designs with explicit guarantees, or a carefully scoped real-data evaluation.

Before changing research claims, state the target estimand and assumptions. Preserve negative results. Separate fixed-pool inference from new-prompt performance, fixed draws from unique annotations, and established methods from proposed specializations.

The core has no third-party dependencies. Run `python -m unittest discover -s tests -v`. Experiment tests use NumPy if present and otherwise skip. Use existing NumPy/Matplotlib to run `python -m experiments.run_study --out artifacts/local/reproduction`; verify with `python -m experiments.verify_results --results artifacts/local/reproduction`.

Do not commit API credentials, private prompt logs, personal data, downloaded model weights, or large datasets. Store local experiments under `artifacts/local/`, which is ignored. A changed protocol should be recorded before measuring its outcomes, and a result change must include matching source/output hashes.

The anytime study has a separate protocol and outputs. Reproduce it with `python -m experiments.run_anytime_study --out artifacts/local/anytime-reproduction`, then run `python -m experiments.verify_anytime_results --results artifacts/local/anytime-reproduction`. Add `--no-plots` when Matplotlib is unavailable. Freeze the measured sources during a run; the runner rejects source changes. The study uses the directional upper-test certificate; the CLI's default interval rule can be more conservative. Keep this distinction explicit in cost comparisons.

Numerical changes to the sequential engine require meaningful endpoint, tiny-mass, and scalar/vector conformance checks. Acquisition and betting scales must be predictable from prior observations. Do not repair an endpoint by inspecting the current label; that can invalidate the martingale argument even if a simulation appears to pass.

The optimized-design follow-up uses existing SciPy in addition to NumPy. Run `python -m experiments.run_design_study --out artifacts/local/design-reproduction` with a new directory, then `python -m experiments.verify_design_results --results artifacts/local/design-reproduction`. Preserve numerical primal–dual gaps separately from measured label costs; a smaller objective need not imply a faster threshold certificate. The verifier is standard-library-only. Reproduce the finite-pool theorem tables with `python -m experiments.check_sharp_envelope --out artifacts/local/sharp-envelope-reproduction.json`.

If reporting a reproducibility issue, include Python/NumPy versions, the command, the protocol, and the smallest input that reproduces it. Cite the exact assumption challenged by a mathematical counterexample.

The zero-table cost theorem has a separate standard-library checker: `python -B -S -m experiments.check_zero_cost --out artifacts/local/zero-cost-reproduction.json`. Choose a new output path. Keep the theorem's structured grid, label-information model, threshold, confidence, and zero-table objective explicit. Its exact rational cost certificates are not exact optima and do not evaluate the existing betting engine. Changes to the proof, checker, tests, or fixed protocol require regenerating the corresponding source-pinned artifact; preserve the older studies separately.
