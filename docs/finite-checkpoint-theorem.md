# A finite checkpoint upper bound for the original audit

Mathematical construction, 27 October 2026. This note retains the original
seven-budget decision and proves validity and completion for arbitrary fixed
real losses. Its expected-cost calculation reduces to the explicit finite
rational inequalities in Section 8. Those inequalities must be verified by
the release checker; this note does not assert that a production calculation,
source freeze, or saved reproduction has already completed.

The construction uses established convex-order, finite-population, and
expected-shortfall tools, attributed in Section 10. The proof was developed
with substantial Codex assistance; separate agent review is not independent
human verification. Prior exploratory searches selected this schedule.

## 1. Experiment and statement

There are 32 prompt pools, each with 64 candidates in a fixed total order,
best first. Every cell has a fixed correct real loss $y_{p,r}\in[0,1]$.
Querying one cell reveals its loss at unit cost. No labels are free.
For $\mathcal K=\{1,2,4,8,16,32,64\}$, define

$$
w_n(r)=\frac{\binom{64-r}{n-1}}{\binom{64}{n}},\qquad
a_n(p,r)=\frac{w_n(r)}{32},\qquad
R_n(y)=\sum_{p,r}a_n(p,r)y_{p,r}.
\tag{1}
$$

Impossible binomial choices are zero. These are the risks of selecting the
best item from a uniform $n$-subset without replacement. Set
$\tau=1/10$, $\epsilon=1/160$, and $\theta=\tau-\epsilon=3/32$.
A whole-family certificate asserts $R_n\le\tau$ for every $n\in\mathcal K$.
An unsafe table violates at least one of these seven inequalities; the
efficiency class is $\mathcal Y_\epsilon=\{y:\max_n R_n(y)\le\theta\}$.

**Theorem.** The evidence auditor in Section 6 has false-certificate
probability at most $1/200$ on every fixed unsafe real table and certifies
every fixed safe real table after at most 2048 queries. Its uniform expected
cost on $\mathcal Y_\epsilon$ is at most

$$
2000+16(\beta_{48}+\beta_{32}+\beta_{16}),
\tag{2}
$$

where the three constants are the finite rational quantities in (14).
The certificate inequalities (15) imply an upper bound of 2016.
An independent initial blind certificate with probability $9/199$, followed
otherwise by the evidence auditor, then has global error at most $1/20$
and uniform expected margin-class cost at most

$$
\boxed{C^*_{1/20}(1/160)\le\frac{383040}{199}<\frac{9671}{5}=1934.2.}
\tag{3}
$$

The last numerical conclusion is subject to the stated finite certificate
obligations. Here $C^*$ is the original minimax objective over auditors valid
on all real tables and complete on all safe tables. The evidence branch's
2016 bound does not itself improve 1934.2. Equation (3) explicitly uses
blind certification and is an upper bound, not an exact minimax value.

## 2. A fixed-total extremal population

For $N\ge1$, $0\le U\le N$, let $e(U)\in[0,1]^N$ have coordinates
$e_i(U)=\min\{1,\max\{0,U-i+1\}\}$. It consists of $\lfloor U\rfloor$
ones, its fractional remainder if nonzero, and zeros. Write $X_{U,u}$ for
the sum from a uniform $(N-u)$-subset of this population, $0\le u\le N$.

**Convex-order lemma.** If $x\in[0,1]^N$ has sum $U$, and $S$ is its sum
over a uniform $(N-u)$-subset, then, for every finite convex function $\phi$,

$$
\mathbb E\phi(S)\le\mathbb E\phi(X_{U,u}).
\tag{4}
$$

To prove it, average $\phi(\sum_{i\in A}x_i)$ over all subsets $A$ of the
specified size. The result $F(x)$ is convex and invariant under coordinate
permutations. Fix two interior coordinates with sum $t$. As one coordinate
varies over $[\max(0,t-1),\min(1,t)]$, the resulting convex function is
symmetric about $t/2$. A convex function on an interval is at most the
larger endpoint value; symmetry makes these two values equal. Replacing
the pair by an endpoint pair therefore cannot decrease $F$, and puts at
least one coordinate in $\{0,1\}$. Repeating finitely many times leaves
at most one interior coordinate. The preserved total determines $e(U)$
up to permutation, proving (4), including real-valued coordinates.

