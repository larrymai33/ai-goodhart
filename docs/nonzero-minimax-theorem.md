# Nonzero finite-table minimax certification for arbitrary best-of-n grids

Candidate result, 26 October 2026. The zero-table cost comparisons do not
extend to arbitrary safe tables through a pointwise optimum: a competing
auditor can encode an instance-specific reference. This note instead uses
one auditor's worst-case cost over a specified margin class. It gives
matching order bounds that allow positive observations, with an additional
replication condition for the lower bound.

The possible contribution is the combined finite-table theorem below, not a
new concentration inequality, a new bandwise information lower bound, or a
new practical audit engine. Closely related best-of-n work already uses
geometric groups, disjoint bands, rare-event variance, and adaptive
transcript KL. Scientific priority for this precise combination remains
unestablished. Section 8 makes that comparison explicit. The proof was
developed with substantial Codex assistance and separate agent review; it
has not received independent human review. See the
[contribution disclosure](provenance.md).

## 1. Fixed experiment and minimax objective

Fix integers $P,m\ge1$ and a nonempty declared family

$$
\mathcal K\subseteq\{1,\ldots,m\}.
$$

There are $P$ equally weighted prompt pools, each containing $m$ distinct
items in a fixed total rank order, with rank 1 best. Querying an item reveals
its fixed, correct loss $y_{p,r}\in[0,1]$ at unit cost. There are no free
actual labels or known relationships that reveal another item's label
without querying it. Computation is not charged. All probability statements
condition on this finite table; no independently generated prompts or
labels are assumed.

For a budget $n\in\mathcal K$, the selector draws a uniform $n$-subset
without replacement and returns its best-ranked member. Its weights and
fixed-table risk are

$$
\begin{aligned}
w_n(r)&=\frac{\binom{m-r}{n-1}}{\binom mn},&
a_n(p,r)&=\frac{w_n(r)}P,\\
R_n(y)&=\sum_{p=1}^P\sum_{r=1}^m a_n(p,r)y_{p,r},&
e(r)&=\max_{n\in\mathcal K}w_n(r),\\
Z&=\sum_{r=1}^m e(r),&D&=Pm.
\end{aligned}
\tag{1}
$$

Impossible binomial choices are zero. Each target row is nonnegative and
sums to one. In particular $Z\ge1$. The rank-weight identity is established
prior work; see [the finite-pool setup](theory.md).

Fix $0<\tau<1$ and $0<\delta<1$. An admissible auditor may randomize,
choose unseen items adaptively, and abstain. Its single whole-family
certificate asserts

$$
R_n(y)\le\tau\qquad\text{for every }n\in\mathcal K.
\tag{2}
$$

It must satisfy both requirements:

1. For every fixed table in $[0,1]^D$ with some $R_n(y)>\tau$, the
   probability of ever issuing (2) is at most $\delta$.
2. For every fixed table with all $R_n(y)\le\tau$, it issues (2) after
   finitely many queries almost surely.

Let $T_A(y)$ count distinct items queried before the first certificate on a
safe table. An auditor can cache repeat queries without changing its law or
distinct-label cost, so lower-bound transcripts may list only first queries
of items. Empty-query certification lotteries are allowed. A full census
followed by exact evaluation is admissible.

For a supplied design margin $0<\epsilon<\tau$, define

$$
\mathcal Y_\epsilon
=\{y\in[0,1]^D:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},
\qquad
C^*(\epsilon)
=\inf_A\sup_{y\in\mathcal Y_\epsilon}\mathbb E_y T_A(y).
\tag{3}
$$

The infimum uses one admissible auditor for the entire class. The auditor
may know $\epsilon$, but validity and all-safe completeness hold outside
$\mathcal Y_\epsilon$ as well. Thus the margin is a parameter for the cost
guarantee, not trusted evidence of safety. This worst-case objective removes
the freedom to choose a different matching support prediction for each
table; the [pointwise benchmark limitation](nonzero-cost-limits.md) concerns
a different order of quantifiers.

