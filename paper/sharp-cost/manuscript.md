# Sharp zero-table audit costs for finite best-of-N families

**Larry Mai - with substantial Codex assistance**

Research manuscript, 26 October 2026. Consolidation of public release v0.7; evidence frozen at commit ba573d604e3810d7edc9780d57ffea0ff8785296 [1]. No new experiment is reported.

**Contribution disclosure.** Larry Mai commissioned this project. Codex developed the theory, software, literature assessment, numerical checks, and manuscript; separate agent contexts reviewed the work. Larry has not personally checked the results. There has been no independent human replication or peer review. The document reports a candidate mathematical result, with scientific priority unresolved.

## Abstract

Consider a frozen collection of ranked candidate outputs and a predeclared family of best-of-N selectors. Each selector chooses the best member of a uniformly sampled subset without replacement. An auditor queries correct, fixed losses and may certify that every declared selector has risk at most a threshold. We study expected distinct-query cost on the all-zero loss table, while requiring validity for every fixed fractional loss table. The comparator allows arbitrary adaptive queries, correlated sampling, abstention, and certification lotteries. For every nonempty budget family, classical negative-exponential inspection has asymptotically optimal cost when the threshold tends to zero and the largest individual target mass vanishes relative to the threshold and confidence scale. The leading cost is the envelope normalizer times the log confidence factor divided by the threshold. A finite bound follows from a zero-path hypergeometric argument, geometrically separated budget representatives, and an exact rank-tail identity. A counterexample shows that normalized decreasing target rows alone do not imply this conclusion. Exact finite checks support the implementation. A previously published safe synthetic table also demonstrates the objective's limitation: ideal zero-only inspection certifies with probability below 0.47%. These results establish no real-model benefit, and closer comparison with older safeguards inspection theory remains necessary before any novelty claim.

## 1. Question and scope

Increasing a search budget changes which candidates a proxy score selects. A reusable audit can address several budgets with shared labels, but minimizing a sampling weight does not automatically minimize the number of labels required for a decision. This manuscript asks when an envelope-based inspection rule achieves the optimal leading cost for one specific decision: certifying that every member of an originally declared budget family is safe.

The cost is evaluated at a completely clean archive. This supplies a precise benchmark with a broad adaptive comparator, but it is deliberately narrower than useful performance on all safe archives. A table can have risk well below the threshold while containing positive losses that cause a zero-only rule to abstain almost always. Section 7 quantifies this distinction using an existing synthetic scenario.

Negative-exponential inspection, or NEGEXP, randomized-subset optimization, and reuse across targets are established auditing methods [2]. The candidate result consolidated here is a uniform comparison between this classical rule and unrestricted adaptive auditors for finite best-of-N rank laws. The family may grow, omit budget 1, and contain arbitrarily large gaps. The proof identifies sufficient geometric and tail properties; it does not classify all families for which the conclusion holds. All evidence comes from the frozen public project [1], without new model outputs or annotations.

## 2. Fixed experiment and main result

There are $P\ge1$ equally weighted prompt pools, each with $m\ge1$ distinct items in a fixed total rank order. Rank 1 is best. A declared tie rule is part of that order. Querying item $(p,r)$ reveals its fixed, correct loss $y_{p,r}\in[0,1]$ at unit cost. There are no supplied labels or known cross-item relationships that reveal other losses for free. Computation is uncharged. Write $D=Pm$.

Let $\mathcal{K}$ be any nonempty subset of $\{1,\ldots,m\}$, with $N=\max\mathcal{K}$. For budget $n$, sample a uniform $n$-subset within a prompt pool and return its best-ranked item. Its winner law and risk are

$$
w_n(r)=\frac{\binom{m-r}{n-1}}{\binom{m}{n}},\qquad a_n(p,r)=\frac{w_n(r)}{P},
$$

$$
R_n(y)=\sum_{p=1}^P\sum_{r=1}^m a_n(p,r)y_{p,r}.
$$

Impossible binomial choices have value zero. Every target row is nonnegative and sums to one. These are conditional finite-pool risks: no independence of prompts, ranks, or losses is assumed. They do not describe new prompts, fresh generations, or a changed ranking system.

