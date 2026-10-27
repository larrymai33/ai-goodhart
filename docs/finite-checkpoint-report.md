# A smaller upper bound for the original finite audit

Version 0.14 adds a complete real-loss proof, a rational callback reference,
and a reproduced exact certificate for the original finite decision.

The construction improves the original seven-budget cost upper bound from
1934.2 to **383040/199, approximately 1924.824 expected distinct labels**.
The reduction is about 9.376 labels, or 0.485%. It uses three scheduled
finite-population tests and an explicitly disclosed blind-certification
branch. This is a modest theoretical improvement on a fixed-table decision,
not a measured saving on LLM outputs or an exact minimax solution.

## The unchanged decision and the two modes

There are 32 fixed prompts, 64 ranked candidates per prompt, and budgets
`1,2,4,8,16,32,64`. A single certificate asserts that all seven risks are
at most `1/10`. Expected cost is maximized over all fixed tables with every
risk at most `3/32`; validity applies to every fixed table, and completion
includes safe tables exactly at the threshold. Every acquired label costs
one, with reuse across targets.

| Construction | Global false-certificate allowance | Uniform expected labels on the margin class |
|---|---:|---:|
| Earlier deterministic audit with blind mixture | 1/20 | 1934.2 |
| New evidence branch, default callback mode | 1/200 | at most 2016 |
| New explicitly enabled mixed mode | 1/20 | at most 383040/199 |

Mixed mode certifies without reading any label with probability **9/199**.
Otherwise it runs the evidence branch. Its error accounting is exactly
`9/199 + (190/199)/200 = 1/20`; the corresponding cost is at most
`(190/199)*2016`. This lottery is permitted by the original mathematical
objective. The evidence branch alone does not improve the earlier 1934.2
bound at its different error allowance.

The preserved [lower certificate](monotone-placement-report.md) still gives
`1103.263793259 <= C*`. The new upper bound narrows that interval slightly.
It does not show that an audit normally needs 1925 labels, or that this
schedule is optimal.

## How the charged evidence branch works

First buy all 1024 labels in ranks 1 through 32. Use their actual values
to determine which targets have deterministic upper bounds below the
threshold. For the remaining eligible targets, draw one uniform random
ordering of the 1024 suffix cells. Consider stopping after **2000, 2016,
and 2032** total acquired labels. Every target must pass at the same
checkpoint; every label already acquired must be consistent with safety.

The tests use lower expected-shortfall cutoffs from a classical extremal
finite population. Convex hinge bounds handle fractional losses exactly;
raw hypergeometric tail probabilities cannot simply replace those bounds.
Passing requires a strict comparison, including at probability atoms.
All unsafe-table error allocations sum to `1/200`.

If the head does not support a statistical test, or no checkpoint passes,
buy the remaining labels and evaluate all seven risks exactly. This fully
charged census is necessary for completion on every safe boundary table.
The mathematical proof covers arbitrary fixed real losses in `[0,1]`.

## Run the callback reference without installation

```python
from fractions import Fraction
from goodhart_audit.checkpoint import audit

# Replace this demonstration with a fixed, correct label source.
def label(prompt_index, rank):
    return Fraction(3, 32)

result = audit(label)  # evidence branch; no blind certification by default
print(result.certified, result.reason, len(result.acquisitions))

# Only this explicit option selects the mathematical mixed benchmark:
mixed = audit(label, allow_blind=True)
print(mixed.reason)  # can be "blind", with zero acquired labels
```

The reference is deliberately restricted to the original geometry. Prompt
indices are `0..31`; ranks are `1..64`. Labels must be integers or Fractions
in `[0,1]` with denominator at most 1,000,000. Floats and booleans are
rejected, as are malformed random draws. Callback failures raise without
issuing a certificate. The callback must supply fixed correct labels
independent of the audit's randomness.

The default random source is `secrets.randbelow`. A supplied `randbelow`
must provide independent uniform integers in its requested range for the
theorem to apply. Range checks and seeded demonstrations do not prove that
condition. The program's rational-input contract is narrower than the ideal
all-real-table theorem; the latter supplies the stated minimax upper bound.

