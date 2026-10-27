# Contributing

Useful contributions include a counterexample to a stated theorem, closer prior art, independent reproduction, better audit designs with explicit guarantees, or a carefully scoped real-data evaluation.

Before changing research claims, state the target estimand and assumptions. Preserve negative results. Separate fixed-pool inference from new-prompt performance, fixed draws from unique annotations, and established methods from proposed specializations.

The core has no third-party dependencies. Run `python -m unittest discover -s tests -v`. Experiment tests use NumPy if present and otherwise skip. Use existing NumPy/Matplotlib to run `python -m experiments.run_study --out artifacts/local/reproduction`; verify with `python -m experiments.verify_results --results artifacts/local/reproduction`.

Do not commit API credentials, private prompt logs, personal data, downloaded model weights, or large datasets. Store local experiments under `artifacts/local/`, which is ignored. A changed protocol should be recorded before measuring its outcomes, and a result change must include matching source/output hashes.

If reporting a reproducibility issue, include Python/NumPy versions, the command, the protocol, and the smallest input that reproduces it. Cite the exact assumption challenged by a mathematical counterexample.
