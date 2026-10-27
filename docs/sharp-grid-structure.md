# Sharp audit cost: arbitrary budget grids and a structural boundary

Candidate result, 26 October 2026. The [earlier sharp-cost note](sharp-cost-theorem.md) proves a ratio-one expected-cost comparison for full-prefix best-of-n budgets. This note removes the grid restriction in that asymptotic regime: every nonempty declared budget family is covered, including a family without budget 1. It also gives decreasing, normalized target rows for which the same small-atom regime does not make NEGEXP near-optimal. Common monotonicity alone does not explain the rank-family result.

The proposed contribution is this uniform cost comparison and its structural boundary, not a new inspection algorithm. NEGEXP, subset-auditing optimization, geometric grouping, and local miss-probability lower bounds are established ingredients. Scientific priority remains unresolved, including a close older stratified-inspection literature discussed in Section 9. This proof was developed with substantial Codex assistance and separate agent reviews; it has not received independent human review. See the [contribution disclosure](provenance.md).

## 1. Fixed experiment, comparator, and statement

Fix integers P>=1 and m>=1, and a nonempty declared family K contained in {1,...,m}. Write N=max K and D=Pm. There are P equally weighted prompt pools, each containing m distinct items in a fixed total rank order. Rank 1 is best. Querying an item reveals its fixed, correct loss y[p,r] in [0,1] at unit cost. There are no free supplied labels or known cross-item relationships that reveal other labels without queries. Computation is not charged.

Define the without-replacement winner weights and risks by

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
a_n(p,r)=\frac{w_n(r)}P,\qquad
R_n(y)=\sum_{p,r}a_n(p,r)y[p,r],\qquad n\in\mathcal K.
\tag{1}
$$

Impossible binomial choices are zero. Each target row is nonnegative and sums to one. The experiment conditions on the fixed pools, ranks, and losses; no independence of prompts or labels is assumed.

Fix 0<tau<1 and 0<delta<=1/4. An admissible auditor may randomize, select unseen items adaptively, and abstain. Its certificate asserts R_n(y)<=tau for every budget in the **originally declared** family. For every fixed table with max_n R_n(y)>tau, its probability of ever issuing that certificate must be at most delta. On the all-zero table it must issue the certificate after finitely many queries almost surely. Let OPT_0 be the infimum, over all these auditors without computational restrictions, of the expected number of distinct items queried before their first zero-table certificate. Empty-query certification lotteries are allowed. A full census followed by exact evaluation is admissible, so the comparator is nonempty.

Put

$$
\begin{aligned}
e(r)&=\max_{n\in\mathcal K}w_n(r),&
s_{p,r}&=e(r)/P,& Z&=\sum_{r=1}^m e(r),\\
L&=\log(1/\delta),& T&=L/\tau,&
a&=\frac{N}{Pm\tau},\qquad \rho=La.
\end{aligned}
\tag{2}
$$

The maximum individual target mass is M=N/(Pm), so rho=LM/tau. Classical NEGEXP independently selects item i with probability 1-exp(-Ts_i), inspects the selected set, and certifies exactly when all inspected losses are zero. Its expected zero-table cost is C_NEG=sum_i(1-exp(-Ts_i)).

**Theorem.** Along any sequence with nonempty K contained in {1,...,m}, 0<delta<=1/4, and

$$
\tau\longrightarrow0,\qquad
\rho=\frac{\log(1/\delta)N}{Pm\tau}\longrightarrow0,
\tag{3}
$$

one has

$$
\boxed{\quad
\operatorname{OPT}_0\sim C_{\mathrm{NEG}}\sim\frac L\tau Z.
\quad}
\tag{4}
$$

Convergence is uniform in P, m, K, and delta subject to these conditions. The family may change at every step. Budget 1 is not required, no missing budget is added, and there is no assumption that the grid fills gaps geometrically. The result concerns one whole-family decision and expected cost on the zero table, not partial certificates, a confidence band, nonzero-instance efficiency, or the published betting engine.

For arbitrary grids, Z must remain in (4). There is no general log(N)/e replacement: for a singleton family K={N}, Z=1 regardless of N. The full-prefix normalizer asymptotic remains applicable only when its own hypotheses hold.

## 2. Generic audit lower bound and upper bound

For any set B whose binary table is unsafe, coupling an auditor's zero-table run with its run on 1_B gives

$$
\Pr_0(Q_0\cap B=\varnothing)\le\delta.
\tag{5}
$$

