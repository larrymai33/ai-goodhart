# A finite-density extension for nonzero best-of-n certification

Candidate theorem, 27 October 2026. This note uses the fixed experiment and
minimax objective of the [v0.8 nonzero theorem](nonzero-minimax-theorem.md).
It replaces that theorem's sufficient per-rank replication condition by a
condition on the largest target atom. It also gives a deterministic prefix
census bound and explains why a general saturation formula based only on
the number of relevant items would be false.

This is a theoretical proof construction, not a new practical audit engine.
The argument was developed and checked with Codex assistance and has not
received independent human review. Its scientific priority remains
unestablished; see the [priority screen](finite-density-priority.md), the
[report](finite-density-report.md), and the
[contribution disclosure](provenance.md).

## 1. The same finite-table objective

Fix integers $P,m\ge1$ and a nonempty declared family
$\mathcal K\subseteq\{1,\ldots,m\}$. There are $P$ equally weighted prompt
pools, each with $m$ distinct items in a fixed total rank order, with rank 1
best. A query reveals one item's fixed, correct loss $y_{p,r}\in[0,1]$ at
unit cost. There are no free actual labels or known relationships that
reveal another item's label without querying it. Computation is not
charged. The selector for budget $n$ draws a uniform $n$-subset without
replacement and returns its best-ranked member. Write

$$
\begin{aligned}
w_n(r)&=\frac{\binom{m-r}{n-1}}{\binom mn},&
a_n(p,r)&=\frac{w_n(r)}P,\\
R_n(y)&=\sum_{p,r}a_n(p,r)y_{p,r},&
Z&=\sum_{r=1}^m\max_{n\in\mathcal K}w_n(r).
\end{aligned}
\tag{1}
$$

Impossible binomial choices are zero. An admissible auditor may randomize,
choose unseen items adaptively, and abstain. It issues one whole-family
certificate asserting $R_n(y)\le\tau$ for every originally declared $n$.
For every fixed table with some $R_n(y)>\tau$, its probability of ever
issuing that certificate must be at most $\delta$. For every fixed safe
table it must certify after finitely many queries almost surely. These
requirements apply to all tables in $[0,1]^{Pm}$.

For a supplied design margin $\epsilon$, let

$$
\mathcal Y_\epsilon
=\{y:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},
\qquad
C^*(\epsilon)=\inf_A\sup_{y\in\mathcal Y_\epsilon}
\mathbb E_y T_A(y),
\tag{2}
$$

where $T_A$ counts distinct queried items before certification. One auditor
serves the entire class. It may know $\epsilon$, but the margin is not
trusted evidence of safety. This is exactly the objective in the v0.8
theorem, including validity outside the efficiency class and completeness
on boundary-safe tables.

Put

$$
N=\max\mathcal K,\qquad a=\min\mathcal K,\qquad
L=\log(1/\delta),\qquad H=\frac{\tau L}{\epsilon^2},\qquad
\rho=\frac{N}{Pm},\qquad M=\frac1\rho=\frac{Pm}{N}.
\tag{3}
$$

Here $\rho$ is the largest item weight over all targets, and $M$ need not
be an integer. Define the prefix length

$$
k_\epsilon
=\min\left\{k\in\{0,\ldots,m\}:
\frac{\binom{m-k}{a}}{\binom ma}\le\epsilon\right\}.
\tag{4}
$$

## 2. Statement and relation to the replication condition

**Theorem.** Suppose

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
\tag{5}
$$

For every nonempty declared family,

$$
C^*(\epsilon)
\le\min\{P k_\epsilon,\;49152 ZH\}.
\tag{6}
$$

If, additionally,

$$
\boxed{\quad
\rho\le\frac{\epsilon^2}{4\tau\log(4/\delta)}
\quad}
\qquad\text{equivalently}\qquad
M\ge\frac{4\tau\log(4/\delta)}{\epsilon^2},
\tag{7}
$$

then

$$
\boxed{\quad
\frac{ZH}{16384}
\le C^*(\epsilon)
\le\min\{P k_\epsilon,\;49152 ZH\}.
\quad}
\tag{8}
$$

The constants are loose. The original sufficient condition
$P\ge L/\epsilon^2$ implies (7): since $N/m\le1$, $\tau\le1/8$, and
$\log(4/\delta)=L+\log4\le2L$,

$$
\frac{4\tau N\log(4/\delta)}{m\epsilon^2}
\le\frac{L}{\epsilon^2}.
\tag{9}
$$

Thus (7) is a weaker sufficient condition throughout the stated parameter
range, with a slightly weaker numerical lower constant than v0.8. It can
apply with $P=1$: the required condition is then
$m/N\ge4\tau\log(4/\delta)/\epsilon^2$. It does not require many prompt
copies of each individual rank.

