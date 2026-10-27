# Nonzero minimax implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans task by task. Root coordinates separate proof and checker ownership.

**Goal:** Make the finite nonzero-table minimax candidate precise, reproducible, and honestly attributed.

**Architecture:** Preserve the existing runtime. A new standard-library research checker uses exact fractions and the frozen sharp-cost logarithm intervals; it validates finite cases and emits a source-pinned JSON artifact. The proof supplies the unbounded statement.

**Tech Stack:** Installed Python 3.11; standard library for the checker; installed scientific libraries only for existing tests.

**Spec:** ../specs/2026-10-26-nonzero-minimax.md

## Global constraints

No downloads, installs, study-model inference, external outreach, or changes to earlier pinned files. Less than 2 GB added storage. No production audit algorithm or useful finite-saving claim.

## Review focus

- Missing budget 1 and terminal zero weights: ratios use only representative support.
- Rounded count alternatives: every prior table must be safe and every alternative strictly unsafe.
- Conditional query probabilities: hypergeometric support must remain positive before the cap.
- Linear stage schedule: error spending must control expected completion without a hidden logarithm.
- Reproducibility: pin imported helpers and the final proof, use one protocol snapshot, and refuse output overwrites.

## Tasks

- [x] Write docs/nonzero-minimax-theorem.md with the complete reviewed argument, exact constants, prior-art comparison, and practical limitations.
- [x] Write tests/test_nonzero_minimax.py first; observe its failure before implementing experiments/check_nonzero_minimax.py.
- [x] Implement geometry checks, finite-profile and conditional-probability checks, and stage/cost bounds according to experiments/nonzero_minimax_protocol.json. Reuse exact_weights and log_interval from the unchanged experiments/check_sharp_cost.py. No expanded large populations.
- [x] Add meaningful tests for terminal support, enumeration-based conditional laws, strict alternative rounding, concentration summation-by-parts, overwrite rejection, source drift, and protocol mutation. Verify under -B -S and -O.
- [x] Independently review proof and checker; freeze sources before the saved run. Record protocol changes before running them.
- [x] Run the fixed protocol twice to different paths; compare bytes; write docs/nonzero-minimax-report.md from actual output.
- [x] Update navigation, provenance, and version only after verification; preserve older manuscript snapshots and manifests.
- [ ] Verify all tests, old pins, links, storage, and staged Git blobs; publish and verify the public release while keeping the full goal active.
