# Rank Envelope Audits

**Which outputs should receive scarce safety labels when auditing many best-of-N selection budgets?**

This research prototype studies that question for a fixed collection of scored candidate pools. It combines a mathematical analysis, a dependency-free audit tool, and reproducible synthetic experiments. The proposed audit distribution places more probability on ranks that matter to at least one target budget.

**Status:** version 0.4 research prototype; mathematical analysis and synthetic evidence. The specific mathematical contributions are candidates for external review, not established novelty claims. No real LLM evaluation or deployment safety guarantee is included.

[Research report](docs/report.md) · [Sharp finite-pool result](docs/sharp-envelope.md) · [Proofs](docs/theory.md) · [Related work](docs/related-work.md) · [Annotation example](examples/README.md) · [Research roadmap](docs/research-roadmap.md)

**New: a finite-table cost approximation theorem.** When every candidate's loss is zero, the classical multi-target NEGEXP audit uses at most **160 times** the optimal expected number of distinct labels among all valid adaptive audits in the stated class. The theorem requires equal fixed pools, a predeclared whole-family decision, a budget grid containing every power of four through its maximum, risk threshold at most 1/8, and error probability at most 1/4. It includes the transition toward a full census. [Complete proof and assumptions](docs/zero-cost-theorem.md).

The factor is deliberately loose. For the existing geometry of 32 pools of 64 candidates, seven dyadic budgets, threshold 0.1, and error probability 0.05, exact rational certificates bound the design's expected zero-table cost within **1.398 times** the adaptive optimum. These are analytical bounds, not measured model performance. They concern a different decision and design from the published six-bet confidence-sequence engine. [Cost certificates and reproduction](docs/zero-cost-report.md).

**Earlier standalone research note:** [seven-page PDF](paper/paper.pdf) · [Markdown source](paper/paper.md) · [review guide](docs/review-guide.md). It consolidates the frozen v0.3 evidence and substantial AI-assistance disclosure; the new cost theorem is in the linked follow-up note. The earlier scientific sources and results are preserved.

**New: sharper finite-pool theory and stronger baselines.** The [latest follow-up](docs/design-report.md) adds attributed variance-optimal and fixed-width proposals, correcting the initial comparison's omission. In the rare-top scenario, the variance proposal certifies the largest budget after median 129 unique labels versus 163 for the envelope. Other proposals are faster for that single target; whole-family comparisons also have counterexamples.

The anytime implementation queries each candidate at most once and supports stopping after any labeled prefix. The [workflow](docs/anytime-report.md) and [attributed proof](docs/anytime-theory.md) describe its established weighted-without-replacement foundation. The combined comparison has 5,600 method paths from 800 independent scenario–replicate streams, including 4,000 previously published paths. It is a synthetic follow-up on known scenarios, not a fresh holdout.

![Envelope scaling and constructed risk curves](results/theory_and_risks.png)

## The result

Let a pool have $m$ candidates, rank $r=1$ be best, and the policy select the best of a uniformly random subset of $n$ candidates. The established winner-rank law is

$$w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}}.$$

For every budget $n=1,\ldots,N\le m$, audit ranks using the classical normalized envelope

$$q^*(r)=\frac{\max_{n\le N}w_n(r)}{Z_{m,N}},\qquad Z_{m,N}=\sum_r\max_{n\le N}w_n(r).$$

The finite without-replacement analysis establishes

$$Z_{m,N}=1+\sum_{n=2}^{N}\operatorname{TV}(w_n,w_{n-1}),$$

$$0\le Z_{m,N}-L_N\le\frac{N-L_N}{m+1}<1.$$

Here $L_N=1+\sum_{n=2}^{N}(n-1)^{n-1}/n^n$ is the established continuous-rank normalizer. Thus $Z_{m,N}=(\log N)/e+O(1)$ uniformly over $m\ge N$, including $m=N$. The [new proof](docs/sharp-envelope.md) also gives the second-order correction as $N/m$ varies.

