# Audit corrections across microbatches and optimizer updates

This constructed experiment tests the conditional rule in the
[surrogate note](audit-surrogate-contract.md). It uses an installed PyTorch
runtime to execute three SGD updates of a small categorical policy. Every
audit branch is enumerated. It does not train an LLM, measure verifier
latency, or establish that unbiased surrogate gradients improve training.

## A microbatch boundary can change the estimator

Fix the parameters for one optimizer update. A group has two chunks with
weak gradient zero and full-reference gradient one each. Its full gradient
is therefore 2. Such gradients can be realized at theta=0 by the two-action
policy `pi_theta=((1-theta)/2,(1+theta)/2)`, full advantages `(-1,1)`,
weak advantages `(0,0)`, and the sum of the two ratio-surrogate terms.

Draw one group audit with probability q=1/4. On selection, buy the group's
full labels and cache them. If the first chunk receives weight 1/q but the
second chunk switches to weight 1 because its labels are now cached, the
expected gradient is

```
q * (1/q + 1) + (1-q) * 0 = 1+q = 5/4,
```

rather than 2. Keeping weight 1/q for both chunks gives the correct mean.
The labels may be cached immediately; the *current update's decision* must
remain unchanged. At the next optimizer update the group receives weight 1.

More generally, let a group's fixed-update reference discrepancy be a sum
of chunk contributions, `D_g=sum_j D_gj`. If all chunks retain the same
`Z_g/q_g`, their sum has expectation `D_g`, conditional on history **before
the current draws**. Changing the weight after seeing a selected audit
breaks that calculation. This does not claim conditional unbiasedness after
conditioning again on the current draw. The parameters, chunk membership
and aggregation weights must stay fixed throughout gradient accumulation.
An optimizer step between chunks starts a different update and requires
its own conditional argument.

## Executed construction

There are two groups, each containing one response for each of three actions.
Each response has one action; there is no text generation or padding. The
policy is `softmax(X @ W)`, with six shared parameters in a 2-by-3 matrix W,
initially zero, and

```
X = [[1, 1/2], [-1/4, 1]]
weak centered advantages = [[0, 1, -1], [1, -1, 0]]
full centered advantages = [[1, -1, 0], [-2, 1, 1]]
```

The old policy stays uniform. The clip interval is [0.8,1.2], every response
has weight 1/6, and SGD ascends with learning rate 0.8, without momentum,
for three optimizer updates. Unknown groups receive independent fresh
audit probabilities (1/2,1/4) at each update. An audited group reveals its
three fixed targets and is never purchased again.

The feature rows have nonzero inner product, so a group's parameter update
can also change the other group's logits.

An oracle callback supplies the constructed full advantages. The evaluator
also holds them to calculate the reference; the simulated acquisition
policy accesses them only when selected or previously cached. A purchase
is charged three labels by definition. This is cost accounting for a
declared simulation, not a measurement of a real verifier's cost.

The experiment exhaustively branches on the draws for every currently
unknown group. At each visited state, it compares the conditional mean
objective and raw gradient with the full-reference objective and gradient
at that same state. It then executes a detached `torch.optim.SGD.step()`
for each branch. It does not compare against a separate full-audit training
trajectory.

Each branch is evaluated as one batch, two whole-group microbatches, and
three permuted microbatches splitting both groups. Gradients accumulate
with the full-batch denominator in every case. The full-reference gradient
is additionally checked by central differences, away from clipping knots.

## Results and reproduction

The local CPU float64 run used installed PyTorch 2.11.0+cu128:

| Check | Result |
|---|---:|
| Conditional states before an update | 14 |
| Complete audit histories | 16 |
| States with active full-reference clipping | 11 |
| Largest conditional gradient discrepancy | 8.33e-17 |
| Largest conditional objective discrepancy | 1.12e-16 |
| Largest gradient discrepancy across partitions | 2.23e-16 |
| Largest central-difference gradient discrepancy | 8.18e-11 |
| Expected distinct labels, exact | 279/64 = 4.359375 |

The exact label expectation also follows independently from
`3[(1-(1/2)^3)+(1-(3/4)^3)]`. Buying only at the first update would instead
cost `3(1/2+1/4)=9/4` labels on average. The conditional rule uses a larger
total acquisition budget in this construction; it is not a free correction.

```powershell
python -B -S -m experiments.check_audit_cache
python -B -m experiments.check_audit_cache --autograd
python -B -m unittest tests.test_audit_cache -v
python -B -O -S -m unittest tests.test_audit_cache -v
```

Four standard-library tests cover the microbatch example, cache lifetime,
immutable copied targets and explicit input errors. An optional fifth test
executes the entire tensor experiment and is explicitly skipped if PyTorch
is unavailable. No installation is required or attempted. Scientific checks
use explicit exceptions and remain active under optimized Python.

The full branch suite passes all 385 tests, including both optional tensor
checks. Normal and optimized tensor-experiment outputs also match exactly.

As a local negative-control check, three in-memory code mutations were each
rejected by the conditional-gradient comparison: applying correction before
clipping, retaining the old inverse weight on previously cached groups,
and assigning unit weight immediately to newly purchased labels. These
were checks by the generating agent, not independent review.

## Scope of the implementation

`AuditCache` is an experimental reference for one immutable batch. It stores
an immutable per-group decision for the duration of an optimizer update.
A new batch needs a new cache, even if it reuses group names. The caller is
responsible for the declared sampling law; the experiment enumerates it
instead of testing a random-number generator. Callback errors abort the
experiment; external purchases have no transaction or recovery protocol.

This is not a TRL adapter. It does not test distributed synchronization,
real token masks, mixed precision, stochastic or stateful verifier labels,
changing normalization, adaptive chunk membership, Adam, gradient clipping,
or a new rollout batch. Neither gradient fidelity nor the clipping-gap
identity establishes policy improvement. No empirical outcome of an
external study is explained by this construction.

Codex chose the construction, implemented and executed it, and wrote this
report. It was developed after the earlier derivations, without a
preregistered experiment. Independent agent review was unavailable; the
owner has not personally verified the work. Novelty and practical value
remain open. No downloads, model calls or external outreach occurred.
