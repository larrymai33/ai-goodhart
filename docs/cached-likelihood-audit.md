# Cached likelihood audits and finite-grid upper bounds

Candidate theorem, 27 October 2026. A likelihood-ratio auditor with a shared
label cache attains a clipped expected distinct-label bound on every
factor-two-separated declared budget grid. A separate grouped construction
extends the upper bound to every declared grid. Both retain the exact
fixed-table decision and boundary-safe completeness requirements of the
[nonzero theorem](nonzero-minimax-theorem.md).

The likelihood-ratio test, nonnegative-supermartingale error bound, bounded
stopping argument, and geometric grouping are classical tools. This note does
not claim a new testing principle or a production audit engine. The
[attribution note](all-grid-minimax-priority.md) separates those ingredients
from the proposed finite-cost statement. The arguments were developed and
checked with substantial Codex assistance; they have not received independent
human review. See the [contribution disclosure](provenance.md).

## 1. Fixed experiment and statements

Fix integers $P,m\ge1$ and a nonempty originally declared family
$\mathcal K\subseteq\{1,\ldots,m\}$. There are $P$ equally weighted prompt
pools with $m$ items each, in a fixed total rank order, best first. Acquiring
item $(p,r)$ reveals its fixed, correct loss $y_{p,r}\in[0,1]$ at unit cost.
No actual labels are free, and no trusted relationship reveals an unqueried
item's label. Computation and auxiliary randomness are not charged.

The budget-$n$ selector samples a uniform $n$-subset without replacement and
returns its best-ranked item. Put

$$
\begin{aligned}
w_n(r)&=\frac{\binom{m-r}{n-1}}{\binom mn},&
a_n(p,r)&=\frac{w_n(r)}P,\\
R_n(y)&=\sum_{p,r}a_n(p,r)y_{p,r},&
e_r&=\max_{n\in\mathcal K}w_n(r).
\end{aligned}
\tag{1}
$$

Impossible binomial choices are zero. An admissible auditor issues one global
certificate that every originally declared risk is at most $\tau$. For every
fixed table with some $R_n(y)>\tau$, its probability of ever issuing that
certificate is at most $\delta$. On every fixed safe table, including tables
with risk exactly $\tau$, it certifies after finitely many queries almost
surely. These requirements apply to all of $[0,1]^{Pm}$.

For a supplied design margin $\epsilon$, define

$$
\begin{aligned}
\mathcal Y_\epsilon
&=\{y:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},\\
C^*(\epsilon)
&=\inf_A\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT_A(y),
\end{aligned}
\tag{2}
$$

where $T_A$ counts distinct acquired labels. One auditor serves the entire
margin class. The supplied margin determines its design but is not trusted
evidence about the actual table.

Write $a=\min\mathcal K$, $D=Pm$, and

$$
\begin{aligned}
L&=\log(1/\delta),& H&=\frac{\tau L}{\epsilon^2},\\
q_a(k)&=\frac{\binom{m-k}{a}}{\binom ma},&
k_\epsilon&=\min\{k\in\{0,\ldots,m\}:q_a(k)\le\epsilon\},\\
Z_{\rm tail}(k)&=\sum_{r>k}e_r,&
G&=\sum_{r=1}^m\min\{P,He_r\},\\
F&=\min\{Pk_\epsilon,G\}.&&
\end{aligned}
\tag{3}
$$

All logarithms are natural. Throughout the cost corollaries assume

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
\tag{4}
$$

**Theorem 1: cached likelihood audit.** Put $\theta=\tau-\epsilon$ and

$$
\begin{aligned}
u&=\log\frac{1-\theta}{1-\tau},\\
d&=\operatorname{kl}(\operatorname{Ber}(\theta),
                    \operatorname{Ber}(\tau)),&
c&=\frac{L+u}{d},\\
B_c&=\sum_{r=1}^m\min\left\{P,
               c\sum_{n\in\mathcal K}w_n(r)\right\}.
\end{aligned}
\tag{5}
$$

There is an admissible auditor with margin-class expected distinct-label cost
at most $B_c$. This statement needs only $0<\epsilon<\tau<1$ and
$0<\delta<1$. Under (4), if successive declared budgets satisfy
$n_{j+1}\ge2n_j$, then

$$
\boxed{\quad C^*(\epsilon)
\le\min\{Pk_\epsilon,B_c\}
\le\min\{Pk_\epsilon,17G\}\le17F.\quad}
\tag{6}
$$

