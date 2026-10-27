# When independent inspection attains the optimal leading label cost

The [new proof](sharp-cost-theorem.md) sharpens the project's zero-table comparison from a constant factor to a ratio tending to one. It concerns the full budget prefix `{1,...,N}` and the same whole-family decision, correct fixed labels, equal prompt weights, and unit query cost as the earlier theorem.

Let `L=log(1/delta)`, let `Z_mN` be the known finite rank-envelope normalizer, and let `D=P*m` be the number of distinct items. Along any parameter sequence satisfying

`tau -> 0`, `rho=L*N/(D*tau) -> 0`, and `0 < delta <= 1/4`,

the theorem gives

`OPT_0 ~ C_NEG ~ L*Z_mN/tau`.

Here `OPT_0` ranges over every admissible adaptive auditor; `C_NEG` is the expected distinct-query cost of classical independent NEGEXP inspection. Both costs are evaluated on an all-zero loss table, while validity is required against every fixed table. The result allows P, m, N, and delta to vary jointly. When N grows, the established normalizer asymptotic gives leading cost `L*log(N)/(e*tau)`.

The candidate contribution is the matching adaptive-cost lower bound, uniform in growing target families. NEGEXP, the envelope construction, its `1/e` coefficient, and generic geometric/Jensen arguments are established ingredients. [The attribution section](sharp-cost-theorem.md#8-rational-designs-numerical-evidence-and-attribution) records those distinctions and the unresolved priority review.

## The step that closes the gap

For a block of d items where every b-item subset is unsafe, the zero-path constraints imply

`expected queried block items >= L*(d-b)/(b+L)`.

This follows from the convex interpolation of the hypergeometric miss probability, without assuming independent queries or a nonadaptive audit. It approaches `L*d/b` when both the unsafe subset and the required inspection fraction are small relative to the block.

The proof groups adjacent ranks whose envelope values differ by at most a factor `1+eta`. A target maximizing the envelope at a bin's last rank supplies a witness for that entire bin, because every rank law is decreasing. Nearly all envelope mass can be retained while making the block approximation accurate. The bound on the number of bins relative to Z is uniform in N, which is what makes the conclusion stronger than a fixed-family limiting observation.

## What the result does not establish

This is a dense-population, rare-threshold limit. The coarse universal finite expression is vacuous at the earlier study's threshold 0.1. It does not establish practical optimality there, efficiency of the betting engine, low costs on nonzero tables, reliable annotations, or safety on new prompts.

The exact probability sandwich used by the released zero-only workflow transfers the mathematical cost bound on supported inputs. Its input and storage limits are unchanged. Symbolic populations in the analytical certificates can exceed those CLI limits; no claim is made that the tool sampled those populations.

The confidence condition matters. If delta approaches one, rho tending to zero alone need not imply optimality: the proof gives a one-target counterexample where an allowed census lottery is much cheaper. The general finite inequality displays both relevant atom-size terms explicitly.

Two proposed nonzero-table directions were also screened. A fixed-reference comparison guarantee is an immediate classical corollary, and universal pointwise competitiveness encounters a known testing-versus-verification obstruction. These are [attributed limitations](nonzero-cost-limits.md), not new research claims promoted into separate algorithms.

## Reproduction and evidence scope

The saved [exact-check artifact](../results/theory/sharp_cost.json) contains 10,400 inverse-miss comparisons over block sizes 1 through 64 and five confidence levels, including 320 full-block endpoints. Four additional cases use block/subset sizes (10,000, 100) and (1,000,000, 1,000). All finite-lemma comparisons pass. These compare the lemma with a block constraint's exact interpolated inverse, not the global adaptive optimum.

The 56 analytical certificates cover four `(m,N)` geometries, two confidence levels, and seven k values. They set `tau=1/k^3` and `P=ceil(3*N*k^4/m)`, which ensures `rho <= 1/k`. There are 2,814 rank-witness checks and 1,164 retained-block unsafe-size checks. For each k, the table gives the largest conservative bound on `C_NEG/OPT_0` across its eight prescribed settings, rounded upward to six decimal places:

| k | Threshold tau | Maximum certified ratio bound |
| ---: | ---: | ---: |
| 8 | 1/512 | 1.168867 |
| 16 | 1/4,096 | 1.083515 |
| 32 | 1/32,768 | 1.041655 |
| 64 | 1/262,144 | 1.020816 |
| 128 | 1/2,097,152 | 1.010407 |
| 512 | 1/134,217,728 | 1.002602 |
| 2,048 | 1/8,589,934,592 | 1.000651 |

These values use the sum of individual block lower bounds, which is stronger than the coarse universal expression. They do not assert that any listed ratio is the exact ratio. The largest population count is 6,755,399,441,055,744; it is a symbolic integer in an analytical calculation, not an acquired dataset, a sampled audit, or a deployment recommendation. The threshold and population scaling are deliberately asymptotic.

The [protocol](../experiments/sharp_cost_protocol.json) was committed as `2593893` after exploratory proof checks and before the saved broader calculation. It prescribes finite inverse-miss checks and analytical certificates, not an empirical model study or an external preregistration. The standard-library command is:

```console
python -B -S -m experiments.check_sharp_cost --out artifacts/local/sharp-cost-reproduction.json
python -B -S -m unittest discover -s tests -p "test_sharp_cost.py" -v
```

Use a new output path. The checker pins its source, tests, protocol snapshot, the new proof, and the existing finite-normalizer proof. It compares exact rational constraints and uses rigorous outward log bounds. Each block lower bound is rounded down and the total linear upper bound up to a fixed dyadic scale before serialization. Populations are represented by counts; no `P*m` loss table is allocated. Finite checks support arithmetic and implementation, while the written proof supplies the unbounded result.

A separate run reproduced all 93,438 artifact bytes, SHA-256 `901ec03f590c01de2ce58f89d7b7048e69e0b61a0236fe94d602980d094dd313`. All 182 project tests pass, including eleven focused tests under standard-library-only Python. Review found and corrected inward decimal-display rounding; exact serialized fractions were already conservative, and displays now also round outward. Earlier saved results and their pinned sources remain unchanged. These reviews and reruns occurred within the assisted development session, not independent human replication.
