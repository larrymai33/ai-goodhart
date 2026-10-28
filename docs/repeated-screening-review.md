# Repeated-screening self-review record

27 October 2026. This is a review by the same Codex session that generated the
proof and code. Independent review agents were unavailable because of the
account limit. This record is not peer review or human endorsement. The branch
is suitable for an explicitly unreviewed draft PR, not a claim of established
research or automatic merge.

## Checks performed

The review used the [specification](superpowers/specs/2026-10-27-repeated-screening.md)
and [implementation plan](superpowers/plans/2026-10-27-repeated-screening.md).

- Gate accounting: the initial rating and all walk steps, including holds,
  are charged. Revealed values are cached, and cached versus newly purchased
  items use their different prescribed coin laws.
- Validity: conditional emission law is stated at completed-proposal
  boundaries; it does not condition on the current unfinished walk. Census
  and exact lower-bound rejection precede further coin emission.
- Expected cost: predictable continuation indicators justify summing the
  per-proposal conditional bound; work and emitted outcomes are not assumed
  independent. Extending the process beyond census bounds actual cost above.
- Lower comparisons: all classes obey the same global validity and boundary
  completeness requirements. The score grid gives a nonempty cheap-only class.
  The positive-null lower bound includes the exceptional-prior cost penalty.
- Numerical directions: upper costs use upper logarithms and lower KL;
  lower costs use lower divergences and upper information rates. Tail checks
  compare lower exponents with upper log targets. Vacuous gaps are rejected.
- Execution: callback types and exact score grids are checked; exceptions
  propagate; a paid-rating cap returns inconclusive. Strict JSON comparison
  rejects duplicate keys, extra fields, floats and booleans replacing integers.
- Reproduction: fresh-path output guard precedes computation, eight source
  pins agree across calculation, and two saved runs agree byte for byte.

## Changes made during implementation

1. Exact partial-sum rejection was added after a failing regression showed
   that the original reference loop could continue processing likelihood
   coins after purchased values alone proved unsafety. The new guard cannot
   reject a safe fixed table and only decreases payment. Nonzero-coin tests
   use a larger table where those partial values remain compatible with safety.
2. A Decimal reference at 110 digits failed to resolve a rational logarithm
   interval of width about 1.158e-302. Separate 350- and 500-digit checks
   confirmed containment; the test now uses 500 digits. The exact production
   enclosure did not change.
3. Execution proceeded locally with self-review when independent agents were
   unavailable. The cost is reduced independence of error detection; publication
   remains an unmerged working draft with this limitation stated prominently.

The complete software suite passes 398 tests. The 25 added tests also pass
under optimized standard-library Python. A small simulated example was run
separately. These checks do not validate the real-world oracle assumptions or
prove the analytic statements by machine.

## Unresolved review questions

The self-review found no remaining implementation blocker to draft publication.
The central analytic questions still warrant independent checking: posterior
factorization under adaptive allocation, the finite-horizon data-processing
limits, and the census-fallback lower bound. The finite absorbing-chain grid
does not settle these universal claims.

No judgement of established novelty is made. The proof-level comparison with
random-cost report bundling and earlier active-evaluation methods is unfinished.
The [subsequent bundling analysis](repeated-screening-bundling.md) now gives
an explicit single-call report representation and a conservative expected
price. It also shows that the two coarsened binary channels are incomparable
under randomized post-processing. This resolves the finite-report-interface
subquestion, while leaving the entire audit/optimality comparison open.
No real-model calibration, field impact, or independent contribution by the
project owner has been demonstrated. Computational scaling of the exact
likelihood implementation is also unbenchmarked; the optional rating cap is
not a general resource limit. These limits are explicit scope boundaries, not
evidence that the corresponding research questions have been solved.

After this follow-up, all 403 repository tests pass, including five added
bundling tests that also pass under optimized standard-library Python. The
901 gate cases and the universal derivation were checked by the generating
session only. The original eight source pins and 3,890-byte certificate remain
unchanged; no independent review is implied by these extra checks.
