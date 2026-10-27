# Attribution and scope of the monotone-placement reduction

This extension strengthens the lower certificate for the original
seven-budget decision by reducing the search over a specified class of
hard priors. The [proof](monotone-placement-theorem.md) separates the
structural reduction from the finite calculation; the
[report](monotone-placement-report.md) records the resulting certificate.
The proposed contribution is that reusable reduction and its quantitative
consequence, with scientific priority still unestablished.

## Established ingredients

With some coordinates fixed to one and exactly k positives among unknown
coordinates, the worst weighted loss is the fixed contribution plus the
sum of the k largest unknown weights. This is an established
budgeted-uncertainty expression. [Bertsimas and Sim, *The Price of
Robustness* (2004), Section 3, equations (4)--(6), Proposition
1](https://www.mit.edu/~dbertsim/papers/melvyn/The-Price-Of-Robustness-OR52.pdf),
maximize selected nonnegative contributions under an integer uncertainty
budget and give the equivalent bounded-selection linear program. That
result supplies an antecedent for the top-k expression, not the statistical
query lower bound here. The sorting proof uses an elementary exchange
argument; no new general rearrangement principle is claimed.

The experiment comparison uses another elementary principle: supplying
additional information cannot increase the optimal decision cost. This
belongs to the classical comparison-of-experiments framework associated
with [Blackwell's *Comparison of Experiments*
(1951)](https://digicoll.lib.berkeley.edu/record/112749). The present proof
provides its own explicit latent-subset construction and simulation,
including the accounting of query costs. It does not introduce a new
information-ordering theorem.

The finite optimization is the same classical Lagrangian sequential-testing
calculation used in the [preceding certificate](finite-decision-priority.md).
[Novikov (2008), Section 2, equation (7), Section 4, Theorem 4 and Remark
5](https://arxiv.org/html/0811.1297v1), treats error penalties and finite-horizon
backward recursion, including stopping before any observations. Exact
integer evaluation verifies a specialization of that machinery; it is not
a new Bellman method.

## What the reduction covers

All target rows must share one nonincreasing coordinate order. Fix the
numbers of known-zero, unknown, and known-one coordinates, with k positives
uniformly placed among the unknown coordinates. Sorting these categories
as a zero prefix, unknown middle, and one suffix simultaneously minimizes
every target's worst null risk. The common ordering is essential.

For fixed k and count difference d, enlarging the unknown block cannot
make the two-prior testing problem easier. A latent subset revealed for
free reduces the larger experiment to the smaller one. The revealed set
is correlated with the labels and contains all unknown positives; it is
not an independent sample of an already fixed table. This comparison does
not apply when k or d changes simultaneously.

Together these facts reduce the declared class to its largest feasible
unknown block for each count split. The finite comparison ranges over all
193 splits of 192 null positives between the fixed-one suffix and unknown
block, at multipliers 2,048 and 4,096. The resulting 386 calculations are
a specified search over this class; one additional clean witness is
evaluated separately. They do not optimize over every hard
prior, every multiplier, or every admissible auditor. Revealing fixed
outside labels is a lower-bound relaxation, not an operational annotation
procedure.

## Separate benchmarks and remaining limits

The original decision still uses all seven budgets, fractional-label
validity, all-safe completeness, and worst expected cost over the supplied
margin class. Budget 1 supplies the unsafe alternatives; the other rows
constrain which common-safe priors are feasible. A larger lower bound does
not imply that every safe table is difficult or that observed model
evaluations require that many labels.

The zero-error comparison is separate: deterministic worst-case margin
cost is 2,036, while randomized zero-error cost lies between 2,034 and
2,036. The lower endpoint follows already from the constant fractional
table with every label equal to 3/32: leaving 15 coordinates unseen admits
an unsafe completion. These are not lower bounds for randomized auditors
allowed error 1/20.
Mixing a zero-error audit with probability 1/20 of immediate blind
certification gives the routine 1,934.2 expected-cost upper benchmark
under the stated objective. It does not demonstrate better statistical
acquisition or introduce an operational audit engine.

The unresolved [2011 weighted-query comparison](finite-saturation-priority.md)
and [historical auditing comparison](inspection-priority-review.md) remain
open. A tighter finite interval and a
structural search reduction strengthen the mathematical artifact without
establishing novelty, independent human verification, real-model
usefulness, or field impact. The [provenance record](provenance.md) discloses
the substantial Codex assistance.
