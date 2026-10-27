# A finite-pool cost approximation theorem for zero-loss certification

Draft candidate result, 26 October 2026. This note gives a special-family proof for independent negative-exponential inspection. That inspection design and the generic subset-auditing optimization are established prior work. Scientific priority for the rank-family cost bound has not been established. The statement concerns expected distinct-label cost on the all-zero table; it is not an optimal stopping theorem or a claim of practical optimality for the published betting engine.

This result was developed with substantial Codex assistance, including proof drafting, implementation, and reviews in separate agent contexts. It has not received independent human review or replication. See the [contribution disclosure](provenance.md).

## 1. Experiment, decision, and algorithm class

Fix integers `P>=1` and `m>=1`. There are `D=Pm` items, indexed by prompt and rank `(p,r)`, with `1<=p<=P` and `1<=r<=m`. Rank 1 is best under a fixed total order. There are no initially known labels. Querying an item reveals its fixed, correct loss `y[p,r]` in `[0,1]` and costs one label; repeated queries supply no new information and are unnecessary. Computation is not charged. The label oracle is the only source of loss information: no known cross-item label relationships, duplicate-answer oracle, or supplied labels reveal additional losses at zero cost.

Let `K` be a nonempty subset of `{1,...,m}`, let `N=max K`, and assume the declared grid contains every power of four up to its maximum:

$$
\{4^j:0\le j\le\lfloor\log_4N\rfloor\}\subseteq\mathcal K.
\tag{1}
$$

The complete prefix `{1,...,N}` satisfies (1). A dyadic grid containing every power of two through its maximum also satisfies it. An arbitrary sparse grid need not satisfy it.

For `n in K`, define the finite without-replacement winner weights and target risk

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
a_n(p,r)=\frac{w_n(r)}P,\qquad
R_n(y)=\sum_{p,r}a_n(p,r)y[p,r].
\tag{2}
$$

Impossible binomial choices are zero. Every target row is nonnegative and sums to one. All statements condition on the fixed pools and losses; there is no assumption of independently generated prompts or labels.

Fix a risk threshold `0<tau<1` and error probability `0<delta<1`. An admissible auditor may randomize, select queries adaptively from previously unseen items, and use all past labels. It may issue a single whole-family certificate asserting

$$
R_n(y)\le\tau\quad\text{for every }n\in\mathcal K,
\tag{3}
$$

or abstain. It must satisfy both conditions:

1. For every fixed `y in [0,1]^D` with `max_n R_n(y)>tau`, the probability it ever issues (3) is at most `delta`.
2. On the all-zero table, it issues (3) after finitely many queries with probability one.

Probability is over the auditor's internal randomness. No correctness or stopping promise beyond these requirements is imposed on other tables. An auditor can be stopped after its first certificate. A full census followed by exact evaluation is admissible, so the class is nonempty. Empty-query certification lotteries are allowed; they consume the same false-certification allowance as any other event.

Let `Q_0` be the set queried before the first certificate on the zero table. Define

$$
\operatorname{OPT}_0=\inf_{\mathcal A}\mathbb E_0|Q_0|,
\tag{4}
$$

where the infimum ranges over all admissible auditors, without computational restrictions. The probability-one condition is essential: if no power requirement were imposed, the procedure that always abstains would have zero cost. A lesser specified power would define a different optimization problem.

The decision in (3) is also essential. Once the whole-family certificate passes, any subset is also certified. It does not authorize individual or subset certificates when the whole-family condition has not passed, nor does it return a confidence band. Whole-family certification and partial certification have different testing requirements.

## 2. The all-zero path and the established subset LP

For a set of items `B`, write `a_n(B)=sum_{i in B}a_n(i)` and call `B` unsafe when `max_n a_n(B)>tau`. Consider the finite linear program

$$
\begin{aligned}
\min_{(p_Q)}\quad &\sum_{Q\subseteq[D]}p_Q|Q|\\
\text{subject to}\quad
&p_Q\ge0,\qquad \sum_Qp_Q=1,\\
&\sum_{Q:Q\cap B=\varnothing}p_Q\le\delta
  &&\text{for every unsafe }B.
\end{aligned}
\tag{5}
$$

This is the established audit-subset optimization specialized to the present dangerous sets; see Aslam, Popa, and Rivest below.

**Lemma 1 (zero-path characterization).** The optimum of (5) equals `OPT_0`, including when validity is required for all fixed losses in `[0,1]`.

