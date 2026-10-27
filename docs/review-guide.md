# Scientific review guide

Start with the consolidated [finite-cost manuscript](../paper/finite-cost/manuscript.pdf), with [editable main text](../paper/finite-cost/main.md), [complete proof appendices](../paper/finite-cost/appendices.md), and a [source and dependency map](../paper/finite-cost/source-map.md). The v0.14.1 consolidation uses the v0.14 scientific base at commit `765ac51`; it adds no experiment. The central result is the all-grid minimax characterization, followed by its cached upper construction and matching dyadic subcensus rate. The original-instance checkpoint improvement and coverage between budgets are secondary results with separate proofs.

For every finite prompt count `P`, pool size `m`, and nonempty declared grid `K`, the main theorem states

$$
F/2^{38}\le C^*(\epsilon)\le2^{16}F,
\qquad
F=\min\left\{Pk_\epsilon,\sum_{r=1}^{m}\min\{P,He_r\}\right\}.
$$

Here `H=tau*log(1/delta)/epsilon^2`, `e_r=max_{n in K} w_n(r)`, and `k_epsilon` is the smallest rank prefix leaving at most `epsilon` winner mass for `min K`. The parameter range is `0<tau<=1/8`, `0<epsilon<=tau/16`, and `0<delta<=1/4`. There is no density, replication, or minimum-budget restriction. The constants are loose, not optimal leading coefficients.

`C*(epsilon)` is the least worst-case expected number of distinct purchased labels on the entire class with every declared risk at most `tau-epsilon`, using one auditor. That auditor must control false whole-family certification on every fixed unsafe table and complete almost surely on every fixed safe table, including the threshold boundary. The supplied margin guides the design; it is not evidence that an unknown table is safe. Correct fixed labels and known ranks are assumed, computation is uncharged, and the certificate concerns only the originally declared budgets.

The cached likelihood construction gives `C* <= min(P*k_epsilon, B_c)` and, on factor-two-separated grids in the main parameter range, `C* <= 17F`. Repeated proposals use fresh auxiliary coins while reusing purchased labels. For `P=1`, `m=2^d`, all dyadic budgets, fixed admissible `tau,delta`, and `epsilon^2=tau*log(m)/m`, the matching rate is

$$
C^*(\epsilon)=\Theta\!\left(\frac{m\log\log m}{\log m}\right)=o(m).
$$

This guide maps those claims to inspectable evidence. The manuscript's Appendix A proves the all-grid lower bound, Appendix B proves the cached and grouped upper bounds, and Appendix C provides the finite-population and residual-concentration arguments they require. The dependency map identifies retained proof branches and deliberate omissions. In particular, the separate v0.14 checkpoint proof is not reproduced in these appendices.

**Research status.** The owner has not personally checked the results. Agent review, exact arithmetic, tests, and byte-for-byte reproduction do not establish independent human validation, scientific novelty, or field impact. No real-model or human-annotation study establishes practical savings; grader reliability, new-prompt generalization, and deployment benefit remain unvalidated. [Provenance](provenance.md) discloses the substantial Codex assistance and distinguishes it from human review.

## Current claim-to-evidence map

