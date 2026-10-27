# Related work and claim boundaries

Research snapshot: 2026-10-26. This note records a bounded primary-source search performed before the user selected fully offline work. Subsequent implementation uses no model calls, downloaded datasets, or installed dependencies. The search was selective, not a systematic review, and absence of a match is not evidence of novelty.

## Proposed contribution

This project applies a classical normalized envelope proposal to auditing several best-of-N selection budgets from a fixed, partially labeled candidate pool. Its proposed contributions are a special-family analysis, a reproducible audit implementation, and an empirical comparison of label allocation methods under controlled failure patterns.

Let M be the candidate count per pool, let n range from 1 to N with N <= M, and let r = 1 denote the highest proxy rank. Candidate IDs resolve score ties before sampling. The winner-rank law for a uniformly chosen n-subset is

$$
w_{M,n}(r)=\frac{\binom{M-r}{n-1}}{\binom{M}{n}},
$$

with impossible binomial choices interpreted as zero. Define

$$
e(r)=\max_{1\le n\le N}w_{M,n}(r),\qquad
Z_{M,N}=\sum_{r=1}^{M}e(r),\qquad q(r)=e(r)/Z_{M,N}.
$$

The proposed special-family results are

$$
Z_{M,N}=1+\sum_{n=2}^{N}\operatorname{TV}(w_{M,n},w_{M,n-1}),
$$

and, uniformly for every M >= N,

$$
1+\sum_{n=2}^{N}\frac{(n-1)^{n-1}}{n^n}
\le Z_{M,N}\le H_N=\sum_{n=1}^{N}\frac1n.
$$

Thus the overhead has logarithmic order as N grows. Here TV is half the sum of absolute probability differences. These are statements of the project's proposed analysis, pending independent mathematical review. They are not claims of established originality. Computational checks support an implementation but do not replace a proof.

The primary estimand is the average selected loss conditional on the recorded pools and fixed labels. Neither the combinatorial identity nor the sampling guarantee implies safety on fresh prompts, unseen candidates, another judge, or a changed deployment process.

## What is already established

