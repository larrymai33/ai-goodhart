# Finite minimax certification for every declared best-of-n grid

Candidate theorem, 27 October 2026. This note completes the finite cost
characterization in the same fixed fractional-table experiment as the
[nonzero theorem](nonzero-minimax-theorem.md). It removes the replication,
maximum-atom, and minimum-budget restrictions from the matching-order
statement. The [companion construction](cached-likelihood-audit.md) gives
both the universal upper bound and a smaller upper constant on separated
grids. Earlier proofs and their source pins remain unchanged.

This is a mathematical audit construction, not a new production auditing
engine or a measured model result. The proof was developed and checked
with substantial Codex assistance and has not received independent human
review. Its concentration, finite-population testing, geometric grouping,
and likelihood-ratio tools have substantial antecedents. No novelty claim
for those tools is made; scientific priority for the combined statement
remains unestablished. See the [priority comparison](all-grid-minimax-priority.md)
and [contribution disclosure](provenance.md).

## 1. Fixed experiment, objective, and theorem

Fix integers $P,m\ge1$ and a nonempty declared family
$\mathcal K\subseteq\{1,\ldots,m\}$. There are $P$ equally weighted prompt
pools, each containing $m$ distinct items in a fixed total rank order,
rank 1 being best. A query reveals one item's fixed correct loss
$y_{p,r}\in[0,1]$ at unit cost. No actual labels are free, and no known
relationship reveals another item's loss without querying it. Computation
is not charged.

The budget-$n$ selector draws a uniform $n$-subset without replacement and
returns its best-ranked member. Its weights, risk, and grid envelope are

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
 a_n(p,r)=\frac{w_n(r)}P,\qquad
 R_n(y)=\sum_{p,r}a_n(p,r)y_{p,r},\qquad
 e_r=\max_{n\in\mathcal K}w_n(r).
$$

Impossible binomial choices are zero. An admissible auditor may randomize,
choose unseen items adaptively, and abstain. It issues one whole-family
certificate asserting $R_n(y)\le\tau$ for every originally declared budget.
For every fixed table having some $R_n(y)>\tau$, its probability of ever
issuing that certificate is at most $\delta$. For every fixed safe table,
including boundary-safe tables, it certifies after finitely many queries
almost surely. Both requirements hold on all of $[0,1]^{Pm}$.

For a supplied design margin $\epsilon$, write

$$
\mathcal Y_\epsilon=
\{y:\max_{n\in\mathcal K}R_n(y)\le\tau-\epsilon\},\qquad
C^*(\epsilon)=\inf_A\sup_{y\in\mathcal Y_\epsilon}
\mathbb E_yT_A(y),
$$

where $T_A$ counts distinct labels acquired before certification. One
auditor serves the entire efficiency class; the design margin is not
trusted evidence about the unknown table. Repeated queries may use cached
labels, and empty-query certification lotteries are allowed.

Put

$$
\begin{aligned}
a&=\min\mathcal K,& L&=\log(1/\delta),&
H&=\frac{\tau L}{\epsilon^2},\\
q_k&=\sum_{r>k}w_a(r)
=\frac{\binom{m-k}a}{\binom ma},&
k_\epsilon&=\min\{k:q_k\le\epsilon\},\\
G&=\sum_{r=1}^m\min\{P,He_r\},&
F&=\min\{Pk_\epsilon,G\}.
\end{aligned}
$$

Prefix indices range from zero to $m$. Because every row and its envelope
are nonincreasing,

$$
G=\min_{0\le k\le m}\left\{Pk+H\sum_{r>k}e_r\right\}.
$$

Increasing the prefix by one changes the expression by $P-He_{k+1}$;
these increments are nondecreasing, proving the identity.

**Theorem.** Suppose

$$
0<\tau\le\frac18,\qquad
0<\epsilon\le\frac\tau{16},\qquad
0<\delta\le\frac14.
$$

For every finite $P,m$ and every nonempty declared grid,

$$
\boxed{\qquad\frac{F}{2^{38}}\le C^*(\epsilon)\le2^{16}F.\qquad}
$$

There is no density, replication, minimum-budget fraction, or grid-spacing
condition. The constants are deliberately loose. When successive declared
budgets are at least twice their predecessors, the companion construction
improves the upper bound to $C^*(\epsilon)\le17F$.

