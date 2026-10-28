# Matched total audit budgets: exact benchmark and constructed comparison

The [one-label theorem](audit-budget-theorem.md) gives a sharp cost for
repeated conditional unbiasedness and a schedule attaining it. It does not
say that unbiased gradients improve learned policies. This report tests
that boundary using the categorical policy from the
[cache experiment](audit-cache-experiment.md), with equal expected label
cost across methods.

## Declared comparison

The [protocol](superpowers/plans/2026-10-27-audit-budget.md) specified all
nine settings before this comparison: three learning rates crossed with
three pairs of final group-purchase probabilities. Choices used the earlier
constructed experiment; this is not an external preregistration or a fresh
holdout. No setting was dropped after seeing results.

The policy, weak and full centered advantages, old uniform policy and
clipping interval are unchanged from the earlier experiment. There are
three SGD ascent updates with no momentum, gradient-norm clipping or
stochastic text generation. Each group costs three labels on its first
purchase. The methods are:

- **Reuse:** audit each group once at the first update with probability p,
  then reuse the same inverse-weighted correction for all three updates.
- **Equal time:** use fresh-or-cached correction and spread the unconditional
  probability of first purchase equally over the three updates,
  `q_t=p/[3-(t-1)*p]`.
- **Inverse survival:** use fresh-or-cached correction with
  `q_t=p/[3*(1-p)+t*p]`, the constant-discrepancy schedule from the theorem.

All methods correct the already-clipped group contributions. Thus the
comparison concerns audit timing and reuse; it does not insert corrections
before PPO's minimum. Every method buys a given group with final probability
p. The exact expected costs for the three budget pairs are respectively
9/8, 9/4 and 15/4 labels.

Each method follows its own stochastic parameter trajectory. All audit
branches are enumerated: four complete histories for reuse, sixteen for
each fresh rule. The reference gradient at each node is the full-reference
clipped gradient at the parameters that method actually reached. No
comparison to a different full-audit trajectory is used to compute errors.

## Gradient fidelity and cost

Let e_t denote estimated minus reference raw gradient, as a six-component
vector. The table gives `sum_t E[||e_t||^2]`, with neither division by the
number of parameters nor by the number of updates. Probabilities are exact
fractions; gradients are CPU float64 calculations.

| Learning rate | Final group probabilities | Reuse | Equal time | Inverse survival |
|---:|---|---:|---:|---:|
| 0.05 | (1/4, 1/8) | 7.739572 | 32.182853 | 31.924446 |
| 0.05 | (1/2, 1/4) | 4.102922 | 13.680090 | 13.140141 |
| 0.05 | (3/4, 1/2) | 1.429834 | 5.341132 | 4.380135 |
| 0.20 | (1/4, 1/8) | 5.020085 | 32.319796 | 32.169431 |
| 0.20 | (1/2, 1/4) | 2.628235 | 13.858801 | 13.326841 |
| 0.20 | (3/4, 1/2) | 1.270514 | 5.425059 | 4.482329 |
| 0.80 | (1/4, 1/8) | 4.314701 | 27.580578 | 27.090156 |
| 0.80 | (1/2, 1/4) | 2.088424 | 11.998877 | 10.828442 |
| 0.80 | (3/4, 1/2) | 0.916515 | 4.817145 | 3.385795 |

For both fresh rules, the maximum over settings and rounds of
`E[||E[e_t | history]||^2]` is below 2.11e-32. The residual in the martingale
identity `E[||sum_t e_t||^2]=sum_t E[||e_t||^2]` is below 1.43e-14.

Reuse has smaller total gradient MSE here, but it does not meet the
conditional-unbiasedness requirement. For example, at learning rate 0.8
and probabilities (1/2,1/4), its second-round expected squared conditional
bias is 0.369925, while its marginal gradient bias norm is 0.390734.
Its summed-error MSE is 4.435381, different from its sum of stepwise MSEs
2.088424 because the cross moments do not vanish. The raw JSON retains
both forms of error and both conditional and marginal bias measures.

