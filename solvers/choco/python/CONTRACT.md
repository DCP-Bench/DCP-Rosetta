# choco_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Choco
(pychoco) expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`,
`flatten` and `mapped` from [runner/runtime.py](../../../runner/runtime.py) but has its own
`build`, solve and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `pychoco` and the standard library; nothing
else is installed (no NumPy), and no other file of yours is staged. The standalone run
block imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[Model, dict, dict | None]:
```

It must return a 3-tuple `(model, outputs, objective)`, with `model` a
`pychoco.model.Model` and `objective` None for a satisfaction problem (see
[Objective](#objective)). The runner imports the file as module `candidate`. Anything the
module prints goes to stderr. For an optimisation problem the runner calls
`create_model(instance)` three times (a Choco search cannot be rewound), so it must build a
fresh, identical model on each call. Models retained before 2026-10-30 name it
`build(instance)`, which the runner still accepts; write `create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a Choco `IntVar` or
`BoolVar`, a Python integer or Boolean, or a nested list/tuple of these with the declared
shape; the standalone run reads each leaf with `solution.get_int_val`, so use variables, not
plain integers. The runner reads `.get_value()` from each variable leaf: an `IntVar` gives an
`int`, a `BoolVar` a `bool`. Any leaf without `get_value` (a constraint, a string) is
rejected.

## Objective

The third element of the return value: the arguments of `find_optimal_solution`,
`{"objective": var, "maximize": True}` (or `False` to minimise), with `var` a Choco variable
of that model; None for a satisfaction problem. Do not call `model.set_objective`: nothing
reads it. The runner proves the optimum with
`find_optimal_solution`, rebuilds the model and posts `arithm(var, "=", best)` before
enumerating.

## Solving

- The runner sets one parameter, Choco's time limit, as `limit_time("<seconds>s")` with
  the time left (at least 1 ms). It is written in seconds because pychoco 0.2.1 ignores
  a limit written in milliseconds.
- Optimisation: `find_optimal_solution` on a first build. A result returned at least
  0.5 s before the budget left is the optimum; no result that early gives `unsat`; any
  later return gives `timeout`.
- Enumeration: repeated `solver.solve()` on a fresh build with `arithm(objective, "=",
  best)` posted. No no-good is added: Choco moves on to its next assignment of all
  variables, and the runner skips any whose declared outputs it has already reported.
  `solve()` returning false at least 0.5 s before the budget is exhaustion (`complete`,
  or `unsat` with nothing found); later is `timeout`.
- Time: the budget runs from the start of the run (including the first `build`). A
  search stops at Choco's own limit; a search stopped that late is reported as
  `timeout`. A `SIGALRM` at `execution_timeout + 5` s is a backstop that only fires once
  control is back in Python.

## Compilation

None.

## Environment

Image `dcp-eval/choco_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, pychoco 0.2.1 and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). pychoco carries Choco as a native
library (`site-packages/pychoco/libchoco_capi.so`): there is no JVM and nothing is fetched
at run time. JSON is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/choco_python:v1 -c '...'`.

## Traps

- The objective must be a variable (anything with `get_value`), not an expression: post
  an equality onto an `IntVar` and pass that, or the run is an `execution_error`.
- `import numpy` fails in this image (`execution_error`), except inside the standalone run
  block, which the runner never executes.
- `create_model` must be deterministic and side-effect free: the optimum is proven on one call's
  model and pinned on another's.
- Choco enumerates assignments of every variable; the runner skips repeats of the declared
  outputs, which costs search time. Auxiliary variables left free can starve enumeration.
- An output leaf that is not a variable, integer or Boolean raises in the runner and is
  reported as `execution_error`.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a Choco-solver (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python knapsack.py knapsack.json

from pychoco.model import Model


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = Model()

    # x[i] is true when the hiker packs item i
    x = [model.boolvar(name=f"x{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.scalar(x, weights, "<=", capacity).post()

    # The total value of the packed items, which the hiker wants as large as possible.
    total_value = model.intvar(0, sum(values), name="total_value")
    model.scalar(x, values, "=", total_value).post()

    return model, {"x": x}, {"objective": total_value, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with Choco-solver
and numpy. Nothing else goes in either: the header is the first lines of the file, the run block
the last, and the model sits between them. The runner loads the file as module `candidate`,
so the block never runs during evaluation.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pychoco numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
```
