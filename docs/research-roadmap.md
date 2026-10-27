# Research roadmap

Latest mathematical status, 2026-10-27: the v0.13 [all-grid theorem](all-grid-minimax-theorem.md) supplies the previously missing finite cost characterization for every nonempty declared best-of-n grid, with loose universal constants. The [companion](cached-likelihood-audit.md) gives a constructive upper bound `C*<=17F` on separated grids. Together the results give a matching sublinear dyadic scaling example. The [report](all-grid-minimax-report.md) separates these theorems from exact finite checks and preserves the stronger v0.12 bound on the original instance. The earlier release discussions below describe the questions open at those releases. Remaining substantive questions include useful original-instance audit constants, realistic label-oracle assumptions, and operational performance beyond synthetic data. Scientific priority and independent human ownership remain unresolved; no external outreach is authorized.

Status: offline research artifact, 2026-10-26. The v0.1 fixed-draw artifact is retained. The v0.2 anytime unique-label extension is implemented and its software checks and full synthetic rerun pass; both result tables reproduce byte for byte. All experimental evidence is synthetic. Real-model experiments have not been run. The future real-model study design below is a draft to preregister before data collection, not an existing preregistration. All current work must remain offline, use available software, avoid downloads and model inference API calls, and stay below the user's 2 GB added-storage limit.

The research question is narrow: how should scarce fixed labels be acquired to estimate every specified best-of-N risk on a recorded candidate pool? The proposed answer specializes classical envelope sampling to winner-rank distributions. [The related-work note](related-work.md) explains which ideas are established and which special-family claims remain provisional.

The v0.3 follow-up strengthens the finite-pool theorem and corrects a material literature-comparison omission. Continuous-rank envelope and optimized audit proposals were already addressed by closer prior work. The [sharp remainder](sharp-envelope.md) is the narrower proposed mathematical distinction. The [new comparison](design-report.md) adds variance-optimal and fixed-width proposals and shows why the envelope cannot be treated as the best default for every objective. The next empirical advance must address evidence beyond previously observed synthetic scenarios; adding more favorable examples would not resolve that gap.

The v0.4 [cost theorem](zero-cost-theorem.md) addresses a different, analytical gap: it compares a classical independent-inclusion audit's expected zero-table cost with all valid adaptive audits for the same whole-family decision. Its proof and exact cost certificates do not add model evidence or extend the earlier engine's guarantee. The user confirmed no additional local model assets are available; the offline constraint remains in force. Independent specialist review and human ownership of the argument remain necessary next milestones.

The v0.4.1 [zero-only workflow](zero-workflow.md) now connects the cost theorem to actual plan creation, annotation, and reporting. Its rational implementation retains the proved cost factor; its hand-authored examples test usability only. This closes the implementation gap for that decision without resolving novelty, model evidence, or independent human ownership. The user has declined external outreach and reports comfort with probability proofs and Python. No outreach is part of the current work; self-reported background is not evidence that the project's arguments have been independently verified.

