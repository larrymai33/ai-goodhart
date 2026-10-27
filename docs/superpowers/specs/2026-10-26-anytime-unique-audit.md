# Anytime auditing with one new label per draw

## Why this extension

The initial release does not support stopping at a unique-annotation budget or upon favorable evidence. Resolve that practical limitation directly, while retaining the finite-pool estimand, bounded fixed labels, offline-only constraint, no downloads, and <2 GB added storage.

## Scientific scope

Specialize established weighted-sampling-without-replacement betting confidence sequences (Shekhar et al., UAI 2023) to simultaneous best-of-N risk targets. The general martingale method is prior art. The contribution is a rank-aware, score-only acquisition design and auditable implementation, with a comparison at equal numbers of genuinely new labels.

For fixed target masses a[n,i] and base proposal h[i], sample unseen item i proportionally to h[i]. Let H be remaining proposal mass, D_n=max_unseen a[n,i]/h[i], c_n=H D_n, and A_n the previously observed weighted loss. The next Y_n=a[n,i]loss/(h[i]D_n) has conditional mean (R_n-A_n)/c_n and lies in [0,1]. Use a fixed uniform mixture over fractions gamma=1,1/2,...,1/32. Upper-test factors are 1-gamma+gamma(1-Y)/(1-m); lower-test factors are 1-gamma+gamma Y/m. Endpoint 0/0 under a feasible candidate is defined as factor 1. Invert wealth at 2K/delta, restricted to nested deterministic missing-label bounds. The resulting intervals cover every target at every sample size with probability >=1-delta. They allow data-dependent stopping. Candidate means and ranges must be validated before division; no inferred population guarantee.

## Implementation decisions

- Keep the first release and result files intact.
- Add a standard-library FinitePoolAudit engine accepting target probability vectors, a fixed proposal, confidence level, and frozen bet fractions. observe(index, loss) accepts each supported item once. bounds() returns target-indexed intervals and partial-identification bounds. log_wealth(target, candidate, direction) supports independent checks and diagnostics.
- Generate a complete weighted-without-replacement acquisition prefix by an exponential race, fixed from scores and a seed. A partial report accepts only a contiguous labeled prefix, so unseen labels cannot affect the displayed result.
- Add CLI commands plan-unique and report-unique. Existing commands and fixed-time semantics stay intact.
- All proposals use the same fractional betting mixture, target-wise predictable scale, and deterministic bounds. Primary comparison is acquisition at equal unique labels.
- Preserve source/protocol/result hashes and report endpoint limitations, numerical approximations, and actual human/agent validation.

## Prespecified study

Reuse the eight synthetic scenario definitions at P=32, m=64; 100 repetitions each; five existing proposal families; target budgets 1,2,4,8,16,32,64; maximum 1,024 new labels from 2,048 candidates; checkpoints 32,128,512,1024; delta=0.05; threshold=0.1. Primary outcomes: ever missing any true target across all observed times, ever falsely certifying a target, certified-target counts at equal unique-label checkpoints, and label counts to certify the declared full-pool budget (with unachieved results censored at the maximum, not counted as achieved). Record known-safe and known-unsafe targets only in evaluation, never acquisition.

The confidence analysis is evaluated at the true risks and threshold using incremental wealth; inversion is tested independently against the public engine. Methods share exponential-race uniforms within each scenario/replicate. There are 800 independent scenario-replicate streams and 4,000 paired method runs, not 4,000 independent trials. All evidence is synthetic.

## Verification

Exhaustively enumerate tiny-pool orders and binary label tables; verify mean-one wealth at the true risk, time-uniform failure bounds, one-label-per-query, exact exhaustion, constant fractional labels, endpoint behavior, zero-support/duplicate/input rejection, monotone inversion, optional stopping, hidden-label isolation, and scalar/vectorized conformance. Check the concrete design against primary prior art before implementation claims. An independent agent reviews theory, code, and claims before publication.
