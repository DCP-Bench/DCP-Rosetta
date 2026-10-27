---
name: dcp-pulp
description: PuLP, a modelling library for linear and mixed-integer programs solved by the CBC solver it bundles, used from Python (PuLP 3.x). Use when writing, debugging or explaining PuLP models, when a linear or integer program must be solved with PuLP or CBC, or when enumerating all or all optimal solutions.
license: Apache-2.0
compatibility: "Python: Python 3.10+ and PuLP 3.x (tested with 3.3.2, which bundles CBC 2.10.3). PuLP 4.0 is not tested here; its removal of PULP_CBC_CMD is taken from the migration guide (unverified). No key or size limits."
metadata:
  domain: constraint-programming
  solver: pulp
  paradigm: mip
  interfaces: "python"
---

# PuLP

PuLP builds a linear or mixed-integer model and hands it to a solver; the solver bundled with PuLP 3.x is CBC. Keep one idea in mind: **every constraint and the objective must be linear**. PuLP refuses products and quotients of variables, so each non-linear pattern needs a linear encoding ([Encoding the constraints](#encoding-the-constraints)).

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `pulp` (PyPI), with CBC bundled |

Other bindings are not covered yet.

## Contents
- [Encoding the constraints](#encoding-the-constraints)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Encoding the constraints

`M` is a constant at least as large as the slack the constraint can need. A larger `M` is always correct but makes CBC slower, so use the smallest value the bounds allow:

- **Rule:** for `left <= right + M*(1-c)`, take `M` at least `max(left - right)` over the variable bounds. Compute it from the bounds, e.g. `M = max(left) - min(right)`.
- **`!=` rule:** when `a, b` are in `0..u`, `a - b` lies in `-u..u`, so `M = u+1` is enough. Example: `a, b` in `0..3` gives `M = 4`.

| Constraint | Linear encoding |
|---|---|
| `a != b`, with `a, b` in `0..u` (so `M = u+1`) | binary `o` (`o = 1` means `a < b`): `a <= b - 1 + (u+1)*(1-o)` and `a >= b + 1 - (u+1)*o` |
| `d = abs(a - b)`, minimised | `d >= a - b` and `d >= b - a` (minimisation pulls `d` down) |
| `c = 1` implies `left <= right` | `left <= right + M*(1-c)`, `M` from the rule above |
| `c = 1` if and only if `x >= 3`, `x` in `0..5` | `x >= 3 - 3*(1-c)` and `x <= 2 + 3*c` |
| `z = a AND b`, binaries | `z <= a`, `z <= b`, `z >= a + b - 1` |
| `v = TABLE[idx]`, `idx` a decision | binaries `ch[j]`: `sum(ch) == 1`, `idx == sum(j*ch[j])`, `v == sum(TABLE[j]*ch[j])` |
| all different `x[0..n-1]` in `1..m` | binaries `p[i][v]`: each row sums to 1, `x[i] == sum(v*p[i][v])`, each value sums to at most 1 |
| disjunction: one of `L_k <= R_k` holds | one binary `b_k` per branch: `L_k <= R_k + M*(1-b_k)`, `sum(b_k) >= 1` |
| no overlap of two jobs on one machine | one binary per pair of jobs: `end[i] <= start[j] + H*(1-o)` and `end[j] <= start[i] + H*o`, `H` the sum of durations |
| job shop: operations of each job in order, machines not shared at once, makespan | start variable per operation; `start[j,k] >= start[j,k-1] + dur[j,k-1]` along each job; one no-overlap binary per pair of operations on the **same** machine (not per pair of jobs); `makespan >= start[j,last] + dur[j,last]`; minimise `makespan` |

Runnable versions: [assets/encodings](assets/python/encodings/README.md) (`!=`, `abs`, element, reification), [assets/schedule-single-machine](assets/python/schedule-single-machine/README.md) (disjunction for no-overlap on one machine) and [assets/job-shop-makespan](assets/python/job-shop-makespan/README.md) (multi-machine job shop with precedence and makespan).

## Solving

A solve ends in one of five ways, and the answers differ:

| Outcome | Meaning |
|---|---|
| optimal | the optimum is proven (with no objective: a solution was found) |
| feasible, optimality not proven | a limit (time) ended the search with a solution in hand |
| infeasible | proven: no solution |
| unbounded | the objective is unbounded |
| no solution found | a limit ended the search with nothing found; this is not a proof of infeasibility |

Never report an optimum unless it is proven, and never report infeasibility for a run that hit a limit. Read values only after a solve that found a solution. The status names, parameters and the exact checks are in the interface file.

## All solutions

A MIP solver has no enumeration call. Solve, record the solution, add a **no-good cut** over the binary decision variables that excludes it, and repeat until the solve is no longer optimal. Runnable: [assets/python/enumerate-latin-square](assets/python/enumerate-latin-square/README.md). The loop is in the interface file.

| Need | Do |
|---|---|
| all solutions | the loop; cut over decision binaries only |
| all **optimal** solutions | solve; require a proven optimum; read the best value; pin the objective to it with a named constraint (keep the objective as one expression `score`), and run the loop. Runnable: [assets/python/all-optimal-committee](assets/python/all-optimal-committee/README.md) |
| no duplicates | auxiliary variables (flags, indicators) must not be in the cut; two solutions count as the same when their decision values match |
| integer decisions, not binary | encode each value with binaries first; a cut over raw integers is not linear |

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Wrong solutions, or none, after a disjunction or `!=` | big-M too small, so an inactive branch cuts off solutions | take `M` from the bounds: `max(left - right)`; for `!=` with `0..u`, `M = u+1` |
| Enumeration never ends | an unbounded integer, or cuts over auxiliary variables | bound all integers; cut only over decision binaries |
| `Unbounded` | a variable with no bound drives the objective | add upper bounds from the data |
| Job shop schedule overlaps on a machine, or precedence broken | no-overlap binaries written per pair of jobs, or missing along a job's chain | one binary per pair of operations on the same machine; `start[j,k] >= start[j,k-1] + dur` for each job ([assets/job-shop-makespan](assets/python/job-shop-makespan/README.md)) |

Symptoms that depend on the binding (type errors, status flags, deprecations, installation) are in the interface file.

## Further reading

- Documentation: [PuLP user guide](https://coin-or.github.io/pulp/) (no `llms.txt` is published)
- Examples: [set partitioning](https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html) and [sudoku](https://coin-or.github.io/pulp/CaseStudies/a_sudoku_problem.html) case studies
