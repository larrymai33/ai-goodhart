# Cached audit reference implementation: v0.13.1

This release makes the [v0.13 cached likelihood construction](cached-likelihood-audit.md)
executable through a bounded rational callback API. It adds exact sampling,
conservative likelihood arithmetic, a finite proposal cap, and a fully
charged deterministic fallback. The [numerical proof](cached-reference-numerics.md)
establishes the guarantees for that rounded and capped construction.
This is supporting software and proof completion for the existing result;
it is not a new generic testing method or evidence of real-model savings.

For the original 32-prompt, 64-candidate, seven-budget instance, the
implementation chooses a deterministic prefix costing **2048 labels**.
It does not improve the stronger **1934.2 expected-label upper benchmark**
from the [monotone-placement report](monotone-placement-report.md).
That benchmark's disclosed blind-certification lottery is a different
auditor and is not implemented here. The earlier mathematical and measured
artifacts remain separate from this release's evidence.

## Callback usage

The complete interface is the Python callback API; this release adds no
production CLI or external annotation integration. Run the following from
the repository root with the installed Python standard library:

```python
from fractions import Fraction as F
from goodhart_audit.cached import audit
from goodhart_audit.cached_math import design

budgets = (1, 2, 4, 8, 16, 32, 64)
tau, epsilon, delta = F(1, 10), F(1, 160), F(1, 20)
plan = design(32, 64, budgets, tau, epsilon, delta)

def oracle(prompt_index, rank_index):
    # A fixed synthetic table; both callback indices are zero based.
    # Replace this with access to a fixed, correct rational loss table.
    return F(3, 32)

result = audit(32, 64, budgets, tau, epsilon, delta, oracle)
print(plan.mode, plan.expected_label_bound)
print(result.status, result.distinct_labels, result.proposals)
```

This example returns:

```text
prefix 2048
certified 2048 0
```

The constant loss is exactly `tau - epsilon`. Both `design` and `audit`
default to `eta=F(1)`. The design is computed without querying the oracle;
`audit` builds and validates its own design. A nonempty tuple or list of
distinct budgets is accepted and sorted into increasing order.

The returned immutable result includes the design, acquisition trace,
per-budget status and passage reason, proposal counts, distinct-label
count, and any proposal-cap fallback reason. Each trace entry records one
actual first acquisition. A cached item never triggers another oracle
call. `expected_label_bound` is a uniform **expected** cost bound on the
supplied-margin class, not a maximum realized count and not a claim about
an arbitrary table's actual margin.

## Experiment and guarantees

