# A finite audit-cost formula for every declared budget grid

Version 0.13, 27 October 2026. The [candidate theorem](all-grid-minimax-theorem.md) characterizes the worst expected distinct-label cost of one globally valid auditor, up to universal constants, for every finite best-of-n budget grid. It removes the density, replication, and minimum-budget restrictions in the earlier nonzero-table results. A [constructive companion](cached-likelihood-audit.md) gives a smaller upper constant for geometrically separated grids. The proofs have received separate agent review, but no independent human verification; scientific priority remains unestablished.

## The decision and cost formula

There are `P` equally weighted prompt pools, each with `m` candidates in a fixed known rank order. Querying a candidate reveals its fixed correct loss in `[0,1]` at unit cost. A budget `n` selects the best-ranked member of a uniformly sampled n-subset without replacement. For a nonempty declared grid `K`, its winner weights and envelope are

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
e_r=\max_{n\in K}w_n(r).
$$

The auditor issues one certificate asserting that every declared risk is at most `tau`. It must control false certification by `delta` on every unsafe fixed table and certify every safe table almost surely, including tables on the threshold. The efficiency objective `C*(epsilon)` is the infimum, over such auditors, of their worst expected distinct-label cost on tables whose risks are all at most `tau-epsilon`. The supplied margin guides the design; it is not evidence that the actual table is safe. Computation and auxiliary randomness are not charged.

Let `a=min K`, `L=log(1/delta)`, and

$$
H=\frac{\tau L}{\epsilon^2},\qquad
k_\epsilon=\min\left\{k:
\frac{\binom{m-k}{a}}{\binom ma}\le\epsilon\right\},\qquad
G=\sum_{r=1}^m\min\{P,He_r\},\qquad
F=\min\{Pk_\epsilon,G\}.
$$

The deterministic prefix term pays for enough top ranks to leave at most the design margin in the unobserved tail. The clipped term accounts for inspecting heavy ranks and sampling lighter ones. It also equals `min_k (P*k + H*sum_{r>k} e_r)`.

For `0<tau<=1/8`, `0<epsilon<=tau/16`, and `0<delta<=1/4`, the theorem gives

$$
\boxed{F/2^{38}\ \le\ C^*(\epsilon)\ \le\ 2^{16}F.}
$$

There is no further restriction on finite `P`, `m`, or the nonempty grid. The constants are deliberately loose. If successive declared budgets are at least twice their predecessors, the constructive upper bound improves to `C*<=17F`. This is a whole-family threshold decision, not separately selectable confidence bands or an unknown-margin result.

## What changes mathematically

The lower proof combines two common-safe prior constructions. At broad scales, a fixed head removes heavy atoms, and a product prior on the suffix is conditioned on the exact safe class. Transcript information is bounded under the unconditioned laws, with the exceptional mass charged explicitly. One common conditional prior permits costs from disjoint rank bands to be added.

When no broad scale remains, the smallest declared budget dominates the other rows on a tail of constant mass. Centered fixed-count perturbations preserve every null table's smallest-budget risk exactly; domination keeps every other declared risk safe. A finite-population testing bound and conditional winner-rank geometry then recover the clipped and prefix costs. The proof covers budget one, small populations, partial supports, and saturation.

The universal upper construction groups budgets geometrically and bounds the sum of representative residual costs by the envelope tail. The smaller-constant construction uses classical likelihood-ratio tests with a shared label cache. Repeated proposals retain their original sampling laws and use fresh auxiliary Bernoulli coins even when the label is cached. Its stopping and occupancy argument bounds expected distinct acquisitions. Exact evaluation after all relevant labels have been acquired supplies completion at boundary-safe tables. These are mathematical constructions; this release adds no production auditing CLI.

A consequence separates the result from a change of constants. Take one pool, `m=2^d`, all dyadic budgets, fixed admissible `tau,delta`, and `epsilon^2=tau*log(m)/m`. For sufficiently large `m`,

$$
C^*(\epsilon)=\Theta\!\left(\frac{m\log\log m}{\log m}\right)=o(m).
$$

The earlier blanket upper bound `min(P*m, constant*Z_K*H)` only gave census order for this sequence. The new lower and upper bounds identify a smaller matching order. This is an asymptotic theorem about fixed tables and audit randomization, not a measured model saving or a claim about every individual safe table.

## The original finite instance remains separate