The proof retains a known margin, fixed correct losses, and one global
certificate. It does not establish a necessary atom condition, a general
finite-population saturation law, or simultaneous confidence bands with
selectable target conclusions.

## 3. A prefix census gives the upper bound

For a winning rank $W_n$, the exact tail is

$$
\Pr(W_n>k)=\frac{\binom{m-k}{n}}{\binom mn}.
\tag{10}
$$

This tail is nonincreasing in $n$. Query every prompt position at the
first $k_\epsilon$ ranks, then compute for each declared target

$$
U_n=\sum_{p=1}^P\sum_{r\le k_\epsilon}
a_n(p,r)y_{p,r}+\Pr(W_n>k_\epsilon).
\tag{11}
$$

Each $U_n$ is a deterministic upper bound on the unknown actual risk. On
every table in $\mathcal Y_\epsilon$,

$$
U_n\le R_n(y)+\Pr(W_n>k_\epsilon)
\le\tau-\epsilon+\epsilon=\tau.
\tag{12}
$$

Certify if every $U_n\le\tau$. Otherwise, query all remaining items with
positive weight for at least one target and evaluate the risks exactly.
The union of target supports consists of ranks $1,\ldots,m-a+1$.
This fallback certifies every other safe table in finite time and never
certifies an unsafe table. Consequently the cost on the margin class is
at most $P k_\epsilon$, with zero error.

The [v0.8 upper construction](nonzero-minimax-theorem.md) independently
gives $C^*(\epsilon)\le49152 ZH$ for all grids under (5). Choosing the
auditor with the smaller stated cost bound proves (6). No new practical
sampling procedure is needed for that statistical upper bound.

## 4. A uniform lemma for monotone target rows

The new safe-prior argument uses the following general fact. A common
ordering of all cells, rather than a union bound over budgets, controls
every monotone target row.

**Lemma.** Let $X_1,\ldots,X_D$ be independent Bernoulli variables of a
common mean $p$. Fix $v\ge p$ with $v>0$, $0<t\le2v$, and $\rho>0$.
Consider any family of nonnegative weight vectors $b$ satisfying

$$
b_1\ge b_2\ge\cdots\ge b_D\ge0,
\qquad \sum_i b_i=1,
\qquad b_1\le\rho.
\tag{13}
$$

Then, simultaneously over the entire family,

$$
\Pr\left\{\text{some }b:
\sum_i b_i(X_i-p)>t\right\}
\le\exp\left(-\frac{t^2}{4v\rho}\right).
\tag{14}
$$

**Proof.** Put $S_k=\sum_{i\le k}(X_i-p)$ and
$\lambda=t/(2v)\le1$. For $0\le\lambda\le1$,

$$
\log\mathbb E e^{\lambda(X_i-p)}
\le p(e^\lambda-1-\lambda)
\le p\lambda^2\le\lambda t/2.
\tag{15}
$$

Therefore $\exp\{\lambda(S_k-kt/2)\}$ is a nonnegative
supermartingale starting at one. Its finite-horizon maximal inequality
gives

$$
\Pr\left\{\exists k\le D:
S_k>\frac t2(k+1/\rho)\right\}
\le\exp\left(-\frac{t^2}{4v\rho}\right).
\tag{16}
$$

On the complementary event, summation by parts with $b_{D+1}=0$ gives

$$
\begin{aligned}
\sum_i b_i(X_i-p)
&=\sum_{k=1}^D(b_k-b_{k+1})S_k\\
&\le\frac t2\left[
\sum_{k=1}^Dk(b_k-b_{k+1})
+\frac1\rho\sum_{k=1}^D(b_k-b_{k+1})\right]\\
&=\frac t2(1+b_1/\rho)\le t.
\end{aligned}
\tag{17}
$$

The same prefix event establishes this for every row, proving the lemma.
Terminal zero weights and noninteger $1/\rho$ cause no change.

## 5. Product priors and an exactly safe conditional prior

Flatten the $D=Pm$ cells in increasing rank order, ordering prompts
arbitrarily within a rank. Each target row $b_i=a_n(p,r)$ is
nonnegative and nonincreasing in this order, sums to one, and has first
weight $n/(Pm)\le\rho$. Indeed,
$w_n(r+1)/w_n(r)=(m-r-n+1)/(m-r)\le1$ wherever the denominator and
the current weight are positive; terminal zeros preserve monotonicity.

Let $\Pi$ be the product distribution on binary fixed tables with every
cell having mean

$$
p=\tau-2\epsilon\ge7\tau/8>0.
\tag{18}
$$