## 2. Finite theorem and its scope

Put $L=\log(1/\delta)$.

**Theorem.** Suppose

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
\tag{4}
$$

For every nonempty declared family $\mathcal K\subseteq\{1,\ldots,m\}$,

$$
C^*(\epsilon)
\le\min\left\{Pm,\frac{49152\,Z\tau L}{\epsilon^2}\right\}.
\tag{5}
$$

If, additionally,

$$
P\ge\frac{L}{\epsilon^2},
\tag{6}
$$

then

$$
\boxed{\quad
\frac{Z\tau L}{12000\,\epsilon^2}
\le C^*(\epsilon)
\le\min\left\{Pm,\frac{49152\,Z\tau L}{\epsilon^2}\right\}.
\quad}
\tag{7}
$$

The constants are deliberately loose. The rate retains the exact envelope
normalizer of the declared grid. For a singleton family $Z=1$, so a general
replacement by $\log(\max\mathcal K)$ would be incorrect. No budget 1 is
required and no missing budgets are inserted into the certificate.

Condition (6) is a strong sufficient replication condition for this lower
bound. It is not the small-atom condition in the
[zero-table sharp-grid theorem](sharp-grid-structure.md), and it must not be
replaced by that condition. No matching finite-population saturation formula
is proved when (6) fails.

The theorem concerns a single assertion that all originally declared risks
are at most the threshold. It does not return simultaneous confidence bands,
authorize partial certificates when the whole family fails, or support an
arbitrarily selected subset using the same error accounting. The absence of
an extra family-cardinality logarithm must be interpreted in light of this
weaker output requirement. Unknown-margin adaptation is not established.

## 3. Representative groups and monotone likelihood ratios

Choose $a_1=\min\mathcal K$. After $a_j$, choose the smallest declared
budget at least $4a_j$, if one exists. Stop otherwise, and let $J$ be the
number of representatives. The corresponding groups partition
$\mathcal K$, with each member satisfying

$$
a_j\le n<4a_j.
\tag{8}
$$

For $a\le n$, the rank laws satisfy

$$
w_n(r)\le\frac na w_a(r).
\tag{9}
$$

On the positive support of $w_n$, this follows from

$$
w_n(r)=\frac nm\prod_{u=1}^{r-1}
\left(1-\frac{n-1}{m-u}\right):
$$

each factor is nonnegative and decreases with $n$. If $w_n(r)=0$, the
inequality is immediate. Its support is contained in that of $w_a$.

For each representative put

$$
I_j=\{\lfloor m/(4a_j)\rfloor+1,\ldots,\lfloor m/a_j\rfloor\}.
\tag{10}
$$

These rank bands are disjoint because $a_{j+1}\ge4a_j$. Each satisfies

$$
c_j:=\sum_{r\in I_j}w_{a_j}(r)>\frac14.
\tag{11}
$$

Here is a finite endpoint argument. Write $a=a_j$,
$h=\lfloor m/a\rfloor\ge1$, and
$\ell=\lfloor m/(4a)\rfloor=\lfloor h/4\rfloor$. If $W_a$ is the
winning rank, a union bound gives
$\Pr(W_a\le\ell)\le a\ell/m\le1/4$. Also

$$
\Pr(W_a>h)
=\frac{\binom{m-h}{a}}{\binom ma}
\le(1-h/m)^a\le e^{-ah/m},
\qquad \frac{ah}{m}>\frac h{h+1}.
\tag{12}
$$

If the numerator binomial coefficient is impossible, the probability is
zero and the bound still holds. For $h\le3$, $\ell=0$, and band mass is
greater than $1-e^{-1/2}>1/4$. For $h\ge4$, it is greater than
$3/4-e^{-4/5}>1/4$. This also covers $a=m$ and $m=1$.

