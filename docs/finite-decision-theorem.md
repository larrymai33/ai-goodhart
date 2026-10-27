# A finite decision lower bound for the original full grid

Candidate result, 27 October 2026. For the original 32-prompt, 64-item
geometry and its complete declared grid, an exact finite calculation gives
a lower bound of **784.185148748 expected distinct labels**. A full census
costs 2,048 labels, less than 2.612 times this lower bound. The decision,
margin class, global validity requirement, and all-safe completeness
requirement are unchanged.

The Lagrange penalty and backward recursion are classical sequential-testing
tools; see [Novikov (2008), Section 2, equation (7), Section 4, Theorem 4,
equations (50)--(51), and Remark 5](https://arxiv.org/html/0811.1297v1).
The argument below specializes them to a finite-population relaxation and
proves its null-completeness restriction directly. It does not assert a new
sequential-testing method. The [priority comparison](finite-decision-priority.md)
records the comparison and its limitations.

The calculation supplies a lower certificate, not a new audit engine or
an exact minimax value. The argument and arithmetic were developed and
checked with Codex assistance; they have not received independent human
review. See the [contribution disclosure](provenance.md).

## 1. The original objective and the quantitative result

Fix

$$
P=32,\qquad m=64,\qquad
\mathcal K=\{1,2,4,8,16,32,64\},
\qquad\tau=\frac1{10},\quad
\epsilon=\frac1{160},\quad\delta=\frac1{20}.
\tag{1}
$$

There are $P$ equally weighted prompt pools, each containing $m$ distinct
items in a fixed total rank order, rank 1 being best. Querying an item
reveals its fixed, correct loss $y_{p,r}\in[0,1]$ at unit cost. There are
no free actual labels or known relationships that reveal other labels
without querying them. Computation is not charged.

For budget $n$, the selector draws a uniform $n$-subset without replacement
and returns its best-ranked member. Its rank weights and risks are

$$
w_n(r)=\frac{\binom{64-r}{n-1}}{\binom{64}n},
\qquad
R_n(y)=\frac1{32}\sum_{p=1}^{32}\sum_{r=1}^{64}w_n(r)y_{p,r}.
\tag{2}
$$

Impossible binomial choices are zero. An admissible auditor may randomize,
choose unseen items adaptively, and abstain. It issues one certificate
asserting $R_n(y)\le1/10$ for every originally declared $n\in\mathcal K$.
For every fixed table with some $R_n(y)>1/10$, its probability of ever
issuing that certificate is at most $1/20$. On every fixed safe table,
including boundary-safe tables, it must certify after finitely many queries
almost surely. These requirements hold on the entire fractional-loss
space $[0,1]^{2048}$.

Let $T_A(y)$ be the number of distinct labels acquired before certification
on a safe table, and define

$$
\mathcal Y_\epsilon
=\{y:\max_{n\in\mathcal K}R_n(y)\le3/32\},
\qquad
C^*(1/160)=\inf_A\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT_A(y).
\tag{3}
$$

The auditor may know the design margin; the margin is not trusted evidence
of safety. This is the same objective as in the
[nonzero theorem](nonzero-minimax-theorem.md).

**Theorem and exact-arithmetic corollary.** Let $W_0(0)$ and $D$ be the
integers defined by the recurrence in Section 4 with
$N=1024$, $k=192$, $d=13$, and $\lambda=2048$. Then

$$
C^*(1/160)\ge\frac{W_0(0)}D-\frac{2048}{20}.
\tag{4}
$$

The exact integer certificate in Section 5 gives

$$
\boxed{\qquad
784.185148748\le C^*(1/160)\le2048.
\qquad}
\tag{5}
$$

The decimal on the left is rounded downward. The upper bound is the
zero-error census followed by exact evaluation of all declared risks;
it satisfies all-safe completeness. Consequently

$$
\frac{2048}{784.185148748}<2.612.
\tag{6}
$$

The lower statement concerns worst-case expected cost for one admissible
auditor over the margin class. It does not state that every safe table,
or every run on a difficult table, requires that many queries.

## 2. A common-safe prior for every declared target

Use only the $N=32\cdot32=1024$ cells at ranks $33,\ldots,64$. In both
priors all other cells have fixed loss zero. Under the null prior $\Pi$,
uniformly choose exactly $k=192$ tail cells to have loss one. Under the
alternative $Q$, uniformly choose exactly $k+d=205$ tail cells to have
loss one. These are proof distributions over fixed correct binary tables,
which are a subclass of the original fractional-loss experiment.

To verify whole-family safety, the adjacent-budget weight identity gives,
for $1\le n<64$ on positive weights,

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{n+1}{n}\frac{64-r-n+1}{64-n}\le1
\quad\Longleftrightarrow\quad (n+1)r\ge65.
\tag{7}
$$

For every $r\ge33$, this condition holds for all $1\le n<64$. Terminal
zeros preserve the inequalities. Therefore

$$
w_n(r)\le w_1(r)=\frac1{64}
\quad(r\ge33, n\in\mathcal K).
\tag{8}
$$

Every nonnegative table supported on this tail has $R_n\le R_1$. On
every table in the null support,

$$
R_1=\frac{192}{2048}=\frac3{32}
=\frac1{10}-\frac1{160}.
\tag{9}
$$

Thus every null table belongs to the full original efficiency class.
On every alternative table,

$$
R_1=\frac{205}{2048}
=\frac1{10}+\frac1{10240}>\frac1{10}.
\tag{10}
$$

Every alternative is therefore unsafe for the original whole-family
decision. An admissible auditor certifies with probability one under
$\Pi$ and with probability at most $1/20$ under $Q$.

## 3. A more informative finite experiment

For a lower bound, give a relaxed auditor the outside zero labels for free
and tell it that the table comes from one of these two priors. Require
only null completeness and the alternative certificate-probability bound.
An original auditor can be simulated in this more informative experiment:
answer its outside queries with the known zeros and acquire its requested
unseen tail labels. Certificate probabilities under both priors are
unchanged, and the charged tail count is no larger than the original total
distinct-label count. A lower bound for this relaxation consequently
applies to the original objective.

Repeated queries can be cached. Under either prior, conditional on all
queried identities and labels, the unseen positive positions remain
uniform. Any choice of an unseen tail cell has the same conditional bit
law. If $t$ distinct tail cells have been observed and $s$ were positive,
then, on histories where the relevant hypothesis is possible,

$$
\Pi(X_{t+1}=1\mid t,s)=\frac{k-s}{N-t},
\qquad
Q(X_{t+1}=1\mid t,s)=\frac{k+d-s}{N-t}.
\tag{11}
$$

This remains true for adaptive identities, interleaved outside queries,
and internal randomization. History beyond $(t,s)$ carries no information
about the remaining labels in the relaxed experiment.

At a history impossible under the null, the relaxed auditor may abstain
without cost. On a null-possible history it cannot abstain with positive
conditional probability, because null completeness would fail. Delays
and outside zero queries reveal no information and can be suppressed.
If an original process were to remain indefinitely at a null-possible
history without certifying or requesting another tail cell, that behavior
would likewise violate completeness. Its conditional no-information
behavior is the same under the two hypotheses.

The relaxed problem can therefore have horizon $N$: after all tail cells
are known, their totals distinguish the priors exactly; certify the null
and abstain on the alternative. This modification adds no tail queries or
false certificates. The resulting finite problem allows all policies
needed for the lower comparison, including randomized ones.

## 4. Ordered-prefix weights and weak duality

Let $\binom ab=0$ unless $0\le b\le a$, and put

$$
D=\binom Nk\binom N{k+d},
\qquad
A_t(s)=\binom{N-t}{k-s}\binom N{k+d},
\qquad
B_t(s)=\binom{N-t}{k+d-s}\binom Nk.
\tag{12}
$$

For a particular ordered bit history of length $t$ with $s$ positives,
its respective prior probabilities are $A_t(s)/D$ and $B_t(s)/D$.
These are not probabilities of the aggregate count state: that would
include an additional factor $\binom ts$. Pascal's identity gives
$A_t(s)=A_{t+1}(s)+A_{t+1}(s+1)$ and the corresponding identity for $B$.

For any fixed $\lambda\ge0$, consider the relaxed Lagrangian objective

$$
\mathbb E_\Pi T+\lambda Q(\text{certificate}),
\tag{13}
$$

subject to certification with probability one under $\Pi$. Define the
unnormalized cost of a subtree rooted at one particular history by
backward induction. Set $W_N(s)=0$. At states with $A_t(s)=0$, set
$W_t(s)=0$, representing immediate abstention. Otherwise, for $t<N$, use

$$
\boxed{\quad
W_t(s)=\min\left\{
\lambda B_t(s),
A_t(s)+W_{t+1}(s)+W_{t+1}(s+1)
\right\}.
\quad}
\tag{14}
$$

Immediate certification costs $\lambda B_t(s)$. Continuing pays one
query under the null, with weight $A_t(s)$, and then sums the costs of
the two possible next bits. The child weights already include their
probabilities, so no extra transition factors or $\binom ts$ factors
appear. If $B_t(s)=0$, certification is free. At time $N$, the only
null-possible count is $s=k$, which is alternative-impossible; hence the
terminal zero value includes certain null certification.

Future conditional laws depend only on $(t,s)$. Randomization between
certification and continuation gives a convex combination of their costs
and cannot improve the minimum. Backward induction proves that (14)
is the minimum of (13) over null-complete relaxed policies. A minimizing
policy completes by time $N$. Reusing the value for histories with the
same $(t,s)$ is valid: root-to-leaf child sums supply the multiplicity of
distinct ordered histories. Thus

$$
\frac{W_0(0)}D
=\inf_{\text{null-complete relaxed policies}}
\{\mathbb E_\Pi T+\lambda Q(\text{certificate})\}.
\tag{15}
$$

For any admissible original auditor, the simulation in Section 3 has
$Q(\text{certificate})\le\delta$. Weak duality therefore gives

$$
\mathbb E_\Pi T
\ge\frac{W_0(0)}D-\lambda\delta.
\tag{16}
$$

The original total count is at least this tail count. Its worst-case
expected cost on the efficiency class is at least the average over the
finite null prior. Taking the infimum over original auditors proves
(4), and more generally (16) is a lower certificate for every
$\lambda\ge0$. No claim that the chosen multiplier is globally optimal
is needed.

## 5. The exact numerical certificate

Evaluate (12)--(14) with

$$
(N,k,d,\lambda)=(1024,192,13,2048).
\tag{17}
$$

All values are integers. The numerical lower bound in (5) is certified
by the integer comparison

$$
\boxed{\quad
10^9 W_0(0)\ \ge\ 886585148748\,D.
\quad}
\tag{18}
$$

Indeed, subtracting $\lambda\delta=2048/20=102.4$ from (18), after
division by $10^9D$, gives exactly
$W_0(0)/D-\lambda\delta\ge784.185148748$.
This comparison uses no floating-point logarithms or simulation.
The accompanying [checker](../experiments/check_finite_decision.py) and
[fixed verification protocol](../experiments/finite_decision_protocol.json)
specify the reproducible finite calculation and its source checks.

An independent formulation divides each null-possible state's value by
$A_t(s)$. With $U_t(s)=W_t(s)/A_t(s)$ and
$u=(k-s)/(N-t)$, it gives

$$
U_t(s)=\min\left\{
\lambda\frac{B_t(s)}{A_t(s)},
1+(1-u)U_{t+1}(s)+uU_{t+1}(s+1)
\right\}.
\tag{19}
$$

Terms with null-impossible children have zero coefficient and are set to
zero. Alternative-impossible states and terminal states have zero value.
Exact rational evaluation using direct binomial coefficients in (19)
agrees with the integer recurrence at the root and verifies (18).
Small-instance enumeration can additionally check all relevant
deterministic stopping choices, pruning free zero-error terminal states.

The value in (18) concerns the more informative two-prior problem. Its
minimizing policy is not asserted to be a valid original auditor: it uses
free outside labels and an exact two-hypothesis restriction. The original
upper certificate used in (5) is the full census.

## 6. Interpretation and limits

Every admissible original auditor has a fixed margin-safe table on which
its expected distinct-label cost is at least the displayed lower bound.
The same common null prior establishes this statement for the complete
original grid; no declared budget was dropped. The census upper bound
places the original minimax value within the factor stated in (6).
Budget 1 supplies the unsafe alternatives and forces this lower bound.
The other declared budgets are retained through the common-safe-support
check in (8)--(9).

This does not establish the exact minimax value, a globally optimal
multiplier, improved performance on observed application data, or an
operational statistical certificate at the lower cost. It also does not
settle the unrestricted general-grid saturation formula discussed in the
[finite-saturation theorem](finite-saturation-theorem.md). The contribution
being assessed is the particular fixed-table reduction and its checked
finite certificate, with classical sequential-testing machinery and
scientific priority treated separately.
