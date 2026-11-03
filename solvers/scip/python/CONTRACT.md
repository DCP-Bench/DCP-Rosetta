# scip_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how PySCIPOpt
(Python, SCIP) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving, in a
worker process it supervises.

## Submission file

One Python file, `model.py`. It may import `pyscipopt`, `numpy` and the standard library;
nothing else is installed, and no other file of yours is staged. Outside the standalone
run block, do not call `optimize()`, and do not set the time limit, threads, gap or
presolve: the runner does what it needs (see Solving). The run block, which the runner
never executes, solves and prints with `numpy`.

## Entrypoint

```python
def create_model(instance) -> tuple[pyscipopt.Model, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)`
once, in its worker process. Models retained before 2026-11-03 name it `build(instance)`,
which the runner still accepts; write `create_model`. It
must return a 2-tuple (not a list) `(model, outputs)` with `model` a `pyscipopt.Model`;
anything else is an `error` (`execution_error`). Anything the module prints, at import or
in `create_model`, goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Every field is there, including ragged or mixed-type ones the
brief lists as unbindable and extra keys (`name`, `note`) to ignore. The shape of each
field is printed by `python -m generation.brief PROBLEM` (from the example instance);
take every size from the data itself, not from that shape.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a leaf or a nested
`list`/`tuple` of leaves. A NumPy array, including a `MatrixVariable` from
`addMatrixVar` and a `MatrixExpr`, is expanded element by element. A leaf is one of:

- a variable (`addVar`): its value is rounded to the nearest integer, so a binary is
  reported as `0`/`1`, an integer as an integer;
- an expression (`x + 2*y`, `quicksum(...)`, a product): evaluated in the solution with
  `getBestSol()[expr]` and rounded the same way;
- a Python `bool`: reported as is;
- a Python or NumPy number: reported as an integer when it is within 1e-6 of one.

A value further than 1e-6 from an integer (a continuous variable at 0.5, a constant 2.5)
is refused: `error`, which the evaluator records as `execution_error`. Values are read
only after SCIP proved its status `optimal` and holds a solution, never from the
`getVal` default of 0.

## Objective

`model.setObjective(expr, "minimize")` or `"maximize"`. The objective must be linear; an
objective with no variable terms (never set, or a constant) is a satisfaction problem.

The runner pins the objective to the proven optimum before enumerating (see Solving).
When the search for a second optimal solution is slow, hold the objective in a bounded
integer variable: `z = model.addVar(vtype="I", lb=.., ub=..)` with bounds from the data,
`model.addCons(z == expr)`, `model.setObjective(z, ...)`. With a bare expression as
objective, one model proved its optimum in 2 s and then timed out searching for the
second optimal solution.

## Solving

- Forced after `create_model` returns, over the submission's own settings: `hideOutput()`,
  `parallel/maxnthreads = 1`, `limits/gap = 0` and `limits/absgap = 0` (so `optimal`
  means proven whatever the submission set), and `limits/time` = the budget left before
  each solve. Other parameters the submission sets are kept.
- Status: `optimal` with a solution is a proven answer; `infeasible` is `unsat`;
  `unbounded` is `error` (objective unbounded); `timelimit` is `timeout`, with nothing
  reported for an unproven optimum. On `inforunbd` the runner frees the transform,
  turns presolve off and solves once more, then maps the new status. Any other SCIP
  status (`nodelimit`, `sollimit`, `gaplimit`, `userinterrupt`, ...) is `error` naming
  it. The final status `limit` means the requested number of solutions was reached: it
  is not a failure.
- Enumeration: after the first proven solve, `freeTransform()`, then the objective is
  pinned by two constraints (±0.5 around the optimum when every objective coefficient is
  integral and no objective variable is continuous, a relative 1e-6 otherwise) and
  replaced by 0. Each next solve adds a no-good over the variables the declared outputs
  are built from (variable leaves, and every variable in an expression leaf); globally
  fixed variables are skipped. A binary contributes the linear term `x` or `1 - x`; a
  general integer contributes up to two new binaries with indicator constraints
  `x <= v - 1` and `x >= v + 1` (only on a side its bounds leave room for, so unbounded
  integers work too); the no-good requires one of them. A repeated output value is
  re-solved, not emitted, so auxiliary variables never produce repeats. `infeasible`
  after a no-good, or no unfixed variable left to move, is `complete`; `timelimit`
  during enumeration is `timeout` (the solutions already emitted stand).
