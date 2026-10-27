# Complete proof appendices

These appendices consolidate the existing proofs; they make no claim of
new scientific results or independently established priority. The fixed
experiment, admissible auditors, exact validity and all-safe completion
requirements, and margin class $\mathcal Y_\epsilon$ are those in the
main text. In particular, labels are fixed and correct, losses may be
fractional, cost counts distinct acquisitions, and the supplied margin
is a design input rather than evidence. The lower bounds permit empty-query
certification lotteries and adaptive query choices.

All logarithms are natural. Throughout, unless an expressly broader
statement is given, the standing parameter conditions are

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
$$

We retain the common notation $a=\min\mathcal K$, $L=\log(1/\delta)$,
$H=\tau L/\epsilon^2$, $e_r=\max_{n\in\mathcal K}w_n(r)$,
$G=\sum_r\min\{P,He_r\}$, and $F=\min\{Pk_\epsilon,G\}$.
The tails are

$$
q_k=q_a(k)=\sum_{r>k}w_a(r)
=\frac{\binom{m-k}a}{\binom ma},\qquad
Z_{\rm tail}(k)=\sum_{r>k}e_r.
$$

Here $W_n$ denotes the rank returned by the budget-$n$ selector.
The index $k$ ranges from zero to $m$, and
$k_\epsilon=\min\{k:q_k\le\epsilon\}$. Binomial coefficients for
impossible choices are zero. The envelope is nonincreasing, and

$$
G=\min_{0\le k\le m}\{Pk+H Z_{\rm tail}(k)\},
$$

because increasing $k$ by one changes the objective by $P-He_{k+1}$.
These increments are nondecreasing, including equality cases.

Appendix letters prefix all retained section numbers and equation labels.
For example, (A1), (B5), and (C7) identify equations in different appendices. Original
setup equations that are not needed again are omitted, so label gaps are
intentional. Appendix A starts at A.2 because its source's Section 1 is
supplied by the main text and these standing conventions. Appendix C
starts at C.2 for the same reason. The source correspondence and surgical
changes are recorded in `source-map.md`.

# Appendix A. Universal lower bound and dyadic corollary

## A.2 Representative bands and the residual lower quantity

Choose the usual representatives: $a_1=\min\mathcal K$, then the smallest declared
budget at least four times the preceding representative, until none remains.
For representative $a_j$, put

$$
I_j=\{\lfloor m/(4a_j)\rfloor+1,\ldots,
\lfloor m/a_j\rfloor\},\qquad S_j=Pm/a_j.
$$

Let

$$
J_{32}=\#\{j:S_j\ge32H\}.
$$

**Proposition.** Every finite nonempty declared best-of-n grid satisfies

$$
\boxed{C^*(\epsilon)\ge HJ_{32}/4096.}
\tag{A1}
$$

The same conditional prior supported entirely on the exact efficiency class
serves every summand. No maximum-atom assumption on the original target rows
and no minimum-budget restriction are needed.

### The representative facts

Every declared budget in the group based at $a_j$ lies in
$[a_j,4a_j)$. For $a\le n$,

$$
w_n(r)\le\frac na w_a(r).
$$

On positive support this follows from

$$
w_n(r)=\frac nm\prod_{u=1}^{r-1}
\left(1-\frac{n-1}{m-u}\right),
$$

because every factor decreases with $n$; terminal zeros preserve the
inequality. Thus each group envelope is at most $4w_{a_j}$.

The bands $I_j$ are disjoint since $a_{j+1}\ge4a_j$. Each has mass
$c_j>1/4$ under its own representative. To check the finite endpoints,
write $a=a_j$, $h=\lfloor m/a\rfloor\ge1$, and
$\ell_0=\lfloor m/(4a)\rfloor=\lfloor h/4\rfloor$. A union bound gives
$\Pr(W_a\le\ell_0)\le a\ell_0/m\le1/4$, and the exact tail gives

$$
\Pr(W_a>h)=\frac{\binom{m-h}a}{\binom ma}
\le(1-h/m)^a\le e^{-ah/m},\qquad ah/m>h/(h+1).
$$

If $h\le3$, then $\ell_0=0$ and the band mass is greater than
$1-e^{-1/2}>1/4$. If $h\ge4$, it is greater than
$3/4-e^{-4/5}>1/4$. Impossible binomial choices make the tail zero,
so this includes $a=m$ and $m=1$.

## A.3 A maximal lemma for residual rows

Let $X_1,\ldots,X_D$ be independent Bernoulli variables with common mean
$p$. Fix $v\ge p$, $v>0$, $0<t\le2v$, and $\rho>0$.
Consider any family of nonnegative decreasing rows $b$ satisfying

$$
b_1\ge\cdots\ge b_D\ge0,\qquad
\sum_{i=1}^D b_i\le1,\qquad b_1\le\rho.
$$

Then

$$
\Pr\left\{\exists b:\sum_{i=1}^D b_i(X_i-p)>t\right\}
\le\exp[-t^2/(4v\rho)].
\tag{A2}
$$

**Proof.** Put $S_s=\sum_{i\le s}(X_i-p)$ and
$\lambda=t/(2v)\le1$. For $0\le\lambda\le1$,

$$
\begin{aligned}
\log\mathbb E e^{\lambda(X_i-p)}
&=\log(1+p(e^\lambda-1))-p\lambda\\
&\le p(e^\lambda-1-\lambda)\\
&\le p\lambda^2\le\lambda t/2.
\end{aligned}
\tag{A2a}
$$

Here $\log(1+z)\le z$ for $z\ge0$, and
$e^\lambda-1-\lambda\le\lambda^2$ on $[0,1]$; the latter follows
by bounding the exponential series by

$$
\lambda^2\sum_{k\ge2}1/k!=(e-2)\lambda^2\le\lambda^2.
$$

The last inequality uses $p\le v$ and $v\lambda=t/2$.
Independence therefore makes

$$
M_s=\exp\{\lambda(S_s-st/2)\},\qquad M_0=1,
$$

a nonnegative supermartingale. Its classical finite-horizon maximal
inequality [14] gives

$$
\Pr\left\{\exists s\le D:
S_s>\frac t2(s+1/\rho)\right\}
\le\exp[-t^2/(4v\rho)].
\tag{A2b}
$$

Indeed, such a prefix forces $M_s>\exp(\lambda t/(2\rho))$.
On the complementary event, append $b_{D+1}=0$ and use summation by parts:

$$
\begin{aligned}
\sum_{i=1}^D b_i(X_i-p)
&=\sum_{s=1}^D(b_s-b_{s+1})S_s\\
&\le\frac t2\left[
\sum_{s=1}^D s(b_s-b_{s+1})
+\frac1\rho\sum_{s=1}^D(b_s-b_{s+1})\right]\\
&=\frac t2\left(\sum_{i=1}^D b_i+\frac{b_1}\rho\right)
\le t.
\end{aligned}
\tag{A2c}
$$

The same prefix event works for every row, including terminal zero weights
and noninteger $1/\rho$. Thus subprobability rows require no
normalization and no target-cardinality union bound. $\square$

## A.4 A common safe prior with a deterministic head

Put

$$
k=\lfloor8H/P\rfloor,\qquad p=\tau-2\epsilon.
$$

