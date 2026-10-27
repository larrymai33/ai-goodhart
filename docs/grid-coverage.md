# Coverage between audited best-of-n budgets

Supporting mathematical note, 27 October 2026. A certificate for a declared
budget grid need not certify omitted budgets. This note gives an exact
deterministic extension rule, a sharp dyadic factor, and two counterexamples
at the original study parameters. It does not change the seven-budget
decision or its label-cost benchmarks in the
[all-grid theorem](all-grid-minimax-theorem.md).

The convexity principle has established antecedents, identified below. The
proof and checks were developed with substantial Codex assistance and have
not received independent human review. These are constructed tables, not
observations of model behavior; see the [provenance disclosure](provenance.md).

## 1. Fixed experiment and normalized convexity

There are $P\ge1$ prompt pools, each with $m\ge1$ items in a fixed total rank
order, best first. Losses $y_{p,r}\in[0,1]$ are fixed. Write

$$
\bar y_r=\frac1P\sum_p y_{p,r},\qquad
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},\qquad
R_n=\sum_{r=1}^m w_n(r)\bar y_r,
\quad 1\le n\le m.
$$

The selector draws a uniform $n$-subset without replacement and returns its
best-ranked item. Impossible binomial choices are zero. No monotonicity of
loss with rank is assumed.

Put $f_n=R_n/n$. The factorial identity

$$
\frac{w_n(r)}n
=\frac{\binom{m-n}{r-1}}{m\binom{m-1}{r-1}}
\tag{1}
$$

holds also at zero weights. For $1\le n\le m-2$, Pascal's identity gives

$$
\begin{aligned}
f_n-2f_{n+1}+f_{n+2}
&=\sum_{r=3}^m
\frac{\bar y_r\binom{m-n-2}{r-3}}
     {m\binom{m-1}{r-1}}\\
&\ge0.
\end{aligned}
\tag{2}
$$

The rank-one and rank-two terms have zero second difference. Thus $f_n$ is
discretely convex. For $m<3$ the second-difference claim is vacuous. This
argument uses nonnegative losses; signed differences between two loss
tables do not automatically satisfy it.

## 2. Exact endpoint transfer

For integers $1\le a<n<b\le m$, convexity implies the chord bound

$$
f_n\le\frac{b-n}{b-a}f_a+\frac{n-a}{b-a}f_b.
$$

Indeed, the nondecreasing forward differences in (2) make the average slope
from $a$ to $n$ no larger than the average slope from $n$ to $b$; rearranging
gives this inequality. Therefore

$$
\boxed{R_n\le
\frac{n(b-n)}{a(b-a)}R_a+
\frac{n(n-a)}{b(b-a)}R_b.}
\tag{3}
$$

The formula also holds at $n=a,b$ by equality. Both coefficients are
nonnegative, so upper bounds $R_a\le U_a$, $R_b\le U_b$ can replace the
endpoint risks. The resulting upper bound may be clamped at one.

If both endpoint risks are at most $s$, (3) becomes

$$
R_n\le s\frac{n(a+b-n)}{ab}\le s\rho(a,b),\qquad
\rho(a,b)=\frac{\lfloor(a+b)^2/4\rfloor}{ab}.
\tag{4}
$$

The integer maximum is exact: $n(a+b-n)$ is maximized at an integer nearest
$(a+b)/2$. In particular, adjacent endpoints have $\rho(a,a+1)=1$.
The continuous bound

$$
\rho(a,b)\le\frac{(a+b)^2}{4ab}
=1+\frac{(b-a)^2}{4ab}
\tag{5}
$$

shows that the excess factor is quadratic in a small relative grid gap.

For a grid $1=g_1<\cdots<g_J=m$, the premises $R_{g_j}\le s$ imply
$R_n\le\tau$ for every integer budget whenever

$$
s\rho(g_j,g_{j+1})\le\tau\quad(1\le j<J).
\tag{6}
$$

These endpoint premises are assumptions or certified claims, not labels
known for free. A globally $\delta$-valid certificate for all endpoint
premises transfers with the same error probability: any table violating
the full-family conclusion must violate an endpoint premise. This is a
deterministic implication and requires no additional union bound.

It does **not** by itself construct a boundary-complete auditor for the
full threshold $\tau$. A full-family-safe table may fail the stricter
endpoint threshold $s$. An auditor claiming completion on every such
table needs its own completion argument, such as a charged census fallback.

## 3. Sharp dyadic factor and the original-instance gap

Let $m=2^d$, $d\ge2$, and declare $\mathcal K=\{1,2,4,\ldots,m\}$.
Every successive ratio is two, so (5) gives

$$
\max_{1\le n\le m}R_n\le\frac98\max_{n\in\mathcal K}R_n.
\tag{7}
$$

The constant is uniformly sharp for this family. Choose
$0<s\le m/[2(m-1)]$ and use the same fractional losses in every prompt:

$$
y_{p,1}=s,\qquad y_{p,2}=\frac{2s(m-1)}m,\qquad
y_{p,r}=0\quad(r\ge3).
$$

These losses lie in $[0,1]$, and direct substitution gives

$$
R_n=s\frac{n(3m-2n)}{m^2}.
\tag{8}
$$

This quadratic increases up to $n=3m/4$. All dyadic budgets below $m$
are at most $m/2$, and $R_{m/2}=R_m=s$. Its full maximum is
$R_{3m/4}=9s/8$, proving sharpness. This does not assert that every
individual grid interval attains its chord bound.

At the original $P=32$, $m=64$, $\tau=1/10$, and $s=3/32=\tau-1/160$,
the fractional table therefore has

