# Conservative arithmetic for the cached audit reference

This note proves the rounded likelihood process and finite-proposal
fallback used by the cached audit reference implementation. It supports
the [v0.13 cached likelihood construction](cached-likelihood-audit.md);
it does not improve that theorem's physical-label constant or establish a
new sequential testing principle. Likelihood-ratio martingales, bounded
stopping, and exponential tail bounds are classical tools. See the
[v0.13 attribution note](all-grid-minimax-priority.md) and the
[contribution disclosure](provenance.md).

There are two distinct claims. The ideal rounded and capped construction
below is an auditor for every fixed real loss table in the original
experiment. The executable callback library represents only its stated
bounded rational inputs and labels. It rejects unsupported designs and
labels, so the program by itself is not an all-real-table auditor for the
minimax infimum. The code contract and its resource limits are stated
separately in Section 10.

## 1. Experiment and notation

Fix integers P,m>=1 and a nonempty family of originally declared budgets
K contained in {1,...,m}. Every item i=(p,r) has a fixed correct loss
y_i in [0,1]. Acquiring a previously unseen loss costs one label. Put

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
a_n(p,r)=\frac{w_n(r)}P,\qquad
R_n=\sum_{p,r}a_n(p,r)y_{p,r}.
\tag{1}
$$

Impossible binomial choices have weight zero. Let D=Pm, J=|K|, and
a=min K. The auditor issues one certificate asserting R_n<=tau for
every originally declared budget. Its false-certificate probability must
be at most delta on every fixed table having some R_n>tau. On every
fixed safe table, including the boundary R_n=tau, it must certify after
finitely many acquisitions almost surely.

Assume

$$
0<\epsilon<\tau<1,\qquad 0<\delta<1,\qquad\eta>0,
$$

and write

$$
\theta=\tau-\epsilon,\quad L=\log(1/\delta),\quad
u=\log\frac{1-\theta}{1-\tau}>0,\quad
v=\log\frac\tau\theta>0.
\tag{2}
$$

The efficiency class consists of all fixed tables with
max_n R_n<=theta. The supplied margin selects the design; it is never
treated as evidence about the actual table.

The smallest-budget tail and deterministic prefix are

$$
q_a(k)=\frac{\binom{m-k}a}{\binom ma},\qquad
k_\epsilon=\min\{k:q_a(k)\le\epsilon\},\qquad A=Pk_\epsilon.
\tag{3}
$$

For k beyond the positive support the tail is zero. Winner-rank tails
decrease with budget, so q_n(k)<=q_a(k) for every original n. In
particular, acquiring the first k_epsilon ranks of every prompt provides
the valid bounds

$$
U_n=\sum_p\sum_{r\le k_\epsilon}a_n(p,r)y_{p,r}
       +q_a(k_\epsilon).
\tag{4}
$$

Every margin-class table satisfies U_n<=R_n+epsilon<=tau. If additional
cached labels are used in a sharper known-contribution-plus-missing-mass
bound, that bound is at most (4) once the entire prefix is known.

## 2. Exact logarithm and square-root enclosures

The arithmetic needs rational enclosures rather than floating-point
transcendental evaluations. For a positive rational x, choose an integer
k so that z=x*2^(-k) lies in [1,2). Then

$$
\log x=k\log2+\log z.
\tag{5}
$$

For t=(z-1)/(z+1), one has 0<=t<1/3 and

$$
\log z=2\sum_{j=0}^{N-1}\frac{t^{2j+1}}{2j+1}+R_N,
\qquad
0\le R_N\le
\frac{2t^{2N+1}}{(2N+1)(1-t^2)}.
\tag{6}
$$

Indeed the omitted series has nonnegative terms, and replacing every
denominator by 2N+1 bounds it by the indicated geometric series.
The same formula at t=1/3 encloses log 2. Every partial sum and remainder
bound is rational. Combining these intervals in (5), reversing endpoints
when multiplying by negative k, gives a rigorous interval for log x.
Choose N large enough and check that the combined interval has the
requested width. The series converges geometrically.

