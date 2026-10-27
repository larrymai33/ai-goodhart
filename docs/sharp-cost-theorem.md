# Sharp zero-table label cost in the dense-pool limit

Candidate result, 26 October 2026. For the full-prefix best-of-n family, this note gives a finite lower bound on the expected distinct-label cost of every admissible adaptive auditor. It implies that classical negative-exponential inspection has asymptotically optimal cost when the safety threshold tends to zero and each item's maximum target mass is small relative to the threshold and confidence scale. The parameters, including the size of the target family, may vary jointly.

This is a proposed sharp comparison with the unrestricted audit optimum, not a new sampling algorithm. NEGEXP, randomized-subset auditing, hypergeometric miss probabilities, and geometric discretization have substantial prior art. A bounded primary-source search found no directly matching uniform theorem; scientific priority remains unestablished. The proof was developed with substantial Codex assistance and reviews in separate agent contexts. It has not received independent human review. See the [contribution disclosure](provenance.md).

## 1. Fixed experiment and objective

Fix integers P>=1 and m>=N>=1. There are D=Pm distinct items, indexed by a prompt p and a frozen rank r. Rank 1 is best. Querying an item reveals its fixed, correct loss y[p,r] in [0,1] at unit cost. There are no initially supplied labels or known cross-item relationships that reveal additional losses for free. Computation is not charged. Each prompt has equal weight.

The declared budgets are the **full prefix** K={1,...,N}. Put

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
a_n(p,r)=\frac{w_n(r)}P,\qquad
R_n(y)=\sum_{p,r}a_n(p,r)y[p,r].
\tag{1}
$$

Impossible binomial choices are zero. Every target row is nonnegative and sums to one. All probabilities below concern audit randomness, conditional on these fixed pools, ranks, and losses. No independence of prompts or labels is assumed.

An admissible auditor may randomize, choose previously unseen items adaptively, and abstain. Its certificate asserts R_n(y)<=tau for **every** declared budget. For every fixed table with max_n R_n(y)>tau, the probability it ever issues that certificate must be at most delta. On the all-zero table it must certify after finitely many queries almost surely. Let

$$
\operatorname{OPT}_0=\inf_{\mathcal A}\mathbb E_0|Q_0|,
\tag{2}
$$

