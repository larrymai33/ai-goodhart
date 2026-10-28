# Finite repeated-screening comparison: working-draft report

The [working proof](repeated-screening-theorem.md) gives two finite ideal-channel
examples in which one repeated-screening auditor has worst expected payment
below a lower bound for every admissible one-report-per-item hybrid auditor.
The same construction also beats the displayed exact-only and cheap-only
lower bounds. This is a theoretical cost comparison, conditional on the
unreviewed analytic proof; it contains no measured LLM performance.

| Example | Repeated-screening upper | One-report hybrid lower | Guaranteed gap at least |
|---|---:|---:|---:|
| Wide margin: N=13,000, c=64 | 2,973 | 3,198 | 75/1066, about 7.0% |
| Small relative margin: N=70,000,000, c=8,192 | 98,855,201 | 128,874,779 | 30,019,578/128,874,779, about 23.3% |

Payment is one per cheap rating and c per exact score, including every paid
random-walk step. All policies share the same unsafe-table error limit and
almost-sure safe completion requirement. Costs are compared over the same
margin class, not by an average over hand-picked tables. Neither lower bound
is asserted tight. The smaller example uses epsilon/tau=0.9; only the larger
example retains epsilon/tau=1/16. Its large N and c limit immediate relevance.

## What is reproducible

The [saved certificate](../results/repeated_screening/certificate.json) contains:

- Outward-rounded integer bounds from rational logarithm/KL enclosures.
- Verification of the product-prior tail conditions and all three strict gaps.
- 561 exact absorbing-chain cases, checking hitting probabilities, corrected
  emissions, purchase probabilities, and the sharper paid-rating bound.
- Five scripted callback traces showing charged work, cache reuse, boundary
  census, and a rating cap. These are possible paths, not Monte Carlo samples
  or evidence of statistical calibration.
- SHA-256 pins for eight scientific source files, checked before and after
  calculation. Runtime/compiler provenance is not captured by those pins.

The [protocol](../experiments/repeated_screening_protocol.json) and scientific
sources were frozen at commit `144e3a7` before the saved full calculation.
Parameter selection, proof development, and test calculations preceded that
freeze. This is not external preregistration or a held-out discovery study.
The generating Codex session implemented and checked the work; independent
review agents were unavailable because of the account limit.

Two fresh runs, one under optimized standard-library Python, produced identical
3,890-byte files with SHA-256:

```text
34ce466e77b54314dbad4f5cf228e8018fd3319b8055c8583d9c26206acd31b1
```

From the repository root, with Python 3.11 and fresh output paths:

```powershell
python -B -S -m experiments.check_repeated_screening --out artifacts/local/screening-a.json
python -B -O -S -m experiments.check_repeated_screening --out artifacts/local/screening-b.json
python -B -S -m unittest discover -s tests -p "test_screening*.py"
```

No additional packages are needed for these commands. The checker refuses to
overwrite files. The 25 focused tests pass both normally and under `-O -S`.
The complete repository suite passes 398 tests in the existing normal Python
environment. Explicitly prepending the bundled supplemental dependency path
caused four older optional modules to skip; that run was not used to claim
full coverage.

Finite enumeration checks the listed cases; the universal statements depend
on the proof. In particular, the checker does not independently establish
adaptive transcript factorization, all-table validity, or the stopping-time
limits. See the [self-review record](repeated-screening-review.md).

## Runnable callback example

This small reproducible example simulates the assumed channel on an all-zero
table. It does not run a model or show the large-example minimax bound in action.

```python
from fractions import Fraction as F
from random import Random
from goodhart_audit.screening import audit

rng = Random(7)
result = audit(
    lambda i: int(rng.randrange(4) == 0),  # q(0)=1/4
    lambda i: F(0),                      # exact fixed score
    population=8, exact_cost=64,
    tau=F(1, 64), epsilon=F(9, 640), delta=F(1, 20),
    gate_height=4, randbelow=rng.randrange, max_ratings=10000,
)
print(result)
```

The checked Python 3.11 trace returns a likelihood certificate after 579
ratings and seven exact purchases, for payment 1,027. This is one simulated
path, not an estimate of expected cost. Without a supplied random source the
auditor uses `secrets.randbelow`.

`rating(i)` must return an int 0 or 1. `adjudicate(i)` must return an int or
Fraction in [0,1] on the 1/c grid. Booleans, floats and off-grid values raise.
Exact scores are cached; purchased evidence that already proves unsafety
causes immediate rejection. `max_ratings` returns inconclusive if another
paid rating would exceed the cap. It does not cap free iterations, cache size,
likelihood-integer growth or total compute, and capped runs lose the theorem's
unconditional safe-completion guarantee. The large certificate is computed
symbolically; it does not allocate 70 million scores or execute the auditor
at that population size.

## Interpretation and remaining work

The channel q(y)=1/4+y/2, fresh independent ratings, fixed scores, exact
adjudication, and free auxiliary computation are model assumptions. No
calibration procedure or real evaluation setting establishing them is supplied.
The theorem concerns uniform mean risk in this two-oracle experiment; it is
separate from the existing best-of-N rank-envelope manuscript.

The [operational scope check](repeated-screening-operational-check.md) finds
two obstacles to treating a finite executable test suite as that experiment:
raw component access enables a cheaper standard bound, and average test
failure does not determine the fraction of programs with any failure. This
mapping therefore supplies no demonstrated practical advantage for the
opaque noisy-rating construction. Its observation interface and target need
an operational justification before further applied claims.

The [source comparison](repeated-screening-theorem.md#interpretation-implementation-and-prior-work)
credits earlier selective evaluation, adaptive KL bounds, lazy continuation,
Bernoulli factories, and multi-fidelity sampling. Whether an earlier method
with bundled, randomly priced reports subsumes this construction remains
unresolved. This draft does not establish priority.

The subsequent [report-bundling analysis](repeated-screening-bundling.md)
resolves one part of that question: a completed gate does have a binary report
interface, and a fixed price can dominate its expected primitive cost.
Neither binary channel is a random post-processing of the other. Thus the
comparison is specifically against one **primitive cost-one rating** per
item, not every compound report described as a single query. The full audit's
revisits and fixed-table objective still prevent this single-call calculation
from being a complete equivalence or a novelty determination.

Codex performed the derivation, implementation, numerical checking and writing.
Larry reports having personally checked none of the project yet. No downloads,
installations, model calls or outreach occurred. Independent correctness,
novelty, practical usefulness, field impact, personal research ownership and
fellowship competitiveness remain open. The public artifact makes the proposed
result inspectable; it does not itself settle those questions.
