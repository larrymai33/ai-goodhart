# Strong Baselines Implementation Plan

> For agentic workers: use superpowers:subagent-driven-development or superpowers:executing-plans task by task.

**Goal:** Establish the finite-pool remainder theorem and test stronger, attributed acquisition proposals.

**Architecture:** Add an optional optimization module and a separate follow-up runner. Reuse frozen v0.2 engine and records, preserving original manifests. Keep proof, numerical brackets, and empirical costs separate.

**Tech Stack:** Python standard library; existing NumPy, SciPy for design and experiments.

**Spec:** ../specs/2026-10-26-strong-baselines-design.md

## Constraints and review focus

No downloads, model API calls, outreach, or >2 GB storage growth. Focus on dual feasibility, missing support, endpoint/numerical failures, reuse provenance, and prior-art scope. Optimizers never receive labels. User delegation covers routine design choices.

- [ ] Derive and independently review the finite-pool theorem; add exact rational checks and documentation.
- [ ] Test then implement goodhart_audit/design.py: optimize_design(weights, rho, tolerance), with independently checkable primal/dual values and fail-closed convergence.
- [ ] Test then implement experiments/run_design_study.py and its verifier. Validate the base protocol and all reused records; freeze sources before measurement.
- [ ] Run the two new methods on all original paired paths. Independently rerun and compare output bytes. Audit costs, negative results, and optimization gaps.
- [ ] Correct related work and headline scope; write the follow-up report. Verify prior release manifests and whole test suite, then publish the reviewed extension.
