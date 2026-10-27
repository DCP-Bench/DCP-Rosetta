---
name: dcp-pycsp3
description: PyCSP3 is a Python library (pip package and import pycsp3) that compiles constraint models to XCSP3; the ACE solver ships inside the wheel as a Java jar and solves them. Use when writing, debugging or explaining PyCSP3 models in Python, or when the user has chosen PyCSP3 or ACE for a constraint satisfaction or optimisation problem.
license: Apache-2.0
compatibility: "Python: Python 3.10+, pycsp3 (tested 2.6.1, MIT, pulls in lxml) and a Java runtime on PATH for the bundled ACE-2.6.jar (tested with OpenJDK 17). No licence key."
metadata:
  domain: constraint-programming
  solver: ace
  paradigm: cp
  interfaces: "python"
---

# PyCSP3 with ACE

PyCSP3 is a modelling library: Python statements declare variables and post constraints,
`solve()` compiles the model to an XCSP3 file (`<script>.xml`) and runs ACE, a Java CP
solver bundled in the wheel, as a subprocess. Keep in mind that **the variable names come
from the Python source line** that declares them, and that a **solver-side error is not an
exception**: `solve()` returns `UNKNOWN` and the cause is in ACE's log file.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `pycsp3` wheel (import `pycsp3`); ACE-2.6.jar inside it, needs a Java runtime on `PATH` |

Other bindings (the XCSP3 format is also read by other solvers, and PyCSP3 can target them) are not covered yet.

## Contents
- [Solving](#solving) · [All solutions](#all-solutions) · [Modelling lessons](#modelling-lessons)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Python: [interfaces/python.md](interfaces/python.md); sources in [sources.md](sources.md)

## Solving

`solve()` compiles the model and runs ACE; the outcome is one of four statuses.

| Status | Meaning |
|---|---|
| `OPTIMUM` | optimisation, optimum proven |
| `SAT` | a solution; for an optimisation, **not proven optimal** (time limit) |
| `UNSAT` | proven infeasible; no values stored |
| `UNKNOWN` | nothing found: time limit, or a solver error (the cause is in ACE's log file, not an exception)|

Calls, options and the error log are in [the Python interface](interfaces/python.md#solving).

## All solutions

ACE enumerates assignments of all constrained variables, so an auxiliary variable that is
not fixed by the ones you print repeats them; deduplicate on the printed values or fix it.
The status is `SAT` whether or not the search finished; an infeasible model enumerates to
`UNSAT`, not `SAT` with zero solutions. The calls and the counting traps are in
[the Python interface](interfaces/python.md#all-solutions).

**All optimal solutions**: solve with the objective, require `OPTIMUM`, keep the optimum;
then rebuild the model, post `objective == optimum` with no objective, and enumerate.
Code: [example](assets/python/all-optimal-permutation/README.md).

## Modelling lessons

Learned across hundreds of PyCSP3 models; the timing claims were measured on small instances.

- **Boolean indicators instead of `NValues`** in a feasibility model: one 0/1 variable per
  (item, value), linked by `(ind[i][c] == 1) == (x[i] == c)`, with plain `Sum` counts, beat
  `NValues` over integer colours on Schur-type colouring models ([examples.md](references/python/examples.md#boolean-indicators-instead-of-nvalues)).
- **`NValues` as the objective** works: `minimize(NValues(colour))` proved the fewest colours
  on a 6-cycle (2), K4 (4), Petersen (3) and a wheel ([fewest colours](assets/python/colouring-min-colours/README.md)).
  A `Maximum`-index objective (`Maximum(colour) == top`, `minimize(top)`) also worked on three
  graphs; use `NValues` unless you need the index.
- **`Product` over four or more variables**: ACE 2.6 accepts wrong tuples (`[100, 50, 1, 1]`
  for `Product == 5040`). Split into binary products with an auxiliary `VarArray`
  ([examples.md](references/python/examples.md#product-of-four-variables-split-into-binary-products)).
- **Symmetry breaking**: `LexIncreasing([row_a, row_b])` orders vectors; for the transpose
  symmetry of a square grid, order the flat row-major list against the flat column-major list
  ([examples.md](references/python/examples.md#grid-symmetry-with-lexincreasing-transpose)). Add it
  only when equivalent solutions are truly interchangeable for the question asked.
- **Nonogram-style lines**: one `Regular` automaton per line, reading cell values, with final
  states that close each run.
- Keep domains tight (they are materialised value by value) and constrain every variable you
  read back.

## Common issues

Solver-side symptoms; syntax and API symptoms are in [the Python interface](interfaces/python.md#common-issues).

| Message or symptom | Cause | Fix |
|---|---|---|
| `UNKNOWN`; log: `Fatal Error: The id E is a keyword, and so cannot be used.` | reserved identifier | rename ([list](references/python/language.md#variables-and-domains)) |
| `UNKNOWN`; log: `Fatal Error: Too big integer value 2147483640` | value >= about 2.1e9 | rescale |
| `UNKNOWN`; log: `! ERROR (use -ev ...)`; ACE `-ev`: `java.lang.OutOfMemoryError` | too many domain values | tighter domains, or more heap |
| `SAT` for an optimisation | time limit before the proof | longer `-t`, stronger model |

## Further reading

- Documentation: <https://pycsp.org/> (models and data: <http://pycsp.org/models/>)
- Source and solver options: <https://github.com/xcsp3team/pycsp3>
- ACE: <https://github.com/xcsp3team/ace>
