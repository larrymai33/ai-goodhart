# Exact all-passing cost for finite program audits

This follow-up studies the program-failure target identified in the
[operational scope check](repeated-screening-operational-check.md). It gives
an exact benchmark on the all-passing input, including a lower bound against
adaptive partial testing. It is a self-contained derivation using classical
sampling and decision-tree arguments, not an established novelty claim.
There is no independent proof review or measured LLM result.

## Decision and observation model

Fix an unknown binary table with N programs and c tests per program. A one
means that the program fails that test. A program is bad if its row contains
any one. The decision is whether fewer than b programs are bad, where
1 <= b <= N. To certify a program-failure fraction at most tau < 1, set
b = floor(N*tau)+1.

Querying a previously unknown component costs one and reveals its fixed
bit; later access is free. A policy may adaptively choose any component,
randomize, and interleave queries across programs. There is no informative
side information about the table. Code inspection, coverage, variable test
durations, stateful tests and flaky outcomes are outside this model.

For a declared d in {1,...,c}, restrict the input class to tables in which
each row is either all zero or has at least d ones. The unrestricted case
is d=1. The promise d>1 is a genuine extra assumption, not something inferred
from passing sampled tests.

Require (i) probability of ever certifying at most delta on every allowed
table with at least b bad rows, and (ii) almost-sure finite certification on
every allowed table with fewer than b bad rows. Rejecting a safe table is
therefore not allowed. A full census can decide the target exactly.

Let C0* be the infimum of expected distinct queries **on the all-zero table**
over these policies. This is not worst expected cost over all safe tables.
It is a lower bound on that stronger objective, but its achieving policy can
be expensive on nonzero safe tables. Auxiliary computation and randomness
are not charged.

## Exact finite characterization

For a query-count profile k=(k_1,...,k_N), with 0 <= k_i <= c, define

```text
a_d(k_i) = choose(c-k_i,d) / choose(c,d)
M_d(k)   = e_b(a_d(k_1),...,a_d(k_N)) / choose(N,b)
cost(k)  = sum_i k_i.
```

Here an out-of-range binomial coefficient is zero and e_b is the elementary
symmetric polynomial of degree b. Then

```text
C0* = min  sum_k pi_k cost(k)
      s.t. pi_k >= 0, sum_k pi_k = 1,
           sum_k pi_k M_d(k) <= delta.                 (1)
```

The minimization is finite. An optimum uses at most two profiles. Profiles
can be sorted without changing their cost or M_d, so small instances are
solved by enumerating integer multisets and taking a lower convex envelope.
This is a characterization, not a scalable general-purpose optimization
algorithm.

**Lower bound.** Put a distribution on unsafe tables: choose exactly b bad
rows uniformly, and independently choose exactly d failing positions
uniformly inside each bad row. Fix the policy's internal random seed and
run it on the all-zero table. By safe completion, outside a seed event of
probability zero it certifies after a finite transcript. Let k be the counts
of distinct queried components in that transcript.

Under the unsafe distribution, the chance that none of those queried
components fails is M_d(k). On this event, coupling the same internal seed
gives exactly the all-zero transcript, including its certification decision.
This argument permits adaptive query selection and stopping: all answers
on the coupled path are identical. Consequently

```text
E_seed[M_d(k)] <= Pr_unsafe-prior(certify) <= delta.
```

The last inequality follows from validity on every table in the prior's
support. The distribution of zero-path profiles is feasible
for (1), and its expected cost equals the policy's all-zero cost. Repeated
free queries do not affect either expression. This proves the lower bound.

**Attainment.** Draw a profile from a feasible mixture, assign its entries to
rows by a uniform random permutation, and choose a uniform subset of the
prescribed size within each row. If every queried bit is zero, certify.
If any queried bit is one, finish a full census and decide exactly.

