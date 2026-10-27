# Finite saturation for high-budget best-of-n grids

Candidate theorem, 27 October 2026. This note uses the fixed experiment and
minimax objective of the [nonzero theorem](nonzero-minimax-theorem.md).
It gives matching finite-table bounds for every declared grid whose
smallest budget is at least one quarter of the pool size, without a
replication or maximum-atom condition.

The prefix-and-residual construction and its clipped-weight cost have
classical threshold-sampling antecedents; see the
[priority comparison](finite-saturation-priority.md). No novelty claim for
that architecture, the concentration tools, or adaptive transcript KL is
made here. This is a theoretical proof construction, not a new practical
audit engine. The argument was developed and checked with Codex assistance
and has not received independent human review. Scientific priority remains
unestablished; see the [contribution disclosure](provenance.md).

## 1. Fixed experiment, objective, and statement

Fix integers $P,m\ge1$ and a nonempty declared family
$\mathcal K\subseteq\{1,\ldots,m\}$. There are $P$ equally weighted prompt
pools, each with $m$ distinct items in a fixed total rank order, rank 1
being best. Querying an item reveals its fixed, correct loss
$y_{p,r}\in[0,1]$ at unit cost. No actual labels are free, and no known
relationship reveals another item's loss without querying it. Computation
is not charged.

The budget-$n$ selector draws a uniform $n$-subset without replacement and
returns its best-ranked member. Write

$$
\begin{aligned}
w_n(r)&=\frac{\binom{m-r}{n-1}}{\binom mn},&
a_n(p,r)&=\frac{w_n(r)}P,\\
R_n(y)&=\sum_{p,r}a_n(p,r)y_{p,r},&
e_r&=\max_{n\in\mathcal K}w_n(r).
\end{aligned}
\tag{1}
$$

Impossible binomial choices are zero. An admissible auditor may randomize,
choose unseen items adaptively, and abstain. Its one whole-family
certificate asserts $R_n(y)\le\tau$ for every originally declared $n$.
For every fixed table with some $R_n(y)>\tau$, its probability of ever
issuing that certificate is at most $\delta$. For every fixed safe table,
including boundary-safe tables, it certifies after finitely many queries
almost surely. Both requirements apply to all tables in $[0,1]^{Pm}$.

For a supplied design margin $\epsilon$, define

$$
\mathcal Y_\epsilon
=\{y:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},
\qquad
C^*(\epsilon)=\inf_A\sup_{y\in\mathcal Y_\epsilon}
\mathbb E_yT_A(y),
\tag{2}
$$

where $T_A$ counts distinct labels acquired before certification. One
auditor serves the whole efficiency class. It may know $\epsilon$, but
that design margin is not trusted evidence about an unknown table.

Put

$$
\begin{aligned}
a&=\min\mathcal K,&L&=\log(1/\delta),&
H&=\frac{\tau L}{\epsilon^2},\\
q_k&=\sum_{r>k}w_a(r)
=\frac{\binom{m-k}{a}}{\binom ma},&
Z_{\rm tail}(k)&=\sum_{r>k}e_r,&
k_\epsilon&=\min\{k:q_k\le\epsilon\},\\
G&=\sum_{r=1}^m\min\{P,He_r\},&
F&=\min\{Pk_\epsilon,G\}.
\end{aligned}
\tag{3}
$$

The prefix indices range over $0,\ldots,m$. Each row, and therefore its
envelope $e_r$, is nonincreasing. Consequently

$$
G=\min_{0\le k\le m}
\{Pk+H Z_{\rm tail}(k)\}.
\tag{4}
$$

Indeed, increasing $k$ by one changes the expression by $P-He_{k+1}$.
These increments are nondecreasing, so a minimizing prefix includes exactly
the ranks where census is cheaper than retaining their residual term,
with either choice permitted at equality. In item notation, $G$ is also
$\sum_{p,r}\min\{1,H\max_n a_n(p,r)\}$.

**Theorem.** Suppose

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14,\qquad
\min\mathcal K\ge\frac m4.
\tag{5}
$$

Then, for every $P\ge1$,

$$
\boxed{\qquad
\frac{F}{2^{21}}\le C^*(\epsilon)\le12288F.
\qquad}
\tag{6}
$$

