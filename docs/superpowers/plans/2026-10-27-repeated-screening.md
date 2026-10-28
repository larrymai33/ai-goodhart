# Finite repeated-screening draft implementation

**Goal:** Publish a reproducible finite theoretical comparison as an unmerged
working draft.

**Architecture:** A callback auditor and exact arithmetic helpers in
`goodhart_audit`, a fixed-protocol checker in `experiments`, and a self-contained
proof/report in `docs`. Results pin their scientific sources.

**Tech Stack:** Python standard library, Fraction, unittest, Git.

**Spec:** [approved scope](../specs/2026-10-27-repeated-screening.md), following
the user's authorization to continue research and publish to their repository.

## Global constraints

No downloads, installs, model calls, or outreach; less than 2 GB growth.
Retain existing results byte for byte. Exact certification decisions only.
No priority or practical model claim. Agents unavailable: author self-review
only, draft remains unmerged.

## Review focus

Check cost/output dependence, cached versus newly purchased coin laws, census
precedence, strict callback types, optional-cap semantics, rational interval
directions, lower-bound exceptional-prior costs, and whether compared policy
classes have identical validity/completeness requirements. Do not infer a
universal theorem from enumerated tests or a novelty claim from a model change.

## Task 1: Runnable auditor and exact numerical mathematics

Produces: `screening.audit`, immutable result, `screening_math` log/KL/cost
helpers. Consumed by Task 2. No floating-point decisions or external imports.

- [ ] Write tests for deterministic path charges, cache reuse, nonzero
  correction, census boundary/rejection, limits, invalid values and exceptions;
  independent Decimal log checks and finite certificate values.
- [ ] Run `python -B -S -m unittest discover -s tests -p 'test_screening*.py'`.
  Expected: missing-module failures before implementation.
- [ ] Implement the gate, rational likelihood, validation, and interval bounds.
- [ ] Repeat focused tests normally and with `-O -S`. Expected: all pass.
- [ ] Commit implementation, tests, spec and plan after successful checks.

## Task 2: Proof, protocol, and reproducible finite certificate

Consumes Task 1 API; produces theorem, runner, frozen protocol and report.
Fixed examples: (N,c,K)=(13000,64,4) and (70000000,8192,52), with parameters
and formulas in the accompanying theorem. Selection preceded protocol freeze.

- [ ] Test overwrite protection, strict protocol validation, and source drift
  before implementing the runner. Expected: missing-module failures.
- [ ] Adapt the private derivation into a self-contained public proof with
  attribution and unresolved report-bundling comparison.
- [ ] Implement independent tridiagonal gate calculations, illustrative
  callback traces, and exact source-pinned certificates. No huge population.
- [ ] Freeze sources and protocol in Git before saved full results.
- [ ] Run the checker twice to fresh paths, one under `-O -S`; compare bytes.
  Expected: identical outward-rounded bounds and all finite checks pass.
- [ ] Add report and README/provenance links; preserve old scientific files.

## Task 3: Review, verify, publish draft

Consumes complete branch. Produces unmerged public draft PR and review record.

- [ ] Read the whole change against the spec as a distinct self-review pass.
  Record independent review as unavailable, not completed.
- [ ] Run the full repository suite and focused standard-library checks;
  verify new source pins and storage size. Expected: pass with stated scope.
- [ ] Commit final report/results, push the authorized draft branch, create
  and attach a draft PR. Do not request reviewers or merge.
- [ ] Report concrete results and remaining proof/novelty/application gaps.