The [design module](../goodhart_audit/cached_math.py) handles x<1 by
enclosing log(1/x) and negating its endpoints. For x>1 it chooses
N=ceil((b+bit_length(k+1)+8)/3), where b is the requested precision.
It rounds the combined lower endpoint down and upper endpoint up on the
grid 2^(-(b+2)), then checks that their width is at most 2^(-b).
Those final outward roundings preserve containment. A failed width or
resource check rejects the calculation; it does not weaken the interval.

For x=p/q>=0 and an integer scale S>0, an upper square-root enclosure is

$$
\operatorname{sqrt\_upper}_S(x)
=\frac{\lceil S\sqrt{x}\rceil}{S}.
\tag{7}
$$

Its numerator can be computed using integer square root. Let
h=isqrt(floor(p*S^2/q)); increment h exactly when h^2*q<p*S^2.
The returned rational h/S has square at least x and differs from sqrt(x)
by less than 1/S, except that equality is exact. Both assertions can be
verified with integer comparisons. No floating square root is trusted.

These formulas specify sufficient certificates; their proof does not
assume that machine floating-point rounding happens to be conservative.

## 3. The integer likelihood walk

Choose S=2^B with integer B>=1. Obtain logarithm intervals
[u_lo,u_hi], [v_lo,v_hi], [L_lo,L_hi], each of width at most 1/S, and set

$$
U=\lfloor S u_{\rm lo}\rfloor,\qquad
V=\lceil S v_{\rm hi}\rceil,\qquad
E=\lceil S L_{\rm hi}\rceil.
\tag{8}
$$

The normalized quantities are u_-=U/S, v_+=V/S, and ell=E/S. In
particular, the threshold E is an integer, whereas ell denotes the
threshold in natural-log units. The enclosures give

$$
0\le u-u_-\le2/S,\qquad
0\le v_+-v\le2/S,\qquad
0\le\ell-L\le2/S.
\tag{9}
$$

Refine until the exact rational lower drift

$$
d_-=(1-\theta)u_- -\theta v_+>0
\tag{10}
$$

is certified. This also forces U>0. Define

$$
c_- =\frac{\ell+u_-}{d_-}
=\frac{E+U}{(1-\theta)U-\theta V},\qquad
B_-=\sum_{r=1}^m\min\left\{P,c_-\sum_{n\in K}w_n(r)\right\}.
\tag{11}
$$

The cancelled integer-scale expression for c_- prevents a units mismatch.
All quantities in (10)-(11) are rational once the intervals are chosen.

For each budget, prepare a fresh independent iid proposal stream with
item law a_n. Each proposal acquires the label only if it is absent from
the shared cache, then generates a fresh auxiliary Bernoulli(y_i) coin,
including on cache hits. Add U for coin zero and -V for coin one to an
integer statistic starting at zero. Pass statistically when that statistic
is at least E. Before further proposals, and after an acquisition that
completes the positive support, exact risk evaluation may pass the budget
or terminate without a certificate when it is unsafe.

Processing budgets in increasing order is the executable convention. None
of the probability or label-cost arguments require free labels or depend
on an unobserved label profile.

## 4. Global validity of the rounded process

Condition throughout on the fixed loss table. A budget's proposal and
fresh-coin pairs are iid, and each coin has mean q=R_n. For the ideal
log increment X, which equals u or -v, the likelihood multiplier satisfies

$$
\mathbb E_q e^X
=(1-q)\frac{1-\theta}{1-\tau}+q\frac\theta\tau
=1+\frac{(\tau-q)(\tau-\theta)}{\tau(1-\tau)}\le1
\tag{12}
$$

when q>tau. The rounded increment X_- equals u_- or -v_+ and obeys
X_-<=X for either coin outcome. Its exponential is therefore also a
nonnegative supermartingale multiplier on an unsafe component. A rounded
crossing has normalized statistic at least ell>=L. Ville's inequality
bounds its probability by exp(-ell)<=delta. Equivalently, each rounded
crossing implies an ideal crossing on the same coin path.

This remains true conditional on previous budget streams: the table is
fixed and the next stream and auxiliary draws are fresh and independent.
Caching changes which proposals purchase labels, not the stream law.