The constants are loose. There is no density or replication assumption.
For $\mathcal K=\{m\}$, the rate is $\min\{P,H\}$. The deterministic
term $Pk_\epsilon$ also captures small weighted tails; Section 7 shows
that it cannot in general be removed when $\delta$ varies.

## 2. An exact finite-population testing lemma

The following lemma concerns distributions over fixed oracle tables, not
a noisy-label model.

**Lemma.** A block has $N$ cells. Under a safe prior, exactly $k$ cells
have the same positive loss amplitude $\gamma\le1$, uniformly permuted,
and all other block cells have loss zero. Under an alternative, exactly
$k+d$ cells have amplitude $\gamma$, uniformly permuted. Assume

$$
k\ge0,\qquad d\ge1,\qquad k+d\le N/2.
\tag{7}
$$

The outside table is independent of this block under both priors and has
the same distribution. Every table in the safe prior's support belongs
to $\mathcal Y_\epsilon$, and every alternative table is unsafe. If $X$
is an admissible auditor's expected number of distinct block queries
under the safe prior, then

$$
X\ge\frac1{1024}
\min\left\{N,\frac{N(k+1)L}{d^2}\right\}.
\tag{8}
$$

Identical outside marginal laws without the stated independence would not
suffice for the proof.

**Proof.** Write $R=\min\{N,N(k+1)L/d^2\}$. The probability of certifying
without querying the block is the same under the two priors. Validity and
safe-table completeness therefore imply
$X\ge1-\delta\ge3/4$. This proves (8) when $R<256$.

Otherwise set $b=\lfloor R/128\rfloor$, so
$b\ge R/256$ and $b\le N/128$. Stop the transcript at certification, at
the $b$th distinct block query, or at an additional finite transition
horizon. A certificate simultaneous with the $b$th block query counts as
reaching the cap. After $t<b$ distinct block queries with $S_t$ positive
labels, the next-label probabilities under the two priors are

$$
u=\frac{k-S_t}{N-t},\qquad
v=\frac{k+d-S_t}{N-t}.
\tag{9}
$$

Uniformity of the remaining placements holds under adaptive choices of
cell identities and interleaving with the independent outside table.
For every history of positive safe-prior probability, $0<v<1$ and

$$
\begin{aligned}
\operatorname{kl}(\operatorname{Ber}(u),\operatorname{Ber}(v))
&\le\frac{(u-v)^2}{v(1-v)}\\
&=\frac{d^2}{(k+d-S_t)(N-t-k-d+S_t)}\\
&\le\frac{4d^2}{N(k+d-S_t)}.
\end{aligned}
\tag{10}
$$

To control the expectation even on histories that reveal many positives,
complete the block's success sequence after stopping to a uniform random
permutation of $k$ ones and $N-k$ zeros. The same sequential construction
is valid for adaptive unseen-cell choices: each next unseen cell has the
uniform remaining-success probability, and an unused suffix can be filled
after the auditor stops. Thus $S_t$ in this completed sequence has the
hypergeometric distribution. Direct summation gives

$$
\begin{aligned}
\mathbb E\frac1{k-S_t+1}
&=\frac1{\binom Nt}
\sum_s\frac{\binom ks\binom{N-k}{t-s}}{k-s+1}\\
&=\frac1{(k+1)\binom Nt}
\sum_s\binom{k+1}s\binom{N-k}{t-s}\\
&\le\frac{\binom{N+1}t}{(k+1)\binom Nt}
=\frac{N+1}{(k+1)(N+1-t)}
\le\frac2{k+1}.
\end{aligned}
\tag{11}
$$

The sum is over the original feasible values of $s$. Extending that range
only adds nonnegative terms; the inequality is Vandermonde's identity.
Since $d\ge1$, (11) also bounds the reciprocal with denominator
$k+d-S_t$.

Query choices, internal randomization, and decisions follow the same
conditional rule given a transcript. Outside labels have the same
conditional kernels, by independence and the unchanged outside law.
The finite-transcript KL chain rule therefore charges only block labels.
Replace each stopping indicator in the expected sum of (10) by one and
use the completed permutation sequence to obtain