| Source | Relevant overlap | Boundary for this project |
| --- | --- | --- |
| [Nakano et al., WebGPT, 2021](https://arxiv.org/html/2112.09332) | The rejection-sampling evaluation appendix averages all subsets and reduces evaluation to binomial rank weights. | Exact finite-pool BoN evaluation is prior art. |
| [Gao, Schulman, and Hilton, Scaling Laws for Reward Model Overoptimization, 2022/2023](https://proceedings.mlr.press/v202/gao23h/gao23h.pdf) | Measures divergence between proxy and gold reward under BoN and reinforcement learning in a synthetic feedback setup. | Observing an inverted-U quality curve or reward overoptimization is not a new phenomenon. |
| [Coste et al., Reward Model Ensembles Help Mitigate Overoptimization, 2023/2024](https://arxiv.org/abs/2310.02743) | Tests conservative ensemble objectives and label noise under BoN and PPO. | Uncertainty penalties and conservative reward aggregation are established approaches; this project audits a fixed selector. |
| [Schweisthal et al., Efficient Best-of-N policy evaluation for inference-time alignment, 2026 preprint](https://arxiv.org/html/2610.09250v1) | Uses score-rank probabilities for sample-only evaluation, doubly robust estimation, simultaneous uncertainty, and budget selection. Its large-budget experiments show coverage limitations. | Rank-based inference, simultaneous bounds, and safe budget selection are not new. Our acquisition problem chooses which existing candidate labels to obtain. |
| [Shah and Li, Holdout Best-of-N: Unbiased Evaluation and Its Cost, 2026 preprint](https://arxiv.org/html/2610.08719v1) | Studies selection and evaluation from repeated stochastic judge scores, an unbiasedness frontier, and dependence sensitivity. | A fixed deterministic label audit is different from validating a noisy judge's independent-score assumptions. |

### The envelope is a classical construction

[Shtarkov's 1987 paper](https://www.mathnet.ru/eng/ppi811) is the historical reference for normalized maximum likelihood. The English mathematical statement is accessible in [Watanabe and Roos, 2015, Section 2](https://www.jmlr.org/papers/volume16/watanabe15a/watanabe15a.pdf). Normalizing the pointwise maximum over a distribution family minimizes worst-case logarithmic density ratio. Applying the monotonic logarithm gives the same optimizer for the maximum importance ratio. Consequently, the general identity

$$
\inf_q\max_{n,r}\frac{w_{M,n}(r)}{q(r)}=Z_{M,N}
$$

is an instance of established theory. Z is a Shtarkov sum. The project should say “apply” or “specialize,” not “introduce,” when describing this general minimax construction. The original paper's metadata and abstract were checked; the theorem's accessible English statement was checked in the later paper.

[Langberg and Schulman, Universal epsilon-approximators for integrals, 2010, Section 2](https://www.openu.ac.il/home/mikel/papers/sampling_35_full.pdf), provides another connection: sensitivity sampling selects points in proportion to their maximum normalized contribution across a function family. Its total sensitivity controls sampling error. The normalized rank laws give the same proposal. The unknown loss labels remain an additional factor, so a classical multiplicative coreset guarantee must not be imported without checking its assumptions.

[He and Owen, Optimal mixture weights in multiple importance sampling, 2014](https://arxiv.org/abs/1411.3954), studies proposal mixtures and regret relative to an unknown best proposal. [Roy and Evangelou, Selection of proposal distributions for multiple importance sampling, 2024](https://www3.stat.sinica.edu.tw/statistica/j34n1/j34n102/j34n102.html), includes a minimax variance approach. These motivate mixture baselines and a distinction between minimizing the largest weight and minimizing a particular estimator's variance. Envelope optimality does not imply universal MSE superiority.

### Label-efficient risk evaluation is established

[Sawade et al., Active Risk Estimation, 2010](https://icml.cc/Conferences/2010/papers/285.pdf), selects labels from an unlabeled pool using importance sampling and studies estimation accuracy. [Kossen et al., Active Testing: Sample-Efficient Model Evaluation, 2021](https://proceedings.mlr.press/v139/kossen21a/kossen21a.pdf), develops label acquisition and bias correction for evaluation. [Berrada et al., Scaling Up Active Testing to Large Language Models, 2025](https://arxiv.org/abs/2508.09093), adapts active testing to LLMs with cheaper surrogate models. This project does not invent active evaluation. Its narrower question concerns a label-independent acquisition plan that covers the whole specified BoN budget family using known ranks.

## Nearby work that constrains broader claims

- [Chen et al., Conformal Tail Risk Control for Large Language Model Alignment, 2025](https://arxiv.org/abs/2502.20285), develops calibration with guarantees for distortion risk measures. Generic risk-controlled LLM alignment is already a substantial literature.
- [Wachi, Tanabe, and Akimoto, Safety Hacking in Constrained Best-of-N Inference-time Scaling, 2026 preprint](https://arxiv.org/html/2608.22915v1), studies how selection can amplify unsafe outputs accepted by a proxy safety filter. Rare unsafe tails under increased search are not a new motivation.
- [Fitas, The geometry of AI validation: From structural blindness to reusable audits, 2026, v2](https://arxiv.org/html/2608.21496v2), directly studies envelope acquisition, variance-optimal design, and reusable BoN audits. Section S2 gives the exact continuous-rank integer-budget normalizer used below. The initial release's abstract-only comparison missed this overlap and is superseded by this full-text check. The remaining proposed distinction is the finite without-replacement analysis, not the continuous formula or envelope principle.
- [Landesberg, When LLM Judge Scores Look Good but Best-of-N Decisions Fail, 2026 preprint](https://arxiv.org/abs/2603.12520), distinguishes global score agreement from within-prompt selection quality and tie behavior. Its abstract was inspected. A scorer's overall correlation alone is not a sufficient validation target.

## Search scope and remaining uncertainty

### Follow-up correction, 26 October 2026

[Sarkar and Baichoo, Cheap to Draw, Expensive to Trust: Certifying Test-Time Scaling Curves, 2026, section 7.6](https://arxiv.org/html/2609.40190v1), optimizes a variance-plus-range objective for sufficient fixed-width Bernstein costs and supplies a primal–dual representation. Its broader analysis includes simultaneous BoN inference and adaptive cost bounds. The follow-up implements its objective as an attributed comparator. The fixed-width objective does not itself optimize our distinct-label threshold stopping rule.

[Aslam, Popa, and Rivest, On Auditing Elections When Precincts Have Different Sizes, 2008, section 12](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/), already formulates optimal randomized auditing as a linear program over subsets that hit every dangerous corruption set. Replacing those sets by finite-pool loss sets gives a related all-zero audit benchmark. Neither that generic formulation nor a generic multiscale lower-bound argument is claimed as a contribution here.

The [finite-pool follow-up](sharp-envelope.md) bounds the difference from the established continuous normalizer uniformly, including when the maximum budget equals the pool size. This bounded literature check found no exact match for that remainder statement; it does not establish priority. The [optimized-baseline follow-up](design-report.md) corrects the initial comparison's omission of variance and fixed-width designs.

The search used general web discovery followed by primary paper pages, author-hosted papers, or conference/journal sources. Relevant passages were checked for the rank estimator, the recent BoN evaluation methods, NML, and sensitivity sampling. Several adjacent works were assessed only through abstracts or extracted sections, as identified above. No external paper, repository, dataset, or model file was saved locally.

Query families included best-of-N with “unbiased estimator,” “finite sample,” “confidence bounds,” “audit,” “label budget,” “partial labels,” “importance sampling,” “Shtarkov,” “normalized maximum likelihood,” and “sensitivity sampling”; and broader searches for minimax proposal design, order statistics, hypergeometric laws, and active risk evaluation.

No direct match for the finite without-replacement rank-family TV identity and the stated uniform harmonic bounds was found in this search. This leaves a provisional special-family claim, not a novelty certification. Further checks should include citation tracing, older order-statistics and universal-coding literature, mathematically equivalent formulations, and independent specialist review.

Until those checks and real-data work exist, describe the artifact as a reproducible statistical audit study with a proposed special-family analysis. Do not call it a new general safety guarantee, evidence of frontier-model safety, or a demonstrated improvement in human-aligned behavior.