On a fixed unsafe table, choose one fixed originally declared budget with
R_n>tau. A false global certificate requires that budget to pass
statistically, because its exact risk cannot pass. Deterministic prefix
and census decisions also cannot falsely certify. Thus the global
false-certificate probability is at most delta. There is no division by
J: this is the original intersection-union accounting for one all-pass
assertion. It does not authorize independently selectable budget claims or
simultaneous confidence intervals.

Before returning a global certificate, the implementation also rejects if
any budget's known partial contribution already exceeds tau, even when
that budget passed statistically earlier and its support remains
incomplete. Nonnegative unseen losses cannot repair this deterministic
contradiction. The override only removes false certificates, never changes
behavior on a safe or margin-class table, and buys no additional labels.

## 5. Expected proposals and ordinary cached acquisitions

On a margin-class table q<=theta, the mean rounded increment obeys

$$
\mu_-(q)=(1-q)u_- -qv_+\ge d_->0.
\tag{13}
$$

Let T_stat^- be the first threshold crossing of the uncapped rounded
stream, without exact-support stopping. For any finite h, its stopped
statistic is at most ell+u_-: before crossing it is below ell and its
last upward increment is u_-. Summing predictable stopping indicators at
the bounded horizon gives

$$
d_-\,\mathbb E(T_{\rm stat}^-\wedge h)
\le\mathbb E S^-_{T_{\rm stat}^-\wedge h}
\le\ell+u_-.
\tag{14}
$$

Monotone convergence yields E T_stat^-<=c_-. In particular it is finite
almost surely on the margin class. An exact-support rule stops no later.

For a fixed item i, the event that proposal t is requested is determined
before that proposal. Its next-item probability remains a_n(i), including
conditional on the cache inherited from previous streams. Hence

$$
\mathbb E\sum_{t\le T_n}\mathbf1\{I_{n,t}=i\}
=a_n(i)\mathbb E T_n\le c_-a_n(i).
\tag{15}
$$

Every label is bought at most once. Its inclusion probability in ordinary
statistical acquisition is at most one and at most the sum of the expected
visits in (15). Summing over actual items gives B_- in (11). This bound
also applies to the ordinary acquisitions before a proposal-cap fallback,
which form a subset of those in the corresponding uncapped construction.
The separately purchased fallback labels must still be charged.

## 6. An affinity tail bound for the implemented walk

Let

$$
\psi=\sqrt{\theta\tau}
     +\sqrt{(1-\theta)(1-\tau)}<1.
\tag{16}
$$

