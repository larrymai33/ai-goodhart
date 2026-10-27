# Current manuscript implementation plan

> **For agentic workers:** Use executing-plans for assembly, with parallel independent writing and final mathematical/layout review.

**Goal:** Make the existing all-grid result and its complete proof dependencies
readable in one current research manuscript.

**Architecture:** Main narrative plus explicitly numbered proof appendices,
assembled from reviewed Markdown components. A local renderer produces the
PDF without downloads; a manifest pins distributed files and frozen evidence.

**Tech stack:** Existing Python, ReportLab, Matplotlib, Pillow, PDF inspection
libraries, Markdown. No installation or model inference.

**Spec:** [Current manuscript design](../specs/2026-10-27-current-manuscript-design.md).

## Review focus

Complete transitive proof dependencies; consistent equation/section references;
all finite endpoint cases and common-safe priors; exact versus noisy labels;
expected acquisitions versus proposal counts; blind lotteries in the comparator;
primary-source attribution; legible displays and no clipped math.

## Work

- [ ] Assemble a current main narrative in `paper/finite-cost/main.md`,
  covering model, main statements, intuition, cached construction, corollary,
  finite example, evidence, limitations, and references.
- [ ] Assemble complete proof appendices and a source correspondence in
  `paper/finite-cost/appendices.md` and `paper/finite-cost/source-map.md`.
  Independently audit every dependency and reference.
- [ ] Add a bounded local build wrapper, with necessary regression checks
  for any new math/display transformations. Render the new PDF, inspect all
  pages and repair clipping, unreadable equations, or broken references.
- [ ] Write build/integrity instructions and a manifest; update current
  review guide, README, provenance, and progress. Verify preserved evidence,
  artifact metadata, local links, and staged bytes.
- [ ] Publish the consolidation, verify remote main/tag and public artifacts,
  and keep the broader research/fellowship goal active.

## Decisions

- This is a v0.14 evidence consolidation. It introduces no new experiment,
  new minimax theorem, novelty determination, or human research verification.
- New primary-source attribution and the rejected tentative noisy-label rate
  are recorded separately from established manuscript results.