This is a proof distribution over deterministic oracle tables, not a
stochastic-label assumption about the audit experiment. Applying the
lemma with $v=\tau$ and $t=\epsilon$ gives, for

$$
S=\{\max_{n\in\mathcal K}R_n\le\tau-\epsilon\},
\qquad \eta_S=\Pi(S^c),
$$

the bound

$$
\eta_S\le\eta:=\exp\left(-\frac{M\epsilon^2}{4\tau}\right)
\le\frac\delta4\le\frac1{16}.
\tag{19}
$$

The conditional prior $\Pi_S=\Pi(\,\cdot\mid S)$ is a common finite
distribution supported entirely on the exact efficiency class. Its labels
are not asserted to be conditionally independent. Information calculations
below use the unconditioned product priors.

Choose representatives as in the v0.8 geometric lemma: start at
$a_1=\min\mathcal K$ and repeatedly choose the smallest declared budget
at least four times its predecessor. For each representative define

$$
I_j=\{\lfloor m/(4a_j)\rfloor+1,\ldots,\lfloor m/a_j\rfloor\}.
\tag{20}
$$

The existing finite endpoint argument establishes that these bands are
disjoint, that

$$
c_j:=\sum_{r\in I_j}w_{a_j}(r)>\frac14,
\qquad J\ge Z/4,
\tag{21}
$$

including representatives close to $m$. This note uses that proved
geometric lemma without changing the bands or their endpoint conventions.

For each band $I_j$, define a product prior $Q_j$ with label mean

$$
q=p+12\epsilon=\tau+10\epsilon\le13\tau/8<1/4
\tag{22}
$$

within the band and mean $p$ outside it. Its representative risk has mean

$$
\mu_j=p+12\epsilon c_j>\tau+\epsilon.
\tag{23}
$$

For independent Bernoulli labels with possibly different means $q_i\le q$
and target weights $b_i$, the inequality
$e^{-u}-1+u\le u^2/2$ for $u\ge0$ gives

$$
\log\mathbb E e^{-t\sum_i b_i(X_i-q_i)}
\le\frac{t^2}{2}\sum_i q_i b_i^2
\le\frac{t^2q}{2M},\qquad t\ge0.
\tag{24}
$$

Optimizing $t$ and using (23) yields

$$
Q_j\{R_{a_j}\le\tau\}
\le e^{-M\epsilon^2/(2q)}
\le e^{-M\epsilon^2/(4\tau)}
\le\delta/4.
\tag{25}
$$

Thus, for any event $E$ contained in certificate issuance, fixed-table
validity gives

$$
Q_j(E)\le\delta+Q_j\{R_{a_j}\le\tau\}\le5\delta/4.
\tag{26}
$$

The alternative need not be conditioned on being unsafe. The extra
$\delta/4$ accounts explicitly for its exceptional tables.

## 6. Finite transcripts and the conditional expected cost

Fix an admissible auditor. Cache repeated queries, so transcripts need
only record first acquisitions of item labels. Let $T_j$ count distinct
queries in band $I_j$ before certification on safe tables, and put

$$
x_j=\mathbb E_{\Pi_S}T_j,
\qquad \kappa=\frac{256\epsilon^2}{\tau},
\qquad B=\left\lceil\frac{H}{512}\right\rceil
=\left\lceil\frac{L}{2\kappa}\right\rceil.
\tag{27}
$$

If some $x_j$ is infinite, the lower bound is immediate. Otherwise, stop a
transcript at certificate issuance, at its $B$th distinct query in band
$I_j$, or at an additional finite transition horizon $h$, whichever comes
first. A certificate simultaneous with the $B$th band query counts as
reaching the cap. Let $E_h$ be certification by horizon $h$ strictly before
that band cap.

Under unconditioned $\Pi$ and $Q_j$, the label of any unseen item is
independent of the observed past. Inside the band its respective means
are $p$ and $q$, giving per-query divergence

$$
\begin{aligned}
\operatorname{kl}(\operatorname{Ber}(p),\operatorname{Ber}(q))
&\le\frac{(12\epsilon)^2}{q(1-q)}\\
&\le\frac{144\epsilon^2}{(7\tau/8)(3/4)}<\kappa.
\end{aligned}
\tag{28}
$$

Outside-band queries contribute zero. Query choices, internal randomization,
and stopping decisions follow the same conditional rule given an observed
history, so they add no divergence beyond labels. On $S$, the truncated
band count is at most $T_j$; on $S^c$, it is at most $B$ regardless of the
auditor's eventual behavior. The finite-transcript chain rule therefore
gives

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
\le\kappa[(1-\eta_S)x_j+\eta_S B].
\tag{29}
$$