The strict inequality follows from Cauchy-Schwarz, since the distinct
Bernoulli parameters theta and tau give distinct unit vectors of square
roots. This is the classical half-power affinity underlying a Chernoff
bound, not a new concentration principle. See, for example,
[Nielsen, Section 1.1, equation (2)](https://arxiv.org/html/2207.03745v3).

For the ideal increment, E_q exp(-X/2) is increasing in q because
exp(v/2)>exp(-u/2). At q=theta it equals psi. By (9),

$$
\mathbb E_q e^{-X_-/2}\le e^{1/S}\psi
\qquad(q\le\theta).
\tag{17}
$$

Choose a rational upper enclosure psi_+ of (16) using (7). Define

$$
\phi=\frac{\psi_+}{1-1/S},\qquad
A_0=\frac{\operatorname{sqrt\_upper}_S(1/\delta)}{1-1/S},
\tag{18}
$$

and refine until phi<1. The elementary series inequality
exp(x)<=1/(1-x) for 0<=x<1, together with (9), gives

$$
\mathbb E_q e^{-X_-/2}\le\phi,\qquad
e^{\ell/2}\le A_0.
\tag{19}
$$

For any integer M>=0, absence of a statistical crossing by M implies
S^-_M<ell. Exponential Markov inequality on the iid rounded increments
then gives

$$
\Pr_q\{T_{\rm stat}^->M\}
\le e^{\ell/2}\big(\mathbb E_qe^{-X_-/2}\big)^M
\le A_0\phi^M\qquad(q\le\theta).
\tag{20}
$$

The per-step and threshold inflation in (18) explicitly account for the
rounding in the implemented process. Using the ideal affinity bound
without those corrections would not establish its claimed cap.

## 7. Certifying the cap without enormous rational powers

Choose an integer M>=0 satisfying

$$
AJA_0\phi^M\le\eta.
\tag{21}
$$

Set R=AJA_0/eta>0. Use the rational logarithm procedure to obtain upper
bounds r_hi>=log R and f_hi>=log phi, refining until f_hi<0. The exact
rational check

$$
r_{\rm hi}+M f_{\rm hi}\le0
\tag{22}
$$

certifies (21). For example, take
M=max(0,ceil(r_hi/(-f_hi))) and verify (22) after selection. Requiring
M>=1 instead is also conservative. If R<=1, immediate fallback at M=0
is mathematically valid. Lower logarithm endpoints cannot replace the
upper endpoints in (22).

This method avoids materializing phi^M with a denominator whose bit
length grows linearly in a potentially large M. Exact rational arithmetic
still has finite implementation limits; crossing those limits is a design
rejection, not permission to relax (22).

## 8. Fallback, completeness, and the selected cost bound

Each budget receives at most M proposals. On its last permitted proposal,
check statistical passage and exact support completion before invoking
fallback. At the first unpassed cap, acquire every still-unseen label in
the prefix (3). If the resulting deterministic bounds certify all original
budgets, issue the global certificate. Otherwise census the remaining
positive union support and evaluate the entire original assertion exactly.
All cached labels are reused and every new fallback acquisition is counted.

On a margin-class table the prefix always succeeds by (4), so fallback
adds at most A labels. It can occur only if some corresponding uncapped
statistical crossing time exceeds M. Equations (20)-(21) and a union bound
for this cost event give

$$
\Pr\{\text{fallback}\}\le JA_0\phi^M\le\eta/A,
\qquad
\mathbb E T\le B_-+\eta.
\tag{23}
$$

The right probability bound may exceed one for a large eta; it remains
valid and the label bound still follows. This union bound is separate from
the intersection-union argument controlling false certificates.

The deterministic prefix alternative starts with the same prefix check,
then censuses if necessary. Its margin-class cost is at most A. Choose
this mode if A<=B_-+eta, using only the known design, and the likelihood
mode otherwise. The selected ideal auditor therefore satisfies

$$
\boxed{\quad
\sup_{\max_nR_n\le\tau-\epsilon}\mathbb E T
\le\min\{A,B_-+\eta\}.
\quad}
\tag{24}
$$

It has at most JM virtual proposals in likelihood mode, none in prefix
mode, and at most D distinct acquisitions on any table. Exact-support,
prefix, and census decisions preserve global validity. On every safe real
table all exact evaluations pass; finite caps followed by the finite
census ensure completion, including tables with risk exactly tau. This
does not depend on waiting for a tiny-weight item to appear by chance.

## 9. Conditional factor-17 corollary

Under the original rare-risk conditions

$$
0<\tau\le1/8,\qquad0<\epsilon\le\tau/16,\qquad
0<\delta\le1/4,
\tag{25}
$$

suppose successive budgets are at least doubled. Put

$$
H=\frac{\tau L}{\epsilon^2},\quad
e_r=\max_{n\in K}w_n(r),\quad
G=\sum_r\min(P,He_r),\quad F=\min(A,G).
\tag{26}
$$

Require a positive rigorous lower endpoint L_lo<=L and additionally
certify the exact rational guard

$$
c_-\le\frac{17}{8}\frac{\tau L_{\rm lo}}{\epsilon^2}.
\tag{27}
$$

The [v0.13 geometric-mixture lemma](cached-likelihood-audit.md#4-a-pointwise-geometric-mixture-inequality)
gives sum_n w_n(r)<=8e_r. Thus (27) implies B_-<=17G, and (24) yields

$$
\boxed{\quad\mathbb E T\le17F+\eta
\quad\text{uniformly on the margin class.}\quad}
\tag{28}
$$

The guard concerns the rounded walk's c_-, not only its ideal limit.
It must be checked before attaching this factor guarantee to a design.
Arbitrary grids and parameters outside (25) retain (24) when accepted,
but receive no factor-17 claim from this argument.

Mathematically, sufficiently fine enclosures satisfy the drift and affinity
requirements because
\(d_-\to\operatorname{kl}(\operatorname{Ber}(\theta),\operatorname{Ber}(\tau))>0\)
and \(\phi\to\psi<1\).
Within (25), the estimates in
[the original constant proof](cached-likelihood-audit.md#5-the-separated-grid-constant-and-deterministic-alternative)
give strict slack below (17/8)H for the ideal c. Hence sufficiently fine
enclosures also satisfy (27). A bounded program may nevertheless reject
before reaching sufficient precision; the ideal existence argument does
not remove its declared resource limits.

## 10. Executable rational contract and limits

The design interface is
`design(prompts, pool_size, budgets, tau, epsilon, delta, eta=Fraction(1))`.
The audit interface additionally takes a fixed-label callback
`oracle(prompt_index, rank_index)` and optional `randbelow` callback.
Prompt and rank indices passed to the oracle are zero based.

The reference implementation accepts strict integer dimensions and budgets,
and exact int/Fraction design parameters, excluding booleans and floats.
Budgets must be a nonempty bounded tuple or list with no duplicates; the
design canonicalizes them into increasing order. Its declared resource
domain is bounded by:

- pool size 1024, total items 100000, and rank-target pairs 250000;
- at most 64 bits for each design parameter's numerator and denominator;
- at most 2000000 total permitted virtual proposals in likelihood mode;
- exact oracle losses in [0,1] represented by int/Fraction, with
  denominator at most 1000000;
- dyadic scale exponents B=32,64,...,256, with logarithm intervals requested
  at B+16 bits; failure to meet the drift, affinity, or applicable factor
  guard within those eight attempts rejects the design;
- helper precision between 16 and 320 bits and rational helper arguments
  of at most 4096 bits; the logarithm series checks its power and partial
  sum against a 131072-bit rational limit. These design checks occur
  before any oracle call.

Accepted integer ticket sampling is exact. Budget n has denominator
binom(m,n), and cumulative rank masses are sums of the integer numerators
binom(m-r,n-1). The hockey-stick identity makes their total binom(m,n).
A uniform integer ticket selects rank r with probability w_n(r), and a
separate uniform prompt index yields (1). For loss b/d, a fresh uniform
integer in {0,...,d-1} is below b with probability b/d. The library calls
the oracle only on first acquisition, but performs this fresh coin draw
for every proposal, including repeats.

Statistical guarantees assume the `randbelow(k)` draws are independent and
uniform. Checking that a callback returns an integer in [0,k) cannot verify
that assumption; an adversarial callback can violate it. A seeded generator
is useful for reproducibility, not an empirical proof of validity. Likewise,
type and range validation cannot establish that an external oracle gives
fixed correct labels; those remain assumptions of the experiment.

The design factory rejects unsupported likelihood designs before acquiring
labels. In particular, if likelihood is the cheaper mode in (24) but its
cap exceeds the source limit, it must reject rather than silently use a
costlier prefix while reporting the smaller minimum. Prefix mode need not
execute virtual streams. Unsupported or malformed oracle output must not
produce a certificate.

For a fixed supported rational table and accepted design, the executable
arithmetic implements the ideal construction above, subject to the stated
randomness assumptions. This is code conformance on that domain. Rejecting
an otherwise safe real label outside it means that the executable library
alone does not meet all-real-table completeness in the original minimax
definition; only the ideal construction has that broader theorem.

Finally, a cap on virtual proposals does not bound oracle wall time,
random-number rejection bits, or every possible host resource use. This
reference does not implement the exploratory stopped-occupancy refinement,
claim an improved physical-label constant, provide selectable confidence
intervals, handle noisy or changing labels, or demonstrate real-model
savings. The numerical proof and source must be reviewed together before
their final evidence freeze.
