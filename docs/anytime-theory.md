# Anytime auditing with one new label per draw

This note specializes established weighted sampling without replacement and betting confidence sequences to several best-of-n risks. The direct methodological precedent is [Shekhar, Xu, Lipton, Liang, and Ramdas, *Risk-limiting Financial Audits via Weighted Sampling without Replacement*, UAI 2023, Definition 2 and Theorem 1](https://proceedings.mlr.press/v216/shekhar23a/shekhar23a.pdf). Their construction already handles a fixed weighted total, predictable sampling from remaining items, inverse-probability correction, and nonnegative betting processes. We do not claim those ingredients, fractional bets, mixtures, or anytime validity as new.

The application here shares each queried label across a predeclared family of rank-based risks, uses the rank envelope as an acquisition proposal, and reports cost in distinct queried items. See [anytime-related-work.md](anytime-related-work.md) for the prior-art boundary and [theory.md](theory.md) for the finite-pool rank law and its envelope bounds.

## 1. Fixed targets and the remaining population

Fix a finite candidate universe `U_0` and `K` targets. Target `n` has known masses `a_n(i)>=0` satisfying

$$
\sum_{i\in U_0}a_n(i)=1,
\qquad
R_n=\sum_{i\in U_0}a_n(i)y_i,
\qquad y_i\in[0,1].
\tag{1}
$$

The losses are fixed, possibly unknown. All probability statements condition on this table and use only the audit's random ordering. No independent-prompts assumption is required for this conditional target, and no new-prompt population guarantee follows from it.

For `P` pools with `m` candidates each, rank 1 is best. The finite-pool best-of-n target is obtained by setting

$$
a_n(i,r)=\frac{w_n(r)}P,
\qquad
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn}.
$$

The selector draws a uniform `n`-subset without replacement and returns its best member under a frozen total order, including a declared tie rule. The target family and its weights must be fixed before the audit.

Before draw `t`, let `U_{t-1}` be the remaining items. Define the revealed contribution and remaining target mass by

$$
S_{n,t-1}=\sum_{j<t}a_n(I_j)y_{I_j},
\qquad
B_{n,t-1}=\sum_{i\in U_{t-1}}a_n(i).
\tag{2}
$$

After drawing and labeling `I_t`, remove it permanently. Thus `t` draws acquire exactly `t` distinct items when the audit starts with no known labels. Existing known labels can instead be removed at initialization and included in an initial `S_n`; they must not also be counted as new queries.

Items whose mass is zero for every target may be omitted. A proposal must have positive probability for every remaining item with positive mass for any target it evaluates.

## 2. General positive proposals and target-specific normalization

Choose known weights `h(i)>0` on the active universe. The three natural comparisons are uniform weights, a mixture of target masses, and the rank envelope. For fixed `h`, the without-replacement proposal is

$$
H_t=\sum_{i\in U_{t-1}}h(i),
\qquad q_t(i)=\frac{h(i)}{H_t}.
\tag{3}
$$

For each unresolved target, use its own sharp observation-range bound

$$
d_{n,t}=\max_{i\in U_{t-1}}\frac{a_n(i)}{h(i)},
\qquad
c_{n,t}=H_t d_{n,t}
=\max_{i\in U_{t-1}}\frac{a_n(i)}{q_t(i)}.
\tag{4}
$$

If `B_n,t-1=0`, the target is already known exactly as `R_n=S_n,t-1`; skip its betting updates. Otherwise `c_n,t>0`, and define

$$
Y_{n,t}=\frac{a_n(I_t)y_{I_t}}{q_t(I_t)c_{n,t}},
\qquad
m_{n,t}(\mu)=\frac{\mu-S_{n,t-1}}{c_{n,t}}.
\tag{5}
$$

The maximum in (4) gives `0<=Y_n,t<=1`. Moreover,

$$
\begin{aligned}
\mathbb E[Y_{n,t}\mid\mathcal F_{t-1}]
&=\frac1{c_{n,t}}\sum_{i\in U_{t-1}}a_n(i)y_i\\
&=\frac{R_n-S_{n,t-1}}{c_{n,t}}
=m_{n,t}(R_n).
\end{aligned}
\tag{6}
$$

Here `F_t-1` records the previous draws and labels. Also

$$
B_{n,t-1}
=\sum_{i\in U_{t-1}}q_t(i)\frac{a_n(i)}{q_t(i)}
\le c_{n,t},
\tag{7}
$$

so the true conditional mean lies in `[0,1]`.

For validity, `q_t` may more generally depend on the past, provided it is chosen before draw `t` and has the required support. Set `c_n,t=max_i a_n(i)/q_t(i)` and the same proof applies. The fixed `h` formulation is convenient for a reproducible acquisition policy and an exponential-race implementation. Normalization (4), rather than an unnecessarily larger common bound, should be used for every comparison proposal.