The vectors $e(U)$ increase coordinatewise with $U$. Coupling their samples
by the same random subset proves that $X_{U,u}$ increases in $U$ under
this coupling. Consequently decreasing convex hinge expectations decrease
with $U$, and increasing convex hinge expectations increase with $U$.
This argument bounds convex expectations; it does not assert stochastic
domination of $S$ by $X_{U,u}$.

## 3. Atom-correct lower expected shortfall

For a finite-support random variable $X$ and $0<\alpha<1$, let
$Q_X(t)=\inf\{z:\Pr(X\le z)\ge t\}$ for $0<t<1$, and define

$$
b_\alpha(X)=\frac1\alpha\int_0^\alpha Q_X(t)\,dt.
\tag{5}
$$

Let $v=Q_X(\alpha)$, $p_- =\Pr(X<v)$, and $b=b_\alpha(X)$. Then
$p_-\le\alpha\le\Pr(X\le v)$ and

$$
\alpha b=\mathbb E[X\mathbf1_{X<v}]+(\alpha-p_-)v,
\qquad \mathbb E[(v-X)_+]=\alpha(v-b).
\tag{6}
$$

The first identity includes the necessary fraction of the atom at $v$;
the second follows by subtraction. In particular $v\ge b$.
Equivalently,
$b=\max_t\{t-\mathbb E[(t-X)_+]/\alpha\}$.
Indeed the expression is concave and piecewise linear, with left and right
slopes $1-\Pr(X<t)/\alpha$ and $1-\Pr(X\le t)/\alpha$; its maximum occurs
at an $\alpha$-quantile. This also supplies a finite-support calculation.

Suppose a sampled population has total $U\ge L$, and put
$b=b_\alpha(X_{L,u})$, $v=Q_{X_{L,u}}(\alpha)$. By (4) and monotonicity,
$\mathbb E[(v-S)_+]\le\mathbb E[(v-X_{L,u})_+]$.
If $v>b$, the event $S<b$ implies $(v-S)_+>v-b$, so Markov's inequality
and (6) give $\Pr(S<b)\le\alpha$. If $v=b$, the right-hand expectation
is zero; hence $(b-S)_+=0$ almost surely and $\Pr(S<b)=0$. Thus

$$
U\ge L\quad\Longrightarrow\quad
\Pr\{S<b_\alpha(X_{L,u})\}\le\alpha.
\tag{7}
$$

The strict event is essential. For example, a constant $X=S=b$ would
satisfy $S\le b$ with probability one. No continuity assumption or
randomized treatment of a quantile atom is needed.

## 4. Upper hinges bound failure to pass

For any finite-support $X$ and real $b$, define

$$
B(X,b)=\min\left\{1,\inf_{v<b}
           \frac{\mathbb E[(X-v)_+]}{b-v}\right\}.
\tag{8}
$$

If the actual population total is $U\le V$, (4), monotonicity, and
$\mathbf1_{S\ge b}\le(S-v)_+/(b-v)$ imply
$\Pr(S\ge b)\le B(X_{V,u},b)$. No independence from another target is used.

This bound is exactly calculable from a finite law. If $b>\max\operatorname{supp}X$,
it is zero. If $b\le\mathbb EX$, it is one: Jensen's inequality makes every
ratio in (8) at least one. Otherwise take the minimum of one and the ratios
at support values $v<b$. Between consecutive support values the numerator
is affine, so the ratio has derivative of constant sign. As $v\to-\infty$
the ratio tends to one. As $v\uparrow b$ it diverges if $\Pr(X>b)>0$;
when $b$ is the support maximum, the ratio is constant on the last interval
below $b$. These observations cover all endpoints and prove the finite rule.

