# Finite-pool corrections for reusable best-of-N audits

**Larry Mai — with substantial Codex assistance**

Research note, 26 October 2026. Evidence frozen at public release v0.3, commit e589045.

**Contribution disclosure.** Larry Mai commissioned this project. Codex agents generated the research direction, literature assessment, mathematical arguments, software, synthetic experiments, and manuscript. Separate agent contexts reviewed the work. Those checks are not independent human review or replication; neither has been completed. Authorship here does not establish independent human derivation of the results.

## Abstract

Auditing a family of best-of-N selectors requires labels where different selection budgets place probability mass. A normalized envelope of their rank distributions minimizes the largest importance weight, but its finite-pool behavior differs from the established continuous-rank formula. For uniform selection without replacement from a pool of size m, we prove that the finite envelope exceeds the continuous integer-budget envelope by at most (N minus the continuous normalizer)/(m+1), uniformly for every N at most m. This yields the same logarithmic leading coefficient throughout joint limits and a bounded second-order correction determined by N/m. We derive that correction and its diagonal constant. Exact arithmetic checks and numerical evaluations support the implementation. A separate synthetic comparison uses established variance and fixed-width proposal objectives within a common sequential audit engine. Optimized proposals improve some certification costs, while simpler mixtures win other comparisons. These experiments use previously observed scenarios and provide no real-model or population-generalization evidence. The finite-pool comparison is a contribution candidate whose priority remains unestablished; general envelope design and sequential inference are prior work.

## 1. Motivation and relation to prior work

Selecting the highest-scoring candidate can amplify failures that a proxy score fails to penalize. Evaluation at one search budget therefore need not describe another. Reusable audits address this problem by sharing labels across a declared family of selectors. Their usefulness depends both on how candidates are acquired and on which risk the resulting statement actually covers.

The all-subsets rank-weight estimator is established: OpenAI's account of Goodhart's law gives the binomial weights and points to WebGPT for their derivation [1]. The normalized-envelope principle is the classical normalized maximum likelihood minimax-ratio construction [2]. Fitas gives the continuous-rank integer-budget envelope, its logarithmic coefficient, and variance-based reusable audit designs [3]. Sarkar and Baichoo provide the fixed-width design objective used in our comparison [4]. Weighted sampling without replacement and betting confidence sequences already appear in financial auditing [5]. We claim no new general auditing method.

The question studied here is narrower: how accurately does the continuous envelope describe a finite pool when the maximum search budget can approach the pool size? Taking the pool size to infinity at a fixed budget does not answer that question. Our result gives a uniform finite remainder and then identifies a joint-limit correction. The empirical component tests the separate issue of whether controlling the worst importance weight also produces favorable label costs.

An earlier project release assessed Fitas only from its abstract and missed material overlap. This note uses the corrected comparison. A bounded literature check did not establish priority for the finite-pool remainder or joint profile; independent novelty assessment remains necessary.

## 2. Finite-pool target and audit envelope

Fix P prompt pools, each containing m candidates. Within each pool, rank candidates by a frozen proxy score, with rank 1 best. A declared total order resolves ties. Candidate losses are fixed numbers between zero and one; binary bad-event labels are the principal example. For budget n, the selector draws a uniform subset of n distinct candidates and returns its best member. Its rank law is

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}},\qquad 1\le r\le m.
$$

The numerator counts subsets in which rank r wins. Binomial coefficients outside their usual support are zero. The mean loss over the fixed prompt pools is

$$
R_n=\frac{1}{P}\sum_{i=1}^{P}\sum_{r=1}^{m}w_n(r)y_{i,r}.
$$

This is a conditional finite-pool estimand. Prompt or candidate independence is unnecessary for its definition. Conversely, an audit of this target does not establish reliability on newly sampled prompts, fresh generations, a changed scorer, or a different tie rule. Sampling with replacement from the empirical candidate distribution defines another selector and another rank law.

For the complete budget family from 1 through N, define

