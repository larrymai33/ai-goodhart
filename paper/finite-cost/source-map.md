# Source and dependency map

This manuscript is a faithful consolidation of the current finite-cost
proofs, not a new theorem or a claim of established priority. The frozen
scientific base is commit `765ac51`. Original scientific notes are preserved
byte for byte. This map records correspondence, not an independent human
verification of the arguments.

## Included sources

| Frozen source | Manuscript location | Treatment |
|---|---|---|
| `docs/all-grid-minimax-theorem.md`, Section 1 | Main text and appendix standing conventions | Model, objective, parameters, and theorem restated; repeated introduction removed. |
| Same, Section 2 | A.2, (A1) | Representatives, finite-endpoint band mass, and residual lower proposition retained. |
| Same, Section 3 | A.3, (A2), (A2a)--(A2c) | Maximal residual-row lemma retained and expanded with the complete MGF, maximal inequality, and summation-by-parts proof. |
| Same, Sections 4--6 | A.4--A.6, (A3)--(A12) | Deterministic head, common safe conditioning, alternatives, finite-horizon transcript argument, and shared-prior cost sum retained. |
| Same, Sections 7--10 | A.7--A.10, (A13)--(A31) | Centered domination-tail prior, count-map reduction, conditional-tail geometry, clipped-envelope accounting, all cases and constants retained. |
| Same, Section 11 | A.11 and Appendix B | Repeated upper synopsis shortened to internal pointers; complete proofs are in B. |
| Same, Section 12 | A.12 | Full dyadic matching-rate corollary retained. |
| `docs/cached-likelihood-audit.md`, Section 1 | Main text and B.1, (B3)--(B7) | Repeated fixed experiment removed; upper-auditor parameters and both theorem statements retained. |
| Same, Sections 2--3 | B.2--B.3, (B8)--(B18) | Fresh auxiliary coins, exact-support completion, bounded-stopping proof, distinct-item clipping, and explicitly charged optional census retained. |
| Same, Sections 4--5 | B.4--B.5, (B19)--(B29) | Both geometric-mixture constants, separated-grid bound, deterministic alternative, and bounded-proposal variant retained. |
| Same, Section 6 | B.6, (B30)--(B39) | Full grouped arbitrary-grid construction and cost accounting retained with internal references to C.6. |
| `docs/finite-saturation-theorem.md`, Section 2 | C.2, (C7)--(C13) | Complete finite-count testing proof, including independence requirement, small-cost branch, completed-permutation reciprocal bound, and finite-horizon KL retained. |
| Same, Section 3 | C.3, (C14)--(C18) | Complete hidden-subset proof on one common fractional safe table retained. |
| Same, Section 4 | C.4, (C19)--(C26) | Both $P\tau\ge4$ exact-count and $P\tau<4$ hidden-subset branches retained. |
| Same, Section 5 | C.5, (C27)--(C37) | Complete high-budget envelope geometry and lower bound, including $m\le4$, both clipping branches, and hazard/tail distinction retained. |
| Same, Section 6 | C.6, (C38)--(C49) | Complete prefix/residual construction, binomial Bernstein plus conditional DKW calculation, simultaneous summation-by-parts bound, unsafe cases, stage-tail expectation, and charged census completion retained. |
| `docs/finite-density-theorem.md`, Section 4 | Expanded A.3 | Full Bernoulli MGF and maximal-prefix proof supplied inline, adapted to the already-stated subprobability rows. No other result from this source is needed. |

## Omitted or shortened source material

- Repeated titles, introductory release narrative, and duplicate fixed-experiment
  setups are replaced by the main text and the appendix standing conventions.
  The manuscript still states the exact quantifiers and oracle assumptions.
- All-grid Section 13 is interpretive discussion rather than an additional
  lemma. Its limitations and attribution belong in the main text. No proof
  branch from Sections 2--10 or the dyadic corollary is omitted.
- Cached-likelihood Section 7's upper-only dyadic example is superseded here
  by all-grid Section 12's matching upper/lower corollary (A.12). Its comparison
  with an earlier census-order guarantee is not used in any proof. Section 8
  is scope discussion represented in the main text.
- Finite-saturation Section 1's repeated model and full original theorem
  statement are shortened. The prefix identity is repeated as (C4), and the
  specialized bound is recorded as (C6). Its Sections 7--8 are a separate
  deterministic-cap example and scope discussion, neither required by the
  all-grid theorem. Their omission removes no dependency of C.2--C.6.
