# Anytime auditing: prior art and extension boundary

Research snapshot: 2026-10-26. This is a bounded primary-source literature check for a proposed extension of the fixed-draw audit. It does not establish novelty. Papers were read through web tools; no paper, package, dataset, or model was downloaded to the workspace. The implementation and experiments remain offline.

## Exact overlap: weighted sampling without replacement

[Shekhar, Xu, Lipton, Liang, and Ramdas, Risk-limiting Financial Audits via Weighted Sampling without Replacement, UAI 2023](https://proceedings.mlr.press/v216/shekhar23a/shekhar23a.pdf), Section 2, Definition 2 and Theorem 1, already constructs confidence sequences for fixed weighted totals under predictable sampling from remaining items. Its process uses

$$
Z_t=\frac{\pi(I_t)f(I_t)}{q_t(I_t)},\quad
\mu_t(m)=m-\sum_{j<t}\pi(I_j)f(I_j),\quad
W_t(m)=\prod_{j\le t}\{1+\lambda_j(m)[Z_j-\mu_j(m)]\}.
$$

Admissible bets keep the process nonnegative, and Ville's inequality supplies validity over time. Section 3's proportional-to-weight sampler minimizes the worst-case observation range for one target. The paper also develops predictable approximate-Kelly bets and control variates for side information. This is the direct methodological precedent, not merely an analogous application.

For the proposed rank audit, substitute target mass a_n(k) for pi(k) and fixed loss y_k for f(k). With remaining set U_t, envelope s(k) = max_n a_n(k), C_t = sum over U_t of s(k), and q_t(k) = s(k)/C_t, define

$$
A_{n,t-1}=\sum_{j<t}a_n(I_j)y_{I_j},\quad
Y_{n,t}=\frac{a_n(I_t)y_{I_t}}{s(I_t)},\quad
m_{n,t}(\mu)=\frac{\mu-A_{n,t-1}}{C_t}.
$$

Then E[Y_{n,t} | history] = m_{n,t}(mu_n). For 0 < m < 1, the implemented fractional bets give lower-direction factors 1 + (gamma/m)(Y - m) and upper-direction factors 1 - (gamma/(1 - m))(Y - m). These are the preceding weighted-audit process after rescaling Z_t = C_t Y_{n,t}, with lambda_lower = gamma/(C_t m) and lambda_upper = -gamma/[C_t(1 - m)]. The more general target-specific normalization below replaces C_t by b_{n,t}; boundary cases need explicit handling. This algebraic identification is our comparison of the formulas, not a new generic confidence-sequence theorem.

## Other foundations and nearby extensions

- [Waudby-Smith and Ramdas, Confidence sequences for sampling without replacement, NeurIPS 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/e96c7de8f6390b1e6c71556e4e0a4959-Paper.pdf), develops time-uniform finite-population inference, including Hoeffding and empirical-Bernstein constructions. Its finite-population setting concerns fixed values and random observation order.
- [Waudby-Smith and Ramdas, Estimating means of bounded random variables by betting, JRSS B 2024](https://arxiv.org/html/2010.09686), Section 5.2, equations (32)-(34), centers observations at the remaining mean (L mu minus the observed sum)/(L minus the observed count). Proposition 4 and Theorem 4 establish betting and hedged confidence sequences for uniform sampling without replacement. Predictable betting, mixtures, and anytime validity are established foundations.
- [Xu, Karampatziakis, and Mineiro, Active, anytime-valid risk controlling prediction sets, NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/file/6eb05d8bc6bd7bb6868c64b5802125bd-Paper-Conference.pdf), combines active label acquisition, inverse-probability correction, predictors, and sequential risk guarantees. Its incoming-data/prediction-set setting differs from this fixed ranked pool; active anytime risk control itself is not new.
- [Ryu and Wornell, Gambling-Based Confidence Sequences for Bounded Random Vectors, ICML 2024](https://proceedings.mlr.press/v235/ryu24a.html), supplies vector-valued gambling constructions and a without-replacement application. Joint inference can improve on coordinatewise methods in its setting. Our union bound across budgets is a simple valid construction, not an optimal use of dependence.
- [Csillag, Struchiner, and Goedert, Prediction-Powered E-Values, 2025](https://arxiv.org/abs/2502.04294), provides related prediction-assisted sequential inference. Only its abstract and selected passages were checked; no claim of technical equivalence is made here.

## Assumptions and valid construction

The following is a proposed specialization of those methods. Let each target be mu_n = sum_k a_n(k)y_k, with known nonnegative masses summing to one and fixed labels in [0,1]. The candidate universe and target family must be fixed before the audit. At step t, q_t is determined before drawing I_t, has support on every remaining item with positive relevant mass, and removes each queried item. Labels are revealed faithfully; repeated noisy judgments are a different model.

For any such proposal, a useful general normalization is

$$
b_{n,t}=\max_{k\in U_t}\frac{a_n(k)}{q_t(k)},\quad
Y_{n,t}=\frac{a_n(I_t)y_{I_t}}{q_t(I_t)b_{n,t}},\quad
m_{n,t}(\mu)=\frac{\mu-A_{n,t-1}}{b_{n,t}}.
$$

This gives Y in [0,1] and the required conditional mean. For the envelope proposal, b_{n,t} <= C_t, so the common C_t normalization is valid but may be looser. Apply the same normalization rule to every comparator.

For feasible candidate means 0 < m < 1, bets gamma/m and -gamma/(1-m), with 0 <= gamma <= 1, give nonnegative lower- and upper-direction factors. They are predictable for each fixed candidate mu. A fixed normalized mixture over gamma values such as {1, 1/2, 1/4, ...} is valid; a finite declared grid is practical. The gamma = 1 component can reach zero, which must be handled correctly in log-space calculations. At m = 0 or m = 1, use explicit boundary logic rather than division by zero. An observation contradicting a degenerate candidate null excludes it; an observation consistent with that null can use a unit factor at that step.

Intersect with the deterministic feasible interval

$$
\left[A_{n,t},\ A_{n,t}+\sum_{k\in U_{t+1}}a_n(k)\right].
$$

It always contains the fixed target. At exhaustion, return its singleton exactly without evaluating a zero denominator. If a target has no remaining positive mass, it is already known even if other targets are not.

For K predeclared target budgets, a two-sided mixture with initial wealth one per target and threshold K/delta, followed by a union bound over targets, gives simultaneous coverage across targets and times. Alternatively, separate directional processes use threshold 2K/delta. Ville handles all times; an additional time union bound is unnecessary. Running intersections retain validity. Numerical inversion must conservatively enclose the acceptance set; retaining only accepted grid points is not by itself a confidence interval for arbitrary real-valued means.

## Comparators and the claim worth testing

Use the same bets, mixture weights, inversion precision, target error allocation, and deterministic feasible intervals for:

1. Uniform sampling without replacement.
2. A dyadic-budget mixture restricted and renormalized over remaining candidates.
3. Rank-envelope sampling without replacement.

The study compares certification by the directional upper test. The public tool's default also suppresses certification when the two-sided interval is empty. Reproducing the study's label-cost counts therefore requires the explicit upper-test CLI option planned for this extension; these counts must not be presented as default-mode costs.

A target-matched single-budget proportional-to-weight audit is an informative specialized comparator. It knows which target matters, not the losses. Report that distinction and its cost honestly: several separate target audits cannot each receive the entire multi-target label budget for free. If labels are shared, report the union of unique queried items and the evidence used by each process.

For continuity with v0.1, a fixed-time with-replacement method may use predeclared alpha spending at its reporting times. It is a conservative baseline, with duplicate draws and unique labels reported separately. Comparing a new betting interval only with an older Bernstein interval would confound the acquisition policy, replacement rule, and uncertainty method.

The empirical question is whether one shared rank-envelope audit achieves useful simultaneous curves with fewer unique labels than these alternatives, and where its cost of covering several budgets outweighs the benefit. The claim is not minimax variance or universally optimal stopping time. Generic weighted-WoR confidence sequences, proportional-to-weight sampling, fraction bets, mixtures, and union bounds are prior art. Any additional contribution must come from the rank-family analysis, implementation, or demonstrated cost tradeoffs. This targeted search found no exact prior treatment of that combined rank-family application; this remains provisional and requires independent review.