Disjointness and (11) give $J\le4Z$. Conversely (9) gives
$e(r)\le4\sum_{j=1}^Jw_{a_j}(r)$, and summation gives $Z\le4J$. Thus

$$
\frac Z4\le J\le4Z.
\tag{13}
$$

Within a group based at $a$, define

$$
h_n(r)=\frac{w_n(r)}{w_a(r)}
\quad\text{on the positive support of }w_a.
\tag{14}
$$

Extend it by zero after that support. Then $0\le h_n(r)\le4$, and
$h_n$ is nonincreasing in rank. On adjacent positive weights,

$$
\frac{h_n(r+1)}{h_n(r)}
=\frac{m-r-n+1}{m-r-a+1}\le1.
\tag{15}
$$

The numerator's terminal zeros preserve monotonicity. For $n=a$, the ratio
is one on its support; for $a=m$, that support has one rank. No division by
a zero representative weight is used. The representative construction and
band-mass argument also appear in the existing sharp-grid proof; their use
here does not create a new geometric grouping principle.

## 4. One cumulative loss curve controls a whole group

Fix a group based at $a$. Draw items independently with replacement from
the item distribution $a_a(p,r)$. On drawing an item $I$, query its loss
if needed and generate a fresh independent auxiliary coin
$B\sim\operatorname{Bernoulli}(y_I)$. A repeated item uses its cached loss
and a new coin. For every fixed fractional-loss table, the resulting pairs
$(\operatorname{rank}(I_t),B_t)$ are iid. Let $p=R_a(y)$ and define

$$
F(k)=\mathbb E[B\mathbf1\{\operatorname{rank}(I)\le k\}],
\qquad
\widehat F_t(k)=\frac1t\sum_{i=1}^t
B_i\mathbf1\{\operatorname{rank}(I_i)\le k\}.
\tag{16}
$$

**Concentration lemma.** If $p\le2\tau$, then for every $x>0$, with
probability at least $1-4e^{-x}$,

$$
\sup_k|\widehat F_t(k)-F(k)|\le r(t,x),
\qquad
r(t,x)=4\sqrt{\frac{\tau x}{t}}+\frac{2x}{t}.
\tag{17}
$$

**Proof.** Write $M=\sum_{i=1}^tB_i$ and $v=x/t$. Binomial Bernstein
gives, except on an event of probability $2e^{-x}$,

$$
|M/t-p|\le\sqrt{2pv}+\frac{2v}3,
\qquad
M/t\le2p+\frac{7v}6.
\tag{18}
$$

The second inequality uses $\sqrt{2pv}\le p+v/2$. Conditional on $M=s>0$,
the $s$ successful ranks are iid from their conditional rank law $G$.
The Dvoretzky--Kiefer--Wolfowitz inequality gives
$\sup|\widehat G-G|\le\sqrt{x/(2s)}$, except with conditional probability
$2e^{-x}$. If $s=0$, its contribution below is zero; if $p=0$, (17)
holds directly. Since $F=pG$, on the two good events

$$
\begin{aligned}
\sup|\widehat F_t-F|
&\le |M/t-p|+\sqrt{(M/t)v/2}\\
&\le(\sqrt2+1)\sqrt{pv}
 +\left(\frac23+\sqrt{\frac7{12}}\right)v\\
&\le4\sqrt{\tau v}+2v.
\end{aligned}
\tag{19}
$$

For the final inequality use $p\le2\tau$, $2+\sqrt2<4$, and
$2/3+\sqrt{7/12}<2$. A union bound proves (17). This is a standard
rare-region conditioning argument combined with Bernstein and DKW, not a
new concentration result; see Section 8.

Define the group estimators

$$
\widehat R_{n,t}=\frac1t\sum_{i=1}^t h_n(\operatorname{rank}(I_i))B_i.
\tag{20}
$$

They have expectation $R_n$. For any nonincreasing function
$h\in[0,4]$, summation by parts gives