## 3. Fractional bets and their endpoint convention

Use the fixed six-point grid

$$
\Gamma=\{1,1/2,1/4,1/8,1/16,1/32\},
\qquad \pi_\gamma=1/6.
\tag{8}
$$

For a fixed candidate risk `mu`, and abbreviating `m=m_n,t(mu)` and `Y=Y_n,t`, define the upper-direction factor

$$
f^{\mathrm{up}}_{\gamma,n,t}(\mu)
=1-\gamma+\gamma\frac{1-Y}{1-m},
\qquad m<1,
\tag{9}
$$

and the lower-direction factor

$$
f^{\mathrm{lo}}_{\gamma,n,t}(\mu)
=1-\gamma+\gamma\frac{Y}{m},
\qquad m>0.
\tag{10}
$$

An upper process grows against candidates with risk too large; a lower process grows against candidates with risk too small. These are ordinary linear bets with candidate-dependent predictable fractions:

$$
f^{\mathrm{up}}=1-\frac{\gamma}{1-m}(Y-m),
\qquad
f^{\mathrm{lo}}=1+\frac{\gamma}{m}(Y-m).
$$

At the relevant consistent deterministic endpoints, define the factor to be one:

- For (9), if `m=1` and `Y=1`, set the factor to `1`.
- For (10), if `m=0` and `Y=0`, set the factor to `1`.

These are rules for the actual `0/0` cases. A positive numerator divided by zero is not a unit factor; it contradicts that degenerate candidate null. Such a contradiction is impossible when the candidate is in the current deterministic feasible interval and calculations are exact, as shown below. It must not be silently accepted by a broad numerical tolerance.

At the true risk, conditional mean zero forces `Y=0` almost surely, and conditional mean one forces `Y=1` almost surely, because `Y` is bounded in `[0,1]`. Therefore the endpoint rules preserve conditional expectation one. In the interior, (6) immediately gives

$$
\mathbb E[f^{\mathrm{up}}_{\gamma,n,t}(R_n)\mid\mathcal F_{t-1}]
=\mathbb E[f^{\mathrm{lo}}_{\gamma,n,t}(R_n)\mid\mathcal F_{t-1}]=1.
\tag{11}
$$

Every factor is nonnegative. Products may be zero, particularly for `gamma=1`; zero wealth remains zero and must be represented correctly in log-space calculations.

## 4. Simultaneous confidence sequences

For each direction form the products and their fixed mixtures,

$$
M^d_{\gamma,n,t}(\mu)=\prod_{j=1}^t f^d_{\gamma,n,j}(\mu),
\qquad
E^d_{n,t}(\mu)=\sum_{\gamma\in\Gamma}\pi_\gamma M^d_{\gamma,n,t}(\mu),
\quad d\in\{\mathrm{up},\mathrm{lo}\}.
\tag{12}
$$

Once a target is resolved, stop its process; equivalently, subsequent factors are one. At the true target, each component and each mixture is a nonnegative martingale with initial value one. This is exactly the kind of weighted finite-population betting construction studied by Shekhar et al.; equations (4)-(10) specify the normalization and bets used here.

**Theorem.** Fix `0<delta<1` and let

$$
T=\frac{2K}{\delta}.
\tag{13}
$$

With probability at least `1-delta`, for every target `n` and every audit time `t`, both `E_up,n,t(R_n)<T` and `E_lo,n,t(R_n)<T` hold. Consequently, inverting those inequalities within the deterministic feasible interval gives intervals containing every `R_n` simultaneously over all targets and times.

**Proof.** Ville's inequality gives

$$
\Pr\left\{\sup_t E^d_{n,t}(R_n)\ge T\right\}\le\frac1T
=\frac{\delta}{2K}
$$

for each target and direction. A union bound over the `2K` processes proves the statement. No independence across targets is required, and no additional union bound over time is needed. Each mixture starts at one because its weights sum to one; the six components do not require six additional multiplicity allocations.

The result permits selecting both an audit stopping time and a budget from the current data. For example, one may stop when some upper bound is below a declared risk tolerance and return any budget satisfying that bound. A largest certified budget is not necessarily the largest truly safe budget. Risks need not be monotone in `n`, and budget 1 is not automatically safe.

## 5. Feasible domains, monotone inversion, and exhaustion

After `t` labels the deterministic partial-identification interval is

$$
D_{n,t}=[S_{n,t},\ S_{n,t}+B_{n,t}].
\tag{14}
$$

It contains the fixed target for every sampling path. It is sharp under unrestricted remaining losses in `[0,1]`: all remaining losses zero attain its lower endpoint and all remaining losses one attain its upper endpoint. The intervals are nested because revealing a loss adds `a_n(I_t)y_I_t` to the lower endpoint and subtracts `a_n(I_t)(1-y_I_t)` from the upper endpoint.