Fix $0<\tau<1$ and $0<\delta\le1/4$. An admissible auditor may randomize, query unseen items adaptively, and abstain. A certificate asserts $R_n(y)\le\tau$ for every $n\in\mathcal{K}$. For every fixed table with some $R_n(y)>\tau$, the probability of ever issuing that certificate is at most $\delta$. On the zero table the auditor must certify after finitely many queries almost surely. If $Q_0$ denotes the distinct items queried before its first zero-table certificate, define

$$
\mathrm{OPT}_0=\inf_{\mathcal{A}}\mathbb{E}_0|Q_0|.
$$

The infimum has no computational restrictions. It includes correlated subsets and empty-query certification lotteries. Almost-sure finite certification excludes the procedure that always abstains; a census followed by exact risk evaluation shows the class is nonempty. Validity is required on every fractional table, even though binary tables will suffice for the lower bound.

Define the envelope, its normalizer, and the relevant scales by

$$
e(r)=\max_{n\in\mathcal{K}}w_n(r),\qquad s_{p,r}=e(r)/P,\qquad Z_{\mathcal{K}}=\sum_{r=1}^m e(r),
$$

$$
L=\log(1/\delta),\quad T=L/\tau,\quad M=\frac{N}{Pm},\quad a=M/\tau,\quad \rho=La.
$$

Here $M$ is the largest individual target mass. Classical NEGEXP selects items independently with probabilities $1-\exp(-Ts_{p,r})$, queries the selected set, and certifies exactly when all selected losses are zero. Its expected zero-table cost is

$$
C_{\mathrm{NEG}}=\sum_{p,r}\left(1-e^{-Ts_{p,r}}\right).
$$

**Theorem 1.** Along every sequence of these experiments satisfying

$$
\tau\longrightarrow0,\qquad \rho=\frac{\log(1/\delta)N}{Pm\tau}\longrightarrow0,
$$

one has

$$
\mathrm{OPT}_0\sim C_{\mathrm{NEG}}\sim\frac{LZ_{\mathcal{K}}}{\tau}.
$$

The convergence is uniform in $P,m,\mathcal{K},\delta$ subject to the conditions above. No intermediate targets are added to the decision, and budget 1 is unnecessary. Increasing the number of prompts can make $M$ small even when $N/m$ stays large.

The actual sparse-grid normalizer is essential. A singleton family has $Z_{\mathcal{K}}=1$; two budgets have $Z_{\mathcal{K}}\le2$, however far apart they are. Only for the complete prefix $\mathcal{K}=\{1,\ldots,N\}$ does the earlier finite-pool result give $Z_{\mathcal{K}}=(\log N)/e+O(1)$ uniformly in $m\ge N$ [1,3]. When that prefix and $N\to\infty$ are assumed, the leading cost can consequently be written $L\log N/(e\tau)$.

## 3. A finite lower bound for arbitrary auditors

Call a binary support $B$ unsafe when $a_n(B)>\tau$ for some declared target. Couple an auditor's zero-table run and its run on $1_B$ using the same random seed. On every seed where the zero-path queried set misses $B$, all observed labels, adaptive choices, and the first certificate coincide. Because the zero-table certificate occurs in finite time almost surely, $Q_0$ has a probability law and

$$
\mathrm{Pr}_0(Q_0\cap B=\varnothing)\le\delta.
$$

This zero-path constraint makes no independence assumption about the auditor. It is the subset-auditing argument specialized to the present decision, rather than a new auditing principle [2,4].

**Lemma 1.** Suppose a block contains $d\ge1$ items and every $b$-subset is unsafe, where $1\le b\le d$. Let $X$ count queried block items on the zero path and let $\mu=\mathbb{E}_0X$. Then

$$
\mu\ge\frac{L(d-b)}{b+L}.
$$

**Proof.** Average the zero-path constraint over a uniform $b$-subset chosen independently of $Q_0$. Conditional on $X=x$, its miss probability is

$$
f(x)=\frac{\binom{d-x}{b}}{\binom{d}{b}},\qquad x=0,\ldots,d.
$$

Extend $f$ linearly between integers. The successive differences

$$
f(x+1)-f(x)=-\frac{\binom{d-x-1}{b-1}}{\binom{d}{b}}
$$

are nondecreasing, using zero for impossible binomial choices. Thus $f$ is convex on $[0,d]$, and averaging followed by Jensen's inequality gives $\delta\ge\mathbb{E} f(X)\ge f(\mu)$.

