# Component access changes the experiment and the evaluation target

Working scope audit, 27 October 2026. Derived and checked by the generating
Codex session only. No real model, benchmark dataset, or generated program was
run. The [finite separation](repeated-screening-theorem.md) remains a result
about its stated opaque noisy-rating/exact-score experiment. This note rejects
an automatic interpretation of that experiment as ordinary test-suite access.

Two obstacles matter. First, executable component outcomes supply a stronger
observation interface than the noisy rating. Second, the mean fraction of
failed tests is a different quantity from the fraction of programs with any
failure. A useful application must resolve both.

## Why inspect a test-suite interpretation?

A fixed finite test suite is a plausible way to make an exact numerical score
available: define a program's score as the fraction of its tests that fail,
and run the entire suite to reveal it. [EvalPlus](https://arxiv.org/html/2305.01210v3),
Sections 2 and 3, evaluates generated programs by comparing outputs against
reference implementations and reports pass@k. It also studies test-suite
reduction using test-level information. Its
[evaluation source](https://github.com/evalplus/evalplus/blob/master/evalplus/evaluate.py)
exposes optional per-input pass/fail details (`test_details` and `Result`). The
file was read through the GitHub connector; its returned Git blob SHA was
`d4e1b91758e89772a32aab2bfcab7048d7cec016`.

These sources motivate the access question. They do not establish unit costs,
fixed independent outcomes, or the known randomized-noise channel assumed in
our theorem. Actual execution costs, setup overhead, timeouts, unequal suite
sizes, and reference errors would require separate treatment. The countermodel
below retains the theorem's simplifying equal-cost accounting to isolate the
information mismatch.

## 1. Visible components can simulate the opaque oracle

Let b_ij in {0,1} be fixed failure bits for N programs and c tests per program.
Define y_i=(1/c)sum_j b_ij and R=(1/N)sum_i y_i. In the component-access
experiment, requesting an individual bit costs one and previously seen bits
can be cached. Auxiliary randomness is free.

This interface can implement both original oracle actions:

1. To emulate a noisy rating of item i, select j uniformly with replacement,
   obtain b_ij, and independently flip it with probability 1/4. The returned
   bit has probability 1/4+y_i/2 of being one. Charge at most one new query.
   The simulated auditor need not see the index or original bit.
2. To emulate an exact score, acquire the remaining component bits in that
   row and compute their mean, paying at most c.

Thus any opaque-oracle policy can be simulated with the same returned-data
law and no larger component-query cost. The converse access is not supplied
by the original oracle. In particular, deliberately adding noise and hiding
indices does not show that an evaluator with direct test access needs to
discard those outcomes. This is elementary simulation/data-processing
reasoning, not a claimed new comparison-of-experiments theorem.

## 2. A standard raw-component baseline

Uniformly propose a pair (i,j) from the Nc cells, with replacement. Read and
cache the selected bit. The emitted bits are iid Bernoulli(R) for every fixed
matrix: independent indices passed through a fixed table have that law,
including when a repeated value is retrieved from cache.

Write theta=tau-epsilon, 0<epsilon<tau<1. Start wealth at one and multiply by
theta/tau on a failure bit and by (1-theta)/(1-tau) on a zero bit. Certify when
wealth reaches 1/delta. If all cells are cached first, decide by the exact
mean. This is a mathematical construction, not a new operational code runner.

On R>tau, the likelihood wealth is a nonnegative supermartingale: its
conditional expected multiplier is an affine decreasing function of R and
equals one at tau. The crossing probability is therefore at most delta;
exact census certification cannot err. If no earlier decision occurs,
independent uniform proposals eventually visit every cell almost surely.
Consequently every safe matrix, including R=tau, is certified after finite
work almost surely. This uses the same validity/completion requirements as
the opaque experiment, with a different observation interface.

On R<=theta, the log drift is at least d=kl(theta,tau)>0 and the upward
overshoot is at most u=log((1-theta)/(1-tau)). For the first likelihood crossing
T, bounded stopping gives

```text
d E(T min t) <= E(log wealth at T min t) <= log(1/delta)+u.
```

Let t increase. Actual new component queries cost at most one per proposal
and at most Nc over the entire run, giving the uniform expected-cost bound

```text
W_component <= min{Nc, [log(1/delta)+log((1-theta)/(1-tau))]/kl(theta,tau)}.
```

The two original parameter settings give the following outward-rounded
inequalities. The columns explicitly refer to different oracle models.

| Parameters | Raw-component upper | Opaque hybrid upper | Opaque cheap-only lower |
|---|---:|---:|---:|
| N=13,000, c=64, tau=1/64, epsilon=9/640 | 285 | 2,973 | 18,653 |
| N=70,000,000, c=8,192, tau=1/512, epsilon=1/8192 | 767,339 | 98,855,201 | 302,326,524 |

Both use delta=1/20. A smaller upper bound is not proof that the opaque
implementation's actual expected cost is larger. It does establish an
achievable competing guarantee in the visible-component model and shows why
the opaque cheap-only lower bound cannot transfer to that richer interface.
No population of either displayed size was instantiated.

## 3. Test failure averages do not determine program failure

Let S=(1/N)sum_i 1{y_i>0}, the fraction of programs failing at least one
test in a fixed archive. A pass@k target additionally depends on task grouping
and the candidate-selection rule; S is not itself that metric. For c equal-size suites,

```text
R <= S <= min(cR,1).
```

The first inequality follows from y_i<=1{y_i>0}; the second follows from
1{y_i>0}<=c*y_i. Both bounds are attained on suitable finite matrices. For
example, with N=c=16, one entirely failing row and fifteen zero rows have
(R,S)=(1/16,1/16), while one failing test in every row gives (R,S)=(1/16,1).

The problem occurs inside the original efficiency classes, not only at their
boundaries:

- Wide example: 1,300 of 13,000 programs each fail exactly one of 64 tests.
  Then R=1/640=tau-epsilon, but S=1/10.
- Small-relative-margin example: every program fails exactly 15 of its
  8,192 tests. Then R=15/8192=tau-epsilon, but S=1.

A valid certificate for R under the original definition would be consistent
with these program-failure rates. It cannot be relabeled as a certificate
for S at the same threshold. Bounding R by tau/c would suffice to bound S
by tau, but changes the decision and its cost analysis. Nor does passing a
finite suite by itself certify semantic correctness or deployment safety.

## Research consequence

The finite-test-suite interpretation does not currently establish a practical
advantage for the opaque repeated-screening construction. It supplies raw
outcomes and usually motivates a program-level decision, while the theorem
withholds those outcomes and audits an average numerical score.

A supported application would need an actual observation interface, a
declared estimand, and matching cost accounting. An opaque service that
returns only calibrated noisy bits could define the stated experiment, but
no such safety-evaluation protocol has been established here. An ordinary
LLM judge's errors cannot simply be assumed to implement known independent
randomized response for every item.

The next research priority is the cost of the actual observable decision,
including individual test access and program-level failure when those are
the intended task. Further features or wider synthetic sweeps of the opaque
auditor would not resolve this application gap. The mathematical draft stays
available as an idealized result; it is not evidence yet of a field-moving
AI-safety contribution or fellowship competitiveness.

## Checks

`python -B -S -m experiments.check_component_access` computes the raw-access
upper bounds using rational log/KL enclosures, verifies the two symbolic
margin counterexamples, and checks the risk inequalities on all 16 two-row,
three-test failure-count profiles. The checker retains the original parameter
domain tau<=1/8 and delta<=1/4. Four regression tests pass normally and
under `-O -S`. These calculations are conditional on the analytic arguments;
there has been no independent proof review.

The original theorem, auditor and saved certificate are unchanged. No
downloads, installations, model calls, dataset execution or outreach occurred.

## Follow-up on the actual target

The [program-audit benchmark](program-audit-zero-cost.md) now gives an exact
all-passing-input cost for direct component access and a bound on the number
of programs with any failure. It permits arbitrary adaptive partial queries.
When a bad program may fail only one test, random complete-row inspection
attains the optimum on the all-zero input. A known minimum failure density
can make partial testing better, but the example also quantifies loss of
validity when that promise fails. This is a conditional baseline with a
narrow cost objective; it does not establish a practical evaluation advantage.