Sections 2--10 prove the universal lower bound. Section 11 identifies the
separate upper construction, and Section 12 gives a dyadic matching-rate
corollary. The theorem concerns one all-target assertion and worst-case
margin-class cost. It does not give selectable confidence bands, an
unknown-margin guarantee, or a sharper numerical lower certificate for the
original finite study instance.

## 2. Representative bands and the residual lower quantity

Choose the usual representatives: `a_1=min K`, then the smallest declared
budget at least four times the preceding representative, until none remains.
For representative `a_j`, put

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
\tag{1}
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
so this includes $a=m$ and $m=1$. This repeats the finite representative
argument in Section 3 of the [nonzero theorem](nonzero-minimax-theorem.md).

## 3. A maximal lemma for residual rows

Let `X_i` be independent Bernoulli(p), and consider any family of decreasing
nonnegative rows `b` satisfying

$$
\sum_i b_i\le1,\qquad b_1\le\rho.
$$

For `v>=p`, `v>0`, and `0<t<=2v`, the proof in Section 4 of the
[finite-density theorem](finite-density-theorem.md) gives

$$
\Pr\{\exists b:\sum_i b_i(X_i-p)>t\}
\le\exp[-t^2/(4v\rho)].
\tag{2}
$$

For clarity, put `S_s=sum_{i<=s}(X_i-p)` and `lambda=t/(2v)<=1`.
The process `exp(lambda(S_s-st/2))` is a nonnegative supermartingale.
Except on an event of probability at most the right side of (2), every
prefix obeys `S_s<=t(s+1/rho)/2`. Summation by parts, with a terminal zero
row entry, then gives simultaneously for every such row

$$
\sum_i b_i(X_i-p)
\le\frac t2\left(\sum_i b_i+\frac{b_1}{\rho}\right)
\le t.
$$

Thus replacing normalized rows by subprobability rows requires no new
concentration theorem and introduces no target-cardinality union bound.

## 4. A common safe prior with a deterministic head

Put

$$
k=\lfloor8H/P\rfloor,\qquad p=\tau-2\epsilon.
$$

If `k>=m`, then `Pm<=8H`, and hence `S_j<=Pm<32H` for every
representative. In that case `J_32=0` and (1) is immediate. Hence suppose
`k<m`.

Under the unconditioned null prior `Pi`, set every head loss at rank `r<=k`
to the fixed value `p`; set every suffix loss at `r>k` independently to a
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
\tag{3}
$$

The expected full risk remains `p` for every target: the deterministic
head and random suffix both have mean `p`. Applying (2) with `v=tau` and
`t=epsilon` proves, for

$$
S=\{\max_{n\in\mathcal K}R_n\le\tau-\epsilon\},\qquad
\eta_S=\Pi(S^c),
$$

that

$$
\eta_S\le\exp[-\epsilon^2/(4\tau\rho)]
\le e^{-2L}=\delta^2\le\delta/4\le1/16.
\tag{4}
$$

The conditional law `Pi_S=Pi(.|S)` is consequently well defined and is
supported on the exact original efficiency class. Its labels are not
claimed to be independent. Information calculations below use `Pi`, not
conditional-label kernels under `Pi_S`.

## 5. Alternatives on the retained bands

For any retained representative with `S_j>=32H`,

$$
\frac m{4a_j}=\frac{S_j}{4P}\ge\frac{8H}{P}\ge k.
$$

As `k` is integral, `floor(m/(4a_j))>=k`, so the entire band `I_j`
is in the random suffix. The band calculation in Section 2 gives

$$
c_j:=\sum_{r\in I_j}w_{a_j}(r)>1/4.
\tag{5}
$$

All representative bands are disjoint, including the retained ones.

Let `Q_j` equal `Pi` except that the independent label mean inside this
one band is

$$
q=p+12\epsilon=\tau+10\epsilon\le13\tau/8<1/4.
$$

The full witness risk under `Q_j` has mean

$$
\mu_j=p+12\epsilon c_j>\tau+\epsilon.
\tag{6}
$$

Only the suffix is random. Its weights have sum at most one and each is
at most `rho`; all its success probabilities are at most `q`. The ordinary
Bernoulli lower-tail moment bound therefore gives, for `s>=0`,

