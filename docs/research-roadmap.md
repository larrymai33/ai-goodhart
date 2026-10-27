# Research roadmap

Status: offline research artifact, 2026-10-26. The v0.1 fixed-draw artifact is retained. The v0.2 anytime unique-label extension is implemented and its software checks and full synthetic rerun pass; both result tables reproduce byte for byte. All experimental evidence is synthetic. Real-model experiments have not been run. The future real-model study design below is a draft to preregister before data collection, not an existing preregistration. All current work must remain offline, use available software, avoid downloads and model inference API calls, and stay below the user's 2 GB added-storage limit.

The research question is narrow: how should scarce fixed labels be acquired to estimate every specified best-of-N risk on a recorded candidate pool? The proposed answer specializes classical envelope sampling to winner-rank distributions. [The related-work note](related-work.md) explains which ideas are established and which special-family claims remain provisional.

## Implemented v0.2 extension and remaining work

The unique-label engine and `plan-unique` / `report-unique` workflow sample previously unqueried candidates without replacement and report confidence sequences across all declared budgets and labeled prefixes. The intended guarantee permits stopping at a unique-label quota or based on accumulated evidence, conditional on frozen pools, target masses, and fixed correct labels. The original `plan` / `report` workflow retains its fixed-time, with-replacement interpretation.

