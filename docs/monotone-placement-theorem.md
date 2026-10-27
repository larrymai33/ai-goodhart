# Canonical placement of common-safe finite priors

Candidate result, 27 October 2026. When target weights share one decreasing
order, a zero-prefix / variable-middle / one-suffix arrangement minimizes
every target's worst null risk within a specified category-count class.
A comparison between finite-population experiments then reduces that
class's strongest fixed-multiplier lower certificates to a finite frontier.

For the original 32-prompt, 64-item, seven-budget decision, this construction
gives the conservative conclusion **more than 1,100 expected distinct
labels**. It retains the original global certificate and margin class.
The separate zero-error problem has deterministic minimax cost exactly
2,036, and randomized minimax cost between 2,034 and 2,036.

The lower certificates use the classical sequential-testing dynamic
program already described in the [finite-decision theorem](finite-decision-theorem.md).
No new dynamic-programming method, unrestricted optimal prior, globally
optimal multiplier, or practical audit engine is claimed. The
[priority comparison](monotone-placement-priority.md) treats antecedents
and scope separately. The argument was developed and checked with Codex
assistance and has not received independent human review; see the
[contribution disclosure](provenance.md).

## 1. Fixed experiment and the two error settings

The concrete experiment throughout the numerical application is

$$
P=32,\quad m=64,\quad
\mathcal K=\{1,2,4,8,16,32,64\},
\qquad\tau=\frac1{10},\quad\epsilon=\frac1{160}.
\tag{1}
$$

Each prompt pool has 64 distinct items in a fixed total rank order, with
rank 1 best. Querying one item reveals its fixed, correct loss
$y_{p,r}\in[0,1]$ at unit cost. No actual labels are free, and no known
relationship reveals another item's label without querying it. Computation
is not charged. The budget-$n$ selector draws a uniform $n$-subset without
replacement and returns its best-ranked member, with

$$
w_n(r)=\frac{\binom{64-r}{n-1}}{\binom{64}n},
\qquad
R_n(y)=\frac1{32}\sum_{p=1}^{32}\sum_{r=1}^{64}w_n(r)y_{p,r}.
\tag{2}
$$

Impossible binomial choices are zero. A $\delta$-valid auditor issues one
whole-family certificate asserting $R_n(y)\le\tau$ for every originally
declared budget. On every fixed table with at least one risk above $\tau$,
its probability of ever certifying is at most $\delta$. It certifies after
finitely many queries almost surely on every safe table, including
boundary-safe tables. Validity and completeness apply to all fractional
tables in $[0,1]^{2048}$, even though the proof priors below are binary.

For $\delta\in\{0,1/20\}$ define

$$
\mathcal Y_\epsilon={y:\max_{n\in\mathcal K}R_n(y)\le3/32\},
\qquad
C^*_{\delta}(1/160)
=\inf_A\sup_{y\in\mathcal Y_\epsilon}\mathbb E_yT_A(y),
\tag{3}
$$

where $T_A$ counts distinct acquired labels and the infimum uses one
admissible auditor for the whole class. Write $C^{\rm det}_{0}(1/160)$
for the same infimum restricted to deterministic zero-error auditors.
The known design margin is not trusted evidence about an unknown table.

The conclusions proved below are

$$
\begin{aligned}
C^*_{1/20}(1/160)&>1100,\\
2034\le C^*_{0}(1/160)&\le2036,\\
C^{\rm det}_{0}(1/160)&=2036.
\end{aligned}
\tag{4}
$$

The zero-error statements concern a different admissible class from the
original $\delta=1/20$ objective. They are not lower bounds for
$C^*_{1/20}$. Section 7 also records the elementary mathematical upper
bound $C^*_{1/20}\le9671/5=1934.2$, using a blind certification lottery
permitted by the objective.

## 2. Simultaneously optimal placement with fixed category counts

Consider a more general finite list of $M$ cells and any family of
nonnegative weight rows $a_n(i)$ sharing the order

$$
a_n(1)\ge a_n(2)\ge\cdots\ge a_n(M)
\quad\text{for every }n.
\tag{5}
$$