$$
\operatorname{KL}(\Pi^{(h)},Q^{(h)})
\le\frac{8d^2b}{N(k+1)}\le\frac L{16}.
\tag{12}
$$

If $X<b/4$, Markov's inequality and almost-sure certification under the
safe prior give probability greater than $3/4$ of certification strictly
before the block cap. At a sufficiently large finite transition horizon
$h$, its probability is at least $3/4$. Under the alternative it is at
most $\delta$. Binary data processing and
$\operatorname{kl}(u,v)\ge u\log(1/v)-\log2$ then give

$$
\operatorname{KL}(\Pi^{(h)},Q^{(h)})
\ge\frac{3L}4-\log2\ge\frac L4,
\tag{13}
$$

contradicting (12). Thus $X\ge b/4\ge R/1024$. Only certificate-event
probabilities take an increasing-horizon limit; every KL calculation is
at a finite horizon. $\square$

## 3. Hidden subsets on a common fractional safe table

Let $p_0=\tau-\epsilon$ and take the single fixed table
$y_{p,r}=p_0$. Every declared risk equals $\tau-\epsilon$.

**Lemma.** For any rank with $e_r\ge16\epsilon$, an admissible auditor's
expected number of queries at that rank on this table is at least

$$
\frac1{1024}\min\left\{P,\frac{Le_r}{\epsilon}\right\}.
\tag{14}
$$

**Proof.** Choose a declared witness with weight $w=e_r$, put
$h=1-p_0\ge7/8$, and let

$$
s=\left\lfloor\frac{\epsilon P}{hw}\right\rfloor+1.
\tag{15}
$$

Change any $s$ cells in this rank from $p_0$ to 1, leaving all others
unchanged. The witness risk becomes $p_0+hws/P>\tau$. Also $1\le s\le P$,
because $\epsilon/(hw)\le1/14$; the case $P=1$ gives $s=1$ directly.

Let $T$ be the rank-query count on the constant safe table. Average the
alternative over all $s$-subsets. Couple the auditor's randomness between
the two tables. If none of the changed cells is queried before the safe
table's certificate, that entire transcript is unchanged and the
alternative also certifies. Therefore

$$
\mathbb E f(T)\le\delta,
\qquad f(t)=\frac{\binom{P-t}s}{\binom Ps},
\tag{16}
$$

where $f(t)=0$ if $P-t<s$. In particular,
$\mathbb ET\ge1-\delta\ge3/4$.

Set $R_0=\min\{P,PL/s\}$. If $R_0<64$, this already implies
$\mathbb ET\ge R_0/256$. Otherwise set $b=\lfloor R_0/32\rfloor$.
Then $P\ge64$, $b\ge R_0/64$, $b\le P/32$, and
$s\le P/14+1<P/2$. The product formula for $f$ and
$\log(1-u)\ge-2u$ for $0\le u\le1/2$ give

$$
f(b)=\prod_{j=0}^{s-1}\left(1-\frac b{P-j}\right)
\ge\exp\left(-\frac{4sb}P\right)
\ge e^{-L/8}.
\tag{17}
$$

If $\mathbb ET<b/4$, then $\Pr(T<b)>3/4$. Since $f$ is
nonincreasing, (16)--(17) would imply
$\delta\ge\mathbb Ef(T)>(3/4)\delta^{1/8}>\delta$.
Thus $\mathbb ET\ge b/4\ge R_0/256$ in this case as well.

Finally $s\le1+(8/7)\epsilon P/w$ implies

$$
R_0\ge\frac7{15}\min\left\{P,\frac{Lw}{\epsilon}\right\}.
\tag{18}
$$

For $\epsilon P/w\ge1$, use $s\le(15/7)\epsilon P/w$; for
$\epsilon P/w<1$, use $s<15/7$ and $L\ge\log4>1$.
Equations (17)--(18), with $7/(15\cdot256)>1/1024$, prove (14).
$\square$

## 4. A rankwise lower bound for every declared grid

This section does not assume $a\ge m/4$.

**Proposition.** Under the first three conditions in (5), every nonempty
declared grid satisfies