$$
\log\mathbb E_{Q_j}
\exp[-s(R_{a_j}-\mu_j)]\le s^2q\rho/2.
$$

Optimizing and using (3), (6), and `q<=2tau`,

$$
Q_j\{R_{a_j}\le\tau\}
\le\exp[-\epsilon^2/(2q\rho)]
\le\exp[-\epsilon^2/(4\tau\rho)]
\le\delta/4.
\tag{7}
$$

For every event `E` consisting only of certificate issuance, fixed-table
global validity and (7) imply

$$
Q_j(E)\le\delta+\delta/4=5\delta/4.
\tag{8}
$$

Thus the alternative need not be conditioned; the mass of its possibly
safe tables is charged explicitly.

## 6. Finite transcripts and the residual lower bound

Fix any admissible auditor. Let `T_j` be its distinct queries in band
`I_j` before certification on safe tables, and set

$$
x_j=\mathbb E_{\Pi_S}T_j,\qquad
\kappa=256\epsilon^2/\tau,\qquad
B=\lceil H/512\rceil=\lceil L/(2\kappa)\rceil.
$$

If any retained `x_j` is infinite, (1) is immediate. Otherwise stop the
transcript at the first of certification, the `B`th distinct band query,
or a finite transition horizon `h`. Certification simultaneous with the
`B`th band query counts as reaching the cap. Let `E_h` be certification
by that horizon strictly before the band cap.

Under the unconditioned product priors `Pi` and `Q_j`, every unseen band
label has its original Bernoulli(p) or Bernoulli(q) law, even with adaptive
query choices. Its divergence is at most

$$
\operatorname{kl}(p,q)
\le\frac{(12\epsilon)^2}{q(1-q)}
\le\frac{144\epsilon^2}{(7\tau/8)(3/4)}<\kappa.
\tag{9}
$$

Every head label is deterministic and identical under both priors. Every
outside-band suffix label has an independent unchanged law. Choices,
randomization, and stopping use identical conditional rules given observed
histories. The finite-horizon chain rule charges only band labels, giving

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
\le\kappa[(1-\eta_S)x_j+\eta_SB].
\tag{10}
$$

On `S` the truncated band count is at most the final `T_j`; on its
complement it is at most `B`. No cost promise outside `S` is used.

Suppose `x_j<B/8`. Almost-sure safe-table certification and Markov's
inequality imply

$$
\Pi\{\text{certify strictly before band cap}\}
\ge(1-\eta_S)(1-x_j/B)>(15/16)(7/8)>3/4.
$$

For some sufficiently large finite horizon, `Pi(E_h)>=3/4`. From (8),
binary data processing, and `L>=log 4`,

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
\ge\tfrac34[L-\log(5/4)]-\log2\ge L/8.
\tag{11}
$$

On the other hand, `kappa<=tau<=1/8<=L/8`, so
`kappa B<=L/2+kappa<=5L/8`. Equations (4) and (10) imply

$$
\operatorname{KL}(\Pi^{(h)},Q_j^{(h)})
<\kappa B(1/8+1/16)\le15L/128<L/8,
$$

contradicting (11). Consequently

$$
x_j\ge B/8\ge H/4096.
\tag{12}
$$

Only the certificate events use increasing-horizon limits; every KL
calculation is at a finite horizon. Summing (12) over the disjoint retained
bands under the same safe conditional prior gives expected total cost at
least `HJ_32/4096`. Some fixed table in that finite support has at least
the average expected cost. Taking the minimax infimum proves (1).

## 7. A centered common-safe prior on the domination tail

Write `a=min K`, and suppose `a<m/4`. Put

$$
k_0=\lfloor m/(a+1)\rfloor,\quad m'=m-k_0,\quad
q=\Pr(W_a>k_0),\quad T=\{k_0+1,\ldots,m-a+1\}.
$$

The exact adjacent-budget ratio is

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{n+1}{n}\frac{m-r-n+1}{m-n}.
$$

Where the weights are positive this ratio is at most one exactly when
`(n+1)r>=m+1`. Terminal zeros preserve the inequality. Thus

$$
w_n(r)\le w_a(r)\quad(n\ge a,\ r\in T).
\tag{13}
$$

