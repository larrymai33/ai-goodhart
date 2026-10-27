# Rank Audit Implementation Plan

> **For agentic workers:** Use test-driven implementation and independent final review. Steps use checkbox syntax for tracking.

**Goal:** A public, honest research artifact for label-efficient finite-pool best-of-N audits.

**Architecture:** A dependency-free statistical core and JSONL audit CLI, with separate synthetic experiments and mathematical documentation. Core, experiment, and documentation work have separate file ownership.

**Tech Stack:** Python 3.10+, unittest; existing NumPy and Matplotlib for experiments.

**Spec:** `docs/superpowers/specs/2026-10-26-rank-audit-design.md`

## Global Constraints

- No downloads or dependency installation; added storage below 2 GB.
- Offline only; no model calls, synthetic results labeled explicitly.
- Standard-library core; all candidate losses in [0,1].
- Finite-pool inference only; sampling draws and unique labels reported separately.
- Attribute established results; no novelty or fellowship guarantee.

## Review Focus

- Support mismatches and invalid numeric inputs fail explicitly.
- Empty data, duplicate IDs and incomplete labels fail explicitly.
- Fixed tie ordering, pool hashes and seeded draw replay are deterministic.
- No-label/zero-loss cases retain positive uncertainty.
- Cached duplicate labels never become extra independent observations beyond the planned iid draws.

## Task 1: Statistical core

Files: `goodhart_audit/core.py`, `goodhart_audit/__init__.py`, `tests/test_core.py`.

Interfaces: `rank_weights(m: int, n: int) -> list[float]` (descending); `envelope_proposal(m: int, budgets: Sequence[int]) -> tuple[list[float], float]`; `full_envelope(m: int, max_budget: int|None=None) -> tuple[list[float], float]`; `estimate_risk(ranks: Sequence[int], losses: Sequence[float], proposal: Sequence[float], budgets: Sequence[int], delta: float=0.05) -> list[dict]` (ranks zero-based; dict keys budget, estimate, lower, upper, radius, max_weight); `partial_bounds(labels: Sequence[float|None], weights: Sequence[float]) -> tuple[float,float]`.

- [x] Write and observe failing tests for exhaustive subset probabilities, minimax ratio, harmonic bounds, support checks, constant loss and valid intervals.
- [x] Implement exact weights, grid/full envelope, sample-variance empirical Bernstein union bounds, partial identification.
- [x] Run `python -m unittest discover -s tests -v`; all tests pass.

## Task 2: Provenance-aware audit CLI

Files: `goodhart_audit/io.py`, `goodhart_audit/__main__.py`, `tests/test_workflow.py`, `examples/pools.jsonl`.

- [x] Test deterministic plans, no hidden-label leaks, repeated draws, report generation, tied scores, invalid schemas, pool tampering, missing labels.
- [x] Implement validated JSONL, SHA-256 fingerprint, iid uniform-prompt/envelope-rank plan and label ingestion, summary reporting.
- [x] Exercise plan/edit-labels/report as a subprocess using a temporary directory and generated fixture.

## Task 3: Synthetic research study

Files: `experiments/run_study.py`, `experiments/protocol.json`, `results/*`, `tests/test_experiments.py`.

- [x] Freeze protocol before results; add analytic variance, sample size and seed controls, exact truth and four baseline proposals.
- [x] Test synthetic fixtures and metrics against hand-calculated cases.
- [x] Run multi-seed study, save aggregate results and per-run CSV, plot uncertainty, efficiency and envelope scaling.
- [x] Confirm outputs reproduce and stay under storage limit. Include counterexamples and negative results.

## Task 4: Research report and public release

Files: `README.md`, `docs/theory.md`, `docs/related-work.md`, `docs/research-roadmap.md`, `docs/report.md`, `CITATION.cff`, `CONTRIBUTING.md`.

- [x] Complete proofs and independent prior-art check.
- [x] Write claims directly from measured results and document limitations, author/tool provenance and reproduction commands.
- [x] Obtain independent code/math review; fix material findings and rerun checks.
- [x] Verify no secrets, artifacts well below 2 GB, and public repo destination.
- [ ] Commit and publish the authorized project (release operation follows verification).