The foundation is [Shekhar et al., Risk-limiting Financial Audits via Weighted Sampling without Replacement, UAI 2023](https://proceedings.mlr.press/v216/shekhar23a.html). Their weighted-without-replacement betting martingale is established methodology. The extension specializes it to shared rank-family targets, acquisition, and auditable reporting; it does not claim a new generic confidence-sequence theorem. See [the exact prior-art correspondence](anytime-related-work.md) and [the mathematical note](anytime-theory.md).

The v0.2 synthetic comparison was specified in [anytime_protocol.json](../experiments/anytime_protocol.json), committed as `2095a91` before measurements. This is internal prespecification, not external preregistration. It compares five proposals with the same betting mixture and target-specific normalization, at equal unique-label cost, using eight synthetic scenarios and 100 repetitions per scenario. Outcomes include errors at any observed time, certified-target counts, and censored time to certify the full-pool budget. [The follow-up report](anytime-report.md) records the measurements and limitations. Its cost criterion is the directional upper test (`--rule upper-test`); the public CLI default additionally suppresses certification for empty two-sided intervals.

Implementation checks, scalar/simulation agreement, result provenance, and report review have passed within the assisted development session. Subsequent research still requires independent human reproduction, external mathematical and novelty review, and a separately authorized real-model study. Implementing the stopping-rule extension does not resolve those gaps or demonstrate universal label-cost optimality.

## Milestone 1: establish the mathematical scope

Write complete proofs of the rank law, treatment of ties, envelope minimax identity with attribution, adjacent-law TV identity, and uniform logarithmic-order bounds. Use consistent notation for pool size M, maximum search budget N, audit draw count B, and number of pools P.

The intended special-family statement, for every M >= N, is

$$
Z_{M,N}=1+\sum_{n=2}^{N}\operatorname{TV}(w_{M,n},w_{M,n-1}),
$$

$$
1+\sum_{n=2}^{N}\frac{(n-1)^{n-1}}{n^n}\le Z_{M,N}\le H_N.
$$

Acceptance evidence:

- Proofs cover N = 1, N = M, impossible ranks, and exact ties resolved by a fixed candidate-ID order.
- Exhaustive small-pool enumeration agrees with formulas and the efficient envelope construction.
- An independent mathematical reviewer checks assumptions, constants, and the uniformity in M. Record actual feedback and unresolved objections when review occurs; do not report review in advance.
- A specialist checks the provisional novelty claim against equivalent order-statistic, NML, and sensitivity-sampling results.

The generic normalized-envelope minimax theorem is prior art. Passing computational tests does not establish the special-family proof or its originality.

## Milestone 2: validate an auditable offline workflow

Use immutable pools, a reproducible acquisition plan, a separate unique-label table, and a provenance fingerprint. The acquisition code sees proxy ranks and candidate identifiers, not hidden full-pool losses. Reports must reject mismatched pools and incomplete required labels. Unknown unqueried labels remain unknown.

The v0.1 experiment uses iid audit draws with replacement from a frozen proposal. Repeated indices reuse the same fixed label and still count as repeated statistical draws. Report both draws and unique labels. Its guarantee does not permit silently switching to sampling without replacement or stopping upon reaching a unique-label quota. The separately implemented v0.2 design supplies the different sampling and confidence argument for those uses; it does not retroactively change v0.1's guarantees.

Acceptance evidence:

- Tests check normalization, unbiasedness on exhaustive cases, score ties, invalid inputs, duplicate identifiers, missing labels, provenance mismatches, and extreme budgets.
- Statistical verification tests simultaneous coverage across the entire declared budget grid, not an average of pointwise coverage rates.
- The report distinguishes uncertainty caused by unqueried labels from guarantees about a new population.
- A software reviewer checks that full labels cannot leak into acquisition or estimation and that the implemented confidence statement matches its mathematical assumptions.

For fixed pools and fixed labels, randomness comes from the audit plan. A separate population claim would require a justified sampling design over prompts and candidates. Counting all candidate labels as independent prompts would not provide that justification.

## Milestone 3: complete the synthetic comparison

Freeze scenario definitions, seeds, proposal methods, draw budgets, and evaluation metrics before inspecting comparative results. Include benign rankings, rare extreme-rank failures, interior failure bands, broad failures, flat/random losses, score ties, and prompt heterogeneity. Use fully labeled synthetic pools only in the evaluation harness to compute exact reference curves.

Compare the envelope against uniform candidate sampling, a uniform mixture over budgets, a dyadic budget mixture, and the largest-budget law with a uniform floor. An oracle variance-informed sampler may be reported as an unattainable ceiling. Include scenarios where the envelope loses: it minimizes a worst-case weight criterion, not every label pattern's variance.

For the v0.1 comparison, maximum absolute curve error across the declared search budgets at a fixed audit-draw budget is one of the declared primary metrics. Also report per-budget MSE, integrated curve error, simultaneous interval coverage and width, threshold-certification errors, draw count, unique labels, and runtime. For repeated simulation, report Monte Carlo uncertainty and use paired pools and seeds where appropriate. The v0.2 protocol above separately specifies the anytime, unique-label endpoints; they must not be substituted for the earlier endpoints after viewing results.

Acceptance evidence is reproducible result files plus figures whose conclusions follow the measured endpoints. A negative result against the dyadic mixture is publishable evidence about the proposal's practical limits. Do not select only favorable scenarios or convert synthetic labels into claims about real LLM behavior.

## Milestone 4: external critique and a research note

Prepare a compact note connecting the application, attributed foundations, proofs, software, and all experimental results. Separate proved statements, tested implementation properties, empirical findings, and open hypotheses. Include an explicit claim ledger and the date and limits of the prior-art search.

Before describing the artifact as independently validated, obtain and address actual mathematical and software feedback. Before claiming a new theorem, complete the additional novelty search. A public repository or research note can document provisional work, provided it identifies those limits accurately; it is not equivalent to peer review or evidence of practical safety.

## Future real-model study: draft protocol, not run

This phase is outside the current offline scope. No model queries, payments, dataset downloads, or external outreach are part of the present work. The following design is a concrete starting point to revise and freeze if the user later chooses empirical model work.

### Target and data

Use a bounded, verifiable task domain first, such as small program transformations or generated mathematical tasks with deterministic reference checks. Correctness labels must come from a frozen independent checker and be inspected for checker errors. A proxy scorer may disagree with that checker. This tests selection and audit statistics; it does not by itself measure broad human values or harmfulness.

An initial scale is 24 discovery prompts with 16 candidates each and 64 confirmation prompts with 32 candidates each. Those counts are a planning choice, not a power calculation. Revise them using pilot variance and a resource estimate before confirmation begins. Keep discovery and confirmation prompts disjoint, and freeze the task generator or sampling frame before acquiring confirmation outputs.

Record the generator and scorer versions, date, exact prompts, sampling settings, failed calls, retry policy, candidate order, truncation rules, and scoring rubric. Freeze candidate-ID tie handling. Changes in a provider's model version require a new dataset version. Retain the fixed completed pools as the primary estimand, without assuming that nominally repeated calls prove independence.

The evaluator may obtain full reference labels for these small pools to measure audit error exactly. Store those labels separately from the audit engine. This extra cost belongs to validating the research method and must be distinguished from the simulated partial-label deployment cost.

### Frozen hypotheses and comparisons

Use search budgets {1, 2, 4, 8, 16, 32} for the confirmation pools. A provisional set of aggregate audit draw budgets is {32, 64, 128, 256}; finalize it from discovery data before any confirmation analysis. Use the five acquisition methods from the synthetic study with frozen parameters and the same candidate pools.

This draft retains the v0.1 fixed-draw planning branch. If a future real-model study instead evaluates v0.2, freeze unique-label checkpoints, the exact directional or two-sided certification rule, anytime error endpoints, and censoring rules before confirmation. Compare acquisition proposals using the same inference engine. Choose and preregister that design before collecting confirmation data; the existing synthetic protocol is not a real-model preregistration.

Primary hypothesis: the envelope reduces expected maximum absolute curve error relative to the dyadic mixture at a prespecified draw budget. Treat this as a two-sided comparison until discovery work justifies a directional hypothesis. Report all budgets and comparisons regardless of outcome. Weight minimax optimality does not establish this hypothesis.

Secondary hypotheses concern simultaneous coverage at the declared confidence level, interval width, and risk-threshold decisions. Freeze the threshold before confirmation. “False certification” means certifying a risk below that threshold when the exact risk on the same stored pools exceeds it. It does not mean the experiment measured a real-world safety incident rate.

Use repeated audit plans, for example 1,000 predeclared seeds, to estimate conditional performance on each fixed collection of pools. Pair methods using the same pool collections and document random-number coupling. Estimate uncertainty over those audit repetitions. If reporting variation across newly sampled prompts, add a distinct prompt-level analysis; audit repetitions do not create new independent prompts.

### Cost and failure accounting

Publish generation and scoring calls, tokens when available, paid cost if any, reference-check cost, draws, and unique labels. Caching deterministic labels is allowed, but a fixed-draw estimator must not be advertised as achieving its guarantee after the same number of unique labels under another stopping rule.

Predeclare handling of invalid candidate outputs, malformed scores, tied scores, failed reference checks, and missing labels. Report excluded cases with reasons. Verify a random subset of reference labels manually and inspect high-impact disagreements without changing frozen confirmation labels opportunistically. If labels need correction, publish both dataset versions and rerun every method.

For a later human-quality or safety-label study, replace the executable target with an explicit annotation rubric, independent raters, disagreement reporting, and a justified aggregation rule. That changes the estimand and cost model and needs its own preregistration. An LLM judge's score cannot simply be relabeled “gold human safety.”

## What an application must independently validate

A researcher or user applying this method must establish that the stored candidate universe, proxy ordering, tie rule, and labels match the selection process they intend to audit. They must verify the label oracle's meaning and reliability; the theory cannot certify that a rubric captures the harm they care about.

They must also check the proposal support, logged probabilities, actual draw mechanism, immutable provenance, confidence level, budget grid, and any data-dependent tuning or stopping. An acquisition plan fitted after examining labels requires an analysis appropriate to that dependence. A numerical threshold must have an application-specific justification.

Finally, deployment on new prompts, changed models, new candidate generators, fresh stochastic judge calls, or larger search budgets is a different claim. It requires fresh evidence and suitable sampling or shift assumptions. The present deliverable is an audit of fixed pools and fixed losses, with a transparent route to testing broader usefulness.

Human research ownership also remains to be demonstrated: independently derive the argument, explain its assumptions and failures, reproduce the evidence, and make further validated contributions. Agent reviews and generated artifacts do not establish those steps. [The provenance disclosure](provenance.md) records the assistance and limits; no application or program acceptance is promised.