## 5. Head information, normalization, and every bin endpoint

Query all 1024 cells of ranks 1 through 32. The suffix has $N=1024$ cells.
For each target define

$$
h_n=\sum_{p,r\le32}a_n(p,r)y_{p,r},\qquad
q_n=\sum_{r=33}^{64}w_n(r)=\frac{\binom{32}{n}}{\binom{64}{n}},\qquad
c_n=\frac{w_n(33)}{32}.
\tag{9}
$$

The actual check $h_n+q_n\le\tau$ certifies a target deterministically.
It must be evaluated on every table; knowledge of $q_n\le\epsilon$ alone
does not certify it. For $n\ge8$ in the declared grid,
$q_n\le2^{-n}\le1/256<\epsilon$ (and $q_{64}=0$), since each factor
$(32-j)/(64-j)\le1/2$ in the binomial ratio. On the efficiency class,
$h_n\le R_n\le\theta$, so all four targets $8,16,32,64$ pass this check.

Statistical tests are used only for $D=\{1,2,4\}$, where $c_n>0$.
Suffix weights are nonincreasing with rank, giving normalized coordinates
$x_{n,i}=a_n(i)y_i/c_n\in[0,1]$ and total $U_n=\sum_i x_{n,i}$.
Then $R_n=h_n+c_nU_n$. Set

$$
T_n=\frac{\tau-h_n}{c_n},\qquad
g_n=\frac{\epsilon}{c_n},\qquad
t_n=\min\{\tau/c_n,N\},\qquad K_n=\lceil t_n-g_n\rceil.
\tag{10}
$$

All constants in the following table are exact.

| $n$ | $c_n$ | $g_n$ | $t_n$ | $K_n$ |
|---:|---:|---:|---:|---:|
| 1 | $1/2048$ | $64/5$ | $1024/5$ | 192 |
| 2 | $31/64512$ | $2016/155$ | $32256/155$ | 196 |
| 4 | $145/655872$ | $20496/725$ | $327936/725$ | 425 |

For $k=0,\ldots,K_n-1$, set $L_{n,k}=g_n+k$ and
$H_{n,k}=\min\{t_n,L_{n,k}+1\}$. Use bins $[L_{n,k},H_{n,k})$ except
that the last bin includes its right endpoint $t_n$. Thus every
$T_n\in[g_n,t_n]$, including all shared boundaries, has exactly one bin;
its index is $\min\{\lfloor T_n-g_n\rfloor,K_n-1\}$.
For a fixed table, the queried head and this bin are deterministic.
For a margin table, $h_n\le\theta$ gives $T_n\ge g_n$;
$h_n\ge0$ and the displayed $t_n=\tau/c_n<N$ give $T_n\le t_n$.

## 6. The complete evidence auditor

After the head, if any of $8,16,32,64$ fails its actual head check, acquire
the entire remaining suffix and use the exact census decision. Also take this fallback
if any still-needed statistical target has $T_n\notin[g_n,t_n]$.
These branches define the procedure outside the efficiency class. There is
no head-only certificate: $q_1=1/2>\tau$ makes its upper bound insufficient.

Otherwise choose one uniform random permutation of the suffix, independently
of the fixed table. Query its prefixes at the following checkpoints:

| Cells left unseen $u$ | Total labels acquired | Error allocation $\alpha_u$ |
|---:|---:|---:|
| 48 | 2000 | $1/250$ |
| 32 | 2016 | $3/4000$ |
| 16 | 2032 | $1/4000$ |

At a checkpoint, for each needed $n\in D$ use its head-selected bin and set

$$
S_{n,u}=\sum_{i\text{ in acquired suffix}}x_{n,i},\qquad
b_{n,k,u}=b_{\alpha_u}(X_{L_{n,k},u}).
\tag{11}
$$

