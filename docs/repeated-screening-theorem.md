# Repeated screening can reduce finite audit cost

**Working draft, 27 October 2026.** Derived and checked by the generating Codex session only;
no independent proof review or novelty clearance. No real-model measurements.
The project owner reports having personally checked none of the project so far.

This note gives an explicit repeated-screening auditor whose worst expected
payment, on the same safe margin class, is below a lower bound for every
one-report-per-item hybrid auditor in two finite ideal-channel examples. It
also beats the stated lower bounds for exact-only and cheap-only auditors.
The quantitative gaps are at least 7.0% and 23.3%, respectively, conditional
on the analytic arguments below. These are bounds on expected oracle payment,
not measured speedups or per-run promises.

The finite comparison uses only the elementary gate calculation, sequential
KL accounting, product-prior tails, census fallback, and convexity below.
It does not rely on a proposed matching hybrid-minimax theorem or on a noisy
channel robustness extension. Throughout, kl(p,q) denotes Bernoulli relative
entropy, with natural logarithms and the usual zero-mass convention.

## Experiment and scope

There are N fixed scores y_i in {0,1/c,...,1}, with positive integer c and
uniform mean R. A cheap rating costs one and returns a fresh independent
Bernoulli(1/4+y_i/2) observation. Exact revelation costs c, gives y_i, and is
cached. Auxiliary randomness and computation are free. The cheap interface
does not expose or permit control of an underlying component index.

Every auditor must certify with probability at most delta on every R>tau,
and must certify after finite work almost surely on every R<=tau. Define
its margin cost W as the supremum of expected total payment on
R<=tau-epsilon. All policies in each comparison obey these same conditions.

Compare unrestricted hybrid policies with (i) hybrid policies permitting
at most one paid cheap rating per item, (ii) exact-only policies, and
(iii) cheap-only policies allowing arbitrary adaptive repeats. Statements
below concern minimax expected cost, not every individual run's payment.
The score grid is finite. Cheap-only admissibility is therefore not excluded
by the boundary obstruction for a continuum of arbitrarily close means.
For the displayed examples, tau lies on the mean lattice of spacing h=1/(cN).
A cheap-only witness uses uniform proposals and a likelihood ratio with
alternative probability 1/4+tau/2 and null probability 1/4+(tau+h/2)/2.
All unsafe means are at least tau+h, making its likelihood a supermartingale;
every safe mean has strictly positive log drift, including R=tau. Thus it
certifies safely and completes almost surely with finite expected cost on
each safe grid table; the table class is finite. Exact census witnesses the
nonemptiness of the other restricted classes. The lower comparisons are
therefore not statements about empty policy classes.

## 1. Repeated-gate upper bound for every fixed score table

Write eta=1/4, alpha=3/4, kappa=2/3, q=eta+y/2 and
r=eta*(1-q)/(alpha*q). Fix K>=0 and n=K+1. On an uncached item:

1. Pay for one rating. If it is zero, emit zero.
2. Otherwise walk from 0 between -1 and K. Each step pays for another rating;
   a positive rating produces an up step with free probability alpha, and
   a negative rating produces a down step with free probability eta. Hold
   otherwise. For K=0 the upper endpoint is already reached.
3. At -1 emit zero. At K buy y and emit a free coin with probability 1-r^n.

For a cached item emit a free Bernoulli(kappa*y) coin. No unknown value is
used before its exact purchase. The finite walk has positive up and down
probabilities, so it has finite expected absorption time.

The hitting probability from zero is

    g=(1-r)/(1-r^n)=1/(1+r+...+r^K),

including r=1 through the latter expression. The emission probability is
q*g*(1-r^n)=kappa*y; at y=0 it is zero directly. Hence uniform fresh item
proposals emit an iid Bernoulli(kappa*R) sequence despite adaptive caching.
Conditional on the completed-proposal history, its emission law is unchanged
by earlier paid ratings and exact revelations. The statement does not condition
on the current proposal's in-progress walk.

The purchase probability obeys

    q*g = kappa*y + q*r^n/(1+r+...+r^K)
        <= kappa*y + eta/(K+1).                              (F1)

The inequality uses sum r^l >= (K+1)r^K and q*r<=eta. It also holds at r=1.

### Sharper paid-rating bound

Let D be the walk duration after its initial positive rating. When y>0,
the walk's drift is y/2=alpha*q*(1-r). Its terminal expected position is
(K+1)g-1, giving

    q E D = [n/(1-r^n)-1/(1-r)]/alpha.

