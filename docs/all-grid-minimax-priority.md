# Attribution and scope of the all-grid finite characterization

Bounded primary-source comparison, 27 October 2026. The target is the
[all-grid theorem](all-grid-minimax-theorem.md): fixed fractional labels,
one globally valid whole-family certificate, completion on every safe
table, and worst expected distinct-label cost over the supplied-margin
class. Its statement is `F/2^38 <= C*(epsilon) <= 2^16 F`, where
`F=min(P*k_epsilon, sum_r min(P,H*e_r))` and
`H=tau*log(1/delta)/epsilon^2`. It removes density, replication, and
minimum-budget restrictions. The [constructive companion](cached-likelihood-audit.md)
gives `C*<=17F` for factor-two-separated grids. Neither statement asserts
optimal leading constants or a new generic sequential test.

## Established sampling and testing mechanisms

[Duffield, Lund, and Thorup, *Priority sampling estimating arbitrary subset
sums* (2005), Sections 3–3.1](https://arxiv.org/html/cs/0509026v1), use
clipped inclusion probabilities. The optimization preceding equation (10)
gives `p_i=min(1,sqrt(beta)*w_i)`. Substituting known item weights `e_r/P`
and threshold `1/H` produces expected sample size
`sum_r min(P,H*e_r)`. This correspondence is algebraic: the clipped
functional and certainty inspection of heavy items are established.
The cited optimality concerns unbiased-estimator variance, rather than
all globally valid decision procedures. The deterministic margin-tail cap
and matching decision lower bound require their own arguments.

[Shekhar et al., *Risk-limiting financial audits via weighted sampling
without replacement* (UAI 2023)](https://proceedings.mlr.press/v216/shekhar23a.html),
already provide weighted finite-population confidence sequences,
predictable acquisition, and control variates for imperfect side
information. Section 2, Definition 2 and Theorem 1, is compared formula by
formula in the [earlier attribution note](anytime-related-work.md).
Weighted sequential auditing of nonzero bounded losses is therefore
established; implementing another such process alone would not supply
the present contribution.

[Fischer and Ramdas, *Improving Wald's (approximate) sequential probability
ratio test by avoiding overshoot*, arXiv:2410.16076v4 (2025), Sections
1–2](https://arxiv.org/html/2410.16076v4), explicitly describe the
conservative power-one likelihood-ratio test with threshold `1/alpha` and
derive its validity from Ville's inequality. They also distinguish this
conservative threshold from exact sample-size optimality. The companion
uses classical likelihood-ratio testing, fresh auxiliary Bernoulli
randomization, and ordinary stopping/occupancy accounting. It does not
introduce an SPRT, prove that its particular stopping rule is exactly
optimal, or claim a new generic martingale inequality.

## Close stratified and best-of-n predecessors

[Spertus, Sridhar, and Stark, *Sequential stratified inference for the
mean*, arXiv:2409.06680v5 (2026)](https://arxiv.org/html/2409.06680v5),
Sections 2.1–2.2 and 3.2, treat bounded finite populations, adaptive
stratum selection, and composite-mean tests built from product test
supermartingales. Lemma 1 separates logical stopping time from actual
sample count, which can differ by the number of strata. The passage
following Proposition 3 explains that greedy Kelly selection can fail
without replacement because strata are depleted; Appendix C uses dynamic
programming. Thus stratification, adaptive allocation, and optimizing
bets are established. The inspected results do not state this project's
all-grid worst-safe-class minimax theorem. Its physical distinct-query
accounting and uniform cost claim must be proved explicitly.

[Sarkar and Baichoo, *Cheap to Draw, Expensive to Trust: Certifying
Test-Time Scaling Curves*, arXiv:2609.40190v1
(2026)](https://arxiv.org/html/2609.40190v1), Appendix C.3, already combines
rare-risk perturbations, geometric score bands, per-label KL of order
`epsilon^2/tau`, and summation over disjoint bands. Section 7.2 explicitly
reuses deterministic grades for repeated question–answer pairs while
preserving the audit's observations and coverage. Neither multiscale
testing nor label caching is introduced here. Their stated experiment
generates answers and certifies simultaneous curve bands; the present
experiment queries a recorded finite table and certifies one global
threshold decision. This difference requires a separate reduction, not
an assertion that their methods are irrelevant.

## The narrower contribution and remaining limits

The candidate contribution is the complete finite characterization for
the specified rank family. The lower proof combines a safe-conditioned
suffix prior for broad scales with a different, exactly safe tail prior
for the saturation regime. Each sum of costs is established under one
common safe prior, using its associated alternatives. The upper proof controls the
total cost of representative residual audits through the finite winner
geometry. Giving each component error delta is ordinary
intersection–union reasoning for an all-pass certificate; it does not
produce separately selectable simultaneous confidence bands.

The constructive companion's additional statement is a clipped expected
**distinct** cost bound with a fully specified completion rule. Repeated
proposals reuse fixed labels but require fresh auxiliary coins. Its
dyadic scaling corollary concerns a parameter sequence, not observed
model performance. These claims strengthen the mathematical result
without improving the existing original-instance lower certificate or
establishing useful operational constants there.

The [finite-saturation comparison](finite-saturation-priority.md) records
the unresolved proof-level comparison with the 2011 weighted-average
query paper; the [inspection review](inspection-priority-review.md)
records the original IAEA-source gap. Those inaccessible sources were
not retried. The inspected primary passages do not directly establish
the complete displayed theorem, but this bounded finding does not
establish priority. No papers were saved or authors contacted. Exact
checks and publication cannot establish independent human verification,
label reliability, actual-model usefulness, or field impact. The
[provenance record](provenance.md) discloses substantial Codex assistance.
