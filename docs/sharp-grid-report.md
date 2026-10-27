# Why sharp audit cost survives sparse search budgets

The [structural proof](sharp-grid-structure.md) extends the sharp zero-table cost limit to every nonempty predeclared best-of-N budget grid. Budget 1 and intermediate budgets need not be present. Under the same conditions as v0.6—`tau -> 0`, `rho=log(1/delta)*max(K)/(P*m*tau) -> 0`, and `0 < delta <= 1/4`—the leading cost is

`OPT_0 ~ C_NEG ~ log(1/delta)*Z_K/tau`.

The comparator includes every adaptive auditor that is valid against all fixed tables and almost surely certifies the zero table in finite time. Costs count distinct queries at that zero table. The target is one certificate for the originally declared family, without adding missing budgets. Correct fixed losses, unit label cost, equal prompt weights, and the absence of free cross-item label information remain assumptions.

The distinction between sparse and complete grids matters. One declared budget has `Z_K=1`. Two budgets have `Z_K<=2`, however far apart they are. The full prefix has `Z_K=(log N)/e+O(1)`. The logarithmic coefficient must therefore not be substituted for the actual sparse-grid normalizer.

## The structural step

The full-prefix proof bounded the number of envelope-value bins using the ratio between the largest and smallest weights. That ratio can be enormous for a sparse grid. The new proof instead controls where appreciable envelope mass lives.

A four-separated set of declared representatives has at most `4*Z_K` members. Each representative dominates its nearby budgets within a factor of four. The exact rank-law tail identity says that all ranks below an epsilon-fraction of a row's peak carry at most epsilon total row mass. Together, these facts cover almost all envelope mass by a bounded collection of value windows, even across arbitrarily large gaps in the grid. The earlier finite block lower bound then yields the matching adaptive cost.

This is a sufficient structural mechanism, not a characterization of all families where envelope auditing is optimal. It connects an established worst-weight sampling criterion to optimal leading label cost for this rank family. The connection need not hold generally: the proof gives a counterexample with normalized decreasing rows, a uniform baseline, shrinking thresholds, and vanishing maximum-item density, yet an unbounded envelope-audit cost ratio. The rows share a large head and place tiny masses on many different tail scales. A head audit plus a population audit is much cheaper. Thus monotonicity and small atoms alone do not justify the conclusion.

The result is consistent with the earlier fixed-threshold, varying-confidence obstruction for grids without budget 1. That example does not satisfy this theorem's joint limit. The released CLI and its finite-factor guarantee domain are unchanged; an asymptotic theorem does not justify lifting its resource caps or assigning an unsupported finite approximation factor.

## What decision this can inform

For a frozen archive of scored outputs, an evaluator can predeclare several candidate search budgets and ask whether every corresponding selected-output risk is below a threshold. The theorem describes the irreducible leading label cost of that decision at a clean archive. It does not choose a useful threshold, establish new-prompt safety, or optimize utility against compute cost.

The clean-table qualifier is consequential. In the existing synthetic [`prompt_cluster` definition](../experiments/run_study.py), two of 32 prompts fail at every rank under the [published anytime geometry](../experiments/anytime_protocol.json). Every declared budget has risk `1/16`, below the study threshold `0.1`. Nevertheless, ideal zero-only NEGEXP certifies only when it samples no failing item. With the frozen seven-budget envelope, that probability is

`0.05^[(5/8)*Z_K]`, with `Z_K=177416516255/61966315152`,

or approximately **0.47%**. The rational workflow samples at least as aggressively, so its certification probability is no larger. This is an analytical consequence of an already published synthetic table, not a new model study or simulation. It illustrates why a zero-table cost theorem cannot substitute for a useful power guarantee across safe nonzero tables.

## Evidence and priority

The [protocol](../experiments/sharp_grid_protocol.json), initially committed as `bcb0790`, follows exploratory proof work and small-grid checks. Amendment `3e26b8c` adds a nonvacuous tail-mass regime before the saved broader calculation. It specifies exact tail identities, exhaustive small nonempty grids, conservative symbolic cost certificates, and a symbolic monotone-family counterexample. It is not an external preregistration. Earlier source-pinned proofs and results are preserved.

The [saved artifact](../results/theory/sharp_grid.json) records 89,440 exact tail identities, 2,080 empty-tail endpoints, and 6,240 low-height-tail checks through pool size 64. It checks all 2,036 nonempty budget grids through pool size 10 at three scales: 6,108 configurations, including 2,036 with a nontrivial aggregate bad-mass bound. Across the configurations, 1,566 have positive bad-envelope mass. The checks include 34,538 bins and 2,802 bad-rank witness assignments.

There are 64 conservative cost certificates across eight declared grids, four k values, and two confidence levels. They use `tau=1/k^3` and `P=ceil(3*max(K)*k^4/m)`, with 1,170 retained-block unsafe-size checks. The largest upper bound on `C_NEG/OPT_0` among each k's sixteen prescribed settings is:

| k | Threshold tau | Maximum certified ratio bound |
| ---: | ---: | ---: |
| 8 | 1/512 | 1.168867 |
| 32 | 1/32,768 | 1.041655 |
| 128 | 1/2,097,152 | 1.010407 |
| 512 | 1/134,217,728 | 1.002602 |

These decimals round upward. The brackets bound the adaptive optimum and NEGEXP cost; neither cost is computed exactly. The largest population count is 26,388,279,066,624, represented symbolically without an item table.

Six further symbolic calculations evaluate the general monotone-family counterexample. At k=64 its conservative ratio **lower** bound exceeds 16.369, despite fixed delta=1/4 and shrinking item masses. This concerns the constructed non-BoN family, so it does not conflict with the preceding table. The counterexample's exponential dimension is retained as `H*(1+2^J)` and never expanded. Unit tests separately check the comparator implication on all 1,024 binary tables and four fractional tables of a ten-item analogue.

## Reproduction

```console
python -B -S -m experiments.check_sharp_grid --out artifacts/local/sharp-grid-reproduction.json
python -B -S -m unittest discover -s tests -p "test_sharp_grid.py" -v
```

Choose a new output path. The checker pins seven sources: its code, tests, protocol snapshot, new proof, the earlier sharp-cost and sparse-grid proofs, and the reused exact-arithmetic helper. Block lower bounds and counterexample ratio lower bounds round downward; total upper costs and their displayed ratios round upward. The protocol and source bytes are rechecked before output, and existing artifacts cannot be overwritten.

A separate run reproduced all 137,749 artifact bytes, SHA-256 `5e0dc8c8adf2316bfe09a7564b64bf4220808d7c84284ab574149611747b5da8`. All 192 project tests pass; the ten focused tests also pass with site-packages disabled. Earlier artifact and source-integrity checks pass. These are checks within the assisted development session, not independent human replication. Finite enumerations support the arithmetic; the written proof supplies the unbounded statements.

## Remaining priority question

The [inspection-literature review](inspection-priority-review.md) identifies a stronger unresolved comparison with older IAEA stratified auditing. NEGEXP, geometric grouping, and finite-population miss probabilities are established. The candidate contribution is the uniform adaptive-cost comparison and its structural scope. Neither the proof reviews nor exact checks establish priority, independent human ownership, or empirical usefulness.
