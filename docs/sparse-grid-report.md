# Auditing sparse budget grids without adding targets

The [new proof](sparse-grid-theorem.md) extends the zero-table cost approximation to any declared budget grid containing 1. For example, `{1,3,7,19,64}` is now covered even though it omits 4 and 16. The decision still concerns exactly the original targets. Adding intermediate targets would strengthen the required decision and change the adaptive optimum; it would not establish this result.

Under the same finite-pool, correct-label, unit-cost assumptions, threshold at most 1/8, and error probability at most 1/4, classical NEGEXP has expected zero-table cost at most **320 times** the unrestricted adaptive optimum. The original factor **160** remains available when all powers of four through the maximum are declared. These coarse upper guarantees do not determine actual overhead or imply that the old grids are twice as efficient.

## What changed in the argument

The proof chooses geometrically separated representatives from the declared grid. Each representative supplies a disjoint block on which every admissible auditor must spend labels. These blocks may leave gaps. The lower bound remains `OPT_0 >= A/40`, with `A` the sum of capped block sizes.

For the upper bound, low-budget groups cost at most four times the common scale `T=log(1/delta)/tau` per representative. All higher-budget groups together are charged once: they occupy a short top-rank region, and their remaining envelope is bounded by the first high-budget row. The large block from budget 1 closes the comparison, giving `S(T)<=8A`, where `S(T)=sum_i min(1,T*s_i)`. The implemented rational probabilities have cost at most this same deterministic upper bound.

Geometric grouping, disjoint-band lower bounds, NEGEXP, and generic subset auditing are established techniques. The candidate contribution is the finite rank-family extension and its boundary. [The attribution section](sparse-grid-theorem.md#8-attribution-evidence-and-limits) identifies the closest verified sources. Priority and practical usefulness remain unestablished.

## Why the baseline condition cannot simply be dropped

At fixed threshold 1/8, consider one pool of `10j` candidates and the single budget `9j`. Rank 1 has mass 0.9 and all other ranks together have mass 0.1. An optimal zero-table audit can query only rank 1 with probability `1-delta`, giving exact expected cost `1-delta` while remaining valid for every fixed fractional loss table.

For the explicit confidence sequence `delta_j=4^(-binom(10j,j))`, NEGEXP selects each of the `j+1` supported ranks with probability at least `65535/65536`. Its competitive ratio therefore grows without bound. Confidence varies in this construction; it is not a fixed-confidence separation. Some grids without 1 are well behaved, so the theorem gives a sufficient condition rather than a complete classification.

The checker represents this extremely small confidence symbolically. It never constructs its expanded denominator. No model calls, random labels, or sampled cost estimates enter these calculations.

## Reproduction

The [saved exact artifact](../results/theory/sparse_grid.json) records the following completed checks:

| Check | Recorded scope |
| --- | ---: |
| All grids containing 1 through pool size 12 | 4,095 families |
| Larger prescribed sparse geometries | 5 |
| Geometry and prompt-count combinations | 12,290 |
| Exact capped-envelope cost comparisons | 122,900 |
| Rank positions checked for block witness density | 43,542 |
| Missing-baseline constructions | 8 |
| All binary supports for constructions with j=1,...,4 | 60 |

The largest observed `S/A` was exactly `5/3` among the recorded finite cases. This is a diagnostic of the proof's intermediate bound, not a universal constant, the exact NEGEXP cost ratio, or a measured model result. The scales include values outside the theorem's threshold/confidence-derived range because the deterministic inequality holds for every positive T.

For the missing-baseline construction with j=320, the exact ratio lower bound is `21036735/65536`, greater than 320.995. It uses 3,200 candidates, budget 2,880, and the symbolic confidence above. This verifies a concrete member of the theoretical family, not a practical-confidence cost claim.

All 171 software tests pass. A second standard-library run reproduced the 31,985-byte artifact exactly, with SHA-256 `e9367cf51b192a80fe21548072c3dfb27646332d2bae50d8d6ad6ce8623cf46a`. All four new source pins match. Earlier evidence checks and v0.4 source pins also pass. Actual CLI checks certified a hand-authored sparse-grid fixture and replayed two v0.4.1 reports byte for byte; four earlier mathematical design records were unchanged.

The [saved-run protocol](../experiments/sparse_grid_protocol.json) was committed as `2d21f4b` after exploratory proof checks and before the recorded broader calculation. It is not an external preregistration or a holdout. The checker uses exact rational arithmetic and the standard library:

```console
python -B -S -m unittest discover -s tests -p "test_sparse_grid.py" -v
python -B -S -m experiments.check_sparse_grid --out artifacts/local/sparse-grid-reproduction.json
```

Use a new output path. The checker refuses overwrites and pins its source, tests, protocol snapshot, and proof note; it fails if those sources change during the calculation. Explicit correctness checks remain active under optimized Python. Finite checks support the implementation and algebra; the written argument supplies the unbounded theorem.

The earlier unified reproduction command retains its v0.1-v0.3 comparison scope. The v0.4 checker and source-pinned evidence also remain separate. The [zero-only workflow](zero-workflow.md) accepts the enlarged domain, records the appropriate factor, and retains the mathematical records and commitments of previously accepted plans. The examples are hand-authored software checks, not evidence about LLM behavior.
