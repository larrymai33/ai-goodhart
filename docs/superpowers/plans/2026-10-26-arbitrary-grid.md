# Arbitrary-grid theorem extension plan

Spec: [arbitrary-grid design](../specs/2026-10-26-arbitrary-grid-design.md).

- [x] Prove the greedy representative comparison, disjoint-block lower bound, and deterministic envelope cost upper bound; independently review the factor 320.
- [x] Prove and check the missing-baseline obstruction, including the varying-confidence and fractional-label qualifications; attribute established ingredients.
- [x] Implement an exact bounded checker and tests under the committed saved-run protocol. The saved 122,900-comparison artifact reproduces byte for byte after source freeze.
- [x] Extend the zero-only workflow domain. Four legacy mathematical records are identical; two actual v0.4.1 reports replay byte for byte. An actual sparse-grid CLI run certifies exactly 1,3,7 with factor 320.
- [x] Full suite: 171 tests pass. Focused standard-library checks pass, and prior evidence/source pins match. Proof and claims were separately agent-reviewed.
- [ ] Check final local links and storage, publish the reviewed result, and confirm remote state.

Exploratory checks preceded the protocol; no independent holdout, external preregistration, model study, human review, or priority determination is claimed. The broader goal remains active.