## Exact evidence and reproduction

The [complete proof](finite-checkpoint-theorem.md) reduces uniform expected
cost to 2,439 exact head-bin/checkpoint calculations. It covers every
possible head statistic through conservative bins, rather than testing
only a few favorable tables. The required upper bounds on failing to stop
are `689/1000`, `311/1000`, and zero. They imply

```text
expected labels <= 2000 + 16*(689/1000 + 311/1000 + 0) = 2016.
```

The final term accounts for census fallback. Zero probability of needing
it applies only on the supplied-margin class; the algorithm retains it for
other safe tables. The proof uses prospective unconditional checkpoint
statistics, not concentration conditional on reaching a checkpoint.

Protocol commit `0624c7e` preceded the saved full run, following exploratory
derivation, schedule searches, and targeted exact checks. It is internal
specification, not external preregistration. The reviewed scientific source
freeze is `46c02503709e069d62fd5dac757c0e32e3e0152a`.

The [protocol](../experiments/finite_checkpoint_protocol.json) fixes all
calculations and examples. The [checker](../experiments/check_finite_checkpoint.py)
pins eight scientific source files, checks for changes during calculation,
rejects altered or nonexact protocol values, and refuses to overwrite an
existing output. The [saved artifact](../results/theory/finite_checkpoint.json)
retains every bin, cutoff, nonpass bound, target maximum, and stage total.
Scientific arithmetic is exact; probabilities and costs serialize as
rational strings, without binary floating-point values.

| Independent finite check | Count |
|---|---:|
| Direct subset laws, including fractional extremal populations | 475 |
| Sorted quarter-grid populations | 456 |
| Convex upper/lower hinge inequalities | 18,356 |
| Strict lower-tail and weak upper-tail comparisons | 5,547 |

A separate regression uses an unsafe population where a weak cutoff would
pass with probability `1/2` despite allowance `1/20`; the correct strict
rule has false-pass probability zero in that example. All 2,439 original
bin calculations are also tested against independent observed-subset counts
and a variational expected-shortfall formula.

Two full runs produced identical **848,201-byte** results, SHA-256
`c89ddf4d0c5a538a6deee168c20c9b794e6463fade77e5b2d670afb547764ac0`.
All eight source pins match the freeze. **366 repository tests passed**;
22 focused tests also passed under optimized Python with site packages
disabled. Separate agent contexts reviewed the proof, callback, checker,
and claims. These are assisted-session checks, not independent human review.

The fixed illustrative runs use seeds 7 and 29. Zero and constant-margin
tables stop at 2000 labels in both runs; the tail-binary table stops at
2016. Constant-boundary and unsafe tables use all 2048 labels, with only
the safe boundary certified. A separate scripted run exhibits the zero-label
blind branch. The result retains exact checkpoint records and hashes of the
charged acquisition transcripts. These eleven demonstrations do not estimate
an error rate or prove uniform expected cost. Separate scripted unit tests
exercise all three stopping points, including 2032 labels.

Reproduce with the Python standard library, choosing a fresh output path:

```console
python -B -S -m experiments.check_finite_checkpoint --out artifacts/local/finite-checkpoint-reproduction.json
python -B -S -m unittest tests.test_checkpoint_math tests.test_checkpoint tests.test_finite_checkpoint -q
```

## Attribution and limits

The proof credits classical finite-population majorization, convex order,
and atom-correct expected shortfall. Error spending, union bounds, and the
blind mixture are established tools. Exploratory searches selected the
specific schedule before the internal protocol freeze. No new generic
testing method, scientific priority, or optimal schedule is claimed.

The project remains a study of fixed correct labels. It does not validate a
grader, generalize to new prompts, certify budgets omitted from the declared
grid, or measure performance on real model outputs. Development and review
used substantial Codex assistance. Neither automated verification nor this
small numerical improvement establishes human research ownership, field
impact, or fellowship competitiveness.

No downloads, installations, model inference, or external outreach were
used. Earlier pinned sources, results, and manuscript snapshots are preserved.
