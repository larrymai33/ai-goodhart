# Exact coverage between audited budgets

The v0.13.2 supporting analysis answers a scope question: what follows about
budgets omitted from a safety audit's declared grid? It adds an attributed
convexity application, an exact transfer rule, two counterexamples, and a
small rational helper library. It does not change the existing seven-budget
decision or improve its label-cost bounds. The [proof](grid-coverage.md)
contains the universal arguments and predecessor comparison.

## What changes for an audit user

For fixed losses in $[0,1]$, candidate pools, rankings, and the same without-replacement selector,
endpoint upper bounds imply

$$
R_n\le \frac{n(b-n)}{a(b-a)}U_a+
            \frac{n(n-a)}{b(b-a)}U_b,
\qquad a\le n\le b.
$$

The bound can be clamped at one. If both endpoint bounds are $s$, the maximum
integer-budget factor on that interval is
$\rho(a,b)=\lfloor(a+b)^2/4\rfloor/(ab)$. Thus a grid certificate at level
$s$ covers all intervening budgets at $\tau$ when every interval satisfies
$s\rho\le\tau$. The same false-certificate probability transfers through
this deterministic implication. The endpoint premises must actually be
certified; a supplied efficiency margin is not evidence that they hold.

For $m=64$, a grid sufficient to transfer level $3/32$ to full-family level
$1/10$ is

```text
1, 2, 3, 5, 8, 13, 21, 35, 58, 64
```

Ten endpoints are minimal under this sufficient interval rule. This is not
global optimality over all inference methods or all audit algorithms.
The exact rule gives 11 endpoints for $m=128$, 15 for $m=1024$, and 24 for
$m=100000$, at the same two levels. Endpoint count is not label cost.

The original seven dyadic budgets do not support that transfer. Both of the
following fixed tables have maximum declared-grid risk exactly $3/32$:

| Constructed table, 32 prompts and 64 ranks | Omitted maximum | Exact risk | Approximate percentage |
|---|---:|---:|---:|
| Every prompt: rank 1 loss $3/32$, rank 2 loss $189/1024$, others zero | 48 | $27/256$ | 10.546875% |
| Rank 1 positive in three prompts, rank 2 positive in five, all other cells zero | 51 | $2159/21504$ | 10.039993% |

These are counterexamples to extending a declared-grid certificate without
a valid transfer argument. They do not contradict the existing theorem,
which certifies exactly its declared targets. The first also attains the
uniformly sharp $9/8$ factor for dyadic grids; sharpness need not hold on
each individual interval. Neither table is real model data.

## Exact helper usage

```python
from fractions import Fraction as F
from goodhart_audit.coverage import covering_grid, interpolate_upper

grid = covering_grid(64, F(3, 32), F(1, 10))
assert grid == (1, 2, 3, 5, 8, 13, 21, 35, 58, 64)

bound = interpolate_upper(32, 64, 48, F(3, 32), F(3, 32))
assert bound == F(27, 256)  # exceeds 1/10
```

These functions perform deterministic arithmetic; they do not issue a
statistical certificate. Budgets must be integers in $[1,100000]$, levels
must be integers or `Fraction` values in $[0,1]$, and the certified level
cannot exceed the target level. Booleans and floats are rejected. The
singleton pool, zero level, adjacent budgets, and equal positive levels
are covered by the documented rules.

An endpoint audit at a stricter level can fail to certify a table that is
safe at the full-family threshold. This transfer therefore does not by
itself preserve the earlier requirement of almost-sure finite completion
on every boundary-safe table. A new auditor claiming that property must
account for its own completion mechanism and every fallback label.

## Fixed calculation and verification

Protocol commit `b28cb3b` preceded the saved exhaustive calculation. It
followed exploratory derivation, a floating-point LP screen, and targeted
exact checks; it is internal specification, not external preregistration.
Reviewed scientific source freeze
`a2ac59e5b33316d9e5ad73726a09fc9fffcf01cd` preceded both saved runs.

The [protocol](../experiments/grid_coverage_protocol.json) fixes the matrix;
the [checker](../experiments/check_grid_coverage.py) records six SHA-256
source pins, rejects altered or nonexact protocol data, checks source drift,
and refuses to overwrite an existing output. All scientific values in the
saved result use integers or rational strings, without binary floats.

| Exact check | Count |
|---|---:|
| Pascal second-difference identities, pools through 64 | 85,281 |
| Coordinatewise chord inequalities, pools through 24 | 250,470 |
| Binary tables checked by enumerating selected subsets, pools through 8 | 510 |
| Chord comparisons on those subset-derived risk curves | 20,488 |
| Grid comparisons against an independent shortest path | 384 |
| Edges examined by that shortest-path calculation | 18,240 |

The two original-instance witnesses retain all 64 exact risks in the
[saved artifact](../results/theory/grid_coverage.json). Finite checks
support the arithmetic; the proof supplies the unbounded quantifiers.

Both full runs produced the same **9,958 bytes**, SHA-256
`a9e32708ce5cf95d833d7aa64ead905a5ab0c14c0798df67077eacb65ec73051`.
All six pins match the scientific source freeze. The complete suite passed
**344 tests**; 13 focused tests also passed with site packages disabled,
normally and under optimized Python. A fresh agent review additionally
checked 4,416 small rational grid cases and six dyadic equality examples.
These assisted-session checks are not independent human verification.

To reproduce with the Python standard library, choose a fresh output path:

```console
python -B -S -m experiments.check_grid_coverage --out artifacts/local/grid-coverage-reproduction.json
python -B -S -m unittest discover -s tests -p "*coverage.py" -q
```

## Attribution and research status

The [proof's predecessor comparison](grid-coverage.md#5-predecessors-helpers-and-limits)
derives the normalized-risk convexity from the established expected-minimum
result of Myatt and Ronayne, and compares the transfer with Fitas's
total-variation grid extension. The underlying convexity and general
interpolation machinery are not new claims. Scientific priority for the
specific application remains unestablished.

This update makes a scope limitation usable and checkable. It does not
supply a new generic auditing method, measured model savings, independent
human research ownership, or evidence of fellowship competitiveness. No
downloads, installations, model inference, or external outreach occurred.