$$
C^*(\epsilon)\ge\frac{A_{16}}{32768},
\qquad
A_{16}=\sum_{r:e_r\ge16\epsilon}\min\{P,He_r^2\}.
\tag{19}
$$

**Proof.** First suppose $P\tau\ge4$. Set

$$
p_0=\tau-\epsilon,
\qquad k=\lceil Pp_0\rceil,
\qquad\gamma=\frac{Pp_0}k.
\tag{20}
$$

Independently at every rank, uniformly choose exactly $k$ of the $P$
prompt positions to have loss $\gamma$, and give all others loss zero.
Every table in this common prior has rank-average loss exactly $p_0$ at
every rank. Hence every declared risk is exactly $\tau-\epsilon$; no
conditioning or exceptional safe-table mass is involved. Moreover

$$
P\ge32,\qquad
\gamma\ge\frac34,\qquad
k\le\frac P8+1\le\frac{5P}{32}.
\tag{21}
$$

For a rank with $w=e_r\ge16\epsilon$, choose a declared budget attaining
that envelope weight. Change only this rank's count to $k+d$, where

$$
d=\left\lceil\frac{2\epsilon P}{\gamma w}\right\rceil.
\tag{22}
$$

Every table under this alternative has witness risk at least
$p_0+\gamma wd/P\ge\tau+\epsilon>\tau$. Since
$d\le P/6+1$ and $P\ge32$, (21) gives $k+d<P/2$. The outside ranks are
independent and unchanged, so the finite-population lemma applies.

Write $z=\epsilon P/w$. If $z\ge1$, then $d<4z$ and

$$
\frac{P(k+1)L}{d^2}
\ge\frac{15}{256}Hw^2.
\tag{23}
$$

If $z<1$, then $d\le3$ and

$$
\frac{P(k+1)L}{d^2}
\ge\frac5{48}\tau P^2L
\ge\frac5{12}LP>\frac P2.
\tag{24}
$$

In both cases
$\min\{P,P(k+1)L/d^2\}\ge\min\{P,Hw^2\}/32$.
Equation (8) therefore gives expected rank cost at least
$\min\{P,Hw^2\}/32768$. These rank counts add under the same safe prior.
Some fixed table in its finite support has cost at least the average,
proving (19) when $P\tau\ge4$.

When $P\tau<4$, use the one constant safe table of Section 3 and put

$$
B_{16}=\sum_{r:e_r\ge16\epsilon}
\min\left\{P,\frac{Le_r}{\epsilon}\right\}.
\tag{25}
$$

For $z=Le_r/\epsilon\ge P$, the corresponding $A_{16}$ term is at most
the $B_{16}$ term. If $z<P$, then

$$
He_r^2=\frac\tau Lz^2
\le\frac{P\tau}Lz<3z.
\tag{26}
$$

Thus $A_{16}\le3B_{16}$. The rank bounds (14) add on the same fixed
table, giving $C^*(\epsilon)\ge B_{16}/1024\ge A_{16}/3072$.
This is stronger than (19) and completes the proposition. $\square$

## 5. High-budget envelope geometry

Assume now $a\ge m/4$ and write $c=1/4$. Each individual positive row is
log-concave, because

$$
\frac{w_n(r+1)}{w_n(r)}
=\frac{m-r-n+1}{m-r}
\tag{27}
$$

is nonincreasing in $r$. Each row also has $w_n(1)=n/m\ge c$.
Multiplying consecutive ratio inequalities, or using concavity of
$\log w_n$, gives

$$
w_n(2r-1)\le\frac{w_n(r)^2}{w_n(1)}
\le\frac{w_n(r)^2}{c}.
\tag{28}
$$

Extend rows by zero after their support; if $w_n(r)=0$, the left side is
also zero. Taking maxima over $n$ in (28) gives

$$
e_{2r-1}\le\frac{e_r^2}{c}.
\tag{29}
$$

This argument does not assume that the maximum of the log-concave rows is
itself log-concave. Since the envelope is decreasing, grouping its terms
in pairs and using (29) yields

$$
G\le\frac2c\sum_r\min\{P,He_r^2\}.
\tag{30}
$$

