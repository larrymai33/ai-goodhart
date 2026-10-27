# Scientific review guide

This guide maps the project's claims to inspectable evidence. All experiments use synthetic fixed pools and fixed loss labels. External novelty review, independent human replication, real-model validation, and practical adoption remain unestablished. [Provenance](provenance.md) describes the substantial agent assistance and distinguishes agent review from human review.

The companion [seven-page research note](../paper/paper.pdf) has [editable Markdown source](../paper/paper.md) and [build instructions](../paper/README.md). It consolidates the existing v0.3 evidence; the notes and saved results below provide supporting detail.

The v0.4 follow-up is the [zero-table cost theorem](zero-cost-theorem.md), with [exact finite checks and cost certificates](zero-cost-report.md). It analyzes an established independent-inclusion audit and a whole-family decision, rather than changing the earlier confidence-sequence engine.

## Claim-to-evidence map

| Claim or question | Evidence to inspect | Boundary |
| --- | --- | --- |
| A classical audit design has a finite rank-family cost approximation guarantee against all valid adaptive audits. | [Full proof](zero-cost-theorem.md), [fixed check protocol](../experiments/zero_cost_protocol.json), [exact checker](../experiments/check_zero_cost.py), [cost certificates](zero-cost-report.md). | Expected cost only on the all-zero fixed-label table; exact unit-cost labels without free loss information; almost-sure zero-table certification; a predeclared whole-family decision; specified grid, threshold, and confidence restrictions. The generic design and optimization are prior art. The universal factor is loose; geometry-specific brackets are bounds, not exact optima. |
| The target is the loss of the winner of a uniform subset of distinct candidates, under a frozen total order. | [Target and rank law](theory.md#1-target-ordering-and-assumptions), [core](../goodhart_audit/core.py), [core tests](../tests/test_core.py). | Conditions on the recorded pools and correct fixed labels; no new-prompt guarantee. The selection rule and the audit sampling rule are separate objects. |
| The finite envelope has an adjacent-total-variation decomposition, a uniform remainder relative to the continuous envelope, and a joint-limit correction profile. | [Original proof](theory.md#3-exact-finite-pool-envelope-theorem), [sharp proof, statements A-D](sharp-envelope.md), [exact tests](../tests/test_sharp_envelope.py), [standalone checker](../experiments/check_sharp_envelope.py), [saved evidence](../results/theory/sharp_envelope.json). | The checker covers 19,900 exact rational increment cases through pool size 200. Finite checks support the algebra; the proof establishes universal statements. Novelty is provisional. |
| The continuous normalizer, generic envelope construction, and sequential inference are established foundations. | [Corrected related work](related-work.md), [anytime correspondence](anytime-related-work.md), [anytime proof](anytime-theory.md). | Fitas v2 already gives the continuous integer-budget normalizer and logarithmic coefficient; Shtarkov's construction supplies the generic minimax-ratio identity; Shekhar et al. supply weighted-without-replacement betting. The initial abstract-only Fitas comparison was incomplete. |
| Variance and fixed-width objectives produce numerically optimized proposals. | [Objective definitions](design-report.md#what-is-optimized), [optimizer](../goodhart_audit/design.py), [independent checks](../tests/test_design.py), [proposals and dual weights](../results/design/designs.json). | The objectives are prior art. Feasible primal and dual values bracket their optima numerically. These are floating-point checks, not formal arithmetic certificates. |
| Those objectives need not minimize actual certification cost. | [All follow-up summaries](../results/design/summary.csv), [path/checkpoint records](../results/design/replicates.csv), [outcome interpretation](design-report.md#certification-outcomes). | Every proposal uses the same anytime engine. Costs use the directional upper test, reproduced with `--rule upper-test`; the CLI default additionally checks for an empty two-sided interval. Censored runs are not successful certifications. |
| Reported counts and reuse are auditable. | [v0.1 manifest](../results/manifest.json), [v0.2 manifest](../results/anytime/manifest.json), [follow-up protocol](../experiments/design_protocol.json), [follow-up manifest](../results/design/manifest.json), [verification code](../experiments/verify_design_results.py). | v0.1: 32,000 method/horizon evaluations from 1,600 scenario-replicate streams. The anytime follow-up: 4,000 reused plus 1,600 new method paths, 22,400 checkpoint rows, and 224 aggregates from the same 800 streams. Methods and checkpoints are paired, not independent experiments. |

Primary attribution anchors are [Fitas (2026, v2), Section 2.4 and Supplement S2](https://arxiv.org/html/2608.21496v2), [Shekhar et al. (2023), Definition 2 and Theorem 1](https://proceedings.mlr.press/v216/shekhar23a.html), and [Sarkar and Baichoo (2026), Section 7.6](https://arxiv.org/html/2609.40190v1). The proposed mathematical distinction is the finite-without-replacement remainder and joint-limit profile, rather than the continuous coefficient or generic audit methods.

The cost follow-up adds the finite rank-block comparison as another contribution candidate. Its [attribution section](zero-cost-theorem.md#8-attribution-and-claim-boundary) covers NEGEXP and multi-target reuse, audit-subset optimization, earlier approximation results, multiscale lower bounds, and finite-table zero-path coupling. Novelty remains subject to specialist review.

## Reproduction and provenance

The unified entry point for this review package is:

```console
python -m experiments.reproduce --verify-only
python -m experiments.reproduce --out artifacts/local/review-reproduction
```

The first command checks saved source/artifact integrity, including the release-pinned theorem JSON. It does not recompute tables or prove mathematical claims. The second runs the tests and all numerical studies in a new directory, comparing ten artifacts byte for byte and saving a diagnostic report. Figures are not rerun, and manifest bytes are not compared; environment differences can cause a reported mismatch. Completion must be assessed from the actual command result. Existing component commands are documented in the [README](../README.md#run-without-installation), [anytime report](anytime-report.md#reproduction), and [design report](design-report.md#reproduction). Verification uses the standard library; full reproduction needs already-installed NumPy and SciPy. No download is part of reproduction.

That command's comparison scope remains the v0.1-v0.3 evidence. The cost theorem's exact checks are separate; use the [cost report](zero-cost-report.md#reproduction) to regenerate and inspect them.

Internal prespecification commits are `2ec734b` for v0.1, `2095a91` for v0.2, and `07fea94` for the optimized-proposal follow-up. Commit `341a1d3` adds the base-manifest pin. The follow-up protocol pins v0.2 commit `4cdcc112c9bace2763a00e03e1c3b481ba0bbe61` and its manifest SHA-256 `26fe14ebc98480561d911810357230e291370ce5d487527aab1b6dceec6210a2`. These records are internal prespecification, not external preregistration. The new proposals were evaluated on previously observed scenarios, not a fresh holdout.

## Questions for an independent reviewer

1. Does prior work already establish the finite-without-replacement remainder, the uniform joint-limit profile, or an equivalent order-statistic result under another parameterization?
2. Does the uniform-subset selection policy, including deterministic tie handling, match an identifiable use case? Which changes would require new target weights or a different guarantee?
3. Are the crossing formula, increment bound, dominated-convergence argument, and endpoint conventions sufficient for statements A-D, including the regime `N=m`?
4. Does the implementation faithfully preserve support, fixed-label assumptions, predictable sampling, and numerical conservatism through exhaustion and threshold certification?
5. Are the optimized proposals fair comparators under the shared anytime engine? Do the paired analysis, censoring, reused paths, and negative results support the stated cost comparisons without implying stopping-time optimality?
6. What concrete deployment or evaluation decision would this conditional audit improve, and what additional evidence about label reliability, candidate generation, or prompt sampling would that decision require?
7. Is the finite rank-block cost comparison a consequence already established elsewhere? Does the all-zero comparator, grid restriction, hypergeometric interpolation, and threshold counterexample support the stated approximation theorem without implying nonzero-table or partial-certificate efficiency?

## Questions for the human project owner

- Can I derive the winner-rank law and explain exactly what is random in each guarantee?
- Can I reconstruct the finite remainder proof and identify which parts are prior art?
- Can I explain why minimizing the largest importance weight, variance, and fixed-width cost gives different proposals, without claiming optimal stopping cost?
- Can I independently reproduce a saved result, trace it to its protocol and hashes, and explain a scenario in which the envelope loses?
- Can I state what this project establishes, what it leaves unresolved, and which contributions I personally made or independently verified?

These are prompts for demonstrating understanding, not a record that it has been demonstrated.