If $\mu\ge d-b$, the desired inequality follows from $L/(b+L)<1$. Otherwise put $c=d-b-\mu>0$. Either neighboring integer $x=\lfloor\mu\rfloor$ or $x=\lceil\mu\rceil$ is at most $d-b$. All factors in the following product are therefore positive. The elementary inequality $\log(1-u)\ge-u/(1-u)$ yields

$$
\log f(x)=\sum_{j=0}^{b-1}\log\left(1-\frac{x}{d-j}\right)
\ge-\sum_{j=0}^{b-1}\frac{x}{d-j-x},
$$

$$
-\sum_{j=0}^{b-1}\frac{x}{d-j-x}\ge-\frac{bx}{d-b+1-x}\ge-\frac{bx}{c}.
$$

The last inequality uses $x\le\mu+1$. Linear interpolation of the two endpoint bounds, followed by convexity of the exponential, gives $f(\mu)\ge\exp(-b\mu/c)$, also when $\mu$ is an integer. Hence

$$
e^{-L}\ge e^{-b\mu/(d-b-\mu)}.
$$

Taking logarithms and rearranging proves $L(d-b)\le\mu(b+L)$. When $b=d$, the stated bound is simply zero, already covered by the first case. This proves the lemma without a continuous-binomial approximation.

For the upper bound, take any unsafe fractional table and let $B$ be its positive support. Since losses are at most one, $a_n(B)\ge R_n(y)>\tau$ for some $n$. Therefore $\sum_{i\in B}s_i>\tau$, and NEGEXP certifies with probability

$$
\exp\left(-T\sum_{i\in B}s_i\right)<e^{-T\tau}=\delta.
$$

It always certifies the zero table after at most $D$ queries. Consequently

$$
\mathrm{OPT}_0\le C_{\mathrm{NEG}}\le TZ_{\mathcal{K}}.
$$

No multiplicity penalty is needed for this single whole-family certificate: any unsafe table supplies one witness that bounds the probability of the common passing event. This does not authorize separate partial certificates for targets when the full family fails.

## 4. Representative budgets, tails, and the sharp limit

Write $Z=Z_{\mathcal{K}}$ throughout the proof. A sparse family may have a very large range of positive envelope heights. Counting all heights directly is insufficient; instead we cover almost all envelope mass by windows associated with a small representative family.

### 4.1. A representative skeleton

Choose $n_1=\min\mathcal{K}$. After $n_j$, choose the smallest declared budget at least $4n_j$, if one exists. Let $R$ be the number of representatives. Every declared budget belongs to a group whose representative $n_j$ satisfies $n_j\le n<4n_j$, including across gaps in the family.

For budgets $u\le n$,

$$
w_n(r)\le\frac{n}{u} w_u(r).
$$

Indeed, on positive support

$$
w_n(r)=\frac{n}{m}\prod_{v=1}^{r-1}\left(1-\frac{n-1}{m-v}\right).
$$

The factors decrease with $n$. If $w_n(r)=0$ the inequality is immediate; if $w_u(r)=0$, then $w_n(r)=0$ as well. The empty product covers $r=1$. Each group is therefore dominated coordinatewise by four times its representative.

The representatives have disjoint rank bands

$$
I_j=\{\lfloor m/(4n_j)\rfloor+1,\ldots,\lfloor m/n_j\rfloor\}.
$$

Disjointness follows because the upper endpoint of $I_{j+1}$ is at most the excluded lower endpoint of $I_j$. Each band has more than $1/4$ mass under its own representative. To verify this, set $n=n_j$, $h=\lfloor m/n\rfloor\ge1$, and $\ell=\lfloor m/(4n)\rfloor=\lfloor h/4\rfloor$. For winner rank $W_n$, a union bound gives $\mathrm{Pr}(W_n\le\ell)\le n\ell/m\le1/4$. Also

$$
\mathrm{Pr}(W_n>h)=\frac{\binom{m-h}{n}}{\binom{m}{n}}\le(1-h/m)^n\le e^{-nh/m},
$$

and $nh/m>h/(h+1)$. A zero numerator already satisfies the inequality; otherwise the without-replacement product proves it. If $h\le3$, then $\ell=0$ and the band mass exceeds $1-e^{-1/2}>1/4$. If $h\ge4$, it exceeds $1-1/4-e^{-4/5}>1/4$. Thus

$$
R/4<\sum_j\sum_{r\in I_j}w_{n_j}(r)\le Z,\qquad R\le4Z.
$$