If $m\le4$, every positive best-of-$n$ weight is at least $1/6$.
Consequently every positive envelope weight exceeds $16\epsilon\le1/8$.
The sum in (30) is then $A_{16}$ and $F\le8A_{16}$.

For the remaining argument take $m\ge5$. Every declared $n$ is at least
2 and $m\le4n$, so

$$
\frac{n-1}{m-1}\ge\frac{n-1}{4n-1}\ge\frac17.
\tag{31}
$$

Thus every row, and then its envelope, satisfies

$$
e_{r+1}\le\frac67e_r.
\tag{32}
$$

This weight-decay factor differs from the tail-decay factor below.
Let $R=\#\{r:e_r\ge16\epsilon\}$. Since
$e_1\ge1/4>16\epsilon$, $R\ge1$. For the smallest declared budget,
the exact hazard and tail identities are

$$
w_a(k+1)=\frac a{m-k}q_k,
\qquad
q_{k+1}=q_k\left(1-\frac a{m-k}\right)
\le\frac34q_k
\tag{33}
$$

whenever $q_k>0$. If $q_R=0$, already $k_\epsilon\le R$.
Otherwise $R<m$, $w_a(R+1)\le e_{R+1}<16\epsilon$, and (33) gives
$q_R<16\epsilon/c=64\epsilon$. Since

$$
\left\lceil\frac{\log64}{\log(4/3)}\right\rceil=15,
\qquad
k_\epsilon\le R+15\le16R.
\tag{34}
$$

If $H(16\epsilon)^2>P$, each of the $R$ terms in $A_{16}$ equals $P$.
It follows that

$$
F\le Pk_\epsilon\le16A_{16}.
\tag{35}
$$

If $H(16\epsilon)^2\le P$, (32) instead gives

$$
\begin{aligned}
\sum_{r>R}\min\{P,He_r^2\}
&\le\frac{H(16\epsilon)^2}{1-(6/7)^2}\\
&\le\frac{H(16\epsilon)^2}{c}
\le\frac{A_{16}}c.
\end{aligned}
\tag{36}
$$

The last inequality uses $R\ge1$ and the fact that an included term is
at least $H(16\epsilon)^2$. Combining (30) and (36) gives
$F\le G\le40A_{16}$. Together with the other cases, this proves

$$
F\le40A_{16},
\qquad
C^*(\epsilon)\ge\frac{F}{40\cdot32768}
\ge\frac{F}{2^{21}}.
\tag{37}
$$

## 6. A globally valid prefix-and-residual upper bound

First, querying every prompt position in the first $k_\epsilon$ ranks
gives known prefix risks

$$
b_n=\sum_p\sum_{r\le k_\epsilon}a_n(p,r)y_{p,r}.
$$

The tail probability is nonincreasing in the budget $n$, so
$b_n+q_{k_\epsilon}$ is a deterministic upper bound for every target risk.
On a margin-class table it is at most
$R_n(y)+q_{k_\epsilon}\le\tau$. Certify if all these upper bounds pass;
otherwise census the remaining positive-support cells and evaluate the
risks exactly. This is globally valid and all-safe complete, and its cost
on $\mathcal Y_\epsilon$ is at most $Pk_\epsilon$.

For the statistical part, fix any prefix $k$, query its $Pk$ cells, and
write $b_n$ for its known risk contributions. Put $q=q_k$. If
$q\le\epsilon$, the same deterministic rule already gives the required
margin-class cost $Pk$. Hence consider $q>\epsilon$.

Since $a\le n\le m\le4a$, the likelihood ratios

$$
h_n(r)=\frac{w_n(r)}{w_a(r)}
\tag{38}
$$

on the positive support of $w_a$ satisfy $0\le h_n(r)\le n/a\le4$ and
are nonincreasing in $r$. Indeed, the product formula

$$
w_n(r)=\frac nm\prod_{u=1}^{r-1}
\left(1-\frac{n-1}{m-u}\right)
$$

gives the bound, and on adjacent positive weights
$h_n(r+1)/h_n(r)=(m-r-n+1)/(m-r-a+1)\le1$.
Terminal zeros preserve monotonicity. This permits the equality endpoint
$n/a=4$; no strict inequality is needed. The support of $w_n$ is contained
in that of $w_a$, and ratios are extended by zero outside the latter.

