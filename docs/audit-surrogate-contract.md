# Verifier audit corrections through clipping and repeated updates

An unbiased estimate of a reference advantage does not automatically yield
an unbiased estimate of its clipped training objective. Even correcting the
objective itself does not justify reusing the same audit draw after that draw
has changed the policy. This note gives exact identities and counterexamples
for those two distinct effects, plus a conditional correction rule.

The results concern a **fixed batch and its reference clipped surrogate**.
They are not guarantees about the policy's true expected reward, training
performance, or reduced reward hacking. They use classical inverse-probability
correction, elementary convexity and conditional expectation. Novelty and
independent correctness have not been established.

## 1. Fixed-state clipping creates an exact additional penalty

Write the maximized PPO integrand as

```text
ell(r,A) = min(r A, clip(r,1-e,1+e) A),   r>0, 0<e<1.
```

This is the standard clipped objective from
[Schulman et al. (2017), Section 3](https://arxiv.org/pdf/1707.06347).
Here r is the current-to-sampling-policy probability ratio. All advantages
and audit probabilities below are held fixed when taking derivatives.

Suppose an integrable random advantage Ahat has E[Ahat]=f. Let x_+=max(x,0)
and define

```text
D = E[(Ahat)_+] - f_+ >= 0,
dist(r) = (r-1-e)_+ + (1-e-r)_+.
```

If the ratio is fixed independently of this audit draw, then exactly

```text
E[ell(r,Ahat)] = ell(r,f) - D dist(r).                 (1)
```

Thus an unbiased advantage inserted into clipping optimizes, in expectation,
the full-reference clipped objective with an additional nonnegative penalty
outside the clipping interval. This is a difference from the reference
**clipped** objective, not merely PPO's familiar difference from an
unclipped policy-gradient objective.

**Proof.** Directly by the two signs of A,

```text
ell(r,A) = r A - (r-1-e)_+ A_+ - (1-e-r)_+ (-A)_+.
```

Since A_+-(-A)_+=A and E[Ahat]=f, the excess expectation of each positive-part
term is the same D. Jensen's inequality gives D>=0, proving (1).

Away from the clip knots, the corresponding derivative error with respect
to r is -D above the upper knot, +D below the lower knot, and zero inside.
For a differentiable ratio r(theta) fixed before the audit draw, multiply
by its gradient. For a batch with fixed nonnegative aggregation weights,
sum (1) termwise. Independence between different groups is unnecessary for
this expected-objective identity. The D values are conditional on the batch
and the audit design; they are not free learned regularization parameters.

In particular, the discrepancy vanishes at the sampling policy r=1, both
in value and locally in raw gradient. This calculation does not contradict
a theorem restricted to that state.

### Group audit specialization

Let w be the weak advantage, f the full-reference advantage, and
Z~Bernoulli(q), with 0<q<=1. The familiar group correction is

```text
Ahat = w + (Z/q)(f-w).
```

Then E[Ahat]=f, but

```text
D = (1-q) w_+ + [f-(1-q)w]_+ - f_+
  = [(1-q)|w| + |f-(1-q)w| - |f|]/2.                 (2)
```

For 0<q<1, D is positive exactly when the two possible corrected advantages
have strictly opposite signs. It is zero if one is zero or their signs
agree. If w and f have opposite nonzero signs, D=(1-q)|w|: reducing the
audit rate need not make this penalty small. Formula (2) also covers f=0,
w=0 and q=1 without a sign convention.

For example, w=1, f=-1, q=1/4 gives Ahat=1 or -7. At r=3/2 and e=1/5:

| Quantity | Correct advantage inserted before clipping | Full reference |
| --- | ---: | ---: |
| Expected advantage | -1 | -1 |
| Expected maximized surrogate | -69/40 | -3/2 |
| Expected derivative with respect to r | -7/4 | -1 |

Here D=3/4 and dist(r)=3/10. No approximation or Monte Carlo is involved.

## 2. Correcting after clipping fixes this fixed-state discrepancy

For the same audit probability, define

```text
Lhat(theta) = Lw(theta) + (Z/q)[LF(theta)-Lw(theta)],   (3)
```

where Lw and LF are the entire weak and full-reference group surrogate
contributions, each including its own clipped terms. At a state independent
of the current audit draw, E[Lhat]=LF and E[gradient Lhat]=gradient LF,
where the gradients exist. For finite Bernoulli outcomes, this follows by
differentiating the two deterministic branches and averaging.

The order matters: applying the correction to the already-clipped objective
is generally different from supplying a corrected advantage to one clipped
objective. In the numeric example, (3) has expected surrogate -3/2 and
expected ratio derivative -1. This is a direct application of classical
inverse-probability correction, not a new unbiased-estimation principle.

Equation (3) is a conditional target, not a recommendation to remove stability
controls. A realized corrected objective need not retain PPO's pessimistic
lower-bound property; its weak term can have a negative coefficient.
Its variance can be large. Gradient-norm clipping, Adam and other nonlinear
operations after this gradient can still change its expected parameter step.
We neither benchmark nor claim a training advantage for (3).

## 3. Reusing the audit draw breaks a different condition

Pointwise unbiasedness at every fixed theta does not imply unbiasedness at
a theta that depends on the same Z. This can fail even when all ratios stay
strictly inside the clipping interval and (1)'s penalty is identically zero.

Consider the valid two-action policy

```text
pi_theta(1)=theta^2/2, pi_theta(2)=1-theta^2/2,
0<theta<sqrt(2), theta_old=1.
```

Condition on a batch containing each action once. Both weak rewards are 1,
so their centered advantages are (0,0). Full-reference rewards (-1,1) give
centered advantages (-1,1). The current ratios are theta^2 and 2-theta^2.
Use q=1/2, e=1/5 and gradient ascent step size eta=1/100.

Locally the full-reference mean surrogate is LF(theta)=1-theta^2, with
gradient -2 theta. Both advantage-level and objective-level corrections
here give Lhat=(Z/q)LF; sign changes and ratio clipping play no role.

Starting at theta_0=1, the first corrected gradient is 0 or -4. Hence
theta_1 is 1 if Z=0 and 24/25 if Z=1. Every second-step ratio lies strictly
between 4/5 and 6/5. If the same Z is reused,

```text
E[gradient Lhat(theta_1)] = -48/25,
E[gradient LF(theta_1)]   = -49/25.                   (4)
```

The discrepancy is 1/25. The first gradient was unbiased, and no active
ratio clipping, group renormalization, Adam, gradient-norm clipping or
stochastic label noise is present. The issue is dependence between the
parameter and the audit draw. The target on the right is the full-reference
gradient **at the random states actually visited**, not at a different
counterfactual full-audit trajectory.

## 4. A conditional rule for repeated updates, with its label cost

Assume each group's full-reference label vector is fixed throughout the
batch's optimizer updates. At update t, condition on all earlier history,
including theta_t, past draws and cached labels. For each group:

1. If its full labels are already cached, use its full-reference group
   objective LF directly, without its old inverse-probability multiplier.
2. Otherwise choose q_t>0 from the available history, draw a new Bernoulli
   indicator with that conditional probability, and apply (3) to the
   group objective. Purchase and cache the full labels only if selected.

Conditional on history, each raw group gradient has expectation equal to
the full-reference gradient at theta_t. In the uncached branch this is
E[Z_t/q_t | history]=1; in the cached branch it is an equality without
randomness. The probability is a sampling-design input and must be detached
from autodifferentiation, as must the reference advantage and sampling policy.
Differentiating through q_t while omitting the audit draw's score term would
be a different estimator.

In the two-action example, this rule's second expected gradient is -49/25.
Its expected number of distinct group audits across the two updates is 3/4,
compared with 1/2 for the original single draw. More generally, with a constant
q and T updates, a previously uncached group is purchased with probability
1-(1-q)^T. If its full audit costs k labels, its expected distinct-label cost
is k[1-(1-q)^T], not Tqk and not qk. Saving labels and refreshing conditional
randomness must be accounted for together.

This rule restores conditional unbiasedness for the specified raw gradient.
It does not make stochastic training trajectories equal in law or expectation
to full-audit trajectories, and does not remove nonlinear optimizer effects.
Caching also needs a well-defined reference: flaky or stateful verifier runs
cannot silently be treated as immutable labels for a different target.

The [cache experiment](audit-cache-experiment.md) now tests this lifecycle
through three actual tensor optimizer steps and split microbatches. Its
additional counterexample shows why newly purchased labels must retain the
current update's inverse weight until all gradient accumulation finishes.

## 5. Relation to prior work and current evidence

[Li et al. (2026), Sections 2-3 and Proposition 8](https://arxiv.org/html/2610.35716v1)
analyze budgeted verifier corrections at the sampling policy. They give an
unbiased group advantage and warn that nonlinear optimizer operations can
change parameter-step expectations. Their experiments use clipped trainers;
their raw-gradient theorem is explicitly local to the sampling state.
Equations (1)-(4) concern extending that guarantee beyond its stated
conditions. We have not inspected their training code or reproduced their
results, and do not attribute their empirical outcomes to either mechanism.

The motivating [Sakib et al. post](https://portfolio.nazmus-sakib-touhid.app/blog/audit-the-group-not-the-patch)
studies whole-group corrections of full-suite signals. Its reported labels
and timings have not been independently checked here. Standard group-relative
clipping and repeated updates also appear in
[DeepSeekMath, Section 4.1](https://arxiv.org/html/2402.03300v3).

The proposed contribution to assess is the precise additional-penalty
identity, the isolated audit-reuse counterexample, and a checkable conditional
rule with explicit cached-label cost. A complete priority comparison remains
open. These calculations do not establish a new general sampling method,
measured LLM savings or a field-moving AI-safety result.

A broader priority search also checked
[Garg et al. (2021)](https://proceedings.mlr.press/v139/garg21b.html), whose
abstract describes empirical heavy-tailed PPO gradients and the role of
clipping, and [Huang et al. (2026), Section 3](https://arxiv.org/html/2609.36816v1),
which changes the clipping operation and compares gradient second moments
under explicit assumptions. These are related analyses, not verification
of the identity here. This bounded search does not settle priority; the
gap calculation could already be known in the broader PPO literature.

### Implementation boundary checked in TRL

We read [TRL v0.26.2, grpo_trainer.py](https://github.com/huggingface/trl/blob/v0.26.2/trl/trainer/grpo_trainer.py),
Git blob `74dc5f3783c570b9610a141dcc29151a0a4aff43`, through the GitHub
connector. Lines 2194-2202 combine the supplied advantages with clipped and
unclipped ratios before taking the minimum. Lines 1142-1165 buffer scored
completions for repeated updates. These are the relevant integration points;
the source contains several loss variants, and our identity covers the
ordinary PPO minimum with the declared fixed clipping interval.

Implementing (3) would require separate weak and full-reference clipped
contributions before the linear aggregation. Merely replacing the advantage
input would implement the other operation. The existing masks, aggregation
weights and audit-independent regularizers must retain the same reference
target; cached labels and fresh draws would need stable group identities
across batch splits. We did not install TRL, modify its source, or implement
and test such a trainer integration. Reading the upstream trainer does not
reproduce the cited paper's implementation or establish its behavior.

## 6. Reproduction

```powershell
python -B -S -m experiments.check_audit_surrogate
python -B -S -m unittest tests.test_audit_surrogate -v
python -B -O -S -m unittest tests.test_audit_surrogate -v
```

The exact-rational checker covers 600 fixed-ratio cases, signs and audit
probabilities, and enumerates every audit branch in the two-action example.
Six tests separately check central finite differences through both the
clipped integrand and the categorical policy, target expectations, and input
validation. The calculator deliberately leaves derivatives at clip knots
unspecified. It is an algebraic reference, not a trainer integration.

An optional seventh test uses an already-installed PyTorch runtime. It checks
400 cases with CPU float64 automatic differentiation, plus the two-update
categorical example. It is skipped when PyTorch is unavailable, including
under standard-library-only `-S`. To run this check without installing anything:

```powershell
python -B -m experiments.check_audit_surrogate --autograd
```

The local PyTorch 2.11.0+cu128 run used CPU tensors, matched the exact reference
within 8.89e-16, and returned second expected gradients -1.92 versus -1.96.
These are conformance checks on a constructed example, not a model-training
experiment or a test of the cited study's implementation.

At initial draft commit `772ec82`, all 380 tests on this branch passed with
the installed environment, including the optional autograd check. The
standard-library normal and optimized
calculations produce identical 825-byte output, SHA-256
`0023c788112670333752e5a1791c9d6a058a42f9ee25badcc29e36c478938789`.
Under `-O -S`, the six standard-library tests pass and the optional test is
explicitly skipped. Existing released scientific sources are unchanged.

The examples were chosen during derivation; no preregistration or measured
statistical experiment is claimed. Codex performed the derivation, coding
and writing. The owner has not personally checked the project and no
independent reviewer has validated this note. All work used installed tools;
no downloads, installations, model calls or external outreach occurred.