$$
s(r)=\max_{1\le n\le N}w_n(r),\qquad Z_{m,N}=\sum_{r=1}^{m}s(r),\qquad q(r)=\frac{s(r)}{Z_{m,N}}.
$$

A randomly selected prompt and rank drawn from q provide an unbiased importance-weighted observation of each risk. Every weight is at most the normalizer. For any competing rank proposal p, an upper bound C on all ratios requires C times p(r) to be at least s(r). Summing establishes C at least Z; the envelope proposal attains equality. This familiar argument minimizes a range constant, not variance, interval width, or stopping cost for every loss table.

For continuous score percentiles u, the winner density is n times u to power n minus one. Its integer-budget envelope normalizer is the established quantity [3]

$$
L_N=1+\sum_{n=2}^{N}\ell_n,\qquad \ell_n=\frac{(n-1)^{n-1}}{n^n}.
$$

The continuous formula has leading term log(N)/e. The following comparison applies to the finite without-replacement laws above.

## 3. A uniform finite-pool bound

**Theorem 1.** For every pair of integers m at least N at least 1,

$$
0\le Z_{m,N}-L_N\le\frac{N-L_N}{m+1}\le\frac{N-1}{m+1}<1.
$$

The sharper upper bound is attained at m=N=2. Consequently, the finite normalizer equals log(N)/e plus a uniformly bounded remainder. Its difference from the continuous normalizer vanishes whenever N/m tends to zero, including growing-budget regimes.

**Proof.** Write v(m,n) for the total variation distance between consecutive rank laws. At each rank, the ratio of consecutive weights is

$$
\frac{w_{n+1}(r)}{w_n(r)}=\frac{n+1}{n}\frac{m-r-n+1}{m-n}.
$$

On positive support this ratio is at least one exactly when n is at most (m-r+1)/r. The weights are therefore unimodal in budget. Increasing a running maximum from budget n-1 to n adds the positive part of the difference between those two weights. Summing over ranks gives

$$
Z_{m,N}=1+\sum_{n=2}^{N}v(m,n),\qquad v(m,n)=\frac{1}{2}\sum_r|w_n(r)-w_{n-1}(r)|.
$$

Two useful bounds follow from elementary comparisons. First, choose a uniform n-subset and delete a uniformly selected member. The remaining set is a uniform subset of size n-1. Their winners differ only if the deleted member was best, an event of probability 1/n. Hence n times v(m,n) is at most one.

For the lower bound, apply a common probability kernel to both rank distributions. The rth largest of m independent uniform variables has density

$$
K_r(u)=\frac{m!}{(m-r)!(r-1)!}u^{m-r}(1-u)^{r-1}.
$$

The binomial theorem verifies that the mixture of these densities with weights w_n is exactly n times u to power n minus one. Total variation contracts under a common kernel. The continuous densities for budgets n and n-1 cross at (n-1)/n; integrating their positive difference gives ell_n. Thus v(m,n) is at least ell_n. The kernel is only a mathematical comparison: it adds no distributional assumption to the fixed-pool audit.

It remains to bound the finite excess. Let k be the floor of (m+1)/n. The consecutive rank laws cross at this rank. Summing their positive difference and simplifying the binomial coefficients yields

$$
v(m,n)=\frac{k}{m-n+1}\prod_{j=0}^{n-2}\left(1-\frac{k}{m-j}\right).
$$

Here k is at most m-n+1, so all factors are nonnegative. Replacing every denominator m-j inside the product by m increases it. With x=k/m, maximize x times (1-x) to power n-1 over the unit interval; its maximum, attained at x=1/n, is ell_n. Therefore

$$
(m-n+1)v(m,n)\le m\ell_n.
$$

Add the deletion-coupling inequality n times v(m,n) at most one. The resulting increment comparison is

$$
0\le v(m,n)-\ell_n\le\frac{1-\ell_n}{m+1}.
$$

Summing proves the theorem because the upper numerators sum to N-L_N. The case N=1 has an empty sum. At m=n=2 both upper comparisons are equalities. Finally, ell_n equals 1/(en) plus a summable term of order 1/n squared. Together with the bounded correction, this proves the uniform logarithmic statement.