Draw iid tail items with probability $w_a(r)/(Pq)$ for each $(p,r)$ with
$r>k$. Query an item's fixed loss only if it is not already cached, and
generate a fresh auxiliary coin $B\sim\operatorname{Bernoulli}(y_{p,r})$
on every proposal. For a fixed fractional-loss table the rank-coin pairs
are iid. Let $\mu$ be the representative's actual tail risk, and put
$p=\mu/q$. Then $\Pr(B=1)=p$. Define the cumulative loss curve and its
empirical version by

$$
F_0(s)=\mathbb E[B\mathbf1\{\operatorname{rank}\le s\}],
\qquad
\widehat F_t(s)=\frac1t\sum_{i=1}^t
B_i\mathbf1\{\operatorname{rank}(I_i)\le s\}.
\tag{39}
$$

**Residual concentration.** If $\mu\le2\tau$, then for every $x>0$,
except with probability at most $4e^{-x}$,

$$
q\sup_s|\widehat F_t(s)-F_0(s)|\le r(t,x),
\qquad
r(t,x)=4\sqrt{\frac{q\tau x}t}+\frac{2qx}t.
\tag{40}
$$

To see this, put $M=\sum_iB_i$ and $v=x/t$. Binomial Bernstein gives,
except with probability $2e^{-x}$,

$$
|M/t-p|\le\sqrt{2pv}+\frac{2v}3,
\qquad M/t\le2p+\frac{7v}6.
$$

Conditional on $M=s>0$, the successful ranks are iid from their conditional
rank distribution. Dvoretzky--Kiefer--Wolfowitz bounds its empirical CDF
error by $\sqrt{x/(2s)}$, except with conditional probability $2e^{-x}$.
If $M=0$, that contribution is zero. Hence

$$
\begin{aligned}
\sup_s|\widehat F_t(s)-F_0(s)|
&\le|M/t-p|+\sqrt{(M/t)v/2}\\
&\le(\sqrt2+1)\sqrt{pv}
 +\left(\frac23+\sqrt{\frac7{12}}\right)v\\
&\le4\sqrt{\frac{\tau x}{qt}}+\frac{2x}t,
\end{aligned}
$$

where $p\le2\tau/q$. Multiplying by $q$ proves (40), including $p=0$.

For each target estimate its tail risk by

$$
\widehat R^{\rm tail}_{n,t}
=\frac qt\sum_{i=1}^t h_n(\operatorname{rank}(I_i))B_i.
\tag{41}
$$

Summation by parts for the nonincreasing functions $h_n\in[0,4]$ gives,
on the one event (40),

$$
\max_{n\in\mathcal K}
|\widehat R^{\rm tail}_{n,t}-R^{\rm tail}_n|
\le4r(t,x).
\tag{42}
$$

No union bound over targets is used: the nonnegative successive
differences of each $h_n$ sum to at most 4.

Use stages $j=1,2,\ldots$ with

$$
\begin{aligned}
\alpha_j&=\delta2^{-j},&
x_j&=\log(4/\alpha_j)=L+(j+2)\log2,\\
A&=\frac{4096q\tau}{\epsilon^2},&
t_j&=\lceil Ax_j\rceil,&r_j&=r(t_j,x_j).
\end{aligned}
\tag{43}
$$

Pass at the first stage at which

$$
b_n+\widehat R^{\rm tail}_{n,t_j}+4r_j\le\tau
\quad\hbox{for every }n\in\mathcal K.
\tag{44}
$$

For global validity, consider any unsafe fixed table. If $\mu\le2\tau$,
passage requires failure of (42), so has probability at most $\alpha_j$
at stage $j$. If $\mu>2\tau$, the declared representative $a$ is itself
unsafe, and passage implies $qM/t_j\le\tau<\mu/2$. A Bernoulli lower-tail
Chernoff bound gives

$$
\Pr(\hbox{pass at stage }j)
\le e^{-t_j\mu/(8q)}
\le e^{-t_j\tau/(4q)}
\le e^{-x_j}\le\alpha_j.
\tag{45}
$$

