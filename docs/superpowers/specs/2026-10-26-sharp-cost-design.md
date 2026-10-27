# Sharp zero-table cost: bounded research specification

The previous release v0.5.0 (`8d3706c`) extended a constant approximation to arbitrary grids containing 1. This continuation screened two tempting nonzero-table directions. The reference-table transfer is a direct corollary of classical comparison auditing. General pointwise instance competitiveness encounters a known testing-versus-labeled-verification obstruction (Grossman, Komargodski, and Naor, ITCS 2020). Neither warrants a new algorithm or standalone novelty claim. The user reports no independent project checks yet and explicitly asked to continue research.

## Selected contribution candidate

For full-prefix budgets 1,...,N, prove a matching first-order expected distinct-label cost against every admissible adaptive auditor at the zero table:

OPT_0 ~ C_NEG ~ L Z_mN / tau when tau tends to zero, rho=L N/(P m tau) tends to zero, and 0<delta<=1/4 (L=log(1/delta)). P, m, N, and delta may vary, with 1<=N<=m. If N also diverges, the existing normalizer theorem gives leading cost L log(N)/(e tau). The contribution candidate is the uniform adaptive-cost lower bound, not NEGEXP, geometric binning, the envelope, or its known 1/e constant. A bounded primary-source search found no directly matching theorem; priority remains unestablished.

## Proof contract

1. A block of d items for which every b-item subset is unsafe imposes E X >= L(d-b)/(b+L), for 1<=b<=d. Prove it from convex interpolation of the hypergeometric miss function and log(1-u)>=-u/(1-u); retain optimized-Python correctness checks.
2. Partition the decreasing rank envelope into maximal consecutive bins with endpoint ratio at most 1+eta. There are J<=1+log(N)/log(1+eta) bins, and the target maximizing at each last rank witnesses the whole bin. Their minimum masses q sum to at least Z/(1+eta).
3. Retain q>=kappa*tau. Put a=N/(P m tau), rho=L*a. For kappa>1+a, the block lemma yields the finite lower bound (L/tau)*(Z/(1+eta)-J*kappa*tau)_+ * [1-(1+a)/kappa]/[(1+a)(1+rho)]. State the trivial-bound cases clearly.
4. Use Z>=1 and Z>=log(N)/e. With eta=tau^(1/3), kappa=1/eta, lost envelope fraction is at most 7eta+eta^2. Every relative error vanishes uniformly when tau,rho tend to zero. Keep delta<=1/4 explicit; rho alone is insufficient if delta tends to one.

The comparator retains correct fixed labels, equal prompt weights, unit query costs, no free gold labels, validity against all fixed tables, and almost-sure zero-table certification. The result does not concern the betting engine, nonzero-instance efficiency, or practical savings at tau=.1. The current coarse universal finite bound is vacuous at that study threshold. Any rational inclusion design within the existing exponential/linear sandwich inherits the mathematical limit; the released CLI keeps its resource caps and gains no new input domain.

## Evidence and constraints

Write a separate proof note and an exact standard-library checker, with tests and a compact saved artifact. The protocol is fixed after exploratory proof checks and before the saved broader run; no external preregistration or empirical holdout is claimed. Check finite hypergeometric inverse comparisons, bin witness conditions, and constructed dense-regime analytical certificates without allocating P*m tables.

For certificates, use rational outward log bounds; round each block lower bound down and the total linear upper bound up to a fixed dyadic scale before serialization, avoiding giant common denominators. Record conservative bounds and symbolic geometry rather than simulated labels. All previous measured sources and pinned proof notes stay unchanged. No new CLI, model calls, downloads, installations, or outreach. Keep storage under 2 GB. Publish only after independent agent proof/code review, exact reproduction, old-evidence integrity, and claim review; this does not complete the broader field-impact or fellowship goal.
