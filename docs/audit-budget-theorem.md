# A sharp one-label benchmark for repeated conditional unbiasedness

The earlier [cache experiment](audit-cache-experiment.md) used more labels
when it refreshed audits across updates. This note asks what can be achieved
at a fixed probability of ever buying a label. The answer is a sharp
benchmark for a restricted observation problem, not an LLM training theorem.

## Observation problem and theorem

An unknown fixed scalar y lies in [-1,1]. There is no observation correlated
with y until a single query reveals it exactly. The algorithm may use private
randomness and adapt its decisions to its history. It outputs T square-
integrable estimates G_1,...,G_T. Its history H_(t-1), before round t, contains
all earlier outputs, query outcomes and internal randomness already used.
Require, for every y and every round,

```
E_y[G_t | H_(t-1)] = y.                                  (1)
```

A query may be made during that round. After the first query, y can be used
without another purchase. For 0<p<1, require probability of ever querying
by T to be at most p. A label has unit cost. The loss is

```
sup_{y in [-1,1]} E_y[sum_t (G_t-y)^2].
```

**Proposition.** Among all algorithms satisfying these conditions, including
adaptive and randomized query rules and arbitrary estimate baselines, the
minimum loss is

```
T^2 * (1-p)/p.                                           (2)
```

An attaining algorithm, for an unknown label at round t=1,...,T, queries
with probability

```
q_t = p / [T*(1-p) + t*p].                               (3)
```

On that round it outputs y/q_t if it queries and 0 otherwise. In every
subsequent round it outputs the cached y directly. Thus the probability of
querying decreases with t, although each uncached round still has a fresh
draw. Its eventual query probability is exactly p.

### Lower bound

Fix an admissible algorithm. Its probability r of ever querying is the
same under y=+1 and y=-1: couple the private randomness across these two
worlds. Before the first query no observation distinguishes them, so the
first-query event is identical. Also 0<r<=p; with r=0 the two worlds have
identical output laws and cannot both satisfy (1).

Write e_t=G_t-y. Conditional unbiasedness makes these martingale differences.
Consequently, for each fixed y, their cross moments vanish and

```
E_y[sum_t e_t^2] = E_y[(sum_t e_t)^2]
                = T^2 * E_y[(Gbar-y)^2],
Gbar = (1/T)*sum_t G_t.                                  (4)
```

Gbar is unbiased for y. On the event of never querying, its conditional
mean b is identical in the two worlds. On the event of querying, let its
conditional mean be c_y. Unbiasedness forces
`(1-r)*b+r*c_y=y`. Jensen's inequality within the two events gives

```
E_y[(Gbar-y)^2] >= (1-r)*(b-y)^2 + r*(c_y-y)^2
                 = (1-r)/r * (b-y)^2.                    (5)
```

At least one of y=+1 and y=-1 has `(b-y)^2>=1`. Combining (4)-(5) and
r<=p proves (2). Algorithms with an infinite second moment already have
infinite loss. The proof does not assume deterministic query probabilities
or an inverse-propensity form for G_t.

### Attainment

Let `a=p/[T*(1-p)]`. Under (3), the probability the label is still unknown
after t rounds telescopes to `S_t=1/(1+t*a)`, so S_T=1-p. Conditional
unbiasedness holds by `E[Z_t/q_t | history]=1` on an uncached round and by
direct equality on a cached round.

If the first query occurs at j, the sum of estimates is

```
y/q_j + (T-j)*y = (T/p)*y.
```

If no query occurs the sum is zero. Thus Gbar is exactly the ordinary
one-shot inverse-propensity estimator `y*1{ever queried}/p`, independent
of query time. Its MSE is `y^2*(1-p)/p`; (4) proves attainment. At every
round, the unconditional MSE is `y^2*T*(1-p)/p`.

## Deterministic schedules and comparison

For any deterministic probabilities 0<q_t<1, write
`S_0=1`, `S_t=product_{s<=t}(1-q_s)`, and assume S_T=1-p. For the same
fresh-or-cached estimator with zero baseline and constant discrepancy d,