Assign $H$ cells fixed loss zero, $b$ cells fixed loss one, and $N$ cells
to a variable set $U$, where $H,N,b$ are nonnegative integers,
$H+N+b=M$, and $0\le k\le N$. Within $U$, a null prior uniformly
chooses exactly $k$ cells to have loss one and sets the remainder to zero.
These are labels in the proof prior; their fixed values do not become
trusted free evidence for the actual auditor.

For a target row, the maximum null risk over this prior's support is

$$
\Phi_n=
\sum_{i\text{ fixed one}}a_n(i)
+\operatorname{Top}_k\{a_n(i):i\in U\},
\tag{6}
$$

where $\operatorname{Top}_k$ is the sum of the $k$ largest listed values.
Every null table is safe for every target precisely when all these maxima
meet the corresponding safety bounds. Under the common order (5), setting
the first $k$ variable cells to one attains all these maxima simultaneously.

**Placement theorem.** For fixed $H,N,b,k$, the canonical arrangement

$$
\underbrace{0,\ldots,0}_{H}\quad
\underbrace{U,\ldots,U}_{N}\quad
\underbrace{1,\ldots,1}_{b}
\tag{7}
$$

simultaneously minimizes $\Phi_n$ for every row satisfying (5).

**Proof.** Order the category symbols as $0<U<1$ and remove adjacent
inversions. For an inverted pair $i<j$, let
$\Delta=a_n(i)-a_n(j)\ge0$ for any one row.

* Swapping a fixed one at $i$ with a variable cell at $j$ lowers the fixed
  contribution by $\Delta$. The variable top-$k$ sum increases by at most
  $\Delta$: each candidate subset sum increases by either zero or
  $\Delta$, so its maximum increases by at most $\Delta$.
* Swapping a variable cell at $i$ with a zero at $j$ replaces one variable
  weight by a smaller value. Its top-$k$ sum cannot increase.
* Swapping a fixed one at $i$ with a zero at $j$ lowers the fixed
  contribution by $\Delta$ and leaves the variable weights unchanged.

Every exchange is nonincreasing for each target row simultaneously.
Removing all inversions terminates at (7), with the category counts and
$k$ preserved. Thus (7) has no larger maximum risk for any row than the
initial arrangement. Equal weights cause no difficulty. $\square$

The theorem optimizes placement for this category-count class. It does
not compare arbitrary dependent priors, fractional encodings, or other
choices of counts.

## 3. More variable cells give a harder relaxed count experiment

For integers $k\ge0$, $d\ge1$, and $k+d\le N$, let $\Pi_{N,k}$ and $Q_{N,k+d}$ be uniform binary
fixed-count priors on $N$ variable cells. The outside table has the same
deterministic values under both hypotheses and can contain both zeros
and ones. In the relaxed experiment these outside values are supplied
for free. For $\lambda\ge0$, define

$$
V_{N,k,d}(\lambda)=
\inf\{\mathbb E_\Pi T+\lambda Q(\text{certificate}):
\Pi(\text{certificate})=1\},
\tag{8}
$$

where $T$ counts variable-cell acquisitions. A policy may abstain on
null-impossible histories.

**Population comparison.** If $k+d\le N_1\le N_2$, then

$$
V_{N_1,k,d}(\lambda)\le V_{N_2,k,d}(\lambda).
\tag{9}
$$

The analogous comparison also holds for the minimum expected null cost
subject to a fixed alternative certificate-probability constraint.

**Proof.** Generate the larger experiment by first choosing a uniform
$N_1$-subset $S$ of its $N_2$ positions, with this same law under both
hypotheses. Place the appropriate uniform positive subset inside $S$,
and set the outside positions to zero. The marginal positive set is
uniform over the larger population: every possible set of $k$ positives,
or of $k+d$ positives, is contained in the same number of choices of $S$.

Now reveal $S$ and supply its outside zeros for free. Conditional on $S$,
the remaining problem is exactly the smaller experiment. Simulate any
larger-population policy in this more informative experiment by answering
outside-$S$ requests for free. Both certificate probabilities are preserved,
and charged queries cannot increase. The same simulation preserves null
completeness. Taking infima proves both assertions. $\square$

