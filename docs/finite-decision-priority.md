# Attribution and scope of the finite decision certificate

This extension evaluates a finite lower bound for the original seven-budget,
nonzero-margin decision. It uses established sequential-testing optimization.
The candidate contribution is the common-safe reduction for this rank family
and its quantitative consequence at the original parameters, not a new
sampling method or dynamic-programming principle. The [proof](finite-decision-theorem.md)
and [report](finite-decision-report.md) give the calculation and its evidence.

## Classical sequential-testing machinery

[Novikov, *Optimal sequential multiple hypothesis tests*,
arXiv:0811.1297v1 (2008)](https://arxiv.org/html/0811.1297v1), Section 1,
treats dependent observations and expected sample cost at a specified
parameter. Section 2, equation (7), adds weighted error probabilities to
that cost. Section 4, Theorem 4, equations (50)-(51), gives the
finite-horizon backward recursion comparing terminal loss with observation
cost plus continuation value. Remark 5 explicitly permits stopping before
any observations. These passages supply the relevant antecedent for the
Lagrangian and Bellman calculation. The present one-sided requirement of
no rejection on safe-prior support needs the accompanying direct
specialization; it should not be identified verbatim with the paper's
positive-error formulation.

The lower-bound direction is ordinary weak duality. If a relaxed test
minimizes `E_safe T + lambda*Pr_unsafe(certificate)` to value `V_lambda`,
every admissible audit with false-certificate probability at most delta
has expected cost at least `V_lambda-lambda*delta`. A single multiplier
suffices for a valid lower certificate. No claim of a new duality theorem,
strong duality, or global multiplier optimization is needed.

## What this instance establishes

The decision retains 32 prompts, 64 ranks per prompt, and all seven budgets
`{1,2,4,8,16,32,64}`, with threshold `1/10`, supplied margin `1/160`, and
error probability `1/20`. On ranks 33 through 64, every target item weight
is at most the uniform-target weight. Consequently, every placement of
192 positive labels in this 1,024-item tail, with zeros elsewhere, is safe
for every target at the required margin. Every placement of 205 positives
there is unsafe for budget 1. Uniform fixed-count priors preserve
exchangeability under adaptive coordinate queries.

Budget 1 alone supplies the unsafe alternative and forces this lower
bound. The other budgets enter by ensuring that the entire null support
remains safe for the declared family. The certificate does not show that
interactions among seven constraints jointly cause the cost, or establish
a new advantage or penalty from sharing labels across targets.

This gives a valid relaxation for **the unchanged whole-family decision**.
It does not substitute the smaller high-budget family used in the earlier
512-label prefix illustration. The five evaluated multipliers are
`512,1024,2048,4096,8192`; the strongest certificate among these is at
`lambda=2048`, giving a lower bound exceeding 784.185 expected labels.
Combined with the 2,048-label census upper bound, this brackets the minimax
cost within a factor below 2.612. The multiplier list does not establish
global optimality.

The minimizing dynamic-program policy solves a relaxed mixture-testing
problem. Its displayed cost is **not** an achievable upper bound for an
auditor valid on every fixed fractional table. The lower bound concerns
worst expected cost over the supplied margin class: it does not say every
safe table needs this many labels, or explain stopping costs for a single
selected budget. There are no actual model labels in this calculation.

## Remaining limits

Within this repository, the result supplies a useful finite lower bound
for the original seven-budget nonzero objective, where the previous loose
order constants gave little operational information. It neither completes
the arbitrary-grid rate characterization nor introduces a faster audit.
The [earlier source comparison](finite-saturation-priority.md) records the
unresolved proof-level comparison with Chakrabarti, Guruswami, Andrew
Wirth, and Anthony Wirth's 2011 weighted-average query paper; it remains
open. Exact computation, public release, and a narrower cost interval do
not establish scientific priority, independent human verification,
real-model usefulness, or field impact. The [provenance record](provenance.md)
discloses the substantial Codex assistance.