For any fixed table with exactly b bad rows and exactly d failures in each,
symmetry makes the chance of missing all failures M_d(k). Any other allowed
unsafe table contains such a table componentwise: choose b of its bad rows
and d failures in each. Adding failures cannot increase the chance that
all selected tests pass. Thus the mixture has false certification probability
at most delta on every allowed unsafe table. Census gives finite correct
certification on every safe table. On the all-zero table its expected cost
is exactly the objective of (1).

The at-most-two-profile assertion follows from a basic feasible solution
of the finite linear program: there is one normalization equality and one
risk inequality. A slack risk constraint permits a one-profile optimum.
Randomization between profiles is part of the cost optimum; this is not a
deterministic query-budget guarantee.

## Without a density promise, complete rows are optimal

For d=1, define

```text
h_j = choose(N-j,b) / choose(N,b),  0 <= j <= N.
```

For 0 < delta < 1, choose j with h_j >= delta >= h_(j+1). Then

```text
C0* = c [ j + (h_j-delta)/(h_j-h_(j+1)) ].             (2)
```

At delta=0 the value is c(N-b+1); at delta=1 it is zero. If delta equals a
knot, the neighboring formulas agree. In particular, b=1 gives
C0*=(1-delta)Nc.

An optimal policy randomly chooses j or j+1 complete rows, samples them
uniformly without replacement, and uses the census fallback above after
any failure. The probability of choosing j+1 is
(h_j-delta)/(h_j-h_(j+1)). No adaptive partial-component policy has smaller
all-zero expected cost.

**Why concentration is optimal.** Fix a total m of queried components.
For d=1, write a_i=1-k_i/c. Holding all other coordinates and a_i+a_l
fixed, the only varying term of e_b is

```text
a_i a_l e_(b-2)(other coordinates).
```

Its coefficient is nonnegative (zero for b=1). Moving two interior
coordinates apart until one reaches 0 or 1 weakly decreases their product.
The move stays on the 1/c grid. Repeating leaves at most one interior
coordinate. Thus a minimizer queries j=floor(m/c) complete rows and
r=m-jc components in one further row. Its miss probability is

```text
h(m) = (1-r/c) h_j + (r/c) h_(j+1).                   (3)
```

At m=Nc use h(Nc)=0. The successive row differences are

```text
h_(j+1)-h_j = -choose(N-j-1,b-1)/choose(N,b).
```

They are nondecreasing in j, including the zero tail. Therefore the
piecewise-linear extension h is decreasing until zero and convex. For any
valid policy, the lower-bound coupling gives
delta >= E[M_1(k)] >= E[h(C)] >= h(E[C]). Inverting h proves (2), with the
stated endpoint cases. Equivalently, the convex envelope in (1) is already
the interpolation through complete-row allocations.

The hypergeometric curve itself is classical zero-acceptance sampling.
The point of this calculation is to check that arbitrary component access
does not beat that baseline for this particular input and assumption set.

## Why the all-passing objective does not describe every safe table

There is a separate elementary boundary obstruction when d=1. Fix any safe
table X with exactly b-1 bad rows. It has N-b+1 all-zero rows. For every cell
z in those zero rows, change just z to one, producing an unsafe table X_z.
Couple a policy on X and X_z using the same internal randomness. Unless the
policy queries z before certifying X, the two transcripts agree and it also
certifies X_z. Safe completion on X and validity on X_z imply

```text
P_X(query z before certification) >= 1-delta.
```

Summing over the c(N-b+1) cells in good rows gives, for every valid policy,

```text
E_X C >= (1-delta)c(N-b+1).                            (4)
```

This charges only good-row cells; discovering bad rows may cost extra. It
is not an equality or a full minimax characterization. The alternative
X_z would violate d>1, so the bound is explicitly for the unrestricted
single-failure model.

For N=100, c=20, b=6, delta=1/20, the all-zero optimum from (2) is
239936300/313113, less than 767 queries. Yet every valid policy spends at
least 1805 queries in expectation on every table with exactly five bad rows,
out of a 2000-component census. Thus a small all-zero cost alone cannot
establish a uniformly cheap audit over the whole safe class. A margin class
excluding these boundary tables would be a different cost objective.