If $k\ge m$, then $Pm\le 8H$, and hence $S_j\le Pm<32H$ for every
representative. In that case $J_{32}=0$ and (A1) is immediate. Hence suppose
$k<m$.

Under the unconditioned null prior $\Pi$, set every head loss at rank $r\le k$
to the fixed value $p$; set every suffix loss at $r>k$ independently to a
Bernoulli(p) bit. This is a finite distribution over fixed correct-loss
tables. The fractional head entries are allowed by the original model.

Every decreasing normalized rank row satisfies

$$
(k+1)w_n(k+1)\le1.
$$

Therefore every suffix item row, in rank-major order, has total mass at
most one and maximum entry at most

$$
\rho=1/[P(k+1)]<1/(8H).
\tag{A3}
$$

The expected full risk remains $p$ for every target: the deterministic
head and random suffix both have mean $p$. Applying (A2) with $v=\tau$ and
$t=\epsilon$ proves, for

$$
S=\{\max_{n\in\mathcal K}R_n\le\tau-\epsilon\},\qquad
\eta_S=\Pi(S^c),
$$

that

$$
\eta_S\le\exp[-\epsilon^2/(4\tau\rho)]
\le e^{-2L}=\delta^2\le\delta/4\le1/16.
\tag{A4}
$$

The conditional law $\Pi_S=\Pi(\,\cdot\mid S)$ is consequently well defined and is
supported on the exact original efficiency class. Its labels are not
claimed to be independent. Information calculations below use $\Pi$, not
conditional-label kernels under $\Pi _S$.

## A.5 Alternatives on the retained bands

For any retained representative with $S_j\ge 32H$,

$$
\frac m{4a_j}=\frac{S_j}{4P}\ge\frac{8H}{P}\ge k.
$$

As $k$ is integral, $\lfloor m/(4a_j)\rfloor\ge k$, so the entire band $I_j$
is in the random suffix. The band calculation in Section A.2 gives

$$
c_j:=\sum_{r\in I_j}w_{a_j}(r)>1/4.
\tag{A5}
$$

All representative bands are disjoint, including the retained ones.

Let $Q_j$ equal $\Pi$ except that the independent label mean inside this
one band is

$$
q=p+12\epsilon=\tau+10\epsilon\le13\tau/8<1/4.
$$

The full witness risk under $Q_j$ has mean

$$
\mu_j=p+12\epsilon c_j>\tau+\epsilon.
\tag{A6}
$$

Only the suffix is random. Its weights have sum at most one and each is
at most $\rho$; all its success probabilities are at most $q$. The ordinary
Bernoulli lower-tail moment bound therefore gives, for $s\ge 0$,

$$
\log\mathbb E_{Q_j}
\exp[-s(R_{a_j}-\mu_j)]\le s^2q\rho/2.
$$

Optimizing and using (A3), (A6), and $q\le 2\tau$,

$$
Q_j\{R_{a_j}\le\tau\}
\le\exp[-\epsilon^2/(2q\rho)]
\le\exp[-\epsilon^2/(4\tau\rho)]
\le\delta/4.
\tag{A7}
$$

For every event $E$ consisting only of certificate issuance, fixed-table
global validity and (A7) imply

$$
Q_j(E)\le\delta+\delta/4=5\delta/4.
\tag{A8}
$$

Thus the alternative need not be conditioned; the mass of its possibly
safe tables is charged explicitly.

## A.6 Finite transcripts and the residual lower bound

Fix any admissible auditor. Let $T_j$ be its distinct queries in band
$I_j$ before certification on safe tables, and set

$$
x_j=\mathbb E_{\Pi_S}T_j,\qquad
\kappa=256\epsilon^2/\tau,\qquad
B=\lceil H/512\rceil=\lceil L/(2\kappa)\rceil.
$$

If any retained $x_j$ is infinite, (A1) is immediate. Otherwise stop the
transcript at the first of certification, the $B$th distinct band query,
or a finite transition horizon $h$. Certification simultaneous with the
$B$th band query counts as reaching the cap. Let $E_h$ be certification
by that horizon strictly before the band cap.

Under the unconditioned product priors $\Pi$ and $Q_j$, every unseen band
label has its original Bernoulli(p) or Bernoulli(q) law, even with adaptive
query choices. Its divergence is at most

$$
\operatorname{kl}(p,q)
\le\frac{(12\epsilon)^2}{q(1-q)}
\le\frac{144\epsilon^2}{(7\tau/8)(3/4)}<\kappa.
\tag{A9}
$$

Every head label is deterministic and identical under both priors. Every
outside-band suffix label has an independent unchanged law. Choices,
randomization, and stopping use identical conditional rules given observed
histories. The finite-horizon chain rule charges only band labels, giving

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
\le\kappa[(1-\eta_S)x_j+\eta_SB].
\tag{A10}
$$

On $S$ the truncated band count is at most the final $T_j$; on its
complement it is at most $B$. No cost promise outside $S$ is used.

Suppose $x_j<B/8$. Almost-sure safe-table certification and Markov's
inequality imply

$$
\Pi\{\text{certify strictly before band cap}\}
\ge(1-\eta_S)(1-x_j/B)>(15/16)(7/8)>3/4.
$$

For some sufficiently large finite horizon, $\Pi (E_h)\ge 3/4$. From (A8),
binary data processing, and $L\ge\log4$,

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
\ge\tfrac34[L-\log(5/4)]-\log2\ge L/8.
\tag{A11}
$$

On the other hand, $\kappa \le \tau \le 1/8\le L/8$, so
$\kappa  B\le L/2+\kappa \le 5L/8$. Equations (A4) and (A10) imply

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
<\kappa B(1/8+1/16)\le15L/128<L/8,
$$

contradicting (A11). Consequently

$$
x_j\ge B/8\ge H/4096.
\tag{A12}
$$

Only the certificate events use increasing-horizon limits; every KL
calculation is at a finite horizon. Summing (A12) over the disjoint retained
bands under the same safe conditional prior gives expected total cost at
least $HJ_{32}/4096$. Some fixed table in that finite support has at least
the average expected cost. Taking the minimax infimum proves (A1).

## A.7 A centered common-safe prior on the domination tail

Write $a=\min\mathcal K$, and suppose $a<m/4$. Put

$$
\begin{aligned}
k_0&=\lfloor m/(a+1)\rfloor,& m'&=m-k_0,\\
q&=\Pr(W_a>k_0),& T&=\{k_0+1,\ldots,m-a+1\}.
\end{aligned}
$$

The exact adjacent-budget ratio is

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{n+1}{n}\frac{m-r-n+1}{m-n}.
$$

Where the weights are positive this ratio is at most one exactly when
$(n+1)r\ge m+1$. Terminal zeros preserve the inequality. Thus

$$
w_n(r)\le w_a(r)\quad(n\ge a,\ r\in T).
\tag{A13}
$$

Every nonnegative table supported on $T$ satisfies $R_n\le R_a$ for all
originally declared targets.

Also $q\ge 1/4$. Indeed, put $x=m/(a+1)\ge 2$. Every denominator in the
rank-by-rank product for $q$ exceeds $m-x=ax$, giving

$$
q=\prod_{u=0}^{k_0-1}\left(1-\frac a{m-u}\right)
\ge(1-1/x)^{k_0}\ge(1-1/x)^x\ge1/4.
\tag{A14}
$$

