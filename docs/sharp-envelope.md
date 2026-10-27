# A sharp finite-pool bridge for the best-of-n envelope

[Fitas (2026, v2), Section 2.4, equation (8), and Supplement S2](https://arxiv.org/html/2608.21496v2) already gives the continuous-rank integer-budget normalizer and its `1/e` logarithmic coefficient. This note proves a uniform finite-without-replacement comparison and a second-order profile. It makes no general novelty claim.

The earlier [related-work entry](related-work.md) recorded an abstract-only comparison. This explicit attribution supersedes that limited comparison for the continuous envelope. Historical v0.1/v0.2 source files and saved results are unchanged.

## Result

Use the notation of [theory.md](theory.md). Set

$$
\ell_n=\frac{(n-1)^{n-1}}{n^n},\qquad
L_N=1+\sum_{n=2}^N\ell_n.
$$

`L_N` is the continuous-rank, integer-budget envelope normalizer. For every `m>=N>=1`,

$$
\boxed{\quad
0\le Z_{m,N}-L_N\le\frac{N-L_N}{m+1}
\le\frac{N-1}{m+1}<1.
\quad}
\tag{A}
$$

The middle upper bound is attained when `m=N=2`. In particular,

$$
Z_{m,N}=\frac{\log N}{e}+O(1)
$$

uniformly over `m>=N`, and the finite-pool correction tends to zero whenever `N/m -> 0`. This establishes the leading coefficient throughout the joint regime; the fixed-`N`, large-`m` limit alone would not establish it.

There is also a second-order profile. Define, for `0<x<=1`,

$$
k(x)=\lfloor1/x\rfloor,\qquad
g(x)=k(x)(1-x)^{k(x)-1}-\frac1{ex},
\qquad
G(\rho)=\int_0^\rho g(x)\,dx.
\tag{B}
$$

At `x=1`, the first term is `1`, using the empty-product convention. Values at the countable breakpoints can equivalently be assigned by either neighboring formula. The proof below shows that `0<=g<=1` almost everywhere, so the integral is well defined at zero. Then

$$
\boxed{\quad
\sup_{1\le N\le m}
\left|Z_{m,N}-L_N-G(N/m)\right|\longrightarrow0
\quad (m\to\infty).
\quad}
\tag{C}
$$

Consequently, if `N -> infinity` and `N/m -> rho in [0,1]`,

$$
Z_{m,N}=\frac{\log N}{e}+c_0+G(\rho)+o(1),
\qquad
c_0=\lim_{N\to\infty}\left(L_N-\frac{\log N}{e}\right).
\tag{D}
$$

The statements (A)-(D) are derived below; no rate is asserted for the uniform remainder in (C).

## Proof of the finite bound

The existing exact decomposition is

$$
Z_{m,N}=1+\sum_{n=2}^N v_{m,n},
\qquad
v_{m,n}=\operatorname{TV}(w_n,w_{n-1}).
$$

Its beta-kernel lower bound and deletion-coupling upper bound give

$$
\ell_n\le v_{m,n}\le1/n.
\tag{1}
$$

For `2<=n<=m`, put `k=floor((m+1)/n)`. The exact crossing formula can be written as

$$
\begin{aligned}
v_{m,n}
&=\frac{\binom{m-k}{n-1}}{\binom m{n-1}}
-\frac{\binom{m-k}n}{\binom mn}\\
&=\frac{k}{m-n+1}
\prod_{j=0}^{n-2}\left(1-\frac{k}{m-j}\right).
\end{aligned}
\tag{2}
$$

All factors are nonnegative. Replacing `m-j` in each factor by `m` increases the product. With `x=k/m`,

$$
\begin{aligned}
v_{m,n}
&\le\frac{k}{m-n+1}(1-k/m)^{n-1}\\
&=\frac{m}{m-n+1}x(1-x)^{n-1}\\
&\le\frac{m}{m-n+1}\ell_n.
\end{aligned}
\tag{3}
$$

The last inequality maximizes `x(1-x)^(n-1)` over `[0,1]`; its maximizer is `x=1/n` and maximum is `ell_n`.

Multiply (3) by `m-n+1`, and multiply the coupling bound in (1) by `n`. Adding gives

$$
(m+1)v_{m,n}\le m\ell_n+1,
$$

or the exact increment bound

$$
\boxed{\quad
0\le v_{m,n}-\ell_n\le\frac{1-\ell_n}{m+1}.
\quad}
\tag{4}
$$

Sum (4) over `n=2,...,N`. Since `sum ell_n=L_N-1`, its upper numerator sums to `N-L_N`. This proves (A), including `N=1` by the empty-sum convention. For `m=n=2`, the product maximization and coupling inequalities are both equalities, establishing the stated attained case.

The expansion `ell_n=1/(en)+O(1/n^2)` establishes existence of `c_0` and `L_N=(log N)/e+O(1)`. Combined with (A), this proves the uniform leading-order conclusion. One exact expression for the constant is

$$
c_0=1+\frac{\gamma_{\mathrm E}-1}{e}
+\sum_{n=2}^{\infty}\left(\ell_n-\frac1{en}\right),
\tag{5}
$$

where `gamma_E` is Euler's constant.

## Proof of the joint second-order profile

An alternative form of (2), obtained by writing its binomial ratio as a product over the `k` excluded ranks and cancelling the first numerator, is

$$
m v_{m,n}
=k\prod_{j=1}^{k-1}
\frac{m-n+1-j}{m-j}.
\tag{6}
$$

For fixed `x in (0,1)` away from reciprocal-integer breakpoints, choose `n_m=ceil(mx)`. Then `n_m/m -> x` and `k_m=floor((m+1)/n_m)` is eventually `floor(1/x)`. Equation (6) gives

$$
m v_{m,n_m}\longrightarrow k(x)(1-x)^{k(x)-1},
\qquad
m\ell_{n_m}\longrightarrow\frac1{ex}.
\tag{7}
$$

Set the increment for `n=1` to zero and define a step function on `(0,1]` by

$$
f_m(x)=m\big(v_{m,\lceil mx\rceil}-\ell_{\lceil mx\rceil}\big),
$$

with that zero convention on its first cell. Equation (4) gives `0<=f_m<1`. Equation (7) gives `f_m -> g` almost everywhere. Dominated convergence therefore gives

$$
\|f_m-g\|_{L^1(0,1)}\longrightarrow0.
\tag{8}
$$

Moreover, for every integer `N<=m`,

$$
Z_{m,N}-L_N=\int_0^{N/m}f_m(x)\,dx.
$$

Thus the absolute difference in (C) is at most the single quantity in (8), independently of `N`. This proves the claimed uniform convergence. The bounded integrand makes `G` continuous; inserting `N/m -> rho` and (5) proves (D), including `rho=0`.

## Closed forms for the profile and the diagonal constant

On the interval `(1/(j+1),1/j)`, the first term of `g` is `j(1-x)^(j-1)`. Therefore

$$
\int_{1/(J+1)}^1 g(x)\,dx
=\left(\frac J{J+1}\right)^J+L_J-1
-\frac{\log(J+1)}e.
$$

Letting `J -> infinity` yields the exact relation

$$
\boxed{\quad G(1)=c_0-1+1/e.\quad}
\tag{9}
$$

More generally, for `0<rho<=1` and `k=floor(1/rho)`,

$$
\boxed{\quad
G(\rho)=c_0+1/e-L_k-(1-\rho)^k-\frac{\log\rho}{e}.
\quad}
\tag{10}
$$

At reciprocal breakpoints either neighboring interval formula agrees. In particular,

$$
Z_{m,m}=\frac{\log m}e+2c_0-1+1/e+o(1).
\tag{11}
$$

Floating-point evaluations give approximately

$$
c_0\approx0.993152990876,\qquad
G(1)\approx0.361032432047,\qquad
2c_0-1+1/e\approx1.354185422923.
$$

These displayed decimals are computational approximations, not interval-certified decimal enclosures. Equations (5), (9), and (11) define the constants exactly.

## Computational checks

The added [exact-arithmetic tests](../tests/test_sharp_envelope.py) compare direct rational rank laws with the adjacent-TV formula, check every budget cap for `m<=60`, verify the attained `(2,2)` case, and compare the frozen numerical envelope against independent exact laws. All three tests pass. The standalone [reproduction script](../experiments/check_sharp_envelope.py) uses `fractions.Fraction` to check every pair `2<=n<=m<=200`: 19,900 exact cases. Each case verifies the binomial-difference expression, `(m-n+1)v<=m ell`, `n v<=1`, and the strengthened increment inequality (4). No floating-point tolerance is used for those inequalities. The [saved JSON](../results/theory/sharp_envelope.json) records source hashes and all table values; a separate rerun reproduced it byte for byte.

The existing, unmodified `goodhart_audit.core.full_envelope` supplied an independent floating-point evaluation of `Z`. Continuous sums used `math.fsum(exp((n-1)*log1p(-1/n))/n)`. Selected diagonal results were:

| `m=N` | `Z_m,m` | `Z_m,m-L_m` | `Z_m,m-log(m)/e` |
|---:|---:|---:|---:|
| 10 | 2.197222222222 | 0.356918985337 | 1.350148504962 |
| 100 | 3.049961981291 | 0.362660789491 | 1.355814546770 |
| 1,000 | 3.895779096448 | 0.361404946127 | 1.354557944667 |
| 10,000 | 4.742538327859 | 0.361090467866 | 1.354243458818 |
| 100,000 | 5.589561964632 | 0.361040387454 | 1.354193378331 |
| 1,000,000 | 6.436628732023 | 0.361033437586 | 1.354186428461 |

The finite correction need not lie below its diagonal limit: the `m=100` row is a counterexample to that stronger assertion. Bound (A) remains valid.

For `m=100,000`, the second-order profile comparison was:

| `N/m` | `Z_m,N-L_N` | `G(N/m)` | Difference |
|---:|---:|---:|---:|
| 0.10 | 0.019131140529 | 0.019124472322 | 0.000006668207 |
| 0.25 | 0.051005930689 | 0.050998478767 | 0.000007451922 |
| 0.50 | 0.116034984886 | 0.116027029481 | 0.000007955405 |
| 1.00 | 0.361040387454 | 0.361032432047 | 0.000007955407 |

These checks support the algebra and limiting formula; the proof, rather than the finite sweep, establishes the universal statements. The continuous coefficient, envelope construction, and any general auditing method require their existing attributions. A separate prior-art assessment is needed before assigning novelty to this finite-without-replacement comparison or its second-order profile.