Singleton families satisfy the spacing condition. The original family
$\{1,2,4,8,16,32,64\}$ does too. The guarantee is an expected distinct-label
bound, not a bound of the same size on random proposals or computation.

**Theorem 2: arbitrary-grid upper.** Every nonempty declared grid under (4)
satisfies

$$
\boxed{\quad C^*(\epsilon)
\le\min\{Pk_\epsilon,61440G\}
\le61440F\le2^{16}F.\quad}
\tag{7}
$$

The [all-grid theorem](all-grid-minimax-theorem.md) proves a matching rate
within universal constants. Neither upper statement supplies selectable
simultaneous confidence intervals or authorizes certifying a chosen subset
when the originally declared global assertion fails.

## 2. The cached likelihood auditor

Fix an order of the originally declared budgets. For each budget $n$, prepare
an independent iid proposal stream with item law $a_n$. Maintain one cache
shared across all budgets. On every proposal of item $I_t$:

1. Acquire its label only if it is absent from the cache.
2. Generate a fresh independent auxiliary coin
   $B_t\sim\operatorname{Bernoulli}(y_{I_t})$, including on repeated items.
3. Update

$$
S_{n,t}=\sum_{s=1}^t\left[
B_s\log\frac\theta\tau
+(1-B_s)\log\frac{1-\theta}{1-\tau}\right].
\tag{8}
$$

Pass budget $n$ statistically when $S_{n,t}\ge L$. Also, before requesting
another proposal, check whether every positive-support label for this budget
is cached. If so, evaluate $R_n$ exactly, pass if $R_n\le\tau$, and otherwise
terminate without the global certificate. Issue the single global
certificate only after every budget has passed. An exact-support check after
the last needed acquisition may be performed immediately.

All probability statements condition on the fixed table. Consequently the
fresh pairs $(I_t,B_t)$ in a budget's stream are iid, and its coin mean is
$R_n(y)$. Caching changes the number of labels purchased; it does not discard
duplicate proposals or change their law. Reusing one old auxiliary coin on
repeated proposals would invalidate this iid argument.

### Global validity

For a fixed unsafe budget with $q=R_n(y)>\tau$, the expected likelihood-ratio
multiplier is

$$
q\frac\theta\tau+(1-q)\frac{1-\theta}{1-\tau}
=1+\frac{(\tau-q)(\tau-\theta)}{\tau(1-\tau)}\le1.
\tag{9}
$$

Thus $\exp(S_{n,t})$ is a nonnegative supermartingale starting at one.
Its probability of ever reaching $1/\delta$ is at most $\delta$.
The same statement holds conditional on all previous budget streams, since
the current proposal stream and fresh coin randomness are independent of
them and the table is fixed.

On any unsafe table, select one fixed originally declared budget whose risk
exceeds $\tau$. A false global certificate requires that budget's statistical
pass: exact evaluation cannot pass it. If an earlier budget terminates the
audit, no global certificate occurs. Hence the global false-certificate
probability is at most $\delta$.

Each component uses error allowance $\delta$, without division by
$|\mathcal K|$. This is intersection--union error accounting for one all-pass
decision; it makes no simultaneous-interval claim.

### Completeness, including the boundary

Each positive-support item in a fixed budget's finite proposal distribution
has strictly positive probability. An iid stream therefore visits every
such item after a finite random number of proposals almost surely. Unless
the budget has already passed statistically, its exact-support check then
evaluates its risk. On a safe table that check passes, including when the
risk equals $\tau$. There are finitely many budgets, so every safe table
receives the global certificate in finite time almost surely.

The exact-support rule acquires no labels for free. Every first visit to an
uncached item is charged. It can require many proposals when some positive
weights are tiny; the model charges distinct labels and leaves computation
uncharged.

## 3. Expected proposals and distinct acquisitions

Let $T_n^{\rm stat}$ be the first crossing time of (8) in the uncapped iid
stream, without the exact-support stopping rule. For a margin-class table,
$q=R_n(y)\le\theta$. The mean log increment is

$$
\mu(q)=q\log\frac\theta\tau
 +(1-q)\log\frac{1-\theta}{1-\tau}
\ge\mu(\theta)=d>0.
\tag{10}
$$

The increment on a zero coin is $u>0$ and the increment on a one coin is
negative. For every finite horizon $h$,

