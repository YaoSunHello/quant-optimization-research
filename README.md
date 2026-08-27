# Quant Optimization Research

Internal workspace for optimization research built around MOSEK tutorial formulations.

## Contents

- `mosek-modeling/`: local Codex skill that distills reusable MOSEK Fusion modeling patterns for quant research.
- `Tutorials/`: upstream MOSEK tutorials repository, tracked as a git submodule.

## Working Model

Use `mosek-modeling/SKILL.md` as the entry point for translating research questions into mathematical programs. Its references map problem families such as regression, CVaR, Wasserstein DRO, optimal transport, mixed-integer conic optimization, and SDP relaxations to the relevant MOSEK tutorial sources.

## Restore

After cloning this repository:

```bash
git submodule update --init --recursive
```