- The all-grid note's redundant summary of the finite-population lemma is
  replaced by a pointer to its complete C.2 proof. Its cellwise invertible
  label-map reduction is retained in A.7.
- The v0.14 finite-instance improvement is secondary and linked separately
  from the main text. Its separate complete proof is not reproduced, and
  this manuscript does not describe that secondary result as self-contained.

## Closed proof dependencies

The lower-bound dependency chain is
A.2--A.6 (broad representatives), or A.7--A.9 plus C.2 (centered tail blocks),
or C.2--C.5 (high-budget endpoint). A.10 exhausts the cases. C.4 uses C.3
when $P\tau<4$; this hidden-subset branch is essential and is included.
The dyadic statement A.12 uses A.6, (A24), and B.5.

The separated-grid upper chain is B.2--B.3 (likelihood auditor and cache
cost), B.4 (mixture inequality), and B.5 (constant and deterministic choice).
The universal upper chain is B.4, B.6, and C.6. The prefix and cache are
shared across groups, while each group's stream is fresh. A fixed unsafe
group controls the error of the one whole-family assertion.

No project-specific lemma needed for these statements remains only in an
external repository document. The only invoked general probability tools
are the stated elementary inequalities, KL chain rule and binary data
processing, nonnegative-supermartingale maximal inequality, binomial
Bernstein/Chernoff, and Dvoretzky--Kiefer--Wolfowitz. References [7,12--14]
cover the likelihood, maximal-inequality, rare-region conditioning, Bernstein,
and empirical-CDF foundations. Elementary KL identities and binomial
Chernoff bounds are used as standard tools, not claimed as contributions.
The forms needed for the argument and their constants are displayed in the
appendices; these references are not an exhaustive history of each tool.

## Surgical changes and notation

1. Every retained source equation number is prefixed by its appendix letter:
   original all-grid (1) becomes (A1), cached (8) becomes (B8), and saturation
   (7) becomes (C7). Section citations receive A., B., or C. prefixes. Gaps
   are intentional where redundant setup equations are omitted.
2. ASCII mathematical expressions in source backticks are converted to
   inline LaTeX without changing their numerical content. Mathematical
   displays may be line-broken for legibility; constants and inequalities
   remain those of the frozen sources.
3. A.3 now displays
   $\log\mathbb E e^{\lambda(X-p)}\le p(e^\lambda-1-\lambda)
   \le p\lambda^2\le\lambda t/2$, explains the exponential-series bound,
   and proves the common maximal-prefix event and summation-by-parts step.
   This expands the existing cited argument rather than supplying a new lemma.
4. External source pointers used as logical steps are replaced by internal
   references. The finite-endpoint representative argument was already
   written out in the all-grid source, so its redundant nonzero-theorem
   pointer is removed. A.7's count-label relabeling explanation remains.
5. B.6's residual and stage-tail pointers now resolve to C.6 and (C47).
   C.6 explicitly records that its group proof needs $a\le n\le4a$;
   the original grid need not have a high minimum budget.
6. Common symbols $P,m,\mathcal K,\tau,\epsilon,\delta,H,G,F,k_\epsilon$
   keep their main-text meanings. Local variables such as $p,q,k,A,R$ and
   block counts are introduced where used, as in the original proofs.
7. Source introductions and duplicated scope paragraphs are removed for
   readability. No admissibility requirement, independence requirement,
   parameter branch, all-safe completion mechanism, or cost charge is dropped.

## Frozen source byte hashes

These SHA-256 values identify the source bytes read during consolidation;
the release manifest also records distributed artifact hashes. They do not
assert mathematical correctness.

- `docs/all-grid-minimax-theorem.md`: `e82d771d4a0019554b002c671d50375e5837ff0e88a4cce8d047214d4680395e`
- `docs/cached-likelihood-audit.md`: `27b858667f04854513bc6497335f16f043e6b30cf560d7abae4aef0cda947280`
- `docs/finite-saturation-theorem.md`: `4f58d2198ca3aa6192e2c24bb9f40f4a052f29c7c6cd5f21a47b0f6abc90ffcc`
- `docs/finite-density-theorem.md`: `9736d9aff1ebaad94bef45e114abbe88b2d01107f960268a47eafd39c91e54e5`
