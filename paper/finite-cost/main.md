# Finite label costs for certifying best-of-N risk

**Larry Mai (project owner), with substantial Codex assistance**

Research manuscript, 27 October 2026. This document consolidates the
finite-cost results in the public research artifact at commit `765ac51`
[1]. It reports no new experiment.

**Contribution disclosure.** Larry Mai commissioned this project. Codex
developed the theory, software, literature assessment, numerical checks,
and manuscript; separate agent contexts reviewed the work. Larry has not
personally checked the results. There has been no independent human
verification or peer review. The mathematical statements are contribution
candidates; scientific priority and practical model benefit remain
unestablished.

## Abstract

Consider a fixed collection of ranked candidate pools and a declared
family of best-of-N selectors. An auditor purchases correct, fixed losses
and may certify that every declared selector has risk at most a threshold.
We study the least worst-case expected number of distinct labels on tables
separated from that threshold by a supplied margin. Validity is required
on every fixed table, and completion on every safe table, including the
boundary. For every finite pool size, prompt count, and nonempty budget
grid, the cost is characterized up to universal constants by the smaller
of a deterministic prefix cost and a clipped envelope sum. A construction
using classical likelihood-ratio tests and a shared label cache attains
a factor-17 upper bound on geometrically separated grids. The lower proof
combines a common safe prior across diffuse rank scales with exact-count
priors for finite saturation. For a full dyadic grid and a particular
shrinking-margin sequence, the matching cost is of order
$m\log\log(m)/\log(m)$, below census order. The constants are loose;
a separate finite-instance certificate illustrates that practical savings
can remain modest. These are fixed-table query-cost results, not measured
LLM improvements or guarantees about graders, new prompts, or deployment.

## 1. The question and the contribution candidate

A higher search budget changes which ranked candidates are likely to be
selected. An audit of several budgets can reuse a purchased label, but
optimizing a sampling weight or an estimator's variance need not minimize
the labels needed to certify a threshold decision. We ask how expensive
that decision must be when the auditor can choose queries adaptively and
share observations across every declared budget.

The decision is deliberately specific: issue one certificate asserting
that the entire declared family has risk at most $\tau$, or abstain.
It does not return an arbitrary selected subset of safe budgets. This
distinction matters both for error accounting and for comparisons with
simultaneous confidence bands.

Finite-pool winner-rank evaluation is established [2]. Envelope acquisition
and reusable best-of-N inference have close predecessors [3,4]. Clipped
inclusion probabilities, deterministic inspection of heavy items, and
truncation once little weight remains are also established [5,6]. The
candidate contribution is the complete finite characterization below for
this particular rank family and decision, together with an upper
construction that charges every acquired label. It does not introduce a
new generic sampling or sequential-testing principle.

The proof is provided in three appendices. Appendix A proves the all-grid
lower bound; Appendix B proves the cached and grouped upper bounds;
Appendix C supplies the finite-population and residual-concentration
lemmas needed by both. The main text explains the quantifiers, geometry,
and consequences before those technical arguments.

## 2. Fixed experiment and exact cost objective

There are $P\ge1$ equally weighted prompt pools, each with $m\ge1$
distinct items in a fixed total rank order, with rank 1 best. The order
includes a declared rule for ties. A query of item $(p,r)$ reveals its
fixed, correct loss $y_{p,r}\in[0,1]$ at unit cost. No labels are supplied
for free, and no trusted cross-item relationship reveals another item's
loss. Computation and auxiliary randomness are uncharged.

Fix a nonempty grid $\mathcal K\subseteq\{1,\ldots,m\}$. At budget
$n$, selection within each pool returns the best-ranked item in a uniform
$n$-subset drawn without replacement. The winner law and risk are

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}},
\qquad a_n(p,r)=\frac{w_n(r)}{P},
$$

$$
R_n(y)=\sum_{p=1}^{P}\sum_{r=1}^{m}a_n(p,r)y_{p,r}.
$$

Impossible binomial choices are zero. Each target row sums to one.
These are conditional risks on the recorded pools; the fixed losses
need not be independent across prompts or candidates. Selecting the
best of fresh independent generations would be a different experiment.

An admissible auditor may randomize, select unseen items adaptively,
reuse cached labels, and abstain. Its certificate asserts that
$R_n(y)\le\tau$ for every originally declared $n$. On every fixed table
with some $R_n(y)>\tau$, the probability of ever issuing that certificate
is at most $\delta$. On every fixed safe table it must certify after
finitely many queries almost surely, including when a risk equals
$\tau$. These requirements apply to all of $[0,1]^{Pm}$. Exact evaluation
after a full census shows that the admissible class is nonempty.

