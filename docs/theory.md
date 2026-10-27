# Auditing a finite family of best-of-n selectors

This note separates established ingredients from the result derived for this project. The rank-weight estimator is established prior work; normalized maximum likelihood gives the general minimax envelope construction; empirical Bernstein concentration is also standard. The specific result here is an exact total-variation decomposition and logarithmic bounds for the envelope of the finite-population best-of-n rank laws. This is a mathematical contribution candidate, not a claim that a literature search has established novelty.

## 1. Target, ordering, and assumptions

Fix a dataset of `P >= 1` prompt pools, each containing `m >= 1` candidates. Within each pool, rank candidates by their proxy score, with **rank 1 best** and rank `m` worst. Scores, rankings, and the pool are fixed before the audit. Resolve ties using a declared deterministic total order that is part of the policy. Let `y[i,r] in [0,1]` be the fixed gold loss of candidate `r` for prompt `i`; binary bad-event labels are the main example.

For a budget `n <= m`, the finite-pool policy samples a uniformly random subset of `n` distinct candidates and returns its best-ranked member. Its rank law is

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}},\qquad r=1,\ldots,m.
$$

We use `C(a,b)=0` when `b>a` or `b<0`. Candidate `r` wins exactly when it is included together with `n-1` of the `m-r` worse candidates. Consequently, the conditional finite-pool mean loss is

$$
R_n=\frac1P\sum_{i=1}^P\sum_{r=1}^m w_n(r)y_{i,r}.
\tag{1}
$$

All probability statements below condition on these fixed pools and labels. The only randomness is the stated audit sampling. They do not require independence of candidates or prompts in this fixed dataset, and they do not establish performance on new prompts or newly generated candidates.