For every target, also compute its acquired contribution
$\ell_{n,u}=h_n+\sum_{i\text{ in acquired suffix}}a_n(i)y_i$.
Certify exactly when all $\ell_{n,u}\le\tau$ and every target passes either
its actual deterministic head check or the strict test
$S_{n,u}<b_{n,k,u}$ at this checkpoint. The acquired-risk guard prevents a
certificate contradicting any labels already revealed.
Passes from different checkpoints are not combined. If no checkpoint
certifies, query all remaining cells and certify exactly when all seven
fully evaluated risks are at most $\tau$; otherwise return no certificate.
Every acquisition is charged once, and all targets reuse the same labels.

## 7. Uniform validity and all-safe completion

Fix an arbitrary unsafe real table and select one fixed unsafe budget $n$.
It cannot pass a deterministic upper bound or the exact census decision.
If $n\notin D$, the procedure goes to census. If it is a statistically
eligible target, its true normalized suffix total satisfies
$U_n>T_n\ge L_{n,k}$. Equation (7) bounds its statistical-pass probability
at checkpoint $u$ by $\alpha_u$. A whole-family certificate at that
checkpoint requires this particular target to pass. Hence the global error
is at most

$$
\alpha_{48}+\alpha_{32}+\alpha_{16}
=\frac1{250}+\frac3{4000}+\frac1{4000}=\frac1{200}.
\tag{12}
$$

There is no union bound over budgets for this single all-pass decision.
It does not authorize separately selectable target conclusions.

For rigor with early stopping, choose the entire suffix permutation
prospectively. Each scheduled prefix is a uniform subset, whether or not
the actual run reaches it. Define all three statistics on this probability
space and bound their unconditional pass events. An actual false pass is
contained in their union. No bound conditions on surviving an earlier test.

Every fixed safe table either certifies earlier or reaches a census, where
all its seven exact risks pass, including equality at $\tau$. Thus it
certifies after at most 2048 charged labels on every random tape. Unsupported
statistical cases cannot obstruct completion. Computation with exact real
numbers is permitted for this ideal mathematical construction.

## 8. Exact finite laws and the cost certificate

For integer $U=j$, the law of $X_{U,u}$ assigns mass
$\binom jz\binom{N-j}{u-z}/\binom Nu$ to $j-z$.
For $U=j+f$, $0<f<1$, it assigns the following masses:

$$
\begin{array}{c|c}
\text{sample sum}&\text{mass}\\ \hline
j-z&\displaystyle\frac{\binom jz\binom{N-j-1}{u-1-z}}{\binom Nu}\\[3pt]
j+f-z&\displaystyle\frac{\binom jz\binom{N-j-1}{u-z}}{\binom Nu}.
\end{array}
\tag{13}
$$

The first row omits the fractional coordinate; the second includes it.
These formulas count the omitted $u$-subset, with $z$ omitted ones.
The choices partition all such subsets, proving normalization, including
$U=0,N$ through the integer formula. All sums run over integers with valid
binomial choices; invalid choices contribute zero. For rational $U$, the
support and all probabilities are rational. Formula (6), splitting the last
atom as needed, and the finite rule after (8) therefore use exact rational
arithmetic. They do not replace fractional labels by Bernoulli labels.

On a margin table, $U_n\le T_n-g_n\le H_{n,k}-g_n$. Equations (4) and (8)
give $\Pr(S_{n,u}\ge b_{n,k,u})\le
B(X_{H_{n,k}-g_n,u},b_{n,k,u})$. Define the finite constants

$$
M_{n,u}=\max_{0\le k<K_n}B(X_{H_{n,k}-g_n,u},b_{n,k,u}),\qquad
\beta_u=\min\left\{1,\sum_{n\in D}M_{n,u}\right\}.
\tag{14}
$$

The required certificate consists of all $3(192+196+425)=2439$
target-bin/checkpoint calculations, followed by these exact comparisons:

$$
\boxed{\beta_{48}\le\frac{689}{1000},\qquad
\beta_{32}\le\frac{311}{1000},\qquad\beta_{16}=0.}
\tag{15}
$$