For a supplied design margin $\epsilon$, define

$$
\mathcal Y_\epsilon
=\{y:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},
$$

$$
C^*(\epsilon)=\inf_A\sup_{y\in\mathcal Y_\epsilon}
\mathbb E_y T_A(y).
$$

Here $T_A$ counts distinct labels bought before certification. One auditor
serves the entire margin class. The margin can guide its design; it is
not trusted evidence that an unknown table is safe. Expectations concern
audit randomization on a fixed table. The comparator permits correlated
sampling and even empty-query certification lotteries, provided global
validity holds. It places no computational restriction on the auditor.

## 3. The finite-cost formula

Write $a=\min\mathcal K$, $L=\log(1/\delta)$, and

$$
H=\frac{\tau L}{\epsilon^2},
\qquad e_r=\max_{n\in\mathcal K}w_n(r).
$$

Let $q_a(k)$ be the smallest budget's probability of selecting beyond
rank $k$, and let $k_\epsilon$ be the first prefix leaving at most
$\epsilon$ such mass:

$$
q_a(k)=\frac{\binom{m-k}{a}}{\binom{m}{a}},
\qquad k_\epsilon=\min\{0\le k\le m:q_a(k)\le\epsilon\}.
$$

Define the clipped sum and the final functional by

$$
G=\sum_{r=1}^{m}\min\{P,He_r\},
\qquad F=\min\{Pk_\epsilon,G\}.
$$

**Theorem 1 (all finite grids).** If

$$
0<\tau\le\frac18,
\qquad 0<\epsilon\le\frac{\tau}{16},
\qquad 0<\delta\le\frac14,
$$

then for every finite $P,m$ and every nonempty declared grid,

$$
\frac{F}{2^{38}}\le C^*(\epsilon)\le2^{16}F.
$$

If consecutive declared budgets satisfy $n_{j+1}\ge2n_j$, then
$C^*(\epsilon)\le17F$. Singletons satisfy this spacing condition.
There is no density, replication, or minimum-budget restriction in
Theorem 1. Its universal constants are deliberately loose and do not
claim an optimal leading coefficient.

The two terms in $F$ describe different finite effects. Since the rows
and envelope decrease with rank,

$$
G=\min_{0\le k\le m}
\left\{Pk+H\sum_{r>k}e_r\right\}.
$$

Increasing $k$ changes the expression by $P-He_{k+1}$; its nondecreasing
increments prove the identity. The clipped term pays once for heavy
items, while assigning smaller costs to lighter items. Algebraically,
it is the expected sample size of classical inclusion probabilities
$\min\{1,He_r/P\}$ [5]. This correspondence alone does not prove a
certification-cost optimum.

The prefix term has a deterministic interpretation. Query every prompt
at ranks $1,\ldots,k_\epsilon$. All larger budgets have no more tail
mass than budget $a$, so the known prefix plus $q_a(k_\epsilon)$ bounds
every risk. On $\mathcal Y_\epsilon$ all those bounds pass. If they fail
on another table, acquire the remaining relevant labels and evaluate the
family exactly. This is globally valid and completes on every safe table.
Its margin-class cost is at most $Pk_\epsilon$, even as $\delta$ tends
to zero. Tail truncation is an established weighted-query idea [6]; the
theorem's additional claim is its role in the matching finite formula.

## 4. A cached likelihood construction

The separated-grid upper bound has a simple description using classical
conservative likelihood-ratio tests [7]. Put $\theta=\tau-\epsilon$ and

$$
u=\log\frac{1-\theta}{1-\tau},
\qquad d=\operatorname{kl}(\operatorname{Ber}(\theta),
\operatorname{Ber}(\tau)),
$$

$$
c=\frac{L+u}{d},
\qquad B_c=\sum_{r=1}^{m}
\min\left\{P,c\sum_{n\in\mathcal K}w_n(r)\right\}.
$$

**Theorem 2 (cached upper bound).** For any grid, whenever
$0<\epsilon<\tau<1$ and $0<\delta<1$, an admissible auditor has
margin-class expected distinct-label cost at most $B_c$. Consequently,
$C^*(\epsilon)\le\min\{Pk_\epsilon,B_c\}$.

Process the declared budgets in a fixed order, with an independent iid
proposal stream of item law $a_n$ for each budget. All streams share one
label cache. Buy the label on the first proposal of an item. On *every*
proposal, including a cache hit, generate a fresh independent coin
$B\sim\operatorname{Ber}(y_{p,r})$. For a fixed table the coins within
the current stream are iid with mean $R_n(y)$. The log-likelihood update
for a coin value $B$ is

