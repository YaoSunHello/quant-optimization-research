# Formulation Patterns

This is the internal working model distilled from the MOSEK Tutorials source. It is a map from mathematical intent to Fusion implementation patterns.

## Standard Fusion Skeleton

```python
import numpy as np
from mosek.fusion import Model, Domain, Expr, ObjectiveSense, Var, Matrix
import mosek.fusion.pythonic

with Model("name") as M:
    x = M.variable("x", n, Domain.greaterThan(0.0))
    # constraints
    M.objective("obj", ObjectiveSense.Minimize, objective_expr)
    M.solve()
    x_sol = np.array(x.level())
```

Use Pythonic operators for algebra: `A @ x`, `x.T @ c`, slicing, `<=`, `>=`, `==`. Use `Expr`/`Var` helpers when broadcasting or stacking shapes.

## Cone Translations

| Mathematical term | Fusion pattern | Main source |
|---|---|---|
| `t >= ||r||_2` | `M.constraint(Expr.vstack(t, r), Domain.inQCone())` | `fusion-intro`, `leastsquares` |
| `t >= ||r||_2^2` | `M.constraint(Expr.vstack(0.5, t, r), Domain.inRotatedQCone())` | `leastsquares` |
| `u >= |x|` | `M.constraint(u >= x); M.constraint(u >= -x)` | `regression`, `surfacecycles` |
| `w >= exp(x)` | `M.constraint(Expr.hstack(w, 1, x), Domain.inPExpCone())` with vectorized constants | `fusion-intro`, `stochastic-risk` |
| power/p-norm epigraph | `Domain.inPPowerCone(alpha)` with stacked auxiliaries | `regression`, `stochastic-risk`, `option-pricing` |
| PSD matrix | `X = M.variable(Domain.inPSDCone(n))` | `fusion-intro`, `binary-quadratic` |
| binary/integer decision | `Domain.binary()` or `Domain.integral(Domain.inRange(...))` | `facility-location`, `kmeans-clustering` |
| assignment/selection | binary matrix plus row/column sum constraints | `facility-location`, `hierarchical-model` |
| repeated solves | `M.parameter(...)`, then `.setValue(...)` before `M.solve()` | `dist-robust-portfolio`, `hierarchical-model` |

## Regression Model Family

Let residuals be `r = X @ w - y`.

- L2 regression: minimize `t` subject to `(t, r) in QCone`.
- Squared L2: minimize `t` subject to `(0.5, t, r) in RotatedQCone`.
- L1 regression: introduce `u >= +/- r`; minimize `sum(u)`.
- Ridge: introduce `pridge >= ||w||_2^2` via rotated cone.
- LASSO: introduce `p >= +/- w`; add `lambda * sum(p)`.
- Huber: split residual magnitude into bounded quadratic part plus linear tail.
- Chebyshev/minimax: introduce scalar `t`; constrain `t >= +/- r_i`.

## Portfolio And Risk Model Family

Always decide sign convention first:

- Return reward: maximize expected return subject to risk/budget constraints.
- Loss: minimize risk measure of `-r.T @ x`.

Basic long-only budget:

```python
x = M.variable("X", n, Domain.greaterThan(0.0))
M.constraint(Expr.sum(x) <= 1.0)  # or == 1.0 when fully invested
```

CVaR with scenario losses uses tail variables `W >= 0` and VaR-like scalar `eta`; the objective has the form `eta + probability_weighted_tail / (1-alpha)`. Inspect `stochastic-risk/stochastic-risk-measures.py` before modifying.

EVaR and entropic risk use exponential cones. Higher-order risk uses power cones.

## Wasserstein DRO Portfolio Pattern

The tutorial reduces a Wasserstein ambiguity-set problem to a finite convex model. The reusable variables are:

- `x`: portfolio weights.
- `tau`: CVaR threshold / auxiliary scalar.
- `lambda`: Wasserstein-radius multiplier.
- `s_i`: scenario epigraph variables.
- `TrainData`: parameter with shape `[N, m]`.
- `WasRadius`: scalar parameter.

Objective:

```python
certificate = eps * l + Expr.sum(s) / N
```

Core constraints:

- enforce the affine loss envelope per scenario and loss branch;
- enforce the dual norm bound with positive and negative linear inequalities for the infinity norm;
- enforce long-only full-investment budget.

Use parameters for repeated simulation over datasets and radius values. For repeated LP-like solves, the tutorial uses `M.setSolverParam("optimizer", "freeSimplex")`.

## Wasserstein Barycenter / Optimal Transport Pattern

Use transport matrices `pi` with nonnegative entries.

- Marginal constraints: sum over rows/columns to match source and barycenter distributions.
- Objective: dot product of transport cost matrix and transport plan.
- Barycenter: add shared distribution `mu`; each input distribution gets its own transport plan.
- Entropic regularization: add exponential-cone entropy auxiliaries; inspect `wasserstein-bary-reg.py`.

## Mixed-Integer Conic Patterns

Facility location and clustering combine binary/integer decisions with conic distance epigraphs.

- Distance to a center: `Expr.hstack(radius_or_aux, coordinate_diff) in QCone`.
- Squared distance: use rotated QCone with a fixed `0.5` slot.
- Coverage assignment: binary matrix `S[i, j]`, plus row sums for "each point covered."
- Big-M: use only when the source model needs conditional activation; compute a data-based tight bound.
- DJC: keep disjunction terms affine; move nonlinear distance constraints to auxiliaries outside the disjunction.

## SDP Relaxation Pattern

For binary quadratic problems, lift `x x.T` into a PSD matrix block:

- create `Z in PSDCone(n+1)`;
- slice `X = Z[:n, :n]` and `x = Z[:n, n]`;
- constrain diagonal consistency and lower-right scalar;
- optimize linear terms in lifted variables.

Use this for relaxations and bounds, not as a direct replacement for an integer solution unless rounding/branching is added.

## Debug Checklist

- Check every vector/matrix shape before building expressions.
- Confirm cone orientation: QCone first coordinate is the epigraph bound; rotated QCone first two coordinates must be nonnegative.
- For scenario models, verify whether data matrix rows are scenarios or assets.
- For portfolio models, test one asset and two scenarios before full scale.
- For MIP/MICO, set runtime/thread parameters explicitly for experiments.
- If MOSEK fails before solving, check license availability separately from model correctness.
