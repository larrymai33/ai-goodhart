# Nonzero finite-table minimax result: scope and arithmetic checks

Research extension, 26 October 2026. The [complete proof](nonzero-minimax-theorem.md) studies one auditor's worst-case expected label cost over a declared class of safe fixed tables. It permits positive observations and avoids the instance-specific reference advantage of a pointwise optimum. The [prior-art comparison](nonzero-minimax-priority.md) identifies substantial overlap in the ingredients; scientific priority remains unestablished.

## The claim and its limits

Let every declared risk be at most `tau-epsilon`, where epsilon is a supplied design parameter, and let `L=log(1/delta)`. For any nonempty finite best-of-n grid, use its actual envelope normalizer Z. Among auditors that remain valid on every unsafe fixed fractional-loss table and certify every safe table almost surely, the minimax expected number of distinct labels satisfies

$$
\frac{Z\tau L}{12000\epsilon^2}
\le C^*(\epsilon)
\le\min\left\{Pm,\frac{49152Z\tau L}{\epsilon^2}\right\},
$$

provided `tau<=1/8`, `epsilon<=tau/16`, `delta<=1/4`, all three are positive, and **`P>=L/epsilon^2`**. The upper bound needs no condition on P. The lower replication condition is stronger than the earlier small-atom condition and cannot be silently replaced by it. No matching saturation result is supplied when it fails.

The upper proof controls a whole group of comparable budgets using one cumulative rank-loss estimate. Bounded decreasing likelihood ratios transfer that estimate to the group. Linear stage sizes and summable error spending give a finite expected completion bound; a census cap ensures completeness on all safe tables. The lower proof uses one mixture of fixed-count rank permutations, so every null table is safe, then changes one disjoint band to make every alternative unsafe. A capped hypergeometric transcript calculation gives the margin dependence without assuming stochastic actual labels.

These are **theoretical cost bounds, not a new implemented audit workflow**. The output is one global assertion, weaker than simultaneously selectable confidence bands. Its lack of an additional family-confidence logarithm does not establish superiority over papers solving that stronger problem. The main concentration and rare-event bandwise lower-bound ideas are established. Constants are loose; unknown-margin adaptation, incorrect labels, new-prompt generalization, and practical finite savings are not established.

## What the fixed calculation checks

Protocol [nonzero_minimax_protocol.json](../experiments/nonzero_minimax_protocol.json) was committed as `fe7a8aa` after exploratory proof work and small-grid checks, before the saved broader calculation. Proof and checker review preceded the saved run; the reviewed implementation was committed as `8e9f05a`. This is internal prespecification, not external preregistration. No model outputs, human annotations, or random audit trajectories were generated.

| Check | Saved scope | Interpretation |
| --- | ---: | --- |
| Within-group likelihood ratios | 15,144 cases through pool size 48 | Exact monotonicity, boundedness, and support |
| Summation-by-parts identities | 327,978 matrix columns | Deterministic linear-map identities within those cases |
| Terminal target zeros | 133,134 entries | Included without dividing by zero representative weights |
| Declared grids | 2,036 nonempty grids through pool size 10 | Includes 1,013 grids without budget 1 |
| Witness bands | 3,376 | Exact disjointness, mass above one quarter, and representative-count bounds |
| Conditional label laws | 3,827 comparisons, including 1,255 cap-boundary cases | Rational KL majorant; not an iid approximation or numerical logarithmic KL |
| Rounded fixed profiles | 16 symbolic certificates | Two thresholds, two relative margins, two confidence levels, two replication multipliers |
| Stage schedules | 8 schedules and 128 stage checks | Sixteen stages per schedule; each schedule reused in two profile records |

The JSON contains 256 stored stage entries because of that reuse. They are not 256 separate schedules or independent trials. The largest symbolic prompt count is 12,565,012; no corresponding population table is allocated. The checker verifies conservative inequalities for rounded counts, strict unsafe alternatives, finite band lower bounds, stage radii, and expected proposal counts. It does not itself prove Bernstein, DKW, the stochastic chain rule, or the infinite-parameter theorem.

The 19 new tests include direct subset enumeration for rank laws, independent fixed-profile enumeration for interleaved conditional queries, signed summation-by-parts examples, terminal-support cases, rounding boundaries, ambiguous ceiling brackets, and source/protocol integrity failures. They pass with site-packages disabled and under optimized Python. The full existing-plus-new suite passes **211 tests** in 9.655 seconds. These checks were performed within the assisted session, not through independent human replication.

## The practical example is a census, not a saving

For the existing 32-prompt, 64-item geometry, take the seven dyadic budgets, `tau=1/10`, `epsilon=1/160`, and `delta=1/20`. The first theoretical stage requires **53,217,055 proposal draws**, while the census cap is only **2,048 distinct labels**. The proof procedure therefore reaches its census cap before its first statistical check. Its cost guarantee here is the census bound.

The lower-bound replication threshold would require at least **76,691 prompts**, so **the lower bound is not applied to this example**. These numbers are exact consequences of the proof's formulas, with logarithms enclosed by outward rational intervals. They are not measured performance. The result establishes a conditional minimax rate, not a practical improvement over the earlier betting engine or a measured resolution of the zero-only power problem.

## Reproduction and integrity

From the repository root, with an existing Python installation:

```console
python -B -S -m experiments.check_nonzero_minimax --out artifacts/local/nonzero-minimax-reproduction.json
python -B -S -m unittest tests.test_nonzero_minimax -q
```

Choose a new output path: the checker refuses overwrites. It uses the standard library, exact fractions, and the unchanged [sharp-cost helper](../experiments/check_sharp_cost.py) for outward logarithm intervals. The canonical protocol is capped at 16 KiB and accepts no larger workload or changed theorem metadata. Both stage-ceiling endpoints are recorded; an unresolved ceiling is reported as an interval rather than silently selected. All ceilings in the saved matrix resolve.

The [saved result](../results/theory/nonzero_minimax.json) pins five sources: the checker, tests, protocol, proof, and imported sharp-cost helper. It uses one protocol snapshot and checks all source bytes again before writing. A second run reproduces all **210,340 bytes** exactly:

```text
SHA-256 57ee1799d142385a8a0edaae4a4bd688b2c5a610bf31d814519c4a22d2f83491
```

Older saved results, mathematical source pins, and both manuscript snapshots remain unchanged. The older `experiments.reproduce` command still covers v0.1-v0.3; this follow-up has its own command above. No downloads, installations, study-model inference, or outreach were performed. Substantial Codex assistance and the missing human verification are recorded in [provenance](provenance.md). Publication and reproducibility do not establish field impact or fellowship competitiveness.
