# Small annotation workflow

These are **invented records**, not LLM responses or safety evidence. They exercise the audit workflow with two pools of four candidates.

From the repository root, without installing anything:

```console
python -m goodhart_audit plan --pool examples/pools.jsonl --out artifacts/local/audit.json --draws 32 --seed 7 --budgets 1,2,4
```

Open `artifacts/local/audit.json` and replace each `queries[].loss` value of `null` with the independently assigned loss, from 0 (no failure) to 1 (failure). Do not edit the draw list, query identities, or other fields. Repeated draws reuse the single label in the unique-query table. For this toy example only, arbitrary annotations are fine; they are not real safety judgments.

```console
python -m goodhart_audit report --pool examples/pools.jsonl --audit artifacts/local/audit.json --out artifacts/local/report.json --delta 0.05 --threshold 0.1
```

The report includes ordinary importance-sampling estimates, simultaneous empirical Bernstein bands, deterministic missing-label bounds, their intersection, and individually certified budgets. `largest_certified_budget` can be null. A certified budget does not imply that every smaller budget is certified. A certificate applies only to the frozen pools, ordering, and label definition.

Scores are sorted descending. Equal scores use ascending candidate ID as a deterministic tie-break. All pools must have the same number of candidates. IDs must be unique within each prompt; prompt IDs must be globally unique. The input limit is 64 MiB. The planner ignores optional source `loss` fields; only annotation values explicitly entered in the query table are used in the report.

Fix the seed, target budgets, and draw count before inspecting any annotations. The fingerprint and plan replay prevent accidental mismatch; they do not stop a researcher from trying multiple seeds and retaining a favorable result. Do not use these fixed-time intervals for optional stopping.
