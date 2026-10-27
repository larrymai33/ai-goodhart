# A useful finite lower bound for the original audit decision

Research extension, 27 October 2026. For the original seven-budget audit, the [proof and exact certificate](finite-decision-theorem.md) give

$$
784.185148748\ \le\ C^*(1/160)\ \le\ 2048.
$$

Here one auditor must be valid on every unsafe fixed fractional-loss table and certify every safe table almost surely. Its cost is the worst expected number of distinct labels over tables whose risks are all at most the threshold minus the supplied margin. The 2,048-label census is therefore within **2.612** of the optimal worst-case cost for this instance. This is a finite cost obstruction, not a faster audit algorithm.

| Decision parameter | Value |
|---|---|
| Prompt pools and candidates per pool | 32 and 64 |
| Declared budgets, all retained | 1, 2, 4, 8, 16, 32, 64 |
| Risk threshold | `1/10` |
| Supplied margin | `1/160` |
| Maximum false-certificate probability | `1/20` |
| Efficiency class | Every declared risk at most `3/32` |

The result retains the original study's seven-budget family and the whole-family objective of the cost theorems. The original confidence-sequence engine supplies stronger selectable simultaneous guarantees. The earlier 512-label prefix illustration changed the declared family to budgets 16, 32, and 64; it does not apply here. The present lower bound also does not say every safe table needs 784 labels, or contradict fast stopping on particular tables or for a single selected budget.

## Why the lower bound applies

Put all uncertain labels in ranks 33 through 64 and make the other labels zero. Every declared target puts at most the uniform budget-1 weight on each of these 1,024 tail cells. Consequently, **every** placement of 192 binary positives in the tail has all risks at most `3/32`. Every placement of 205 positives is unsafe for budget 1.

Give a hypothetical auditor the zero outside labels for free and tell it that the tail comes from one of those two uniformly shuffled fixed-count populations. This makes the problem easier. Adaptive choices of unseen tail identities still reveal hypergeometric labels. A lower bound for the easier sequential test therefore applies to the original audit. Budget 1 forces this obstruction; the other budgets enter through verification that the entire safe prior remains safe for the whole family.

For a multiplier lambda, minimize expected safe-prior query cost plus lambda times the alternative certificate probability. Classical backward induction evaluates this finite Lagrangian exactly. Subtracting `lambda/20` gives a lower certificate by weak duality. The [source comparison](finite-decision-priority.md) attributes the sequential-testing machinery and distinguishes it from this rank-family reduction.

The five registered multipliers are 512, 1,024, 2,048, 4,096, and 8,192. The strongest of those certificates uses lambda 2,048. The calculation does not prove that this multiplier is globally optimal or that the original minimax value equals the lower bound. In particular, the dynamic program's minimizing policy uses information unavailable to the original auditor; its cost is **not an operational upper bound**. The upper bound reported here is census.

## Reproducible evidence

The [protocol](../experiments/finite_decision_protocol.json) was committed as `f914279`, and reviewed proof/checker sources as `428d2b1`, before the saved production run. Exploratory calculations preceded that freeze; this is not external preregistration or a new model experiment. The [saved artifact](../results/theory/finite_decision.json) pins six source files. Their committed Git bytes matched the worktree before calculation.

All five registered multipliers were evaluated:

| Multiplier | Lower bound, rounded down | Census/lower ratio, rounded up |
|---|---:|---:|
| 512 | 486.400000000 | 4.210526316 |
| 1,024 | 745.719242319 | 2.746341899 |
| 2,048 | 784.185148748 | 2.611628139 |
| 4,096 | 719.885228491 | 2.844897936 |
| 8,192 | 535.929003718 | 3.821401690 |

The minimizing relaxed policy at lambda 2,048 has safe-prior expected cost below 809.042 and alternative certificate probability below 0.038, with certain null certification. Thus it is feasible for the **two-prior relaxation**. Weak duality bounds every multiplier's lower certificate for this same pair by 809.042. Further multiplier tuning alone therefore cannot close most of the gap to census; stronger hard instances or better globally valid upper bounds are needed. This diagnostic cost remains unavailable as an upper bound for the original audit.

Each integer calculation visits 160,769 null-possible count states. At every state it checks certain null certification, the cost-plus-error decomposition, and cost/error bounds. The result retains exact fractions, integer rounding residuals, and a checksum covering every state's values. The implementation uses rolling arrays with at most 1,758 integer slots for these calculations; the largest tracked integer is 1,456 bits. It does not enumerate 1,024-cell tables.

Independent finite checks include 81 hand comparisons, 170 comparisons with explicit deterministic stopping choices (416 retained cost/error pairs across those instances), and 120 comparisons with an explicit-support optimizer that considers every coordinate choice. Free zero-error terminal states and null-impossible certification are pruned in the stopping oracle. Exact rank-weight checks verify tail domination at 2,048 budget/rank pairs, including every originally declared budget. These bounded checks support the implementation; the general reduction rests on the proof.

All 254 repository tests pass. The 13 focused tests also pass with site packages disabled, normally and under optimized Python. Separate agent review checked the proof and production source; independent normalized rational calculations matched the exploratory full-size value and four production small-case values, policy costs/errors, and complete state checksums.

Reproduce with the installed Python standard library and a fresh output path:

```console
python -B -S -m experiments.check_finite_decision --out artifacts/local/finite-decision-reproduction.json
python -B -S -m unittest tests.test_finite_decision -q
```

The 35,192-byte result has SHA-256 `660b25f5f59de76970e950d26bdac1e6156d449fdcac7cd187fb461e1436166b`. A separate run reproduced every byte. Existing output paths and changes to pinned sources during calculation are rejected. Earlier saved evidence remains verified. These are agent-assisted mathematical and software checks, not independent human replication.

## What remains unresolved

This replaces an uninformative loose-constant lower bound with a concrete numerical constraint for the original decision. It does not establish the general finite-geometry rate for all grids, a practical method attaining the lower bound, unknown-margin adaptation, or robustness to incorrect labels. All losses in the argument are fixed and correct. No actual model labels were collected.

Scientific priority, usefulness in real model evaluations, and independent human verification remain unestablished. The [provenance record](provenance.md) discloses substantial Codex assistance. Publication of this certificate does not establish field impact or the project owner's fellowship competitiveness.