where Q_0 is the set queried before the first zero-table certificate. The infimum includes all such auditors without computational restrictions. Empty-query certification lotteries are allowed. The almost-sure certification requirement excludes the vacuous procedure that always abstains. This is the same comparator as [the earlier cost theorem, Sections 1-2](zero-cost-theorem.md#1-experiment-decision-and-algorithm-class).

Write

$$
\begin{aligned}
e(r)&=\max_{1\le n\le N}w_n(r),&
s_{p,r}&=e(r)/P,&
Z&=Z_{m,N}=\sum_{r=1}^m e(r),\\
L&=\log(1/\delta),& T&=L/\tau,&
a&=\frac{N}{Pm\tau},\qquad \rho=La.
\end{aligned}
\tag{3}
$$

NEGEXP includes each item i independently with probability 1-exp(-Ts_i), queries the selected set, and certifies exactly when all selected losses are zero. Its expected zero-table cost is

$$
C_{\mathrm{NEG}}=\sum_i(1-e^{-Ts_i}).
\tag{4}
$$

For any unsafe fractional table, its positive support B satisfies a_n(B)>tau for some n. Therefore sum_(i in B) s_i>tau, and the chance that NEGEXP misses B is exp(-T sum_(i in B) s_i)<delta. It certifies the zero table after at most D queries. Thus

$$
\operatorname{OPT}_0\le C_{\mathrm{NEG}}\le TZ.
\tag{5}
$$

No multiplicity penalty is needed for this one whole-family decision. This argument does not authorize partial certificates when the whole family fails.

## 2. Statement

**Theorem.** Consider any sequence of the experiments above with 0<tau<1 and 0<delta<=1/4. If

$$
\tau\longrightarrow0,\qquad
\rho=\frac{\log(1/\delta)N}{Pm\tau}\longrightarrow0,
\tag{6}
$$

then

$$
\boxed{\quad
\operatorname{OPT}_0\sim C_{\mathrm{NEG}}
\sim\frac{\log(1/\delta)}{\tau}Z_{m,N}.
\quad}
\tag{7}
$$

The conclusion is uniform in the other parameters: P, m, N, and delta may all vary, subject to the displayed conditions and 1<=N<=m. It does not require N/m to tend to zero, because increasing P can make the individual-item masses small. If N also tends to infinity, then

$$
\operatorname{OPT}_0\sim C_{\mathrm{NEG}}
\sim\frac{\log(1/\delta)\log N}{e\tau}.
\tag{8}
$$

The logarithmic coefficient in (8) comes from the established continuous envelope normalizer and its [uniform finite-pool comparison](sharp-envelope.md), not from a new normalizer calculation here. For bounded N, retain Z_(m,N) in (7).

The proof below supplies a finite inequality. The theorem concerns expected cost at the all-zero table, not the published betting engine, low cost on nonzero tables, population generalization, or an optimal stopping rule. The full-prefix assumption is not replaced here by the arbitrary-grid condition in [the factor-320 theorem](sparse-grid-theorem.md).

## 3. A finite hypergeometric lower bound

Call a set B unsafe if max_n a_n(B)>tau. The zero-path coupling in [the earlier theorem, Lemma 1](zero-cost-theorem.md#2-the-all-zero-path-and-the-established-subset-lp) implies, for every admissible auditor,

$$
\Pr_0(Q_0\cap B=\varnothing)\le\delta
\quad\text{for every unsafe binary support }B.
\tag{9}
$$

Indeed, if Q_0 misses B, the table 1_B produces exactly the same queried labels and certificate as the zero table under the same random seed. This is a constraint on arbitrary adaptive auditors, with no independence assumption on Q_0.

**Lemma 1.** Suppose a block contains d>=1 items and every b-item subset of that block is unsafe, where 1<=b<=d. If X is the number of queried block items on the zero path and mu=E_0 X, then

$$
\boxed{\quad
\mu\ge\frac{L(d-b)}{b+L}.
\quad}
\tag{10}
$$

This lemma holds for every 0<delta<1. When b=d its displayed lower bound is zero; no positive bound is asserted in that case.

**Proof.** Average (9) over a uniformly chosen b-subset, independently of Q_0. Conditional on X=x, its miss probability is

$$
f(x)=\frac{\binom{d-x}{b}}{\binom db},\qquad x=0,\ldots,d.
\tag{11}
$$

Extend f linearly between integers. Its successive differences are

$$
f(x+1)-f(x)=-\frac{\binom{d-x-1}{b-1}}{\binom db},
$$

which are nondecreasing, with impossible binomial choices zero. Hence f is convex on [0,d]. Averaging and Jensen's inequality give delta>=E f(X)>=f(mu).

If mu>=d-b, then (10) follows immediately because L/(b+L)<1. Otherwise mu<d-b. Put c=d-b-mu>0. For either integer endpoint x=floor(mu) or x=ceil(mu), we have x<=d-b, so all factors below are positive. The inequality log(1-u)>=-u/(1-u), for 0<=u<1, gives

$$
\begin{aligned}
\log f(x)
&=\sum_{j=0}^{b-1}\log\left(1-\frac{x}{d-j}\right)\\
&\ge-\sum_{j=0}^{b-1}\frac{x}{d-j-x}
\ge-\frac{bx}{d-b+1-x}
\ge-\frac{bx}{c}.
\end{aligned}
\tag{12}
$$

The last step uses x<=mu+1. Linear interpolation of the two endpoint bounds, followed by convexity of x -> exp(-bx/c), yields f(mu)>=exp(-b mu/c). This also holds when mu is an integer. Consequently

$$
e^{-L}=\delta\ge e^{-b\mu/(d-b-\mu)}.
$$

Taking logarithms and rearranging gives L(d-b)<=mu(b+L), proving (10). QED.

## 4. Geometric bins of the rank envelope

Every w_n(r) is nonincreasing in r, so e(r) is nonincreasing. Budget 1 ensures e(r)>0. At the endpoints,

$$
e(1)=N/m,\qquad e(m)=1/m.
\tag{13}
$$

Fix eta>0. Starting at rank 1, construct each bin as the maximal consecutive interval [u,v] satisfying e(u)/e(v)<=1+eta, and start the next bin at v+1. This is well defined even when e has jumps or ties. Let J be the number of bins. If a next bin exists, maximality implies e(u)/e(v+1)>1+eta. Applying this to successive bin starts and using (13) proves

$$
J\le1+\frac{\log N}{\log(1+\eta)}.
\tag{14}
$$

For N=1 there is exactly one bin, and (14) still holds.

For bin j=[u_j,h_j], choose any budget n_j attaining e(h_j), and include all P prompts at these ranks. Define

$$
d_j=P(h_j-u_j+1),\qquad
\nu_j=e(h_j)/P,\qquad
q_j=d_j\nu_j=(h_j-u_j+1)e(h_j).
\tag{15}
$$

Monotonicity of the single witness row n_j gives a_(n_j)(i)>=nu_j throughout the block. The bin ratio also gives

$$
\sum_j q_j\ge\frac{Z}{1+\eta}.
\tag{16}
$$

Thus each bin has one valid witness target, even if the envelope maximizer changes inside it. The bins partition all D items; they are geometric in envelope value, not necessarily in rank or budget.

## 5. The finite cost inequality

Fix kappa>1+a and retain only bins with q_j>=kappa*tau. In each retained bin put

$$
b_j=\left\lfloor\frac{\tau}{\nu_j}\right\rfloor+1.
\tag{17}
$$

Every b_j-subset is strictly unsafe under its witness budget. Let M=N/(Pm), the maximum individual target mass, so nu_j<=M and a=M/tau. Exact rounding in (17) gives

$$
\begin{aligned}
b_j&\le\frac{\tau}{\nu_j}(1+a),&
\frac{b_j}{d_j}&\le\frac{1+a}{\kappa}<1,\\
\frac{d_j}{b_j}&\ge\frac{q_j}{\tau(1+a)},&
\frac{L}{b_j}&\le\frac{LM}{\tau}=\rho.
\end{aligned}
\tag{18}
$$

In particular 1<=b_j<d_j, so Lemma 1 applies without an infeasible subset size. It yields

$$
\begin{aligned}
\mathbb E_0|Q_0\cap I_j|
&\ge L\frac{d_j}{b_j}
\frac{1-b_j/d_j}{1+L/b_j}\\
&\ge\frac{Lq_j}{\tau}
\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
\end{aligned}
\tag{19}
$$

Here I_j denotes the block of prompt-rank items, rather than only its rank interval. Costs in disjoint retained blocks add; the number queried outside those blocks is nonnegative. At most J bins were discarded, each having q_j<kappa*tau. Therefore, writing x_+=max(x,0), every admissible auditor satisfies

$$
\boxed{\quad
\operatorname{OPT}_0\ge
\frac L\tau
\left(\frac{Z}{1+\eta}-J\kappa\tau\right)_+
\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
\quad}
\tag{20}
$$

This is a finite inequality, valid for any eta>0 and kappa>1+a. If the positive part is zero or no bin survives, it gives the trivial lower bound zero. It does not replace a missing positive lower bound by a numerical tolerance. The sharper sum of the individual bounds L(d_j-b_j)/(b_j+L), when available, can be used instead of (20).

## 6. Uniform passage to the limit

The envelope has Z>=1. The [existing finite-pool normalizer result](sharp-envelope.md#proof-of-the-finite-bound) also gives

$$
Z\ge L_N=1+\sum_{n=2}^N\frac{(n-1)^{n-1}}{n^n}
\ge1+\frac{H_N-1}{e}\ge\frac{\log N}{e}.
\tag{21}
$$

Here H_N is the Nth harmonic number, and L_N is the earlier continuous normalizer, distinct from L=log(1/delta). The middle inequality follows from (1-1/n)^(n-1)>=e^(-1). Thus, for 0<eta<=1, (14) implies

$$
\frac JZ\le1+\frac e{\log(1+\eta)}
\le1+\frac6\eta,
\tag{22}
$$

using log(1+eta)>=eta/2 and 2e<6.

Choose eta=tau^(1/3) and kappa=1/eta. When eta(1+a)<1, which holds eventually in (6), inequality (20) and 1/(1+eta)>=1-eta give the explicit relative bound

$$
\boxed{\quad
\frac{\operatorname{OPT}_0}{LZ/\tau}
\ge
(1-7\eta-\eta^2)_+
\frac{1-(1+a)\eta}{(1+a)(1+\rho)}.
\quad}
\tag{23}
$$

Indeed, the discarded fraction is at most (J/Z)kappa*tau<=eta^2+6eta, and flattening the bins loses at most eta. Since delta<=1/4, L>=log(4), and therefore

$$
0<a=\rho/L\le\rho/\log4\longrightarrow0.
$$

All factors on the right of (23) tend to one with tau and rho, independently of the remaining parameters. Combining this with (5) proves (7). The uniform relation Z_(m,N)=(log N)/e+O(1) from [sharp-envelope.md](sharp-envelope.md#result) proves (8) whenever N tends to infinity.

This argument allows delta to tend to zero, provided rho still tends to zero. It does not assert a nonasymptotic improvement at ordinary thresholds. In particular, the universal expression (23) is vacuous at the earlier synthetic study's tau=.1. That study is not evidence for practical efficiency in this limit.

## 7. Why confidence cannot approach one without another condition

The bound delta<=1/4 is sufficient, not asserted sharp. A restriction keeping L away from zero cannot simply be dropped while retaining only tau->0 and rho->0.

Take P=N=1, let m tend to infinity through integers m>=2, and set tau=m^(-2), L=m^(-3), delta=exp(-m^(-3)). Then rho=m^(-2)->0, but a=m. Every singleton binary support is unsafe. The zero-path constraints force each item to be queried with probability at least 1-delta, so OPT_0>=m(1-delta). Equality is attained by choosing a full census with probability 1-delta and the empty set otherwise, certifying exactly when the queried labels are all zero. This is valid for fractional labels as well, since any unsafe table has a positive loss somewhere. Hence

$$
\operatorname{OPT}_0=m(1-e^{-m^{-3}})\sim m^{-2},\qquad
C_{\mathrm{NEG}}=m(1-e^{-m^{-2}})\sim m^{-1}.
\tag{24}
$$

Here Z=1 and LZ/tau=m^(-1), so NEGEXP/OPT_0 diverges like m. The empty-query lotteries are legitimate under the comparator; excluding them would change the problem.

## 8. Rational designs, numerical evidence, and attribution

Any independent inclusion design with probabilities satisfying

$$
1-e^{-Ts_i}\le q_i\le\min\{1,Ts_i\}
\tag{25}
$$

is valid by the same miss-probability argument and has C_NEG<=C_q<=LZ/tau. Its formal expected cost therefore inherits (7). The [existing rational construction](zero-workflow-numerics.md) supplies this sandwich on its supported inputs. This is a mathematical transfer, not a change to the released CLI's resource caps or input domain. No claim is made that the capped implementation samples an unbounded parameter sequence.

The [internal protocol](../experiments/sharp_cost_protocol.json) fixes a deterministic exact-arithmetic check after exploratory proof checks and before the saved broader run. It is not an external preregistration or empirical holdout. Its finite checks compare hypergeometric inverse constraints with Lemma 1 and inspect rank-bin witnesses. Its constructed geometries evaluate analytical lower and upper costs without allocating P*m labels. For conservative numerical certificates, an outward lower bound on L can be inserted into L(d-b)/(b+L), which is nondecreasing in L; an upper bound on L gives the upper cost LZ/tau. Rounding block lower bounds down and the total upper bound up preserves the comparison. Finite checks and conservative rounding support the proof's implementation; they do not establish the infinite-sequence theorem, novelty, or real-model utility.

[Aslam, Popa, and Rivest (2008), Sections 8, 12, and 13.2](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/), give NEGEXP, unrestricted randomized-subset auditing, and multi-target reuse. The zero-path characterization here is a specialization of that established optimization, using the coupling stated in the earlier note. [Anthony and Salehzadeh Nobari (2026), Theorem 13](https://arxiv.org/html/2607.21480v1), is close finite-corpus prior art for adaptive zero-history lower bounds with planted positives. The hypergeometric averaging and convexity used here are classical ingredients.

[Fitas (2026, v2), Section 2.4 and Supplements S2, S5, and S7.2](https://arxiv.org/html/2608.21496v2), supplies the continuous envelope normalizer and its 1/e coefficient, geometric control, and adaptive lower bounds through score bands. [Sarkar and Baichoo (2026), Appendix C](https://arxiv.org/html/2609.40190v1), likewise uses geometric levels and disjoint score bands for lower bounds. Those particular lower-bound experiments differ from the fixed distinct-label comparator here; this is not a claim that the papers omit stored pools or caching. Older [inspection-game work by Avenhaus, Canty, Kilgour, von Stengel, and Zamir (1996)](https://doi.org/10.1016/0377-2217(95)00261-8) studies stratified inspection allocation and is another relevant priority lead. The older inspection literature has not been exhaustively checked.

The candidate contribution is the explicit finite lower bound (20) and its uniform sharp consequence (7) against unrestricted adaptive zero-table auditors, with the stated joint-limit conditions. Neither the sampling primitive, the normalizer coefficient, nor a generic geometric lower-bound technique is claimed as new. The result does not resolve annotation error, duplicate-label information, unequal acquisition costs, nonzero-instance efficiency, or the empirical usefulness of this audit objective.
