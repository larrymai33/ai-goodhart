# Exact probabilities for the zero-only workflow

The companion workflow implements a conservative rational version of the classical NEGEXP audit. Its probabilities are exact rational numbers sampled with uniform-integer rejection. They preserve the validity and factor-160 cost guarantee in the [finite-pool cost theorem](zero-cost-theorem.md), despite generally differing from the ideal exponential probabilities. This is an implementation argument for an established design and the stated special-family theorem, not a new algorithm or a model evaluation.

The implementation is [zero_math.py](../goodhart_audit/zero_math.py). It uses only the Python standard library and does not change the earlier theorem checker, source-pinned proof, or saved evidence.

## Contract and notation

There are P equal pools of m ranked candidates, with D=P*m distinct items. The declared budget family contains every power of four through its maximum, including budget 1. The threshold and error probability are exact fractions satisfying

$$
0<\tau\le\frac18,\qquad 0<\delta\le\frac14.
$$

Let a_n(i) be the finite-pool winner mass, s_i=max_n a_n(i), and L=log(1/delta). Each prompt has equal mass 1/P. The exact rank law is

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom mn},
\qquad a_n(p,r)=w_n(r)/P.
$$

The program computes these rational laws by their adjacent-rank recurrence. No labels enter the computation. The only decision is a certificate for the entire declared family, issued when every selected label is exactly zero. Positive or missing annotations do not produce that certificate. Cost is evaluated on the all-zero table; validity must hold for every fixed loss table in [0,1].

## An exact log enclosure

Use integer comparisons to write

$$
1/\delta=2^k y,\qquad 1\le y<2.
$$

For 0<=z<=1/3 and an integer J>=1, define

$$
S_J(z)=2\sum_{j=0}^{J-1}\frac{z^{2j+1}}{2j+1},
\qquad
R_J(z)=\frac{2z^{2J+1}}{(2J+1)(1-z^2)}.
$$

The positive atanh series gives

$$
S_J(z)\le\log\frac{1+z}{1-z}\le S_J(z)+R_J(z).
$$

The remainder bound follows by replacing every later odd denominator with 2J+1 and summing a geometric series. For log(2), use z=1/3. For log(y), use z=(y-1)/(y+1), which lies in [0,1/3). Add k times the first interval to the second interval. All endpoints and remainders are rational.

Finally, put B=4J+16 and round the lower endpoint down and the upper endpoint up to multiples of 2^(-B). Call the resulting endpoints L_lo and L_hi. Outward rounding preserves

$$
L_{\mathrm{lo}}\le L\le L_{\mathrm{hi}}.
$$

It also prevents a long input denominator from propagating directly into every inclusion probability. The record stores the final endpoints, J, and B. There is no floating-point logarithm or assumed numerical tolerance.

## Rational inclusion and the checked sandwich

For x>=0, define

$$
P_5(x)=x-\frac{x^2}{2}+\frac{x^3}{6}-\frac{x^4}{24}+\frac{x^5}{120},
\qquad U_5(x)=\min\{1,P_5(x)\}.
$$

Taylor's signed remainder gives 1-exp(-x)<=P_5(x). Both entries in the minimum are therefore upper bounds on the inclusion probability. For each item the program proposes

$$
q_i=U_5(L_{\mathrm{hi}}s_i/\tau).
$$

It increases J until it has checked, using exact fractions, that every rank satisfies

$$
0\le q_i\le\min\{1,L_{\mathrm{lo}}s_i/\tau\}.
$$

The final probabilities consequently obey

$$
\boxed{
1-\exp(-Ls_i/\tau)
\le q_i
\le\min\{1,Ls_i/\tau\}.
}
$$

The first inequality uses the valid upper log endpoint and the Taylor bound. The second uses the explicit check and the lower log endpoint. The program checks the endpoints after outward rounding, so the rounding cannot silently break either argument. These checks use ordinary control flow; optimized Python does not remove them.

## Why refinement terminates

Here is a uniform sufficient precision bound, including small item masses and clipping boundaries. Budget 1 implies s_i>=1/D. Thus t=s_i/tau>=8/D. Put h=L_hi, ell=L_lo, epsilon=h-ell, and x=h*t. Since h>=L>=log(4)>4/3, the condition

$$
\epsilon\le\frac1{4D}
$$

implies ell/h>=13/16.

For 0<x<=1,

$$
x-P_5(x)
=\frac{x^2}{120}(60-20x+5x^2-x^3)
\ge\frac{13x^2}{40}.
$$

Also h^2*t>=128/(9D). Therefore epsilon<=(13/40)*h^2*t, and

$$
q_i\le P_5(x)\le x-\epsilon t=\ell t.
$$

For 1<=x<=2, the cubic 60-20x+5x^2-x^3 decreases to 32. Hence

$$
P_5(x)\le x-\frac4{15}x^2
\le\frac{11}{15}x<\frac{13}{16}x\le\ell t.
$$

