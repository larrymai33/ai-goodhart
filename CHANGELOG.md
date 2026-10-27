# Research releases

## 0.3.0 — 26 October 2026

Adds a sharp uniform finite-without-replacement envelope remainder, a second-order joint-limit profile, and a reproducible exact-arithmetic check. Corrects the initial abstract-only comparison with Fitas v2: the continuous normalizer and envelope design were already prior work.

Adds attributed variance-optimal and fixed-width proposals with numerical primal–dual brackets. The [follow-up comparison](docs/design-report.md) reuses the five verified v0.2 baselines and adds two methods on identical synthetic paths. It shows that the optimized proposals outperform the envelope on some stopping targets, and retains counterexamples. This is not a new holdout or a claim that either objective optimizes all unique-label costs.

Preserves measured v0.1/v0.2 sources and outputs. New runner refuses nonempty output directories, pins the base manifest, and checks reuse and source stability.

## 0.2.0 — 26 October 2026

Adds audits with distinct queries and confidence sequences valid at every labeled prefix. The statistical construction adapts established weighted-without-replacement betting methods, with explicit attribution and a finite-pool proof. The query plan freezes the random order, target budgets, proposal, bets, and confidence level before labels are supplied.

The new paired synthetic study compares five acquisition proposals on eight loss patterns at equal unique-label cost. It includes 4,000 method paths, 16,000 checkpoint records, raw measurements, a separate protocol and manifest, and an aggregate verifier. It measures the directional upper-test certificate; the CLI defaults to a more conservative interval rule. Advantages and counterexamples appear in the [report](docs/anytime-report.md).

The original fixed-draw commands and v0.1 measurements retain their semantics. No real-model evidence, external novelty determination, or human peer review is claimed.

## 0.1.0 — 26 October 2026

Initial fixed-pool rank-envelope analysis, fixed-draw importance audit workflow, and reproducible study of 32,000 audit evaluations. Includes proofs, baseline comparisons, negative results, and [contribution disclosure](docs/provenance.md).
