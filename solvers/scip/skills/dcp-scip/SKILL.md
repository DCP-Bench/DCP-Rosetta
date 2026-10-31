---
name: dcp-scip
description: SCIP, a branch-and-cut mixed-integer and nonlinear solver with native general constraints (and/or/xor, indicator, cardinality, SOS, cumulative, nonlinear), used from Python (PySCIPOpt, pip package and import `pyscipopt`). Use when writing, debugging or explaining SCIP models in Python, or when the user has chosen SCIP for an optimisation or feasibility problem.
license: Apache-2.0
compatibility: "Python: Python 3.8+ and pip install pyscipopt (tested with PySCIPOpt 6.3.0, whose wheel bundles SCIP 10.0.2, on Python 3.12). SCIP is Apache-2.0 and PySCIPOpt MIT; no licence key or size limit."
metadata:
  domain: constraint-programming
  solver: scip
  paradigm: mip
  interfaces: "python"
---

# SCIP

SCIP is a branch-and-cut MIP solver that also handles general constraints natively:
logical and/or/xor, indicators, cardinality, SOS, cumulative and nonlinear expressions.
Use them where they state the problem directly; do not hand-linearise what SCIP already
supports. The objective must be linear, and the result is a **status** to check
before any value is read.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `pyscipopt` wheel; bundles SCIP, needs NumPy only |

Other bindings (C API, C++, Java, Julia and others from the SCIP documentation) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)

## Modelling

Use the general constraints where they state the problem; their exact calls, the encodings
SCIP lacks (`!=`, `abs`, min/max, `//`, `%`) and the examples are in the interface file.

Lessons that turned timeouts into solves:

- **One-hot binaries for discrete choices**: all-different as "each value at most once"
  is far stronger than pairwise `!=`.
- **Indicators instead of big-M**: indicator models solved where big-M versions timed out.
- **`abs` is slow in constraints**: `d == abs(x - y)` timed out from about 13 variables;
  a sign binary with indicators was fast ([encoding](references/python/encodings.md#absolute-value)).
- **Symmetry breaking and implied constraints** derived from the data
  ([details](references/python/encodings.md#search-help-symmetry-and-implied-constraints)).
- **Large coefficients in one linear equality are fine**: a cryptarithm's
  `SEND + MORE == MONEY` with `10**k` weights solved in milliseconds; no need to split it
  into column-wise carries.
- **Hold the objective in a bounded integer variable** (`z == expr`, bounds from the data,
  `setObjective(z)`): it can then be pinned to enumerate optima. With a bare expression as
  objective, one model proved its optimum in 2 s and then timed out finding a second
  optimal solution.

## Solving

| Outcome | Meaning |
|---|---|
| optimal | proven optimal (default gap 0); with no objective: a solution was found |
| infeasible | proven to have no solution; this is also the outcome of "no solution" with an objective |
| unbounded | objective unbounded |
| infeasible or unbounded | presolve could not decide: re-solve with presolve off |
| time or other limit | stopped, not proven; a solution exists only if one was found |

Names, parameters and the presolve-off re-solve: [interfaces/python.md](interfaces/python.md#solving).

## All solutions

There is no reliable built-in enumeration. Enumerate with no-goods in a loop: solve, stop
only at "infeasible" (any other status means the list is incomplete), record the values,
add a no-good over the variables that define a distinct solution, solve again. All optimal
solutions: solve, pin the objective variable to the optimum, then enumerate. Each solution
is a full re-solve, so time grows with their number: cap the list when a few are enough.
Calls and the objective pin: [interfaces/python.md](interfaces/python.md#all-solutions).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `inforunbd` taken as "no solution" | presolve could not tell infeasible from unbounded | re-solve with presolve off ([Solving](interfaces/python.md#solving)) |
| fractional objective: all-optimal list misses optima or repeats | objective variable declared integer, or pinned with `==` on a float | `z` continuous, pin `z <= best + 1e-6` (or `>=`) ([All solutions](interfaces/python.md#all-solutions)) |
| enumeration slow with many solutions | one full re-solve per no-good | expected; use `m.count()` for a count on pure binary linear models |
| `timelimit`, slow proof | weak formulation | one-hot binaries, indicators, no `abs`, symmetry breaking, implied constraints, tight bounds |

Binding-specific errors: [interfaces/python.md](interfaces/python.md#common-issues).

## Further reading

- Documentation and tutorials: https://pyscipopt.readthedocs.io/en/latest/
- Model API reference: https://pyscipopt.readthedocs.io/en/latest/api/model.html
- SCIP parameters: https://www.scipopt.org/doc/html/PARAMETERS.php
- Examples: https://github.com/scipopt/PySCIPOpt/tree/master/examples/finished (`logical.py` for and/or/xor, `gcp.py` graph colouring, `sudoku.py`, `diet.py`, `piecewise.py`)