For x>=2, ell*t>=13x/16>1, and q_i<=1 suffices. Thus every item passes once the stated log-width condition holds. In particular, neither a mass near zero nor a probability near the clipping point creates a nontermination exception in this finite family.

Before dyadic rounding, the combined interval width is at most

$$
\frac{3(k+1)}{4\cdot9^J(2J+1)}.
$$

Rounding adds at most 2/2^(4J+16). It is enough to choose J with

$$
9^J\ge6D(k+1),\qquad 2^{4J+16}\ge16D.
$$

Each contribution is then at most 1/(8D). Such a finite J always exists. Under the implementation's D<=100,000 and 256-bit parameter limits, J=9 already satisfies both sufficient inequalities. The program ordinarily stops sooner when the actual checked sandwich holds; it does not replace that check with an estimated precision threshold.

## Validity and expected cost

Select items independently with probabilities q_i. For an unsafe fixed fractional loss table, let B be its positive support. Some target has risk greater than tau, so sum over i in B of s_i is greater than tau. False certification requires missing all of B. The lower side of the probability sandwich gives

$$
\Pr(Q\cap B=\varnothing)
=\prod_{i\in B}(1-q_i)
\le\exp\left(-\frac L\tau\sum_{i\in B}s_i\right)
<\delta.
$$

No factor for the number of declared budgets is needed for this one whole-family decision. An empty selected set is a possible outcome and must not be silently redrawn. With all-zero labels, every selected item is queried and the expected distinct-label cost is exactly

$$
C_{\mathrm{rat}}=\sum_i q_i.
$$

This finite sum is a rational number, serialized as `expected_zero_cost`. It is the implemented design's expectation, not a simulation estimate or a realized query count. On nonzero tables the workflow may abstain before every query is annotated; the cost theorem makes no optimality claim for those tables.

Using the fourfold blocks from the original theorem, each item in block j has s_i<=4/D_j. The upper side of the sandwich gives

$$
C_{\mathrm{rat}}
\le\sum_j\min\{D_j,4L/\tau\}
\le4\sum_j\min\{D_j,L/\tau\}
=4A\le160\operatorname{OPT}_0.
$$

The comparator, its uniform validity requirement, and its almost-sure finite certification on the zero table are unchanged. The rational design is itself admissible, so OPT_0<=C_rat. This does not establish exact optimality, the expected cost on other tables, or optimality of the earlier six-bet engine.

## Uniform integers and the randomness assumption

For a reduced fraction q=a/b, draw U uniformly from 0,...,b-1 and include the item iff U<a. The helper `exact_randbelow` requests ceil(log2(b)) unbiased bits and rejects words at least b. Every accepted integer has probability

$$
\sum_{j=0}^{\infty}
\left(\frac{2^w-b}{2^w}\right)^j2^{-w}=\frac1b,
\qquad w=\lceil\log_2 b\rceil.
$$

When b=1 it returns zero without consuming bits. Otherwise fewer than two words are needed in expectation, and termination is almost sure. Invalid bit-source outputs fail explicitly. Fresh independent bits across items give the required independent subset law; there is no modulo reduction or approximate probability comparison.

The workflow supplies OS random bits under the explicit ideal-randomness assumption. The actual accepted integers are recorded in hexadecimal for reporting. That tape permits checking the selected items and reproducing the report, but it does not prove that the tape was randomly generated, that labels were hidden, or that another plan was not tried. No finite user-selected seed is presented as a mathematical guarantee of the independent rational law.

## Bounded implementation and checks

The reference implementation rejects inputs outside these software limits:

| Quantity | Limit |
| --- | ---: |
| Candidates per pool | 1,024 |
| Total distinct items | 100,000 |
| Pool size times declared target count | 250,000 |
| Threshold/confidence numerator or denominator | 256 bits |
| Each serialized fraction numerator or denominator | 12,000 bits |
| Sum of accepted draw-width bounds over all items | 64,000,000 bits |
| Workflow input or output JSON | 64 MiB |

The math module checks geometry and parameter bounds before expanding rank laws. It checks rational serialization and tape-width limits before returning a design; the workflow enforces JSON limits before publishing output. Failures do not substitute approximate probabilities or truncate the population. The draw-width sum bounds the accepted tape's integer payload, not the random number of rejected words. The serialized-fraction cap also stays below Python's default 4,300-decimal-digit integer-conversion limit. These implementation limits do not restrict the mathematical theorem.

[Tests](../tests/test_zero_math.py) independently enumerate rank winners and, in an eight-item case, every random queried subset and every binary unsafe table. They check the exact total mass, expected cost, and miss probabilities. Additional tests cover the log enclosure with an independent high-precision decimal oracle, tiny exact parameters, the probability sandwich, rejection paths, invalid randomness, and resource failures. The analytic arguments above supply the unbounded mathematical justification; these finite tests support the implementation.
