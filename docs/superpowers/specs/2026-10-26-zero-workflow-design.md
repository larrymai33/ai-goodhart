# A usable zero-only finite-pool audit

The previous turn published v0.4.0 as a5df7d1, including the finite cost theorem and exact cost certificates. The new work closes an adoption gap: the existing CLI implements different acquisition/inference rules. This companion implements the theorem's decision without changing frozen sources, saved evidence, or the older commands. It is not a new experiment or a claim of additional scientific novelty.

The user authorized public repository research, prohibits downloads and 2 GB added storage, chose offline work, confirmed no local model assets, and declined external outreach. No model inference, installation, account messaging, or downloaded data is part of this work.

## Mathematical contract

Use equal fixed pools, a declared target grid containing every power of four through its maximum, threshold 0 < tau <= 1/8, and error probability 0 < delta <= 1/4. Labels are fixed exact numbers in [0,1] under a recorded rubric. The only certificate is that every declared target risk is at most tau. Any positive annotation yields no certificate; missing annotations yield pending unless a positive value already rules out this zero-only certificate. Neither outcome establishes that a target is unsafe. Every selected annotation must be zero to certify; an empty random selection is allowed and must not be redrawn automatically.

Implement a conservative rational version of NEGEXP. Compute certified rational log bounds Llo <= log(1/delta) <= Lhi with a scaled atanh series and outward dyadic rounding. Use q_i=min(1,P5(Lhi*s_i/tau)), with P5(x)=x-x^2/2+x^3/6-x^4/24+x^5/120. Refine until q_i <= min(1,Llo*s_i/tau) for every rank. The resulting probabilities preserve both validity and the factor-160 block-cost proof. Store the exact expected zero-table cost, not a sampled estimate. Document the proof in a new numerical note; do not edit the source-pinned v0.4 theorem.

Sampling uses independent uniform-integer rejection from OS random bits, under the stated ideal-randomness assumption. For q=a/b, draw U uniformly from 0,...,b-1 and include iff U<a. Record every draw as a hexadecimal string. No user-supplied seed option is exposed. The recorded tape makes reporting reproducible; it does not prove the tape was randomly chosen or that no alternative plans were tried.

## Interfaces and ownership

- `goodhart_audit/zero_math.py`: `design_probabilities(m, budgets, P, tau, delta)` returns `(record, tuple_of_Fraction_probabilities_per_rank)`. Exact tau/delta are Fraction objects. Record includes method/version, geometry, canonical budgets, exact tau/delta, log interval and series/rounding metadata, per-item rank envelope masses, rational inclusion probabilities, exact expected zero-table cost, and factor 160. `exact_randbelow(n, bits_callable)` implements unbiased rejection, including n=1 and invalid-source checks. Separate tests in `tests/test_zero_math.py`.
- `goodhart_audit/zero.py`: `make_zero_plan(pools,budgets,threshold,delta,rubric)` and `zero_report(pools,plan,expected_plan_sha256)` plus standalone CLI. Planning uses the existing pool canonicalization/fingerprint, but never source loss fields. Query proxy values are canonical strings so immutable plan JSON has no floats. The plan contains the full random tape and selected query identities, text, and null losses. Its commitment hashes all immutable content with losses normalized to null; reporting requires the externally recorded SHA-256. Separate tests in `tests/test_zero_workflow.py`.
- `docs/zero-workflow.md`, a hand-authored arithmetic pool, and a small arithmetic annotator provide an end-to-end example. They are workflow fixtures, not model outputs or safety measurements.

CLI:

```console
python -m goodhart_audit.zero plan --pool POOLS --out NEW_PLAN --budgets 1,2,4 --threshold 1/10 --delta 1/20 --rubric "Fixed exact loss definition"
python -m goodhart_audit.zero report --pool POOLS --plan ANNOTATED_PLAN --plan-sha256 RECORDED_HASH --out NEW_REPORT
```

Both output paths must be new. Reporting parses annotation JSON with exact Decimal tokens and rejects duplicate object keys, booleans, nonfinite values, and losses outside [0,1]. Only query loss values may change. Positive `1e-400` remains positive. Reports distinguish expected versus realized counts and give the declared assumptions; no per-budget confidence curve is manufactured.

## Resource bounds

The companion is a bounded reference implementation: pool size at most 1,024; at most 100,000 total items; pool size times number of targets at most 250,000; threshold/confidence numerator and denominator at most 256 bits; rational values serialized to decimal fraction strings at most 12,000 bits per numerator/denominator; random draw-width sum at most 64,000,000 bits; input/output JSON at most 64 MiB. Validate resource limits before expensive expansion or file creation. Fail rather than approximate probabilities, silently drop items, or overwrite evidence. These software limits do not narrow the mathematical theorem.

## Acceptance evidence

Tests must precede implementation. Independently enumerate tiny subset risks using exact arithmetic; test rejection sampling including rejected values; check the numerical probability sandwich; test exact-positive annotations, empty/missing/positive/zero outcomes, metadata/tape/commitment tampering, duplicates, and output preservation. Run the actual command-line arithmetic example without site-packages. Verify all earlier source/artifact pins, and independently review the new mathematics and complete workflow. Keep all previous evidence unchanged. Public publication is authorized; external outreach is not.