The v0.5 [arbitrary-grid theorem](sparse-grid-theorem.md) removes the requirement that intermediate powers of four be declared targets. The remaining sufficient condition is inclusion of budget 1; the [boundary example](sparse-grid-theorem.md#7-a-boundary-when-budget-1-is-absent) shows why no condition at all would fail uniformly in confidence. The principal cost limitation remains the all-zero objective. Label reliability and relevance to actual model decisions also remain unresolved.

The v0.6 [sharp-cost theorem](sharp-cost-theorem.md) identifies the optimal leading cost in a dense-population, shrinking-threshold regime for the full budget prefix. Its matching adaptive lower bound is uniform in the growing target family; the design and normalizer coefficient are established. The [exact-check report](sharp-cost-report.md) includes symbolic finite certificates, without expanding those populations or changing CLI resource limits. This closes a leading-constant question in the zero-table problem; it does not solve the nonzero-table limitation.

The v0.7 [structural result](sharp-grid-structure.md) extends that limit to any nonempty declared best-of-N grid and explains why a general decreasing-row version would be false. Its sufficient mechanism combines a representative collection bounded relative to envelope mass, coordinatewise domination, and controlled low-height tails. The [report](sharp-grid-report.md) also quantifies poor zero-only power on a safe nonzero table from the existing synthetic study. This is a scope clarification and boundary result, not a new model experiment or a claim that the practical efficiency gap has closed.

The v0.8 [nonzero minimax theorem](nonzero-minimax-theorem.md) defines one auditor's worst-case cost over tables separated from the threshold by a supplied margin. It gives matching order in the exact grid normalizer and inverse squared margin, with a strong many-prompts condition for the lower bound. The proof can process positive observations; its [finite checks and census example](nonzero-minimax-report.md) make clear that the loose upper construction does not show practical savings. The [prior-art comparison](nonzero-minimax-priority.md) attributes close existing concentration and rare-risk lower-bound mechanisms. Its replication restriction is addressed by the separately proved extension below; the frozen v0.8 sources remain unchanged.

The v0.9 [finite-density theorem](finite-density-theorem.md) replaces that restriction with an explicit maximum-item-weight condition, which can hold with one sufficiently large prompt pool. It uses a common safe-conditioned prior for expected cost and unconditioned product priors for capped transcript information, explicitly bounding both exceptional prior masses. A deterministic prefix upper bound and an exponentially decaying-tail example show why total archive size or positive support size alone cannot give a general census-saturated minimax rate. The [new source comparison](finite-density-priority.md) attributes the line-crossing and monotone-mixture tools. This resolves a sufficient-regime restriction, not the entire finite-population problem. Unknown-margin adaptation, useful operational constants, real-model evidence, and independent human verification remain unresolved.

The v0.10 [finite-saturation theorem](finite-saturation-theorem.md) supplies a matching finite cost formula for every declared grid with `min K>=m/4`, without a density or replication condition. It combines a clipped-weight expression with a deterministic margin-tail cap. A stronger exact-count information lemma and a common fractional safe prior provide its lower bound. The [source comparison](finite-saturation-priority.md) identifies threshold sampling and weighted-query antecedents, including an unresolved 2011 proof-level comparison. The [report](finite-saturation-report.md) makes clear that a restricted-grid prefix example does not certify omitted budgets. General small-budget grids and useful leading constants remain unresolved.

The v0.11 [finite-decision certificate](finite-decision-theorem.md) addresses the numerical gap on the unchanged seven-budget example. An unconditioned fixed-count tail prior is safe for all targets, while a second fixed-count prior is unsafe for budget 1. Classical exact sequential-testing optimization then gives `784.185148748 <= C*(1/160) <= 2048`, placing census within 2.612 of the minimax optimum for this instance. Its [report](finite-decision-report.md) separates that worst-margin-class lower bound from the invalid inference that the relaxed policy is an achievable original auditor. A feasible relaxed policy also bounds every multiplier's certificate for this same prior pair below 809.042; further multiplier tuning alone cannot close the gap. Stronger common-safe hard instances or better globally valid upper bounds are the substantive finite-cost directions. The general all-grid characterization remains open; exploratory singleton and ballot-prior work was not promoted as another contribution. Independent human verification, scientific priority, and model usefulness remain unresolved.

The v0.12 [monotone-placement reduction](monotone-placement-theorem.md) constructs stronger common-safe priors for that unchanged decision. An exchange argument identifies the best arrangement of fixed-zero, uncertain, and fixed-one cells; a latent-subset experiment comparison identifies the largest feasible uncertain block for each count split. The [report](monotone-placement-report.md) evaluates all 193 splits at two specified multipliers, with one separate clean witness proving `C*>1100`. The independent zero-error comparison gives randomized cost between 2,034 and 2,036 and deterministic cost exactly 2,036. A blind-certification mixture supplies the positive-error upper benchmark 1,934.2. These are distinct admissible classes and must not be conflated. The reduction is optimal only within its specified placement class; it does not settle unrestricted prior optimization, an exact positive-error minimax value, or the general all-grid rate. An evidence-based globally valid auditor approaching the lower bound remains a more substantive next target than further multiplier tuning alone.

The literature continuation located a stronger unresolved predecessor: IAEA stratified auditing, including a without-replacement optimality result cited in Avenhaus and Canty's 2007 review. The [priority note](inspection-priority-review.md) records what was read and the unavailable original proof-level comparison. Neither additional exact checks nor another theorem extension can settle that specific historical comparison by themselves. Independent human verification and practical usefulness remain separate gaps; no outreach is authorized.

The continuation also screened fixed-reference comparison audits and a universal pointwise guarantee for nonzero tables. The first transfers the old result by an immediate classical corollary; the second encounters a known testing-versus-verification obstruction. The [attributed limitations note](nonzero-cost-limits.md) records both. A broader useful cost criterion must address that obstruction explicitly. More interfaces, modest constant improvements, or favorable synthetic cases would not resolve priority, independent human ownership, label reliability, or usefulness on actual model decisions. Those remain substantive next milestones under the user's constraints; no external outreach is authorized.

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