For any `mu` in `D_n,t` and any historical draw `j<=t`, nesting gives `mu` in `D_n,j-1`. Equations (5) and (7) then place every historical `m_n,j(mu)` in `[0,1]`. Also, `mu` remains compatible with the observed label at draw `j` and some completion of the then-unseen bounded losses. Under that completion, `m` is the proposal mean of bounded normalized losses. If this mean equals zero or one, every item with positive sampling probability has that same normalized loss. In particular the already observed item has `Y=0` or `Y=1`, respectively. This proves that only the consistent endpoint cases arise inside the current feasible domain.

For a fixed observed `Y`, the upper factor is nondecreasing in `m`, and hence in `mu`; the lower factor is nonincreasing. At `m=1,Y=1`, the upper endpoint convention jumps upward from `1-gamma` to `1`; at `m=0,Y=0`, the lower factor jumps downward from its value `1` at the endpoint to `1-gamma` immediately to its right. These jumps preserve monotonicity. Products and mixtures preserve it as well because all factors on the domain are nonnegative.

Define the current acceptance set

$$
\mathcal C_{n,t}
=\{\mu\in D_{n,t}:E^{\mathrm{up}}_{n,t}(\mu)<T,
\ E^{\mathrm{lo}}_{n,t}(\mu)<T\}.
\tag{15}
$$

It is an interval, possibly empty, with endpoints possibly excluded. Its closure is a conservative closed confidence interval. A numerical implementation must enclose this acceptance set rather than retain only accepted grid points:

- For the upper endpoint, maintain an accepted lower bracket and a rejected upper bracket; return the outer, upper bracket.
- For the lower endpoint, maintain a rejected lower bracket and an accepted upper bracket; return the outer, lower bracket.
- Check whether the entire domain is accepted or rejected in a direction before bisection. Endpoint jumps mean a continuous equality root need not exist.
- Record an interval conflict when the two directional acceptance sets do not overlap. The high-probability coverage event rules out such a conflict at the true target, but conflicts are possible on the failure event.

Calculations should use log products and log-sum-exp for the mixture. For example the upper factor can be evaluated from

$$
\log\big((1-\gamma)(1-m)+\gamma(1-Y)\big)-\log(1-m),
$$

with separate exact-endpoint and zero-factor branches. Declaring a denominator merely "small" is not sufficient justification for replacing the factor by one. Floating-point intervals inherit the intended theorem only to the extent that their reported bounds conservatively enclose the mathematical acceptance set; bisection tolerance is not a new statistical error allocation.

If `B_n,t=0`, the target is exactly `S_n,t`, even when other targets remain unresolved. Return this singleton directly without evaluating a zero normalization. At full exhaustion every target is exact. This direct return is valid regardless of earlier statistical exclusions, because the complete weighted sum has been observed.

The current intervals above need not be nested. One may optionally use running intersections of valid intervals to obtain nested confidence sequences; the same coverage guarantee holds. There is a distinction on the probability-`delta` failure event: a past false exclusion can make a running intersection empty even when the current full-data interval is exact. Therefore exact exhaustion of the current interval and exact exhaustion of a mechanically retained running intersection are different claims. The direct current-interval convention returns the census value exactly.

## 6. Sampling by a weighted exponential race

For fixed proposal weights `h`, one may generate the entire without-replacement order in advance. Independently draw `E_i~Exp(1)` and sort the keys

$$
T_i=\frac{E_i}{h(i)}.
\tag{16}
$$

These keys are independent exponentials with rates `h(i)`. Their first minimum is item `i` with probability `h(i)/sum_j h(j)`. By the memoryless property, after revealing the minimum, the residual clocks on the remaining items are again independent exponentials with their original rates. Repeating this argument gives exactly the sequential probabilities in (3).

The race changes how the random order is generated, not the target, label cost, or inference. Labels remain hidden until their items are reached. It gives one distinct queried item at each step and supports stopping at any data-dependent point along the order. A single precomputed race does not implement proposals that adapt their weights to newly seen labels; those require sequential sampling from the updated probabilities.

## 7. The residual envelope is conditionally minimax for the common range

For an arbitrary remaining set `U`, let

$$
s(i)=\max_n a_n(i),\qquad
C(U)=\sum_{i\in U}s(i).
\tag{17}
$$

If `C(U)>0`, then

$$
\inf_q\max_{n,\ i\in U}\frac{a_n(i)}{q(i)}=C(U),
\qquad q^*(i)=\frac{s(i)}{C(U)},
\tag{18}
$$

where the proposal supports every item with positive envelope. Indeed, if the maximum ratio is `L`, then `Lq(i)>=s(i)` for every item. Summing gives `L>=C(U)`. The proposed `q*` attains equality. Zero-envelope items need no probability or query.

