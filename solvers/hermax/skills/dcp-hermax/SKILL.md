---
name: dcp-hermax
description: hermax is a MaxSAT modelling library (hermax.model.Model over PySAT) with Boolean and integer variables, hard constraints, weighted soft clauses for minimise and maximise, and solution enumeration. Python binding (pip package hermax). Use when writing, debugging or explaining hermax models or MaxSAT-style optimisation, or when the user has chosen hermax.
license: Apache-2.0
compatibility: Python binding - Python 3 with pip (tested with Python 3.12.11 and hermax 1.2.9, which installs python-sat); no licence key or account needed
metadata:
  domain: constraint-programming
  solver: hermax
  paradigm: maxsat
  interfaces: "python"
---

# hermax (MaxSAT)

hermax models are built with `hermax.model.Model`. Hard constraints are posted with
`m &= constraint`. An objective is a set of **weighted soft clauses**: `solve` minimises
the total weight of the soft clauses it breaks. The one idea to keep: a soft clause
`m.obj[w] += literal` pays `w` when the literal is **false**.

## Pick an interface

Read this file and the interface below.

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `hermax` (`hermax.model`) |

Other bindings are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Further reading](#further-reading)

## Modelling

Boolean and integer variables, hard constraints (cardinality, linear, all-different,
`cumulative`) and an objective made of weighted soft clauses. Exact calls, patterns and
pitfalls are in the interface file. Full list:
[API reference](https://hermax.readthedocs.io/en/latest/api.html).

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement, not the
API call.

## Solving

| Status | Meaning |
|---|---|
| `sat` | satisfiable (the model has no soft clauses) |
| `optimum` | proven optimal (soft clauses present) |
| `unsat` | proven: no solution |
| `interrupted_sat` | a solution found, optimality not proven (time limit) |
| `interrupted` | time limit reached, no solution |
| `unknown` | the backend gave no verdict |
| `error` | the solve failed |

A maximisation with soft clauses (`m.obj[w] += x`) is solved as minimising the forgone weight, so `cost` is that forgone weight; an expression maximised as `m.obj += 0 - expr` reports the negated value instead.

## All solutions

Enumeration is by blocking clauses: solve, forbid exactly the answer found (over the
variables you report), and solve again until the status is no longer `sat`. All optimal
solutions: solve for the optimum, record the cost, then block each optimal answer and
re-solve while the status is `optimum` and the cost is unchanged. Code: the interface file.

## Further reading

- Documentation: [hermax.readthedocs.io](https://hermax.readthedocs.io/en/latest/)
- Quick start and modelling guide: [quickstart](https://hermax.readthedocs.io/en/latest/quickstart.html), [modeling](https://hermax.readthedocs.io/en/latest/modeling.html)
- API reference: [api](https://hermax.readthedocs.io/en/latest/api.html)
- Solver backends: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html), [incremental](https://hermax.readthedocs.io/en/latest/incremental.html)
- Runnable examples: [satisfy](assets/python/satisfy/README.md), [all-solutions](assets/python/all-solutions/README.md), [all-optimal](assets/python/all-optimal/README.md), [maximise](assets/python/maximise/README.md), [minimise](assets/python/minimise/README.md), [infeasible](assets/python/infeasible/README.md), [scheduling](assets/python/scheduling/README.md)
- Examples: [examples](https://hermax.readthedocs.io/en/latest/examples.html) (UWrMaxSAT, RC2, graph colouring, scheduling)