- Process: SCIP can crash the whole process (SIGSEGV), so the model is built and solved
  in a worker process. The supervisor relays the worker's solution records and holds back
  its final status. A worker that dies on a signal is `error` naming the signal
  (`SCIP worker terminated by signal SIGSEGV`); one that exits nonzero, e.g. through
  `sys.exit(3)`, is `error` with that status (`SCIP worker exited with status 3`).
- Time: the deadline is set in the worker before `create_model` runs, so importing and building
  spend the budget. Each solve gets the time left; at budget + 5 s the supervisor kills
  the worker and reports `timeout`.
- A legacy request is `unsupported`.

## Compilation

None.

## Environment

Image `dcp-eval/scip_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11
(`/usr/local/bin/python`), PySCIPOpt 6.3.0 whose wheel bundles SCIP 10.0.2, NumPy
2.4.6, both pinned by hash in [requirements.txt](requirements.txt) and installed from
binary wheels only; the standard library (`json` included) and nothing else. SCIP is
Apache-2.0: no licence file, no size limit. A local image built from an older
requirements file can carry older versions; `docker run --rm --entrypoint pip
dcp-eval/scip_python:v1 list` shows what it has.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs,
the working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`, no `/dataset`. The runner keeps the protocol on its own copy of file
descriptor 1 and sends fd 1, and everything the submission or SCIP prints, to stderr.
The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad hoc run
override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/scip_python:v1 -c '...'`.

## Traps

- `addConsIndicator` without `binvar=` crashes SCIP with SIGSEGV at solve time: the run
  ends as `error` (`terminated by signal SIGSEGV`), never as a wrong answer.
- A parameter that adds a stop of its own (`limits/nodes`, `limits/solutions`, ...)
  makes SCIP stop with a status other than `optimal`, which the runner reports as
  `error`.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment with
  the same value. A one-hot sum such as `quicksum((c + 1) * b[r, c] ...)` is fine;
  otherwise declare the output as its own integer variable linked by `==`.
- A general expression leaf (`abs(x)`, `sqrt`, ...) is evaluated, but its variables are
  not in the no-good: if no output variable is left to block, the runner stops with
  `complete` after the first solution. Declare such an output as an integer variable.
- A `dict` inside an output is walked as one and comes out as a JSON object
  (`invalid_output`); a NumPy `bool_` leaf is not read (`execution_error`). Return lists
  of variables and Python `bool`s.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a SCIP (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python knapsack.py knapsack.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [model.addVar(f"x_{i}", vtype="B") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.addCons(quicksum(w * xi for w, xi in zip(weights, x)) <= capacity)

    # Pack the most valuable selection.
    model.setObjective(quicksum(v * xi for v, xi in zip(values, x)), "maximize")

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with PySCIPOpt and
numpy (the wheel bundles SCIP). Nothing else goes in either: the header is the first lines
of the file, the run block the last, and the model sits between them. The runner loads the
file as module `candidate`, so the block never runs during evaluation.

The run block silences SCIP, solves once, and prints each output as `round(model.getVal(v))`
through `numpy.vectorize` when the status is `"optimal"`. It sets no gap: SCIP's default
`limits/gap` and `limits/absgap` are 0, so `"optimal"` is a proven optimum, and it is also
the status of a satisfaction model with a solution. Otherwise it prints the status, such as
`infeasible`; `inforunbd` means presolve could not tell infeasible from unbounded (the
runner then re-solves with presolve off). PySCIPOpt has no call that reads a plain list of
variables (`getVal` takes one variable or expression, or a matrix), hence `numpy.vectorize`,
which reads lists, nested lists, matrix variables and matrix expressions alike. It fails on
a plain `int` or `bool` (`TypeError`), on an empty list and on a ragged nested list, so give
a fixed output as a variable and keep each output rectangular.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
```