$$
S_{n,T_n^{\rm stat}\wedge h}\le L+u.
\tag{11}
$$

Before crossing, the sum is below $L$; its last upward increment is at most
$u$. Summing predictable stopping indicators at this bounded horizon gives

$$
d\,\mathbb E(T_n^{\rm stat}\wedge h)
\le\mu(q)\mathbb E(T_n^{\rm stat}\wedge h)
=\mathbb E S_{n,T_n^{\rm stat}\wedge h}
\le L+u.
\tag{12}
$$

Monotone convergence gives

$$
\mathbb E T_n^{\rm stat}\le c.
\tag{13}
$$

In particular this crossing is finite almost surely on the margin class.
Only bounded-stopping identities were used before taking the expectation
limit. The actual budget duration $T_n$ stops no later than
$T_n^{\rm stat}$, because its exact-support rule may pass first.

Now fix an item $i=(p,r)$. Before proposal $t$, the event $T_n\ge t$ is
determined by the past, while the next item has probability $a_n(i)$.
Therefore

$$
\begin{aligned}
\mathbb E\sum_{t=1}^{T_n}\mathbf1\{I_{n,t}=i\}
&=\sum_{t\ge1}\Pr(T_n\ge t)a_n(i)\\
&=a_n(i)\mathbb E T_n\le ca_n(i).
\end{aligned}
\tag{14}
$$

The cache received from earlier budgets does not change this identity.
Conditional on that earlier history, the next stream remains iid and the
bound (13) still applies. On the margin class every preceding budget passes
almost surely, so each declared component is eventually reached.

Item $i$ is acquired at most once. Its probability of ever being acquired is
at most its expected total number of proposals across all streams, and also
at most one. Consequently

$$
\begin{aligned}
\mathbb E_y T
&\le\sum_i\min\left\{1,c\sum_{n\in\mathcal K}a_n(i)\right\}\\
&=\sum_{r=1}^m\min\left\{P,c\sum_{n\in\mathcal K}w_n(r)\right\}
=B_c,
\qquad y\in\mathcal Y_\epsilon.
\end{aligned}
\tag{15}
$$

This is the finite clipping step. It uses an inclusion probability for each
actual item, with no promise about an unknown support or loss-count profile.

### An optional, explicitly charged census cap

The preceding auditor already has almost-sure finite completion. To obtain a
deterministic bound on the number of proposals, fix any $\eta>0$, put
$J=|\mathcal K|$, and cap each budget at

$$
M=\left\lceil\frac{cJD}{\eta}\right\rceil
\tag{16}
$$

proposals. Check for statistical or exact passage on the last proposal before
invoking the cap. At the first unpassed cap, acquire every remaining relevant
label and evaluate the global assertion exactly. This auditor uses at most
$JM$ proposals and at most $D$ distinct labels, and still has the stated
global validity and completeness.

On the margin class, a fallback implies that some corresponding uncapped
statistical crossing time exceeds $M$. By (13), Markov's inequality, and a
union bound,

$$
\Pr(\text{fallback})\le\frac{Jc}{M}\le\frac\eta D.
\tag{17}
$$

Ordinary acquisitions before fallback still obey the itemwise bound in (15).
The census adds at most $D$ labels, so this capped version has

$$
\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT\le B_c+\eta.
\tag{18}
$$

A forced census after $D$ proposals has no such uncharged itemwise guarantee:
it may acquire a rare item that none of the statistical streams proposed.
The coupon-completion auditor attains (15) directly; the optional deterministic
proposal cap pays the explicit extra term (18).

## 4. A pointwise geometric-mixture inequality

**Lemma.** For any increasing factor-four-separated sequence of budgets
$a_{j+1}\ge4a_j$,

$$
\sum_jw_{a_j}(r)
\le\frac{14}{3}\max_jw_{a_j}(r)
\tag{19}
$$

at every rank. For a factor-two-separated sequence, the corresponding bound
with constant $8$ holds.

**Proof.** Fix a rank. On the interval where all factors are positive, extend
the integer-budget formula by

$$
g(x)=\frac1m\prod_{u=1}^{r-1}
\frac{m-u-x+1}{m-u}.
\tag{20}
$$

At an integer budget with positive weight, $w_n(r)=ng(n)$.
The function $g$ is nonincreasing and log-concave, and $g(1)=1/m$.
For rank one the product is empty. All terminal zero weights can be discarded.

