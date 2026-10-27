# Arbitrary budget grids with a baseline target

The prior turn published the complete zero-only workflow as v0.4.1 (`cfe3806`). That was concrete progress, but it did not establish field impact, priority, or fellowship competitiveness. The current research gap is the theorem's requirement that every power of four be a declared target.

## Proposed mathematical result

Retain the v0.4 finite fixed-label experiment, unit query cost, unrestricted adaptive comparator, whole-family decision, threshold at most 1/8, and error probability at most 1/4. Allow any nonempty declared grid K containing budget 1. Greedily retain budgets separated by a factor of four. Their disjoint, potentially noncovering rank blocks give the existing lower cost A/40. A new envelope-cost argument uses low-budget representatives and the monotonic tail of the smallest high budget to prove the deterministic bound sum_i min(1,T*s_i) <= 8A. This implies a factor-320 NEGEXP/adaptive-optimum comparison. The earlier factor 160 remains available on its original structured grids.

Show why one cannot simply remove all grid restrictions: at fixed threshold 1/8, a singleton high-budget family has adaptive zero-table optimum 1-delta while NEGEXP approaches its growing support size as delta decreases. This is a confidence-uniform obstruction, not a fixed-confidence separation or a claim that every grid without 1 is bad.

The design and packing/charging techniques are established. The contribution candidate is the finite rank-family scope extension and its boundary. Padding K with extra targets is not an acceptable proof, since it changes the comparator's required decision.

## Evidence and implementation

Write a separate proof note; preserve all source-pinned v0.1-v0.4 material. Add a standard-library exact checker, tests, an explicit protocol, and a compact saved artifact. Exploratory proof checks occurred before this specification; the protocol fixes the broader saved verification run, not an external preregistration or a fresh empirical holdout. Do not infer theorem validity or novelty from finite checks alone.

Extend the existing zero-only math module to accept arbitrary K containing 1, recording cost_factor 320 for grids outside the old condition and retaining 160 for the old grids. Preserve all other serialized metadata and calculations for previously accepted inputs, so earlier commitments remain replayable. Add new-grid end-to-end checks and replay an actual v0.4.1 plan.

## Constraints and completion for this phase

No downloads, model inference, installations, or external outreach. Keep total storage below 2 GB. Primary-source reading and publication to the existing public repository remain authorized. Separate agent contexts review the proof, counterexample, checker, and compatibility. Publish only after exact checks, tests, old-evidence integrity, and public-claim review pass. This phase does not establish human ownership or complete the broader goal.
