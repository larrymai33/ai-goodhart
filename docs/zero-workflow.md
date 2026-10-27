# A zero-only annotation workflow

`python -m goodhart_audit.zero` plans a finite-pool audit and verifies its annotations. It implements a conservative rational version of classical NEGEXP, attributed to [Aslam, Popa, and Rivest (2008), Sections 8 and 13.2](https://www.usenix.org/legacy/events/evt08/tech/full_papers/aslam/aslam_html/). The existing `python -m goodhart_audit` commands remain separate. The [finite-cost theorem](zero-cost-theorem.md) and [arbitrary-grid extension](sparse-grid-theorem.md) state the research claims and their restrictions.

The only positive decision is that **every declared budget's risk on these fixed pools is at most the declared threshold**, under the stated sampling and correct-label assumptions. The workflow does not estimate a risk curve or establish population safety. It does not verify that a human or model supplied correct annotations.

## Hand-authored example

[zero_pools.jsonl](../examples/zero_pools.jsonl) contains eight pools of four correct integer-addition equations. [zero_mixed_pools.jsonl](../examples/zero_mixed_pools.jsonl) changes exactly one top-ranked equation from `2 + 3 = 5` to `2 + 3 = 6`. Both fixtures have numeric proxy scores and no stored losses. They were deliberately authored for workflow coverage; they are not LLM outputs, sampled evaluation data, or evidence of labeling efficiency. Their mechanically accessible answers and relationships between equations also make them unsuitable for measuring the theorem's unit-cost, no-free-label-information benchmark.

Freeze this rubric before creating either plan: for candidate text `A + B = C`, loss is 0 if exact integer addition gives `A + B == C`, and 1 otherwise. The example annotator accepts signed ASCII integers of at most 100 digits, with exactly the displayed spaces. A malformed expression is an input error, not an inferred zero or one. The annotator parses with a full-match regular expression and integer arithmetic; it never uses `eval`.

Run the following PowerShell commands from the repository root. `-S` demonstrates that the commands require no site-packages. Every output filename must be new; keep an earlier run's files intact.

```powershell
New-Item -ItemType Directory -Force artifacts/local/zero-example | Out-Null
$rubric = "Exact integer addition A + B = C: loss 0 iff A+B equals C, otherwise 1. Malformed equation is an input error."
python -S -m goodhart_audit.zero plan --pool examples/zero_pools.jsonl --out artifacts/local/zero-example/zero-plan.json --budgets 1,2,4 --threshold 1/10 --delta 1/20 --rubric $rubric
```

**Before annotating, record the plan commitment SHA-256 outside the editable plan**, for example in your audit log. Retain that value for reporting. Copy the recorded value below; do not obtain a replacement commitment from an edited plan. This is the workflow's commitment hash, not an ordinary hash of the JSON file's bytes: query losses are normalized to null when computing it.

```powershell
$zeroPlanSha256 = "REPLACE_WITH_THE_EXTERNALLY_RECORDED_PLAN_COMMITMENT"
python -S -m goodhart_audit.zero report --pool examples/zero_pools.jsonl --plan artifacts/local/zero-example/zero-plan.json --plan-sha256 $zeroPlanSha256 --out artifacts/local/zero-example/zero-pending.json
python -S examples/annotate_zero_example.py --plan artifacts/local/zero-example/zero-plan.json --out artifacts/local/zero-example/zero-annotated.json
python -S -m goodhart_audit.zero report --pool examples/zero_pools.jsonl --plan artifacts/local/zero-example/zero-annotated.json --plan-sha256 $zeroPlanSha256 --out artifacts/local/zero-example/zero-report.json
```

The first report is pending. The annotator independently checks each selected equation and changes only its null `loss` to 0 or 1. It preserves the random tape, commitment, and other metadata, and refuses existing annotations or output files. It does not certify the audit itself. The final report verifies the pool, immutable plan, random tape, and recorded commitment before interpreting the annotations. The all-correct fixture should certify.

The predefined mixed fixture exercises the positive-label outcome in a separate audit:

```powershell
python -S -m goodhart_audit.zero plan --pool examples/zero_mixed_pools.jsonl --out artifacts/local/zero-example/mixed-plan.json --budgets 1,2,4 --threshold 1/10 --delta 1/20 --rubric $rubric
# Record this distinct plan's commitment before annotation, then copy it here.
$mixedPlanSha256 = "REPLACE_WITH_THE_EXTERNALLY_RECORDED_MIXED_PLAN_COMMITMENT"
python -S examples/annotate_zero_example.py --plan artifacts/local/zero-example/mixed-plan.json --out artifacts/local/zero-example/mixed-annotated.json
python -S -m goodhart_audit.zero report --pool examples/zero_mixed_pools.jsonl --plan artifacts/local/zero-example/mixed-annotated.json --plan-sha256 $mixedPlanSha256 --out artifacts/local/zero-example/mixed-report.json
```

At these parameters, top-ranked items have inclusion probability one under the rational design. The incorrect equation is therefore selected without retrying plans, and the mixed fixture does not certify. These two fixtures are predefined test cases, not a procedure for filtering real audit data until it passes.

## An arbitrary sparse grid

[zero_sparse_pools.jsonl](../examples/zero_sparse_pools.jsonl) contains eight hand-authored pools of seven correct equations. It permits a complete example with budgets `1,3,7`, which omits 4. It has the same software-fixture limitations as the earlier examples. Use fresh output paths and record the printed commitment before annotation:

```powershell
$sparseRubric = "Exact integer addition A + B = C: loss 0 iff A+B equals C, otherwise 1. Malformed equation is an input error."
python -S -m goodhart_audit.zero plan --pool examples/zero_sparse_pools.jsonl --out artifacts/local/sparse-example/plan.json --budgets 1,3,7 --threshold 1/10 --delta 1/20 --rubric $sparseRubric
$sparsePlanSha256 = "REPLACE_WITH_THE_EXTERNALLY_RECORDED_PLAN_COMMITMENT"
python -S examples/annotate_zero_example.py --plan artifacts/local/sparse-example/plan.json --out artifacts/local/sparse-example/annotated.json
python -S -m goodhart_audit.zero report --pool examples/zero_sparse_pools.jsonl --plan artifacts/local/sparse-example/annotated.json --plan-sha256 $sparsePlanSha256 --out artifacts/local/sparse-example/report.json
```

This plan records `cost_factor: 320`; the certificate covers exactly budgets 1, 3, and 7. It makes no claim about undeclared budgets.

## Reading an outcome

| Observed selected labels | Interpretation |
| --- | --- |
| Some missing, none positive | Pending. Zero observations on a partial selection cannot certify. |
| Any positive, even if others are missing | Not certified. This alone does not establish that a target risk exceeds the threshold. |
| All selected labels exactly zero | The whole declared family is certified under the recorded assumptions. |
| Empty randomly selected set | The same all-zero rule applies. This is an allowed random outcome; do not redraw automatically. |

The examples above always select top-ranked items, so they do not produce an empty selection. More general allowed inputs can. Expected zero-table label cost is an exact sum of inclusion probabilities; the realized selected count is a different quantity. Neither is an estimate of performance on a model population.

A certificate for the entire family also covers any subset of that family. A failed or pending whole-family audit supplies no individual-budget certificate through this rule. The report therefore does not choose a largest passing budget.

## Conditions to preserve

Freeze the pools, ranking and tie rule, budget grid, threshold, error probability, and rubric before acquisition. The tool canonicalizes proxy scores in descending order and breaks ties by candidate ID. Pools must have equal size; the declared grid must include budget 1. This implementation accepts `0 < threshold <= 1/8` and `0 < delta <= 1/4`.

A sparse grid such as `1,3,7` is now allowed when each pool has at least seven candidates. The recorded cost factor is 320 for such grids, and remains 160 when the grid contains every power of four through its maximum. These are proved upper guarantees on expected zero-table cost, not estimates of the actual overhead. Only the originally declared targets are audited; the tool does not silently add intermediate budgets. Previously accepted plans retain their design metadata and can still be replayed against their original commitment.

Annotations are fixed exact losses in `[0,1]`. Null denotes missing. A positive value, however small, prevents this zero-only certificate: `1e-400` remains positive in the report's exact decimal parser. Duplicate JSON keys, booleans, nonfinite numbers, out-of-range losses, and changes to immutable plan content are errors. The arithmetic helper accepts only fresh null-loss plans and writes binary labels; it is not a general annotation importer.

Create one plan for the declared audit and finish that plan. Do not generate alternatives and choose a cheaper, empty, or favorable selection; do not stop at a convenient zero prefix or change the rubric after seeing results. Repeated opportunities to pass need a separately justified error allocation or method. Re-reading and reporting the same unchanged plan is replay, not a fresh audit. Observing a positive label permits an early noncertificate; it never permits discarding that item and restarting.

Planning obtains integer draws from operating-system random bits, with rejection sampling to avoid rounding or modulo bias. There is no user seed option. Exact rational inclusion probabilities and the recorded tape make the calculation replayable. The statistical guarantee assumes independent uniform bits; neither an OS source nor a saved tape proves that assumption. The tape and commitment cannot prove that no alternative plans were tried or that the commitment was recorded before annotation. A seeded pseudorandom run would be deterministic replay, not proof of random selection.

The fixed-pool claim remains conditional on the rubric and correctness of the supplied labels. Annotation mistakes, a proxy's relevance to harm, deployment on new prompts, and general model safety require evidence outside this workflow.