**Proof.** Couple all runs of an admissible auditor using the same complete internal random seed. For each seed on which the zero-table run certifies, record its queried set `Q_0`. Its law is a probability distribution by condition 2. Fix an unsafe binary table `1_B`. If `Q_0` misses `B`, every observed loss before the zero-table certificate is also zero under `1_B`. Induction over the queries shows that the two runs make the same choices and issue the same certificate. Hence

$$
\Pr_0(Q_0\cap B=\varnothing)
\le \Pr_{1_B}(\text{certificate})\le\delta.
\tag{6}
$$

Thus the zero-path distribution is feasible in (5), and its objective is exactly the auditor's zero-table cost. This gives the lower bound on every adaptive auditor, regardless of its behavior after a positive observation.

Conversely, sample `Q` according to any feasible solution of (5), inspect it, and certify if and only if every inspected loss is exactly zero. Otherwise abstain. It certifies the zero table with probability one. For any unsafe fractional table `y`, its positive support `B={i:y_i>0}` is an unsafe binary set, since

$$
\max_n a_n(B)\ge\max_n\sum_i a_n(i)y_i>\tau.
\tag{7}
$$

The procedure certifies this table exactly when `Q` misses `B`, which has probability at most `delta`. Its expected zero-table cost is the objective in (5). The feasible LP is finite and compact, so its optimum is attained. This proves equality. If eventual certification of every safe table is desired, replace abstention after a positive observation by a full census and exact evaluation; the zero-table objective is unchanged. Neither construction promises low cost on nonzero tables. QED.

The proof uses nonnegative target weights and `y<=1`. It does not cover incorrect, changing, or noisy latent labels. Nor does zero mean “smaller than a numerical tolerance.”

## 3. Design and theorem

Define the unnormalized envelope on individual items

$$
s_i=\max_{n\in\mathcal K}a_n(i),\qquad
L=\log(1/\delta),\qquad T=\frac L\tau.
\tag{8}
$$

Independently include each item `i` with probability

$$
p_i=1-\exp(-Ts_i).
\tag{9}
$$

Inspect the selected set and certify (3) only if all selected losses are zero. This is the classical NEGEXP design, using the target envelope as the item error bound. Its expected zero-table label cost is

$$
C_{\mathrm{NEG}}=\sum_i[1-\exp(-Ts_i)].
\tag{10}
$$

To state an explicit finite cost scale, put `J=floor(log_4 N)`, `n_j=4^j`, and partition ranks into

$$
\begin{aligned}
I_j&=\{\lfloor m/4^{j+1}\rfloor+1,\ldots,\lfloor m/4^j\rfloor\},
&&0\le j<J,\\
I_J&=\{1,\ldots,\lfloor m/4^J\rfloor\}.
\end{aligned}
\tag{11}
$$

Each block contains all `P` prompts at its ranks. Write `D_j=P|I_j|` and

$$
A=\sum_{j=0}^{J}\min\{D_j,T\}.
\tag{12}
$$

The blocks are nonempty, disjoint, and cover all items. In particular, `sum_j D_j=D`; if `T>=D`, then `A=D` exactly. The formula retains the saturation of individual blocks near census rather than continuing a logarithmic approximation beyond the finite population.

**Theorem (finite-pool cost approximation).** Suppose (1) holds and

$$
0<\tau\le\frac18,\qquad 0<\delta\le\frac14.
\tag{13}
$$

Then the zero-only NEGEXP procedure is admissible, and

$$
\boxed{
\frac A{40}\le\operatorname{OPT}_0\le C_{\mathrm{NEG}}
\le4A\le160\operatorname{OPT}_0.
}
\tag{14}
$$

The constants are deliberately loose. The theorem compares actual expected distinct-label cost with an unrestricted adaptive zero-table optimum at the same error probability. It incurs no factor growing with the number of declared budgets. It does not compare expected cost on other loss tables, establish exact optimality, or imply optimality of the repository's betting procedure.

## 4. The finite fourfold-block lemma

**Lemma 2.** For each block `j` in (11) and every item `i` in that block,

$$
a_{n_j}(i)>\frac1{4D_j},\qquad s_i\le\frac4{D_j}.
\tag{15}
$$

**Proof of the lower bound.** Fix `n=n_j`, write `x=m/n>=1`, `h=floor x`, and `t=|I_j|`. For a nonfinal block, `t=h-floor(h/4)`; for the final block, `t=h`. Thus in both cases `t>=3h/4`. All its ranks are at most `h`. The law `w_n(r)` is nonincreasing in `r`, so its minimum over the block is at least `w_n(h)`.

The rank-product representation gives

$$
w_n(h)=\frac nm\prod_{u=1}^{h-1}\left(1-\frac{n-1}{m-u}\right).
\tag{16}
$$

