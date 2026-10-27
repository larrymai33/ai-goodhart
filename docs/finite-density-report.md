# Finite-density minimax extension: result and limits

Research extension, 27 October 2026. The [complete proof](finite-density-theorem.md) replaces the earlier nonzero theorem's many-prompts condition with a condition on the largest individual target weight. It also gives a prefix-census upper bound and a counterexample to a general census-saturation formula. The [primary-source comparison](finite-density-priority.md) attributes the established concentration, monotone-mixture, and adaptive-information tools. Scientific priority for the combined result remains unestablished.

## What changes mathematically

Keep the fixed-table objective: one auditor must remain delta-valid on every unsafe fractional-loss table and certify every safe table almost surely. Its efficiency is worst-case expected distinct labels over tables with all declared risks at most `tau-epsilon`; epsilon is supplied to the design. Put `N=max K`, `L=log(1/delta)`, and let Z be the actual declared grid's envelope normalizer. For positive `tau<=1/8`, `epsilon<=tau/16`, and `delta<=1/4`, the new sufficient condition is

$$
\frac{N}{Pm}\le\frac{\epsilon^2}{4\tau\log(4/\delta)}.
$$

Under that condition,

$$
\frac{Z\tau L}{16384\epsilon^2}
\le C^*(\epsilon)
\le\min\left\{P k_\epsilon,\frac{49152Z\tau L}{\epsilon^2}\right\}.
$$

Here `k_epsilon` is the shortest rank prefix whose unobserved probability under the smallest declared budget is at most epsilon. The upper bound needs no density condition. The new sufficient condition contains the [frozen v0.8](nonzero-minimax-report.md) regime `P>=L/epsilon^2`, and can hold with P=1 when the pool is sufficiently large relative to its maximum declared budget. The new numerical lower constant is slightly weaker. Neither condition is claimed necessary.

A single exponential prefix boundary controls all decreasing target-weight rows. This makes the baseline product prior safe with high probability without paying a family logarithm. The common prior used to assess cost is conditioned to be exactly inside the margin class. Transcript information is calculated under the original, independent product priors, with explicit charges for their exceptional tables and a finite band-query cap. Conditioning is not assumed to preserve independence.

## Why a census cap is not a universal lower rate

For `P=1` and `K={m}`, only the top-ranked item has positive weight, so one query suffices. Even replacing archive size by positive support size does not repair a general `min(census,Z*tau*L/epsilon^2)` lower formula. Take `m=2^(3j)`, `K={m/2}`, `epsilon=2^-j`, `tau=1/8`, and `delta=1/4`. The probability outside the first j ranks is at most `2^-j`. Querying that prefix, then assigning worst-case loss one to the unseen tail, certifies every margin-class table. A full relevant-support fallback guarantees completeness on every other safe table.

Thus the expected cost on the margin class is at most j, although the proposed support-capped statistical formula grows as `2^(2j)*log(4)/8`. For j=8, eight labels suffice by this mathematical construction despite more than eight million positive-weight items. These are analytic examples, not model outputs, empirical speedups, or a claim that the prefix rule is always optimal.

## Fixed checks and reproduction

The protocol was frozen as `dad5dd2` after exploratory proof work and separate agent reviews. Reviewed proof and checker sources were committed as `58bf5e5` before the saved full calculation. This is internal prespecification, not external preregistration. The new checker uses exact fractions and the unchanged sharp-cost helper's outward logarithm intervals; large populations are symbolic and never allocated.

| Exact check | Saved scope | What it checks |
| --- | ---: | --- |
| Flattened monotone rows | 600 cases, pool sizes through 24, P=1 or 3 | Signed Abel identities and linear-boundary transfer; 19,600 matrix columns, including 9,200 terminal-zero cells |
| Noninteger effective populations | 404 of those 600 cases | The boundary argument does not need integer `Pm/N` |
| Binary-table enumeration | 1,490 tables across 11 small geometries | One prefix event implies all budget-risk bounds; exact prior event counts |
| Symbolic density certificates | 8 parameter profiles in 2 geometries, giving 16 certificates | Conservative density rounding, alternative separation, rational KL majorant, cap and information inequalities |
| Exact winning-rank tails | 11,968 identities through pool size 32 | Tail equals unobserved mass and decreases with budget |
| Shortest prefix lengths | 1,584 cases at 3 margins | Tail threshold and strict failure at the preceding rank |
| Saturation counterexamples | 4 symbolic sizes | Exact products of only 8, 12, 16, or 24 tail factors |

These counts are deterministic checks, not independent statistical trials. The binary enumeration uses `tau=1/4, epsilon=p=1/8` for the standalone monotone-row lemma, explicitly outside the minimax theorem's parameter range. It verifies the event implication and counts, not the exponential maximal inequality numerically. The 16 symbolic density records use theorem-range parameters and P=1 or 32; their largest pool is 18,379,552. All saved cap ceilings resolve. The largest counterexample pool is `2^72`, represented by integers and a 24-factor rational product; no such pool or model outputs are generated. The checker does not prove the stochastic lemmas, the adaptive KL chain rule, or the unbounded theorem.

Sixteen new tests cover independent subset enumeration, signed and terminal-zero identities, Decimal checks of logarithm enclosures, Bernoulli divergence bounds, unresolved ceiling brackets, protocol mutations, source drift, and overwrite rejection. They pass with site packages disabled and under optimized Python. The full suite passes **227 tests** in 8.866 seconds; the earlier saved-evidence verification also passes. Separate agent review found no actionable proof or checker defect. These are assisted-session checks, not human replication.

From the repository root, using an existing Python installation:

```console
python -B -S -m experiments.check_finite_density --out artifacts/local/finite-density-reproduction.json
python -B -S -m unittest tests.test_finite_density -q
```

Choose a new output path; overwrites are refused. The canonical protocol is capped at 16 KiB, read as one bounded snapshot, and rejects changed workload or theorem metadata. The [saved result](../results/theory/finite_density.json) pins six sources: the checker, tests, protocol, new proof, frozen v0.8 proof, and imported sharp-cost helper. The checker rereads pinned sources to detect drift before writing. A second run reproduced all **331,669 bytes** exactly:

```text
SHA-256 26191f62508d5b25568038d2af19dcd9feafde950b3815f026e6a1d994532e90
```

Earlier pinned sources, results, and both PDF snapshots remain unchanged. The older `experiments.reproduce` command retains its v0.1-v0.3 scope; it does not silently include this extension. No downloads, installations, study-model inference, or outreach occurred.

## The existing geometry still receives no practical saving

For 32 prompts, 64 candidates per prompt, the seven dyadic budgets, `tau=1/10`, `epsilon=1/160`, and `delta=1/20`, the effective size `Pm/N` is only 32. The new sufficient threshold is between 44,871 and 44,872, so it fails. Since budget 1 is included, the prefix tail is `(64-k)/64`; achieving the specified margin requires k=64 and all **2,048 labels**. The [v0.8 statistical construction](nonzero-minimax-report.md) also reaches its census cap before its first stage. No lower bound or finite saving is asserted for this example.

The extension improves a theorem's regime and explains a finite-population obstruction. It does not implement a new audit engine, remove the known-margin input, handle incorrect labels, generalize beyond the fixed archive, or establish useful constants. No new PDF or model study is part of this phase. The [contribution disclosure](provenance.md) records substantial Codex assistance and the absence of independent human verification. Publication and reproducibility do not establish field impact or fellowship competitiveness.