Every nonnegative table supported on `T` satisfies `R_n<=R_a` for all
originally declared targets.

Also `q>=1/4`. Indeed, put `x=m/(a+1)>=2`. Every denominator in the
rank-by-rank product for `q` exceeds `m-x=ax`, giving

$$
q=\prod_{u=0}^{k_0-1}\left(1-\frac a{m-u}\right)
\ge(1-1/x)^{k_0}\ge(1-1/x)^x\ge1/4.
\tag{14}
$$

The final inequality follows because `(1-1/x)^x` increases for `x>=2`.

Consider disjoint blocks of tail cells. A block has `N>=3` cells with
positive original item weights `a_i=w_a(r_i)/P`, and put

$$
s=N\min_i a_i.
$$

**Centered tail block lemma.** If every selected block has `s>=8epsilon`,
then one common safe prior gives

$$
C^*(\epsilon)\ge2^{-17}
\sum_{\text{selected blocks}}\min(N,Hs^2).
\tag{15}
$$

Here blocks need not have comparable maximum and minimum weights.

To prove this, set every loss outside `T` to zero and every unassigned tail
cell to

$$
p_0=(\tau-\epsilon)/q.
$$

Equations (14) and the parameter range give
`15tau/16<=p_0<=1/2`. Independently in each block, choose a uniform
`k`-subset, put `p=k/N`, and assign

$$
k=\lfloor N\tau/8\rfloor,\qquad
y_i=p_0+\frac{\min_l a_l}{2a_i}(Z_i-p).
\tag{16}
$$

The coefficient lies in `(0,1/2]`. Since `p<=tau/8`, the losses are
nonnegative, and their maximum is at most `p_0+1/2<=1`. Each block's
weighted risk is exactly `p_0` times its original target mass, because
`sum_i(Z_i-p)=0`. Therefore every null table has
`R_a=p_0q=tau-epsilon`, and (13) puts it in the original efficiency class.

For one block at a time change its count to `k+d`, where

$$
d=\lfloor2\epsilon N/s\rfloor+1.
$$

Retain the same affine label maps and unchanged independent outside law.
The witness risk increases by `sd/(2N)>epsilon`, so every alternative is
strictly unsafe. Moreover

$$
k+d\le N/64+N/4+1\le N/2\qquad(N\ge5).
$$

For `N=3,4`, one has `k=0` and respectively `d<=1,2`, so the same
count condition holds. Each label reveals its bit through a known
invertible map. Thus the finite-population lemma stated below applies exactly, with
no conditioning of slice placements, giving block cost at least

$$
\frac1{1024}\min\{N,N(k+1)L/d^2\}.
$$

Put `z=epsilon N/s`. If `z>=1`, then `d<=3z` and
`k+1>N tau/8`, whence the information term is at least `Hs^2/72`.
If `z<1`, then `d<=2` and the information term is at least
`NL/4>=N/4`. In both cases the displayed cost is at least
`min(N,Hs^2)/(72*1024)`, hence at least `2^-17 min(N,Hs^2)`.
All blocks use the same independent product of exact-count null laws.
Their expected distinct query counts add; taking a fixed table with at
least the average cost proves (15).

### The finite-population testing fact used here

Section 2 of the [finite-saturation theorem](finite-saturation-theorem.md)
proves the following statement for this same fixed-table oracle model. A
block has $N$ cells. Under the null, a uniformly placed $k$-subset has one
positive amplitude and all other block labels are zero; under the
alternative the count is $k+d$. If $d\ge1$, $k+d\le N/2$, the outside law
is independent and unchanged, every null table belongs to the efficiency
class, and every alternative is unsafe, then the expected null block cost
is at least

$$
\frac1{1024}\min\left\{N,\frac{N(k+1)L}{d^2}\right\}.
$$

That proof uses finite capped transcripts, the exact hypergeometric
remaining-count probabilities, and an unconditional completed-permutation
reciprocal bound. It allows $k=0$. It also applies to a cellwise known
invertible map $Z_i\mapsto b_i+c_iZ_i$ with $c_i>0$: given the queried
identity, the two outcomes are an invertible relabeling and their
conditional KL is unchanged. This is a proof reduction; no actual label
or profile promise is supplied to the auditor for free. In (16), each
coordinate uses just such a map. The original lemma, including its proof
and constants, remains unchanged.

