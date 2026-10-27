---
name: dcp-cpmpy
description: CPMpy is a Python constraint modelling library for constraint programming and optimisation, solved by OR-Tools CP-SAT by default (Python package cpmpy). Use when writing, debugging or explaining CPMpy models, or when the user has chosen CPMpy for scheduling, assignment, packing, sequencing or other combinatorial problems.
license: Apache-2.0
compatibility: Python 3.10+ and cpmpy 1.0.0 (tested; installs OR-Tools as a dependency). Other solvers need their own packages through extras. No key or size limits.
metadata:
  domain: constraint-programming
  solver: cpmpy
  paradigm: cp
  interfaces: "python"
---

# CPMpy

CPMpy is a modelling layer: you write NumPy-like expressions and constraints, and a
backend solver (OR-Tools CP-SAT by default) searches. Expressions are lazy: nothing is
computed until the model is solved.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `cpmpy` (installs `ortools`) |

Other bindings are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

Integer and Boolean variables (scalar or arrays), constraints from comparisons, arithmetic and
logic operators, reification and implication, and global constraints (all different, element,
table, cumulative, no-overlap, number of distinct values) and functions (sum, absolute value,
max, min). One objective, minimised or maximised. The exact calls are in the interface file;
full list: [API catalogue](references/python/api.md) and the
[model and variable reference](https://cpmpy.readthedocs.io/en/latest/api/model.html).
Integer only: a float coefficient anywhere fails.

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement, not the
API call.

## Solving

Status values: [solver interface](https://cpmpy.readthedocs.io/en/latest/api/solvers/solver_interface.html).

| Status | Meaning |
|---|---|
| `OPTIMAL` | optimisation: objective proven optimal |
| `FEASIBLE` | solution found, optimality not proven (time limit), or a satisfaction problem solved |
| `UNSATISFIABLE` | proven: no solution |
| `UNKNOWN` | limit reached with no solution found |

Satisfaction problems report `FEASIBLE`, not `OPTIMAL`. Solver parameters (time limit, workers,
seed) go to the backend, which must then be named. Calls: [interfaces/python.md](interfaces/python.md#solving).

## All solutions

- **The OR-Tools backend rejects enumeration on a model with an objective.** Build the
  enumeration model without the objective.
- **Solutions are counted over all variables of the model.** A variable the outputs do not
  determine (a free auxiliary variable) multiplies the count. An auxiliary variable fixed by the
  outputs does not duplicate, and expressions over decision variables create no counted variables.
  Either enumerate a model whose variables are all outputs, or loop with blocking clauses.
- **All optimal solutions**: solve with the objective to get the optimum, then enumerate a model
  without objective that fixes `objective == optimum`.

Code: [interfaces/python.md](interfaces/python.md#all-solutions).
[Solution enumeration](https://cpmpy.readthedocs.io/en/latest/api/model.html).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `solveAll` returns more solutions than expected | a free auxiliary variable the outputs do not determine | enumerate over outputs only, or use blocking clauses; see [All solutions](#all-solutions) |
| `solve()` is `False` but the cause is unclear | expected | read `model.status().exitstatus`: `UNSATISFIABLE` is proof, `UNKNOWN` is a limit |
| status `FEASIBLE` on a minimisation | time limit reached | the solution is valid but not proven optimal; raise the limit |


Issues specific to the Python API are in [interfaces/python.md](interfaces/python.md#common-issues).

## Further reading

- Documentation: [cpmpy.readthedocs.io](https://cpmpy.readthedocs.io/en/latest/)
- API reference: [model](https://cpmpy.readthedocs.io/en/latest/api/model.html), [global constraints](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html), [OR-Tools backend](https://cpmpy.readthedocs.io/en/latest/api/solvers/ortools.html)
- Examples: [CPMpy examples folder](https://github.com/CPMpy/cpmpy/tree/master/examples)