Since `nu<=nh<=m`, every quotient `(n-1)/(m-u)` is at most `n/m=1/x`. Therefore

$$
w_n(h)\ge \frac1x\left(1-\frac1x\right)^{h-1}.
\tag{17}
$$

When `h=1`, the product is empty. The right side is `1/x`, including `x=1` under the empty-product convention; because `1<=x<2` and `t=1`, it is greater than `1/2` after multiplying by `t`.

For `h>=2`, let `F_h(x)=x^{-1}(1-x^{-1})^{h-1}` on `[h,h+1)`. Its logarithmic derivative is

$$
\frac{d}{dx}\log F_h(x)=\frac{h-x}{x(x-1)}\le0.
\tag{18}
$$

Consequently,

$$
t w_n(h)\ge\frac{t h^{h-1}}{(h+1)^h}
\ge\frac34\left(\frac h{h+1}\right)^h
>\frac3{4e}>\frac14.
\tag{19}
$$

Here `(1+1/h)^h<e<3`. Dividing by `Pt=D_j` proves the first bound in (15). The separate `h=1` argument covers that endpoint without differentiating at `x=1`.

**Proof of the upper bound.** Since each `w_n` is a nonincreasing probability mass function, `r w_n(r)<=1`; also `w_n(r)<=w_n(1)=n/m`. In a nonfinal block, `r>m/(4n_j)`, so

$$
s_{p,r}\le\frac1{Pr}<\frac{4n_j}{Pm}\le\frac4{Pt}.
\tag{20}
$$

The last inequality uses `t<=m/n_j`. In the final block, every declared budget is at most `N<4n_J`, giving

$$
s_{p,r}\le\frac N{Pm}<\frac{4n_J}{Pm}\le\frac4{Pt}.
\tag{21}
$$

This proves (15). Nonemptiness follows from `m/n_j>=1` and the displayed formulas for `t`. The endpoints in (11) telescope, proving the stated partition property. QED.

The lower bound uses only the declared rows `n_j=4^j`; the upper bound uses only that all declared budgets are at most `N`. This explains exactly why the structured-grid extension (1) is allowed.

## 5. A finite hypergeometric miss bound

**Lemma 3.** Let a block contain `d>=1` items and put

$$
b=\lfloor4\tau d\rfloor+1.
\tag{22}
$$

Under (13), `1<=b<=d`. Suppose a random inspected subset has count `X` in this block and misses each fixed `b`-item subset with probability at most `delta`. Then

$$
\mathbb E X\ge\frac1{40}\min\{d,L/\tau\}.
\tag{23}
$$

**Proof.** The bound `b<=d` follows from `b<=floor(d/2)+1<=d` for `d>=2`; when `d=1`, `b=1`. Average the miss constraints uniformly over all `b`-item subsets. Conditional on the actual inspected set, the average miss probability depends only on its size. Thus

$$
\mathbb E f(X)\le\delta,\qquad
f(z)=\frac{\binom{d-z}{b}}{\binom db},\quad z=0,\ldots,d.
\tag{24}
$$

Interpret impossible binomial coefficients as zero and extend `f` linearly between consecutive integers. This extension is convex: for `b>=2`, its successive second differences are

$$
f(z+2)-2f(z+1)+f(z)
=\frac{\binom{d-z-2}{b-2}}{\binom db}\ge0;
\tag{25}
$$

for `b=1`, `f(z)=1-z/d` is linear. Write `mu=E X`. Jensen's inequality yields `f(mu)<=E f(X)<=delta`.

First suppose `d>=8`. Since `tau<=1/8`,

$$
b\le d/2+1\le3d/4.
\tag{26}
$$

At any integer `0<=z<=d/8`,

$$
f(z)=\prod_{u=0}^{b-1}\left(1-\frac z{d-u}\right)
\ge\exp\left(-\frac{8bz}{d}\right).
\tag{27}
$$

Indeed, `d-u>=d-b+1>=d/4`; hence each subtracted quantity is at most `4z/d<=1/2`. Applying `log(1-v)>=-2v` on `[0,1/2]` and summing proves (27).

If `mu>=d/16`, retain that lower bound. Otherwise `mu<d/16`, and both `floor(mu)` and `ceil(mu)` lie in `[0,d/8]`. To check the rounding boundary: for `8<=d<16`, `ceil(mu)<=1<=d/8`; for `d>=16`, `ceil(mu)<=mu+1<d/16+1<=d/8`. Thus (27) holds at both interpolation endpoints. Their linear interpolation is at least `exp(-8b mu/d)`, by convexity of the exponential. Jensen now gives

$$
\delta\ge f(\mu)\ge e^{-8b\mu/d},
\qquad
\mu\ge\frac{dL}{8b}.
\tag{28}
$$

