# Exact cost certificates for finite-pool zero-loss audits

The [cost theorem](zero-cost-theorem.md) bounds the expected distinct-label cost of the classical multi-target NEGEXP audit relative to every valid adaptive auditor in a specified class. Its universal factor 160 is loose. Exact rational calculations give much tighter bounds for particular score geometries, without collecting labels, fitting a model, or running a simulation.

For the project's geometry of 32 pools of 64 candidates and budgets 1, 2, 4, 8, 16, 32, 64, at threshold 0.1 and error probability 0.05, the certificates imply

$$
52.605\ \le\ \operatorname{OPT}_0\ \le\ C_{\mathrm{NEG}}\ \le\ 73.530,
\qquad C_{\mathrm{NEG}}/\operatorname{OPT}_0\le1.398.
$$

These displayed bounds are rounded conservatively from exact fractions. Every item has loss zero when cost is evaluated, but the audit must remain valid for every fixed loss table in `[0,1]`. This bounds the possible overhead by 39.8% for that geometry; it does not report a 39.8% saving or determine the exact optimum.

## What the guarantee covers

The auditor certifies that every declared target risk is at most a fixed threshold, or abstains. It has exact fixed labels, equal pool weights, unit query costs, no free label information, and almost-sure certification on the all-zero table. The budget family must contain every power of four through its maximum; the full prefix and the displayed dyadic grid satisfy this requirement. The theorem requires threshold at most 1/8 and error probability at most 1/4.

NEGEXP independently selects each item with probability `1-exp(-log(1/delta)*s_i/tau)`, where `s_i` is its largest target mass. It certifies only when all inspected labels are zero. This design, its multi-target reuse, and the generic subset-audit optimization are established prior work. The proposed contribution is the finite rank-family cost comparison. The [attribution section](zero-cost-theorem.md#8-attribution-and-claim-boundary) identifies the relevant prior methods and lower-bound arguments.

The comparator is unrestricted in computation and adaptivity. Its cost objective is restricted to the all-zero table. The theorem does not give a good cost guarantee after discovering positive losses, certify a chosen subset before the whole family passes, or establish competitiveness of the existing six-bet confidence-sequence engine. The earlier synthetic stopping-time results use that other engine and decision, so their medians are not direct comparators for these bounds.

## Fixed analytical illustrations

These nine cases were specified in [the internal protocol](../experiments/zero_cost_protocol.json), committed as `9ba2417` before the saved calculations. This is not an external preregistration or an empirical holdout. Cases vary pool size, threshold, confidence, and budget family. They are analytical illustrations, not a population sample of applications.

| Case | Items | Threshold | Error probability | Lower bound on optimum | Upper bound on NEGEXP cost | Ratio upper bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| One pool, 8 candidates, full prefix | 8 | 0.1 | 0.05 | 7.600 | 8.000 | 1.053 |
| One pool, 64 candidates, full prefix | 64 | 0.1 | 0.05 | 24.964 | 32.029 | 1.283 |
| Four pools, 64 candidates, dyadic grid | 256 | 0.1 | 0.05 | 36.208 | 48.952 | 1.352 |
| Published grid geometry | 2,048 | 0.1 | 0.05 | 52.605 | 73.530 | 1.398 |
| Smaller threshold, same geometry | 2,048 | 0.01 | 0.05 | 376.882 | 463.733 | 1.231 |
| Threshold endpoint, same geometry | 2,048 | 0.125 | 0.05 | 41.945 | 60.405 | 1.441 |
| 16 pools, 256 candidates, search through 64 | 4,096 | 0.1 | 0.05 | 45.368 | 69.667 | 1.536 |
| 16 pools, 256 candidates, search through 256 | 4,096 | 0.1 | 0.05 | 54.601 | 77.982 | 1.429 |
| Stronger confidence, published geometry | 2,048 | 0.1 | 0.001 | 107.364 | 152.910 | 1.425 |

The two 256-candidate cases use powers-of-four grids. Lower bounds are rounded down; upper and ratio bounds are rounded up, separately from their exact fractions. Ratios use the exact fractions, rather than the rounded display endpoints. Costs are expectations in units of distinct queried items. There is no Monte Carlo uncertainty because these entries are rational bounds, not estimated means.

The eight-item case reaches the finite-census regime: every single nonzero binary loss violates at least one target. Its lower bound 7.6 is attained by inspecting all eight items with probability 0.95 and certifying without inspection otherwise. This allowed randomization illustrates why an expected optimal cost may be fractional; it is not a claim that any single run uses 7.6 labels.

## How the certificates are obtained

The proof partitions ranks into blocks using the budgets 1, 4, 16, and so on. Each block has a witness target with enough mass throughout the block. For an instance-specific bound, the checker uses the actual minimum target mass in that block. Every subset of a calculated size is then an unsafe alternative. Averaging its necessary miss constraints gives a hypergeometric function of the number queried. Convexity and exact linear interpolation bound the expected number of queries in each block from below.

For the upper bound, a positive Taylor sum certifies an integer upper bound on `log(1/delta)`. An odd degree-five Taylor polynomial, clipped at one, bounds each inclusion probability from above. All rank masses, binomial coefficients, sums, interpolation values, and resulting cost brackets use exact rational arithmetic. [Equations (38)-(41)](zero-cost-theorem.md#9-sharper-computable-cost-certificates) give the full argument. Neither bound generally equals its respective optimum or actual design cost.

The saved artifact also checks a negative case. When the threshold approaches one in a single pool with the full budget family, only failure sets containing the best rank are unsafe. The optimum is `1-delta`, while NEGEXP's competitive ratio is at least the full rank-envelope normalizer, which diverges with pool size. The small-threshold restriction cannot simply be removed.

## Reproduction

Use Python 3.10+ and the standard library from the repository root. Choose a fresh output path:

```console
python -B -S -m experiments.check_zero_cost --out artifacts/local/zero-cost-reproduction.json
```

The checker rejects an existing output and detects changes to its pinned sources during a run. The [saved artifact](../results/theory/zero_cost.json) contains its protocol, source hashes, exact fractions, rounded display summaries, counts, and runtime metadata. Its source pins include the proof note and tests. Numerical environment-dependent sampling is absent.

The configured finite sweep checks 24,768 family configurations through pool size 128 and 2,121,792 rank positions, checking both block inequalities at each position. It also checks 5,592,320 hypergeometric convexity identities through block size 256, 24,558 algebraic prerequisites for the logarithm bound, 249 rounding conditions, and 3,072 exact inverse values. These finite checks do not prove the universal theorem; the written analytic steps remain essential.

All 131 software tests pass, including 16 tests for this checker. Review added regressions for optimized Python disabling assertions, altered theorem metadata, and protocol changes between parsing and hashing; all three safeguards now fail explicitly. Run the suite separately with `python -m unittest discover -s tests -v`. The older `experiments.reproduce` command retains its v0.1-v0.3 ten-artifact comparison and does not regenerate this follow-up. Its saved-evidence checks still pass; no earlier measured source or output was altered.

This proof, checker, and review were developed with substantial Codex assistance. Internal agent review and repeated execution are not independent human review or replication. Scientific priority and practical value on real model outputs remain unestablished.
