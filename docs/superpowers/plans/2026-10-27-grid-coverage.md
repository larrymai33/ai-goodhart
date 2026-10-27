# Grid coverage implementation plan

> **For agentic workers:** Use executing-plans to implement this plan task by task.

**Goal:** Make the limits and valid extension of sparse-budget certificates exact and reproducible.

**Architecture:** Pure rational helpers implement a deterministic implication.
A separate standard-library checker validates identities, witnesses, and grid
minimality under the sufficient interval rule. Existing auditors are unchanged.

**Tech stack:** Python 3.11 standard library, unittest, Markdown.

**Spec:** [Coverage design](../specs/2026-10-27-grid-coverage-design.md).

## Constraints and review focus

No downloads, installs, model calls, or outreach; less than 2 GB added storage.
Do not alter pinned older sources. Check singleton pools, zero certified level,
equal levels, adjacent endpoints, malformed numeric types, and input bounds.
Distinguish statistical validity from deterministic transfer and completeness.
Attribute convexity; qualify grid optimality and dyadic sharpness precisely.

## Work

- [x] Write failing tests in `tests/test_coverage.py` for
  `interval_factor(a,b)`, `interpolate_upper(a,b,n,left_upper,right_upper)`,
  and `covering_grid(m,certified_level,target_level)` in
  `goodhart_audit/coverage.py`. Include the exact 10-point original grid,
  subset enumeration, an independent shortest path, and domain rejection.
- [x] Observe the tests fail, implement the helpers, and pass normal and
  optimized standard-library runs. Review the code independently.
- [x] Write `docs/grid-coverage.md` with the complete proof, predecessor
  correspondence, both witnesses, greedy proof, and scope limitations.
- [x] Commit `experiments/grid_coverage_protocol.json` before the saved run.
  Add `experiments/check_grid_coverage.py` and runner regression tests;
  freeze reviewed sources before writing `results/theory/grid_coverage.json`.
- [x] Run the fixed exact matrix twice, compare bytes, and verify source pins.
  Write `docs/grid-coverage-report.md`, update README/roadmap/provenance/progress,
  and check the complete test suite and all earlier evidence pins.
- [ ] Review claims and staged bytes, publish the bounded research update,
  and verify remote state. Keep the broader goal active.
