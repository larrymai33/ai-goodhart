# Rank-envelope auditing of best-of-N selection

## Intent

Build a public, reproducible research artifact for measuring reward-selection risk with scarce gold labels. The user delegated research direction and implementation, prohibited downloads, and limited added storage to 2 GB. They subsequently chose fully offline work. Fellowship competitiveness motivates the work; neither acceptance nor scientific impact is a promised outcome.

## Research claim and limits

Apply the established Shtarkov / sensitivity envelope to the family of finite-pool best-of-N winner-rank laws. Prove matching logarithmic-order bounds on its minimax importance-weight overhead across all N <= M. Evaluate practical label allocation, simultaneous uncertainty, and failure cases. Do not claim the rank estimator, importance sampling, NML, or safe budget selection is new. Specific-family novelty is provisional pending external review.

For P fixed pools, each with M candidates ordered by descending proxy score, the target R_n averages loss of the winner of a uniformly chosen n-subset. Labels lie in [0,1]; the label oracle is fixed. Ties use candidate ID order. The primary estimand is conditional on these pools; no iid candidate or population-generalization assumptions are needed or claimed.

## Components

- A standard-library Python package: exact rank probabilities, envelope proposal, unbiased importance estimates, simultaneous empirical Bernstein intervals, partial-identification bounds.
- An offline JSONL workflow: immutable candidate pools, auditable draw plan, separate unique-label table, provenance fingerprint, report. Draws are iid with replacement; repeat queries reuse labels but are still repeated statistical draws.
- Reproducible synthetic benchmark: benign, rare extreme-rank failures, middle-rank failures, and heterogeneous prompts. Compare uniform, uniform budget mixture, dyadic mixture, max-budget plus uniform floor, and envelope. Report risk errors, simultaneous coverage, width, false certification, and unique labels separately from draws. No simulated outputs described as real LLM results.
- A mathematical note, related-work audit, machine-readable results, figures, and research roadmap.

## Implementation choices made by the agent

Python >=3.10. Runtime and tests require only the standard library. Experiment acceleration/plots may use already installed NumPy and Matplotlib; no installation commands or auto-downloads. Use a feature branch in this clean existing repository. Generated files remain well below 2 GB. No external model calls or paid services.

CLI: `python -m goodhart_audit plan --pool PATH --out PATH --draws B --seed S --budgets 1,2,4`; `python -m goodhart_audit report --pool PATH --audit PATH --out PATH --delta 0.05 --threshold 0.1`. Pools use one JSON object per prompt, with `prompt_id`, `candidates` containing unique `candidate_id`, finite `proxy`, optional `loss` and `text`. Each prompt has the same M. `plan` never copies hidden pool labels into its query table. `report` requires every queried label; unknown unqueried labels stay unknown.

## Verification and review focus

Exhaustive subset enumeration versus exact weights; brute-force envelope versus efficient formula; harmonic bounds and envelope-TV identity; negative, nonfinite and fractional parameters; missing/duplicate labels; tied scores; deterministic provenance mismatch rejection; no treating P*M candidate labels as independent prompts; no hidden use of full labels during auditing. Independent mathematical and software reviews precede public release.