$$
\left|\sum_r h(r)
\big[\widehat F_t(r)-\widehat F_t(r-1)-F(r)+F(r-1)\big]\right|
\le4\sup_k|\widehat F_t(k)-F(k)|.
\tag{21}
$$

Indeed, the nonnegative coefficients $h(k)-h(k+1)$, using $h(m+1)=0$,
sum to $h(1)\le4$. Applying (21) to every ratio (14) gives, on the single
event in (17),

$$
\max_{n\text{ in the group}}|\widehat R_{n,t}-R_n|\le4r(t,x).
\tag{22}
$$

There is no union bound over budgets in this step.

## 5. Stages, global validity, and expected upper cost

For each group use one iid sample sequence, evaluated at the following
successive prefix lengths. For $j=1,2,\ldots$, put

$$
\begin{aligned}
\alpha_j&=\delta 2^{-j},&x_j&=\log(4/\alpha_j)=L+(j+2)\log2,\\
A&=\frac{4096\tau}{\epsilon^2},&t_j&=\lceil A x_j\rceil,\\
r_j&=4\sqrt{\tau x_j/t_j}+2x_j/t_j.
\end{aligned}
\tag{23}
$$

Declare the group passed at the first stage at which every declared budget
in the group satisfies

$$
\widehat R_{n,t_j}+4r_j\le\tau.
\tag{24}
$$

First consider validity on an arbitrary fixed table that is unsafe for at
least one budget in this group. If $p=R_a\le2\tau$, passage at stage $j$
requires failure of (22), whose probability is at most
$4e^{-x_j}=\alpha_j$. If $p>2\tau$, the representative $a$ is itself
declared and belongs to the group, so (24) implies $M/t_j\le\tau$.
Binomial lower-tail Chernoff gives

$$
\Pr(M/t_j\le\tau)
\le e^{-t_jp/8}
\le e^{-t_j\tau/4}
\le e^{-x_j}
\le\alpha_j.
\tag{25}
$$

Here $t_j\ge4x_j/\tau$ follows from (4) and (23). The group ever passes
with probability at most $\sum_j\alpha_j=\delta$. This high-risk branch
is necessary: the assumption $R_a\le2\tau$ in the concentration lemma is
not a trusted promise about an unknown table.

For power and cost, now take any table in $\mathcal Y_\epsilon$. Every
group has $p\le\tau-\epsilon$, and

$$
r_j\le\frac\epsilon{16}+\frac{\epsilon^2}{2048\tau}
\le\epsilon\left(\frac1{16}+\frac1{32768}\right)
<\frac\epsilon8.
\tag{26}
$$

On (22), each left side of (24) is at most
$\tau-\epsilon+8r_j<\tau$. Consequently the probability the group has
not passed by stage $j$ is at most $\alpha_j$. Independence between
stages is unnecessary. If $T_{\mathrm{group}}$ counts proposal draws
until passage, then

$$
\begin{aligned}
\mathbb E T_{\mathrm{group}}
&\le t_1+\sum_{j\ge1}(t_{j+1}-t_j)\alpha_j\\
&\le\lceil A(L+3\log2)\rceil
  +\delta\lceil A\log2\rceil\\
&\le3AL
=\frac{12288\tau L}{\epsilon^2}.
\end{aligned}
\tag{27}
$$

For the last inequality, the preceding line is at most
$A(L+3.25\log2)+1.25$. Since $L\ge\log4$,
$3L-(L+3.25\log2)\ge0.75\log2$; and (4) implies $A\ge4096$.
Thus (27) bounds expected completion, not just the sample size on a
high-probability event. The stage lengths increase linearly in $j$, so
this argument adds no logarithm of the margin or its logarithm.

Run the groups in any fixed order, sharing the label cache, and issue (2)
only after every group passes. On an unsafe table, choose any one unsafe
budget and its group. Whole-family certification requires that group to
pass, an event of probability at most $\delta$. There is no need to divide
$\delta$ between groups for this single decision. This is ordinary
intersection--union testing, and does not assert simultaneous coverage of
separately selectable group conclusions.