The bands need not partition the ranks. This count uses declared representatives only and never requires budget 1.

### 4.2. Exact tail control and height windows

The rank laws satisfy an exact tail identity:

$$
\sum_{v=r}^m w_n(v)=\frac{\binom{m-r+1}{n}}{\binom{m}{n}}
=\frac{m-r+1}{n}w_n(r)\le\frac{m}{n} w_n(r).
$$

The identity follows by summing binomial coefficients, or by requiring all sampled ranks to be at least $r$. It remains true where the weights vanish. Because $w_n$ is nonincreasing, its strict low-height set is a terminal interval. At its first rank, the identity implies, for $0<\epsilon<1$,

$$
\sum_{r:\,w_n(r)<\epsilon n/m}w_n(r)\le\epsilon.
$$

Empty tails and zero weights cause no difficulty. No exponential approximation or assumption that $n/m$ is small enters this step.

Put $h_j=n_j/m$. Call a rank good when its envelope height lies in the union of windows

$$
\bigcup_{j=1}^R[\epsilon h_j,4h_j].
$$

Other ranks are bad. At a bad rank with positive envelope, choose an actual maximizing budget $n$ and assign the rank to its representative $n_j$. Domination gives $e(r)=w_n(r)\le4w_{n_j}(r)\le4h_j$. Being outside the window then forces $e(r)<\epsilon h_j$, and the declared representative satisfies $w_{n_j}(r)\le e(r)$. Summing these assignments and the tail bound yields

$$
\sum_{r\,\mathrm{bad}}e(r)
\le4\sum_{j=1}^R\sum_{r:\,w_{n_j}(r)<\epsilon h_j}w_{n_j}(r)
\le4R\epsilon\le16\epsilon Z.
$$

Zero-envelope ranks contribute nothing. A representative need not itself maximize the envelope at an assigned rank.

### 4.3. Bins and the finite inequality

The positive envelope occupies ranks $1$ through $m-\min\mathcal{K}+1$. For $\eta>0$, partition those ranks into maximal consecutive bins $[u,v]$ satisfying $e(u)/e(v)\le1+\eta$. Start the next bin at $v+1$. The envelope is nonincreasing, and maximality ensures that successive start heights decrease by a factor strictly greater than $1+\eta$. This handles ties, jumps, and singleton bins.

For each bin, choose a declared budget attaining $e(v)$. Its decreasing row witnesses all $P$ prompt copies of the bin with individual mass at least $\nu=e(v)/P$. Set

$$
d=P(v-u+1),\qquad q=d\nu=(v-u+1)e(v).
$$

The bin ratio gives $\sum q\ge Z/(1+\eta)$. A single endpoint witness suffices even when maximizing budgets change within the bin.

Define

$$
B(\epsilon,\eta)=1+\frac{\log(4(1+\eta)/\epsilon)}{\log(1+\eta)}.
$$

If a bin contains a good rank $r$ in representative window $j$, its start height satisfies

$$
\epsilon h_j\le e(r)\le e(u)\le(1+\eta)e(v)\le(1+\eta)e(r)\le4(1+\eta)h_j.
$$

Geometric separation permits at most $B(\epsilon,\eta)$ starts in that interval. Summing over windows bounds the number of bins meeting good ranks by $RB(\epsilon,\eta)\le4ZB(\epsilon,\eta)$. Overlapping windows only loosen the count.

Choose $\kappa>1+a$ and retain bins with $q\ge\kappa\tau$. A discarded bin meeting good ranks loses less than $\kappa\tau$, charged to that count. A discarded bin containing only bad ranks has $q$ at most its actual envelope mass, charged to the bad-mass bound. With $x_+=\max(x,0)$,

$$
\sum_{\mathrm{retained}}q\ge
Z\left[\frac{1}{1+\eta}-16\epsilon-4\kappa\tau B(\epsilon,\eta)\right]_+.
$$

In each retained bin put $b=\lfloor\tau/\nu\rfloor+1$. Every $b$-subset is strictly unsafe under the endpoint witness. Since $\nu\le M$ and $d\nu\ge\kappa\tau$,

$$
b\le\frac{\tau}{\nu}(1+a),\quad
\frac{b}{d}\le\frac{1+a}{\kappa}<1,\quad
\frac{d}{b}\ge\frac{q}{\tau(1+a)},\quad
\frac{L}{b}\le\rho.
$$