$$
B\log\frac{\theta}{\tau}
+(1-B)\log\frac{1-\theta}{1-\tau}.
$$

Pass a budget when the cumulative sum reaches $L$. Also pass by exact
evaluation if all its positive-support labels have been acquired and its
risk is at most $\tau$; terminate without certification if exact
evaluation finds it unsafe. Certify the family only after every budget
passes. The finite iid proposal stream visits its entire positive support
almost surely, so this exact check supplies completion on boundary-safe
tables. Every first acquisition remains charged.

On a fixed unsafe budget, the likelihood multiplier has expectation at
most one, so its probability of crossing $1/\delta$ is at most
$\delta$. A false family certificate requires passage of any one fixed
unsafe budget. Thus each component may use allowance $\delta$, without
division by the number of budgets. This is ordinary intersection-union
logic for an all-pass assertion; it does not give individually selectable
target conclusions.

On a margin-class table the mean log increment is at least $d$, and the
upward overshoot is at most $u$. Bounded stopping and monotone convergence
give expected proposals at most $c$ per budget. For any item $i$, its
probability of being acquired is at most one and at most its expected
total number of proposals:

$$
\Pr\{i\ \mathrm{is\ acquired}\}
\le\min\left\{1,c\sum_{n\in\mathcal K}a_n(i)\right\}.
$$

Summing over actual items gives $B_c$. Caching does not remove repeated
proposals from the statistical stream. Reusing the same auxiliary coin
on a repeated item would invalidate its iid argument. The proof charges
distinct labels, not an equally small number of proposals or units of
runtime.

For a factor-two-separated grid, finite winner-rank geometry gives
$\sum_n w_n(r)\le8e_r$. Under Theorem 1's parameter range,
$c\le17H/8$, so $B_c\le17G$. Choosing the deterministic prefix
instead whenever its bound is smaller proves $17F$. A finite proposal
cap with a fully charged fallback gives $B_c+\eta$ for any prescribed
$\eta>0$; Appendix B accounts for that surcharge explicitly.

For an arbitrary grid, Appendix B groups budgets between factor-four
representatives, inspects a shared prefix, and tests the remaining group
risks through one empirical cumulative loss curve. Monotone likelihood
ratios control a whole group without a target-count union bound. A
geometric mixture inequality then bounds the sum of residual masses by
the envelope tail, giving the more precise upper coefficient 61440,
which is less than $2^{16}$.

## 5. Why the same functional is unavoidable

The lower bound must place expensive inputs *inside* the entire safe
margin class. A difficult table for one budget, or a different safe prior
for each rank band, does not justify adding the resulting costs. Adaptive
fixed-table query bounds are classical [8], as are rare-risk perturbations
across geometric score bands [4]. The proof here combines two common-safe
constructions to cover all finite regimes.

Choose representatives by starting at $a=\min\mathcal K$ and taking
the next declared budget at least four times the preceding one. Their
rank bands, from just beyond $m/(4a_j)$ through $m/a_j$, are disjoint
and each has constant mass under its own representative. When many such
bands contain sufficiently many items, a deterministic head removes the
heavy coordinates. A product prior on the suffix is conditioned on the
exact whole-family safe event. A maximal inequality for monotone rows
controls the exceptional mass without a grid-size penalty.

Information is calculated under the *unconditioned* product laws using
finite capped transcripts, with the exceptional mass charged explicitly.
Each retained band requires order $H$ expected acquisitions under the
same conditional safe prior, so their costs add. This supplies the broad
scale part of the lower bound.

When no broad scale remains and the smallest budget is below $m/4$,
that budget dominates all larger budgets on a tail of constant mass.
Centered fixed-count
perturbations in disjoint tail blocks preserve the smallest-budget risk
exactly at $\tau-\epsilon$; domination keeps every null table safe for
the whole grid. Changing one block's count gives a strictly unsafe
alternative. The finite-population testing lemma in Appendix C controls
depletion even under adaptive acquisition. Conditional-tail geometry
compares the resulting block costs with $F$.

Appendix A also handles the high-budget endpoint using Appendix C's
rankwise and hidden-subset bounds. The latter is needed for small prompt
counts. The uniform-tail case covers budget one; finite endpoint checks
cover small pools and partial supports. These arguments account for both
clipping and deterministic truncation, rather than inserting a census cap
into an asymptotic lower bound.

## 6. A subcensus regime and a finite limitation

Take one pool, $m=2^d$, and every dyadic budget:

