# cpmpy_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how CPMpy
(Python) expresses it. Runner: [run.py](run.py), which calls `main("cpmpy")` in
[runner/runtime.py](../../../runner/runtime.py).

## Submission file

One Python file, `model.py`. It may import `cpmpy`, `numpy` and the standard library;
no other file of yours is staged.

## Entrypoint

```python
def create_model(instance) -> tuple[cp.Model, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return a 2-tuple `(model, outputs)`. Anything the module prints goes to stderr,
not to the result. Models retained before 2026-10-30 name it `build(instance)`, which the
runner still accepts; write `create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Convert to NumPy yourself where that helps (`np.array(...)`).

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a CPMpy variable or
a CPMpy array of variables with the declared shape (`cp.intvar(..., shape=...)`, a slice of
one, or `cp.cpm_array([...])` for an output assembled from a list). The runner also accepts
expressions, constants and plain lists, but the run block's `.value()` fails on a list. The runner reads `.value()` from each leaf; a leaf whose value is not an
integer or Boolean makes the runner raise, which the evaluator reports as
`execution_error`.

## Objective

Set it on the model: `model.minimize(expr)` or `model.maximize(expr)`, with an integer
expression. No objective for a satisfaction problem.

## Solving

- Every solve is `model.solve(solver="ortools", time_limit=<seconds left>,
  num_search_workers=1)`, plus `keep_all_feasible_solutions_in_presolve=True` while the
  model has an objective (the OR-Tools CP-SAT bug https://github.com/google/or-tools/issues/5552;
  the later enumeration solves have none); the submission cannot change these.
- Status: a solution is reported only when CPMpy's exit status is `OPTIMAL` (optimisation)
  or a solution was found (satisfaction). `UNSATISFIABLE` gives `unsat` on the first solve
  and `complete` after; anything else (a time limit, `FEASIBLE` with an objective) gives
  `timeout`.
- Next solution: the objective is pinned (`objective == best`, objective dropped), then
  `any(leaf != value)` over every declared output leaf is added and the model is solved
  again from scratch. The search is exhausted when that solve is `UNSATISFIABLE`.
- Time: each solve gets the seconds left of `execution_timeout`, measured from the start
  of the run (including `build`); a `SIGALRM` at exactly `execution_timeout` covers
  import and `build` too, and turns into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/cpmpy_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, CPMpy 1.0.0 with OR-Tools CP-SAT 9.15.6755 as its solver,
NumPy 2.5.3, all pinned in `runner/requirements.txt`, which also installs pandas 3.0.5,
protobuf, absl-py, immutabledict, packaging, python-dateutil, six and typing_extensions.
JSON is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/cpmpy_python:v1 -c '...'`.

## Traps

- Output variables that appear in no constraint are still registered by the runner, so an
  unconstrained output is enumerated over its whole domain: give every output a domain that
  matches the problem. The standalone run does not register them, and prints `None` for
  such a variable.
- A float anywhere in an expression raises at build time (`TypeError: Multiplication does
  not support float constants`), which surfaces as `execution_error`. Scale to integers.

## Example

A complete submission:

```python
# knapsack: a CPMpy model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python knapsack.py knapsack.json

import cpmpy as cp


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    # x[i] is true when the hiker packs item i
    x = cp.boolvar(shape=len(values), name="x")

    model = cp.Model()
    # The packed items weigh no more than the backpack can carry.
    model.add(cp.sum(x * weights) <= capacity)
    # Pack the most valuable selection.
    model.maximize(cp.sum(x * values))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
```

## Standalone run

Every model starts with the header and ends with the run block of the example, with
`knapsack` replaced by the problem id. The runner loads the file as module `candidate`, so
the block never runs during evaluation.

For a problem whose instance file is `[]`, the header and run block are:

```python
# abbots_puzzle: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install cpmpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
```
