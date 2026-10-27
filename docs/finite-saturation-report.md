# Finite saturation: a matching cost formula for high budgets

Research extension, 27 October 2026. The [complete proof](finite-saturation-theorem.md) gives matching upper and lower bounds, up to loose universal constants, for every declared best-of-n grid whose smallest budget is at least one quarter of the pool size. It covers every finite prompt count and confidence level in the stated range, including cases where the [v0.9 density condition](finite-density-report.md) fails. The [source comparison](finite-saturation-priority.md) distinguishes the candidate theorem from established threshold-sampling and query-lower-bound methods; scientific priority remains unestablished.

## The mathematical result

The objective is unchanged: one auditor must remain delta-valid on every unsafe fixed fractional-loss table and certify every safe table almost surely. Cost is the worst-case expected number of distinct labels over tables with every declared risk at most `tau-epsilon`, with epsilon supplied to the design. Let

$$
H=\frac{\tau\log(1/\delta)}{\epsilon^2},\qquad
e_r=\max_{n\in\mathcal K}w_n(r),\qquad
F=\min\left\{Pk_\epsilon,\sum_r\min(P,He_r)\right\}.
$$

Here `k_epsilon` is the shortest prefix leaving at most epsilon probability under the smallest declared budget. For positive `tau<=1/8`, `epsilon<=tau/16`, `delta<=1/4`, and **`min K>=m/4`**, the theorem gives

$$
\frac{F}{2^{21}}\le C^*(\epsilon)\le12288F.
$$

No replication or maximum-item-weight condition is required within this budget range. For a single full-pool budget, F becomes `min(P,H)`. For rapidly decreasing rank weights, the prefix term accounts for a small unobserved tail. These are order bounds; their constants do not give a useful precise estimate of optimal finite cost.

The clipped sum is classical threshold-sampling expected size. The new proof work under assessment is the matching fixed-table decision bound. An exact-count testing lemma controls expected information even when few positives remain unseen. A common fractional-amplitude rank prior makes **every** target risk exactly `tau-epsilon`. A separate hidden-subset argument handles small prompt counts. The geometric comparison uses an inequality for each log-concave rank row before taking its maximum; it does not assume the envelope itself is log-concave.

## Why the deterministic cap matters

The clipped sum alone can be arbitrarily too large. For `P=1`, `tau=1/8`, `epsilon=1/128`, `m=2^(3j)`, `K={m/2}`, and `delta=exp(-4^j)`, the first seven ranks leave probability at most `1/128`. Inspecting them certifies every margin-class table with zero error; a census fallback ensures completeness on all other safe tables. Yet at least the first j terms of the clipped sum equal one. Thus the cost is at most seven while the uncapped expression grows without bound. This is an analytic construction, not a model experiment.

## Exact-check evidence

The [protocol](../experiments/finite_saturation_protocol.json) was fixed in commit `4eedbd2` after exploratory derivations and before the saved full calculation. Reviewed proof and checker sources were committed as `52e1b4b`; their Git blob bytes matched the worktree before the run. This is a committed protocol, not an external preregistration. The [saved result](../results/theory/finite_saturation.json) pins six source files, including the protocol, theorem, checker, tests, and unchanged earlier proof/helper.

The bounded checker uses exact fractions and outward logarithm bounds. Its saved run contains:

| Check | Observed scope |
|---|---|
| Reciprocal remaining-positive expectation | 1,711 cases through population 32, including 151 zero-positive cases |
| Conditional Bernoulli KL majorant | 6,875 feasible histories, including 615 with no remaining null positives |
| Finite-slice cap arithmetic | 56 cases: 18 finite-cap and 38 zero-query arguments; all registered floors resolved |
| High-budget grids | All 644 nonempty allowed grids through pool size 10; 20,608 parameter configurations |
| Outward geometry comparison | `F_upper<=40*A16_lower` in every configuration; clipped cost strictly below prefix cost in 6,356 |
| Rounded rank priors | 56,416 fixed-count and 35,392 hidden-subset checks, plus six displayed boundary witnesses |
| Confidence-cap construction | Four symbolic exponents, 7, 12, 20, and 32 |

Large prompt populations and very small confidence levels are represented symbolically. No million-row table or numerical value of `exp(-4^j)` is allocated. The evidence checks arithmetic ingredients over a finite matrix; the general theorem depends on the proof, including concentration and adaptive-transcript arguments.

All 241 project tests pass. The 14 focused tests also pass with site packages disabled, both normally and under optimized Python. They include independent subset enumeration, high-precision logarithm comparisons, source-drift detection, and an intentionally widened cap interval. Review exposed conservative interval handling that was corrected after a failing regression.

Reproduce with the installed Python standard library, choosing a fresh output path:

```console
python -B -S -m experiments.check_finite_saturation --out artifacts/local/finite-saturation-reproduction.json
python -B -S -m unittest tests.test_finite_saturation -q
```

The saved artifact is 17,746 bytes with SHA-256 `7a406e94bcbaf1105df94934163ec4491ce1a200ccdbf9da273993fcc926af53`. A separate run reproduced every byte; output overwrite and source changes during a run are rejected. These are agent-assisted implementation checks, not independent human replication or model-label evidence.

## A restricted-grid example, not the original whole-family decision

For 32 prompts and 64 candidates per prompt, declare **only budgets 16, 32, and 64**, with `tau=1/10`, `epsilon=1/160`, and `delta=1/20`. The shortest deterministic prefix has 16 ranks, so it uses 512 labels on every table in the margin class. The clipped expression is approximately 525.29, making F=512. The exact checker encloses the logarithm rather than treating this decimal as evidence.

This example changes the declared family from the earlier seven dyadic budgets. It provides no certificate for omitted budgets 1, 2, 4, or 8. The 512-label upper bound already follows from the v0.9 prefix argument; the new result is the matching order characterization for the stated high-budget family. The displayed theorem's lower bound here is only `1/4096` expected labels, so its constants are too loose to claim tight practical optimality. No audit engine or model-label study was run.

Grids with `min K<m/4` remain outside this matching theorem. The new rankwise lower proposition applies to any grid, but need not match an upper bound there. Unknown-margin adaptation, incorrect-label robustness, independent human proof review, and real-model usefulness remain open. The [provenance record](provenance.md) discloses substantial Codex assistance. Publication and arithmetic reproducibility do not establish field impact or fellowship competitiveness.