Thus $1\le b<d$, and Lemma 1 bounds its expected query contribution below by

$$
\frac{L(d-b)}{b+L}
\ge\frac{Lq}{\tau}\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
$$

The retained blocks are disjoint, so their expected counts add regardless of dependence. Every admissible auditor therefore obeys the finite bound

$$
\frac{\mathrm{OPT}_0}{LZ/\tau}\ge
\left[\frac{1}{1+\eta}-16\epsilon-4\kappa\tau B(\epsilon,\eta)\right]_+
\frac{1-(1+a)/\kappa}{(1+a)(1+\rho)}.
$$

A nonpositive bracket gives only zero. Neither this coarse bound nor an empty retained collection is silently replaced by a useful positive approximation.

### 4.4. Uniform passage to the limit

Choose $\epsilon=\eta=\tau^{1/3}$ and $\kappa=1/\eta$. Then

$$
\kappa\tau B(\eta,\eta)=\eta^2\left[1+\frac{\log(4(1+\eta)/\eta)}{\log(1+\eta)}\right]\longrightarrow0.
$$

For example, $\log(1+\eta)\ge\eta/2$ for $0<\eta\le1$ bounds the second term by $2\eta\log(4(1+\eta)/\eta)$. Also $a=\rho/L\le\rho/\log4\to0$, so $\kappa>1+a$ eventually and the remaining factor tends to one. Every error depends only on $\tau$ and $\rho$, not on the number or spacing of budgets. Squeezing between this lower bound and $\mathrm{OPT}_0\le C_{\mathrm{NEG}}\le LZ/\tau$ proves Theorem 1.

## 5. A sufficient structure and its boundary

The proof suggests sufficient conditions for other normalized rows on a common decreasing coordinate order. Suppose a representative subfamily has size at most $C_1Z$; each row is coordinatewise at most $C_2$ times one representative; and each representative assigns at most $g(\epsilon)$ mass to coordinates below $\epsilon$ times its initial height, uniformly with $g(\epsilon)\to0$. For fixed $C_1,C_2$, the bad envelope mass is at most $C_1C_2g(\epsilon)Z$. The same logarithmic-window count and bin argument apply with the largest coordinate mass $M$. The preceding choice of parameters proves the sharp limit when $\tau\to0$, $LM/\tau\to0$, and $L\ge\log4$. Rank laws supply $C_1=C_2=4$ and $g(\epsilon)=\epsilon$.

These are sufficient assumptions only. Shared monotonicity and normalization alone do not work, even with a uniform baseline. To prove this, take an integer $k\ge2$ and define

$$
\tau=1/k,\quad\beta=1/k^2,\quad H=J=k^3,
$$

$$
t_j=H2^j\ (j=0,\ldots,J),\qquad D=H+t_J.
$$

On one ordered universe of $D$ items, make the first $H$ items a common head. Row $j$ gives each head item mass $(1-\beta)/H$, each of the next $t_j$ items mass $\beta/t_j$, and all later items zero. Add the uniform row $1/D$.

Every row is normalized and nonincreasing because $t_j\ge H$ and $\beta\le1/4$. Its largest individual mass is at most $1/H$. Fix $\delta=1/4$, so $L=\log4$ and $\rho=LM/\tau\le L/k^2\to0$. Nevertheless the envelope normalizer grows: the head contributes at least $1-\beta$, the first $H$ tail items contribute at least $\beta$, and each subsequent dyadic shell contributes at least $\beta/2$. The shells are disjoint, giving

$$
Z\ge1+J\beta/2=1+k/2.
$$

A cheaper valid auditor exploits the shared head. Define its mean-loss threshold

$$
\gamma=\frac{\tau-\beta}{1-\beta}=\frac{1}{k+1}.
$$

If the head mean is at most $\gamma$, every nonuniform row has risk at most $(1-\beta)\gamma+\beta=\tau$, whatever the tail losses. Audit the uniform head distribution at threshold $\gamma$ and the uniform population distribution at threshold $\tau$, each with NEGEXP error level $\delta$. Query the union of their selected sets, count duplicates once, and certify only if every queried loss is zero.

This is valid for all fixed fractional tables. An unsafe original target implies either an unsafe head mean or an unsafe uniform population mean. For that fixed table, certification requires the corresponding unsafe test to miss its positive support, an event of probability at most $\delta$. Both tests may use $\delta$: the decision requires both to pass, so a union-bound division is unnecessary. The procedure certifies the zero table almost surely, with expected cost at most