Finally, cap the total number of proposal draws across all groups at $D$.
If the statistical certificate has not issued by then, query every remaining
unknown item and evaluate every declared risk exactly. Certify if safe and
abstain otherwise. This adds no false certificates and gives finite
certification on every safe table, including the boundary and tables outside
$\mathcal Y_\epsilon$.

To count cost, couple this capped auditor to its unbounded sequence of group
draws. If the unbounded auditor finishes in fewer than $D$ proposal draws,
its distinct-label cost is at most that number. If it takes at least $D$
draws, the capped auditor costs at most $D$ distinct labels, including any census. Thus
cost is pathwise at most both $D$ and the unbounded proposal count. Cached
labels and repeated proposals cannot increase it. Summing (27) over
$J\le4Z$ groups proves (5).

## 6. A common fixed-profile permutation lower bound

Assume (6). Define integer counts and their rates by

$$
k=\lfloor P(\tau-\epsilon)\rfloor,\qquad
p=\frac kP,\qquad
\Delta=\frac{\lceil8P\epsilon\rceil}{P},\qquad
q=p+\Delta.
\tag{28}
$$

Conditions (4)--(6) imply $P\epsilon\ge1$ and $k\ge4$. For example,
$\epsilon\le1/128$, $L\ge\log4>1$, and
$\tau-\epsilon\ge15\epsilon$ give both directly. Therefore

$$
\begin{aligned}
\tau-2\epsilon&\le p\le\tau-\epsilon,&p&\ge7\tau/8,\\
8\epsilon&\le\Delta\le9\epsilon,&
q&\le\tau+8\epsilon\le3\tau/2\le3/16<1/4.
\end{aligned}
\tag{29}
$$

All the counts in (28) are integers between zero and $P$.

Let $\Pi$ be the following distribution over fixed binary tables:
independently at every rank, uniformly choose exactly $k$ of its $P$
prompt positions to have label one. Every table in its finite support has
every target risk exactly $p\le\tau-\epsilon$. Thus $\Pi$ is supported
on the efficiency class. It is a minimax construction, not a model for how
actual labels are generated.

For each band $I_j$, define $Q_j$ by instead placing exactly $qP$ ones
at every rank in $I_j$, with $k$ ones at every other rank. The placements
are again uniform and independent across ranks. Every table in $Q_j$ is
unsafe for representative $a_j$, since

$$
R_{a_j}=p+\Delta c_j>p+2\epsilon\ge\tau.
\tag{30}
$$

The last inequality follows from
$p\ge\tau-\epsilon-1/P$ and $P\epsilon\ge1$; the strict inequality
comes from $c_j>1/4$. Global validity therefore bounds the certificate
probability under every $Q_j$ by $\delta$.

Fix an admissible auditor. Under $\Pi$, let $T_j$ count the distinct
queries in band $I_j$ before certification, and write $x=\mathbb E_\Pi T_j$.
Truncate the transcript when it certifies or when it has made

$$
b=\lfloor k/2\rfloor
\tag{31}
$$

queries in this band. Classify a certificate simultaneous with the $b$th
query as reaching the cap. For the event $E$ of certification strictly
before the cap,

$$
\Pi(E)\ge1-x/b,\qquad Q_j(E)\le\delta.
\tag{32}
$$

The first inequality is Markov's inequality applied to $T_j\ge b$;
almost-sure certification on each safe table gives a well-defined $T_j$.

Before the cap, suppose a queried rank in $I_j$ has already had $t$
distinct positions inspected, with $s$ positive labels. Conditional on the
full observed history and queried identities, the remaining positions at
that rank are uniform with the appropriate remaining counts. This holds
under arbitrary adaptive choices because ranks were independently
permuted. The conditional success probabilities under $\Pi$ and $Q_j$
are respectively