## 8. Conditional-tail geometry, including block length three

For `a>=2`, the conditional tail is another exact best-of-a law:

$$
w_a(k_0+r)=qv_r,\qquad
v_r=\frac{\binom{m'-r}{a-1}}{\binom{m'}a}.
\tag{17}
$$

Since `a<m/4` implies `m>=4a+1`,
`m'>=ma/(a+1)>=3a`. Put

$$
\epsilon'=\epsilon/q\le1/32,\quad H'=Hq^2,\quad
\ell=\lfloor m'/a\rfloor\ge3,\quad
D'=m'-a+1,\quad U=\lceil D'/2\rceil,\quad
J'=\lfloor U/\ell\rfloor.
$$

Here `J'>=1`, because
`D'-(2ell-1)>=(a-2)(ell-1)>=0`, and `U<=m'/2`.
Use conditional-rank blocks

$$
B_j=\{(j-1)\ell+1,\ldots,j\ell\},\quad
N=P\ell,\quad s'_j=\ell v_{j\ell}\qquad(1\le j\le J').
$$

Their original-weight minimum masses are `s_j=qs'_j`. Define

$$
R=\#\{j:s'_j\ge8\epsilon'\},\qquad
A=\sum_{j=1}^R\min(N,H'(s'_j)^2).
\tag{18}
$$

Let `Q'_t=sum_{r>t}v_r`,
`k'_{epsilon'}=min{t:Q'_t<=epsilon'}`, and

$$
G'=\sum_r\min(P,H'v_r),\qquad
F'=\min(Pk'_{\epsilon'},G').
$$

The needed pure-geometric statement is

$$
R\ge1,\qquad F'\le8192A.
\tag{19}
$$

### First block

If `ell=3`, then `a/m'>1/4`, and the first two adjacent ratios of `v`
are at least `2/3` because `m'>=3a`. Thus
`s'_1=3v_3>=1/3`.

If `ell>=4`, the exact hazard identity gives

$$
s'_1=\frac{\ell a}{m'-\ell+1}Q'_{\ell-1}.
$$

Every factor in the `a`-factor product for `Q'_{ell-1}` exceeds
`1-1/a`. Also `m'<=a ell+a-1`, so the prefactor is at least
`a/(5a/4-1)`. For `a=2,3` this gives lower bounds `1/3` and
`32/99`. For `a>=4`, use `(1-1/a)^(a-1)>1/3` to obtain
`s'_1>(a-1)/[3(5a/4-1)]>=1/4`.
Consequently `s'_1>=1/4>=8epsilon'`, proving `R>=1`.

### Pairing, comparability, and decay

Log-concavity of the positive best-of-a weights gives

$$
v_{2r-1}\le v_r^2/v_1.
$$

Pairing ranks, and padding by zeros outside the positive support, yields

$$
G'\le2\sum_{r=1}^U\min(P,H'v_r^2/v_1).
\tag{20}
$$

Within the first half of the pool every adjacent ratio is at least
`1-2/ell`. Since `(1-2/ell)^ell>=1/27` for integers `ell>=3`,
each full block's weights are at most 27 times its endpoint weight.
Further, `ell v_1>=ell/(ell+1)>=3/4`. Therefore a full block contributes
at most

$$
\ell\min(P,729H'v_{j\ell}^2/v_1)
\le972\min(N,H'(s'_j)^2)
$$

to the sum in (20). The remaining fewer than `ell` ranks before `U`
contribute at most `(4/3) min(N,H'(s'_{J'})^2)`. Thus, writing
`A_all=sum_{j=1}^{J'}min(N,H'(s'_j)^2)`,

$$
G'\le2048A_{\rm all}.
\tag{21}
$$

Consecutive block endpoints also satisfy

$$
s'_{j+1}\le(8/11)s'_j.
\tag{22}
$$

Indeed every adjacent ratio is at most `1-(a-1)/(m'-1)`, while
`ell(a-1)/(m'-1)>=3/8`, and `(1-x)^ell<=1/(1+ell x)`.

### Removing small blocks

If `H'(8epsilon')^2<=N`, equation (22) gives

$$
\sum_{j>R}\min(N,H'(s'_j)^2)
\le\frac{H'(8\epsilon')^2}{1-(8/11)^2}
<3H'(8\epsilon')^2\le3A.
$$

