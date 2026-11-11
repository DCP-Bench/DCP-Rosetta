# gurobipy_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how gurobipy
(Python, Gurobi) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `gurobipy`, `numpy`, `scipy` and the standard
library; nothing else is installed, and no other file of yours is staged.

## Entrypoint

```python
def create_model(instance) -> tuple[gurobipy.Model, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
Models retained before 2026-11-03 name it `build(instance)`, which the runner still
accepts; write `create_model`. It must return a 2-tuple
(not a list) `(model, outputs)` with `model` a `gurobipy.Model`. Anything the module
prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a `gp.Var`,
`LinExpr` or `QuadExpr`, a Python/NumPy integer or Boolean, or a nested `list`/`tuple`
of these. Anything with `.tolist()` (an `MVar`, a NumPy array) is expanded element by
element. Integer and binary variables are rounded to the nearest integer and expressions
are evaluated over the rounded values. A `GRB.BINARY` variable is reported as `0`/`1`.
A value that is not within 1e-6 of an integer is rejected (`execution_error`).

## Objective

`model.setObjective(expr, GRB.MINIMIZE)` or `GRB.MAXIMIZE`. An objective with no
variable terms (never set, or a constant) is a satisfaction problem; more than one
objective (`NumObj > 1`) is `unsupported`.

The objective reported with each solution is the objective expression evaluated on that
solution (its constant included, integer variables rounded), in the model's own direction.
The incumbents are Gurobi's `MIPSOL_OBJ`, which already has the model's constant
(`ObjCon`) and direction (Gurobi maximises natively).

## Solving

- Forced over the submission's own parameters: `OutputFlag = 0` (no solver log),
  `Threads = 1`, `MIPGap = 0` (Gurobi's default 1e-4 relative gap reports `OPTIMAL` short
  of the optimum) and `TimeLimit` = the budget left. Other parameters you set are kept.
- Status: `OPTIMAL` with a solution is proven; `INFEASIBLE` is `unsat`; `UNBOUNDED` is
  `error` (objective unbounded); `TIME_LIMIT` is `timeout`; any other status is `error`.
  On `INF_OR_UNBD` the runner re-solves once with `DualReductions = 0` and maps the new
  status. `SIZE_LIMIT_EXCEEDED` is `unsupported`, any other `GurobiError` `error`.
- Incumbents: the first solve of an optimisation passes a `MIPSOL` callback (it only reads)
  that reports each improving integer `MIPSOL_OBJ` as an `incumbent`, with the seconds
  since `optimize()` was called. Later solves pass none.
- Enumeration is not pool-based: after the first proven solve the objective is pinned by
  two constraints (±0.5 around the optimum for an integral objective) and replaced by 0;
  each next solve adds a no-good over the integer variables under the declared outputs
  (a linear term per binary, two indicator constraints per general integer; fixed
  variables skipped). A repeated output value is re-solved, not emitted. Infeasible after
  a no-good, or no unfixed variable left to move, is `complete`.
- Time: the deadline is set before `create_model` runs, so building spends the budget. Each solve
  gets the time left; a SIGALRM at budget + 5 s, armed over `create_model` and the whole loop,
  turns a hang in Python into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/gurobipy_python:v1`: Python 3.12.11 (`/usr/local/bin/python`), gurobipy
13.0.3 (Gurobi Optimizer 13.0.3), NumPy 2.4.6, SciPy 1.18.1; the standard library (`json`
included) and nothing else. The wheel's bundled licence needs no licence file and no
network (the container has none) and expires 2027-11-29. It refuses a model above 2000
variables or 2000 linear constraints with `GurobiError` 10010 (`SIZE_LIMIT_EXCEEDED`):
`Model too large for size-limited license; visit https://gurobi.com/unrestricted for more
information`. Its banner (`Restricted license - for non-production use only - expires
2027-11-29`) is printed from C to file descriptor 1; the runner keeps the protocol on its
own copy of that descriptor and sends fd 1, and everything the submission prints, to
stderr. For an ad hoc run, `--entrypoint sh` bypasses `/opt/runner/run.py`.

On a machine configured with a Gurobi token server (`python -m evaluation.licences set
gurobi FILE`), the evaluator binds a client licence at `/run/licence/gurobi.lic`
(`GRB_LICENSE_FILE`) and relays the server through a socket. The container still has no
network, and the size limit is lifted. A model must work either way: everything
above holds without the server, and the result's `licence` says which edition ran
(`licensed` or `size-limited`). If the server refuses or cannot be reached, the result is
`licence_unavailable`, which says nothing about the model.

## Traps

- The licence size limit (see Environment) is reported as `unsupported`, which the
  evaluator records as `unsupported_capability`; size the model for the largest
  instance. Enumeration adds rows of its own: two constraints pinning the objective,
  one no-good per extra solution, and per general-integer output variable up to two
  binaries and two indicator constraints.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