Call a positive representative low if $g(a_j)\ge g(1)/2$, and high
otherwise. The low representatives form an initial segment. If $a$ is its
last member, factor-four spacing gives

$$
\sum_{j:\,\mathrm{low}}w_{a_j}(r)
\le g(1)\sum_{j:\,\mathrm{low}}a_j
\le\frac43g(1)a\le\frac83w_a(r).
\tag{21}
$$

For consecutive positive high representatives $a<b$, necessarily $a>1$.
Concavity of $\log g$ on the three points $1,a,b$ gives

$$
\frac{g(b)}{g(a)}
\le\left(\frac{g(a)}{g(1)}\right)^{(b-a)/(a-1)}
\le2^{-(b/a-1)}.
\tag{22}
$$

Here $(b-a)/(a-1)\ge b/a-1$, and the base in the middle is below one half.
For $x=b/a\ge4$,

$$
\frac{w_b(r)}{w_a(r)}
\le x2^{-(x-1)}\le\frac12.
\tag{23}
$$

The last function decreases on $[4,\infty)$. Hence the high weights sum to
at most twice their first weight. Adding this to (21) gives (19), including
empty low or high segments.

For factor-two spacing, the geometric sum in (21) is at most $2a$, giving
a low contribution at most four times the largest weight. Split the high
sequence into its odd and even positions. Each subsequence is factor-four
separated; (22)--(23) bound each sum by twice its first weight. Their combined
contribution is at most four times the largest weight. The total is at most
eight times that weight. $\square$

This is a pointwise statement. In particular, for any factor-four-separated
representatives contained in the declared family and any prefix $k$,

$$
\sum_j\sum_{r>k}w_{a_j}(r)
\le\frac{14}{3}Z_{\rm tail}(k)
\le5Z_{\rm tail}(k).
\tag{24}
$$

No minimum-budget fraction or rank-decay assumption is used.

## 5. The separated-grid constant and deterministic alternative

For $f(x)=\operatorname{kl}(\operatorname{Ber}(x),
\operatorname{Ber}(\tau))$, we have $f(\tau)=f'(\tau)=0$ and

$$
f''(x)=\frac1{x(1-x)}\ge\frac1\tau
\qquad(\theta\le x\le\tau).
$$

Integrating twice gives

$$
d\ge\frac{\epsilon^2}{2\tau}.
\tag{25}
$$

Under (4),

$$
u=\log\left(1+\frac\epsilon{1-\tau}\right)
\le\frac\epsilon{1-\tau}\le\frac1{112}<\frac L{16}.
\tag{26}
$$

The last inequality follows from $L\ge\log4>1$. Thus

$$
c\le\frac{17}{8}H.
\tag{27}
$$

The factor-two part of the mixture lemma and (15) now imply

$$
B_c\le\sum_r\min\{P,8ce_r\}
\le\sum_r\min\{P,17He_r\}\le17G.
\tag{28}
$$

For completeness, the deterministic alternative in (6) queries every prompt
position in ranks $1,\ldots,k_\epsilon$. With the resulting known prefix
contribution $b_n$, use

$$
U_n=b_n+q_a(k_\epsilon).
\tag{29}
$$

Winning-rank tails decrease with the budget, so $U_n$ bounds the actual
$R_n$ for every declared $n$. On $\mathcal Y_\epsilon$,
$U_n\le R_n+q_a(k_\epsilon)\le\tau$. If the deterministic check fails
on another table, census the remaining positive-support items and evaluate
the family exactly. This is globally zero-error, all-safe complete, and
costs at most $Pk_\epsilon$ throughout the margin class.

Choose between this deterministic rule and the likelihood auditor using
their design bounds, before any labels are observed. This proves (6).
The optional capped likelihood version has the additional $\eta$ from (18);
choosing $\eta=F$ and combining with the deterministic rule gives the explicit
bound $18F$ with finitely bounded proposal counts. The uncapped coupon-completion
version gives $17F$ as stated.

## 6. An arbitrary-grid prefix and group construction

Take the existing greedy representatives: start at $a_1=\min\mathcal K$,
and after $a_j$ choose the smallest declared budget at least $4a_j$, if one
exists. Assign every declared budget to its preceding representative. Thus
each group has

$$
a_j\le n<4a_j,
\tag{30}
$$

and the representatives are factor-four separated. No undeclared budget is
added to the certificate.