| Claim or question | Evidence to inspect | Boundary |
| --- | --- | --- |
| The finite all-grid cost is bounded between `F/2^38` and `2^16 F`. | [Consolidated main text](../paper/finite-cost/main.md), [complete Appendices A-C](../paper/finite-cost/appendices.md), [dependency map](../paper/finite-cost/source-map.md), [original theorem](all-grid-minimax-theorem.md), [exact-check report](all-grid-minimax-report.md), [saved artifact](../results/theory/all_grid_minimax.json). | One globally valid, all-safe-complete auditor; worst expected distinct-label cost on a supplied-margin class of fixed real-loss tables. The 27,600 finite configurations support arithmetic and implementation, not universal quantifiers or novelty. |
| Classical likelihood tests with a shared cache attain the stated upper bound, including `17F` on separated grids. | [Construction and proof](cached-likelihood-audit.md), Appendix B, [rational callback report](cached-reference-report.md), [numerical proof](cached-reference-numerics.md), [implementation](../goodhart_audit/cached.py), [design arithmetic](../goodhart_audit/cached_math.py). | Fresh auxiliary coins are required on cache hits; all first acquisitions and fallback labels are charged. The bounded rational program has a `17F + eta` guarantee under its stated conditions and does not implement the grouped arbitrary-grid construction. It alone is not an all-real-table auditor. |
| The dyadic shrinking-margin sequence has matching cost `Theta(m*log(log(m))/log(m))`, below census order. | Main text Section 6 and Appendix A.12 in the [manuscript sources](../paper/finite-cost/manuscript.md), [all-grid theorem](all-grid-minimax-theorem.md), [report](all-grid-minimax-report.md). | Fixed admissible `tau,delta`, one pool, all dyadic budgets, the specified margin sequence, and sufficiently large `m`. This compares proved guarantees, not measured costs or every individual safe table. |
| The v0.14 checkpoint construction improves the original instance's upper bound to `383040/199`, about 1924.824 expected labels. | [Complete checkpoint proof](finite-checkpoint-theorem.md), [report and reproduction](finite-checkpoint-report.md), [callback](../goodhart_audit/checkpoint.py), [exact certificate](../results/theory/finite_checkpoint.json), [preserved lower certificate](monotone-placement-report.md). | Secondary, separate proof for 32 prompts, 64 ranks, seven dyadic budgets, `tau=1/10`, `epsilon=1/160`, `delta=1/20`. The mixed bound uses blind certification with probability `9/199`; the default evidence branch instead has error `1/200` and expected cost at most 2016. The lower bound remains 1103.263793259. Neither endpoint is an exact optimum or a measured model saving. |
| Certified endpoint risks can imply bounds between budgets, but the original seven-budget certificate does not automatically cover all budgets. | [Coverage proof and attribution](grid-coverage.md), [counterexamples and report](grid-coverage-report.md), [rational helper](../goodhart_audit/coverage.py), [saved artifact](../results/theory/grid_coverage.json). | Endpoint premises must actually be certified; a design margin is insufficient. Ten endpoints are minimal for the stated sufficient interval rule at `m=64`, not for all inference methods. Coverage does not change the original decision, improve its label-cost bounds, or by itself supply boundary-safe completion. |

For the original finite instance, `F=2048`, so the loose all-grid theorem does not improve the separate numerical certificate. The v0.14 mixed upper bound improves the earlier 1934.2 benchmark by about 9.376 labels, or 0.485%. Its exact error accounting is `9/199 + (190/199)/200 = 1/20`, with expected cost at most `(190/199)*2016`. Review that permitted certification lottery as part of the objective, not as evidence that an audit usually needs 1925 labels.

For attribution, start with the [all-grid primary-source comparison](all-grid-minimax-priority.md) and the manuscript references. Clipped inclusion sampling, heavy-item inspection, residual sampling, tail truncation, likelihood testing, and label reuse are established tools. The proposed contribution is their finite minimax characterization for this rank family and all-pass decision. The older weighted-query and inspection comparisons remain partly unresolved; the available source review is not a proof of novelty.

## Historical evidence and claim map

The following material preserves earlier claims and their original scopes. It is not the current finite-cost theorem or a cumulative count of independent studies. Historical reports and manuscripts retain their frozen release evidence, including upper benchmarks later improved by v0.14.

The v0.8 [nonzero minimax theorem](nonzero-minimax-theorem.md) is a restricted precursor to the current all-grid result. Review its one-auditor worst-case objective, monotone-ratio/sub-CDF upper argument, linear stage schedule, and common fixed-count permutation lower bound. Its strong replication condition belongs only to that lower bound and cannot be replaced by small atoms. Its [report](nonzero-minimax-report.md) distinguishes exact arithmetic from probability proofs and records a census fallback on the original geometry. Its [priority comparison](nonzero-minimax-priority.md) identifies close prior rare-event bandwise KL and concentration results.

For the historical zero-table cost result, the [self-contained sharp-cost manuscript](../paper/sharp-cost/README.md) combines the arbitrary-grid theorem, complete finite lower-bound proof, structural counterexample, saved arithmetic evidence, and practical power limitation. Its evidence remains frozen at v0.7; that manuscript is a consolidation, not an additional experiment.