$$
u=\frac{pP-s}{P-t},\qquad
v=\frac{qP-s}{P-t}.
\tag{33}
$$

On every prefix with positive probability under $\Pi$,
$t\le b\le pP/2$, $s\le t$, and

$$
v\ge p/2,\qquad v\le2q\le3/8<1/2,\qquad |v-u|\le2\Delta.
\tag{34}
$$

In particular the conditional probabilities under $Q_j$ stay strictly
between zero and one. The elementary binary relative-entropy bound gives

$$
\operatorname{kl}(\operatorname{Ber}(u),\operatorname{Ber}(v))
\le\frac{(u-v)^2}{v(1-v)}
\le\frac{16\Delta^2}{p}
\le\frac{1296\epsilon^2}{p}.
\tag{35}
$$

Queries outside $I_j$ have the same conditional label law in both
experiments and contribute zero KL. Query choices, internal randomness, and
decisions use the same conditional rule given the history and also add no
KL beyond the observed labels. The finite-transcript chain rule therefore
bounds divergence in the direction **safe mixture to unsafe mixture** by
$(1296\epsilon^2/p)x$.

To make the stopping argument explicit, additionally stop after $h$
transitions of the auditor. For this finite transcript the chain rule and
data processing apply directly. Let $E_h$ be certification by that horizon
and before the band cap. Its divergence is bounded by
$(1296\epsilon^2/p)x$, uniformly in $h$, because the number of band
queries in it is at most $T_j$ under $\Pi$. Also $Q_j(E_h)\le\delta$.
For probabilities $a,c$, binary relative entropy satisfies
$\operatorname{kl}(a,c)\ge a\log(1/c)-\log2$. Consequently

$$
\frac{1296\epsilon^2}{p}x
\ge\Pi(E_h)L-\log2.
$$

Let $h\to\infty$. Only the bounded event probabilities are taken to the
limit: $E_h\uparrow E$ by finite certification under $\Pi$. No identity
for KL at an unbounded stopping time is assumed. Using (32) gives

$$
\frac{1296\epsilon^2}{p}x
\ge(1-x/b)L-\log2,
$$

and hence the finite inequality

$$
\mathbb E_\Pi T_j
\ge\frac{L-\log2}{1296\epsilon^2/p+L/b}.
\tag{36}
$$

Since $k\ge4$, $b\ge pP/4$. Furthermore
$L-\log2\ge L/2$ and $L/P\le\epsilon^2$. Thus

$$
\mathbb E_\Pi T_j
\ge\frac{pL}{2600\epsilon^2}
\ge\frac{7\tau L}{20800\epsilon^2}
\ge\frac{\tau L}{3000\epsilon^2}.
\tag{37}
$$

The same safe mixture $\Pi$ is used for every band. Their distinct query
counts add because the bands are disjoint. There are at least $Z/4$ bands
by (13), so the average total cost under $\Pi$ is at least
$Z\tau L/(12000\epsilon^2)$. Some fixed safe table in its support has at
least this cost. Taking the supremum over the margin class and then the
infimum over admissible auditors proves the lower bound in (7).

The lower construction varies only the support locations within one common
rank-count profile. It would still apply if that profile were supplied as
untrusted reference metadata while validity remained required outside it.
It does not provide trusted free labels or assume a stochastic oracle.

## 7. Interpretation and practical limits

The theorem provides order $Z\tau L/\epsilon^2$ in its stated regime. For
a fixed relative margin $\epsilon=c\tau$, $0<c\le1/16$, this is order
$ZL/\tau$, with constants depending on $c$. As the relative margin
shrinks, the inverse-squared-margin factor becomes essential in this
worst-case class. The permutation lower bound explains why a positive-label
minimax benchmark differs from a matching-reference pointwise optimum.