$$
\max_{n\in\{1,2,4,8,16,32,64\}}R_n=\frac3{32},\qquad
R_{48}=\frac{27}{256}=0.10546875>\frac1{10}.
\tag{9}
$$

There is also a binary witness with the same pool dimensions. Put loss one
at rank one in three prompts and at rank two in five prompts, and put zero
in every other cell. The two prompt subsets may overlap. Then
$\bar y_1=3/32$, $\bar y_2=5/32$, and

$$
R_n=\frac{n(509-5n)}{129024}.
\tag{10}
$$

On the seven dyadic budgets the maximum is $R_{64}=3/32$; for budgets at
most 32 the quadratic is increasing and $R_{32}=349/4032<3/32$.
The real-valued maximizer is $509/10$, so the unique integer maximizer is
51, with

$$
R_{51}=\frac{2159}{21504}>\frac1{10}.
\tag{11}
$$

Thus the omitted-budget failure occurs even with binary labels. Neither
witness contradicts the existing theorem, which certifies only the
originally declared family.

## 4. A smallest grid under the sufficient interval rule

Fix $0\le s\le\tau\le1$ and require the grid to include 1 and $m$.
Starting at $a=1$, repeatedly take the largest integer $b\le m$ with
$b>a$ and $s\rho(a,b)\le\tau$, then continue from $b$. An adjacent
endpoint always qualifies, so the procedure terminates. For $m=1$ return
the singleton grid.

This greedy rule minimizes the number of endpoints **among grids satisfying
(6)**. To prove it, set $v_n(a,b)=n(a+b-n)/(ab)$. For a fixed admissible
$n$, this quantity decreases as $a$ increases and increases as $b$
increases. These statements follow directly from

$$
v_n(a,b)=\frac nb+\frac{n(b-n)}{ab}
=\frac na-\frac{n(n-a)}{ab}.
$$

Increasing $a$ also shrinks the integer maximization domain; increasing
$b$ enlarges it. Thus $\rho$ decreases with its left endpoint and
increases with its right endpoint. In particular, an admissible interval
remains admissible when its left endpoint moves rightward inside it.

Compare the greedy grid with any competing admissible grid. Both start at
1. Inductively suppose the greedy endpoint is at least the competing
endpoint. If the competitor's next endpoint is already behind the greedy
one, domination persists. Otherwise its next endpoint is reachable from
the greedy one by the preceding monotonicity, and the greedy rule reaches
at least that far. Hence the greedy grid reaches $m$ in no more intervals.
This proves the stated minimality; it does not prove optimality among all
possible inference rules for actual risks.

For $s=3/32$ and $\tau=1/10$, condition (6) is $\rho\le16/15$.
The continuous ratio condition $b/a\le5/3$ is sufficient by (5), while
the exact integer rule allows some larger ratios. At $m=64$ the greedy
grid is

$$
\boxed{\{1,2,3,5,8,13,21,35,58,64\}.}
\tag{12}
$$

It has ten points and is minimal under (6). If $s=0$, the two endpoints
suffice for this rule when $m>1$; if $s=\tau>0$, only adjacent intervals
qualify and every integer is retained.

## 5. Predecessors, helpers, and limits

[Myatt and Ronayne, *Decreasing Returns to Sampling Without Replacement*,
Proposition 1](https://rationality-and-competition.de/wp-content/uploads/discussion_paper/555.pdf)
establish discrete convexity of the expected sample minimum. There is a
direct correspondence here: set $x_j=\sum_{r=1}^j\bar y_r$ for
$1\le j\le m-1$, and sample $n-1$ ranks without replacement from these
$m-1$ ordered values. For $n\ge2$, summation by parts gives
$\mathbb E[x_{\min}]=mR_n/n$. Their convexity result therefore applies
to the normalized risks away from the $n=1$ boundary, which (2) also
covers. The underlying convexity is not claimed as new. The cited working
paper appeared in November 2025; the
[published article](https://doi.org/10.1016/j.econlet.2026.112956)
appeared in 2026.

[Fitas, *The geometry of AI validation*, Supplement S5](https://arxiv.org/html/2608.21496v2)
constructs geometric budget grids and extends simultaneous bounds using a
total-variation modulus for iid winner kernels. That method controls a
change from one representative to a neighboring budget. Equations
(3)--(5) instead combine two endpoint upper bounds and use nonnegative
losses to obtain a quadratic relative-gap factor for the finite
without-replacement decision. This comparison distinguishes these
particular bounds; it does not establish scientific priority for the
application or a new general interpolation principle.

The exact helpers in [coverage.py](../goodhart_audit/coverage.py) are:

```python
interval_factor(a, b)
interpolate_upper(a, b, n, left_upper, right_upper)
covering_grid(m, certified_level, target_level)
```

They implement deterministic rational arithmetic, not a statistical audit.
Inputs use integers or `Fraction` values as appropriate; booleans, floats,
and out-of-domain inputs are rejected. Endpoint bounds lie in $[0,1]$,
interpolation requires $1\le a\le n\le b$ with $a<b$, and grid levels
satisfy $0\le s\le\tau\le1$. The implementation caps pool size at
100,000 to bound grid output length. Finite implementation checks are
documented separately in the [coverage report](grid-coverage-report.md);
the universal mathematical claims rest on the proofs above.

No new labels, population guarantees, or model evidence follow from the
transfer. It assumes the same frozen candidate pools, fixed ranking,
without-replacement selector, and loss definition as the endpoint claims.
It neither improves the original seven-budget label-cost result nor
authorizes changing the audited generator, scorer, or prompt population.