Put x=-log r. The expression in brackets equals

    K/2 + (n/2)coth(nx/2) - (1/2)coth(x/2).

For z>0, 1/z<=coth z<=1/z+z/3. One direct justification is that both
z*cosh(z)-sinh(z) and (1+z^2/3)*sinh(z)-z*cosh(z) have nonnegative power
series coefficients. For the second expression the coefficient of
z^(2k+1) is 4k(k-1)/[3(2k+1)!], k>=1, and the first is equally immediate.
Thus the bracket is at most K/2+n^2*x/12. On q in [1/4,3/4],

    x=logit(q)-logit(1/4)<=16(q-1/4)/3=8y/3.

Consequently

    E paid ratings <= 1+2K/3+8(K+1)^2*y/27.                  (F2)

At y=0 the fair lazy walk gives q E D=2K/3, so the bound includes that
endpoint; K=0 also holds directly. The dependence on the score permits a
sharper average bound on low-risk tables than the score-uniform estimate 1+4K/3.

Let theta=tau-epsilon, with 0<epsilon<tau, and L=log(1/delta). Run the
likelihood ratio for p1=kappa*theta versus p0=kappa*tau and certify at
log likelihood >=L. Also certify or reject by the exact mean when all items
are cached, and reject early if the sum of revealed scores already exceeds
N*tau. This additional deterministic rejection cannot occur on a safe table
and only reduces payment. On unsafe tables the likelihood ratio is a nonnegative
supermartingale, and exact certification cannot err. Its crossing probability
is therefore at most delta.

If no earlier decision occurs, every item is proposed infinitely often,
and its chance of purchase on an uncached proposal is at least eta/(K+1)>0.
All items are eventually cached almost surely. Thus safe completion includes
R=tau; every walk terminates after finite work almost surely.

For R<=theta, conditional log-likelihood drift is at least d=kl(p1,p0)>0.
The upward overshoot is at most u=log((1-p1)/(1-p0)). Stopping at the first
crossing or t proposals yields expected proposal count <=(L+u)/d; letting
t increase proves the same bound for the statistical stopping time. Extend
that process past census if necessary; the actual audit stops earlier.

Combining (F1)-(F2), conditional expected payment per continued proposal is
at most the average of their linear score bounds. The fully charged result is

    U = (L+u)/d *
        [1+2K/3+8(K+1)^2*theta/27+(2c/3)*theta+c/(4(K+1))].  (F3)

Predictable continuation indicators justify this multiplication. Work and
the emitted coin are not independent. Caching only removes charges.

## 2. One-report information bound

Under independent latent binary scores B_i with probability p versus p',
each fixed seed-augmented transcript likelihood factors by item. Conditioning
on an adaptive history therefore leaves the posterior of an unrevealed item
dependent only on its own cheap report, if one has been requested. Other
items' outcomes and their selection order do not change this posterior.