The final inequality follows because $(1-1/x)^x$ increases for $x\ge 2$.

Consider disjoint blocks of tail cells. A block has $N\ge 3$ cells with
positive original item weights $a_i=w_a(r_i)/P$, and put

$$
s=N\min_i a_i.
$$

**Centered tail block lemma.** If every selected block has $s\ge 8\epsilon$,
then one common safe prior gives

$$
C^*(\epsilon)\ge2^{-17}
\sum_{\text{selected blocks}}\min(N,Hs^2).
\tag{A15}
$$

Here blocks need not have comparable maximum and minimum weights.

To prove this, set every loss outside $T$ to zero and every unassigned tail
cell to

$$
p_0=(\tau-\epsilon)/q.
$$

Equations (A14) and the parameter range give
$15\tau /16\le p_0\le 1/2$. Independently in each block, choose a uniform
$k$-subset, put $p=k/N$, and assign

$$
k=\lfloor N\tau/8\rfloor,\qquad
y_i=p_0+\frac{\min_l a_l}{2a_i}(Z_i-p).
\tag{A16}
$$

The coefficient lies in $(0,1/2]$. Since $p\le \tau /8$, the losses are
nonnegative, and their maximum is at most $p_0+1/2\le 1$. Each block's
weighted risk is exactly $p_0$ times its original target mass, because
$\sum_i(Z_i-p)=0$. Therefore every null table has
$R_a=p_0q=\tau -\epsilon$, and (A13) puts it in the original efficiency class.

For one block at a time change its count to $k+d$, where

$$
d=\lfloor2\epsilon N/s\rfloor+1.
$$

Retain the same affine label maps and unchanged independent outside law.
The witness risk increases by $sd/(2N)>\epsilon$, so every alternative is
strictly unsafe. Moreover

$$
k+d\le N/64+N/4+1\le N/2\qquad(N\ge5).
$$

For $N=3,4$, one has $k=0$ and respectively $d\le 1,2$, so the same
count condition holds. Each label reveals its bit through a known
invertible map. Thus the finite-population lemma in Section C.2 applies exactly, with
no conditioning of slice placements, giving block cost at least

$$
\frac1{1024}\min\{N,N(k+1)L/d^2\}.
$$

Put $z=\epsilon  N/s$. If $z\ge 1$, then $d\le 3z$ and
$k+1>N \tau /8$, whence the information term is at least $Hs^2/72$.
If $z<1$, then $d\le 2$ and the information term is at least
$NL/4\ge N/4$. In both cases the displayed cost is at least
$\min\{N,Hs^2\}/(72\cdot1024)$, hence at least $2^{-17}\min\{N,Hs^2\}$.
All blocks use the same independent product of exact-count null laws.
Their expected distinct query counts add; taking a fixed table with at
least the average cost proves (A15).

### Application of the finite-population testing lemma

Section C.2 proves the exact-count lower bound used above, including its
$k=0$ case and independent, unchanged outside law. That lemma is stated
for a common positive amplitude and zero labels. It also applies to a
cellwise known invertible map $Z_i\mapsto b_i+c_iZ_i$ with $c_i>0$:
given the queried identity, the two observed outcomes are an invertible
relabeling of the bit, so each conditional KL divergence is unchanged.
This is a proof reduction; no actual label or profile promise is supplied
to the auditor for free. Each coordinate in (A16) uses such a map.

## A.8 Conditional-tail geometry, including block length three

For $a\ge 2$, the conditional tail is another exact best-of-a law:

$$
w_a(k_0+r)=qv_r,\qquad
v_r=\frac{\binom{m'-r}{a-1}}{\binom{m'}a}.
\tag{A17}
$$

Since $a<m/4$ implies $m\ge 4a+1$,
$m'\ge ma/(a+1)\ge 3a$. Put

$$
\begin{aligned}
\epsilon'&=\epsilon/q\le1/32,& H'&=Hq^2,\\
\ell&=\lfloor m'/a\rfloor\ge3,& D'&=m'-a+1,\\
U&=\lceil D'/2\rceil,& J'&=\lfloor U/\ell\rfloor.
\end{aligned}
$$

Here $J'\ge 1$, because
$D'-(2\ell -1)\ge (a-2)(\ell -1)\ge 0$, and $U\le m'/2$.
Use conditional-rank blocks

$$
\begin{aligned}
B_j&=\{(j-1)\ell+1,\ldots,j\ell\},\\
N&=P\ell,\qquad s'_j=\ell v_{j\ell}
\quad(1\le j\le J').
\end{aligned}
$$

Their original-weight minimum masses are $s_j=qs'_j$. Define

$$
R=\#\{j:s'_j\ge8\epsilon'\},\qquad
A=\sum_{j=1}^R\min(N,H'(s'_j)^2).
\tag{A18}
$$

Let $Q'_t=\sum_{r>t}v_r$,
$k'_{\epsilon'}=\min\{t:Q'_t\le\epsilon'\}$, and

$$
G'=\sum_r\min(P,H'v_r),\qquad
F'=\min(Pk'_{\epsilon'},G').
$$

The needed pure-geometric statement is

$$
R\ge1,\qquad F'\le8192A.
\tag{A19}
$$

### First block

If $\ell =3$, then $a/m'>1/4$, and the first two adjacent ratios of $v$
are at least $2/3$ because $m'\ge 3a$. Thus
$s'_1=3v_3\ge 1/3$.

If $\ell \ge 4$, the exact hazard identity gives

$$
s'_1=\frac{\ell a}{m'-\ell+1}Q'_{\ell-1}.
$$

Every factor in the $a$-factor product for $Q'_{\ell -1}$ exceeds
$1-1/a$. Also $m'\le a \ell +a-1$, so the prefactor is at least
$a/(5a/4-1)$. For $a=2,3$ this gives lower bounds $1/3$ and
$32/99$. For $a\ge 4$, use $(1-1/a)^{a-1}>1/3$ to obtain
$s'_1>(a-1)/[3(5a/4-1)]\ge 1/4$.
Consequently $s'_1\ge 1/4\ge 8\epsilon '$, proving $R\ge 1$.

### Pairing, comparability, and decay

Log-concavity of the positive best-of-a weights gives

$$
v_{2r-1}\le v_r^2/v_1.
$$

Pairing ranks, and padding by zeros outside the positive support, yields

$$
G'\le2\sum_{r=1}^U\min(P,H'v_r^2/v_1).
\tag{A20}
$$

Within the first half of the pool every adjacent ratio is at least
$1-2/\ell$. Since $(1-2/\ell )^\ell \ge 1/27$ for integers $\ell \ge 3$,
each full block's weights are at most 27 times its endpoint weight.
Further, $\ell  v_1\ge \ell /(\ell +1)\ge 3/4$. Therefore a full block contributes
at most

$$
\ell\min(P,729H'v_{j\ell}^2/v_1)
\le972\min(N,H'(s'_j)^2)
$$

