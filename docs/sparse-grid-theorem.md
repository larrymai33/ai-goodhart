# A cost bound for arbitrary declared budget grids containing 1

Candidate extension, 26 October 2026. The [earlier cost theorem](zero-cost-theorem.md) requires every power of four through the maximum declared budget. This note replaces that requirement by the single condition that budget 1 is declared. It proves a factor-320 expected-cost comparison for classical NEGEXP. The earlier factor 160 remains available on the grids covered by that theorem.

The method, geometric grouping, and lower-bound strategy have substantial prior art; attribution appears below. The proposed contribution is this finite rank-family scope extension and its boundary. Scientific priority and practical usefulness remain unestablished. The proof and associated checks were developed with substantial Codex assistance and separate agent reviews, not independent human review.

## 1. Experiment and statement

Fix P>=1 equally weighted prompt pools, each containing m>=1 items in a frozen total rank order. Rank 1 is best, and D=Pm is the number of distinct items. Querying an item reveals its fixed, correct loss in [0,1] at unit cost. There are no free labels or known cross-item relationships that reveal other losses. Computation is not charged. Let

$$
1\in\mathcal K\subseteq\{1,\ldots,m\},\qquad
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
a_n(p,r)=w_n(r)/P.
\tag{1}
$$

Impossible binomial choices are zero. The target risk is R_n(y)=sum_i a_n(i)y_i. Each target row is nonnegative and sums to one.

An admissible auditor may randomize, query adaptively, and abstain. Its only certificate asserts R_n(y)<=tau for **every budget in the originally declared family K**. For every fixed unsafe table with max_n R_n(y)>tau, the probability of ever issuing this certificate must be at most delta. On the all-zero table it must issue the certificate after finitely many queries almost surely. Define OPT_0 as the infimum of its expected number of distinct labels before that zero-table certificate, over all such auditors without computational restrictions. Empty-query certification lotteries are allowed.