This bounds the optimal **largest importance weight**, compared with $N$ for uniform-rank auditing. It is not a minimax label-complexity theorem or universal variance claim. The continuous normalizer and score-based envelope audits already appear in [Fitas (2026, v2)](https://arxiv.org/html/2608.21496v2); the general minimax identity is classical NML theory. The initial abstract-only literature comparison missed that overlap and has been corrected. The proposed mathematical distinction is the finite-pool remainder and joint-limit profile, with novelty still subject to external review.

## What the experiments show

Eight synthetic fixed-pool scenarios, five acquisition methods, four draw counts, and 200 repetitions produce **32,000 audit evaluations**. Methods and draw counts share random numbers: there are 1,600 independent scenario–replicate streams, not 32,000 independent experiments.

For 256 candidates and nine target budgets, the maximum importance weight is **3.362** for the envelope, **9** for a dyadic mixture, and **256** for uniform sampling. The full 256-budget envelope constant is **3.395**, a different quantity.

At 256 draws, mean squared error averaged over the nine risk budgets was:

| Constructed loss pattern | Uniform | Dyadic mixture | Envelope |
| --- | ---: | ---: | ---: |
| Top-ranked candidate always fails | 0.145185 | 0.002385 | 0.001497 |
| Same failure prevalence at every rank | 0.025739 | 0.001118 | 0.001077 |
| Bottom quarter of ranks fail | **0.000102** | 0.000736 | 0.000417 |

The envelope wins some comparisons and loses others. A proposal concentrated on the top rank beats it on the top-only scenario. Comparisons use equal **fixed draws**, with unique-label costs reported separately; they do not establish superiority at equal unique annotation budgets.

The valid bands covered all nine true risks in 200/200 repetitions in each setting, and were conservative. This is not evidence of exact 95% calibration. For one setting, 200/200 has a 95% Wilson interval of approximately [0.981, 1]. Full metrics, Monte Carlo uncertainty, negative results, and assumptions are in the [report](docs/report.md).

![Estimation tradeoffs](results/estimation_tradeoffs.png)

## Run without installation

Python 3.10+ is sufficient for the core, CLI, and result-integrity check. The synthetic runner additionally uses NumPy and Matplotlib if already installed. Nothing downloads models, datasets, packages, or other artifacts.

Verify the v0.1-v0.3 saved evidence with the standard library, or rerun those numerical studies with already-installed NumPy and SciPy:

```console
python -m experiments.reproduce --verify-only
python -m experiments.reproduce --out artifacts/local/full-reproduction
```

Verification checks saved artifacts and source integrity; it does not recompute results or prove theorems. Full mode requires a new output directory, runs the tests, regenerates all three numerical studies and the exact theorem checker, and compares ten numerical artifacts byte for byte. It preserves published results and writes a diagnostic report. Figures and manifest bytes are excluded from regeneration/comparison; software-version differences may produce a reported mismatch. The [paper build](paper/README.md) is separate.

The v0.4 cost theorem has a separate standard-library check and exact rational cost certificates. Its command and scope are documented in the [cost report](docs/zero-cost-report.md). The older reproduction command retains its ten-artifact comparison; it does not silently include this new follow-up.

```console
python -m unittest discover -s tests -v
python -m experiments.verify_results
python -m experiments.verify_anytime_results
python -m experiments.verify_design_results
python -m goodhart_audit --help
```

Experiment tests are skipped if NumPy is unavailable; core/workflow tests still run. To rerun the full study with existing NumPy/Matplotlib:

```console
python -m experiments.run_study --out artifacts/local/reproduction
python -m experiments.verify_results --results artifacts/local/reproduction
```

Use `--no-plots` if only NumPy is available. Use a fresh output directory for each configuration. The manifest lists only files generated in that run, hashes the relevant source files and output bytes, and records the protocol and environment. Floating-point or image-byte differences across software versions are possible.

The checked-in study contains 128 prompts × 256 binary labels per scenario. Its generated outputs occupy about 6 MB. This project was built with no dependency/model/dataset downloads and stayed far below its 2 GB storage limit.

The additional anytime study uses 32 prompts × 64 candidates per scenario. Reproduce it with:

    python -m experiments.run_anytime_study --out artifacts/local/anytime-reproduction
    python -m experiments.verify_anytime_results --results artifacts/local/anytime-reproduction

The optimized-proposal follow-up additionally needs existing SciPy. Its verifier and theorem check use only the standard library. Choose a new output directory for each run:

    python -m experiments.run_design_study --out artifacts/local/design-reproduction
    python -m experiments.verify_design_results --results artifacts/local/design-reproduction
    python -m experiments.check_sharp_envelope --out artifacts/local/sharp-envelope-reproduction.json

## Audit your own fixed pools

Provide JSONL with `prompt_id` and a `candidates` list containing `candidate_id`, `proxy`, and optional `text`. All pools must have the same size. Proxy scores determine descending order; equal scores use ascending candidate ID. See [the example and schema](examples/README.md).

```console
python -m goodhart_audit plan --pool examples/pools.jsonl --out artifacts/local/audit.json --draws 32 --seed 7 --budgets 1,2,4
```

Fill only `queries[].loss` with independently assigned values in [0,1], then:

```console
python -m goodhart_audit report --pool examples/pools.jsonl --audit artifacts/local/audit.json --out artifacts/local/report.json --delta 0.05 --threshold 0.1
```

Each report contains an unbiased importance estimate, simultaneous empirical Bernstein bounds, sharp missing-label bounds, and individually certified budgets. Certification concerns **these exact pools and the declared loss definition**. It does not validate the labeler, cover new prompts, extend beyond the pool size, support optional stopping, or prove that every budget below the largest certified one is safe.

That restriction on stopping applies to the original commands above. The new plan-unique and report-unique commands use an explicitly anytime-valid design. [The follow-up guide](docs/anytime-report.md#use-the-workflow) explains contiguous-prefix labeling and the two available certification rules.

## Research integrity

The protocol was committed before the experiment; it was not externally preregistered. Independent agent reviews checked the mathematical argument and implementation; these are not human peer review. The initial release was developed with substantial Codex assistance. [Provenance and contribution disclosure](docs/provenance.md) distinguishes recorded work from validation still needed.

Corrections, counterexamples, overlooked prior art, and independent reproductions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Code and project-authored text are MIT licensed; cited works retain their own licenses.