$$
H\left(1-e^{-L/(H\gamma)}\right)+D\left(1-e^{-L/(D\tau)}\right)
\le L/\gamma+L/\tau=L(2k+1).
$$

Thus $\mathrm{OPT}_0\le L(2k+1)$; its exact value is not claimed. In contrast, $1-e^{-x}\ge x-x^2/2$ and $\max_i Ts_i=\rho$ imply

$$
C_{\mathrm{NEG}}\ge(1-\rho/2)LZ/\tau.
$$

Consequently

$$
\frac{C_{\mathrm{NEG}}}{\mathrm{OPT}_0}\ge
\left(1-\frac{L}{2k^2}\right)\frac{k(1+k/2)}{2k+1}\longrightarrow\infty.
$$

The displayed bound grows like $k/4$. There are $J+2$ targets. The exponential population size is symbolic and need not be allocated. All labels remain unknown; the head is known target geometry, not free label information. Each row's tail mass lies below the threshold, yet these negligible tails accumulate substantial envelope mass across scales. These rows are not best-of-N rank laws.

## 6. Frozen arithmetic evidence and reproducibility

The v0.7 checker uses exact rational arithmetic and outward-rounded logarithm bounds. Its protocol was committed as bcb0790 after exploratory proof work and small-grid checks. Amendment 3e26b8c added a nonvacuous aggregate-tail regime before the saved broader calculation. This is a recorded analysis protocol, not external preregistration or an empirical holdout. The following counts describe deterministic checks or explicitly paired synthetic paths; none are independent human replications [1].

| Evidence | Recorded scope | Unit and interpretation |
| --- | --- | --- |
| v0.7 rank tails | 89,440 identities; 2,080 empty endpoints; 6,240 low-height checks | Exact cases through $m=64$ |
| v0.7 grid structure | 2,036 nonempty grids; 6,108 scale configurations | Exhaustive grids through $m=10$, each at three scales |
| v0.7 bin checks | 34,538 bins; 2,802 bad-rank assignments | Dependent checks within those configurations |
| v0.7 cost bounds | 64 certificates; 1,170 unsafe-size checks | Eight grids, four scales, two confidence levels |
| v0.7 counterexample | Six symbolic bounds | Six constructed values of $k$, not sampled populations |
| Earlier block lemma | 10,400 small inverse comparisons; four larger cases | Exact interpolated block constraints, not global optima |
| Earlier synthetic comparison | 800 independent scenario-replicate streams; 5,600 paired method paths | Eight scenarios, 100 repetitions; shared randomness across methods |

Of the 6,108 grid configurations, 2,036 have a nontrivial aggregate bad-mass bound and 1,566 have positive bad-envelope mass. The earlier synthetic comparison's 22,400 checkpoint records are repeated observations, not independent experiments. Its two added proposals reused scenarios and paired seeds already observed in earlier releases; it supplies no fresh holdout for this theorem. Section 7 uses only its published scenario definition.

The 64 cost certificates set $\tau=1/k^3$ and $P=\lceil3Nk^4/m\rceil$. Their greatest conservative ratio upper bounds across the sixteen prescribed settings at each scale are:

| $k$ | $\tau$ | Upper bound on $C_{\mathrm{NEG}}/\mathrm{OPT}_0$ |
| ---: | ---: | ---: |
| 8 | 1/512 | 1.168867 |
| 32 | 1/32,768 | 1.041655 |
| 128 | 1/2,097,152 | 1.010407 |
| 512 | 1/134,217,728 | 1.002602 |

The decimals round upward. They bound a ratio rather than compute either cost exactly; individual block lower bounds can improve on the coarse universal expression. The largest represented population is 26,388,279,066,624 items, stored as a count rather than a label table. For the non-rank counterexample, the saved bound at $k=64$ exceeds 16.369; its direction is a ratio lower bound. Separate tests check the head/uniform implication on all 1,024 binary tables and four fractional tables of a ten-item analogue.

The frozen development record reports 192 passing project tests, ten focused tests with site-packages disabled, and a separate run reproducing the 137,749-byte v0.7 artifact exactly. Its SHA-256 is 5e0dc8c8adf2316bfe09a7564b64bf4220808d7c84284ab574149611747b5da8. These are assisted-session checks, not independent human replication. The checker pins seven sources, rechecks source and protocol bytes before output, and refuses to overwrite artifacts. Reproduction commands and immutable source links are supplied in the public report [1]. Finite enumeration checks arithmetic and implementation; the proofs supply the unbounded statements.

