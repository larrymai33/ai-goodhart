# Prior-art comparison for finite saturation

Bounded primary-source comparison, 27 October 2026. The target is the
[finite-saturation theorem](finite-saturation-theorem.md): fixed fractional
losses, a supplied margin, one globally valid whole-family certificate,
and worst-case expected distinct-query cost over tables whose risks are
all at most `tau-epsilon`. For every declared grid with `min K>=m/4`, its
claim is

`F/2^21 <= C*(epsilon) <= 12288 F`,

where `H=tau*log(1/delta)/epsilon^2`, `e_r=max_(n in K) w_n(r)`, and
`F=min(P*k_epsilon, sum_r min(P,H*e_r))`. Here `k_epsilon` is the first
prefix leaving at most epsilon mass under the smallest declared budget.
The parameter restrictions remain `tau<=1/8`, `epsilon<=tau/16`, and
`delta<=1/4`. No density or replication condition is imposed. This is a
restricted finite-geometry result; it does not settle grids whose smallest
budget is a vanishing fraction of the pool.

## Established sampling architecture

Deterministic heavy-item inspection followed by randomized residual
sampling is established. [Duffield, Lund, and Thorup (2005), Section 3 and
Proposition 3](https://arxiv.org/html/cs/0509026v1), use inclusion
probabilities `min(1,w_i/t)` and prove optimality for the sum of unbiased
item-estimator variances. For the present decreasing envelope, the identity

`inf_k [P*k+H*sum_(r>k)e_r] = sum_r min(P,H*e_r)`

shows that the proposed hybrid surrogate is exactly the expected size of
that classical clipped-inclusion design, using item weights `e_r/P` and
threshold `1/H`. Neither the architecture nor this functional is claimed
as new.

[Thorup (2013), Section 3.1, equations (12), (15), and (17), and Theorem
5](https://arxiv.org/html/1303.5479v2), explicitly handles fractional
contributions, separates exact heavy mass from random light mass, and
obtains tail-dependent concentration. Its target fraction vector is fixed;
uniformity over sampling thresholds in its proof is not simultaneous
coverage over different target vectors. These statements do not directly
give the present family-wide power and expected completion guarantee.
Conversely, the present global decision is weaker than simultaneously
selectable confidence bands. Its absence of a grid-confidence logarithm
must not be advertised as improving those stronger guarantees.

## Classical lower-bound ingredients and the finite step

[Canetti, Even, and Goldreich (1995), Sections 2–3, Theorem 1 and Corollary
1](https://www.wisdom.weizmann.ac.il/~/oded/PSX/ceg.pdf), already treat
adaptive queries to fixed Boolean functions, use exact-average classes,
and derive expected-query lower bounds through truncation. Their displayed
theorem concerns unweighted estimation around one half and assumes at most
`sqrt(D)/4` queries on a domain of size D, for sufficiently large D. It does
not supply the present all-finite, weighted, safe-side certificate result.
Fixed-table priors and expected-cost truncation are nevertheless established
ingredients, not contributions of this extension.

Rare-event perturbations also predate it. [Sarkar and Baichoo (2026),
Appendix C.3, “The multiscale term”](https://arxiv.org/html/2609.40190v1),
combines a rare baseline, order-epsilon changes within geometric bands,
per-label information of order `epsilon^2/tau`, and summation over disjoint
bands. The present proof does not introduce that information principle.

The proposed finite step controls depletion in a uniform fixed-count
block. With N cells, k positives under the safe prior, and k+d under its
alternative, it obtains expected block cost at least
`min(N,N*(k+1)*log(1/delta)/d^2)/1024`, when `k+d<=N/2`.
Instead of requiring every transcript to leave half the positives unseen,
it bounds the expected reciprocal remaining count:

`E[1/(k-S_t+1)] <= (N+1)/[(k+1)*(N-t+1)]`.

This is elementary hypergeometric algebra from a binomial-coefficient
identity and Vandermonde's identity, not a new distributional identity.
Its use inside the capped transcript-information argument is the specific
proof step to assess. Independence of the outside table from the changed
block is necessary; identical outside marginals alone do not suffice.

Fractional amplitudes make one common rank-count prior have risk exactly
`tau-epsilon` for every target. Its alternatives are strictly unsafe, so
there is no exceptional unsafe mass in the baseline prior. A complementary
hidden-subset argument covers small prompt counts. Log-concavity and the
high-budget condition then compare the resulting squared-weight lower
bound with F. These steps describe the candidate theorem's additional
work, without establishing its originality.

## Remaining comparison limits

[Shekhar and Ramdas (2026), Definition 3.3 and Theorem
3.4](https://arxiv.org/html/2603.14423v1), provide finite-population
information limits for fixed-size uniform sampling without replacement.
Their finite-alphabet lower theorem uses an asymptotic confidence regime;
weighted sampling and time-uniform guarantees are listed as extensions.
It does not directly imply this adaptive expected-cost characterization.
The deterministic prefix cap also matters: at very small delta it can
remain bounded while the uncapped clipped sum grows. Census-size
saturation alone therefore misses the relevant weight geometry.

[Chakrabarti, Guruswami, Andrew Wirth, and Anthony Wirth (2011), *The query
complexity of estimating weighted
averages*](https://link.springer.com/article/10.1007/s00236-011-0145-8),
is an unresolved close lead. Its publisher abstract covers geometric and
power-law weights, but the full proof was not obtained. Its precise
finite-size conditions, confidence dependence, and lower-bound quantifiers
remain unchecked; retrieval was not repeated for this comparison.

The inspected statements do not directly establish the complete displayed
theorem. That bounded finding establishes neither priority nor practical
savings. Independent human proof review and the outstanding weighted-query
comparison remain separate requirements.
