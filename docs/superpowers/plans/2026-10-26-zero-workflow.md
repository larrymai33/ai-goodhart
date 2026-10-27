# Zero-only audit workflow implementation plan

> **For agentic workers:** use subagent-driven-development or executing-plans task by task, with tests before implementation and independent review.

**Goal:** Make the v0.4 theorem's all-or-nothing decision usable through a complete local annotation workflow.

**Architecture:** Add two standalone standard-library modules for exact mathematics and plan/report behavior. Reuse the frozen pool reader only for geometry; preserve old commands, measured sources, and evidence. Record actual OS random draws and verify an external plan commitment when reporting.

**Tech stack:** Python 3.10+, standard library only.

**Spec:** [zero-workflow-design.md](../specs/2026-10-26-zero-workflow-design.md).

## Tasks

- [x] Math: write failing tests for exact rank/subset laws, log enclosure, probability sandwich, rejection sampling, theorem restrictions and resource bounds. Implement `zero_math.py`; prove the rational implementation preserves factor 160 in a separate note; independently review both.
- [x] Workflow: write failing tests for plan replay, external commitment, immutable metadata, exact tiny-positive losses, missing/positive/zero/empty outcomes, malformed inputs, and overwrite protection. Implement the standalone module against the agreed math API; independently review it.
- [x] Example: add clearly hand-authored arithmetic fixtures and a mechanical annotator; document the complete commands, frozen rubric, expected versus realized labels, and randomness/label assumptions. Run it end to end with site-packages disabled.
- [x] Verification: 159 full-suite tests and 44 zero-related tests under `-S` pass; earlier saved evidence and four v0.4 source pins match; end-to-end statuses/replay/failure cases pass; storage is about 37.4 MB; local links and changed-file credential-pattern checks are clean.
- [ ] Publication: publish the companion workflow under the existing public-project authorization and verify the remote result.

The preceding turn was progress, not completion of the broader goal. This implementation adds usability, not real-model validation, independent human ownership, priority, field impact, or established fellowship competitiveness. No outreach will occur.