$$
P=1,\qquad\mathcal K=\{1,2,4,\ldots,m\},
\qquad\epsilon^2=\frac{\tau\log m}{m}.
$$

Fix admissible $\tau,\delta$. For sufficiently large $m$ the margin
condition holds and $H=Lm/\log m$. The representative bands with
$m/a_j\ge32H$ number $\Theta(\log\log m)$, giving the lower rate.
For the upper rate, $e_r\le2/r$ when $r\ge2$ bounds the clipped sum by
order $H[1+\log(m/H)]$. The separated-grid construction therefore gives

$$
C^*(\epsilon)
=\Theta\!\left(\frac{m\log\log m}{\log m}\right)=o(m).
$$

Constants here may depend on the fixed $\tau,\delta$. For this sequence,
the earlier blanket bound of order
$\min\{m,H\sum_r e_r\}$ was only of census order because
$\sum_r e_r=\Theta(\log m)$. The clipped analysis resolves a smaller
matching order. This compares proved guarantees, not observed model
performance or the actual cost on every individual safe table.

A separate exact finite analysis [1] concerns 32 prompts, 64 candidates,
budgets $1,2,4,8,16,32,64$, threshold $1/10$, margin $1/160$, and error
allowance $1/20$. Its current bounds are

$$
1103.263793259\le C^*(1/160)\le\frac{383040}{199}.
$$

The upper endpoint is approximately 1924.824 labels. It certifies without
observing a label with probability $9/199$; otherwise it runs a charged
evidence branch whose error allowance is $1/200$ and whose uniform
expected cost is at most 2016. Its accounting is

$$
\frac9{199}+\frac{190}{199}\frac1{200}=\frac1{20},
\qquad\frac{190}{199}\,2016=\frac{383040}{199}.
$$

This is a permitted certification lottery under the stated objective.
The default callback disables blind certification and has the separate
2016-label guarantee at error $1/200$. The mixed bound improves 1934.2
by about 9.376 labels, or 0.485%; it is not an exact optimum or a measured
LLM saving. Here $F=2048$, so the generic theorem does not improve this
instance-specific certificate. The complete
[checkpoint proof](../../docs/finite-checkpoint-theorem.md) and
[lower-certificate proof](../../docs/monotone-placement-theorem.md) remain
separate; they are not reproduced in the appendices of this manuscript.

## 7. Evidence, attribution, and scope

The saved all-grid checker covers 27,600 exact finite configurations,
including all nonempty grids through pool size ten and specified larger
grids. It checks the finite geometry, centered slices, mixture bounds,
and likelihood identities. Its output reproduced byte for byte in a
separate run. These are arithmetic and implementation checks; they do
not replace the proofs' universal quantifiers or constitute independent
human verification [1].

The rational callback reference implements the cached construction with
exact integer sampling, conservative likelihood arithmetic, a finite
proposal cap, and fully charged fallback. Under its stated conditions it
retains a $17F+\eta$ bound. It has bounded rational input and resource
limits, whereas the ideal theorem allows real losses. It does not
implement the arbitrary-grid grouped construction. Mathematical
admissibility for all real tables must not be inferred from that narrower
program alone.

The relevant foundations are substantial. Weighted finite-population
confidence sequences and use of side information appear in Shekhar et
al. [9]; sequential stratified inference and careful sample accounting
appear in Spertus et al. [10]. Fitas [3] already studies envelope designs
and adaptive acquisition limits for best-of-N evaluation. Sarkar and
Baichoo [4] develop curve certification, multiscale lower bounds, and
deterministic-grade reuse. Their experiments and outputs differ from
the present all-pass fixed-table problem; that difference requires a
comparison of theorems and reductions, not dismissal of their results.

The older weighted-query comparison is only partially resolved. Wirth's
2010 primary talk [6] explicitly presents heavy-item inspection followed
by residual sampling, including its confidence logarithm, and deterministic
tail truncation for geometric weights. Thus those mechanisms are not new
here. The final 2011 journal proof [11] was not obtained. Its precise
finite-size conditions, expected-cost quantifiers, and possible reductions
to the present safe-side family objective remain unchecked. The bounded
source comparison does not establish scientific priority.

The theorem assumes correct fixed labels and known ranks. It does not
validate a grader or a harm rubric, account for noisy repeated labels,
adapt to an unknown margin with the same guarantee, or infer safety on
new prompts. An omitted budget is outside the certificate. Computation
may greatly exceed acquired-label cost. No real-model output or human
annotation study supports the claimed rates. The artifact makes a
specific mathematical statement inspectable; practical usefulness,
independent correctness, and research ownership remain separate tests.
