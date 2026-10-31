---
name: dcp-gurobi
description: Gurobi, a solver for linear, mixed-integer and indicator-constrained optimisation models (branch-and-cut), used from Python (gurobipy). Covers install, variables, linear and indicator constraints, minimise or maximise, solution status, and enumerating all or all optimal solutions. Use when writing, debugging or explaining Gurobi (gurobipy) models, or when the user has chosen Gurobi from Python for an optimisation or feasibility problem.
license: Apache-2.0
compatibility: "Python: Python 3.10+ and pip install gurobipy (tested with gurobipy 13.0.3 on Python 3.12). The pip wheel runs under a size-limited licence without a key (2000 variables and 2000 constraints; 200 variables with quadratic terms); larger models need a Gurobi licence."
metadata:
  domain: constraint-programming
  solver: gurobi
  paradigm: mip
  interfaces: "python"
---

# Gurobi

Gurobi solves linear and mixed-integer models by branch-and-cut. Two ideas to keep: every
constraint must be linear (or an indicator, a general constraint, or a product linearised by
hand), and the result is a **status** that must be checked before any value is read.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `gurobipy` (the wheel bundles the Gurobi Optimizer and a size-limited licence) |

Other bindings (C, C++, Java, .NET, MATLAB, R) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

Every constraint must be linear, an indicator, a general constraint (`abs`, `max`, `min`, `and`,
`or`), or a product linearised by hand; the exact calls are in the interface files.

`x * y` over two variables builds a `QuadExpr`, a quadratic model. Gurobi accepts it, but
it is nonconvex and slower, and the size-limited licence caps it. Linearise when one factor
is binary or has a small range.

## Solving

Status codes: [status reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html).
Parameters: [parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html).

| Outcome | Meaning |
|---|---|
| optimal | optimal within `MIPGap`; the objective and variable values are valid |
| infeasible | proven to have no solution; compute an IIS to see why |
| infeasible or unbounded | set `DualReductions = 0` and re-solve to tell |
| unbounded | objective unbounded; says nothing about feasibility |
| time limit | stopped at `TimeLimit`; a solution exists only if the solution count is above 0 |
| suboptimal | tolerances not met; a suboptimal solution is available |

The constant names are in the interface files.

Parameters you will set: `TimeLimit` (seconds), `Threads`, `Seed`, `MIPGap` (relative gap),
`OutputFlag` (0 silences the log, but for the licence banner create the `Env` with it; see the Install section of [interfaces/python.md](interfaces/python.md#install)), `MIPFocus`.

**The default `MIPGap` is 1e-4, not 0.** Gurobi reports `OPTIMAL` when the gap is below it, so a
solution can be reported optimal and still be worse than the true optimum. Set `MIPGap = 0`
when the exact optimum matters. Observed: a 40-item strongly correlated knapsack (weights
`random.Random(3).randint(1, 1000)`, values `w + 100`, capacity `sum(w) // 2`) reports
`OPTIMAL 12950` by default, and `12951` with `MIPGap = 0` (bound 12951).

## All solutions

Use the solution pool. With `PoolSearchMode = 2` Gurobi keeps up to `PoolSolutions`
solutions; `PoolSolutions` above the number of feasible solutions makes the list exhaustive.

| You want | Settings |
|---|---|
| every feasible solution | `setObjective(0)` or no objective, `PoolSearchMode = 2`, `PoolSolutions = 2_000_000_000` |
| every optimal solution | keep the objective, `MIPGap = 0`, `PoolSearchMode = 2`, `PoolGap = 0` |

- Count with `model.SolCount`. The pool is exhaustive only when `SolCount` is **strictly below**
  `PoolSolutions` (and `Status` is `OPTIMAL`). If `SolCount == PoolSolutions`, the list may have
  been cut short: raise `PoolSolutions` and re-run. Verified: with `PoolSolutions = 2` and 3
  feasible solutions, the run still reports `OPTIMAL` and returns only 2. A count equal to the
  cap is not proof of completeness, because a 3-solution model with `PoolSolutions = 3` also
  returns 3.
- Auxiliary variables can make two pool entries differ only in values you do not care about:
  collect the outputs into a `set` of tuples before counting.
- `PoolGap = 0` with a kept objective returns exactly the optimal solutions; verified on a
  4-cycle (two minimum covers) and on "at most 2 of 4 binaries" maximised (6 solutions).

Pool reference: [Solution Pool guide](https://docs.gurobi.com/projects/optimizer/en/13.0/features/solutionpool.html)
and [parameters](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`PoolSearchMode`, `PoolSolutions`, `PoolGap`).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Model too large for size-limited license` | pip licence limit exceeded | reduce variables or constraints (count them first), or use a full licence |
| `OPTIMAL` but a better solution exists | default `MIPGap` 1e-4 | `model.Params.MIPGap = 0` |
| `INFEASIBLE` on a model you expect feasible | a default `lb=0` hides negative values, or a wrong bound | set `lb` explicitly; `computeIIS()` and `model.write("m.ilp")` to find the conflict |
| `TIME_LIMIT` and no values | nothing found in time | check `SolCount` before reading; raise `TimeLimit`, tighten the formulation |
| solution cut off by a big-M constraint | M too small for the bounds | derive M from variable bounds; prefer indicators (encodings in [the Python interface](interfaces/python.md)) |
| enumeration returns duplicates or too few | auxiliary variables; time limit hit | collect output tuples in a `set`; check `Status` is `OPTIMAL` |
| enumeration returns fewer solutions than exist, `Status` still `OPTIMAL` | pool truncated at `PoolSolutions` | `SolCount == PoolSolutions` means possibly cut short: raise `PoolSolutions` (e.g. 2_000_000_000) and re-run |

Binding-specific issues are in the interface files.

## Further reading

- Python API reference: https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html
- Solution pool: https://docs.gurobi.com/projects/optimizer/en/13.0/features/solutionpool.html
- Status codes and parameters: https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html, https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html
- Gurobi examples (Python): https://docs.gurobi.com/projects/examples/en/current/
- Size-limited licence: https://support.gurobi.com/hc/en-us/articles/360051597492
