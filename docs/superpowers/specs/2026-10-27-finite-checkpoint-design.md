# Finite checkpoint audit design

The original decision uses 32 prompts, 64 ranked candidates, budgets
`1,2,4,8,16,32,64`, threshold `1/10`, supplied efficiency margin `1/160`,
and one whole-family error allowance `1/20`. Preserve this decision and
all earlier evidence. The next contribution is a modest improved upper
bound from a concrete scheduled finite-population audit, not a new generic
test or a claim of practical model savings.

The candidate evidence branch queries all 1024 head cells at ranks 1..32,
then one uniform suffix permutation at checkpoints leaving 48, 32, and 16
cells unqueried. Each label is charged once. Three error allocations are
`1/250,3/4000,1/4000`, totaling `1/200`. Statistical passing is strict at a
lower expected-shortfall cutoff of a binary-plus-fractional extremal
population. Conservative bins of the head statistic have width at most
one. Convex-order hinge bounds give finite rational cost certificates.
Actual head upper bounds determine deterministic passes on every table.
Unsupported statistical cases go to full census, ensuring boundary-safe
completion. Test only budgets 1,2,4 statistically; other budgets must pass
their actual deterministic head bounds or the branch goes to census.

The all-real-label mathematical construction should prove uniform expected
margin-class cost at most 2016 and global false-pass probability at most
1/200. A separately explicit initial blind pass with probability `9/199`
then gives error `1/20` and cost `383040/199 < 1934.2`. The evidence branch
alone does not beat 1934.2. This is an upper bound, not the exact minimax cost.

Implement a narrow callback reference for this fixed geometry. API:
`audit(oracle, *, allow_blind=False, randbelow=None)`, where
`oracle(prompt, rank)` returns an integer or Fraction in [0,1], denominator
at most 1,000,000. Prompts are zero-based; ranks are one-based. No labels
are obtained before their charged callback. Return immutable acquisitions,
checkpoint records, and a whole-family decision with an explicit reason.
The evidence branch is the default; `allow_blind=True` opts into the
mathematical mixed benchmark. Invalid callbacks or RNG values raise, without
issuing a certificate. Default RNG is `secrets.randbelow`; a supplied RNG
must be independent and uniform for the stated guarantees. A seed is only
for demonstrations, not a certification argument.

Finite probability calculations use only exact integers and Fractions.
No SciPy import or ignored-file dependency is allowed. The checker must
recompute all 2439 original head-bin/checkpoint bounds, independent small
subset laws, hinge checks, and atom-sensitive strict tails. Fixed callback
examples include zero, margin, boundary, unsafe, and heterogeneous tables;
they are conformance demonstrations, not an empirical error-rate study.

Publish the full real-loss proof, classical attribution, rational reference
scope, exact checker and source pins, reproducible result, and concise
report. Freeze the protocol before the saved full run and reviewed sources
before final evidence. Prior exploratory search must be disclosed. No
downloads, installs, model inference, outreach, or 2 GB storage growth.
