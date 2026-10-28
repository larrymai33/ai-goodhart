# Audit cache experiment implementation plan

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Test conditional raw-gradient fidelity across optimizer updates and
microbatch splits, with distinct full-label purchases accounted for.

**Architecture:** An experimental cache freezes a group's correction multiplier
for an entire optimizer update. A small CPU categorical policy enumerates all
audit branches and compares accumulated gradients with the full-reference
gradient at each actually visited state.

**Tech stack:** Python standard library, optionally already-installed PyTorch.

**Spec:** `docs/audit-surrogate-contract.md`, Section 4 and the implementation
boundary in Section 5. Routine design choices below are Codex's choices under
the user's authorization to continue research.

## Global constraints

- No downloads, model calls, external outreach or new dependencies.
- Fixed batch, immutable reference advantages, fixed old policy and weights.
- One fresh draw per uncached group per optimizer update.
- Correction after the PPO minimum; targets and propensities detached.
- Enumerated construction, not evidence of LLM training benefit or novelty.

## Review focus

- Group split across microbatches: one weight throughout an update.
- Group encountered in a different order: stable identities, same gradient.
- Newly cached group: inverse weight now, unit weight next update.
- Unequal probabilities: conditional gradient equality and exact label cost.
- Invalid lifecycle or labels: fail explicitly, without disabled assertions.

## Task 1: cache lifecycle and microbatch regression

Files: `experiments/check_audit_cache.py`, `tests/test_audit_cache.py`.

- [x] Write failing tests for `AuditCache.begin_update(probabilities, draw,
  audit)`, `decision(group)`, `end_update()` and `purchases`.
- [x] Run tests and confirm the new module is missing.
- [x] Implement frozen decisions `(full_advantages, weight)`; copy immutable
  labels, draw only for unknown groups, reject overlapping/absent updates.
- [x] Check an exact two-chunk example: weak gradient zero, full gradient
  one in each chunk, q=1/4. Correct mean is 2; premature unit weight gives 5/4.
- [x] Run focused tests, including optimized Python.

## Task 2: enumerate a real tensor update loop

- [x] Add tests for `verify_training_loop()`: all conditional means match,
  split/permuted batch gradients agree, three updates cost 279/64 labels.
- [x] Implement two groups, three actions, shared linear logits, fixed
  centered advantages, q=(1/2,1/4), three detached SGD ascent steps.
- [x] Enumerate the complete audit tree; check objective and raw gradient
  before stepping. Count each group's three labels only on first purchase.
- [x] Require clipping-active states to occur; report float64 errors and
  actual counts. Do not compare to a counterfactual full-audit trajectory.
- [x] Document the microbatch failure and scope, run the suite and inspect
  the diff, then commit and update the existing public draft PR.

Self-review: each listed failure mode has a task; the public evidence will
state that independent review was unavailable. No production trainer API is
promised. Implementation proceeds locally under the user's broad delegation.