## 7. Practical limitation: safe tables can defeat zero-only power

In the published `prompt_cluster` scenario, two of $P=32$ prompts fail at every rank, while all other losses are zero. With $m=64$ and $\mathcal{K}=\{1,2,4,8,16,32,64\}$, every target has

$$
R_n=2/32=1/16<\tau=0.1.
$$

The exact seven-budget envelope normalizer is

$$
Z_{\mathcal{K}}=\frac{177416516255}{61966315152}=2.86311225413044\ldots.
$$

The positive support contains two complete prompt pools, so its envelope mass is $2Z_{\mathcal{K}}/32=Z_{\mathcal{K}}/16$. At $\delta=0.05$, ideal NEGEXP certifies exactly when it selects none of those items. Independence gives

$$
\mathrm{Pr}(\mathrm{certificate})
=\exp\left(-\frac{\log20}{0.1}\frac{Z_{\mathcal{K}}}{16}\right)
=0.05^{5Z_{\mathcal{K}}/8}.
$$

This is approximately $0.4697623\%$, strictly below $0.469763\%$. The released rational workflow includes items at least as aggressively and therefore has certification probability no larger.

This calculation is an analytical consequence of an existing synthetic table, not a new simulation or model study. Every target is safe, yet a zero-only procedure almost always abstains. The earlier sequential betting engine can use observed nonzero losses differently; Theorem 1 neither establishes its optimality nor transfers its behavior to NEGEXP. Useful auditing requires attention to nonzero-instance power as well as the clean-table benchmark.

The theorem also does not lift the released CLI's baseline requirement or resource caps. Independent inclusion probabilities satisfying $1-e^{-Ts_i}\le q_i\le\min(1,Ts_i)$ inherit the formal sharp comparison by squeezing their expected costs, but that is a mathematical statement on supported inputs, not an implementation of arbitrary enormous populations. The finite expression can be vacuous at ordinary thresholds such as $0.1$.

An earlier factor-320 theorem covers grids containing budget 1 at fixed $\tau\le1/8$. Its missing-baseline obstruction uses $P=1$, $m=10j$, $\mathcal{K}=\{9j\}$, and increasingly stringent confidence; there $\rho=(36/5)\log(1/\delta)$ diverges [1]. It does not contradict the present joint limit. Conversely, this result does not establish a confidence-uniform finite factor for arbitrary grids at fixed threshold. The confidence restriction also keeps $L$ away from zero; dropping that condition admits census lotteries that can beat NEGEXP by an unbounded factor [1].

## 8. Prior art, provenance, and open questions

Aslam, Popa, and Rivest give NEGEXP, randomized-subset auditing, and multi-target reuse [2]. Checkoway's near-optimality discussion explicitly restricts its statement to independent sampling and notes possible improvements from correlated methods [5]. Fitas supplies the continuous integer-budget envelope and its $1/e$ coefficient, geometric control, and adaptive lower bounds through score bands [3]. Sarkar and Baichoo likewise use geometric levels and disjoint bands [6]. Anthony and Salehzadeh Nobari provide a close finite-corpus zero-history lower-bound precedent [4]. These are substantive antecedents. Different experiments and comparators do not establish novelty, nor imply that earlier work ignores stored pools or caching.

Older safeguards inspection theory is a particularly important unresolved comparison. Avenhaus and colleagues study stratified inspection allocation and give proportional allocation in a small-falsification regime; their 1996 account explicitly points to optimal without-replacement IAEA sampling in earlier work [7]. Avenhaus and Canty's 2007 account describes choosing stratum sample sizes to control nondetection when falsification is concentrated in one stratum, and also when it is distributed across strata, with optimality under prior announcement [8]. Krieger and Burr compare exact hypergeometric inversion with the approximate IAEA formula for one homogeneous stratum [9]. Hypergeometric calculations and rare-falsification allocation are therefore established ingredients.

