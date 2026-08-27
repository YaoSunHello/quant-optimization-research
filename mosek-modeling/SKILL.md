---
name: mosek-modeling
description: Build, adapt, explain, and debug mathematical optimization models using MOSEK Fusion and the local MOSEK Tutorials repository. Use for portfolio optimization, stochastic risk, Wasserstein/DRO, regression, conic modeling, mixed-integer conic models, semidefinite relaxations, exponential/power cone formulations, and converting math into reusable Python optimization code.
---

# MOSEK Modeling

## Core Workflow

Use the local tutorial source as the ground truth:

`/Users/yaosun/Desktop/Master Folder/QuantTrading/Optimization/Tutorials`

For each modeling task:

1. Classify the problem family: LP/QP/SOCP/EXP/POW/SDP/MIP/DRO.
2. Read `references/tutorial-map.md` to choose the closest tutorial source file.
3. Read `references/formulation-patterns.md` for reusable formulations and Fusion idioms.
4. Inspect the relevant tutorial code before implementing a new model.
5. Prefer Fusion Python with `import mosek.fusion.pythonic` for readable algebraic expressions.
6. Keep financial and quant models explicit about units, scenario dimensions, return convention, loss sign, and solver assumptions.

## Modeling Rules

- Express nonlinear convex terms through supported cones rather than hand-written nonlinear callbacks.
- Introduce auxiliary variables for norms, absolute values, maxima, CVaR tails, exponentials, powers, and products.
- Keep dimensions visible in variable names and comments when shape mistakes are likely.
- Reuse `Model.parameter(...)` for repeated solves over changing data, radii, thresholds, or hyperparameters.
- Use `freeSimplex` only for repeated LP-like solves where warm starts matter; otherwise let MOSEK choose unless a tutorial gives a reason.
- For disjunctions, keep nonlinear constraints outside the disjunction; MOSEK DJC terms should be affine.
- For portfolio models, define whether returns are rewards or losses before writing the objective.

## References

- `references/tutorial-map.md`: map from user intent to source tutorials.
- `references/formulation-patterns.md`: internal mathematical model, cone translations, and Fusion templates.

## Validation

Before considering a model usable:

1. Run a small deterministic instance.
2. Verify feasibility, objective sign, and constraint activity.
3. Check dimensions by printing input shapes and variable levels.
4. Compare against a simpler baseline when possible, such as unconstrained least squares, sample-average portfolio, or a one-scenario case.
5. Record MOSEK license/runtime limits if execution fails for environment reasons.