The companion [seven-page research note](../paper/paper.pdf) has [editable Markdown source](../paper/paper.md) and [build instructions](../paper/README.md). It consolidates the existing v0.3 evidence; the notes and saved results below provide supporting detail.

The v0.4 follow-up is the [zero-table cost theorem](zero-cost-theorem.md), with [exact finite checks and cost certificates](zero-cost-report.md). It analyzes an established independent-inclusion audit and a whole-family decision, rather than changing the earlier confidence-sequence engine.

Version 0.4.1 makes that decision available through a [complete annotation workflow](zero-workflow.md). Review the [rational probability construction and proof](zero-workflow-numerics.md), [math implementation](../goodhart_audit/zero_math.py), [plan/report implementation](../goodhart_audit/zero.py), and their [math](../tests/test_zero_math.py) and [workflow](../tests/test_zero_workflow.py) tests. The code checks a conservative probability sandwich, uses exact integer rejection sampling, and verifies an externally recorded plan commitment. Its saved tape establishes replay consistency; independent randomness, correct labels, and commitment timing remain assumptions. The examples are hand-authored software fixtures, not another study.

### Earlier claims and their evidence

| Claim or question | Evidence to inspect | Boundary |
| --- | --- | --- |
| Sharp zero-table cost extends to every nonempty declared BoN grid, while general decreasing rows can have an unbounded NEGEXP cost ratio. | [Structural proof](sharp-grid-structure.md), [scope and analytical power example](sharp-grid-report.md), [protocol](../experiments/sharp_grid_protocol.json), [checker](../experiments/check_sharp_grid.py), [saved artifact](../results/theory/sharp_grid.json). | Same shrinking-threshold and small-atom regime, with arbitrary gaps and no baseline requirement in the mathematical theorem. Leading cost uses Z_K. The structural conditions are sufficient, not necessary or an if-and-only-if characterization. CLI domain is unchanged. |
| Classical NEGEXP attains the optimal leading zero-table cost for the full budget prefix in the stated joint limit. | [Sharp-cost proof](sharp-cost-theorem.md), [finite-check report](sharp-cost-report.md), [protocol](../experiments/sharp_cost_protocol.json), [checker](../experiments/check_sharp_cost.py), [saved certificates](../results/theory/sharp_cost.json). | Requires tau tending to zero, log(1/delta)*N/(P*m*tau) tending to zero, and delta at most 1/4. Uniform in the other parameters; expected all-zero cost only. Symbolic finite certificates are conservative bounds, not measured model costs or an implementation of unbounded populations. |
| The zero-table cost comparison extends to arbitrary declared grids containing budget 1, without padding the decision with extra targets. | [Complete extension proof](sparse-grid-theorem.md), [exact-check report](sparse-grid-report.md), [protocol](../experiments/sparse_grid_protocol.json), [checker](../experiments/check_sparse_grid.py), [saved artifact](../results/theory/sparse_grid.json). | Factor 320 under the original threshold/confidence restrictions; factor 160 remains for the old grids. Counterexample varies confidence at fixed threshold. Finite S/A checks are not exact NEGEXP/OPT ratios or a universal proof. |
| A classical audit design has a finite rank-family cost approximation guarantee against all valid adaptive audits. | [Full proof](zero-cost-theorem.md), [fixed check protocol](../experiments/zero_cost_protocol.json), [exact checker](../experiments/check_zero_cost.py), [cost certificates](zero-cost-report.md). | Expected cost only on the all-zero fixed-label table; exact unit-cost labels without free loss information; almost-sure zero-table certification; a predeclared whole-family decision; specified grid, threshold, and confidence restrictions. The generic design and optimization are prior art. The universal factor is loose; geometry-specific brackets are bounds, not exact optima. |
| The target is the loss of the winner of a uniform subset of distinct candidates, under a frozen total order. | [Target and rank law](theory.md#1-target-ordering-and-assumptions), [core](../goodhart_audit/core.py), [core tests](../tests/test_core.py). | Conditions on the recorded pools and correct fixed labels; no new-prompt guarantee. The selection rule and the audit sampling rule are separate objects. |
| The finite envelope has an adjacent-total-variation decomposition, a uniform remainder relative to the continuous envelope, and a joint-limit correction profile. | [Original proof](theory.md#3-exact-finite-pool-envelope-theorem), [sharp proof, statements A-D](sharp-envelope.md), [exact tests](../tests/test_sharp_envelope.py), [standalone checker](../experiments/check_sharp_envelope.py), [saved evidence](../results/theory/sharp_envelope.json). | The checker covers 19,900 exact rational increment cases through pool size 200. Finite checks support the algebra; the proof establishes universal statements. Novelty is provisional. |
| The continuous normalizer, generic envelope construction, and sequential inference are established foundations. | [Corrected related work](related-work.md), [anytime correspondence](anytime-related-work.md), [anytime proof](anytime-theory.md). | Fitas v2 already gives the continuous integer-budget normalizer and logarithmic coefficient; Shtarkov's construction supplies the generic minimax-ratio identity; Shekhar et al. supply weighted-without-replacement betting. The initial abstract-only Fitas comparison was incomplete. |
| Variance and fixed-width objectives produce numerically optimized proposals. | [Objective definitions](design-report.md#what-is-optimized), [optimizer](../goodhart_audit/design.py), [independent checks](../tests/test_design.py), [proposals and dual weights](../results/design/designs.json). | The objectives are prior art. Feasible primal and dual values bracket their optima numerically. These are floating-point checks, not formal arithmetic certificates. |
| Those objectives need not minimize actual certification cost. | [All follow-up summaries](../results/design/summary.csv), [path/checkpoint records](../results/design/replicates.csv), [outcome interpretation](design-report.md#certification-outcomes). | Every proposal uses the same anytime engine. Costs use the directional upper test, reproduced with `--rule upper-test`; the CLI default additionally checks for an empty two-sided interval. Censored runs are not successful certifications. |
| Reported counts and reuse are auditable. | [v0.1 manifest](../results/manifest.json), [v0.2 manifest](../results/anytime/manifest.json), [follow-up protocol](../experiments/design_protocol.json), [follow-up manifest](../results/design/manifest.json), [verification code](../experiments/verify_design_results.py). | v0.1: 32,000 method/horizon evaluations from 1,600 scenario-replicate streams. The anytime follow-up: 4,000 reused plus 1,600 new method paths, 22,400 checkpoint rows, and 224 aggregates from the same 800 streams. Methods and checkpoints are paired, not independent experiments. |

Primary attribution anchors for the earlier envelope analysis are [Fitas (2026, v2), Section 2.4 and Supplement S2](https://arxiv.org/html/2608.21496v2), [Shekhar et al. (2023), Definition 2 and Theorem 1](https://proceedings.mlr.press/v216/shekhar23a.html), and [Sarkar and Baichoo (2026), Section 7.6](https://arxiv.org/html/2609.40190v1). Its proposed mathematical distinction is the finite-without-replacement remainder and joint-limit profile, rather than the continuous coefficient or generic audit methods.

The cost follow-up adds the finite rank-block comparison as another contribution candidate. Its [attribution section](zero-cost-theorem.md#8-attribution-and-claim-boundary) covers NEGEXP and multi-target reuse, audit-subset optimization, earlier approximation results, multiscale lower bounds, and finite-table zero-path coupling. Novelty remains subject to specialist review.

The sharp-cost follow-up adds a uniform matching lower bound in a restricted asymptotic regime. Inspect the [hypergeometric lemma, bin construction, and finite inequality](sharp-cost-theorem.md#3-a-finite-hypergeometric-lower-bound), particularly strict unsafe-support rounding, discarded bin mass, and the two atom-size terms. Its [attribution section](sharp-cost-theorem.md#8-rational-designs-numerical-evidence-and-attribution) retains unresolved inspection-literature priority leads. The [nonzero-table limitations](nonzero-cost-limits.md) are attributed observations, not additional novelty claims.

The structural follow-up removes the full-prefix hypothesis using a bounded representative collection and an exact small-height-tail identity. Review the two different discarded-bin charges and the counterexample's cheaper conjunction audit. The [inspection-priority review](inspection-priority-review.md) identifies a closer 1989 stratified without-replacement result whose original proof remains unavailable. Older optimal-allocation statements must be compared at the level of their allowed strategy class, not dismissed because a review first presents a with-replacement example.

## Reproduction and provenance

The current finite-cost evidence has separate, source-pinned checkers. Use fresh output paths and inspect each command's actual result:

```console
python -B -S -m experiments.check_all_grid_minimax --out artifacts/local/all-grid-minimax-reproduction.json
python -B -S -m experiments.run_cached_reference --out artifacts/local/cached-reference-reproduction.json
python -B -S -m experiments.check_finite_checkpoint --out artifacts/local/finite-checkpoint-reproduction.json
python -B -S -m experiments.check_grid_coverage --out artifacts/local/grid-coverage-reproduction.json
```

The [all-grid report](all-grid-minimax-report.md#fixed-verification-matrix-and-reproduction), [cached-reference report](cached-reference-report.md#checks-and-demonstration-evidence), [checkpoint report](finite-checkpoint-report.md#exact-evidence-and-reproduction), and [coverage report](grid-coverage-report.md#fixed-calculation-and-verification) record their protocols, source freezes, artifact hashes, test commands, and evidence boundaries. The [monotone-placement report](monotone-placement-report.md#reproduction-and-interpretation) separately reproduces the preserved original-instance lower certificate. These standard-library commands check different claims; their saved counts are not independent experiments or a proof of the universal theorems. A reproduction recorded in a release report is not a claim that it has been rerun during this manuscript consolidation.

The consolidated paper reports no new experiment. Its [source map](../paper/finite-cost/source-map.md) records proof correspondence and frozen source hashes; the [builder](../paper/finite-cost/build_pdf.py) produces the review artifact. Rebuilding or visually checking a PDF does not validate its mathematics. The central theorem's proof dependencies are inside Appendices A-C; the checkpoint and coverage results retain their own external-to-the-manuscript proof documents.

For the historical v0.1-v0.3 evidence, the unified entry point is:

```console
python -m experiments.reproduce --verify-only
python -m experiments.reproduce --out artifacts/local/review-reproduction
```

The first command checks saved source/artifact integrity, including the release-pinned theorem JSON. It does not recompute tables or prove mathematical claims. The second runs the tests and all numerical studies in a new directory, comparing ten artifacts byte for byte and saving a diagnostic report. Figures are not rerun, and manifest bytes are not compared; environment differences can cause a reported mismatch. Completion must be assessed from the actual command result. Existing component commands are documented in the [README](../README.md#run-without-installation), [anytime report](anytime-report.md#reproduction), and [design report](design-report.md#reproduction). Verification uses the standard library; full reproduction needs already-installed NumPy and SciPy. No download is part of reproduction.

That command's numerical comparison scope remains the v0.1-v0.3 evidence; it does not reproduce the later finite-cost matrices above. The zero-table cost theorem's exact checks are also separate; use the [cost report](zero-cost-report.md#reproduction) to regenerate and inspect them.

The arbitrary-grid extension has its own [reproduction command and source-pinned artifact](sparse-grid-report.md#reproduction). Its protocol commit `2d21f4b` followed exploratory proof checks and preceded the saved broader run. It is neither an external preregistration nor a new empirical holdout. Its proof must be checked against the original target family; simply adding missing powers of four changes the comparator.

The sharp-cost [reproduction command](sharp-cost-report.md#reproduction-and-evidence-scope) is also separate. Protocol commit `2593893` followed exploratory proof checks and preceded the saved run. The five pinned files include both the new proof and the earlier normalizer proof. Exact fractions and outward rounding support the numerical certificates; the finite run cannot establish the unbounded theorem or its novelty.

Internal prespecification commits are `2ec734b` for v0.1, `2095a91` for v0.2, and `07fea94` for the optimized-proposal follow-up. Commit `341a1d3` adds the base-manifest pin. The follow-up protocol pins v0.2 commit `4cdcc112c9bace2763a00e03e1c3b481ba0bbe61` and its manifest SHA-256 `26fe14ebc98480561d911810357230e291370ce5d487527aab1b6dceec6210a2`. These records are internal prespecification, not external preregistration. The new proposals were evaluated on previously observed scenarios, not a fresh holdout.

## Questions for an independent reviewer

### Current finite-cost theorem and secondary results

1. Do the main statement and proofs use the same one-auditor minimax objective, fixed-label oracle, whole-family decision, unsafe-table validity, and all-safe completion requirements? Is the supplied margin used only for design and efficiency?
2. Does the common conditioned safe prior justify adding broad-band costs, with finite-horizon transcript information and exceptional mass accounted for under the stated laws?
3. Do centered tail blocks, the finite-population testing lemma, the small-prompt hidden-subset branch, and the high-budget and uniform-tail endpoints exhaust every finite grid and support the constant `2^38`?
4. Do fresh coins on cached proposals, bounded stopping, exact-support completion, and distinct-item clipping prove the cached bound? Does the grouped construction, including every prefix and fallback charge, justify the all-grid coefficient? Is the rational callback's narrower domain kept distinct from the real-loss theorem?
5. Does Appendix A.12 establish both sides of the dyadic subcensus rate for the stated margin sequence? Does the dependency map leave any required project-specific lemma outside the manuscript?
6. Does earlier weighted-query, inspection, or best-of-N work already imply this finite characterization under equivalent quantifiers? Which unresolved primary-source comparisons must be completed before a novelty claim is justified?
7. For the separate v0.14 instance, do fractional-loss convex bounds, strict atom cutoffs, unconditional checkpoint statistics, charged completion, and the disclosed blind mixture establish the reported upper certificate without implying optimality or observed savings?
8. Does the coverage transfer require genuinely certified endpoint bounds, and are its counterexamples, sufficient-rule endpoint minimum, and boundary-completion limitation stated without enlarging the original certificate?

### Historical envelope, design, and zero-table claims

1. Does prior work already establish the finite-without-replacement remainder, the uniform joint-limit profile, or an equivalent order-statistic result under another parameterization?
2. Does the uniform-subset selection policy, including deterministic tie handling, match an identifiable use case? Which changes would require new target weights or a different guarantee?
3. Are the crossing formula, increment bound, dominated-convergence argument, and endpoint conventions sufficient for statements A-D, including the regime `N=m`?
4. Does the implementation faithfully preserve support, fixed-label assumptions, predictable sampling, and numerical conservatism through exhaustion and threshold certification?
5. Are the optimized proposals fair comparators under the shared anytime engine? Do the paired analysis, censoring, reused paths, and negative results support the stated cost comparisons without implying stopping-time optimality?
6. What concrete deployment or evaluation decision would this conditional audit improve, and what additional evidence about label reliability, candidate generation, or prompt sampling would that decision require?
7. Is the finite rank-block cost comparison a consequence already established elsewhere? Does the all-zero comparator, grid restriction, hypergeometric interpolation, and threshold counterexample support the stated approximation theorem without implying nonzero-table or partial-certificate efficiency?
8. Does the sharp lower bound follow uniformly when N and confidence vary? Is the bin-count-to-envelope-mass control sufficient, and does older inspection literature already imply this result for the same comparator? What practical regime, if any, makes the asymptotic cost characterization useful?
9. Do the representative count, tail identity, and two discarded-bin charges remove all dependence on gaps in K? Does the shared-head counterexample correctly separate this sufficient mechanism from monotonicity, including fractional-loss validity and a fixed confidence level?

## Questions for the human project owner

- Can I state the all-grid cost functional, parameter range, and quantifiers, and explain why the theorem has both a clipped-envelope term and a deterministic prefix term?
- Can I reconstruct the main lower-bound branches and cached upper argument, distinguish the ideal real-loss construction from its rational reference, and explain the role of the separate checkpoint lottery?
- Can I derive the winner-rank law and explain exactly what is random in each guarantee?
- Can I reconstruct the finite remainder proof and identify which parts are prior art?
- Can I explain why minimizing the largest importance weight, variance, and fixed-width cost gives different proposals, without claiming optimal stopping cost?
- Can I independently reproduce a saved result, trace it to its protocol and hashes, and explain a scenario in which the envelope loses?
- Can I state what this project establishes, what it leaves unresolved, and which contributions I personally made or independently verified?

These are prompts for demonstrating understanding, not a record that it has been demonstrated.
