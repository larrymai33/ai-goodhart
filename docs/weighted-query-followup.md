# Weighted-average query follow-up

Primary-slide follow-up, 27 October 2026, supplementing the dated
[all-grid attribution note](all-grid-minimax-priority.md) and
[finite-saturation comparison](finite-saturation-priority.md). The official
2010 talk explicitly contains both heavy-prefix inspection followed by
residual sampling and deterministic truncation of a light tail. These
mechanisms must be credited as prior weighted-query practice. The final
journal proof was not obtained, so the proof-level comparison remains open.

The source is Tony Wirth, *The Query Complexity of Estimating Weighted
Averages*, Google TechTalk, delivered 4 February 2010 and posted 16 February
2010, crediting joint work with Amit Chakrabarti, Venkatesan Guruswami, and
Andrew Wirth. The corresponding [2011 Acta Informatica
article](https://link.springer.com/article/10.1007/s00236-011-0145-8) lists
Amit Chakrabarti, Venkatesan Guruswami, Andrew Wirth, and Anthony Wirth. Its
abstract and references were accessible; its full proof was not inspected.

## Direct slide evidence

The following paraphrases come from rendered slides inspected in the
official video, not a transcript or secondary summary. Write normalized
weights as `b_i=a_i/sum_j a_j` and use `eta` for the talk's additive accuracy
to distinguish it from this repository's design margin.

| Timestamp | Observed statement |
| --- | --- |
| [1:37](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=97s), [4:55](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=295s) | Estimate one specified weighted mean of unknown rational values in `[0,1]`, with additive accuracy `eta` and success probability `1-delta`. |
| [14:32](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=872s) | Inspect heavy set `H`, then sample the normalized residual. The displayed cost is `h + b_L^2 log(2/delta)/(2 eta^2)`, where `h=|H|` and `b_L=sum_(i in L)b_i`. |
| [18:13](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=1093s) | A cited Bar-Yossef et al. mean worst-case query lower bound is `min(n/4, log(1/(4 delta))/(24 eta^2))`; joint parameter ranges are not specified on this slide. |
| [19:55](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=1195s) | A cited expected-query lower bound is `(1-2 delta)` times block sensitivity; weighted sensitivity is at least `#{i:b_i>=2 eta}`. |
| [22:47](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=1367s) | A reduction transfers `(eta,delta)` weighted approximation to `(2 eta,delta)` mean approximation. |
| [23:12](https://www.youtube.com/watch?v=qyxIUPTeNfI&t=1392s) | For geometric weights, the upper bound explicitly queries a prefix until remaining mass is below `eta/2`. |

## Attribution and remaining comparison

The squared-residual-mass sampling construction and the principle of
deterministic tail truncation are explicit antecedents. The generic
sampling display includes a confidence logarithm, and the talk discusses
expected-query lower bounds. Neither mechanism should be presented as
new here, nor should the older work be characterized as exclusively
constant-confidence or worst-case-query analysis.

The [all-grid theorem](all-grid-minimax-theorem.md) concerns one globally
valid certificate for every target in a finite best-of-n family, almost-sure
completion on every safe table, and worst expected **distinct** query cost
over a supplied safe-margin class. The inspected slides do not establish
the complete comparison for that objective. In particular, a worst-case
query lower bound is not automatically an expected-query lower bound, and
an expensive estimation input need not lie in the required safe-margin
class. Separate coefficient-family examples also do not establish the
shared-label envelope result. Singleton prior art remains relevant because
the all-grid statement includes singleton grids.

Closing the comparison requires the final article or an author manuscript:
exact finite-size, accuracy, and confidence ranges through saturation;
expected-query and repeated-index conventions; any general coefficient-vector
or coefficient-family theorem; and whether its hard inputs and reductions
preserve safe-side cost and certification requirements. The talk does not
show that such results are absent from the paper. The candidate contribution
remains the precise combined all-grid certification theorem and proof,
subject to this unresolved comparison and independent proof review.