The upper construction is a proof device. It uses replacement proposals,
cached labels, auxiliary thinning for fractional losses, a supplied margin,
loose concentration constants, and a census cap. It does not replace the
repository's existing betting engine or CLI. It establishes neither a sharp
leading constant nor useful finite-sample savings.

For example, at the existing 32-prompt, 64-item geometry with
$\tau=1/10$, $\epsilon=1/160$, and $\delta=1/20$, the census cap is
$D=2048$. Already $A=4096\tau/\epsilon^2=10{,}485{,}760>D$, and
$x_1>1$, so the construction reaches its census cap before its first
statistical check. The replication condition also fails: $P=32$ is less
than $L/\epsilon^2$. **The lower bound is not applied to that geometry.**
These are consequences of the displayed formulas, not a new model study or
a claim of improved audit performance.

No guarantee is established here for adapting to an unknown margin, for
matching costs when the replication condition fails, for new prompts or
newly generated candidates, or for wrong, noisy, or changing oracle labels.
The fixed-table model remains conditional on frozen pools, ranks, and
correct acquired losses. Finite arithmetic checks can support the formulas
and their implementation; they cannot prove scientific priority, practical
usefulness, or independent human understanding of the argument.

## 8. Primary-source comparison and unresolved priority

The [separate priority comparison](nonzero-minimax-priority.md) records the
bounded source screen and its unresolved questions.

[Fitas (2026, v2), Theorem 2 and Supplements S5 and S7.2](https://arxiv.org/html/2608.21496v2)
are close predecessors. S7.2 uses geometrically separated rank bands and
adaptive stopped-transcript KL with Bernoulli perturbations around one half.
S5 combines Bernstein concentration and finite-family error accounting with
a geometric grid and total-variation interpolation. Its main minimax
objective is worst-coordinate mean-squared error in a candidate/label
experiment, rather than the exact fixed-table global threshold decision in
(3). That difference alone does not establish novelty.

[Sarkar and Baichoo (2026, v1), Appendix C.3](https://arxiv.org/html/2609.40190v1)
is especially direct prior art. The multiscale and noisy-label arguments
already obtain rare-event variance divided by squared accuracy or margin,
summed over disjoint geometric bands through adaptive KL. Replacing a fair
Bernoulli center by a rare-event center is therefore not a contribution of
this note. Their Appendix B.5 uses bracketing to reduce simultaneous-family
costs, and Section 7.6 uses Bernstein with a family-confidence factor. The
finite count conditioning and capped hypergeometric argument in Section 6
are the additional steps used here to ensure every safe-prior table belongs
to the exact margin class and every alternative is strictly unsafe.

[Lhaut, Sabourin, and Segers (2022), Lemma 2.1 and the following discussion](https://arxiv.org/html/2110.05826v2)
explicitly condition an empirical measure on the binomial number of samples
inside a rare region and combine that representation with concentration and
binomial Bernstein. Section 4 specializes that device to nested rank
prefixes using DKW. [Reeve (2024), Theorem 1 and Corollary 1](https://arxiv.org/html/2403.16651v1)
also gives variance-sensitive localized DKW bounds. The concentration rate
in this note is established material.

The possible distinction is the combined statement: exact finite-grid
$Z$, globally valid fixed-table certification, expected distinct-label
cost over one specified margin class, a positive-label upper bound without
additional grid or margin logarithms, and a matching lower rate under (6).
The bounded comparison above does not establish that no earlier theorem
already implies this combination. Geometric grouping, rare-risk bandwise
KL, permutation mixtures, summation by parts, staged error spending, and
intersection--union testing are not claimed as new ingredients.

In particular, the absence of a family-confidence logarithm partly follows
from asking a weaker question than simultaneous inference with selectable
budgets. An unsafe whole-family decision must falsely pass one particular
unsafe group. Simultaneous confidence bands must instead protect all
reported intervals at once. Equation (7) does not dominate those stronger
inference guarantees. Priority, practical value, and independent human
review remain separate unresolved requirements.