The inverse-survival rule has lower total gradient MSE than equal time
in these nine settings. This does not extend the constant-discrepancy
optimality theorem to arbitrary adaptive training problems.

## Synthetic reward does not follow from conditional fidelity

For this construction only, define full reward by the full-advantage table
as a one-step bandit: average the policy's expected full reward across the
two groups. Initial reward is zero. The table reports its expectation after
the third update, under each method's full audit tree.

| Learning rate | Final group probabilities | Reuse | Equal time | Inverse survival |
|---:|---|---:|---:|---:|
| 0.05 | (1/4, 1/8) | 0.017287 | 0.022553 | 0.022712 |
| 0.05 | (1/2, 1/4) | 0.026099 | 0.026428 | 0.026404 |
| 0.05 | (3/4, 1/2) | 0.028867 | 0.029160 | 0.029342 |
| 0.20 | (1/4, 1/8) | 0.003518 | 0.018310 | 0.018083 |
| 0.20 | (1/2, 1/4) | 0.038137 | 0.063323 | 0.063713 |
| 0.20 | (3/4, 1/2) | 0.080648 | 0.089093 | 0.090985 |
| 0.80 | (1/4, 1/8) | -0.070317 | -0.085319 | -0.084777 |
| 0.80 | (1/2, 1/4) | 0.027481 | 0.036752 | 0.046840 |
| 0.80 | (3/4, 1/2) | 0.132348 | 0.187920 | 0.204033 |

At the lowest budget and highest learning rate, both fresh rules have worse
reward than reuse, and all three finish below their initial reward. The
inverse-survival rule also does not dominate equal time: it has slightly
lower reward in two settings despite lower total gradient MSE. These are
deterministic calculations over the specified finite trees, not noisy
Monte Carlo rankings or evidence about real language models.

## Reproduction and evidence limits

```powershell
python -B -S -m experiments.check_audit_budget
python -B -m experiments.check_audit_budget --autograd
python -B -m unittest tests.test_audit_budget -v
python -B -O -S -m unittest tests.test_audit_budget -v
```

The exact checker covers 180 schedule/discrepancy cases and 192 nonuniform
precision allocations. Tests compare first-query enumeration with a separate
enumeration of all Bernoulli paths, check error cross moments, and exercise
the two-point lower-bound algebra with nonzero miss baselines. These checks
support examples of the written proof; they do not enumerate all adaptive
algorithms in its minimax statement. Seven tests use only the standard
library; an eighth runs one tensor setting when PyTorch is installed.

All 393 tests on this branch pass with the installed environment. Under
optimized standard-library Python, the seven exact tests pass and the
optional tensor test is explicitly skipped. Normal and optimized execution
produce identical exact-checker output (502 bytes, SHA-256
`1eebdc9c3d9991f4272bf942029e92f3973d526517c181f030ed66a6b5d8e0c6`)
and identical full tensor-comparison output.

The complete [raw comparison](../results/audit_budget/comparison.json) used
installed PyTorch 2.11.0+cu128 on CPU, float64. Its saved local output is
24,357 bytes with SHA-256
`a84e89cd5d6ee2bc3475b3c361504b31c3257e33a6f0dfb8529b55bc8c0ddfa2`.
The hash identifies this output, including its line endings; exact floating
point bytes are not promised across different runtime builds or platforms.
The [manifest](../results/audit_budget/manifest.json) records local runtime
metadata and the generator/dependency hashes for this saved result.

The experiment has no real verifier, language model, changing rollout data,
distributed trainer or human labels. It accounts for a declared synthetic
label cost; it does not measure latency or financial savings. Codex selected
the protocol, wrote the proof and code, executed the comparison and reviewed
the results. Independent agent review remains unavailable and the user has
not independently checked the project. Novelty and practical impact remain
unestablished. No downloads, installations, model calls or outreach occurred.