The subset $S$ is an auxiliary variable in the comparison proof. It is
not additional evidence available to an actual auditor in the original
experiment.

## 4. The exact canonical frontier for the original decision

Flatten the original cells in rank-major order, using prompt order within
each rank. All rows $a_n(i)=w_n(r)/32$ then satisfy (5). Fix

$$
M=2048,\qquad b+k=192,\qquad d=13,
\qquad k\in\{0,\ldots,192\}.
\tag{10}
$$

For a canonical layout with $H$ zero cells, the variable population is
$N=M-b-H$. Its exact worst null risks are

$$
\Phi_n(H,k)=
\sum_{i=M-b+1}^{M}a_n(i)
+\sum_{i=H+1}^{H+k}a_n(i).
\tag{11}
$$

For fixed $k$, these quantities are nonincreasing in $H$. The largest
feasible variable population is therefore obtained at

$$
H_k=\min\left\{H\in\{0,\ldots,1843\}:
\Phi_n(H,k)\le3/32\text{ for every }n\in\mathcal K\right\},
\qquad N_k=2048-(192-k)-H_k.
\tag{12}
$$

This minimum exists. At $H=1843$, all possible positive positions lie in
the last 205 cells, and $N=k+13$. These positions have ranks at least 58.
For $r\ge33$, the adjacent-budget ratio gives

$$
\frac{w_{n+1}(r)}{w_n(r)}
=\frac{n+1}{n}\frac{64-r-n+1}{64-n}\le1
\quad(1\le n<64)
\tag{13}
$$

on positive weights, since $(n+1)r\ge65$; terminal zeros preserve the
conclusion. Thus every relevant nonuniform weight is at most $w_1=1/64$.
Any placement of the 192 null positives in these positions has every
risk at most $192/2048=3/32$.

Every null table in a feasible layout has uniform-target risk exactly
$3/32=\tau-\epsilon$. Replacing its variable count $k$ by $k+13$ gives
total positive count 205, so every alternative table has

$$
R_1=\frac{205}{2048}=\frac1{10}+\frac1{10240}>\tau.
\tag{14}
$$

The placement theorem and population comparison have the following exact
class consequence: for fixed $k$, $b=192-k$, and multiplier $\lambda$,
the layout at $H_k$ maximizes the relaxed dual lower certificate over all
feasible three-category layouts with those counts. Indeed, any feasible
layout can be sorted without increasing a worst risk, and any resulting
feasible population is at most $N_k$; (9) then applies. Subtracting the
same $\lambda\delta$ preserves this comparison.

This result does not select an optimal $k$, unrestricted prior, or
multiplier. The accompanying
[protocol](../experiments/monotone_placement_protocol.json) evaluates the
193 exact frontiers at the two registered multipliers 2048 and 4096.
Selection within that finite list is distinct from global optimization.

## 5. A transparent common-safe witness above 1,100 labels

The following slightly smaller population gives a simple description:

* Ranks 1--9: all 288 cells have fixed loss zero.
* Ranks 10--60, and prompts 1--16 at rank 61: the $N=1648$ variable cells.
* Prompts 17--32 at rank 61, and all ranks 62--64: 112 fixed losses equal to one.

The null uniformly chooses 80 variable cells to have loss one; the
alternative uniformly chooses 93. Their identical outside table contains
both fixed zeros and fixed ones. Every null has 192 positives and every
alternative has 205.

The worst placement of the 80 variable positives fills ranks 10 and 11
and half of rank 12. Thus the exact worst null risk for target $n$ is

$$
\tfrac12w_n(61)+\sum_{r=62}^{64}w_n(r)
+w_n(10)+w_n(11)+\tfrac12w_n(12).
\tag{15}
$$

| Budget | Worst null risk |
|---:|---:|
| 1 | $3/32$ |
| 2 | $275/4032$ |
| 4 | $118561/1270752$ |
| 8 | $49766990/553270671$ |
| 16 | $114348180/3258149507$ |
| 32 | $204880/228324159$ |
| 64 | $0$ |

