# Matched audit budget implementation plan

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Check the one-label minimax calculation and compare three audit
rules at exactly the same expected distinct-label cost.

**Architecture:** A standard-library rational checker enumerates first-query
times and error cross moments. An optional installed-PyTorch comparison
reuses the experimental AuditCache on the existing categorical construction.

**Tech stack:** Python 3.11, fractions, unittest, installed CPU PyTorch.

**Spec:** `docs/audit-budget-theorem.md` and the protocol below.

## Global constraints

- No downloads, installations, model calls or outreach.
- Preserve the previous checkers' behavior and saved outputs.
- Conditional-gradient targets are evaluated at actually visited states.
- Do not infer optimal training performance from the constant-target theorem.

## Comparison protocol, declared before execution

Use the same two-group, three-action policy, advantages and clip interval
as `docs/audit-cache-experiment.md`; three SGD ascent updates. Compare
one-shot inverse weights reused across updates, fresh-or-cached equal
first-query probabilities, and fresh-or-cached probabilities from (3).
Use every combination of learning rates (0.05,0.2,0.8) and final group
purchase probabilities ((1/4,1/8),(1/2,1/4),(3/4,1/2)). This is nine
constructed settings and three methods per setting, chosen after earlier
experiments, not an external preregistration or held-out validation.

Enumerate all audit histories. Report exact expected distinct-label cost;
per-update gradient MSE, expected squared conditional bias and marginal
bias norm; MSE of the sum of gradient errors; and expected final synthetic
full reward. Report all settings without selecting winners. Three labels
are charged for each group's first purchase. No runtime-cost claim.

## Review focus

- Conditional versus marginal unbiasedness: record both and error cross terms.
- Fixed versus changing gradient discrepancy: keep theorem claims separate.
- Correlated errors under one-shot reuse: do not apply martingale orthogonality.
- Baselines at identical expected cost: verify exact fractions on each tree.
- p near boundaries and invalid scalar types: explicit validation, no asserts.

## Tasks

- [x] Add failing tests in `tests/test_audit_budget.py` for rational schedules,
  exact first-query enumeration, cross moments, lower-bound equality and
  the equal-time excess; observe the missing-module failure.
- [x] Implement `hazards(p,T,kind)`, `moments(probabilities,d=1)`, and `verify()`
  in `experiments/check_audit_budget.py`. Check T=3,p=1/2 against 9 and 31/3.
- [x] Add optional tensor tests for `compare_training()`: all costs match,
  both fresh rules have conditional bias below numerical tolerance, their
  cumulative MSE matches the sum of per-step MSEs, and reuse has nonzero
  conditional bias. Do not require any method to win on reward or MSE.
- [x] Implement and run the full declared comparison; save its JSON locally
  and publish the generated report. Run optimized exact checks and the full
  suite, inspect claims and diff, then update the existing public draft.

Native implementation proceeds under the user's delegated research scope.
Independent agents remain unavailable due to the account usage limit.