Fix a prefix $k\in\{0,\ldots,m\}$ and acquire its $Pk$ labels once. Let

$$
b_n=\sum_p\sum_{r\le k}a_n(p,r)y_{p,r},\qquad
q_j=\sum_{r>k}w_{a_j}(r).
\tag{31}
$$

If $q_j\le\epsilon$, use the deterministic bounds $b_n+q_j$ for this
group. They pass on every margin-class table. If they fail on another table,
census the remaining group support and decide that group exactly. A group
with $q_j=0$ is already determined by the prefix.

For a group with $q_j>\epsilon$, use the residual test proved in
[finite saturation, Section 6](finite-saturation-theorem.md#6-a-globally-valid-prefix-and-residual-upper-bound).
That argument only uses $a_j\le n\le4a_j$ within the group, not the earlier
theorem's assumption $a_j\ge m/4$. The following records its parameters
and the changes needed here.

Draw iid tail proposals with item probability
$w_{a_j}(r)/(Pq_j)$, acquire each uncached label, and use fresh auxiliary
coins. On the representative's support put
$h_n(r)=w_n(r)/w_{a_j}(r)$, extended by zero outside it. The rank-product
identity gives $0\le h_n\le4$, and $h_n$ is nonincreasing in rank.
The tail-risk estimates are

$$
\widehat R^{\rm tail}_{n,t}
=\frac{q_j}{t}\sum_{s=1}^t h_n(\operatorname{rank}(I_s))B_s.
\tag{32}
$$

The frozen residual-concentration proof, combining binomial Bernstein,
conditional DKW, and summation by parts, gives

$$
\Pr\left\{\max_{n\text{ in group}}
|\widehat R^{\rm tail}_{n,t}-R_n^{\rm tail}|>4r_j(t,x)\right\}
\le4e^{-x},\qquad
r_j(t,x)=4\sqrt{\frac{q_j\tau x}{t}}+\frac{2q_jx}{t},
\tag{33}
$$

when the representative's actual tail risk $\mu_j$ is at most $2\tau$.
This is one event for the entire group, without a union bound over its targets.

At stages $\ell=1,2,\ldots$, take

$$
\begin{aligned}
\alpha_\ell&=\delta2^{-\ell},&
x_\ell&=L+(\ell+2)\log2,\\
A_j&=\frac{4096q_j\tau}{\epsilon^2},&
t_{j,\ell}&=\lceil A_jx_\ell\rceil.
\end{aligned}
\tag{34}
$$

Pass the group if every member satisfies

$$
b_n+\widehat R^{\rm tail}_{n,t_{j,\ell}}
+4r_j(t_{j,\ell},x_\ell)\le\tau.
\tag{35}
$$

For an unsafe group with $\mu_j\le2\tau$, passage requires failure of
(33), of probability at most $\alpha_\ell$ at that stage. If
$\mu_j>2\tau$, its declared representative is unsafe and passage forces
its empirical tail risk below $\mu_j/2$. The same Bernoulli lower-tail
bound as in the frozen proof gives probability at most

$$
\exp[-t_{j,\ell}\mu_j/(8q_j)]
\le\exp[-t_{j,\ell}\tau/(4q_j)]
\le e^{-x_\ell}\le\alpha_\ell.
\tag{36}
$$

Thus each unsafe group passes statistically with probability at most
$\sum_\ell\alpha_\ell=\delta$.

On a margin-class table, $\mu_j\le\tau$ and the radius in (34) is
less than $\epsilon/8$. On the event (33), every left side in (35) is
therefore at most $\tau-\epsilon+8r_j<\tau$. If $U_j$ is the number
of uncapped proposals until group passage, the unchanged stage-tail
calculation from the frozen proof gives

$$
\mathbb E U_j
\le t_{j,1}
 +\sum_{\ell\ge1}(t_{j,\ell+1}-t_{j,\ell})\alpha_\ell
\le12288Hq_j.
\tag{37}
$$

For this grouped construction, explicitly cap proposals at the number $D_j$
of positive-support group items after the prefix. If no passage has occurred,
query all remaining unknown group-support items and evaluate its risks
exactly. Its distinct-label cost beyond the prefix is at most
$\min\{U_j,D_j\}$ on the margin class: when $U_j<D_j$ it uses at most
$U_j$ labels; otherwise its entire support census uses at most $D_j$.
This cap is valid for (37), which charges total proposal expectation. It is
not used to assert the itemwise clipping bound (15).

Run all groups with one shared label cache, independent proposal streams,
and error allowance $\delta$ for each group. Issue the global certificate
only when every group passes. On an unsafe table, choose a fixed unsafe
group; its error bound alone controls global false certification. All exact
fallbacks preserve validity, and the finite caps give all-safe completeness.
On the margin class, the groups with $q_j\le\epsilon$ require no fallback,
so they add no uncharged cost.

Using (24) and (37),

$$
\begin{aligned}
\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT
&\le Pk+12288H\sum_jq_j\\
&\le Pk+61440H Z_{\rm tail}(k)\\
&\le61440\{Pk+H Z_{\rm tail}(k)\}.
\end{aligned}
\tag{38}
$$

The envelope $e_r$ is nonincreasing because every target row is. Incrementing
$k$ in the last braces changes its value by $P-He_{k+1}$, so

$$
\min_{0\le k\le m}\{Pk+H Z_{\rm tail}(k)\}
=\sum_r\min\{P,He_r\}=G.
\tag{39}
$$

Optimize this fixed prefix and also consider the deterministic
$k_\epsilon$ rule. This proves (7). The extension from the frozen
high-budget proof consists of partitioning the originally declared targets,
sharing their prefix and label cache, giving each group the global decision's
error allowance, and bounding the sum of residual masses by (24).

## 7. A full-dyadic asymptotic example

Let $P=1$, $m=2^J$, and
$\mathcal K=\{1,2,4,\ldots,m\}$. Fix $0<\tau\le1/8$ and
$0<\delta\le1/4$, and set

$$
\epsilon^2=\frac{\tau\log m}{m}.
\tag{40}
$$

For all sufficiently large $m$, (4) holds and $H=Lm/\log m$.
For $m\ge2$ and $r\ge2$, put $x=(r-1)/(m-1)$. The rank-product
formula and $1-z\le e^{-z}$ give, on positive support,

$$
w_n(r)\le\frac nm e^{-(n-1)x}
\le\frac{e^x}{emx}
\le\frac{m-1}{m(r-1)}\le\frac2r.
\tag{41}
$$

The middle inequality maximizes $n e^{-nx}$ over positive real $n$.
Zero weights obey the same bound, and $e_1=1$. Consequently

$$
\begin{aligned}
G&=\sum_r\min\{1,He_r\}
=O\left(H\left[1+\log\frac mH\right]\right)\\
&=O\left(\frac{m\log\log m}{\log m}\right)=o(m).
\end{aligned}
\tag{42}
$$

Theorem 1 therefore supplies one evidence-based auditor with this expected
distinct-label guarantee uniformly over the entire margin class. The envelope
normalizer $Z=\sum_re_r$ is $\Theta(\log m)$: (41) gives the upper
bound, and the disjoint representative bands from Section 3 of the
[nonzero theorem](nonzero-minimax-theorem.md#3-representative-groups-and-monotone-likelihood-ratios)
give the lower bound. Hence the earlier blanket guarantee
$\min\{m,49152ZH\}$ is of order $m$ on this family. Equation (42)
improves that earlier upper guarantee by an unbounded factor. It does not
assert that the earlier upper guarantee was a matching lower bound.

This is an asymptotic comparison of proved worst-case guarantees. It is not
a measured model experiment or a finite numerical savings claim. At the
original $P=32$, $m=64$, $\tau=1/10$, $\epsilon=1/160$,
$\delta=1/20$ geometry, the displayed bounds do not establish an improvement
over the existing $1934.2$ upper benchmark or the $1103.263793259$ lower
certificate. The [placement report](monotone-placement-report.md) retains
those stronger original-instance conclusions.

## 8. Scope

Theorems 1 and 2 concern fixed correct fractional labels, a known design
margin, and one certificate for the entire originally declared family. They
do not provide noisy-label guarantees, unknown-margin adaptation, a new-prompt
population guarantee, or a validated production implementation. Fresh auxiliary
coins simplify the exact proof but can discard information in fractional
observations. Tiny proposal weights can make computation much larger than
distinct-label cost.

The finite checker accompanying the all-grid theorem checks selected exact
geometry and likelihood identities. Those finite checks support their
implementation; the universal bounds rest on the proofs above. Scientific
priority, useful numerical performance, and independent human understanding
remain separate questions.