Every entry is at most $3/32$ by exact rational comparison. The entire
null support is therefore in the original whole-family efficiency class,
and (14) makes every alternative strictly unsafe. Budget 1 supplies the
unsafe alternatives; the other declared budgets are retained through the
common-safe-support check.

For completeness, the exact lower calculation is as follows. Put

$$
(N,k,d,\lambda)=(1648,80,13,4096),
\qquad D=\binom Nk\binom N{k+d},
$$

and define the masses of one ordered prefix of $t$ observed bits with $s$
positives by

$$
A_t(s)=\binom{N-t}{k-s}\binom N{k+d},
\qquad
B_t(s)=\binom{N-t}{k+d-s}\binom Nk.
\tag{16}
$$

Binomial coefficients outside their feasible range are zero. These are
ordered-prefix masses multiplied by $D$, not aggregate state masses; no
factor $\binom ts$ is included. Set $W_N(s)=0$, set $W_t(s)=0$ when
$A_t(s)=0$, and otherwise use

$$
W_t(s)=\min\{\lambda B_t(s),
A_t(s)+W_{t+1}(s)+W_{t+1}(s+1)\}.
\tag{17}
$$

This is the exact value in (8), multiplied by $D$. Immediate certification
pays $\lambda B$; continuation pays one query under the null, with mass
$A$, and adds its two child costs. Null-impossible histories may abstain
for free; alternative-impossible histories may certify for free. Pascal's
identity supplies the child probability weights. At the terminal time,
the two counts are disjoint, so a null-possible history certifies with zero
penalty. Randomized actions cannot improve a minimum of two linear costs.

For adaptive identities, every unseen variable cell has the uniform
remaining-count law under either prior. Giving all common outside labels
for free, whether zero or one, can only reduce the original auditor's
charged cost. Outside queries and delays provide no distinguishing
information. Null completeness excludes positive-probability indefinite
abstention on a null-possible history, and after at most $N$ variable
queries the two totals distinguish the hypotheses exactly. Thus the
finite relaxed problem includes a simulation of every admissible original
auditor. The detailed ordered-prefix argument is also given in the
[finite-decision theorem](finite-decision-theorem.md).

Global validity gives $Q(\text{certificate})\le1/20$, while every null
table must certify. Weak duality and the supremum over the safe class give

$$
C^*_{1/20}(1/160)\ge\frac{W_0(0)}D-\frac{4096}{20}.
\tag{18}
$$

The conservative numerical conclusion $C^*_{1/20}>1100$ is the exact
integer certificate

$$
\boxed{\qquad5W_0(0)>6524D.\qquad}
\tag{19}
$$

The [checker](../experiments/check_monotone_placement.py) evaluates this
clean witness separately from the frontier search, using exact integers.
The more informative relaxed policy is not asserted to be an operational
original auditor. Its outside labels and two-count promise are not trusted
evidence in the original experiment.

## 6. Deterministic zero-error cost is exactly 2,036

**Upper bound.** Query every cell except 12 fixed prompt positions at
rank 64. These omitted cells have total weight $12/2048$ for budget 1
and zero weight for every declared budget at least 2. The acquired labels,
plus worst-case loss one at those 12 positions, therefore give deterministic
upper bounds on every actual risk.

On a margin-class table, the uniform-target upper bound is at most

$$
\frac3{32}+\frac{12}{2048}
=\frac{51}{512}<\frac1{10}.
\tag{20}
$$

Every other target is already known exactly and has risk at most $3/32$.
Thus all margin-class tables certify within 2,036 labels. If the
deterministic upper bounds fail on another table, query the remaining 12
cells and evaluate all risks exactly. This fallback ensures completeness
on all safe tables and never certifies an unsafe one. Hence

$$
C^{\rm det}_{0}(1/160)\le2036.
\tag{21}
$$

**Matching deterministic lower bound.** On any binary table, a zero-error
certificate must have observed at least 1,844 distinct zero labels. If it
has observed only $z\le1843$, completing every unqueried cell by one gives
at least $2048-z\ge205$ positives, so the completion is unsafe for budget
1. A deterministic strategy would follow the identical transcript and
falsely certify that completion.