Thus (21) implies `F'<=G'<=8192A`.

If `H'(8epsilon')^2>N`, every retained block contributes `N` to `A`.
When `R=J'`, the positive support has size
`D'<=2U<2(J'+1)ell<=4J'ell`, so `Pk'_{epsilon'}<=4A`.
When `R<J'`, the exact tail identity gives

$$
Q'_{(R+1)\ell}
\le(m'/a)v_{(R+1)\ell}
<(32/3)\epsilon'.
$$

Each additional `ell` ranks shrink the tail by at most
`(1-a/m')^ell<=4/7`. Once the positive support is exhausted the tail
is zero, so this statement also covers blocks extending past that support.
Since `(32/3)(4/7)^5<1`,
`k'_{epsilon'}<=(R+6)ell<=7Rell`; hence `Pk'_{epsilon'}<=7A`.
This proves (19) in all cases.

All retained blocks have `N>=3` and `s_j=qs'_j>=8epsilon`, so (15)
and (18) give the original-grid lower bound

$$
C^*(\epsilon)\ge A/2^{17}.
\tag{23}
$$

## 9. Deterministic accounting against the full clipped envelope

Let

$$
F=\min(Pk_\epsilon,G),\quad
G=\sum_r\min(P,He_r),\quad
e_r=\max_{n\in\mathcal K}w_n(r).
$$

Continue to write `J_32` for the number of broad representatives in
Section 2. If `J_32>=1`, split the greedy groups into those first
`J_32` groups and the remaining groups. The first part has envelope at
most `4 sum_{j<=J_32}w_{a_j}`, so its clipped contribution is at most
`4HJ_32`.

If there are remaining groups, let `b` be their smallest budget. Then
`Pm/b<32H`. The pointwise domination calculation (13), now using `b`,
gives envelope `w_b` after rank `floor(m/(b+1))`. Censusing that
prefix and charging the remaining row mass bounds this part by

$$
P\lfloor m/(b+1)\rfloor+H<33H.
$$

Clipping is subadditive, so

$$
F\le G\le37HJ_{32}\qquad(J_{32}\ge1).
\tag{24}
$$

If `J_32=0`, put `S_0=Pm/a<32H`, and define the smallest-budget
singleton quantities

$$
G_a=\sum_r\min(P,Hw_a(r)),\qquad
F_a=\min(Pk_\epsilon,G_a).
$$

Since every `w_a(r)<=a/m=P/S_0`,

$$
G_a\ge\min(S_0,H)\ge S_0/32.
\tag{25}
$$

Pointwise domination after `k_0=floor(m/(a+1))` gives
`G<=Pk_0+G_a<=S_0+G_a<=33G_a`. Therefore

$$
F\le33F_a\qquad(J_{32}=0).
\tag{26}
$$

For `2<=a<m/4`, use Sections 7--8. Since `q>epsilon`, the exact
conditional-tail identity implies

$$
k_\epsilon=k_0+k'_{\epsilon'}.
$$

Also clipping the original tail at `Hq` instead of `Hq^2` costs at
most a factor `1/q<=4`, so

$$
G_a\le Pk_0+4G',\qquad
F_a\le Pk_0+4F'.
\tag{27}
$$

The first term in `A` is at least
`min(Pell,H'/16)`. Since `m'>=m/2`,
`ell>=3m'/(4a)`, `q>=1/4`, and `S_0<32H`,

$$
A\ge\min(3S_0/8,H/256)\ge S_0/8192.
\tag{28}
$$

Using (19), (27), and `Pk_0<=S_0`,

$$
F_a\le8192A+4\cdot8192A=40960A.
\tag{29}
$$

Combining (26) and (29),

$$
F\le1{,}351{,}680A<2^{21}A.
\tag{30}
$$

## 10. Complete universal lower bound and endpoint cases

**Universal lower bound.** Under exactly the original rare-risk
parameter range and finite fractional-table objective, every nonempty
declared grid satisfies

$$
\boxed{C^*(\epsilon)\ge F/2^{38}.}
\tag{31}
$$