The bounded review did not obtain Avenhaus and Canty's 1989 original, *Re-examination of the IAEA Formula for Stratified Attribute Sampling*, or the relevant full proofs in *Compliance Quantified* [10]. It remains unclear whether those comparator classes include arbitrary random sample sizes, cross-stratum correlations, and expected-cost certification lotteries. This is an unresolved priority question, not permission to presume that the older results use only replacement sampling or a weaker design. The candidate contribution is the explicit uniform finite bound, its sharp consequence for every declared best-of-N grid, and the demonstrated failure of monotonicity alone. No claim of established novelty is made.

The work assumes correct fixed labels, unit costs, equal prompt weights, and no free cross-item label information. Annotation error, unequal costs, duplicate information, population generalization, and efficiency on nonzero tables require different analyses. The counterexample establishes a boundary but not necessary structural conditions. Independent proof review and a complete safeguards comparison are needed before stronger scientific claims. No real-model inference, human-label study, or deployment benefit was measured.

The project was commissioned by Larry Mai and developed with substantial Codex multi-agent assistance. Codex performed the mathematical development, programming, literature assessment, and internal checks; agent reviews are not peer review. Larry has not personally verified these results, and authorship does not demonstrate independent derivation or research ownership. The study used existing local software without downloading packages, datasets, or model weights, or contacting external researchers. No study-model inference was performed: the scientific measurements use synthetic loss tables. Earlier literature verification read primary-source web pages. This manuscript consolidates the frozen record and adds no external validation.

## References

[1] Larry Mai, with substantial Codex assistance. *ai-goodhart*, v0.7 (2026), immutable source and evidence at ba573d604e3810d7edc9780d57ffea0ff8785296. [Frozen release](https://github.com/larrymai33/ai-goodhart/tree/ba573d604e3810d7edc9780d57ffea0ff8785296), including structural proof, exact checks, protocol, and provenance; [structural report and reproduction commands](https://github.com/larrymai33/ai-goodhart/blob/ba573d604e3810d7edc9780d57ffea0ff8785296/docs/sharp-grid-report.md).

[2] Javed A. Aslam, Raluca A. Popa, and Ronald L. Rivest. *On Auditing Elections When Precincts Have Different Sizes*. EVT (2008), Sections 8, 12, and 13.2. [Primary paper](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/).

[3] Ricardo Fitas. *The geometry of AI validation: From structural blindness to reusable audits*. arXiv:2608.21496v2 (2026), Section 2.4 and Supplements S2, S5, and S7.2. [Primary preprint](https://arxiv.org/html/2608.21496v2).

[4] Martin Anthony and Kaveh Salehzadeh Nobari. *Finite-Sample Coverage Audits for High-Recall Candidate Generation: Certification and Learning-Theoretic Design*. arXiv:2607.21480v1 (2026), Theorem 13. [Primary preprint](https://arxiv.org/html/2607.21480v1).

[5] Stephen Checkoway. *Methods of Post-election Confidence-level Auditing*, Section 4.10. [Primary report](https://checkoway.net/papers/re/re.pdf).

[6] Sarkar and Baichoo. *Cheap to Draw, Expensive to Trust: Certifying Test-Time Scaling Curves*. arXiv:2609.40190v1 (2026), Appendix C. [Primary preprint](https://arxiv.org/html/2609.40190v1).

[7] Rudolf Avenhaus, Morton Canty, D. Marc Kilgour, Bernhard von Stengel, and Shmuel Zamir. *Inspection games in arms control*. European Journal of Operational Research 90(3), 383-394 (1996), especially p. 388. [Publisher record](https://doi.org/10.1016/0377-2217%2895%2900261-8).

[8] Rudolf Avenhaus and Morton Canty. *Formal Models for NPT Safeguards*. Journal of Nuclear Materials Management 35(4), 69-76 (2007), especially p. 71. [Journal full text](https://resources.inmm.org/system/files/jnmm/vol_35/V-35_4.pdf).

[9] Krieger and Burr. *Comparison of an Exact to an Approximate Sample Size Calculation for Attribute Testing*. Journal of Nuclear Materials Management 44(3), 45-48 (2016). [Journal full text](https://resources.inmm.org/system/files/jnmm/vol_44/V-44_3.pdf).

[10] Rudolf Avenhaus and Morton Canty. *Compliance Quantified* (1996). Publisher summaries for [Chapter 2, Attributes Sampling](https://doi.org/10.1017/CBO9780511526510.004), and [Chapter 9, Inspector Leadership](https://doi.org/10.1017/CBO9780511526510.011). Full chapter proofs were not obtained in the bounded review.
