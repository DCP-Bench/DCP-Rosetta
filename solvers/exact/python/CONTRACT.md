# exact: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Exact
(Python bindings) expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`,
`flatten` and `mapped` from [runner/runtime.py](../../../runner/runtime.py) but has its own
loader, solve and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `exact` and the standard library; nothing else
is installed (no NumPy), and no other file of yours is staged. The standalone run block
imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[Exact, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return a 2-tuple `(solver, outputs)` with `solver` an `exact.Exact`; an
optimisation problem sets its objective on that solver (see [Objective](#objective)).
Anything the module prints goes to stderr. Models retained before 2026-11-02 name it
`build(instance)` and may return the objective as a third value, `("minimize", terms)` or
`("maximize", terms)`; the runner still accepts that form. Write `create_model` and set the
objective on the solver.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a **variable name**
(the `str` given to `addVariable`), or a nested list/tuple of names with the declared
shape. The runner reads them all with `getLastSolutionFor(names)`; every value comes back
as an integer, so a Boolean output is a variable over 0..1 reported as `0`/`1`.

## Objective

Set on the solver inside `create_model`, as Exact's own examples do:
`solver.setObjective(terms, minimize=True)` (or `minimize=False` to maximise), with `terms`
a list of `(integer coefficient, variable name)` pairs and an optional `offset`. A
satisfaction problem sets none. Exact cannot hand an objective back, so before importing the
submission the runner replaces `exact.Exact` with a subclass that records the arguments of
`setObjective` and passes them on unchanged. It calls `toOptimum`, accepts only the state
`"SAT"` as a proven optimum, then pins `terms` at that value with `addConstraint` before
enumerating.

## Solving

- The runner sets no solver option; it passes the seconds left of `execution_timeout`
  (measured from the start of the run, `create_model` included) as the timeout of each
  `toOptimum` and `runFull` call.
- Optimisation: `toOptimum` returning `"SAT"` is the proven optimum, `"UNSAT"` gives
  `unsat`, and `"TIMEOUT"` or any other state gives `timeout` (the incumbent Exact still
  holds is never reported). Exact minimises internally and reports the objective plus
  its offset, so the runner negates the returned value for a maximisation and subtracts
  the offset before pinning `terms` to it.
- Enumeration: `runFull(False, left)`. `"SAT"` reports a solution, `"UNSAT"` gives `unsat`
  on the first call and `complete` after, anything else `timeout`.
- Next solution: `invalidateLastSol(names)`, Exact's own blocking clause projected onto
  the declared output variables, so solutions differing only in auxiliary variables are
  not found twice.
- Time: there is no `SIGALRM`; only Exact's timeouts bound the search. Import and `create_model`
  are not bounded by the runner: the evaluator kills the container at
  `execution_timeout + 10` s, reported as `execution_timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/exact:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, `exact` 2.2.1 (pip lists it as `Exact`; one compiled module,
`site-packages/exact.cpython-312-x86_64-linux-gnu.so`) and nothing else besides pip (the
shared `runner/requirements.txt` stack is not installed). JSON is the standard library's
`json`. No edition or size limits (a variable over 0..10^20 is accepted); the package is
AGPL-3.0.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/exact:v1 -c '...'`.

## Traps

- An output leaf must be a `str` naming a declared variable. A Python integer, Boolean or
  any other object is rejected (`execution_error`); for a constant output declare a fixed
  variable, `addVariable(name, c, c)`. An undeclared name raises
  `ValueError: No variable ... found` (`execution_error`).
- The objective is a term list, not an expression. Set it once: a second `setObjective`
  replaces the first, and the runner pins the last one.
- `import numpy` fails in this image (`execution_error`), except inside the standalone run
  block, which the runner never executes.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: an Exact (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python knapsack.py knapsack.json

from exact import Exact


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [f"x{i}" for i in range(len(values))]
    for name in x:
        solver.addVariable(name, 0, 1)

    # The packed items weigh no more than the backpack can carry.
    solver.addConstraint(list(zip(weights, x)), False, 0, True, capacity)

    # Pack the most valuable selection.
    solver.setObjective(list(zip(values, x)), minimize=False)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with Exact and
numpy. Nothing else goes in either: the header is the first lines of the file, the run block
the last, and the model sits between them. The runner loads the file as module `candidate`,
so the block never runs during evaluation.

The run block is the same for satisfaction and optimisation: `runFull()` stops at the first
solution when no objective is set, and otherwise searches until no better solution exists.
Each output is read with one `getLastSolutionFor` call on its names, flattened with
`numpy.ravel` and put back in the output's shape with `numpy.reshape`; a single name is a
0-d array to both. The first list of variable names in a model carries the comment
`# Exact identifies its variables by name.`

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install exact numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
```
