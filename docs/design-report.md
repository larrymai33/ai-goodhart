# Stronger proposal baselines change the comparison

**26 October 2026. Offline, synthetic follow-up on previously observed scenarios.**

The envelope minimizes the largest importance weight. That objective is useful for a guarantee, but it does not establish the best label cost. This follow-up adds two missing optimized proposals and evaluates them with the same unique-label engine. In the rare-top scenario, median first certification of the largest budget drops from 163 labels for the envelope to 129 for the variance proposal. The updated evidence supports choosing a proposal for a specified objective, not treating the envelope as universally preferable.

The initial literature comparison was incomplete. [Fitas (2026, v2)](https://arxiv.org/html/2608.21496v2) includes continuous-rank envelope and variance designs. [Sarkar and Baichoo (2026), section 7.6](https://arxiv.org/html/2609.40190v1) supplies the fixed-width objective used here. These proposals are attributed comparators. This is not a reproduction of either paper's complete inference pipeline or real-model results.

## What is optimized

For known finite target rows a[k,i], define V_k(q)=sum_i a[k,i]^2/q[i] and W_k(q)=max_i a[k,i]/q[i]. The variance proposal minimizes max_k V_k. The fixed-width proposal minimizes max_k (V_k + rho W_k), with rho=2 epsilon/3=1/48 and epsilon=1/32. These are fixed-draw design objectives. In this experiment, their proposals feed the same without-replacement betting engine used by every baseline; their original fixed-draw confidence procedure is not substituted into that engine.

For numerical verification, each design saves a feasible proposal and simplex weights over the established dual atoms B[(k,i),j]=a[k,j]^2+rho a[k,i]1[j=i]. Their dual value is (sum_j sqrt(sum_atom lambda[atom] B[atom,j]))^2. The feasible objective is an upper bound, and that dual value is a lower bound. The optimizer returns only when the independently recomputed relative gap is within 1e-5. These floating-point brackets are not formal interval-arithmetic certificates.

For the seven declared targets on 64 ranks:

| Proposal | max V | max W | max(V + W/48) |
| --- | ---: | ---: | ---: |
| Uniform | 64.000000 | 64.000000 | 65.333333 |
| Budget mixture | 22.000000 | 64.000000 | 23.333333 |
| Dyadic mixture | 3.527559 | 7.000000 | 3.601050 |
| Max/uniform | 11.461564 | 32.507937 | 12.138813 |
| Envelope | 2.863112 | **2.863112** | 2.922760 |
| Variance optimal | **2.326780** | 4.574166 | 2.402215 |
| Fixed-width optimal | 2.336517 | 4.440723 | **2.385195** |

The final column is a maximum of sums, not the sum of the preceding two column maxima. The numerical relative gaps are 7.63e-8 for variance optimization and 1.56e-7 for fixed-width optimization. [Saved proposals and dual weights](../results/design/designs.json) permit independent recalculation using the standard-library verifier. Identical target columns are grouped during optimization and expanded back to the original candidate coordinates in both the proposal and dual.

## Protocol and reuse

[design_protocol.json](../experiments/design_protocol.json) was committed as 07fea94, with the exact base-manifest pin added as 341a1d3, before new measurements. It fixes the two objectives and reuses the v0.2 scenarios, target budgets, six betting fractions, threshold 0.1, delta 0.05, and 100 paired repetitions. There are 32 prompts and 64 candidates per prompt. Labels are checked at 32, 128, 512, and 1,024 unique queries; error events are checked at every intervening step.

The five original methods contribute 4,000 already published paths; the new methods add 1,600 paths. Together they yield 5,600 method paths and 22,400 checkpoint records from the same 800 independent scenario–replicate streams. These are not 5,600 independent experiments. Generated loss-table hashes and the exponential-race uniforms match the original study. The reused records remain identical, and a pinned manifest ties them to commit 4cdcc11.

This is a follow-up comparison on scenarios whose earlier results were already visible, not an untouched holdout or external preregistration. All proposals see only target masses, never losses. No optimizer parameter was selected by measured certification cost. A separate full rerun reproduced both combined CSVs and the saved designs byte for byte. Earlier measured sources and outputs are unchanged.

The decision rule remains the directional upper test. The CLI's default interval rule can be more conservative on a confidence-failure path, as explained in the [anytime report](anytime-report.md). Neither optimization objective guarantees minimum stopping cost for that test.

## Certification outcomes

At 512 distinct labels, the mean numbers of truly safe budgets certified were:

| Scenario | Truly safe | Envelope | Variance optimal | Fixed-width optimal |
| --- | ---: | ---: | ---: | ---: |
| Rare top | 7 | 7.00 | 7.00 | 7.00 |
| Top failure | 3 | 3.00 | 3.00 | 3.00 |
| Interior band | 4 | 4.00 | 4.00 | 4.00 |
| Bottom band | 6 | 5.87 | 5.93 | 5.92 |
| Flat risk | 0 | 0.00 | 0.00 | 0.00 |
| Goodhart turn | 0 | 0.00 | 0.00 | 0.00 |
| Prompt cluster | 7 | 1.39 | 1.30 | 1.28 |
| All safe | 7 | 7.00 | 7.00 | 7.00 |

The optimized proposals do not dominate every whole-family result. In the prompt-cluster case, the budget-mixture baseline certifies 4.26 safe budgets at this checkpoint, exceeding all three proposals shown above. The small differences in this table are descriptive; they are not claims of statistical significance. [All seven proposals, checkpoints, and Monte Carlo standard errors](../results/design/summary.csv) are included.

In the rare-top case, every nonuniform method certifies the largest budget in all 100 paths by 512 labels:

| Proposal | Median first certification | Successes by 512 |
| --- | ---: | ---: |
| Uniform | Not reached | 0/100 |
| Budget mixture | 93 | 100/100 |
| Dyadic mixture | 200.5 | 100/100 |
| Max/uniform | 103.5 | 100/100 |
| Envelope | 163 | 100/100 |
| Variance optimal | 129 | 100/100 |
| Fixed-width optimal | 129.5 | 100/100 |

The variance proposal's median is about 21% below the envelope's for this one stopping target. The top-focused mixtures are faster still, while certifying fewer budgets at 512 labels. In the all-safe case, medians are 147 for the envelope, 116.5 for variance, and 117 for fixed-width. No universal cost ranking follows from these constructed tables.

The largest observed ever-miscoverage fraction through 1,024 labels is 2/100; no false certifications were observed. This does not establish exact 95% calibration or eliminate implementation risk. A per-setting 95% Wilson interval for 2/100 extends to about 0.070; for 0/100, to about 0.037. Validity relies on the mathematical assumptions, not those finite empirical counts.

## What remains a contribution candidate

The optimized proposal objectives and the generic sequential inference are prior work. The mathematical follow-up is the [uniform finite-pool remainder and joint-limit correction](sharp-envelope.md), assessed against the continuous result. The reproducible software contribution is a shared finite-pool audit implementation with explicit decision rules, provenance, and comparisons that retain counterexamples. External novelty review, independent human replication, practical adoption, and real-model evidence remain absent.

## Reproduction

With the existing NumPy and SciPy installations, use a new output directory:

    python -m experiments.run_design_study --out artifacts/local/design-reproduction
    python -m experiments.verify_design_results --results artifacts/local/design-reproduction

The runner refuses nonempty output directories to protect earlier evidence. The verifier uses only the standard library. The optional optimizer is available as goodhart_audit.design.optimize_design; its input is a matrix of known target probabilities, and its output includes the proposal and numerical bracket. It does not add a new CLI acquisition mode. The v0.1 and v0.2 commands retain their published semantics.

Reproduce the new theorem's computational evidence independently with:

    python -m experiments.check_sharp_envelope --out artifacts/local/sharp-envelope-reproduction.json

This checks 19,900 exact rational cases and reproduces the numerical tables. The [saved theorem evidence](../results/theory/sharp_envelope.json) records its source hashes. Finite tests support the implementation; the written proof establishes the universal statements.
