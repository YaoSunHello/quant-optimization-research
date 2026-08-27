# Tutorial Map

Source root: `/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/Tutorials`

Use this map to decide which source file to inspect before building or adapting a model.

## Foundation

- `fusion-intro/fusion.py`: Fusion basics, linear expressions, vectorized constraints, quadratic cone, exponential cone, semidefinite variable, Pythonic operators.
- `leastsquares/regression-leastsquares.py`: least squares, LASSO, ridge, Huber loss, rotated quadratic cones for squared penalties.
- `regression/regression.py`: L2, L1, Lp, Chebyshev, quantile-style residual formulations.

## Quant And Finance

- `stochastic-risk/stochastic-risk-measures.py`: CVaR, EVaR, and higher-order risk measures for scenario portfolio optimization.
- `dist-robust-portfolio/Data-driven_distributionally_robust_portfolio.py`: Wasserstein distributionally robust portfolio model with reusable Fusion parameters.
- `dist-robust-portfolio/distributionally_robust_portfolio.py`: stripped-down reusable Python class for the DRO portfolio model.
- `option-pricing/utility-option-pricing.py`: utility-based option pricing on scenario trees, self-financing constraints, transaction costs, power/exponential utility.
- `wasserstein/wasserstein-bary.py`: optimal transport and Wasserstein barycenter without entropic regularization.
- `wasserstein/wasserstein-bary-reg.py`: regularized Wasserstein barycenter using exponential cone entropy terms.

## Conic Engineering Patterns

- `facility-location/small_disks.py` and `facility-location/disks.py`: smallest enclosing disks, coverage, big-M assignment, binary conic models.
- `kmeans-clustering/kmeans.py`: exact K-means and Euclidean clustering with disjunctive constraints and cone distances.
- `f-sparc/fsparc.py`: mixed-integer exponential-cone resource allocation.
- `sinr-optimization/sinr-optimization.py`: signal-to-interference optimization.
- `filterdesign/filterdesign.py`: filter design as conic optimization.

## Advanced Optimization Families

- `binary-quadratic/binquad.py`: semidefinite relaxation of binary quadratic problems.
- `binary-quadratic/branchbound.py`: SDP relaxation inside branch-and-bound.
- `max-volume-cuboid/maxVolumeCuboid.py`: geometric mean cone and mixed formulations.
- `minimum-ellipsoid/minimum-ellipsoid.py`: smallest enclosing ellipsoid.
- `rank-one-regression/RankOneConvexification.py`: sparse regression convexification.
- `approx-uncertain-ineq/hard_uncertain.py`: exponential cone approximations for uncertain inequalities.
- `pwl-convex-approximation/pwl-convex-approximation.py`: piecewise-linear approximation of convex functions.
- `gp-toolbox/gptoolbox.py` and `transformer-design/transformerdesign.py`: geometric programming transformations through exponential cone representations.
- `unitcommitment/ucp.py` and `unitcommitment/ucpMarimo.py`: mixed-integer operational scheduling.

## Non-Finance But Useful Structures

- `surfacecycles/surfaceCycles.py`: sparse topology LP with absolute value linearization.
- `truss-design/TrussTopology.py`: topology design.
- `equilibrium/equilibrium.py`: equilibrium constraints.
- `exact-planar-cover/exactcover.py`: exact cover / combinatorial modeling.
- `hierarchical-model/hierarchical.py`: binary assignment plus parameterized re-solves.
- `mle-convex-density-function/MLEConvexDensityFunction.py`: maximum likelihood with convexity constraints.