Fix any deterministic zero-error, all-safe-complete auditor. Answer all
queries at ranks 1--32 with zero. Among its distinct queries at ranks
33--64, answer the first 192 with one and the rest with zero. These answers
are consistent with a fixed table having exactly 192 tail positives and
all other losses zero. Such a table is in the efficiency class by (13),
since every nonuniform tail weight is at most the uniform weight.

If fewer than 192 tail cells have yet been queried, fill unqueried tail
positions to bring the positive total to 192. Such a safe completion
always exists. Completeness excludes a path that indefinitely avoids
certification and further informative queries. A certificate before any
tail zero is observed would have at most 1,024 zeros and is invalid by the
preceding completion argument. Consequently the first 192 positive tail
answers have all been acquired before certification can occur. At that
point the auditor still needs a total of at least 1,844 observed zeros.
It therefore makes at least $192+1844=2036$ distinct queries on the fixed
safe table defined by its answer path.

This is an adversary argument for a deterministic strategy: after the
path is specified, each assigned cell value is fixed, and running that
table reproduces the same path. It proves

$$
C^{\rm det}_{0}(1/160)\ge2036,
\tag{22}
$$

which, with (21), establishes the exact deterministic value.

## 7. Randomized zero error and the original positive-error objective

**Randomized zero-error lower bound.** Take the fixed fractional table
$y_i=p_0=3/32$ at all 2,048 positions. It belongs to the margin class
for every declared target. If a certificate leaves $u\ge15$ cells
unqueried, change those unqueried losses to one. Its uniform risk becomes

$$
p_0+\frac{u(1-p_0)}{2048}
\ge p_0+\frac{15(29/32)}{2048}
>p_0+\frac1{160}=\tau.
\tag{23}
$$

To justify this for a randomized zero-error auditor, consider the finite
set of all tables whose entries lie in $\{p_0,1\}$. For each unsafe such
table, zero-error validity excludes a null set of random tapes that ever
falsely certify. The finite union of these exceptional sets is still
null. Outside that union, the realized deterministic strategy cannot
certify any transcript consistent with an unsafe completion in this set.
Thus (23) forces at most 14 unqueried cells almost surely when auditing
the constant table. It follows that

$$
C^*_{0}(1/160)\ge2048-14=2034.
\tag{24}
$$

The deterministic construction (20)--(21) also upper-bounds the randomized
class, so $2034\le C^*_{0}(1/160)\le2036$. No equality claim for the
randomized value is made.

**A mathematical positive-error upper bound.** With probability $1/20$,
certify without querying; with probability $19/20$, run the zero-error
auditor of Section 6. Its false-certificate probability on any unsafe
table is at most $1/20$, and it is all-safe complete. On the margin class
its expected count is at most

$$
\frac{19}{20}\,2036=\frac{9671}{5}=1934.2.
\tag{25}
$$

This blind lottery is permitted by the stated objective. It is a routine
mathematical bound, not an evidence-based auditing improvement or a change
to the repository's audit implementation. Equations (19) and (25) apply
to the original $\delta=1/20$ problem; (22) and (24) concern zero-error
auditors separately.

## 8. Scope of the reduction and finite calculation

Canonical placement is simultaneously optimal for the stated counts and
common order. The population comparison is for fixed $k,d,\lambda$.
The original application fixes total null positives at 192 and alternative
positives at 205. Its finite frontier search does not prove that those
totals, a three-category prior, or either registered multiplier are optimal
among all possible lower-bound constructions.

The finite calculation checks the original seven declared budgets and
does not substitute a smaller family. The common outside table may include
ones because its values are identical under both proof priors. The actual
fixed-table auditor receives no free labels; revealing those common values
is only the lower-bound relaxation.

The numerical certificate places a nontrivial constraint on worst-case
expected cost for the original finite decision. It is not an exact
positive-error minimax value, a practical statistical engine, a model
experiment, or a resolution of unrestricted general-grid saturation.
Scientific priority and independent human review remain separate questions.