Combining the two cases,

$$
\mu\ge\min\left\{\frac d{16},\frac{dL}{8b}\right\}.
\tag{29}
$$

Set `x=tau d`. We have `b<=4x+1` and `L>=log 4>1`. If `x<=1`, then `8b<=40` and (29) is at least `d/40`; also `min(d,L/tau)=d`. If `x>=1`, then `8b<=40x`, so

$$
\mu\ge\min\left\{\frac d{16},\frac{dL}{40x}\right\}
\ge\frac1{40}\min\{d,L/\tau\}.
\tag{30}
$$

For `1<=d<8`, fix one `b`-item subset. The event `X=0` implies it was missed, so `Pr(X=0)<=delta`. Therefore `E X>=1-delta>=3/4>d/40`, which proves (23) in the remaining cases. QED.

This argument makes no independence assumption about the inspected items. Their distribution may contain arbitrary correlations induced by an adaptive audit's zero path.

## 6. Proof of the cost approximation theorem

**Lower cost.** Take any admissible auditor and its zero-path set `Q_0`. In block `j`, let `X_j=|Q_0 intersect block j|` and `b_j=floor(4tau D_j)+1`. By Lemma 2, every `b_j`-item subset `B` within this block has

$$
a_{n_j}(B)>\frac{b_j}{4D_j}>\tau,
\tag{31}
$$

so it is unsafe. Lemma 1 supplies all corresponding miss constraints. Applying Lemma 3 and summing over the disjoint partition gives

$$
\mathbb E_0|Q_0|=\sum_j\mathbb E X_j
\ge\frac1{40}\sum_j\min\{D_j,T\}=\frac A{40}.
\tag{32}
$$

Infimizing over auditors proves the first inequality in (14).

**Validity and upper cost.** For any unsafe loss table, let `B` be its positive support. By (7), some target gives `a_n(B)>tau`, and therefore `sum_{i in B}s_i>tau`. Independent inclusion in (9) gives

$$
\Pr(Q\cap B=\varnothing)
=\prod_{i\in B}e^{-Ts_i}
=e^{-T\sum_{i\in B}s_i}<e^{-T\tau}=\delta.
\tag{33}
$$

There is no union bound over targets: every fixed unsafe table has a particular unsafe target whose mass supplies this inequality. The procedure certifies the zero table after at most `D` queries, including the possible empty subset, so it is admissible.

Since `1-e^{-u}<=min(1,u)` for `u>=0`, Lemma 2 gives

$$
\begin{aligned}
C_{\mathrm{NEG}}
&\le\sum_j D_j\min\{1,4T/D_j\}\\
&=\sum_j\min\{D_j,4T\}
\le4\sum_j\min\{D_j,T\}=4A.
\end{aligned}
\tag{34}
$$

Admissibility implies `OPT_0<=C_NEG`; combining (32) and (34) gives the factor 160. QED.

## 7. Why a threshold restriction matters

A universal constant over all thresholds is false even for the complete BoN prefix. Take one prompt, `N=m>=2`, and

$$
\tau_m=1-\frac1{2m}.
\tag{35}
$$

For binary failure sets, being unsafe is equivalent to containing rank 1. If a set contains rank 1, its budget-`m` risk is one. If it does not, then for every `n`,

$$
a_n(B)\le1-w_n(1)=1-\frac nm\le1-\frac1m<\tau_m.
\tag{36}
$$

The constraint for the singleton `{1}` forces `Pr(1 in Q)>=1-delta`, so `OPT_0>=1-delta`. Equality is attained by inspecting rank 1 with probability `1-delta`, choosing the empty set otherwise, and certifying only after zero observations. This is valid for fractional losses too by Lemma 1.

For NEGEXP, `0<=s_r<=1`. Concavity of `u -> 1-exp(-Tu)` on `[0,1]` gives

$$
C_{\mathrm{NEG}}\ge(1-e^{-T})\sum_r s_r
\ge(1-\delta)Z_{m,m},
\tag{37}
$$

because `T=L/tau_m>=L`. Hence `C_NEG/OPT_0>=Z_m,m`, which diverges logarithmically by the [finite-envelope analysis](sharp-envelope.md). Even with fixed `delta`, the ratio is unbounded as these thresholds approach one. These thresholds lie outside (13), so the example does not contradict the theorem; it precludes removing all threshold restrictions from the stated design guarantee.

## 8. Attribution and claim boundary

[Aslam, Popa, and Rivest (2008), Sections 8, 12, and 13.2](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/), supply NEGEXP, its miss-probability calculation, optimal randomized subset auditing, and reuse across multiple races. Equations (5) and (9) are applications of these established constructions. Neither is claimed as a new general audit design.

