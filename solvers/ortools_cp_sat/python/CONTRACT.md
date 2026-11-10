# ortools_cp_sat_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how OR-Tools
CP-SAT (Python) expresses it. Runner: [run.py](run.py), which calls `main("cp_sat")` in
[runner/runtime.py](../../../runner/runtime.py).

## Submission file

One Python file, `model.py`. It may import `ortools`, `numpy` and the standard library
(the image installs the shared `runner/requirements.txt` stack); no other file of yours
is staged.

## Entrypoint

```python
def create_model(instance) -> tuple[cp_model.CpModel, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return a 2-tuple `(model, outputs)` with `model` a `cp_model.CpModel`. Anything the
module prints goes to stderr, not to the result. Models retained before 2026-10-30 name it
`build(instance)`, which the runner still accepts; write `create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Convert to NumPy yourself where that helps.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a CP-SAT `IntVar`,
`BoolVar` (or its `.Not()`), integer linear expression, Python/NumPy integer or Boolean,
or a nested list/tuple/NumPy array of these with the declared shape. The runner reads each
leaf with `int(solver.value(leaf))`, so every value, Booleans included, is reported as an
integer (`0`/`1` for a Boolean).

## Objective

Set it on the model: `model.minimize(expr)` or `model.maximize(expr)`, with an integer
linear expression. No objective for a satisfaction problem.

The objective is the problem's own value: do not scale, offset or negate it. Each
solution record carries it as `objective`. CP-SAT stores an objective as integer terms
plus an offset and a scaling factor, and a maximisation with its terms and offset negated
and a factor of -1; the runner computes `scaling_factor * (terms + offset)` exactly from
the solution's values, which is the expression given to `minimize`/`maximize`, constant
included. Solutions enumerated at the optimum carry the same value. No improving
solutions are reported.

## Solving

- Every solve uses a fresh `CpSolver` with `num_search_workers = 1`,
  `keep_all_feasible_solutions_in_presolve = True` and `max_time_in_seconds` = the
  seconds left; the submission cannot set solver parameters.
- Right after `build`, before any solve, a floating-point objective is refused with
  runner status `unsupported` (see Traps).
- Status: `OPTIMAL` is accepted; `FEASIBLE` is accepted only without an objective, and
  with one (an incumbent at the time limit) gives `timeout` ("Candidate optimum was not
  proven"). `INFEASIBLE` gives `unsat` on the first solve and `complete` after;
  `MODEL_INVALID` gives `error` (see Traps); `UNKNOWN` gives `timeout`.
- Next solution: the objective is cleared and pinned (`expression == best`), then one
  reified `leaf != value` per declared output leaf (Booleans `_different_<k>_<i>`) and
  their `add_bool_or` are added and the model is solved again. Exhausted when that solve
  is `INFEASIBLE`.
- Time: each solve gets what is left of `execution_timeout`, measured from the start of
  the run (including `build`); a `SIGALRM` at exactly `execution_timeout` turns into
  `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/ortools_cp_sat_python:v1` (`python:3.12.11-slim-bookworm`): Python
3.12.11 at `/usr/local/bin/python`, OR-Tools 9.15.6755, NumPy 2.5.3, all pinned in
`runner/requirements.txt`, which also installs CPMpy 1.0.0, pandas 3.0.5, protobuf,
absl-py, immutabledict, packaging, python-dateutil, six and typing_extensions. JSON is
the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/ortools_cp_sat_python:v1 -c '...'`.

## Traps

- A floating-point objective (any float coefficient in `minimize`/`maximize`) is refused
  before solving with `unsupported_capability` ("Use an integer objective").
- An output leaf `solver.value` cannot evaluate is an `execution_error`: a constraint
  such as `x >= 1`, a float or a float-coefficient expression, a string. Reify into a
  `BoolVar` and output that instead.
- A model CP-SAT validates as `MODEL_INVALID` is reported as `execution_error`
  ("Invalid CP-SAT model").
- Every variable created with `new_int_var`/`new_bool_var` is in the model, so an output
  that appears in no constraint is enumerated over its whole domain: give every output a
  domain that matches the problem.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install ortools`):
#   python knapsack.py knapsack.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = cp_model.CpModel()

    # x[i] is true when the hiker packs item i
    x = [model.new_bool_var(f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.add(sum(w * xi for w, xi in zip(weights, x)) <= capacity)
    # Pack the most valuable selection.
    model.maximize(sum(v * xi for v, xi in zip(values, x)))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with OR-Tools
alone. Nothing else goes in either: the header is the first lines of the file, the run block
the last, and the model sits between them. The runner loads the file as module `candidate`,
so the block never runs during evaluation.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install ortools`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
```