The last step uses $t_j\ge4qx_j/\tau$, which follows from (5) and
(43). Thus the probability of ever passing an unsafe table is at most
$\sum_j\alpha_j=\delta$. Neither case assumes the supplied margin is
true of that table.

On a table in $\mathcal Y_\epsilon$, $\mu\le\tau$ and

$$
r_j\le\frac\epsilon{16}
 +\frac{\epsilon^2}{2048\tau}<\frac\epsilon8.
\tag{46}
$$

On (42), each expression in (44) is at most
$\tau-\epsilon+8r_j<\tau$. Therefore the probability of not passing by
stage $j$ is at most $\alpha_j$. If $U$ counts the uncapped proposal draws
until passage, then

$$
\begin{aligned}
\mathbb EU
&\le t_1+\sum_{j\ge1}(t_{j+1}-t_j)\alpha_j\\
&\le A(L+3.25\log2)+1.25\\
&\le3AL=12288Hq.
\end{aligned}
\tag{47}
$$

For the last inequality, $L\ge2\log2$ leaves at least
$0.75A\log2$ to absorb $1.25$; and $q>\epsilon$ gives
$A>4096\tau/\epsilon\ge65536$.

Cap tail proposals at the number $D_k$ of remaining cells in the union of
positive target supports. If passage has not occurred, query every
remaining unknown support cell and evaluate all risks exactly. This adds
no false certificate and ensures finite certification for every safe
table. Coupled with the uncapped sequence, the distinct-label cost beyond
the prefix is at most $\min\{U,D_k\}$: if $U<D_k$ it is at most $U$,
and otherwise the census costs at most $D_k$. Thus the margin-class
expected cost is at most

$$
Pk+12288Hq_k
\le12288\{Pk+H Z_{\rm tail}(k)\}.
\tag{48}
$$

The same displayed bound holds when $q_k\le\epsilon$ by the deterministic
prefix rule. Optimize over $k$ using (4), and also choose the deterministic
$k_\epsilon$ auditor when its bound is smaller. This gives

$$
C^*(\epsilon)\le\min\{Pk_\epsilon,12288G\}
\le12288F,
\tag{49}
$$

completing the theorem.

## 7. Why the deterministic confidence cap is necessary

The clipped expression $G$ alone is not a matching rate uniformly in
$\delta$. For integers $j\ge7$, take

$$
P=1,\quad\tau=\frac18,\quad\epsilon=\frac1{128},\quad
\delta=e^{-4^j},\quad m=2^{3j},\quad\mathcal K=\{m/2\}.
\tag{50}
$$

The winning-rank tail satisfies

$$
q_k=\prod_{r=0}^{k-1}\frac{m/2-r}{m-r}\le2^{-k}.
\tag{51}
$$

Hence the first seven ranks give a zero-error margin-class certificate
with all-safe completeness restored by the same census fallback, so
$C^*(\epsilon)\le7$.

Here $H=2048\cdot4^j$. For ranks up to $j$, (27) is at least $1/3$:
$m\ge4j$ suffices for that inequality. Thus

$$
w_{m/2}(r)\ge\frac12\,3^{-(r-1)}
\quad(1\le r\le j),
\qquad Hw_{m/2}(r)>1.
\tag{52}
$$

The first $j$ summands in $G$ are therefore one, giving $G\ge j$ while
$C^*(\epsilon)\le7$. This separates the uncapped clipped functional
from the objective even within the high-budget singleton regime.

## 8. Scope

The theorem characterizes the order of worst-case expected distinct-label
cost for the fixed margin class and every grid with $\min\mathcal K\ge
m/4$. The common fractional rank-count prior is exactly safe for every
declared target. The finite-population lemma controls depletion in
expectation, and the envelope comparison uses a rowwise inequality before
taking maxima.

The proposition (19) applies to arbitrary grids, but a matching
characterization for unrestricted smaller budgets is not established here.
The theorem does not provide unknown-margin adaptation, separately
selectable target certificates, guarantees for new prompts or changing
pools, noisy-label robustness, useful leading constants, or a replacement
audit implementation. The [priority comparison](finite-saturation-priority.md)
addresses antecedents separately; the rate statement is not a claim of
scientific priority or practical improvement.