This calculation does not use independence under $\Pi_S$, and it does
not require any cost guarantee outside the margin class.

As $h$ increases, $E_h$ increases to the event $E$ of certification
strictly before the band cap. Completeness on each fixed table in $S$ and
Markov's inequality under the safe conditional prior give

$$
\Pi(E)\ge(1-\eta_S)(1-x_j/B).
\tag{30}
$$

Suppose for a contradiction that $x_j<B/8$. Then

$$
\Pi(E)\ge(15/16)(7/8)>3/4.
\tag{31}
$$

For all sufficiently large finite $h$, $\Pi(E_h)\ge3/4$, while (26)
gives $Q_j(E_h)\le5\delta/4$. Data processing and the elementary binary
entropy bound $\operatorname{kl}(u,v)\ge u\log(1/v)-\log2$ imply

$$
\begin{aligned}
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
&\ge\frac34[L-\log(5/4)]-\log2\\
&\ge L/8.
\end{aligned}
\tag{32}
$$

For the last inequality use $L\ge2\log2$ and
$\log2\ge3\log(5/4)$, equivalently $2\ge125/64$.
On the other hand, (5) implies
$\kappa\le\tau\le1/8\le L/8$. The ceiling in (27) consequently gives

$$
\kappa B\le L/2+\kappa\le5L/8.
\tag{33}
$$

Equations (19), (29), and the supposition $x_j<B/8$ now yield

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
<\kappa B(1/8+1/16)
\le15L/128<L/8,
\tag{34}
$$

contradicting (32). Hence

$$
x_j\ge B/8\ge H/4096.
\tag{35}
$$

Only the certificate event probabilities were taken to their increasing
limit in this argument. All KL calculations use a sufficiently large
finite horizon; no unproved identity at an unbounded stopping time is
needed.

The same safe conditional prior serves every disjoint band, so their
distinct query counts add. Using $J\ge Z/4$,

$$
\mathbb E_{\Pi_S}T
\ge\sum_jx_j\ge\frac{ZH}{16384}.
\tag{36}
$$

Some fixed table in the finite support of $\Pi_S$ has at least this
expected cost. Taking the supremum over the efficiency class and then the
infimum over admissible auditors proves (8).

## 7. Why item-count saturation fails outside this regime

The density condition is sufficient, not a characterization of every
finite grid. Neither the total table size nor the number of positive
target atoms generally supplies a matching saturation term.

First, for $\mathcal K=\{m\}$, only rank 1 matters. Querying those $P$
items determines the risk exactly. Thus $C^*(\epsilon)\le P$, although
$Z=1$ and $Pm$ can be arbitrarily larger. In particular,
$\min\{Pm,ZH\}$ cannot be a general matching lower rate.

Even replacing $Pm$ by the union's positive-support size is insufficient.
For an explicit sequence, take integers $j\ge7$ and set

$$
P=1,\quad \tau=1/8,\quad\delta=1/4,\quad
\epsilon=2^{-j},\quad m=2^{3j},\quad\mathcal K=\{m/2\}.
\tag{37}
$$

The target has $m/2+1$ positive-weight ranks and $Z=1$. For $k\le m/2$,
its exact winning-rank tail satisfies

$$
\Pr(W_{m/2}>k)
=\frac{\binom{m-k}{m/2}}{\binom m{m/2}}
=\prod_{r=0}^{k-1}\frac{m/2-r}{m-r}
\le2^{-k}.
\tag{38}
$$

Querying the first $j$ ranks therefore certifies every margin-class table
by the deterministic upper-bound rule (11). If that rule fails, a census
of the remaining positive-support items restores all-safe completeness;
the auditor still has zero error. Consequently

$$
C^*(2^{-j})\le j,
\qquad
\min\{m/2+1,ZH\}=H=\frac{\log4}{8}\,2^{2j}.
\tag{39}
$$

Their ratio is unbounded. Thus even a support-adjusted census formula
misses the effect of small tail weights. Equation (6) accounts for one
such effect through $k_\epsilon$; it does not claim that this prefix bound
is minimax optimal in every remaining regime.

## 8. Scope of the extension

The proved change is the larger finite-table regime in which the exact
grid envelope $Z$ determines the minimax order, together with a simple
additional upper bound and counterexamples to proposed saturation laws.
The lower proof's common safe prior is obtained by conditioning; its
information calculation remains under product priors and explicitly pays
for exceptional safe and alternative table mass.

The note does not establish a new concentration principle, a new
geometric-band method, or scientific priority for their combination. It
does not supply an unknown-margin guarantee, useful numerical constants,
a replacement audit engine, or guarantees for new prompts, changing
candidates, or noisy labels. Those questions and independent human review
remain outside the theorem proved here.