On seeds where Q_0 misses B, the two runs see the same labels, make the same adaptive choices, and issue the same certificate. Almost-sure zero-table certification ensures that Q_0 has a probability law. This is the established zero-path subset-auditing argument; see [the earlier characterization](zero-cost-theorem.md#2-the-all-zero-path-and-the-established-subset-lp).

We use [the finite hypergeometric lemma](sharp-cost-theorem.md#3-a-finite-hypergeometric-lower-bound): if every b-subset of a d-item block is unsafe, with 1<=b<=d, then its expected zero-path query count mu satisfies

$$
\mu\ge\frac{L(d-b)}{b+L}.
\tag{6}
$$

To recall its mechanism, average (5) over a uniformly chosen b-subset. The resulting miss function is f(x)=binom(d-x,b)/binom(d,b). Its piecewise-linear extension is convex, so delta>=E f(X)>=f(E X). If mu<d-b, the two integer endpoints surrounding mu satisfy log f(x)>=-bx/(d-b-mu). Convex interpolation of the exponential lower bound gives delta>=exp(-b mu/(d-b-mu)), which rearranges to (6). If mu>=d-b the bound is immediate. This handles noninteger mu and b=d without a continuous-binomial approximation.

Conversely, any unsafe fractional table has positive support B satisfying a_n(B)>tau for some declared n. Hence sum_(i in B) s_i>tau, and NEGEXP misses B with probability exp(-T sum_(i in B) s_i)<delta. It certifies the zero table after at most D distinct queries. Therefore

$$
\operatorname{OPT}_0\le C_{\mathrm{NEG}}\le TZ.
\tag{7}
$$

No independence is imposed on the zero-path queried set in (5)-(6). Independence is part of the NEGEXP construction in (7).

## 3. A bounded collection of representative budgets

Choose representatives greedily: n_1=min K; after n_j, choose the smallest declared budget at least 4n_j, if one exists. Stop when none exists. Let R be the number of representatives. Every declared budget belongs to a group with representative n_j and lies in [n_j,4n_j). This follows from the greedy minimality of the next representative, including across arbitrarily large gaps.

For a<=n, the rank laws satisfy

$$
w_n(r)\le\frac na w_a(r).
\tag{8}
$$

If w_n(r)=0, this is immediate. If w_a(r)=0, then w_n(r)=0 as well, because positive support ends at m-n+1. On positive support use

$$
w_n(r)=\frac nm\prod_{u=1}^{r-1}
\left(1-\frac{n-1}{m-u}\right).
$$

The factors are nonnegative and decrease as n increases, proving (8), including r=1 by the empty-product convention. Thus every target in group j is bounded coordinatewise by 4w_(n_j).

There are at most 4Z representatives. For completeness, consider the disjoint rank blocks

$$
I_j=\{\lfloor m/(4n_j)\rfloor+1,\ldots,\lfloor m/n_j\rfloor\}.
\tag{9}
$$

They need not partition the ranks. Disjointness follows from n_(j+1)>=4n_j, so the next block's upper endpoint is at most the preceding block's excluded lower endpoint.

Each block has mass greater than 1/4 under its own representative. Here is a direct endpoint check. Write n=n_j, h=floor(m/n)>=1, and ell=floor(m/(4n))=floor(h/4). For the winning rank W_n, a union bound gives Pr(W_n<=ell)<=n ell/m<=1/4. Also

$$
\Pr(W_n>h)=\frac{\binom{m-h}{n}}{\binom mn}
\le(1-h/m)^n\le e^{-nh/m},\qquad
nh/m>h/(h+1).
\tag{10}
$$

When m-h<n, the binomial ratio is zero; otherwise the product formula proves the first inequality. If h<=3, then ell=0 and the block has mass greater than 1-exp(-1/2)>1/4. If h>=4, its mass is greater than 1-1/4-exp(-4/5)>1/4. These elementary exponential inequalities also cover n=m and m=1. Thus

$$
\frac R4<\sum_{j=1}^R\sum_{r\in I_j}w_{n_j}(r)
\le\sum_{r=1}^m e(r)=Z,
\qquad R\le4Z.
\tag{11}
$$

This supplies a representative count relative to envelope mass, independently of the grid's largest gap. It does not use budget 1.

## 4. Exact tail control and useful envelope values

For every budget n and rank 1<=r<=m,

$$
\sum_{u=r}^m w_n(u)
=\frac{\binom{m-r+1}{n}}{\binom mn}
=\frac{m-r+1}{n}w_n(r)
\le\frac mn w_n(r).
\tag{12}
$$

The identity follows by summing binomial coefficients, or by the event that all n sampled ranks are at least r. It also holds where the weights vanish. Therefore, for 0<epsilon<1,

$$
\sum_{r:w_n(r)<\epsilon n/m}w_n(r)\le\epsilon.
\tag{13}
$$

Indeed, the strict low-height set is a terminal interval because w_n decreases. If it is empty there is nothing to prove; otherwise apply (12) at its first rank. Zero weights cause no difficulty. This exact argument covers n/m near one and does not approximate the rank law by an exponential distribution.

For representative j put h_j=n_j/m and call a rank good if its envelope value belongs to the union

$$
\bigcup_{j=1}^R[\epsilon h_j,4h_j].
\tag{14}
$$

All other ranks are bad. Fix any maximizer n of e(r) at a bad rank with e(r)>0, and let n_j represent its group. Equation (8) gives e(r)=w_n(r)<=4w_(n_j)(r)<=4h_j. Since the rank is outside (14), e(r)<epsilon*h_j. The representative is itself declared, so w_(n_j)(r)<=e(r)<epsilon*h_j. Assign this rank to the chosen winning group. Summing over that assignment and then using (13) gives

$$
\sum_{r\text{ bad}}e(r)
\le4\sum_{j=1}^R
\sum_{r:w_{n_j}(r)<\epsilon h_j}w_{n_j}(r)
\le4R\epsilon\le16\epsilon Z.
\tag{15}
$$

Zero-envelope ranks contribute nothing. The argument charges each bad rank through a group containing one actual envelope maximizer; it does not assume that one representative globally maximizes the envelope.

## 5. Binning and the finite cost bound

The positive envelope occupies ranks 1 through m-min(K)+1. Omit the zero ranks. Fix eta>0 and partition the positive ranks into maximal consecutive bins [u,v] satisfying e(u)/e(v)<=1+eta. The next bin starts at v+1. Whenever another bin exists, maximality implies that its start value is less than the preceding start value divided by 1+eta. This remains true across ties, large jumps, and singleton bins.

For a bin ending at v, choose any declared budget attaining e(v). Its row is nonincreasing, so it witnesses every rank in the bin at mass at least e(v). Include all P prompts at these ranks, and define

$$
d=P(v-u+1),\qquad \nu=e(v)/P,\qquad q=d\nu=(v-u+1)e(v).
\tag{16}
$$

The bin ratio gives sum_bins q>=Z/(1+eta). Although the maximizer may change inside a bin, the endpoint's single witness is sufficient for a lower bound.

Let

$$
B(\epsilon,\eta)
=1+\frac{\log(4(1+\eta)/\epsilon)}{\log(1+\eta)}.
\tag{17}
$$

At most R*B(epsilon,eta) bins intersect good ranks. To see this, suppose a bin contains a good rank r whose value lies in the jth interval of (14). Its start value satisfies

$$
\epsilon h_j\le e(r)\le e(u)
\le(1+\eta)e(v)\le(1+\eta)e(r)
\le4(1+\eta)h_j.
$$

Start values decrease by a factor greater than 1+eta, so an interval with this ratio contains at most B(epsilon,eta) starts. Sum this count over the R representative intervals; overlaps only make that upper bound looser. Thus the number of bins intersecting any good rank is at most 4Z*B(epsilon,eta).

Choose kappa>1+a and retain only bins with q>=kappa*tau. There are two ways a discarded bin can lose minimum mass. If it intersects good ranks, its q is less than kappa*tau and is charged to the preceding bin count. If it contains only bad ranks, its q is at most its actual envelope mass and is charged to (15). Consequently

$$
\sum_{\text{retained bins}}q
\ge Z\left[\frac1{1+\eta}-16\epsilon
-4\kappa\tau B(\epsilon,\eta)\right]_+.
\tag{18}
$$

The positive part x_+=max(x,0) includes the case where no bin is retained. The second charge uses q<=sum_bin e(r), not the reverse inequality.

In a retained bin choose

$$
b=\lfloor\tau/\nu\rfloor+1.
\tag{19}
$$

Every b-subset is strictly unsafe under the endpoint witness. Since nu<=M=N/(Pm) and q=d*nu>=kappa*tau,

$$
b\le\frac\tau\nu(1+a),\qquad
\frac bd\le\frac{1+a}{\kappa}<1,\qquad
\frac db\ge\frac q{\tau(1+a)},\qquad
\frac Lb\le\rho.
\tag{20}
$$

Thus 1<=b<d, and the finite lemma gives a contribution of at least

$$
\frac{L(d-b)}{b+L}
\ge\frac{Lq}{\tau}
\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
\tag{21}
$$

The prompt-rank blocks are disjoint, so their expected query counts add, regardless of dependence between the queries. Combining (18)-(21) proves the finite inequality

$$
\boxed{\quad
\frac{\operatorname{OPT}_0}{LZ/\tau}
\ge
\left[\frac1{1+\eta}-16\epsilon
-4\kappa\tau B(\epsilon,\eta)\right]_+
\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
\quad}
\tag{22}
$$

It holds for any 0<epsilon<1, eta>0, and kappa>1+a. A nonpositive bracket supplies only the trivial lower bound zero. No assumption is made that this coarse finite bound is useful at a moderate threshold.

## 6. Uniform sharpness and its interpretation

For 0<tau<1 choose

$$
\epsilon=\eta=\tau^{1/3},\qquad \kappa=1/\eta.
\tag{23}
$$

Then kappa*tau=eta^2, and

$$
\kappa\tau B(\eta,\eta)
=\eta^2\left[1+\frac{\log(4(1+\eta)/\eta)}{\log(1+\eta)}\right]
\longrightarrow0.
\tag{24}
$$

For example, log(1+eta)>=eta/2 when eta<=1, so the second term is at most 2eta log(4(1+eta)/eta). The other losses in the bracket of (22) also vanish. Since L>=log(4), one has a=rho/L<=rho/log(4)->0. Therefore kappa>1+a eventually, and the last factor of (22) tends to one. All error bounds depend only on tau and rho. Together with (7), this proves (4) uniformly, without any dependence on the number of budgets or their gaps.

The proof exhibits sufficient structural ingredients beyond monotonicity. More generally, consider normalized nonnegative rows on a common decreasing coordinate order. Suppose a representative subfamily has count at most C_1 times the envelope normalizer; every row is coordinatewise bounded by C_2 times some representative; and every representative assigns at most g(epsilon) mass to coordinates below epsilon times its initial height, with g(epsilon)->0 uniformly. If C_1 and C_2 are fixed, the same argument applies: bad mass is at most C_1*C_2*g(epsilon) times the envelope mass, and each representative contributes only a logarithmic interval of good envelope values. The choice (23), together with the maximum-item condition LM/tau->0, again makes the losses vanish.

These are sufficient conditions, not an if-and-only-if characterization or claimed necessary assumptions. For the rank family, the proof supplies C_1=C_2=4 and g(epsilon)=epsilon. The next construction shows that normalization and a shared decreasing order alone are insufficient.

## 7. Decreasing target rows can have an unbounded NEGEXP ratio

Fix an integer k>=2 and let

$$
\tau=1/k,\quad \beta=1/k^2,\quad H=J=k^3,
\quad t_j=H2^j\ (j=0,\ldots,J),\quad D=H+t_J.
\tag{25}
$$

There is one ordered universe of D items. Its first H items form a shared head. For each j define a row with weight (1-beta)/H on every head item, weight beta/t_j on the next t_j items, and weight zero elsewhere. Add the uniform row of weight 1/D on every item.

All rows are normalized and nonincreasing: t_j>=H and beta<=1/4 ensure the head weight is at least the tail weight. Their largest individual mass M is at most 1/H. Fix delta=1/4 and L=log(4). Then the corresponding small-atom parameter satisfies

$$
\rho=LM/\tau\le L/k^2\longrightarrow0,
\qquad \tau\longrightarrow0.
\tag{26}
$$

Nevertheless the envelope normalizer diverges. The head contributes at least 1-beta, the first H tail items contribute at least beta, and each of the J further dyadic shells contributes at least beta/2. These are disjoint coordinates, and adding the uniform row cannot decrease the envelope. Hence

$$
Z\ge1+J\beta/2=1+k/2.
\tag{27}
$$

The whole family can be audited much more cheaply. Let the mean head loss have threshold

$$
\gamma=\frac{\tau-\beta}{1-\beta}=\frac1{k+1}.
\tag{28}
$$

If the head mean is at most gamma, every nonuniform row has risk at most (1-beta)gamma+beta=tau, whatever the other losses are. Audit the uniform head distribution at threshold gamma and the uniform population distribution at threshold tau, each using NEGEXP with error level delta. Query their union, counting repeated selections once, and certify only when every queried loss is zero.

This procedure is valid for every fixed table in [0,1]^D. Any unsafe member of the original family implies that the head mean exceeds gamma or that the population mean exceeds tau. For that fixed unsafe table, certification requires the audit of at least one such unsafe distribution to miss its positive support, an event of probability at most delta. There is no need to divide delta between the two audits: the issued decision requires both to pass. On the zero table, the procedure certifies almost surely. Its expected cost is at most

$$
H\left(1-e^{-L/(H\gamma)}\right)
+D\left(1-e^{-L/(D\tau)}\right)
\le\frac L\gamma+\frac L\tau=L(2k+1).
\tag{29}
$$

Thus OPT_0<=L(2k+1); no exact value of OPT_0 is claimed. In contrast, 1-exp(-x)>=x-x^2/2 and max_i Ts_i=rho imply

$$
C_{\mathrm{NEG}}\ge(1-\rho/2)\frac L\tau Z.
$$

Using (26)-(29),

$$
\boxed{\quad
\frac{C_{\mathrm{NEG}}}{\operatorname{OPT}_0}
\ge
\left(1-\frac{L}{2k^2}\right)
\frac{k(1+k/2)}{2k+1}
\longrightarrow\infty.
\quad}
\tag{30}
$$

The displayed lower bound grows asymptotically like k/4. There are J+2=k^3+2 target rows. The population sizes in (25) are symbolic; no such label table needs to be allocated to establish the result. The reference to a head is known target geometry, not free gold labels: all actual losses remain unknown and must be queried.

Each row's total tail mass is smaller than the safety threshold. A suitable head test can therefore control all those rows, while their tails accumulate substantial envelope mass across many scales. This shows why a generic monotone-row theorem based only on tau->0 and LM/tau->0 would be false. The rows in this counterexample are not best-of-n rank laws.

## 8. Scope relative to earlier results and software

The [factor-320 arbitrary-grid theorem](sparse-grid-theorem.md) requires budget 1 and permits fixed tau<=1/8 uniformly over 0<delta<=1/4. Its missing-baseline counterexample fixes tau=1/8 and sends confidence to an extreme value on K={9j}, m=10j, P=1. In that construction rho=(36/5)log(1/delta) diverges. It lies outside (3), so it does not contradict the new theorem. The present result removes the grid condition only in the joint small-threshold, small-atom regime; it does not establish a new confidence-uniform finite factor for arbitrary grids at fixed tau.

The earlier proofs, saved arithmetic checks, and their source pins remain unchanged. In particular, this note does not retroactively enlarge the hypotheses recorded by the full-prefix checker. It also does not replace the full-prefix normalizer by log(N)/e on a sparse grid.

Any independent probability design satisfying 1-exp(-Ts_i)<=q_i<=min(1,Ts_i) inherits the formal ratio-one conclusion by the same upper-bound squeeze. That statement is mathematical. The existing CLI retains its input conditions, including its baseline requirement, and its resource caps. No sampling implementation for new grids or enormous symbolic populations is asserted here. The result gives no guarantee of practical savings at the earlier tau=.1 study threshold.

## 9. Prior art and remaining scientific uncertainty

[Aslam, Popa, and Rivest (2008), Sections 8, 12, and 13.2](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/), establish NEGEXP, randomized-subset auditing, and multi-target reuse. The adaptive zero-path constraint and local hypergeometric averaging are not newly claimed auditing principles. [Fitas (2026, v2), Supplements S5 and S7.2](https://arxiv.org/html/2608.21496v2), and [Sarkar and Baichoo (2026), Appendix C](https://arxiv.org/html/2609.40190v1), supply close geometric-grouping and disjoint-band lower-bound precedents. Their particular lower-bound experiments differ from this unrestricted expected-distinct-label objective on a fixed zero table; that difference does not establish priority or imply that those papers omit stored pools or caching.

A close unresolved antecedent is the stratified-inspection literature. [Avenhaus and Canty, “Formal Models for NPT Safeguards” (2007), printed page 71](https://resources.inmm.org/system/files/jnmm/vol_35/V-35_4.pdf), describes a data-verification allocation that controls nondetection when falsification is concentrated in any one stratum and when it is distributed across strata, and discusses optimality under prior announcement. It points to their 1989 “Re-examination of the IAEA Formula for Stratified Attribute Sampling” and the 1996 book *Compliance Quantified*. The original 1989 argument and book proof have not been obtained. The available review does not settle whether that optimality comparator includes arbitrary random sample sizes, correlations between strata, or expected-cost certification lotteries. This is a substantive unresolved priority comparison, not grounds for assuming those earlier results concern only a weaker with-replacement design. See the separate [inspection-priority review](inspection-priority-review.md) for the inspected sources and outstanding comparison.

The candidate contribution is the finite uniform comparison (22), its sharp consequence for every declared BoN grid, and the explicit boundary (30) separating this mechanism from monotonicity alone. The representative and tail argument also exposes sufficient structural conditions; it is not a complete characterization of all target families. A proof or an exact computational check cannot establish novelty, real-model usefulness, independent human understanding, or field impact. Those remain separate evidence requirements.
