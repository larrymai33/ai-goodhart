# Rank Envelope Audits

**Which outputs should receive scarce safety labels when auditing many best-of-N selection budgets?**

This research prototype studies that question for a fixed collection of scored candidate pools. It combines a mathematical analysis, a dependency-free audit tool, and reproducible synthetic experiments. The proposed audit distribution places more probability on ranks that matter to at least one target budget.

**Status:** initial research release; synthetic evidence only. The specific mathematical contribution is a candidate for external review, not an established novelty claim. No real LLM evaluation or deployment safety guarantee is included.

[Research report](docs/report.md) · [Proofs](docs/theory.md) · [Related work](docs/related-work.md) · [Annotation example](examples/README.md) · [Research roadmap](docs/research-roadmap.md)

![Envelope scaling and constructed risk curves](results/theory_and_risks.png)

## The result

Let a pool have $m$ candidates, rank $r=1$ be best, and the policy select the best of a uniformly random subset of $n$ candidates. The established winner-rank law is

$$w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}}.$$

For every budget $n=1,\ldots,N\le m$, audit ranks using the classical normalized envelope

$$q^*(r)=\frac{\max_{n\le N}w_n(r)}{Z_{m,N}},\qquad Z_{m,N}=\sum_r\max_{n\le N}w_n(r).$$

The BoN-specific analysis in this project establishes

$$Z_{m,N}=1+\sum_{n=2}^{N}\operatorname{TV}(w_n,w_{n-1}),$$

$$1+\sum_{n=2}^{N}\frac{(n-1)^{n-1}}{n^n}\le Z_{m,N}\le H_N.$$

Thus the optimal **largest importance weight** grows as Θ(log N), uniformly over $m\ge N$, compared with $N$ for uniform-rank auditing. This is not a minimax label-complexity theorem or a claim of minimum variance on every loss table. The general minimax-envelope identity is established NML/Shtarkov theory; rank-based BoN evaluation and empirical Bernstein bounds are also established. See the [proof and attribution](docs/theory.md).

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

```console
python -m unittest discover -s tests -v
python -m experiments.verify_results
python -m goodhart_audit --help
```

Experiment tests are skipped if NumPy is unavailable; core/workflow tests still run. To rerun the full study with existing NumPy/Matplotlib:

```console
python -m experiments.run_study --out artifacts/local/reproduction
python -m experiments.verify_results --results artifacts/local/reproduction
```

Use `--no-plots` if only NumPy is available. Use a fresh output directory for each configuration. The manifest lists only files generated in that run, hashes the relevant source files and output bytes, and records the protocol and environment. Floating-point or image-byte differences across software versions are possible.

The checked-in study contains 128 prompts × 256 binary labels per scenario. Its generated outputs occupy about 6 MB. This project was built with no dependency/model/dataset downloads and stayed far below its 2 GB storage limit.

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

## Research integrity

The protocol was committed before the experiment; it was not externally preregistered. Independent agent reviews checked the mathematical argument and implementation; these are not human peer review. The initial release was developed with substantial Codex assistance. [Provenance and contribution disclosure](docs/provenance.md) distinguishes recorded work from validation still needed.

Corrections, counterexamples, overlooked prior art, and independent reproductions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Code and project-authored text are MIT licensed; cited works retain their own licenses.