## 4. Joint-limit profile and the diagonal

The bounded remainder has a more precise form. For positive x at most one, put k(x) equal to the floor of 1/x and define

$$
g(x)=k(x)(1-x)^{k(x)-1}-\frac{1}{ex},\qquad G(\rho)=\int_0^\rho g(x)\,dx.
$$

Use the empty-product convention at x=1. Neighboring formulas agree at reciprocal-integer breakpoints. The next argument also proves that g is bounded between zero and one almost everywhere, resolving integrability at zero.

**Theorem 2.** The approximation is uniform over all budget caps:

$$
\sup_{1\le N\le m}|Z_{m,N}-L_N-G(N/m)|\longrightarrow0.
$$

**Proof.** Rewriting the preceding binomial ratio as a product over the k excluded ranks gives

$$
mv(m,n)=k\prod_{j=1}^{k-1}\frac{m-n+1-j}{m-j}.
$$

For fixed x away from reciprocal-integer breakpoints, choose n as the ceiling of mx. Then n/m tends to x and k eventually equals k(x). The last display tends to k(x) times (1-x) to power k(x)-1, whereas m times ell_n tends to 1/(ex).

On each cell ((n-1)/m,n/m], define a step function f_m as m times the difference v(m,n)-ell_n; set its first cell to zero. Theorem 1's increment bound gives zero at most f_m less than one. These functions converge almost everywhere to g. Dominated convergence therefore gives convergence in the integral of the absolute difference. But the finite correction is exactly the integral of f_m from zero to N/m. Its error against G(N/m) is bounded by that same absolute-difference integral, independently of N. This proves uniformity, rather than only convergence for a single chosen ratio.

Define c_0 as the limit of L_N minus log(N)/e, which exists by the summable expansion above. If N grows and N/m tends to rho, continuity of G implies

$$
Z_{m,N}=\frac{\log N}{e}+c_0+G(\rho)+o(1).
$$

For rho zero the profile vanishes. To identify the diagonal, integrate g separately on its reciprocal-integer intervals. The finite sum telescopes:

$$
\int_{1/(J+1)}^1 g(x)\,dx=\left(\frac{J}{J+1}\right)^J+L_J-1-\frac{\log(J+1)}{e}.
$$

Taking J to infinity gives G(1)=c_0-1+1/e. Thus

$$
Z_{m,m}=\frac{\log m}{e}+2c_0-1+\frac{1}{e}+o(1).
$$

Numerically, c_0 is approximately 0.993152990876 and the diagonal constant is approximately 1.354185422923. These decimals are approximations, not interval-certified enclosures. No convergence rate is asserted for Theorem 2.

## 5. Arithmetic and numerical checks

The standalone checker verifies 19,900 exact rational pairs covering every 2 at most n at most m at most 200. It compares the crossing expression with an independent product formula and checks both component inequalities and their sharpened combination. Separate tests compare direct rational rank laws and every budget cap through pool size 60. These checks support the implementation; the proofs establish the universal statements.

For pool size 100,000, the saved profile comparison is:

| N/m | Finite correction | Limiting profile | Difference |
| ---: | ---: | ---: | ---: |
| 0.10 | 0.019131140529 | 0.019124472322 | 0.000006668207 |
| 0.25 | 0.051005930689 | 0.050998478767 | 0.000007451922 |
| 0.50 | 0.116034984886 | 0.116027029481 | 0.000007955405 |
| 1.00 | 0.361040387454 | 0.361032432047 | 0.000007955407 |

At m=N=1,000,000 the normalizer is 6.436628732023 and its correction is 0.361033437586. Finite corrections need not approach the diagonal limit from below: at m=N=100 the correction is 0.362660789491, exceeding the limiting value approximately 0.361032432047. Theorem 1 does not assert such monotonicity.

## 6. Synthetic proposal comparison