## A density promise changes the optimum, and can invalidate it

Take N=2, c=4, b=1, delta=1/4. With no promise beyond one failure per bad
program, (2) gives expected cost 6.

Now assume each bad program fails at least two tests (d=2). With probability
1/4 query counts (1,1); with probability 3/4 query (2,2). Within rows, choose
uniform subsets. Their miss probabilities on the least favorable unsafe
tables are 1/2 and 1/6, respectively. Their query costs are 2 and 4.
The mixture therefore costs 7/2 with error 1/4,
and (1) verifies optimality.

A baseline that completely resolves every selected row needs three passing
tests to rule out two hidden failures. Complete-row sampling consequently
costs 3*(1-delta)*2=9/2 on the all-zero input. Partial testing is strictly
better here. This baseline already uses the promise; charging four tests
per passing row would be an unfair comparison.

But on a fixed table with just one failing test in one program and all
other tests passing, that same partial-testing policy misses the failure
with probability

```text
1 - (7/2)/(2*4) = 9/16 = 56.25%.
```

Its intended error limit was 25%. A density assumption cannot silently be
learned from an all-passing audit transcript. This example is constructed
and small; it is neither an estimate of LLM failure density nor evidence
of measured savings.

## Prior work and interpretation

Classical acceptance sampling already uses the exact hypergeometric law
to bound acceptance of a finite population with too many defective items;
see [Samohyl (2018), Traditional acceptance sampling](https://link.springer.com/article/10.1007/s40092-017-0231-9).
Formula (2)'s row-sampling curve is an instance of that established method.

Adaptive costly bit inspection is also established. For example,
[Allen et al., Evaluation of DNF Formulas, Section 2](https://www.cs.cmu.edu/afs/cs/user/srallen/www/papers/dnfdraft17.pdf)
define stochastic Boolean function evaluation under a known product
distribution and require an exact Boolean certificate. The present objective
instead imposes uniform error control over fixed tables and charges expected
cost on one specified input. That distinction does not establish novelty.

[Suruga (2026), Section 1.1 and Theorem 2](https://arxiv.org/html/2608.04152v1)
explicitly studies one-sided query algorithms with cost measured on zero
inputs and gives exact amortized identities for OR compositions. Thus neither
zero-input cost nor one-sided query lower bounds should be presented as new
ideas here. A complete comparison with finite threshold-of-OR and search-game
results has not been completed.

This benchmark rules out one hoped-for improvement under a transparent
model, and identifies an assumption under which partial testing can help.
It does not establish practical AI-safety relevance, solve cost minimization
on nonzero safe tables, validate a test suite as a safety oracle, or transfer
to adaptive code inspection and non-fixed test outcomes. These are material
limits, not conclusions deferred to a larger synthetic sweep.

## Reproduction and provenance

```powershell
python -B -S -m experiments.check_program_audit
python -B -S -m unittest tests.test_program_audit -v
python -B -O -S -m unittest tests.test_program_audit -v
```

The checker uses exact fractions, elementary-symmetric coefficients and a
lower convex envelope. Its small-instance solver refuses tables with more
than 128 components or more than 20,000 sorted profiles. The d=1 closed-form
routine does not enumerate profiles. Neither routine runs an actual audit.

The checker covers 789 singleton-failure allocation profiles. Seven tests
independently enumerate hidden failure locations, random query
subsets on fixed unsafe tables, and all two-profile mixtures for selected
small instances. They also compare the closed form against the allocation
optimization, and verify the off-promise error counterexample. Such finite
checks support the derivation but are not a proof of the general theorem.

Codex derived and wrote this note and its checker. Larry has not personally
checked it; no independent reviewer has validated it. No files or software
were downloaded, no models or datasets were run, and no outreach occurred.
The original noisy-screening certificate and released manuscript are unchanged.
