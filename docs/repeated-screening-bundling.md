# What changes when repeated ratings are bundled into one report?

Working analysis, 27 October 2026; derived and checked by the generating Codex
session, without independent review. This clarifies the interpretation of the
[finite separation](repeated-screening-theorem.md). It does not change its
numerical bounds or establish scientific priority.

**A complete gate can be exposed as one finite-valued report.** Therefore
counting reports, without specifying their primitive computation and price,
is not a defensible novelty argument. The original lower bound permits one
primitive cost-one Bernoulli rating per item. A bundled gate has a different
channel and consumes multiple such ratings. Its random cost can be bounded
in conditional expectation by a fixed price, as shown below.

## The relevant existing interface

[Ham, Zhao, Jasin and Yang (v1)](https://arxiv.org/html/2609.28859v1), Sections
3.1–3.3, allow an arbitrary known strictly positive finite report channel
conditional on a binary latent label, with one AI report and one exact human
label per item. The AI report has a fixed price. Theorem 4.6 and Appendix 8.2
give adaptive transcript-KL accounting. Their testing target uses two simple
iid hypotheses and two error constraints, whereas this project's finite
comparison requires validity and boundary completion on fixed score tables.

The finite-alphabet assumption does **not** prevent a completed random walk
from returning a binary summary. The issue is which summary and price are
supplied, and whether another report from the same physical item is allowed.
The calculation below is our application to the project's gate, not a result
attributed to that paper. It shows an interface connection, not a reduction
of the entire fixed-table minimax problem to the cited optimality theorem.

## 1. The gate's binary report and expected cost

Run the gate on one uncached item, stopping before any exact purchase. Let
U=1 if the initial positive rating and subsequent walk reach the upper
boundary; let U=0 otherwise. Let T count all primitive paid ratings, including
the initial rating and holding steps. Put n=K+1, q=1/4+y/2 and
r=(1-q)/(3q). The gate calculations give

```text
G_K(y) := P_y(U=1) = q / (1+r+...+r^K),
t_K(y) := E_y T = 1 + [n/(1-r^n)-1/(1-r)]/(3/4),  y>0,
t_K(0) = 1+2K/3.
```

In particular, on the binary score submodel y in {0,1},

```text
g0 = 1/[4(K+1)],
g1 = (2/3)/(1-9^[-(K+1)]),
t0 = 1+2K/3,
t1 = 1+(4/3)*[(K+1)/(1-9^[-(K+1)])-9/8].
```

Both report values have strictly positive probability under either label.
For K=0 this is exactly one primitive rating, with cost one. For K>=1 the
expected costs differ by label. In fact, writing n=K+1>=2,

```text
t1 > 4n/3-1/2 > 2n/3+1/3 = t0.
```

Thus no single constant equals the gate's expected cost under both pure
labels. A pathwise constant is also impossible: after an initial positive
rating, any finite number of holding steps has positive probability. T has
unbounded support when K>=1. A finite report alphabet and random computation
cost are separate facts; retaining the entire walk is unnecessary for U.

## 2. A fixed price can nevertheless dominate expected work

For every score y in [0,1],

```text
t_K(y) <= A_K := 1+4K/3.
```

Here is a direct proof. For r<1 set S=sum_{j=0}^{n-1} r^j. Bounding the bracket
in the expression for t_K by n-1 is equivalent to

```text
n <= [n-(n-1)r] S
   = n + sum_{j=1}^{n-1} r^j - (n-1)r^n.
```

Each summand r^j is at least r^n. At r=1 the fair-walk expression t_K(0)
also satisfies the bound. The argument includes K=0.

Consider an outer policy that commits to completing each bundled gate before
choosing its next action, and uses only the returned U values, any purchased
exact labels, and its own independent randomness. It does not use elapsed
gate duration to steer later choices. Replacing its atomic report calls by
the actual gate preserves that policy's observation and decision law.
Conditional expected work for each requested gate is at most A_K, including
when earlier observations change a latent label's posterior. Predictable
continuation indicators and nonnegative summation therefore give

```text
E(actual payment) <= A_K E(number of bundled calls)
                     + c E(number of new exact purchases).
```

This is a valid one-sided expected-cost transfer. It is neither a pathwise
budget guarantee nor an exact equality of cost models. In particular, an
outer policy allowed one bundled report per item fits the corresponding
report interface on binary scores, priced conservatively at A_K. A new
testing primitive is not needed merely to use that finite report.

## 3. Neither binary channel is a post-processing of the other

The gate amplifies positive evidence, but calling U uniformly more informative
than a primitive rating Z would be incorrect. Suppose a label-independent
randomized post-processing of Z returned U. Put a=P(U=1|Z=1) and
b=P(U=1|Z=0). Matching the two channel probabilities forces

```text
a = (3g1-g0)/2,
b = (3g0-g1)/2.
```

For K>=1, g1/g0>3, so b<0. No such post-processing exists. Conversely, a
post-processing of U that reproduced Z would require

```text
P(Z=1|U=1) = [(3/4)(1-g0)-(1/4)(1-g1)]/(g1-g0) > 1.
```

The final strict inequality is equivalent to 3g1-g0<2, which is equivalent
to 9^n>8n+1. This holds for every integer n>=2 (induction from n=2).
Consequently neither binary channel is a randomized post-processing of the
other. This concerns the coarsened bit U: the full stopped transcript retains
the first primitive rating, so it can of course reproduce that rating.

The smallest nontrivial example is explicit:

| K | P(U=1|y=0) | P(U=1|y=1) | E(T|y=0) | E(T|y=1) | A_K |
|---:|---:|---:|---:|---:|---:|
| 0 | 1/4 | 3/4 | 1 | 1 | 1 |
| 1 | 1/8 | 27/40 | 5/3 | 11/5 | 7/3 |
| 4 | 1/20 | 19683/29524 | 11/3 | 45517/7381 | 19/3 |

At K=1 the required forward b is -3/20 and the required reverse probability
is 23/22. They are invalid probabilities, not small numerical discrepancies.

## What this settles, and what it does not

The finite comparison remains a separation against **one primitive rating
per physical item**, not against every method that exposes a single compound
report. Substituting G_K for the primitive channel requires recomputing its
information rates and report price. The old lower-bound constants cannot be
carried over unchanged.

The complete project auditor can revisit an unrevealed physical item after a
failed gate and later reuse cached exact values. The single-call reduction
does not eliminate those revisits. Nor does it turn fractional scores and
fixed-table validity into the cited iid binary-hypothesis objective. Whether
earlier generalizations cover those details remains open. This analysis does
not claim to beat SCALE on a common oracle model or settle prior priority.

[Prangle's Lazy ABC, Appendix B](https://arxiv.org/html/1405.7867v3), already
allows several stopping decisions, including random stopping times. Random
continuation is therefore not an independent novelty claim here either.
The surviving candidate is the explicit, fully priced finite comparison in
the stated primitive-oracle model. Its importance for actual safety evaluation
still needs an operational justification.

## Reproduction and scope

Run `python -B -S -m experiments.check_screening_bundling`. The
[checker](../experiments/check_screening_bundling.py) prints exact fractions
for K=0,1,4,52. It uses the separately implemented absorbing-chain recurrence
to check 901 pairs (K,y), with K=0,...,52 and y=0,1/16,...,1. It checks the
uniform expected-price bound and the endpoint formulas; 52 binary-channel
comparisons check both post-processing obstructions. Five regression tests
also pass under optimized standard-library Python. These finite checks do
not replace the universal arguments above or an independent review.

No frozen theorem, callback implementation, or certificate has changed. No
downloads, installations, model calls or outreach were used. This is a bounded
source comparison and elementary deduction, not an exhaustive literature
review or evidence of independent research ownership or field impact.