to the sum in (A20). The remaining fewer than $\ell$ ranks before $U$
contribute at most $(4/3) \min(N,H'(s'_{J'})^2)$. Thus, writing
$A_{\rm all}=\sum_{j=1}^{J'}\min\{N,H'(s'_j)^2\}$,

$$
G'\le2048A_{\rm all}.
\tag{A21}
$$

Consecutive block endpoints also satisfy

$$
s'_{j+1}\le(8/11)s'_j.
\tag{A22}
$$

Indeed every adjacent ratio is at most $1-(a-1)/(m'-1)$, while
$\ell (a-1)/(m'-1)\ge 3/8$, and $(1-x)^\ell \le 1/(1+\ell  x)$.

### Removing small blocks

If $H'(8\epsilon ')^2\le N$, equation (A22) gives

$$
\sum_{j>R}\min(N,H'(s'_j)^2)
\le\frac{H'(8\epsilon')^2}{1-(8/11)^2}
<3H'(8\epsilon')^2\le3A.
$$

Thus (A21) implies $F'\le G'\le 8192A$.

If $H'(8\epsilon ')^2>N$, every retained block contributes $N$ to $A$.
When $R=J'$, the positive support has size
$D'\le 2U<2(J'+1)\ell \le 4J'\ell$, so $Pk'_{\epsilon '}\le 4A$.
When $R<J'$, the exact tail identity gives

$$
Q'_{(R+1)\ell}
\le(m'/a)v_{(R+1)\ell}
<(32/3)\epsilon'.
$$

Each additional $\ell$ ranks shrink the tail by at most
$(1-a/m')^\ell \le 4/7$. Once the positive support is exhausted the tail
is zero, so this statement also covers blocks extending past that support.
Since $(32/3)(4/7)^5<1$,
$k'_{\epsilon '}\le (R+6)\ell \le 7R\ell$; hence $Pk'_{\epsilon '}\le 7A$.
This proves (A19) in all cases.

All retained blocks have $N\ge 3$ and $s_j=qs'_j\ge 8\epsilon$, so (A15)
and (A18) give the original-grid lower bound

$$
C^*(\epsilon)\ge A/2^{17}.
\tag{A23}
$$

## A.9 Deterministic accounting against the full clipped envelope

Let

$$
F=\min(Pk_\epsilon,G),\quad
G=\sum_r\min(P,He_r),\quad
e_r=\max_{n\in\mathcal K}w_n(r).
$$

Continue to write $J_{32}$ for the number of broad representatives in
Section A.2. If $J_{32}\ge 1$, split the greedy groups into those first
$J_{32}$ groups and the remaining groups. The first part has envelope at
most $4\sum_{j\le J_{32}}w_{a_j}$, so its clipped contribution is at most
$4HJ_{32}$.

If there are remaining groups, let $b$ be their smallest budget. Then
$Pm/b<32H$. The pointwise domination calculation (A13), now using $b$,
gives envelope $w_b$ after rank $\lfloor m/(b+1)\rfloor$. Censusing that
prefix and charging the remaining row mass bounds this part by

$$
P\lfloor m/(b+1)\rfloor+H<33H.
$$

Clipping is subadditive, so

$$
F\le G\le37HJ_{32}\qquad(J_{32}\ge1).
\tag{A24}
$$

If $J_{32}=0$, put $S_0=Pm/a<32H$, and define the smallest-budget
singleton quantities

$$
G_a=\sum_r\min(P,Hw_a(r)),\qquad
F_a=\min(Pk_\epsilon,G_a).
$$

Since every $w_a(r)\le a/m=P/S_0$,

$$
G_a\ge\min(S_0,H)\ge S_0/32.
\tag{A25}
$$

Pointwise domination after $k_0=\lfloor m/(a+1)\rfloor$ gives
$G\le Pk_0+G_a\le S_0+G_a\le 33G_a$. Therefore

$$
F\le33F_a\qquad(J_{32}=0).
\tag{A26}
$$

For $2\le a<m/4$, use Sections A.7--A.8. Since $q>\epsilon$, the exact
conditional-tail identity implies

$$
k_\epsilon=k_0+k'_{\epsilon'}.
$$

Also clipping the original tail at $Hq$ instead of $Hq^2$ costs at
most a factor $1/q\le 4$, so

$$
G_a\le Pk_0+4G',\qquad
F_a\le Pk_0+4F'.
\tag{A27}
$$