- A `tupledict` from `addVars` is a dict, which the runner walks as one. Keyed by tuples
  it crashes serialisation (`execution_error`, not `invalid_output`); keyed by ints it
  becomes a JSON object (`invalid_output`). Return lists:
  `[[x[i, j] for j in range(m)] for i in range(n)]`.
- An `MLinExpr` or a general expression (`gp.abs_`, `gp.max_`, ...) is not an accepted
  leaf (`execution_error`): give a list of `LinExpr`, or the variable the general
  constraint defines.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment
  with the same value. Declare such an output as its own integer variable.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a Gurobi (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python knapsack.py knapsack.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = gp.Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [model.addVar(vtype=GRB.BINARY, name=f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.addConstr(gp.quicksum(w * xi for w, xi in zip(weights, x)) <= capacity)

    # Pack the most valuable selection.
    model.setObjective(gp.quicksum(v * xi for v, xi in zip(values, x)), GRB.MAXIMIZE)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced by
the problem id, so a reader can copy it from the catalogue and run it with gurobipy and numpy.
Nothing else goes in either: the header is the first lines of the file, the run block the last,
and the model sits between them. The runner loads the file as module `candidate`, so the block
never runs during evaluation.

The run block silences Gurobi, sets `MIPGap` to 0 as the runner does (the default stops within
0.01% of the optimum and still reports `OPTIMAL`), solves once, and when the status is
`GRB.OPTIMAL` prints the objective value (`model.ObjVal`) and each output as an integer through
`numpy.vectorize`. Gurobi also returns `GRB.OPTIMAL` for a model with no objective that has a
solution. A satisfaction model's block leaves out the `MIPGap` line and the objective line, and
its status comment reads `# a solution`. Otherwise it prints the status code:
3 is infeasible, and 4 means presolve could not tell infeasible from unbounded (the runner then
re-solves with `DualReductions = 0`). Gurobi's batch call `model.getAttr("X", variables)` reads
only a flat list, not nested lists, a matrix variable or an expression, hence
`round(gp.LinExpr(out).getValue())` through `numpy.vectorize`, which reads a variable, a linear
expression or a number inside lists of any depth. It fails on a `QuadExpr`, an empty list, a
ragged list, a `tupledict` and an `MVar` (give `.tolist()`), so keep each output a rectangular
list.

The licence that comes with `pip install gurobipy` prints its banner (`Restricted license - for
non-production use only`) when the first model is created, and refuses a model above 2000
variables or 2000 linear constraints; the header says so.

A satisfaction example, whose outputs are linear expressions:

```python
# sudoku: a Gurobi (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python sudoku.py sudoku.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Fill a 9-by-9 grid with digits so that every row, every column and every
    3-by-3 box holds each of the digits 1 to 9 exactly once."""
    given = instance["input_grid"]  # given[r][c]: the digit in row r, column c, or 0 when empty

    # The 9-by-9 grid and its 3-by-3 boxes are fixed by the rules of Sudoku.
    lines = range(9)  # row and column numbers
    digits = range(1, 10)

    model = gp.Model("sudoku")

    # holds[r, c, d] is 1 when the cell in row r, column c holds digit d
    holds = model.addVars(lines, lines, digits, vtype=GRB.BINARY, name="holds")
    # Every cell holds exactly one digit (holds.sum(r, c, "*") adds holds[r, c, d] over all d).
    model.addConstrs((holds.sum(r, c, "*") == 1 for r in lines for c in lines), name="one_digit")

    # A filled-in cell keeps its digit.
    model.addConstrs((holds[r, c, given[r][c]] == 1 for r in lines for c in lines
                      if given[r][c] != 0), name="given")

    # Each digit appears once in every row and once in every column.
    model.addConstrs(holds.sum(r, "*", d) == 1 for r in lines for d in digits)
    model.addConstrs(holds.sum("*", c, d) == 1 for c in lines for d in digits)

    # Each digit appears once in every 3-by-3 box.
    model.addConstrs(gp.quicksum(holds[r, c, d] for r in range(top, top + 3)
                                 for c in range(left, left + 3)) == 1
                     for top in (0, 3, 6) for left in (0, 3, 6) for d in digits)

    # grid[r][c] is the digit in row r, column c
    grid = [[gp.quicksum(d * holds[r, c, d] for d in digits) for c in lines] for r in lines]

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
```

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`) has
all its data fixed by the statement. Its header is

```python
# abbots_puzzle: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python abbots_puzzle.py
```

and its run block is the one above with `import json` and `import sys` and the two lines that
read the instance file removed, and `create_model({})` in place of `create_model(instances[index])`.