These are the same conditions as [the earlier note, Section 1](zero-cost-theorem.md#1-experiment-decision-and-algorithm-class). The almost-sure zero-table requirement prevents vacuous zero-cost abstention. The objective is not expected cost on every safe table, worst-case cost, or the cost of certifying a selected subset of budgets.

Put

$$
L=\log(1/\delta),\qquad T=L/\tau,\qquad
s_i=\max_{n\in\mathcal K}a_n(i),\qquad
S(T)=\sum_i\min\{1,Ts_i\}.
\tag{2}
$$

Classical NEGEXP independently selects item i with probability 1-exp(-Ts_i), inspects the selected set, and certifies only when all selected labels are zero. Its expected zero-table cost is C_NEG=sum_i[1-exp(-Ts_i)].

Construct representatives greedily: start at n_0=1; after n_j, take the smallest declared budget at least 4n_j if one exists, and otherwise stop. Write n_0,...,n_J for the resulting sequence. Define

$$
I_j=\{\lfloor m/(4n_j)\rfloor+1,\ldots,\lfloor m/n_j\rfloor\},
\qquad D_j=P|I_j|,
\qquad A(T)=\sum_{j=0}^J\min\{D_j,T\}.
\tag{3}
$$

Each rank block includes all P prompts. These blocks are disjoint but need not cover the population. In particular, there is **no terminal block filled to rank 1** beyond the definition in (3).

**Theorem.** If 0<tau<=1/8 and 0<delta<=1/4, then

$$
\boxed{
\frac{A(T)}{40}\le\operatorname{OPT}_0
\le C_{\mathrm{NEG}}\le S(T)
\le8A(T)\le320\operatorname{OPT}_0.
}
\tag{4}
$$

The deterministic inequality S(T)<=8A(T) holds for every T>0. The threshold and confidence restrictions enter the lower bound on OPT_0. No missing budget is added to K: enlarging K changes the required decision and can increase its optimum, so padding the grid would not prove (4).

## 2. Two finite rank-law comparisons

**Representative comparison.** If 1<=a<=n<=m, then

$$
w_n(r)\le\frac na\,w_a(r)\quad\text{for every rank }r.
\tag{5}
$$

If w_a(r)=0, then w_n(r)=0 because the support ends at m-n+1. If w_n(r)=0 the inequality is immediate. Otherwise the positive-support product formula is

$$
w_n(r)=\frac nm\prod_{u=1}^{r-1}
\left(1-\frac{n-1}{m-u}\right).
$$

Every product factor decreases with n and is nonnegative on that support. Comparing it with a proves (5), including the empty product at r=1.

By greedy minimality the groups

$$
G_j=\{n\in\mathcal K:n_j\le n<4n_j\}
\tag{6}
$$

partition K. A gap before n_(j+1) contains no other declared budget at least 4n_j. Equation (5) therefore gives max_(n in G_j) a_n(i)<=4a_(n_j)(i).

**Tail comparison.** Fix a declared budget a and put h=floor(m/a). For each r>h, w_n(r) is nonincreasing over n>=a. Indeed, while w_n(r)>0 and n<m,

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{(n+1)(m-n+1-r)}{n(m-n)}.
\tag{7}
$$

The ratio is at most one exactly when (n+1)r>=m+1. Here ar>m, so that inequality holds for every n>=a. Once a weight becomes zero, all subsequent weights at that rank remain zero. If a=m, the tail weights are already zero. This handles all support endpoints without dividing by a zero weight.

## 3. Disjoint blocks and their witness mass

Since n_(j+1)>=4n_j, the last rank of I_(j+1) is at most floor(m/(4n_j)), strictly before the first rank of I_j. Thus the blocks in (3) are disjoint.

For any representative n, write x=m/n>=1 and h=floor(x). Its block size in ranks is

$$
t=h-\lfloor h/4\rfloor\ge3h/4,
\qquad t>x/2.
\tag{8}
$$

For the second inequality, h=1 gives t=1>x/2. For h>=2, 3h/4>=(h+1)/2>x/2. Consequently every block is nonempty and D_j>D/(2n_j). The uniform representative has the stronger size bound

$$
D_0=P(m-\lfloor m/4\rfloor)\ge3D/4.
\tag{9}
$$

The lower-mass proof of [the earlier Lemma 2, equations (16)-(19)](zero-cost-theorem.md#4-the-finite-fourfold-block-lemma) applies to this individual block for any integer n; it does not require n to be a power of four. For completeness, w_n is nonincreasing in rank and

$$
w_n(h)=\frac1x\prod_{u=1}^{h-1}
\left(1-\frac{n-1}{m-u}\right)
\ge\frac1x(1-1/x)^{h-1}.
\tag{10}
$$

The factor inequality uses nu<=nh<=m. At h=1 the product is empty, and t*w_n(h)=1/x>1/2. For h>=2 the logarithmic derivative of x^(-1)(1-1/x)^(h-1) on [h,h+1) is (h-x)/(x(x-1))<=0. Therefore

$$
t\,w_n(h)
\ge\frac{t h^{h-1}}{(h+1)^h}
\ge\frac34\left(\frac h{h+1}\right)^h
>\frac3{4e}>\frac14.
$$

Every item i in block j thus satisfies

$$
a_{n_j}(i)>\frac1{4D_j}.
\tag{11}
$$

We use the earlier lemma's local lower-mass argument, not its partition conclusion or its bound on the global envelope.

## 4. Lower cost for every adaptive auditor

Let Q_0 be an admissible auditor's queried set before its zero-table certificate. For any unsafe binary support B, coupling the zero and planted-positive tables with the same random seed gives

$$
\Pr_0(Q_0\cap B=\varnothing)\le\delta.
\tag{12}
$$

On the miss event, the two observed histories and their decisions are identical. This is the zero-path argument in [the earlier Lemma 1, equation (6)](zero-cost-theorem.md#2-the-all-zero-path-and-the-established-subset-lp). It allows arbitrary adaptivity and correlations among queried items. For a fractional unsafe table, its positive support is an unsafe binary support because all weights are nonnegative and losses are at most one.

We use the following finite miss lemma, exactly [the earlier Lemma 3, equations (22)-(30)](zero-cost-theorem.md#5-a-finite-hypergeometric-miss-bound). In a block of d>=1 items set b=floor(4*tau*d)+1. If an inspected subset with count X misses every fixed b-item subset with probability at most delta, then

$$
\mathbb E X\ge\frac1{40}\min\{d,T\}.
\tag{13}
$$

Here is its argument to make the constant explicit. The parameter restrictions give 1<=b<=d. Averaging the miss constraints yields E f(X)<=delta for

$$
f(z)=\frac{\binom{d-z}{b}}{\binom db},\quad z=0,\ldots,d.
$$

The piecewise-linear interpolation is convex: its second differences are binom(d-z-2,b-2)/binom(d,b)>=0 for b>=2, and b=1 is linear. With mu=E X, Jensen gives f(mu)<=delta. If d>=8, then b<=3d/4. At integers 0<=z<=d/8, each factor z/(d-u) in the miss product is at most 1/2, and log(1-v)>=-2v gives f(z)>=exp(-8bz/d).

If mu>=d/16 retain that bound. Otherwise both floor(mu) and ceil(mu) lie in [0,d/8]: for 8<=d<16 the ceiling is at most 1, and for d>=16 it is less than d/16+1<=d/8. Interpolation and convexity of the exponential yield mu>=dL/(8b). Thus mu>=min(d/16,dL/(8b)). Write u=tau*d. When u<=1, b<=5 and L>=log(4)>1 give mu>=d/40, with min(d,T)=d. When u>=1, b<=5u gives mu>=min(d,T)/40. For d<8, the event X=0 misses any fixed b-subset, so mu>=1-delta>=3/4>d/40. This proves (13).

In block j let b_j=floor(4*tau*D_j)+1. By (11), every b_j-item subset has witness risk greater than b_j/(4D_j)>tau. Equations (12)-(13) therefore apply to X_j=|Q_0 intersect block j|. Since the blocks are disjoint, but possibly noncovering,

$$
\mathbb E_0|Q_0|\ \ge\ \sum_j\mathbb E X_j
\ \ge\ \frac1{40}\sum_j\min\{D_j,T\}
=\frac{A(T)}{40}.
\tag{14}
$$

The first relation is an inequality, not a partition identity. Taking the infimum proves the lower bound in (4).

## 5. Charging the envelope cost to the blocks

We now prove S(T)<=8A(T) for every T>0.

If T>=D, then S(T)<=D. Equation (9) gives A(T)>=D_0>=3D/4, so S(T)<=4A(T)/3.

Suppose instead that T<D. Call a group low when its representative satisfies n_j<=D/T, and let ell be the number of such groups. The uniform representative is low, so ell>=1. For each low group, (5)-(6) and normalization give

$$
\sum_i\min\{1,T\max_{n\in G_j}a_n(i)\}
\le\sum_i4T a_{n_j}(i)=4T.
\tag{15}
$$

If there are high groups, let n_* be their smallest representative and let H be the union of their **original declared budgets**. Every n in H is at least n_*, and n_* itself belongs to H. Set h=floor(m/n_*). The top h ranks across all prompts have Ph<=D/n_*<T items. Their contribution to the high-family capped envelope is at most Ph<T. On ranks r>h, the tail comparison shows that the high-family maximum equals a_(n_*). Hence its remaining contribution is at most T times that row's tail mass, and therefore at most T. In total,

$$
\sum_i\min\{1,T\max_{n\in H}a_n(i)\}<2T.
\tag{16}
$$

There is no factor four in (16): it uses monotonicity for the original high budgets directly. If no high group exists, this contribution is zero. A capped maximum is bounded by the sum of the capped group maxima. Combining (15)-(16) gives

$$
S(T)\le(4\ell+2)T.
\tag{17}
$$

For every low representative, (8) gives D_j>D/(2n_j)>=T/2. Its contribution to A(T) is therefore at least T/2. The uniform block contributes at least 3T/4 by (9) and T<D. Consequently

$$
A(T)\ge\left[\frac{\ell-1}{2}+\frac34\right]T
=\left(\frac\ell2+\frac14\right)T,
\qquad S(T)\le8A(T).
\tag{18}
$$

This includes the singleton grid K={1}, grids with arbitrarily large gaps, and the absence of a high group. The constants are not optimized further.

## 6. Validity and the rational workflow

For any fixed unsafe fractional table let B={i:y_i>0}. Some declared target has a_n(B)>tau, so sum_(i in B) s_i>tau. Independent NEGEXP inclusion gives

$$
\Pr(Q\cap B=\varnothing)=\exp\left(-T\sum_{i\in B}s_i\right)<\delta.
\tag{19}
$$

All selected labels are zero exactly on this miss event. On the zero table the procedure certifies after at most D distinct queries. It is therefore admissible, and OPT_0<=C_NEG. Since 1-exp(-u)<=min(1,u), its cost is at most S(T). Equations (14) and (18) complete (4). No union bound over budgets is needed for this one whole-family decision.

The [rational workflow's numerical argument](zero-workflow-numerics.md) constructs independent inclusion probabilities satisfying

$$
1-e^{-Ts_i}\le q_i\le\min\{1,Ts_i\}.
\tag{20}
$$

The lower side preserves (19), and the upper side gives its exact expected zero-table cost C_rat=sum_i q_i<=S(T)<=320*OPT_0. The numerical construction needs budget 1, but not intermediate powers of four: its refinement proof uses s_i>=1/D. Thus the same probability construction transfers to the enlarged domain. On previously supported grids the original proof still supplies factor 160; this note does not replace that stronger bound.

## 7. A boundary when budget 1 is absent

The inclusion of budget 1 is a sufficient condition for the confidence-uniform bound above. The following family shows that it cannot simply be removed from every grid; it does not assert that every grid without 1 is problematic.

For an integer j>=1 take one pool, m=10j, the singleton grid K={9j}, and tau=1/8. Put

$$
C_j=\binom{10j}{j},\qquad \delta_j=4^{-C_j}.
\tag{21}
$$

The best rank has mass w_(9j)(1)=9/10, while every other rank together has mass 1/10<tau. Thus a binary failure set is unsafe exactly when it contains rank 1. For fractional labels, unsafe risk implies y_1>0; the converse need not hold.

For every admissible auditor, the unsafe binary alternative supported only on rank 1 and the zero-path coupling give Pr_0(1 in Q_0)>=1-delta_j. Hence OPT_0>=1-delta_j. Equality is attained by querying rank 1 with probability 1-delta_j, choosing the empty set otherwise, and certifying exactly when all queried labels are zero. Any unsafe fractional table has positive loss at rank 1, so the only false certificate occurs on the empty-set branch. Therefore

$$
\operatorname{OPT}_0=1-\delta_j.
\tag{22}
$$

The target has j+1 positive ranks. Each has weight at least 1/C_j, because the weight numerators are positive integers and binom(10j,9j)=C_j. Since T=8C_j log(4), NEGEXP includes each supported rank with probability at least 1-4^(-8). Thus

$$
\frac{C_{\mathrm{NEG}}}{\operatorname{OPT}_0}
\ge\frac{(j+1)(1-4^{-8})}{1-\delta_j}
\longrightarrow\infty.
\tag{23}
$$

The threshold stays fixed while confidence varies with j. This is not a separation at fixed delta, and it makes no claim about every missing-baseline family. For large j, delta_j should be represented symbolically; constructing its expanded denominator would be an unnecessary exponential allocation. The rational upper-inclusion design also has cost at least C_NEG, so the same boundary applies to it if extended without the baseline condition.

## 8. Attribution, evidence, and limits

[Aslam, Popa, and Rivest (2008), Sections 8, 12, and 13.2](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/), establish NEGEXP, its miss-probability calculation, optimal randomized subset auditing, and multi-target reuse. The zero-path and hypergeometric lemmas used here are restated from the earlier note; they are not newly claimed general auditing principles. [Anthony and Salehzadeh Nobari (2026), Theorem 13](https://arxiv.org/html/2607.21480v1), is close finite-corpus prior art for coupling adaptive zero-label histories with planted-positive alternatives and requiring power on the zero table.

[Fitas (2026, v2), Supplement S5](https://arxiv.org/html/2608.21496v2), already constructs multiplicatively spaced integer budgets and controls targets between representatives; S7.2 uses geometrically separated score bands for adaptive label-cost lower bounds. [Sarkar and Baichoo (2026), Appendix C.1](https://arxiv.org/html/2609.40190v1), groups budgets into geometric levels and charges representative costs to disjoint index blocks; C.3 derives label lower bounds from disjoint score bands. Geometric packing and charging are established ingredients. The particular lower-bound experiments in those sections differ from fixed distinct labels and this zero-table expected-cost comparator; that distinction does not establish priority or imply that those papers omit stored pools or reuse.

The candidate extension is the finite arbitrary-grid comparison (14)-(18), with the originally declared decision and the boundary (21)-(23). The constants are coarse. This is not a new sequential testing rule, an optimal-stopping theorem, a guarantee of low cost after positive labels, real-model evidence, or a population safety guarantee.

The [internal protocol](../experiments/sparse_grid_protocol.json) fixes a saved exact-check run after exploratory proof checks. It is not an external preregistration or an empirical holdout. Finite checks can detect implementation and algebra errors; they do not prove the unbounded theorem or establish scientific novelty. All earlier source-pinned proofs and measurements remain separate.