Write q(p)=1/4+p/2. A first cheap rating has information
I_R=kl(q(p),q(p')). A direct exact reveal has information J=kl(p,p'). If
a cheap report z has preceded the reveal, its posterior probability is

    p_z = r_z*p/[1+(r_z-1)*p],  r_1=3, r_0=1/3,

and the exact reveal has information d_z=kl(p_z,p'_z). A cheap report after
exact revelation has zero information. Therefore, for any adaptive policy
with at most one paid cheap report per item, the KL per unit of expected
payment is at most

    I = max(I_R, J/c, d_0/c, d_1/c).                         (F4)

This is a deliberately relaxed upper bound on information efficiency; it
does not assert that the maximizing type can always be obtained freely.
Sequential KL accounting gives KL(transcripts)<=I*E_p(payment). It permits
selective exact purchasing, arbitrary item order, internal randomization,
and stopping. For exact-only policies replace I by J/c. All of these statements
also apply at p=0, using kl(0,q)=-log(1-q).

## 3. Zero-null lower bound for a finite wide-margin case

Take p=0 and p'>tau. The null is the single all-zero table, on which the
auditor must certify almost surely. Suppose

    exp[-N*kl(tau,p')] <= nu.

The alternative product prior has probability at most nu of R<=tau.
Otherwise validity bounds certification by delta. Thus its probability of
certification is at most delta+nu. Apply binary data processing to bounded
transcripts, then take the limit as null certification probability tends to
one. Equations (F4) and the null cost guarantee imply

    W_one-report >= log(1/(delta+nu))/I,
    W_exact-only >= c*log(1/(delta+nu))/J.                    (F5)

No cost bound on alternative tables or cost cap is required here. The null
is in the efficiency class for every epsilon<tau. This lower bound happens
to hold on the same all-zero table for every competitor in the named class.

## 4. Census-fallback lower bound for the small-relative-margin regime

Choose 0<p<theta<tau<p'<1 with both product-prior exceptional masses at most nu:

    exp[-N*kl(theta,p)]<=nu,  exp[-N*kl(tau,p')]<=nu.           (F6)

For any original auditor with margin cost W, fix lambda>0. Transform it as
follows: immediately before a paid action would make its cumulative payment
exceed B=lambda*c*N, instead buy all remaining exact scores and decide by the
exact mean. This preserves validity, safe completion and the one-report
restriction. Its payment never exceeds (lambda+1)cN.

On every margin table, a fallback requires the original auditor's eventual
payment to exceed B. Markov's inequality bounds its probability by W/B.
Pre-fallback work costs no more than the original continuation, and the
fallback adds at most cN, so expected transformed cost is at most
(1+1/lambda)W. On exceptional null-prior tables, its pathwise payment is
at most (lambda+1)cN; no original efficiency promise is made there.

The transformed null certification probability is at least 1-nu, while
the alternative's is at most delta+nu. Require 1-nu>delta+nu. With
D=kl(1-nu,delta+nu), data processing and (F4) give

    W_one-report >=
      [D/I - nu*(lambda+1)*c*N]/(1+1/lambda).                (F7)

For exact-only policies use I=J/c. A negative right side is vacuous, not a
cost advantage. Finite-horizon approximation handles any unbounded free
randomness or stopping; the transformed payment bound holds at every horizon.

If A=D/I and b=nu*cN, optimizing over lambda gives (sqrt(A)-sqrt(b))^2 when
A>b. The exact numerical certificate below uses the explicit rational choice
lambda=48, so it needs no square-root approximation. The census-fallback
argument is included in full here; no priority claim about cost caps is made.

## 5. Cheap-only lower bound using a mixture of unsafe fixed tables

Let s<=theta be an available constant score on the grid. The null is y_i=s
for every i. For each j in {1,...,N}, form an alternative with y_j=2tau and
all other scores equal tau, assuming those scores belong to the grid and
2tau<=1. Every alternative is unsafe: its mean is tau+tau/N.

Let P_0 be the null transcript law, P_j the alternative law, and P_bar their
uniform mixture. Validity gives P_bar(certifies)<=delta, while null completeness
gives P_0(certifies)=1. Hence KL(P_0||P_bar)>=L, by finite-horizon data processing
and a limit. Convexity in the second KL argument gives

    KL(P_0||P_bar) <= (1/N) sum_j KL(P_0||P_j).

Put q_s=1/4+s/2, q_b=1/4+tau/2 and q_h=1/4+tau. Under the fixed constant
null, averaging each query's information over the hidden exceptional index
gives exactly

    I_noise = (1-1/N)kl(q_s,q_b) + (1/N)kl(q_s,q_h).

This calculation is unaffected by adaptive item selection or repeats: for
each fixed selected item, exactly one of the N alternatives assigns q_h.
All other alternatives assign q_b. Thus

    W_cheap-only >= L/I_noise.                              (F8)

This lower bound does not rely on a boundary-completeness impossibility or
restrict the competing strategy to uniform sampling.

## 6. Exact numerical inequalities

The two examples were selected exploratorily, then certified separately with
rational intervals. The quoted integers are outward rounded. The certificate
assumes the analytic arguments above; it is not machine-checked mathematics.

| Quantity | Finite wide margin | Small-relative-margin regime |
|---|---:|---:|
| N | 13,000 | 70,000,000 |
| c | 64 | 8,192 |
| tau | 1/64 | 1/512 |
| epsilon | 9/640 | 1/8192 |
| Margin-class maximum risk | 1/640 | 15/8192 |
| delta | 1/20 | 1/20 |
| K | 4 | 52 |
| Hybrid upper | 2,973 | 98,855,201 |
| Every one-report hybrid: lower | 3,198 | 128,874,779 |
| Every exact-only policy: lower | 9,410 | 2,747,662,969 |
| Every cheap-only policy: lower | 18,653 | 302,326,524 |

For the first column use p=0, p'=5/256, nu=1/200 and s=0. It gives a cost
gap of at least 75/1066, about 7.0%, relative to the smallest displayed lower
bound. Its epsilon/tau=0.9 lies outside the small-relative-margin domain
epsilon<=tau/16. The elementary upper and lower arguments here cover it
directly. It is an additional wide-margin example, not evidence for a narrower margin.

For the second use p=59/32768, p'=65/32768, nu=1/10,000,000, lambda=48 and
s=15/8192. It retains epsilon=tau/16 and gives a gap exceeding 23%. Its large
population and high adjudication cost remain material practical limitations.

The verifier computes log(x) by dyadic reduction to [1,2] and the positive
series 2*sum z^(2k+1)/(2k+1), z=(x-1)/(x+1). After 64 terms, the omitted tail
is at most 2*z^129/[129*(1-z^2)]. Rational lower and upper endpoints propagate
through every KL, tail inequality, upper cost and lower cost. All statistical
tail and strict-separation conditions pass. An additional 561 rational
absorbing-chain cases check the sharper work inequality independently of its
coth derivation. No N-item population is allocated for either certificate.

Reproduction code: [fixed checker](../experiments/check_repeated_screening.py),
[exact bounds](../goodhart_audit/screening_math.py), and
[callback auditor](../goodhart_audit/screening.py). See the
[report](repeated-screening-report.md) for commands, source pins, and limits.

## Interpretation, implementation, and prior work

This is a fully charged finite-population comparison in an idealized two-oracle
experiment. Independent cheap ratings, the known affine response channel, and
exact numerical adjudication are assumptions, not facts established about LLM
judges or human annotators. Auxiliary randomization and computation are free
in the payment model. In particular, the 70-million-item example is a finite
inequality certificate; no such population or model run was instantiated.

The callback implementation uses exact integer/Fraction likelihood updates
and sparse caching. Every valid paid rating, including holding steps, costs
one; every new exact revelation costs c. The default uses independent uniform
randomness from Python's secrets module. A caller-supplied random source must
have the same conditional law. Type checks cannot validate independence,
channel calibration, truth of adjudication, or persistence of a fixed table.

Optional `max_ratings` returns inconclusive before the next rating would
exceed that cap. It preserves validity of returned certificates but removes
the unconditional safe-completion guarantee. It does not bound free proposals,
integer bit growth, or total compute. Exceptions propagate without a result;
external callback costs incurred before an exception are outside returned
accounting. Adjudicated scores outside the declared grid are rejected.

Established precedents are essential to interpreting the proposed distinction:

- [Ham, Zhao, Jasin and Yang, Human-AI-Powered Hypothesis Testing,
  v1](https://arxiv.org/html/2609.28859v1) develops selective AI scoring,
  human escalation, adaptive transcript-KL cost bounds and asymptotically
  optimal cost-aware testing with one AI report per item. Relevant passages
  are Section 3.2, Theorem 4.6 and Appendix 8.2. Selective verification and
  cost-aware testing are not new claims here. The candidate distinction is
  the explicit value of repeated, adaptively stopped reports within an item.
  A complete reduction/comparison with bundled reports of random cost remains
  open; the one-report restriction alone does not establish novelty.
- [Angelopoulos et al., Cost-Optimal Active AI Model Evaluation,
  v1](https://arxiv.org/html/2506.07949v1), Sections 2.1 and 4.2, studies
  cost-aware weak/strong evaluation and report-dependent selection for mean
  estimation. A complete proof-level comparison remains open.
- [Prangle, Lazy ABC, v3](https://arxiv.org/html/1405.7867v3), Theorem 1 and
  Section 4.1, provides earlier randomized continuation and unbiased correction
  machinery. [Nacu and Peres, Fast simulation of new coins from old
  (2005)](https://arxiv.org/pdf/math/0309222), Proposition 3 and Section 6,
  supplies Bernoulli-factory foundations. Neither randomized screening nor
  probability-factory principles are claimed independently new here.
- [Poiani et al., Optimal Multi-Fidelity Best-Arm Identification,
  v2](https://arxiv.org/html/2406.03033v2), Section 2, addresses repeated
  adaptive choices among costs and fidelities for a different statistical
  target. The difference in target does not itself resolve possible proof
  overlap; the full comparison is unfinished.

Independent review should focus on adaptive posterior factorization in (F4),
the finite-horizon limits in (F5)-(F8), and cost/output dependence in (F3).
The rational calculations are reproducible diagnostics conditional on those
proofs, not a formal verification or independent human review. Priority,
practical model usefulness, field impact, the owner's personal research
contribution, and fellowship competitiveness remain unestablished.