This argument holds conditional on any history, including a history selected using past labels. It is the classical envelope minimax identity on the remaining support, not a new general theorem. Because the target masses remain fixed, an initial choice `h(i)=s(i)` continues to attain (18) after every removal. Its target-specific constants satisfy `c_n,t<=C(U_t-1)`; across all targets their maximum equals this common optimum.

For the complete strict-rank family `n=1,...,N` in equally sized prompt pools, initially

$$
C(U_0)=\sum_{r=1}^m\max_{n\le N}w_n(r)=Z_{m,N}\le H_N,
$$

by the rank-envelope theorem in [theory.md](theory.md). Removing items decreases `C(U)`.

Equation (18) minimizes the common worst inverse-probability range. It does not minimize every target's range separately, every confidence interval's width, variance, or stopping cost. For a single target, sampling proportional to its remaining mass attains the smaller constant `B_n,t-1`. The benefit and cost of covering several budgets with one shared audit are empirical questions beyond the range identity.

## 8. An explicit zero-observed-loss bound

Suppose a target has accumulated no weighted observed loss through time `t`, so every `S_n,j-1=0` and every `Y_n,j=0`. Consider its `gamma=1` upper component. For feasible candidate risks,

$$
M^{\mathrm{up}}_{1,n,t}(\mu)
=\prod_{j=1}^t\frac1{1-\mu/c_{n,j}}.
\tag{19}
$$

For an unresolved target the denominators are positive on the current feasible interval. Using `-log(1-x)>=x` and the mixture weight `pi_1=1/6`,

$$
E^{\mathrm{up}}_{n,t}(\mu)
\ge\frac16\exp\left(\mu\sum_{j=1}^t\frac1{c_{n,j}}\right).
$$

Thus the mathematical upper endpoint is at most

$$
U_{n,t}\le
\min\left\{B_{n,t},\
\frac{\log(12K/\delta)}{\sum_{j=1}^t1/c_{n,j}}\right\}.
\tag{20}
$$

A conservatively rounded numerical endpoint can exceed this expression by its numerical enclosure tolerance. If a target resolves, its exact zero value takes precedence. With an initial known contribution `S_n,0`, the same argument bounds the remaining risk after subtracting that contribution, provided all subsequently observed weighted losses are zero.

For fixed `h`, both `H_t` and `max_remaining a_n/h` are nonincreasing, so `c_n,t` is nonincreasing. Therefore (20) also gives

$$
U_{n,t}\le
\min\{B_{n,t},\ c_{n,1}\log(12K/\delta)/t\}.
\tag{21}
$$

For the rank envelope, `c_n,1<=Z_m,N<=H_N`. This shows an explicit logarithmic range cost for a zero-error certification path, with further improvement from the shrinking remaining population. It is not a distribution-free prediction that a real audit will observe no errors or stop after that many labels.

As a check, take a single uniform target over `M` binary-labeled items and observe an all-zero prefix of length `t`. At candidate risk `mu=j/M`, the `gamma=1` wealth is

$$
\prod_{\ell=0}^{t-1}\frac{M-\ell}{M-j-\ell}
=\frac{\binom Mt}{\binom{M-j}t},
$$

the reciprocal of the exact hypergeometric probability of observing no bad labels. Candidates incompatible with the prefix are already removed by the deterministic interval.

## 9. Limits and comparison requirements

The fixed six-point betting grid is valid but is not an assertion of asymptotically optimal intervals. Before census, very small candidate discrepancies can require smaller bets than `1/32`; a finite grid may then shrink slowly. The deterministic interval still collapses exactly at exhaustion. A different fixed grid or predictable betting strategy can remain valid, but its performance and comparisons should be specified separately.

Use the same target-specific normalization, bet grid, mixture weights, confidence allocation, feasible intervals, numerical precision, and interval convention for competing acquisition proposals. Otherwise interval construction and proposal quality are confounded. Fractional bets can be more informative than small fixed bets in some regimes; they do not uniformly dominate every other bet on every observation sequence.

The gold values must be fixed for target (1). If a noisy oracle is queried once per candidate, the result may be understood as inference for that realized annotation table. It does not certify latent annotation expectations. For example, with one item whose oracle is Bernoulli with mean `1/2`, observing zero and returning the census singleton `{0}` plainly does not cover the latent mean `1/2`. Repeated judgments, drifting labels, or a target based on expected oracle responses require a separate observation model.

The method permits adaptive stopping and adaptive choice among the declared targets. It does not permit silently adding targets, modifying the generator or ranking rule, extrapolating beyond the available pool size, or inferring deployment performance without additional assumptions. These restrictions concern the estimand, not the availability of more audit labels.