For the original `P=32`, `m=64`, seven dyadic budgets, `tau=1/10`, `epsilon=1/160`, and `delta=1/20`, the new functional is exactly `F=2048`. Both endpoints of a rigorous rational bracket for `log(20)` give that value. The loose universal theorem does not improve the [v0.12 certificate](monotone-placement-report.md):

$$
1103.263793259\ \le\ C^*(1/160)\ \le\ 1934.2.
$$

That upper bound uses an explicitly disclosed blind-certification lottery. The new cached construction does not establish a better numerical upper bound on this instance. The separate zero-error bounds and earlier saved results remain unchanged.

## Fixed verification matrix and reproduction

Protocol/specification commit `9dd4a1362f8fce7a5b7334cfa71a40e7c945d74e` preceded the full calculation. An initial source freeze and run were followed by review that found integer-division paths producing floats. The corrected source freeze, `2465848a4ad97f2401d3ceedd330ac4d8a52f761`, precedes the final saved calculation and reproduction. The superseded output is retained locally; no earlier published artifact was replaced. Exploratory derivations and targeted checks preceded these freezes; this is not external preregistration. The [protocol](../experiments/all_grid_minimax_protocol.json) fixes the finite matrix and scope. The [saved result](../results/theory/all_grid_minimax.json) contains aggregate counts, a matrix checksum, six illustrative profiles, the original-instance log bracket, and nine direct/transitive scientific source pins.

| Exact check | Completed count |
|---|---:|
| Distinct budget grids | 2,300 |
| Family/parameter configurations | 27,600 |
| Conditional rank identities | 151,008 |
| Centered finite-slice configurations | 24,384 |
| Factor-two mixture rank checks | 379,856 |
| Factor-four mixture rank checks | 51,864 |
| Likelihood multiplier expectations | 20 |
| Proposal-coefficient comparisons | 8 |

The family matrix includes every nonempty grid through pool size ten and specified larger grids at pool sizes 16, 32, 64, and 128. Each grid is crossed with three prompt counts, two margins, and two exact rational log-confidence values. Its proof branches comprise 6,804 broad-band, 7,618 high-budget, 3,946 tail-block, and 9,232 uniform-tail configurations. Prompt counts are symbolic: the checker does not allocate their candidate tables. The conditional, slice, and mixture matrices are separate checks; these counts are not independent statistical experiments.

All 282 repository tests pass. The 16 focused tests also pass with site packages disabled, normally and under optimized Python. Separate agent contexts reviewed the lower proof, upper construction, attribution, checker, and edge cases. The tests include direct binomial/subset oracles, exhaustive small-prefix minimization, small-population boundaries, validation through cached calls, actual imported-helper source pinning, and an extreme-margin regression. Two new regression tests first reproduced the float paths, then passed after explicit fraction normalization and recursive rejection of floats in exact output. These checks do not replace the proofs' universal arguments or independent human replication.

The saved result is **13,025 bytes**, SHA-256 `fa6175e1392d8edc95ac387a4f4b4a34fc62968a889d2bef24382be20ebb7027`. A second full run to a fresh ignored path reproduced every byte. The ordered finite-matrix checksum is `3b0d96627782d50cd6c88b71061a05d3227df6265c6193e74c6dbd4426357875`. All nine scientific source pins match the reviewed source commit. The earlier saved-evidence integrity command also passes.

```console
python -B -S -m experiments.check_all_grid_minimax --out artifacts/local/all-grid-minimax-reproduction.json
python -B -S -m unittest tests.test_all_grid_minimax -q
python -B -S -O -m unittest tests.test_all_grid_minimax -q
```

Use a fresh output path. The checker uses only the Python standard library, validates the canonical protocol, rejects source drift and overwrites, and uses exact arithmetic for its inequalities. Finite checks support the implementation and arithmetic; the written proofs supply the universal quantifiers.

## Attribution and remaining research gaps

The [primary-source comparison](all-grid-minimax-priority.md) credits clipped inclusion sampling, weighted finite-population inference, conservative likelihood-ratio testing, stratification, geometric-band information arguments, and label caching. The proposed contribution is their combination with this finite rank geometry into the displayed minimax characterization. The comparison does not establish priority, and older unresolved inspection/query-complexity comparisons remain disclosed.

The exact fixed-label oracle, known ranks, equal pools, supplied margin, and single all-pass decision remain material assumptions. No real-model study, noisy-label guarantee, new-prompt inference, downloads, installations, or external outreach occurred. The [provenance record](provenance.md) discloses substantial Codex assistance. The owner has not yet reported personally verifying the project. Publication and agent review do not establish field impact, personal research ownership, or fellowship competitiveness.