These are finite arithmetic obligations, not an assumed empirical error
rate. A release checker must recompute the distributions, cutoffs, all-bin
maxima, and comparisons from the fixed rational inputs, retain source pins,
and include independently enumerated small subset laws, hinge inequalities,
and atom-sensitive strict-tail checks. No production run is asserted here.

For a margin table the unsupported-head fallbacks never occur, by Section 5.
The acquired-risk guard also always holds, because
$\ell_{n,u}\le R_n\le\theta<\tau$ for every target and checkpoint.
At each prospective checkpoint, failure of the whole-family decision
implies failure of at least one of the three statistical targets. A union
bound gives probability at most $\beta_u$, regardless of dependence between
targets. Reaching the next stage requires this preceding failure. If $T$
counts charged labels through termination, pathwise

$$
T\le2000+16\mathbf1_{\{\text{continue after }48\}}
          +16\mathbf1_{\{\text{continue after }32\}}
          +16\mathbf1_{\{\text{continue after }16\}}.
\tag{16}
$$

Taking expectations proves (2), uniformly over all real margin tables.
Equation (15) then gives
$\mathbb ET\le2000+16(689+311)/1000=2016$. The last term in (16) charges
the final census labels; its bound is zero on this efficiency class, but
the fallback is still required for completion on other safe tables.

## 9. The disclosed mixture and executable scope

Before any labels are acquired, independently certify with probability
$p=9/199$ and otherwise run the evidence auditor. On every unsafe table,

$$
\Pr(\text{certificate})\le p+(1-p)/200=1/20,\qquad
\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT
\le\frac{190}{199}\,2016=\frac{383040}{199}.
\tag{17}
$$

Every safe table still certifies in finite time. The improvement relative
to $1934.2$ is exactly $9329/995$ expected labels. This mixture is admissible
under the original objective, which permits certification lotteries; it
should not be described as an evidence-only improvement.

The planned reference API is `audit(oracle, *, allow_blind=False,
randbelow=None)`, for this fixed geometry, with zero-based prompt indices
and one-based ranks. It accepts integer or `Fraction` losses in $[0,1]$
with denominator at most 1,000,000. Its default evidence mode excludes the
initial blind pass; opting into the mixed benchmark must be explicit.
An injected random source must supply independent uniform draws for the
theorem to apply. A valid integer range or a seed does not prove uniformity.

Malformed callbacks, unsupported losses, and invalid random draws raise
without issuing a certificate. Therefore a rational reference alone is
not an all-real-table admissible auditor: its input rejection excludes
some safe real tables. The ideal construction above supplies the all-real
theorem; conformance of a separately implemented reference is a separate
verification obligation. Exact labels, fixed rankings, and the original
prompt population remain assumptions throughout.

## 10. Classical foundations and research limits

[Greene and Wellner, *Exponential bounds for the hypergeometric distribution*
(2017), Section 3, Lemmas 1 and 4](https://sites.stat.washington.edu/jaw/JAW-papers/jaw-greene.bern.2017.pdf)
describe the bounded-population majorization and sampling convex-order
foundations, crediting Kemperman and Karlin. The binary population with at
most one fractional coordinate is an established extremal construction.
Section 2 supplies the specific fixed-total proof needed for both hinge
directions here. [Hoeffding (1963), Section 6, Theorem 4](https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf)
is a classical source for convex comparisons in sampling without replacement.

[Rockafellar and Uryasev, *Conditional Value-at-Risk for General Loss
Distributions* (2002), Theorem 10](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf)
establish the variational CVaR formula for distributions with atoms.
The lower-tail formulation in Section 3 is its sign-reversed counterpart;
the fractional-atom calculation is included to specify the strict test.
These general tools, Markov bounds, and finite union bounds are not new claims.

This construction concerns one fixed finite decision and one supplied-margin
cost objective. It makes no claim of scientific priority, optimal schedule,
measured model savings, label reliability, or transfer to new prompts.
Exploratory computations and assisted review motivated the candidate;
release verification must separately establish the finite certificate and
reference conformance. Neither proves independent human research ownership
or practical impact.