The experiment addresses acquisition quality, which the range theorem does not settle. It uses 32 prompts with 64 candidates each and seven targets: budgets 1, 2, 4, 8, 16, 32, and 64. **These seven-target empirical envelopes differ from the complete-prefix family in Theorems 1 and 2.** In particular, their normalizer 2.863112 is not the full-prefix value Z for all 64 budgets.

Seven proposals share one sequential inference engine. Uniform sampling is compared with a uniform mixture over all 64 budget laws, a mixture over the seven dyadic budgets, an equal mixture of uniform and budget-64 sampling, the seven-target envelope, and two optimized proposals. For known target masses a, let V be the sum of squared masses divided by proposal probabilities, and W the largest mass-to-probability ratio. The variance proposal minimizes the maximum V across targets. The fixed-width proposal minimizes the maximum of V+W/48. These are attributed fixed-draw objectives [3,4], used here only to choose proposals for the common without-replacement engine; neither directly minimizes its stopping time.

| Proposal | Maximum V | Maximum W | Maximum of V+W/48 |
| --- | ---: | ---: | ---: |
| Uniform | 64.000000 | 64.000000 | 65.333333 |
| Budget mixture | 22.000000 | 64.000000 | 23.333333 |
| Dyadic mixture | 3.527559 | 7.000000 | 3.601050 |
| Max/uniform | 11.461564 | 32.507937 | 12.138813 |
| Envelope | 2.863112 | 2.863112 | 2.922760 |
| Variance optimized | 2.326780 | 4.574166 | 2.402215 |
| Fixed-width optimized | 2.336517 | 4.440723 | 2.385195 |

The last column maximizes a sum and is not obtained by adding the preceding maxima. Feasible primal and dual objectives bracket the numerical optima, with relative gaps 7.63e-8 and 1.56e-7. These are floating-point brackets, not formal interval-arithmetic certificates. Optimizers receive target masses, never labels.

Each draw queries a previously unseen candidate. Predictable inverse-probability normalization supplies bounded observations centered at the candidate remaining risk. A fixed mixture of six fractional bets, from 1 to 1/32, constructs separate upper and lower processes. Applying Ville's inequality at threshold 2K/delta and combining the K targets gives simultaneous validity over the observed times. Deterministic missing-label bounds are also used. This is a specialization of established weighted-without-replacement inference [5], not a new confidence-sequence theorem. Every proposal uses the same implementation and settings.

Eight fixed synthetic scenarios represent rare top-rank failures, systematic top failures, interior and bottom bands, constant rank prevalence, a Goodhart-shaped curve, prompt-clustered failures, and an all-safe table. The threshold is 0.1 and delta is 0.05. There are 100 paired repetitions per scenario, with checkpoints at 32, 128, 512, and 1,024 unique labels. Error events are checked between checkpoints as well. Certification uses the directional upper test; it is distinct from requiring a nonempty two-sided reported interval.

The combined evidence has **800 independent scenario–replicate streams and 5,600 paired method paths**: 4,000 paths reused from v0.2 and 1,600 added for the two optimized proposals. Methods share exponential-race uniforms within each stream. The 22,400 checkpoint records are not independent experiments. The follow-up protocol was committed before new measurements, but earlier scenario outcomes were visible. This is neither a fresh holdout nor external preregistration.

The next table reports first certification of budget 64 in the rare-top scenario, and mean certified safe budgets at 512 labels in the prompt-cluster scenario. Parentheses contain Monte Carlo standard errors for those means. All seven targets are truly safe in both scenarios.

| Proposal | Rare-top median labels | Successes by 512 | Prompt-cluster mean (SE) |
| --- | ---: | ---: | ---: |
| Uniform | Not reached | 0/100 | 0.38 (0.06) |
| Budget mixture | 93 | 100/100 | 4.26 (0.05) |
| Dyadic mixture | 200.5 | 100/100 | 2.44 (0.15) |
| Max/uniform | 103.5 | 100/100 | 1.34 (0.06) |
| Envelope | 163 | 100/100 | 1.39 (0.08) |
| Variance optimized | 129 | 100/100 | 1.30 (0.07) |
| Fixed-width optimized | 129.5 | 100/100 | 1.28 (0.06) |

