# Finite Decision Cost Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to implement and review the assigned units. Root coordinates commits and publication in the shared checkout.

**Goal:** Certify a useful finite minimax lower bound for the original seven-budget decision.

**Architecture:** A common-safe tail prior reduces the problem to an exchangeable fixed-count test. A classical finite-horizon Lagrangian recursion produces exact integer certificates; independent small-state enumeration checks the implementation.

**Tech Stack:** Installed Python 3.11 standard library; unchanged exact-weight helper; Markdown and JSON.

**Spec:** [finite-decision-cost specification](../specs/2026-10-27-finite-decision-cost.md).

## Global constraints

No downloads, installs, model inference, or outreach. Workspace under 2 GB. Preserve all earlier pinned sources and manuscripts. No new operational audit CLI or PDF. Keep all original target budgets and the global validity/all-safe-completeness requirements. No novelty, exact minimax value, or field-impact claim follows from the calculation.

## Review focus

- Ordered-prefix weights must not accidentally include binomial path multiplicities.
- Null-impossible paths may abstain, but positive-null-mass histories cannot reject permanently.
- Exposing zero outside cells for free must weaken the problem, preserving the lower-bound direction.
- A relaxed prior-pair policy is not a globally valid fixed-table audit engine.
- Exact fractions and directed decimal rounding must support the printed numerical inequalities.

## Proof and protocol

- [x] Screen unrestricted-grid directions and identify the concrete original-decision certificate. Retain exploratory singleton and ballot work only in ignored notes.
- [ ] Write `docs/finite-decision-theorem.md` and `docs/finite-decision-priority.md`; independently review the common-safe geometry, policy reduction, recursion, and attribution.
- [ ] Commit this specification, plan, and `experiments/finite_decision_protocol.json` before the saved production calculation. Record that exploration preceded the freeze.

## Checker and evidence

- [ ] Write failing tests in `tests/test_finite_decision.py`, then implement `experiments/check_finite_decision.py`. The main entry point accepts the exact frozen protocol and a fresh output path. The integer recurrence returns exact Lagrangian/cost/error values; invalid input and provenance changes abort before publication.
- [ ] Cross-check tiny cases by explicit prior-table/stopping-policy enumeration; check null completeness and the cost/error identity. Verify zero-count and zero-observation cases, protocol bounds, source drift, output preservation, and runtime guards under `-O`.
- [ ] Independently review the checker, run focused standard-library/optimized tests and the full suite, and commit reviewed sources before the saved calculation.
- [ ] Generate `results/theory/finite_decision.json`, rerun to a fresh ignored path, and require identical bytes. Report only exact observed bounds and matrix counts.

## Public integration

- [ ] Write `docs/finite-decision-report.md`; update README, citation, roadmap, provenance, and progress. Independently reconcile every numerical and scope claim with the saved artifact.
- [ ] Verify legacy evidence, all source/document pins, committed source bytes, staged bytes, local links, and storage; commit the complete evidence package.
- [ ] Publish and verify public main and the version tag. Record this bounded phase's completion while leaving the broader goal active.