The experiment fixes one correct loss `y[p,r]` in `[0,1]` for every item.
For each originally declared budget `n`, its risk is the winner-weighted
mean `R_n` defined in the [numerical proof](cached-reference-numerics.md#1-experiment-and-notation).
The auditor issues one certificate asserting `R_n <= tau` for **every**
original budget. It does not issue independently selectable budget
certificates or simultaneous confidence intervals.

On each fixed unsafe table, the chance of a false whole-family certificate
is at most `delta`, under the stated randomness assumptions. On every safe
table in the executable domain, including `R_n = tau`, finite proposal
caps and exact fallback ensure completion. Exact unsafe evaluation returns
`not_certified`; statistical passage can still certify an unsafe table
with probability bounded by `delta`. Malformed callbacks or unsupported
losses raise exceptions rather than providing a certificate.

Let `theta = tau - epsilon`, let `A = P*k_epsilon` be the deterministic
prefix cost, and let `B_minus` be the rounded walk's cached acquisition
bound. The design chooses its mode using only these known quantities:

$$
\sup_{\max_n R_n\le\tau-\epsilon}\mathbb E T
\le \min\{A,B_{\rm minus}+\eta\}.
$$

It chooses prefix mode when `A <= B_minus + eta`; otherwise it chooses
likelihood mode. The positive surcharge `eta` bounds the expected extra
labels purchased by fallback on the margin class. If the selected
likelihood design exceeds the implementation's proposal limit, the
factory rejects it before acquiring labels. It does not silently choose
a costlier mode while retaining the smaller bound.

For `tau <= 1/8`, `epsilon <= tau/16`, `delta <= 1/4`, and successive
budgets at least doubled, the design additionally verifies the rounded
drift condition needed for the constructive bound `17F + eta`. Here
`H = tau*log(1/delta)/epsilon^2`, `e_r = max_n w_n(r)`,
`G = sum_r min(P,H*e_r)`, and `F = min(A,G)`, as in v0.13.
Only a design satisfying these conditions receives
`factor_guarantee == "17F + eta"`. Other accepted designs retain the
displayed cost bound without this factor label. The code does not
implement the separate grouped construction for the all-grid theorem.

## What the implementation checks

[The design module](../goodhart_audit/cached_math.py) uses integer and
`Fraction` arithmetic. Rational logarithm enclosures round each
log-likelihood increment downward and the passage threshold upward.
Integer square-root enclosures support an affinity tail bound for the
implemented rounded walk. A rational logarithmic inequality certifies the
proposal cap without constructing a huge rational power. These are
conservative arithmetic checks, not floating-point approximations treated
as certificates.

[The callback engine](../goodhart_audit/cached.py) samples winner ranks
using exact integer binomial masses and samples prompt indices uniformly.
Every proposal uses a fresh auxiliary Bernoulli coin for the sampled
loss, including cache hits. Losses zero and one have deterministic coins.
Exact support completion takes precedence over a simultaneous statistical
crossing. At an unpassed proposal cap, the engine acquires the remaining
prefix; if its worst-case completion bounds do not certify, it censuses
the remaining positive union support. Every new fallback label is charged.
The final decision also rejects an earlier statistical pass when later
acquisitions already imply risk above the threshold, even if that target's
support remains incomplete. A failing-then-passing actual-design regression
records this consistency correction; it acquires no extra labels.

The default generator is `secrets.randbelow`. The theorem assumes
independent uniform draws; merely naming a generator or checking its
integer range does not prove this assumption. An injected `randbelow`
callback supports reproducible tests and demonstrations. A seeded run
does not empirically establish the theorem's risk guarantee.

The executable limits are:

| Quantity | Limit |
| --- | --- |
| Pool size | 1024 |
| Total items | 100000 |
| Rank-target pairs | 250000 |
| Each exact design parameter's numerator and denominator | 64 bits |
| Total permitted proposals in likelihood mode | 2000000 |
| Oracle-loss denominator | 1000000 |

Dimensions and budgets must be strict integers. Parameters and losses
must be integers or `Fraction` values; floats and booleans are rejected.
The design requires `0 < epsilon < tau < 1`, `0 < delta < 1`, and
`eta > 0`. Precision refinement and intermediate rational sizes also have
explicit limits documented in the [numerical contract](cached-reference-numerics.md#10-executable-rational-contract-and-limits).
These are necessary limits, not a promise to accept every combination
below them. A cap on virtual proposals does not bound oracle latency,
random-number rejection bits, or wall-clock time.

The ideal rounded and capped construction in the proof covers arbitrary
fixed real losses. The executable program covers only its supported
rational domain. Because it rejects unsupported safe labels, this program
alone is not an admissible all-real-table auditor for the original minimax
infimum. Its guarantee is code conformance on accepted inputs; the broader
theorem belongs to the separately stated ideal construction.

## Checks and demonstration evidence

There are three different kinds of evidence: proof and arithmetic
certificates, implementation tests, and illustrative synthetic runs.
They should not be read interchangeably.

Before the final source freeze, the focused standard-library command

```text
python -B -S -m unittest tests.test_cached_math tests.test_cached tests.test_cached_exact tests.test_cached_reference_runner
```

passed 49 tests: 9 numerical-design tests, 22 callback-engine tests,
5 exact stopped-process/actual-path checks, and 13 demonstration-runner
tests. The stopped-process checks independently enumerate a
small two-proposal sample space and use a rational recurrence for a
small binary population. They check safe completion, unsafe certification
probability, and charged costs in those cases. They do not exhaust all
fractional tables; the universal statements rely on the proof. The
callback example above was also executed with its displayed output.

The completed demonstration has 45 fixed runs: `P` in `{1,32,1024}`,
`m=64`, the seven dyadic budgets, five scenarios (all-zero, constant
margin, rare-top, constant boundary, and constant unsafe), and seeds
`11,29,47`. Exact table definitions and design parameters were fixed
in the [protocol](../experiments/cached_reference_protocol.json) before the saved runs. These demonstrations show execution
paths and label/proposal accounting. Three seeds per scenario cannot
establish statistical efficiency, uniform risk control, or real-model
usefulness, and no such claim is intended.

| Evidence item | Status |
| --- | --- |
| Frozen demonstration protocol and commit | `0e4481ddfb2281ccf72a9a049180c447910dfb8b` |
| Reviewed source commit | `1fd785bf7899ec8aacc33f842bf39eca3a960d9d` |
| Saved result and exact scenario definitions | [108,290-byte JSON](../results/cached_reference.json), 45 runs and ten direct/imported source pins |
| Byte-for-byte reproduction and artifact hash | A second full run is identical; SHA-256 `8deb0b8fa3fa7d7e2dc5f183097c85b528be0a2b1eee238ebdd97a3b641e35f9` |
| Full repository test command and count | `python -B -m unittest discover -s tests -q`: 331 tests pass |
| Final optimized-Python focused test result | All 49 focused tests pass under `-B -S -O` |
| Prior evidence integrity checks | The original saved-evidence verification command passes; earlier pinned sources remain unchanged |

All ten source pins matched committed bytes before the run and again after
both runs. The protocol follows exploratory proof and implementation work;
it is not external preregistration. Both saved runs used Python 3.11.0.
Byte reproduction assumes compatible seeded-generator behavior; the
statistical theorem does not depend on those particular seed sequences.

For `P=1` and `P=32`, every demonstration uses prefix mode and acquires
64 and 2048 labels respectively, with zero virtual proposals. Thus even
the zero-loss examples do not show label savings in these geometries.

For `P=1024`, the design chooses likelihood mode. Its conservative
margin-class expected bound is below **39,476.053 labels**, including
the surcharge `eta=1`. The cap is 260,357 proposals per budget, at most
1,822,499 across the seven budgets. The following are the actual counts
for seeds `11,29,47`, in that order:

| Fixed synthetic table | Distinct labels | Virtual proposals |
| --- | --- | --- |
| All zero | 2665, 2650, 2663 | 3031, 3031, 3031 |
| Constant margin loss `3/32` | 25964, 29461, 33609 | 55563, 131446, 80147 |
| Rank-zero loss `3/32`; other ranks zero | 3464, 3404, 3480 | 11563, 10152, 11186 |
| Constant safety-boundary loss `1/10` | 65536, 65536, 65536 | 260357, 260357, 260357 |
| Constant unsafe loss `17/160` | 65536, 65536, 65536 | 260357, 260357, 260357 |

The boundary and unsafe runs trigger the charged fallback. They lie
outside the supplied-margin efficiency class, so its expected-cost bound
does not apply to them. All 36 safe matrix runs certified; none of the
nine unsafe matrix runs certified. These observed outcomes check the
recorded software paths and do not establish a general error rate.
Every prompt in a given scenario has the same fixed rank pattern; this
is not evidence from diverse prompts or models.
Here the deterministic prefix has all 64 ranks, so fallback completes the
full support during its prefix phase; no extra census-phase acquisition
is needed in this matrix.

To reproduce the demonstration, choose a fresh output path:

```console
python -B -S -m experiments.run_cached_reference --out artifacts/local/cached-reference-reproduction.json
```

The runner rejects overwrites and source drift, verifies charged labels
and exact table truths independently of the engine, and retains a hash
of each acquisition trace. It stores no full traces or runtime results.

## Scientific scope and provenance

Likelihood-ratio testing, conservative threshold crossing, caching fixed
labels, and exponential tail bounds are established ingredients; the
[v0.13 attribution note](all-grid-minimax-priority.md) records the primary
comparisons. This release supplies an executable reference and the
rounding/fallback argument needed to retain its stated cost guarantee.
It establishes neither methodological priority nor an improved
physical-label constant.

An exploratory floating-point checkpoint screen produced a bound estimate
around 1993.37 on the original instance, above the 1934.2 benchmark. That
screen is neither an exact cost certificate nor an impossibility result.
The separately explored stopped-occupancy refinement is excluded from
this implementation; its larger-instance numerical bound reductions are
not this release's guarantees or measured acquisition savings.

Codex developed the implementation, numerical argument, tests, and this
report, with separate agent contexts reviewing the mathematics, API,
resource limits, and claims. These are assisted-session checks, not
independent human verification. The [contribution disclosure](provenance.md)
records the wider project history. No owner-authored derivation, personal
verification, real-model experiment, or external validation is inferred
from this work. This phase uses no model inference, downloads,
installations, or outreach.