[Behnezhad et al. (SODA 2018), Section 7, LPs (7.5)-(7.6), and Theorem 7.1](https://people.csail.mit.edu/rivest/pubs/BBDHx18.pdf), provide fractional packing/covering benchmarks and a constant approximation to detection probability at a fixed inspection budget in auditing games. This is direct prior art for generic hitting arguments and approximation by randomized inspection. The present statement fixes the false-certification probability and bounds expected distinct-label cost for a specified rank family. That difference identifies the claim to check; it does not establish novelty. [DOI](https://doi.org/10.1137/1.9781611975031.148).

[Fitas (2026, v2)](https://arxiv.org/html/2608.21496v2) and [Sarkar and Baichoo (2026)](https://arxiv.org/html/2609.40190v1) already derive multiscale label-acquisition lower bounds for BoN families. Their relevant lower-bound experiments involve fresh responses or answer occurrences, rather than the present fixed-label, distinct-item zero-path objective and its finite census saturation. This compares particular theorem objectives; it does not assert that those papers omit stored pools or label reuse. The proof above still uses established multiscale and coupling ideas. A priority assessment must check equivalent formulations and consequences of those works, not infer novelty merely from different notation or a finite-population specialization.

[Anthony and Salehzadeh Nobari (2026), Theorem 13](https://arxiv.org/html/2607.21480v1), give a finite-corpus lower bound by coupling an adaptive audit's zero-label path with planted-positive tables. Their zero-table power condition also rules out vacuous abstention. This is close prior art for Lemma 1's indistinguishability argument and for the blockwise necessity of acquiring labels.

The candidate special-family contribution is the explicit block comparison (15) combined with the finite miss bound to give (14), with its stated grid, threshold, confidence, and algorithm-class restrictions. It is a cost approximation theorem for the all-zero instance. It does not establish a practically tight factor, good cost after positive labels, a new confidence sequence, real-model evidence, or a population safety guarantee. No measured source or result from the published studies is changed by this note.

## 9. Sharper computable cost certificates

The universal factor is intentionally coarse. For a particular finite geometry, the same proof gives an exact rational lower bound that can be much sharper. In block j, let v_j be the minimum of the chosen target mass a_nj(i) over its items, and set b_j=floor(tau/v_j)+1. The block lemma and tau<=1/8 ensure 1<=b_j<=D_j. Every b_j-item subset has risk strictly greater than tau.

Let f_j be the piecewise-linear hypergeometric miss function from (24). Since f_j(0)=1 and f_j(D_j)=0, find the smallest integer d with f_j(d)<=delta. The exact inverse at delta is

$$
q_j=d-1+\frac{f_j(d-1)-\delta}{f_j(d-1)-f_j(d)}.
\tag{38}
$$

Its denominator is positive. Jensen's inequality implies E X_j>=q_j for every admissible auditor. Therefore the sum of q_j is a lower bound on OPT_0. It is not generally the exact optimum: it uses only a subset of the unsafe-set constraints. For rational tau and delta, the rank masses and the whole expression are rational numbers.

An exact rational upper bound on C_NEG is also available without numerical logarithms or exponentials. Choose an integer c>=1 and a finite positive Taylor sum satisfying

$$
\sum_{k=0}^{H}\frac{c^k}{k!}\ge\frac1\delta.
\tag{39}
$$

The left side is at most exp(c), so c>=L. For x>=0, Taylor's signed remainder gives

$$
1-e^{-x}\le U_5(x)=\min\left\{1,x-\frac{x^2}{2}+\frac{x^3}{6}-\frac{x^4}{24}+\frac{x^5}{120}\right\}.
\tag{40}
$$

Both entries of the minimum are upper bounds; the polynomial is nonnegative because it bounds 1-exp(-x). Monotonicity in the exponent now gives the exact rational certificate

$$
\sum_j q_j\le\operatorname{OPT}_0\le C_{\mathrm{NEG}}
\le\sum_i U_5(cs_i/\tau).
\tag{41}
$$

Thus the right sum divided by the positive left sum is a certified competitive-ratio upper bound for that particular geometry. It bounds a theoretical expected cost on the zero table, not a realized query count or a measured model result. It need not equal the design's actual cost. The global factor 160 is still available when this geometry-specific upper bound is looser.

The standard-library checker uses these rational expressions for the fixed cases in the internal protocol. Decimal displays summarize exact fractions. Its finite-grid checks support implementation of the lemmas; they do not replace the proof for unbounded pool sizes or confidence levels.