The variance proposal reduces this rare-top median by about 21% relative to the envelope. Top-focused mixtures are faster still, but certify fewer rare-top budgets at 512 labels: 6.00 for the budget mixture and 4.99 for max/uniform, versus 7.00 for the envelope and both optimized proposals. Prompt-cluster results reverse the comparison: the budget mixture certifies substantially more of the safe family. Smaller differences among the other proposals are descriptive, not significance claims. In the all-safe case, medians are 147, 116.5, and 117 for envelope, variance, and fixed-width proposals. No uniform cost ranking follows.

Uncertified targets remain censored; the sample cap is not recorded as a successful stopping time. Across settings, the largest observed ever-miscoverage fraction through 1,024 labels is 2/100; no false certifications were observed. Per-setting 95% Wilson upper limits are approximately 0.070 for 2/100 and 0.037 for 0/100. These counts neither establish exact 95% calibration nor replace the validity assumptions.

## 7. Limitations, reproducibility, and interpretation

The mathematical contribution candidate is the finite-pool bridge and joint profile. The coefficient inherited from continuous ranks, normalized-envelope design, optimized proposal objectives, and generic sequential inference are established. Controlling range is useful but does not prove universally optimal annotation cost. The six-bet grid can limit sensitivity to small discrepancies before census; its use is shared across the comparisons.

All loss tables are synthetic and fixed. No model inference, human annotation study, population-level reliability evaluation, or practical deployment benefit has been measured. One noisy judgment per candidate would certify the realized annotation table, not latent error-free labels. Moving to new prompts requires a separate sampling argument. These restrictions matter even when every finite-pool label has been acquired.

Release v0.3 records source and output hashes, reused-data provenance, raw paths, summaries, and optimization brackets [6]. Its recorded verification comprises 105 passing tests and a separate rerun reproducing the combined CSVs, saved designs, and theorem JSON byte for byte. Those checks occurred within the assisted development session. They are not independent human replication. The experiment runner uses existing NumPy and SciPy; the result verifier and theorem checker use the standard library. No packages, datasets, or model weights were downloaded, and no model inference API calls were made for the study.

The narrower lesson is that the continuous envelope remains uniformly accurate to an additive constant for finite without-replacement pools, while its second-order correction can remain nonzero near census. This analytical statement survives the negative empirical comparisons. Establishing scientific priority, human ownership of the argument, and value on independently collected model outputs remains future work.

## References

[1] OpenAI. *Measuring Goodhart's law* (2022). https://openai.com/index/measuring-goodharts-law/

[2] Watanabe and Roos. JMLR 16, 2357–2375 (2015), Section 2, normalized maximum likelihood. https://www.jmlr.org/papers/volume16/watanabe15a/watanabe15a.pdf

[3] Ricardo Fitas. *The geometry of AI validation: From structural blindness to reusable audits*. arXiv:2608.21496v2 (2026), Section 2.4 and Supplement S2–S4. https://arxiv.org/html/2608.21496v2

[4] Sarkar and Baichoo. *Cheap to Draw, Expensive to Trust: Certifying Test-Time Scaling Curves*. arXiv:2609.40190v1 (2026), Section 7.6 and Appendix C. https://arxiv.org/html/2609.40190v1

[5] Shubhanshu Shekhar, Ziyu Xu, Zachary C. Lipton, Pierre Jinghong Liang, and Aaditya Ramdas. *Risk-limiting Financial Audits via Weighted Sampling without Replacement*. UAI, PMLR 216 (2023). https://proceedings.mlr.press/v216/shekhar23a.html

[6] Larry Mai, with Codex assistance. *ai-goodhart*, release v0.3, commit e589045 (2026). Source, protocols, theorem evidence, and synthetic results. https://github.com/larrymai33/ai-goodhart/tree/e589045