The rank-weight identity and its use to reuse one pool for many budgets appear in [OpenAI, Measuring Goodhart's law](https://openai.com/index/measuring-goodharts-law/), which points to Appendix I of the [WebGPT paper](https://arxiv.org/abs/2112.09332). We do not present that estimator as new.

For interpretation outside this conditional target, additional assumptions are necessary. If prompt pools are independently drawn from the target prompt distribution, and each pool consists of `m` conditionally iid candidates from a fixed generator, then (1), before conditioning on the pools, is unbiased for fresh best-of-n mean loss. A separate generalization bound over prompt pools would still be needed. Budgets above `m`, different generators or scorers, adaptive scoring changes, and prompt distribution shifts are outside the present result.

## 2. A common audit distribution

Consider every integer budget `n=1,...,N`, where `1 <= N <= m`. Define

$$
s(r)=\max_{1\le n\le N}w_n(r),\qquad
Z_{m,N}=\sum_{r=1}^m s(r),\qquad
q^*(r)=\frac{s(r)}{Z_{m,N}}.
\tag{2}
$$

The inclusion of `n=1` guarantees `s(r)>=1/m`, so every rank has positive audit probability. For one audit draw, independently choose a prompt uniformly from the `P` pools and a rank from `q*`, then obtain that candidate's gold label. One label supplies the following importance-weighted observation for every budget:

$$
X_n=\frac{w_n(J)}{q^*(J)}y_{I,J}.
\tag{3}
$$

Then `E[X_n]=R_n`, `0<=X_n<=Z_{m,N}`, and

$$
\operatorname{Var}(X_n)
\le E[X_n^2]
\le Z_{m,N}R_n.
\tag{4}
$$

The stronger elementary bound is `Var(X_n) <= Z R_n - R_n^2`. The sample mean of (3) is the ordinary importance-sampling estimator; dividing by an estimated sum of weights would instead produce a different, generally biased estimator.

### Minimax range property — an established NML construction

For any rank distribution `q` positive wherever the target laws have support, set

$$
C(q)=\max_{n,r}\frac{w_n(r)}{q(r)}.
$$

Then

$$
\inf_q C(q)=Z_{m,N},
\qquad q^*=s/Z_{m,N}.
\tag{5}
$$

Indeed, `C(q) q(r)>=s(r)` for every rank, so summing gives `C(q)>=Z`. At `q*`, every ratio is at most `Z`, and some budget attains the maximum at each rank. Because `s(r)>0`, the minimizer is unique. The same conclusion holds if the proposal may assign arbitrary probabilities to prompt-rank pairs: the target mass is `w_n(r)/P`, whose envelope is `s(r)/P`.

Equation (5) is the classical normalized maximum likelihood, or Shtarkov-envelope, minimax identity applied to rank laws. A primary account is [Watanabe and Roos (2015), Section 2, equation (1)](https://www.jmlr.org/papers/volume16/watanabe15a/watanabe15a.pdf). Related sensitivity sampling also samples proportional to a pointwise envelope; see [Langberg and Schulman (2010)](https://www.openu.ac.il/home/mikel/papers/sampling_35_full.pdf). The claim in (5) concerns the largest importance weight. It is not a claim of minimax variance or optimal label complexity among all adaptive estimators.

## 3. Exact finite-pool envelope theorem

Write

$$
\operatorname{TV}(p,q)=\frac12\sum_r|p(r)-q(r)|,
\qquad H_N=\sum_{n=1}^N\frac1n.
$$

**Theorem.** For every `m>=N>=1`,

$$
Z_{m,N}
=1+\sum_{n=2}^N\operatorname{TV}(w_n,w_{n-1}),
\tag{6}
$$

and

$$
1+\sum_{n=2}^N\frac{(n-1)^{n-1}}{n^n}
\ \le\ Z_{m,N}\ \le\ H_N.
\tag{7}
$$

In particular,

$$
1+\frac{H_N-1}{e}\le Z_{m,N}\le H_N.
\tag{8}
$$

Thus the optimal worst importance weight is `Theta(log N)` uniformly over all pool sizes `m>=N`. For `N=1`, all empty sums vanish and `Z=1`.

### Proof of the envelope–TV identity

For ranks where both weights are positive and `n<m`,

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{n+1}{n}\frac{m-r-n+1}{m-n}.
$$

This ratio is at least one exactly when

$$
n\le\frac{m-r+1}{r}.
$$

The sequence `n -> w_n(r)` therefore increases and then decreases, with possible equality at the peak; weights beyond its support are zero. An upper maximizing budget has the closed form

$$
n_*(r)=\min\left\{N,\left\lfloor\frac{m+1}{r}\right\rfloor\right\}.
\tag{9}
$$

If `(m+1)/r` is an integer, the adjacent feasible budget immediately below that integer can tie. Formula (9) remains a maximizer, including the endpoint `r=1` after capping by `N`.

For a unimodal sequence, adding its `n`th entry to the previous running maximum increases that maximum by exactly `[w_n(r)-w_{n-1}(r)]_+`. Sum this statement over ranks and then over `n=2,...,N`. The initial envelope is `w_1`, of mass one. Since each `w_n` has total mass one, the sum of the positive differences equals total variation. This proves (6).

An alternative exact computation of each increment follows from the one-crossing property

$$
w_n(r)\ge w_{n-1}(r)
\quad\Longleftrightarrow\quad
r\le\frac{m+1}{n}
$$

on their common support, with zero-support endpoints handled directly. Put `k_n=floor((m+1)/n)` for `n>=2`. The positive mass difference is

$$
\operatorname{TV}(w_n,w_{n-1})
=\frac{\binom{m-k_n}{n-1}}{\binom{m}{n-1}}
-\frac{\binom{m-k_n}{n}}{\binom{m}{n}}.
\tag{10}
$$

At an integer crossing, including its zero difference does not change this expression.

### Proof of the harmonic upper bound

Draw a uniformly random `n`-subset and delete one uniformly random member. The remaining set is a uniformly random `(n-1)`-subset. Under this coupling their winners differ only when the deleted member was the best of the original subset, which occurs with probability `1/n`. The coupling inequality gives

$$
\operatorname{TV}(w_n,w_{n-1})\le\frac1n.
$$

Insert this into (6) to obtain `Z<=H_N`. This argument is entirely finite-population and does not approximate sampling without replacement by independent sampling.

### Proof of the lower bound by a common beta kernel

For descending rank `r`, define the probability density

$$
K_r(u)=\frac{m!}{(m-r)!(r-1)!}
u^{m-r}(1-u)^{r-1},\qquad 0<u<1.
\tag{11}
$$

This is `Beta(m-r+1,r)`, the value distribution of the `r`th largest of `m` iid uniforms. Crucially, the kernel is the same for every budget. It maps each finite rank law exactly to the density of the largest of `n` iid uniforms:

$$
\sum_{r=1}^m w_n(r)K_r(u)=n u^{n-1}=:f_n(u).
\tag{12}
$$

One direct algebraic verification avoids any conditioning ambiguity. For `r<=m-n+1`, the coefficient in the summand satisfies

$$
\frac{\binom{m-r}{n-1}}{\binom{m}{n}}
\frac{m!}{(m-r)!(r-1)!}
=n\binom{m-n}{r-1}.
$$

Factor `n u^(n-1)` from the sum and apply the binomial theorem to the remaining powers of `u` and `1-u`; all terms with `r>m-n+1` are zero. This proves (12).


Total variation contracts under a common probability kernel:

$$
\begin{aligned}
\operatorname{TV}(f_n,f_{n-1})
&=\frac12\int_0^1\left|\sum_r(w_n(r)-w_{n-1}(r))K_r(u)\right|du\\
&\le\frac12\sum_r|w_n(r)-w_{n-1}(r)|\int_0^1 K_r(u)du\\
&=\operatorname{TV}(w_n,w_{n-1}).
\end{aligned}
$$

For `n>=2`, the two continuous densities cross at `a=(n-1)/n`; integrating their positive difference on `[a,1]` gives

$$
\operatorname{TV}(f_n,f_{n-1})
=\int_a^1\bigl(nu^{n-1}-(n-1)u^{n-2}\bigr)du
=\frac{(n-1)^{n-1}}{n^n}.
$$

Combine this with (6) to obtain (7). Finally, `(1-1/n)^(n-1)>=e^(-1)` yields (8).

### The fixed-budget, large-pool limit

For each fixed `N`, as `m -> infinity`, the finite-rank laws converge as Riemann sums to `f_n(u)=n u^(n-1)`. Because this is a finite family,

$$
\lim_{m\to\infty}Z_{m,N}
=\int_0^1\max_{1\le n\le N}n u^{n-1}du
=1+\sum_{n=2}^N\frac{(n-1)^{n-1}}{n^n}.
\tag{13}
$$

The last equality also follows from the same unimodality and TV decomposition for the continuous densities. The sum in (13) is `(log N)/e + O(1)` as `N -> infinity`, since its `n`th term is `1/(en)+O(1/n^2)`. Equation (13) takes `m -> infinity` with `N` fixed; we do not use it to assert an unproved joint-limit constant when `N` grows with `m`. The nonasymptotic inequalities (7) hold in that regime without qualification.

## 4. Fixed-sample simultaneous confidence bounds

Take `b>=2` independent audit draws `(I_t,J_t)` with replacement using the fixed proposal `Uniform(P) x q*`. Let

$$
\widehat R_n=\frac1b\sum_{t=1}^b X_{t,n},\qquad
\widehat V_n=\frac1{b-1}\sum_{t=1}^b(X_{t,n}-\widehat R_n)^2.
$$

For a confidence level `0<delta<1`, put

$$
\ell=\log\frac{4N}{\delta},\qquad
\epsilon_n=\sqrt{\frac{2\widehat V_n\ell}{b}}
+\frac{7Z_{m,N}\ell}{3(b-1)}.
\tag{14}
$$

Then, with probability at least `1-delta`, simultaneously for all `n=1,...,N`,

$$
R_n\in
\left[\max\{0,\widehat R_n-\epsilon_n\},
\min\{1,\widehat R_n+\epsilon_n\}\right].
\tag{15}
$$

The underlying one-sided empirical Bernstein inequality is Theorem 4 of [Maurer and Pontil (2009), Empirical Bernstein Bounds and Sample Variance Penalization](https://www.cs.mcgill.ca/~colt2009/papers/012.pdf). For iid observations in `[0,Z]`, it gives the radius in (14) with `log(2/eta)` for one tail at failure probability `eta`. Apply it to `X/Z` and to `1-X/Z`, and set `eta=delta/(2N)` for the `2N` tails. This explains the `log(4N/delta)` and both constants in (14). The observations for different budgets can be dependent; the union bound does not require independence between budgets.

If only upper confidence bounds are needed, use `ell=log(2N/delta)` and omit the lower-bound guarantee. This allocates `delta/N` to each of the `N` upper tails.

On the simultaneous event, any audit-dependent selected budget whose upper bound is at most a threshold `alpha` has `R_n<=alpha`. In particular one may return the largest certified budget. If none is certified, report that outcome; `n=1` is not automatically safe. A largest certified budget need not be the largest truly safe budget, because conservative bounds can fail to certify a safe one.

The sample size `b` in this statement is fixed in advance. It does not license repeatedly inspecting fixed-time intervals and stopping at the first favorable result. A simple valid extension at predetermined checkpoints `b_t` uses failure budgets `delta_t=delta/[t(t+1)]` in (14), whose sum is `delta`; a union bound then permits stopping at those checkpoints. Such a procedure retains the additional checkpoint multiplicity cost.

### Draws are different from unique labels

The iid sample size `b` counts random **draws**, including repeated prompt-rank pairs. A deterministic gold label can be cached, so the number of distinct gold labels acquired is at most `b`. Repeated draws still appear in the sample mean and variance. Conditional on the fixed gold table, a function of independently drawn indices remains iid even when some indices coincide.

Sampling until a prescribed number of distinct labels has been acquired makes the number of draws random. Dropping duplicates, forcing sampling without replacement, or using adaptively changed rank probabilities also changes the sampling law. Formula (14) must not be applied to such a modified design without a corresponding justification. Cached noisy annotations target that cached table; they do not by themselves certify an unobserved error-free ground truth.

## 5. What the design improves, and what it does not

Uniform rank sampling has largest importance weight

$$
\max_{n,r}m w_n(r)=N,
$$

attained by the best rank at budget `N`. The envelope proposal replaces this by `Z<=H_N`. This is an exact comparison of range constants, not a universal empirical claim about every loss table or every audit budget.

For an illustrative variance comparison, let `N=m` and make the top candidate bad in every prompt. At policy budget `m`, the target risk is one. Uniform rank auditing gives an observation equal to `m` with probability `1/m` and zero otherwise, hence variance `m-1`. Envelope auditing gives an observation equal to `Z` with probability `1/Z`, hence variance `Z-1<=H_m-1`. This example isolates the effect of rank mismatch. Other label patterns can favor a different proposal.

Useful comparisons include a mixture over geometrically spaced budgets: it can also achieve logarithmic range scaling, so uniform sampling alone is an insufficient baseline for judging practical improvements. Learned or adaptive variance-minimizing proposals can improve on the envelope when reliable loss structure is available, but require their own estimation and concentration analysis.

Risk need not be monotone in the selection budget. For example, one pool with descending-rank losses `(0,1,0,0)` and `m=4` has risks `(1/4,1/3,1/4,0)` for budgets `1,2,3,4`. Thus a policy at budget 4 can be safe at a threshold that budget 2 violates. The guarantee concerns whichever budgets are individually certified; it does not certify every smaller budget unless those also pass.

## 6. Optional sharp bounds from partially observed labels

Let `A` be any set of audited prompt-rank pairs, selected by any procedure. With no assumptions on unobserved labels beyond `0<=y<=1`, define

$$
L_n=\frac1P\sum_{(i,r)\in A}w_n(r)y_{i,r},\qquad
U_n=L_n+\frac1P\sum_{(i,r)\notin A}w_n(r).
\tag{16}
$$

Then `L_n<=R_n<=U_n` holds deterministically and simultaneously for every budget. Each bound is sharp: setting every unaudited label to zero attains all lower bounds, and setting every unaudited label to one attains all upper bounds. These are marginal ranges; intermediate combinations of coordinates need not be jointly attainable because all budgets share the same missing labels.

The width is the unaudited policy mass. For one fixed budget and equal label costs, auditing the remaining pairs with largest `w_n(r)/P` minimizes the residual worst-case width after a fixed number of new labels. This does not establish optimality for simultaneous widths, stochastic estimation, or the number of labels needed to certify a particular threshold. For multiple budgets, (2) solves the stated minimax importance-weight objective instead.

The deterministic intervals can be intersected with valid statistical intervals. Their validity survives arbitrary audit adaptivity, but they can remain wide when much policy mass is unlabeled. Neither a missing-label interval nor a conditional sampling confidence interval supplies a new-prompt population guarantee.

## 7. Scope checklist

- The policy chooses a uniform subset without replacement from each fixed pool, then its best member under a declared total order.
- The supported budgets are `1,...,N` with `N<=m`; every target and proposal uses the same frozen ordering.
- The gold table is fixed and bounded in `[0,1]`; binary labels are a special case.
- The statistical audit draws are independent with replacement, using a proposal fixed before those draws.
- Simultaneous selection over budgets is supported. Optional stopping, adapting the scorer, changing proposals, and deduplicating draws need separate treatment.
- The primary target is the conditional finite-pool mean in (1). No independence of rows is needed for that target, and no deployment or population guarantee is implicit.

If the intended policy breaks score ties uniformly at random instead of using the declared total order, its weights must reflect that policy. For a tied block occupying descending ranks `a,...,b`, each member has weight

$$
\frac{\binom{m-a+1}{n}-\binom{m-b}{n}}
{(b-a+1)\binom{m}{n}}.
$$

This follows by counting subsets whose best score lies in the block and using symmetry among its members. Averaging strict-rank weights within tie blocks recovers the formula. The envelope for these averaged laws cannot exceed the strict-rank envelope, by `max_n average <= average max_n`; however, equations (6), (9), and (10) were proved for strict ranks and should not be silently transferred to a different tied-rank family.
