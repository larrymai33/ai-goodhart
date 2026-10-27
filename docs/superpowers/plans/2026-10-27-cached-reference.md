# Cached Reference Auditor Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans for assigned tasks. Root coordinates the shared checkout, freezes, and publication.

**Goal:** Make the v0.13 cached audit construction executable with a conservative expected distinct-label guarantee and a finite virtual-proposal cap.

**Architecture:** An immutable exact design supplies integer sampling masses and conservative log increments. A callback engine shares labels across independent budget streams and uses a fully charged prefix/census fallback. New proofs and evidence accompany the implementation without editing earlier pinned sources.

**Tech Stack:** Installed Python standard library, exact integers/Fractions, Markdown/JSON.

**Spec:** [cached reference design](../specs/2026-10-27-cached-reference-design.md).

## Global constraints

No downloads, installations, model inference, outreach, or extra service dependencies. Keep storage below 2 GB and preserve old pinned files. No novel-method, measured-model-efficiency, field-impact, or human-ownership claim. Resource caps and complete API are specified in the design.

## Review focus

- Rounded likelihood must remain below true likelihood, with cost drift and tail bounds computed for the implemented process.
- A fallback may acquire labels outside previous proposals; every such label is charged, and all-safe completeness includes the boundary.
- Cached proposals require fresh auxiliary coins, exact sampling, and separate virtual/physical counts.
- Input validation and design rejection occur before oracle calls; malformed oracle values cannot yield certificates.
- The factor-17 label must be conditional on verified grid/parameter conditions; generic validity and bounded-rational implementation scope remain distinct.

## Task 1: exact design and numerical proof

**Files:** create `goodhart_audit/cached_math.py`, `tests/test_cached_math.py`, `docs/cached-reference-numerics.md`.

- [x] Independently review the design mathematics before implementation; resolve interface and proof findings.
- [x] Write failing tests for log enclosures, square-root enclosures, drift/rounding, cap inequalities, exact weights, resource/type validation, and both mode decisions.
- [x] Implement the immutable design and verify focused tests normally and under optimized Python.
- [x] Review design arithmetic independently and write the complete numerical implementation proof. Separate contexts checked edge parameters, high-precision enclosures, cap endpoints, and scope.

## Task 2: callback auditor

**Files:** create `goodhart_audit/cached.py`, `tests/test_cached.py`.

**Interfaces:** consume `CachedDesign` from the exact design factory and expose the `audit` callback API specified in the design. Final field names are agreed by root and both implementers before code integration.

- [x] Write failing tests for exact ticket endpoints, repeated-item fresh coins, one-call-per-label, whole-family decisions, exact support completion, boundary/cap fallback, and malformed callbacks.
- [x] Implement the bounded engine and immutable trace, then run focused normal/optimized tests (36 tests across numerical design, engine, and independent exact recurrence/actual-path checks).
- [x] Independently review proof-to-code correspondence and test meaningful stopping/sampling invariants. A reproduced later-budget contradiction now overrides an earlier statistical pass even before full support is known; the failing-then-passing actual-design regression is preserved.

## Task 3: frozen demonstration and public scope

**Files:** create a deterministic demonstration protocol, runner, saved result, and `docs/cached-reference-report.md`; update README, citation, provenance, progress, and roadmap.

- [x] Specify scenarios, comparisons, counts, and source pins before saved runs; commit reviewed sources before running (protocol `0e4481d`, source freeze `1fd785b`).
- [x] Run the complete repository tests and reproduce the saved demonstration byte for byte (331 tests, 49 focused normal/optimized tests, two identical 108,290-byte 45-case results).
- [x] Reconcile every cost/validity claim with the implemented process and actual artifacts. Include the unsuccessful original-instance screen and classical attribution. Final independent review confirms all ten frozen pins, 45 rows, exact bounds/caps/truths, and byte-identical reproduction; fallback phase wording matches the trace.
- [ ] Verify old/new worktree and Git-byte pins, links, storage, and public publication; keep the full goal active.