```
E[e_t^2] = d^2*S_(t-1)*(1-q_t)/q_t = d^2/x_t,
x_t = 1/S_t - 1/S_(t-1),
sum_t x_t = p/(1-p).                                    (6)
```

Cauchy's inequality yields `sum_t E[e_t^2]>=d^2*T^2*(1-p)/p`, with equality
at equal x_t, giving (3). This is also a useful derivation of the schedule;
the preceding proof establishes a stronger minimax statement for the
specified one-label observation problem.

A simple comparator distributes the unconditional first-query probability
equally across rounds: `P(first query=t)=p/T`. Its probabilities are
`q_t=p/[T-(t-1)*p]`. Its total MSE for constant d is exactly

```
d^2 * [T^2*(1-p)/p + p*(T^2-1)/3].                       (7)
```

To obtain (7), substitute `S_t=1-t*p/T` in (6), then use
`sum_t (2t-1)=T^2` and `sum_t t*(t-1)=T*(T^2-1)/3`.

For T=3,p=1/2,d=1, (3) uses (1/4,1/5,1/6), with total MSE 9. Equal
first-query probabilities use (1/6,1/5,1/4), with total MSE 31/3. Both
buy the label with probability 1/2.

Reusing a single draw Z~Bernoulli(p) and the estimate Zy/p at every round
instead has total pointwise MSE `T*d^2*(1-p)/p`. It violates (1) after the
first round for nonzero y. Its average error still has MSE
`d^2*(1-p)/p`: its errors are correlated, while the fresh estimator's
errors are martingale differences. The factor T in (2) is the price of the
stronger conditional requirement in this game, not a statement that the
fresh estimator has a better averaged estimate or better training behavior.

## Relation to training and prior work

The benchmark can occur inside a clipped policy surrogate. Take
`pi_theta=((1-theta)/2,(1+theta)/2)`, old theta=0, one response per action,
weak centered advantages `(0,0)` and full centered advantages `(-y,y)`.
If `|theta|<epsilon`, the mean full surrogate is exactly `theta*y`, and its
raw gradient is y. A group query reveals the unknown sign or value y.
Thus predictable parameter choices that stay in this interval realize the
constant-gradient problem. This is a constructed subclass, not a bound
for every policy, verifier or training trajectory.

For a fixed full-minus-weak raw gradient vector d, the construction scales
by `||d||^2`. Actual training discrepancies change with the parameters and
may depend on previous audits. Conditional unbiasedness still follows from
fresh draws and cached targets, but the constant-discrepancy optimum does
not transfer automatically. For deterministic q_t and a predictable
discrepancy with `||d_t||<=B`, (6) supplies an upper bound after replacing
`d^2` by B^2; it does not establish optimal training performance.

Inverse-propensity correction and optimal allocation are established ideas.
[Imberg et al. (2020), Sections 2-3](https://proceedings.mlr.press/v108/imberg20a/imberg20a.pdf)
study sampling-weighted active learning and distinguish variance and
prediction-error objectives. [Alain et al. (2016)](https://arxiv.org/abs/1511.06481)
describe gradient importance sampling with variance-optimal probabilities.
[Farquhar et al. (2021), Sections 2-3](https://arxiv.org/html/2101.11665v2)
give unbiased active-learning estimators and explicitly separate fixed-model
unbiasedness from dependence introduced by fitting the model on those data.
Their PURE construction (Equation 4) already combines a direct sum of known
losses with a fresh inverse-probability estimate of the unknown remainder.
They also show why correcting a statistical estimator need not improve
training. Neither this basic construction nor these distinctions are new here.

The candidate contribution to assess is the sharp sequential one-label
benchmark, its attaining schedule and its connection to verifier-cache
contracts. A complete priority comparison is outstanding; the elementary
martingale and inverse-propensity argument may already be known. Codex
derived and self-reviewed this note. Independent review and user verification
have not occurred. No field-impact or fellowship-readiness claim follows.

The [matched-budget report](audit-budget-report.md) supplies exact finite
checks and a constructed training comparison, including an adverse outcome
for both fresh-audit rules.
