## References

[1] Larry Mai, with substantial Codex assistance. *ai-goodhart*, public
v0.14 research artifact (2026), frozen source at `765ac51`.
[Source and evidence](https://github.com/larrymai33/ai-goodhart/tree/765ac51).
The principal statements are in
[all-grid minimax](https://github.com/larrymai33/ai-goodhart/blob/765ac51/docs/all-grid-minimax-theorem.md)
and
[cached likelihood audits](https://github.com/larrymai33/ai-goodhart/blob/765ac51/docs/cached-likelihood-audit.md).
The secondary finite example uses the separate
[placement](https://github.com/larrymai33/ai-goodhart/blob/765ac51/docs/monotone-placement-theorem.md)
and
[checkpoint](https://github.com/larrymai33/ai-goodhart/blob/765ac51/docs/finite-checkpoint-theorem.md)
proofs. The repository records exact-check protocols, saved outputs,
source pins, rational callback contracts, and contribution disclosures.

[2] Reiichiro Nakano et al. *WebGPT: Browser-assisted question-answering
with human feedback*. arXiv:2112.09332, first posted 2021; inspected
version v3 (2022), Appendix I, “Predicting rejection sampling performance.”
[Primary preprint](https://arxiv.org/html/2112.09332v3).
Its all-subsets evaluation uses binomial rank weights for finite-pool
rejection sampling.

[3] Ricardo Fitas. *The geometry of AI validation: From structural
blindness to reusable audits*. arXiv:2608.21496v2 (2026), Section 2.4
and Supplements S2, S5, and S7.2.
[Primary preprint](https://arxiv.org/html/2608.21496v2).
Relevant antecedents include envelope acquisition, the continuous-rank
normalizer, and best-of-N acquisition bounds. The finite-table all-pass
objective here must be compared at the level of its quantifiers.

[4] Sohail (Neel) Sarkar and Shakuntala Baichoo. *Cheap to Draw, Expensive
to Trust: Certifying Test-Time Scaling Curves*. arXiv:2609.40190v1 (2026),
Section 7.2 and Appendix C.3.
[Primary preprint](https://arxiv.org/html/2609.40190v1).
These passages give deterministic-grade reuse and geometric-band
rare-risk information arguments. The paper also addresses simultaneous
curve certification; that is a different output from one all-pass
threshold assertion.

[5] Nick Duffield, Carsten Lund, and Mikkel Thorup. *Priority sampling
estimating arbitrary subset sums*. arXiv:cs/0509026v1 (2005), Sections
3-3.1.
[Primary preprint](https://arxiv.org/html/cs/0509026v1).
The fixed-threshold scheme and its variance optimization use clipped
inclusion probabilities. Their expected sample-size functional supplies
the algebraic antecedent of the clipped sum in this manuscript; the
optimization objective there is distinct from adaptive certification cost.

[6] Tony Wirth. *The Query Complexity of Estimating Weighted Averages*.
Google TechTalk delivered 4 February 2010, posted 16 February 2010,
crediting joint work with Amit Chakrabarti, Venkatesan Guruswami, and
Andrew Wirth.
[Official primary talk](https://www.youtube.com/watch?v=qyxIUPTeNfI).
The inspected slide at
[14:32](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=872s)
shows heavy-set inspection and normalized residual sampling, with a
squared residual-mass cost and explicit confidence dependence. The slide
at [23:12](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=1392s)
uses deterministic prefix queries until the remaining geometric-weight
mass is below half the desired additive accuracy. This talk is an
antecedent for both mechanisms, not a substitute for checking every
quantifier of the later journal theorem [11].

[7] Lasse Fischer and Aaditya Ramdas. *Improving Wald's (approximate)
sequential probability ratio test by avoiding overshoot*.
arXiv:2410.16076v4 (2025), Sections 1-2.
[Primary preprint](https://arxiv.org/html/2410.16076v4).
The paper describes the classical conservative power-one likelihood-ratio
test, its Ville-inequality justification, and the distinction between
valid conservative thresholds and exact sample-size optimality.

[8] Ran Canetti, Guy Even, and Oded Goldreich. *Lower Bounds for Sampling
Algorithms for Estimating the Average*. Information Processing Letters
53(1), 17-25 (1995); inspected author manuscript dated 6 October 1994,
Sections 2-3.
[Primary author manuscript](https://www.wisdom.weizmann.ac.il/~/oded/PSX/ceg.pdf).
Adaptive fixed-function queries, hard average classes, and expected-query
arguments precede this work. The inspected finite-size regime and
unweighted estimation objective differ from the present theorem.

[9] Shubhanshu Shekhar, Ziyu Xu, Zachary Lipton, Pierre Liang, and Aaditya
Ramdas. *Risk-limiting financial audits via weighted sampling without
replacement*. UAI, PMLR 216:1932-1941 (2023), Section 2, Definition 2,
and Theorem 1.
[Primary proceedings page](https://proceedings.mlr.press/v216/shekhar23a.html).
Weighted finite-population confidence sequences, predictable acquisition,
and control variates for side information are established antecedents.

[10] Jacob V. Spertus, Mayuri Sridhar, and Philip Stark. *Sequential
stratified inference for the mean*. arXiv:2409.06680v5 (2026), Sections
2.1-2.2 and 3.2, Lemma 1, and Appendix C.
[Primary preprint](https://arxiv.org/html/2409.06680v5).
The inspected treatment includes finite populations, adaptive stratum
selection, composite-mean testing, and the difference between logical
stopping time and actual sample count.

[11] Amit Chakrabarti, Venkatesan Guruswami, Andrew Wirth, and Anthony
Wirth. *The query complexity of estimating weighted averages*. Acta
Informatica 48:417-426 (2011). DOI: 10.1007/s00236-011-0145-8.
[Primary publisher record](https://link.springer.com/article/10.1007/s00236-011-0145-8).
The publisher abstract and references were accessible; the final paper's
full proof was not obtained. The earlier primary talk [6] establishes
specific algorithmic antecedents, while the full finite-size,
confidence-dependent, safe-side expected-cost comparison remains open.

[12] Stéphane Lhaut, Anne Sabourin, and Johan Segers. *Uniform concentration
bounds for frequencies of rare events*. arXiv:2110.05826v2 (2022), Lemma 2.1
and equation (2.1).
[Primary preprint](https://arxiv.org/html/2110.05826v2).
Conditioning on the rare-region count and then combining conditional
concentration with binomial Bernstein is an established device.

[13] Henry W. J. Reeve. *A short proof of the Dvoretzky–Kiefer–Wolfowitz–Massart
inequality*. arXiv:2403.16651v1 (2024), Theorem 1 and Corollaries 1–2.
[Primary preprint](https://arxiv.org/html/2403.16651v1).
This provides a modern proof and attribution for empirical-CDF concentration;
the manuscript uses the classical two-sided bound.

[14] Steven R. Howard, Aaditya Ramdas, Jon McAuliffe, and Jasjeet Sekhon.
*Exponential line-crossing inequalities*. arXiv:1808.03204v4 (2019),
Section 1.2. Published as *Time-uniform Chernoff bounds via nonnegative
supermartingales* (2020).
[Primary preprint](https://arxiv.org/html/1808.03204v4).
The stated Ville inequality for a nonnegative supermartingale is the
classical maximal inequality applied in Appendix A.3.