If `J_32>=1`, (1) and (24) give the stronger bound
`C*>=F/(37*4096)>=F/2^18`. If `J_32=0` and `a>=m/4`, the
[finite-saturation theorem](finite-saturation-theorem.md) already gives
`C*>=F/2^21`.
If `J_32=0` and `2<=a<m/4`, combine (23) and (30) to get (31).

It remains to cover `J_32=0`, `a=1`, `m>4`. The domination tail has
`m'=ceil(m/2)>=3`, `q=m'/m>=1/2`, and uniform weights on its
`N=Pm'` cells. Use this whole tail as one block in (15), for which
`s=q`. Then

$$
C^*(\epsilon)\ge2^{-17}\min(Pm',Hq^2)
\ge2^{-19}\min(Pm,H)\ge2^{-19}F_a.
$$

Equation (26) gives `C*>=F/(33*2^19)>=F/2^25`, which is stronger
than (31). Cases with `a=1,m<=4` were already in the high-budget case.
This exhausts every finite grid.

The constant is intentionally loose. The completion is structural: broad
scales use one safe conditioned product prior; the complementary regime
uses an exact common-safe prior supported on the smallest-budget domination
tail. Neither construction trusts the supplied margin on an unknown table.
Every alternative is handled under fixed-table global validity, and all
cost lower bounds permit adaptive acquisition and arbitrary certification
lotteries.

## 11. The universal upper construction

The [companion proof](cached-likelihood-audit.md) establishes, in this same
fixed fractional-table experiment,

$$
C^*(\epsilon)\le\min\{Pk_\epsilon,2^{16}G\}\le2^{16}F.
$$

Its universal construction partitions the declared budgets using the
factor-four representatives, bounds the representative mixture pointwise
by a constant times the grid envelope, and applies globally valid
prefix/residual component tests. It issues one certificate only when every
component has passed. A fixed unsafe table has an unsafe component, so
assigning error level $\delta$ to each component controls this one all-pass
decision without a union bound over the number of components. That logic
does not authorize independently selectable target conclusions.

For a grid whose successive budgets differ by factors at least two, the
same companion gives a constructive bound $C^*(\epsilon)\le17F$ using
cached likelihood-ratio tests. Proposals remain iid; each repeated item
uses its cached loss and a fresh auxiliary Bernoulli coin. Almost-sure
coupon completion supplies exact certification of boundary-safe tables.
The companion supplies the stopping, caching, validity, and expected
coordinate-cost details; no uncharged proposal-count census fallback is
assumed here. These upper bounds and Section 10 prove the theorem.

## 12. A dyadic matching-rate corollary

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

Section 6 gives $C^*(\epsilon)\ge HJ_{32}/4096$, while (24) gives
$F\le37HJ_{32}$. The original dyadic grid is factor-two separated, so
its companion upper bound yields

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
over audit randomization. It is not a measured model saving. For this
family the earlier $\min\{Pm,\mathrm{constant}\cdot ZH\}$ upper bound
was only of census order, since $Z=\Theta(\log m)$; the new bound resolves
a strictly smaller asymptotic order. It makes no claim that every safe
table incurs the displayed worst-case cost.

## 13. Interpretation, attribution, and limits

The missing finite geometry is handled by two complementary common-safe
priors. A deterministic head allows the original product-prior argument to
add costs across arbitrarily many diffuse scales. When there are no such
scales, the smallest budget dominates every other target on a tail of
constant mass; centered fixed-count perturbations preserve its risk
exactly and therefore preserve safety for the whole grid. Conditional-tail
geometry then accounts for the clipped and deterministic-prefix terms.

This is a completion of one finite minimax characterization, with loose
universal constants. It does not improve the existing stronger
original-instance lower certificate, establish a new practical audit
engine, justify noisy or changing labels, or support inference to new
prompts. The exact fixed-label oracle, known ranks, supplied margin, and
single all-pass decision remain material assumptions.

Adaptive transcript KL, finite-population testing, geometric budget groups,
rare-event concentration, threshold sampling, caching, and likelihood-ratio
martingales all have prior literature. The separate
[priority comparison](all-grid-minimax-priority.md) distinguishes the
combined statement from those ingredients and records unresolved
comparisons. Mathematical proofs, bounded exact checks, public source
pins, and publication do not establish scientific novelty, independent
human understanding, real-model usefulness, or field impact.