The first term in $A$ is at least
$\min(P\ell ,H'/16)$. Since $m'\ge m/2$,
$\ell \ge 3m'/(4a)$, $q\ge 1/4$, and $S_0<32H$,

$$
A\ge\min(3S_0/8,H/256)\ge S_0/8192.
\tag{A28}
$$

Using (A19), (A27), and $Pk_0\le S_0$,

$$
F_a\le8192A+4\cdot8192A=40960A.
\tag{A29}
$$

Combining (A26) and (A29),

$$
F\le1{,}351{,}680A<2^{21}A.
\tag{A30}
$$

## A.10 Complete universal lower bound and endpoint cases

**Universal lower bound.** Under exactly the original rare-risk
parameter range and finite fractional-table objective, every nonempty
declared grid satisfies

$$
\boxed{C^*(\epsilon)\ge F/2^{38}.}
\tag{A31}
$$

If $J_{32}\ge 1$, (A1) and (A24) give the stronger bound
$C^*\ge F/(37\cdot4096)\ge F/2^{18}$. If $J_{32}=0$ and $a\ge m/4$, the
high-budget result proved in Sections C.2--C.5 gives
$C^*\ge F/2^{21}$.
If $J_{32}=0$ and $2\le a<m/4$, combine (A23) and (A30) to get (A31).

It remains to cover $J_{32}=0$, $a=1$, $m>4$. The domination tail has
$m'=\lceil m/2\rceil\ge3$, $q=m'/m\ge 1/2$, and uniform weights on its
$N=Pm'$ cells. Use this whole tail as one block in (A15), for which
$s=q$. Then

$$
C^*(\epsilon)\ge2^{-17}\min(Pm',Hq^2)
\ge2^{-19}\min(Pm,H)\ge2^{-19}F_a.
$$

Equation (A26) gives $C^*\ge F/(33\cdot2^{19})\ge F/2^{25}$, which is stronger
than (A31). Cases with $a=1,m\le 4$ were already in the high-budget case.
This exhausts every finite grid.

The constant is intentionally loose. The completion is structural: broad
scales use one safe conditioned product prior; the complementary regime
uses an exact common-safe prior supported on the smallest-budget domination
tail. Neither construction trusts the supplied margin on an unknown table.
Every alternative is handled under fixed-table global validity, and all
cost lower bounds permit adaptive acquisition and arbitrary certification
lotteries.

## A.11 Completion by the upper construction

Appendix B establishes in the same experiment

$$
C^*(\epsilon)\le\min\{Pk_\epsilon,61440G\}\le2^{16}F,
$$

and, on a factor-two-separated grid, $C^*(\epsilon)\le17F$.
Section B.6 supplies the arbitrary-grid construction, with the residual
concentration and stopping calculations proved in Section C.6.
Sections B.2--B.5 give the cached likelihood construction and its finite
completion, stopping, and expected coordinate-cost arguments.
Combining these upper bounds with Section A.10 proves the main theorem.

## A.12 A dyadic matching-rate corollary

Fix $\tau\in(0,1/8]$ and $\delta\in(0,1/4]$. Along powers of two
$m=2^d\to\infty$, take

$$
P=1,\qquad\mathcal K=\{1,2,4,\ldots,m\},\qquad
\epsilon^2=\frac{\tau\log m}{m}.
$$

For all sufficiently large $m$, the theorem's margin condition holds, and

$$
H=\frac{Lm}{\log m}.
$$

The factor-four representatives are $a_j=4^{j-1}$ up to the largest such
budget in the grid. For large $m$, the broad representative count is

$$
J_{32}=\left\lfloor\log_4\left(\frac{\log m}{32L}\right)\right\rfloor+1
=\Theta(\log\log m).
$$

Section A.6 gives $C^*(\epsilon)\ge HJ_{32}/4096$, while (A24) gives
$F\le37HJ_{32}$. The original dyadic grid is factor-two separated, so
Section B.5 yields

$$
\frac{HJ_{32}}{4096}\le C^*(\epsilon)
\le17F\le629HJ_{32}.
$$

Consequently

$$
\boxed{\qquad C^*(\epsilon)
=\Theta\!\left(\frac{m\log\log m}{\log m}\right).\qquad}
$$

The constants in this asymptotic statement may depend on the fixed
$\tau,\delta$. This is a cost theorem for fixed tables, with expectations
over audit randomization. It is not a measured model saving. It makes no claim that every safe table incurs the displayed worst-case cost.


# Appendix B. Cached likelihood and arbitrary-grid upper constructions

## B.1 Definitions and upper statements

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
\tag{B3}
$$

All logarithms are natural. Throughout the cost corollaries assume

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
\tag{B4}
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
\tag{B5}
$$

There is an admissible auditor with margin-class expected distinct-label cost
at most $B_c$. This statement needs only $0<\epsilon<\tau<1$ and
$0<\delta<1$. Under (B4), if successive declared budgets satisfy
$n_{j+1}\ge2n_j$, then

$$
\begin{aligned}
C^*(\epsilon)&\le\min\{Pk_\epsilon,B_c\}\\
&\le\min\{Pk_\epsilon,17G\}\le17F.
\end{aligned}
\tag{B6}
$$

Singleton families satisfy the spacing condition. The original family
$\{1,2,4,8,16,32,64\}$ does too. The guarantee is an expected distinct-label
bound, not a bound of the same size on random proposals or computation.

**Theorem 2: arbitrary-grid upper.** Every nonempty declared grid under (B4)
satisfies

$$
\begin{aligned}
C^*(\epsilon)&\le\min\{Pk_\epsilon,61440G\}\\
&\le61440F\le2^{16}F.
\end{aligned}
\tag{B7}
$$

Appendix A proves the matching lower bound within universal constants. Neither upper statement supplies selectable
simultaneous confidence intervals or authorizes certifying a chosen subset
when the originally declared global assertion fails.

## B.2 The cached likelihood auditor

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
\tag{B8}
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
\tag{B9}
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

## B.3 Expected proposals and distinct acquisitions

Let $T_n^{\rm stat}$ be the first crossing time of (B8) in the uncapped iid
stream, without the exact-support stopping rule. For a margin-class table,
$q=R_n(y)\le\theta$. The mean log increment is

$$
\mu(q)=q\log\frac\theta\tau
 +(1-q)\log\frac{1-\theta}{1-\tau}
\ge\mu(\theta)=d>0.
\tag{B10}
$$

The increment on a zero coin is $u>0$ and the increment on a one coin is
negative. For every finite horizon $h$,

$$
S_{n,T_n^{\rm stat}\wedge h}\le L+u.
\tag{B11}
$$

Before crossing, the sum is below $L$; its last upward increment is at most
$u$. Summing predictable stopping indicators at this bounded horizon gives

$$
d\,\mathbb E(T_n^{\rm stat}\wedge h)
\le\mu(q)\mathbb E(T_n^{\rm stat}\wedge h)
=\mathbb E S_{n,T_n^{\rm stat}\wedge h}
\le L+u.
\tag{B12}
$$

Monotone convergence gives

$$
\mathbb E T_n^{\rm stat}\le c.
\tag{B13}
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
\tag{B14}
$$

The cache received from earlier budgets does not change this identity.
Conditional on that earlier history, the next stream remains iid and the
bound (B13) still applies. On the margin class every preceding budget passes
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
\tag{B15}
$$

This is the finite clipping step. It uses an inclusion probability for each
actual item, with no promise about an unknown support or loss-count profile.

### An optional, explicitly charged census cap

The preceding auditor already has almost-sure finite completion. To obtain a
deterministic bound on the number of proposals, fix any $\eta>0$, put
$J=|\mathcal K|$, and cap each budget at

$$
M=\left\lceil\frac{cJD}{\eta}\right\rceil
\tag{B16}
$$

proposals. Check for statistical or exact passage on the last proposal before
invoking the cap. At the first unpassed cap, acquire every remaining relevant
label and evaluate the global assertion exactly. This auditor uses at most
$JM$ proposals and at most $D$ distinct labels, and still has the stated
global validity and completeness.

On the margin class, a fallback implies that some corresponding uncapped
statistical crossing time exceeds $M$. By (B13), Markov's inequality, and a
union bound,

$$
\Pr(\text{fallback})\le\frac{Jc}{M}\le\frac\eta D.
\tag{B17}
$$

Ordinary acquisitions before fallback still obey the itemwise bound in (B15).
The census adds at most $D$ labels, so this capped version has

$$
\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT\le B_c+\eta.
\tag{B18}
$$

A forced census after $D$ proposals has no such uncharged itemwise guarantee:
it may acquire a rare item that none of the statistical streams proposed.
The coupon-completion auditor attains (B15) directly; the optional deterministic
proposal cap pays the explicit extra term (B18).

## B.4 A pointwise geometric-mixture inequality

**Lemma.** For any increasing factor-four-separated sequence of budgets
$a_{j+1}\ge4a_j$,

$$
\sum_jw_{a_j}(r)
\le\frac{14}{3}\max_jw_{a_j}(r)
\tag{B19}
$$

at every rank. For a factor-two-separated sequence, the corresponding bound
with constant $8$ holds.

**Proof.** Fix a rank. On the interval where all factors are positive, extend
the integer-budget formula by

$$
g(x)=\frac1m\prod_{u=1}^{r-1}
\frac{m-u-x+1}{m-u}.
\tag{B20}
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
\tag{B21}
$$

For consecutive positive high representatives $a<b$, necessarily $a>1$.
Concavity of $\log g$ on the three points $1,a,b$ gives

$$
\frac{g(b)}{g(a)}
\le\left(\frac{g(a)}{g(1)}\right)^{(b-a)/(a-1)}
\le2^{-(b/a-1)}.
\tag{B22}
$$

Here $(b-a)/(a-1)\ge b/a-1$, and the base in the middle is below one half.
For $x=b/a\ge4$,

$$
\frac{w_b(r)}{w_a(r)}
\le x2^{-(x-1)}\le\frac12.
\tag{B23}
$$

The last function decreases on $[4,\infty)$. Hence the high weights sum to
at most twice their first weight. Adding this to (B21) gives (B19), including
empty low or high segments.

For factor-two spacing, the geometric sum in (B21) is at most $2a$, giving
a low contribution at most four times the largest weight. Split the high
sequence into its odd and even positions. Each subsequence is factor-four
separated; (B22)--(B23) bound each sum by twice its first weight. Their combined
contribution is at most four times the largest weight. The total is at most
eight times that weight. $\square$

This is a pointwise statement. In particular, for any factor-four-separated
representatives contained in the declared family and any prefix $k$,

$$
\sum_j\sum_{r>k}w_{a_j}(r)
\le\frac{14}{3}Z_{\rm tail}(k)
\le5Z_{\rm tail}(k).
\tag{B24}
$$

No minimum-budget fraction or rank-decay assumption is used.

## B.5 The separated-grid constant and deterministic alternative

For $f(x)=\operatorname{kl}(\operatorname{Ber}(x),
\operatorname{Ber}(\tau))$, we have $f(\tau)=f'(\tau)=0$ and

$$
f''(x)=\frac1{x(1-x)}\ge\frac1\tau
\qquad(\theta\le x\le\tau).
$$

Integrating twice gives

$$
d\ge\frac{\epsilon^2}{2\tau}.
\tag{B25}
$$

Under (B4),

$$
u=\log\left(1+\frac\epsilon{1-\tau}\right)
\le\frac\epsilon{1-\tau}\le\frac1{112}<\frac L{16}.
\tag{B26}
$$

The last inequality follows from $L\ge\log4>1$. Thus

$$
c\le\frac{17}{8}H.
\tag{B27}
$$

The factor-two part of the mixture lemma and (B15) now imply

$$
B_c\le\sum_r\min\{P,8ce_r\}
\le\sum_r\min\{P,17He_r\}\le17G.
\tag{B28}
$$

For completeness, the deterministic alternative in (B6) queries every prompt
position in ranks $1,\ldots,k_\epsilon$. With the resulting known prefix
contribution $b_n$, use

$$
U_n=b_n+q_a(k_\epsilon).
\tag{B29}
$$

Winning-rank tails decrease with the budget, so $U_n$ bounds the actual
$R_n$ for every declared $n$. On $\mathcal Y_\epsilon$,
$U_n\le R_n+q_a(k_\epsilon)\le\tau$. If the deterministic check fails
on another table, census the remaining positive-support items and evaluate
the family exactly. This is globally zero-error, all-safe complete, and
costs at most $Pk_\epsilon$ throughout the margin class.

Choose between this deterministic rule and the likelihood auditor using
their design bounds, before any labels are observed. This proves (B6).
The optional capped likelihood version has the additional $\eta$ from (B18);
choosing $\eta=F$ and combining with the deterministic rule gives the explicit
bound $18F$ with finitely bounded proposal counts. The uncapped coupon-completion
version gives $17F$ as stated.

## B.6 An arbitrary-grid prefix and group construction

Take the existing greedy representatives: start at $a_1=\min\mathcal K$,
and after $a_j$ choose the smallest declared budget at least $4a_j$, if one
exists. Assign every declared budget to its preceding representative. Thus
each group has

$$
a_j\le n<4a_j,
\tag{B30}
$$

and the representatives are factor-four separated. No undeclared budget is
added to the certificate.

Fix a prefix $k\in\{0,\ldots,m\}$ and acquire its $Pk$ labels once. Let

$$
b_n=\sum_p\sum_{r\le k}a_n(p,r)y_{p,r},\qquad
q_j=\sum_{r>k}w_{a_j}(r).
\tag{B31}
$$

If $q_j\le\epsilon$, use the deterministic bounds $b_n+q_j$ for this
group. They pass on every margin-class table. If they fail on another table,
census the remaining group support and decide that group exactly. A group
with $q_j=0$ is already determined by the prefix.

For a group with $q_j>\epsilon$, use the residual test proved in
Section C.6.
That argument only uses $a_j\le n\le4a_j$ within the group, not the high-budget
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
\tag{B32}
$$

The residual-concentration proof in Section C.6, combining binomial Bernstein,
conditional DKW, and summation by parts, gives

$$
\begin{aligned}
\Pr\left\{\max_{n\text{ in group}}
|\widehat R^{\rm tail}_{n,t}-R_n^{\rm tail}|>4r_j(t,x)\right\}
&\le4e^{-x},\\
r_j(t,x)&=4\sqrt{\frac{q_j\tau x}{t}}+\frac{2q_jx}{t}.
\end{aligned}
\tag{B33}
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
\tag{B34}
$$

Pass the group if every member satisfies

$$
b_n+\widehat R^{\rm tail}_{n,t_{j,\ell}}
+4r_j(t_{j,\ell},x_\ell)\le\tau.
\tag{B35}
$$

For an unsafe group with $\mu_j\le2\tau$, passage requires failure of
(B33), of probability at most $\alpha_\ell$ at that stage. If
$\mu_j>2\tau$, its declared representative is unsafe and passage forces
its empirical tail risk below $\mu_j/2$. The same Bernoulli lower-tail
bound as in Section C.6 gives probability at most

$$
\exp[-t_{j,\ell}\mu_j/(8q_j)]
\le\exp[-t_{j,\ell}\tau/(4q_j)]
\le e^{-x_\ell}\le\alpha_\ell.
\tag{B36}
$$

Thus each unsafe group passes statistically with probability at most
$\sum_\ell\alpha_\ell=\delta$.

On a margin-class table, $\mu_j\le\tau$ and the radius in (B34) is
less than $\epsilon/8$. On the event (B33), every left side in (B35) is
therefore at most $\tau-\epsilon+8r_j<\tau$. If $U_j$ is the number
of uncapped proposals until group passage, the stage-tail calculation in (C47) gives

$$
\mathbb E U_j
\le t_{j,1}
 +\sum_{\ell\ge1}(t_{j,\ell+1}-t_{j,\ell})\alpha_\ell
\le12288Hq_j.
\tag{B37}
$$

For this grouped construction, explicitly cap proposals at the number $D_j$
of positive-support group items after the prefix. If no passage has occurred,
query all remaining unknown group-support items and evaluate its risks
exactly. Its distinct-label cost beyond the prefix is at most
$\min\{U_j,D_j\}$ on the margin class: when $U_j<D_j$ it uses at most
$U_j$ labels; otherwise its entire support census uses at most $D_j$.
This cap is valid for (B37), which charges total proposal expectation. It is
not used to assert the itemwise clipping bound (B15).

Run all groups with one shared label cache, independent proposal streams,
and error allowance $\delta$ for each group. Issue the global certificate
only when every group passes. On an unsafe table, choose a fixed unsafe
group; its error bound alone controls global false certification. All exact
fallbacks preserve validity, and the finite caps give all-safe completeness.
On the margin class, the groups with $q_j\le\epsilon$ require no fallback,
so they add no uncharged cost.

Using (B24) and (B37),

$$
\begin{aligned}
\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT
&\le Pk+12288H\sum_jq_j\\
&\le Pk+61440H Z_{\rm tail}(k)\\
&\le61440\{Pk+H Z_{\rm tail}(k)\}.
\end{aligned}
\tag{B38}
$$

The envelope $e_r$ is nonincreasing because every target row is. Incrementing
$k$ in the last braces changes its value by $P-He_{k+1}$, so

$$
\min_{0\le k\le m}\{Pk+H Z_{\rm tail}(k)\}
=\sum_r\min\{P,He_r\}=G.
\tag{B39}
$$

Optimize this fixed prefix and also consider the deterministic
$k_\epsilon$ rule. This proves (B7). The extension from the high-budget proof in Section C.6 consists of partitioning the originally declared targets,
sharing their prefix and label cache, giving each group the global decision's
error allowance, and bounding the sum of residual masses by (B24).


# Appendix C. Finite-population, rankwise, and residual dependencies

Sections C.2--C.4 require the standing parameter conditions but no
minimum-budget restriction. Sections C.5--C.6 give the high-budget
specialization with $a\ge m/4$, establishing

$$
\frac{F}{2^{21}}\le C^*(\epsilon)\le12288F.
\tag{C6}
$$

For later references, repeat the prefix identity

$$
G=\min_{0\le k\le m}\{Pk+H Z_{\rm tail}(k)\}.
\tag{C4}
$$

The residual proof in C.6 itself uses only that every budget tested with
representative $a$ obeys $a\le n\le4a$. Appendix B applies that proof
separately to its groups; it does not impose $a\ge m/4$ on the original
grid. Thus these sections supply every project-specific lemma used in
Appendices A and B.

## C.2 An exact finite-population testing lemma

The following lemma concerns distributions over fixed oracle tables, not
a noisy-label model.

**Lemma.** A block has $N$ cells. Under a safe prior, exactly $k$ cells
have the same positive loss amplitude $\gamma\le1$, uniformly permuted,
and all other block cells have loss zero. Under an alternative, exactly
$k+d$ cells have amplitude $\gamma$, uniformly permuted. Assume

$$
k\ge0,\qquad d\ge1,\qquad k+d\le N/2.
\tag{C7}
$$

The outside table is independent of this block under both priors and has
the same distribution. Every table in the safe prior's support belongs
to $\mathcal Y_\epsilon$, and every alternative table is unsafe. If $X$
is an admissible auditor's expected number of distinct block queries
under the safe prior, then

$$
X\ge\frac1{1024}
\min\left\{N,\frac{N(k+1)L}{d^2}\right\}.
\tag{C8}
$$

Identical outside marginal laws without the stated independence would not
suffice for the proof.

**Proof.** Write $R=\min\{N,N(k+1)L/d^2\}$. The probability of certifying
without querying the block is the same under the two priors. Validity and
safe-table completeness therefore imply
$X\ge1-\delta\ge3/4$. This proves (C8) when $R<256$.

Otherwise set $b=\lfloor R/128\rfloor$, so
$b\ge R/256$ and $b\le N/128$. Stop the transcript at certification, at
the $b$th distinct block query, or at an additional finite transition
horizon. A certificate simultaneous with the $b$th block query counts as
reaching the cap. After $t<b$ distinct block queries with $S_t$ positive
labels, the next-label probabilities under the two priors are

$$
u=\frac{k-S_t}{N-t},\qquad
v=\frac{k+d-S_t}{N-t}.
\tag{C9}
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
\tag{C10}
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
\tag{C11}
$$

The sum is over the original feasible values of $s$. Extending that range
only adds nonnegative terms; the inequality is Vandermonde's identity.
Since $d\ge1$, (C11) also bounds the reciprocal with denominator
$k+d-S_t$.

Query choices, internal randomization, and decisions follow the same
conditional rule given a transcript. Outside labels have the same
conditional kernels, by independence and the unchanged outside law.
The finite-transcript KL chain rule therefore charges only block labels.
Replace each stopping indicator in the expected sum of (C10) by one and
use the completed permutation sequence to obtain

$$
\operatorname{KL}(\Pi^{(h)},Q^{(h)})
\le\frac{8d^2b}{N(k+1)}\le\frac L{16}.
\tag{C12}
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
\tag{C13}
$$

contradicting (C12). Thus $X\ge b/4\ge R/1024$. Only certificate-event
probabilities take an increasing-horizon limit; every KL calculation is
at a finite horizon. $\square$

## C.3 Hidden subsets on a common fractional safe table

Let $p_0=\tau-\epsilon$ and take the single fixed table
$y_{p,r}=p_0$. Every declared risk equals $\tau-\epsilon$.

**Lemma.** For any rank with $e_r\ge16\epsilon$, an admissible auditor's
expected number of queries at that rank on this table is at least

$$
\frac1{1024}\min\left\{P,\frac{Le_r}{\epsilon}\right\}.
\tag{C14}
$$

**Proof.** Choose a declared witness with weight $w=e_r$, put
$h=1-p_0\ge7/8$, and let

$$
s=\left\lfloor\frac{\epsilon P}{hw}\right\rfloor+1.
\tag{C15}
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
\tag{C16}
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
\tag{C17}
$$

If $\mathbb ET<b/4$, then $\Pr(T<b)>3/4$. Since $f$ is
nonincreasing, (C16)--(C17) would imply
$\delta\ge\mathbb Ef(T)>(3/4)\delta^{1/8}>\delta$.
Thus $\mathbb ET\ge b/4\ge R_0/256$ in this case as well.

Finally $s\le1+(8/7)\epsilon P/w$ implies

$$
R_0\ge\frac7{15}\min\left\{P,\frac{Lw}{\epsilon}\right\}.
\tag{C18}
$$

For $\epsilon P/w\ge1$, use $s\le(15/7)\epsilon P/w$; for
$\epsilon P/w<1$, use $s<15/7$ and $L\ge\log4>1$.
Equations (C17)--(C18), with $7/(15\cdot256)>1/1024$, prove (C14).
$\square$

## C.4 A rankwise lower bound for every declared grid

This section does not assume $a\ge m/4$.

**Proposition.** Under the standing parameter conditions, every nonempty
declared grid satisfies

$$
C^*(\epsilon)\ge\frac{A_{16}}{32768},
\qquad
A_{16}=\sum_{r:e_r\ge16\epsilon}\min\{P,He_r^2\}.
\tag{C19}
$$

**Proof.** First suppose $P\tau\ge4$. Set

$$
p_0=\tau-\epsilon,
\qquad k=\lceil Pp_0\rceil,
\qquad\gamma=\frac{Pp_0}k.
\tag{C20}
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
\tag{C21}
$$

For a rank with $w=e_r\ge16\epsilon$, choose a declared budget attaining
that envelope weight. Change only this rank's count to $k+d$, where

$$
d=\left\lceil\frac{2\epsilon P}{\gamma w}\right\rceil.
\tag{C22}
$$

Every table under this alternative has witness risk at least
$p_0+\gamma wd/P\ge\tau+\epsilon>\tau$. Since
$d\le P/6+1$ and $P\ge32$, (C21) gives $k+d<P/2$. The outside ranks are
independent and unchanged, so the finite-population lemma applies.

Write $z=\epsilon P/w$. If $z\ge1$, then $d<4z$ and

$$
\frac{P(k+1)L}{d^2}
\ge\frac{15}{256}Hw^2.
\tag{C23}
$$

If $z<1$, then $d\le3$ and

$$
\frac{P(k+1)L}{d^2}
\ge\frac5{48}\tau P^2L
\ge\frac5{12}LP>\frac P2.
\tag{C24}
$$

In both cases
$\min\{P,P(k+1)L/d^2\}\ge\min\{P,Hw^2\}/32$.
Equation (C8) therefore gives expected rank cost at least
$\min\{P,Hw^2\}/32768$. These rank counts add under the same safe prior.
Some fixed table in its finite support has cost at least the average,
proving (C19) when $P\tau\ge4$.

When $P\tau<4$, use the one constant safe table of Section C.3 and put

$$
B_{16}=\sum_{r:e_r\ge16\epsilon}
\min\left\{P,\frac{Le_r}{\epsilon}\right\}.
\tag{C25}
$$

For $z=Le_r/\epsilon\ge P$, the corresponding $A_{16}$ term is at most
the $B_{16}$ term. If $z<P$, then

$$
He_r^2=\frac\tau Lz^2
\le\frac{P\tau}Lz<3z.
\tag{C26}
$$

Thus $A_{16}\le3B_{16}$. The rank bounds (C14) add on the same fixed
table, giving $C^*(\epsilon)\ge B_{16}/1024\ge A_{16}/3072$.
This is stronger than (C19) and completes the proposition. $\square$

## C.5 High-budget envelope geometry

Assume now $a\ge m/4$ and write $c=1/4$. Each individual positive row is
log-concave, because

$$
\frac{w_n(r+1)}{w_n(r)}
=\frac{m-r-n+1}{m-r}
\tag{C27}
$$

is nonincreasing in $r$. Each row also has $w_n(1)=n/m\ge c$.
Multiplying consecutive ratio inequalities, or using concavity of
$\log w_n$, gives

$$
w_n(2r-1)\le\frac{w_n(r)^2}{w_n(1)}
\le\frac{w_n(r)^2}{c}.
\tag{C28}
$$

Extend rows by zero after their support; if $w_n(r)=0$, the left side is
also zero. Taking maxima over $n$ in (C28) gives

$$
e_{2r-1}\le\frac{e_r^2}{c}.
\tag{C29}
$$

This argument does not assume that the maximum of the log-concave rows is
itself log-concave. Since the envelope is decreasing, grouping its terms
in pairs and using (C29) yields

$$
G\le\frac2c\sum_r\min\{P,He_r^2\}.
\tag{C30}
$$

If $m\le4$, every positive best-of-$n$ weight is at least $1/6$.
Consequently every positive envelope weight exceeds $16\epsilon\le1/8$.
The sum in (C30) is then $A_{16}$ and $F\le8A_{16}$.

For the remaining argument take $m\ge5$. Every declared $n$ is at least
2 and $m\le4n$, so

$$
\frac{n-1}{m-1}\ge\frac{n-1}{4n-1}\ge\frac17.
\tag{C31}
$$

Thus every row, and then its envelope, satisfies

$$
e_{r+1}\le\frac67e_r.
\tag{C32}
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
\tag{C33}
$$

whenever $q_k>0$. If $q_R=0$, already $k_\epsilon\le R$.
Otherwise $R<m$, $w_a(R+1)\le e_{R+1}<16\epsilon$, and (C33) gives

$$
q_R<16\epsilon/c=64\epsilon.
$$

Consequently,

$$
\left\lceil\frac{\log64}{\log(4/3)}\right\rceil=15,
\qquad
k_\epsilon\le R+15\le16R.
\tag{C34}
$$

If $H(16\epsilon)^2>P$, each of the $R$ terms in $A_{16}$ equals $P$.
It follows that

$$
F\le Pk_\epsilon\le16A_{16}.
\tag{C35}
$$

If $H(16\epsilon)^2\le P$, (C32) instead gives

$$
\begin{aligned}
\sum_{r>R}\min\{P,He_r^2\}
&\le\frac{H(16\epsilon)^2}{1-(6/7)^2}\\
&\le\frac{H(16\epsilon)^2}{c}
\le\frac{A_{16}}c.
\end{aligned}
\tag{C36}
$$

The last inequality uses $R\ge1$ and the fact that an included term is
at least $H(16\epsilon)^2$. Combining (C30) and (C36) gives
$F\le G\le40A_{16}$. Together with the other cases, this proves

$$
F\le40A_{16},
\qquad
C^*(\epsilon)\ge\frac{F}{40\cdot32768}
\ge\frac{F}{2^{21}}.
\tag{C37}
$$

## C.6 A globally valid prefix-and-residual upper bound

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
\tag{C38}
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
\tag{C39}
$$

**Residual concentration.** If $\mu\le2\tau$, then for every $x>0$,
except with probability at most $4e^{-x}$,

$$
q\sup_s|\widehat F_t(s)-F_0(s)|\le r(t,x),
\qquad
r(t,x)=4\sqrt{\frac{q\tau x}t}+\frac{2qx}t.
\tag{C40}
$$

To see this, put $M=\sum_iB_i$ and $v=x/t$. Binomial Bernstein [12] gives,
except with probability $2e^{-x}$,

$$
|M/t-p|\le\sqrt{2pv}+\frac{2v}3,
\qquad M/t\le2p+\frac{7v}6.
$$

Conditional on $M=s>0$, the successful ranks are iid from their conditional
rank distribution [12]. Dvoretzky--Kiefer--Wolfowitz--Massart [13] bounds its empirical CDF
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

where $p\le2\tau/q$. Multiplying by $q$ proves (C40), including $p=0$.

For each target estimate its tail risk by

$$
\widehat R^{\rm tail}_{n,t}
=\frac qt\sum_{i=1}^t h_n(\operatorname{rank}(I_i))B_i.
\tag{C41}
$$

Summation by parts for the nonincreasing functions $h_n\in[0,4]$ gives,
on the one event (C40),

$$
\max_{n\in\mathcal K}
|\widehat R^{\rm tail}_{n,t}-R^{\rm tail}_n|
\le4r(t,x).
\tag{C42}
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
\tag{C43}
$$

Pass at the first stage at which

$$
b_n+\widehat R^{\rm tail}_{n,t_j}+4r_j\le\tau
\quad\hbox{for every }n\in\mathcal K.
\tag{C44}
$$

For global validity, consider any unsafe fixed table. If $\mu\le2\tau$,
passage requires failure of (C42), so has probability at most $\alpha_j$
at stage $j$. If $\mu>2\tau$, the declared representative $a$ is itself
unsafe, and passage implies $qM/t_j\le\tau<\mu/2$. A Bernoulli lower-tail
Chernoff bound gives

$$
\Pr(\hbox{pass at stage }j)
\le e^{-t_j\mu/(8q)}
\le e^{-t_j\tau/(4q)}
\le e^{-x_j}\le\alpha_j.
\tag{C45}
$$

The last step uses $t_j\ge4qx_j/\tau$, which follows from the standing parameter conditions and
(C43). Thus the probability of ever passing an unsafe table is at most
$\sum_j\alpha_j=\delta$. Neither case assumes the supplied margin is
true of that table.

On a table in $\mathcal Y_\epsilon$, $\mu\le\tau$ and

$$
r_j\le\frac\epsilon{16}
 +\frac{\epsilon^2}{2048\tau}<\frac\epsilon8.
\tag{C46}
$$

On (C42), each expression in (C44) is at most
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
\tag{C47}
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
\tag{C48}
$$

The same displayed bound holds when $q_k\le\epsilon$ by the deterministic
prefix rule. Optimize over $k$ using (C4), and also choose the deterministic
$k_\epsilon$ auditor when its bound is smaller. This gives

$$
C^*(\epsilon)\le\min\{Pk_\epsilon,12288G\}
\le12288F,
\tag{C49}
$$

completing the theorem.
