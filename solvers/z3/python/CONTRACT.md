# z3_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Z3 (Python)
expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`, `flatten` and
`mapped` from [runner/runtime.py](../../../runner/runtime.py) but has its own loader, solve
and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `z3` and the standard library; nothing else is
installed (no NumPy), and no other file of yours is staged. The standalone run block
imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[z3.Solver | z3.Optimize, dict]:
```

It must return a 2-tuple `(solver, outputs)`: a `z3.Solver` for a satisfaction problem, or a
`z3.Optimize` with one objective for an optimisation problem (see [Objective](#objective)).
Add the constraints with `solver.add(...)`. The runner imports the file as module
`candidate` and calls `create_model(instance)` once. Anything the module prints goes to
stderr.

Models retained before 2026-10-30 name it `build(instance)` and return
`(constraints, outputs)` or `(constraints, outputs, (direction, objective))`, with
`constraints` a `z3.Solver`, a `z3.Optimize`, a list/tuple of Boolean expressions or a single
one, and `direction` "minimize" or "maximize". The runner still accepts those forms; write
`create_model` and the form above.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a Z3 `Int`- or
`Bool`-sorted expression, or a nested list/tuple of these with the declared shape. The
standalone run reads each leaf with `model.eval`, which fails on a plain Python integer or
Boolean, so give a fixed value as `z3.IntVal(...)` or `z3.BoolVal(...)` (the runner itself
also accepts the plain value). The runner evaluates each expression with
`model.eval(e, model_completion=True)`: a Boolean comes back as `true`/`false`, an integer
as its `as_long()`; any other sort (a `Real`, a bit-vector) is rejected.

## Objective

Set on the returned `z3.Optimize` with `solver.minimize(expr)` or `solver.maximize(expr)`,
with `expr` an `Int`-sorted Z3 expression; exactly one objective, or the run is an
`execution_error`. The runner reads it back with `objectives()`. Z3 stores a maximised
term negated, as `-(expr)`; when the term is a negation and the solver's SMT-LIB text says
`maximize`, the runner maximises `expr` itself, so that the objective values it reports
(incumbents included) are the model's own and not their negation. It builds its own
`z3.Optimize` over the assertions, requires the proven lower and upper bound to be the same
finite integer, then adds `objective == best` before enumerating. A `z3.Solver`, or a
`z3.Optimize` with no objective, means satisfaction.

The objective reported with each solution is the model's objective (`expr`, unnegated)
evaluated on that solution's model; the incumbents are the values of `expr` on each
improving model z3's `on_model` callback hands over, and last the proven optimum if it did not.

## Solving

- The only parameter set is Z3's `timeout`, in milliseconds, on each `check()`: what is
  left of `execution_timeout`, measured from the start of the run (including `create_model`).
- Optimisation: `check()` on the runner's `z3.Optimize`. `unsat` gives `unsat`; `unknown`,
  or `sat` with lower and upper bound apart, gives `timeout`. Each strictly better model
  Z3 hands to `set_on_model` during that `check()` is reported as an `incumbent` record,
  `seconds` from right after `build`.
- Enumeration: a plain `z3.Solver` over the constraints (plus `objective == best`).
  `sat` reports a solution; `unsat` gives `unsat` on the first check and `complete`
  after; `unknown` gives `timeout`.
- Next solution: `Or(leaf != value)` over every declared output leaf that is not a Python
  constant, with values read under `model_completion=True`. With only constant leaves
  the next check is refused outright, so the search is `complete` after one solution.
- Time: a `SIGALRM` at `execution_timeout + 5` s is a backstop that becomes `timeout`;
  Z3's own `timeout` is what stops a search.

## Compilation

None.

## Environment

Image `dcp-eval/z3_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, the `z3-solver` 5.1.0.0 wheel (Z3 core 5.1.0, as
`z3.get_version_string()` reports) and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). JSON is the standard library's `json`.
No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/z3_python:v1 -c '...'`.

## Traps

- `import numpy` fails in this image (`execution_error`), except inside the standalone run
  block, which the runner never executes; build nested structure with lists.
- A `z3.Optimize` with two or more objectives is rejected (`execution_error`); so is one
  where `add_soft` added a soft constraint, which Z3 also counts as an objective.
- An objective with no finite bound, or a `Real`-sorted one, is reported as
  `execution_error` ("Objective is not a finite integer..."). `z3.Int` is unbounded, so
  add the bounds the problem implies.
- An output of a non-integer, non-Boolean sort raises in the runner and is reported as
  `execution_error`.
- An output in no constraint is accepted (model completion gives it `0` or `false`) and
  is then enumerated over its whole domain, which for a `z3.Int` is unbounded: constrain
  every output to the domain the problem implies.

## Example

A complete submission, with the standalone run below:

```python
# covering_opl: a Z3 (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python covering_opl.py covering_opl.json

import z3


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    nb_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]              # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]    # qualified[t]: the workers who can perform task t, numbered from 1

    solver = z3.Optimize()

    # hired[i] is true when worker i is hired
    hired = [z3.Bool(f"hired_{i}") for i in range(nb_workers)]
    # total_cost is the hiring cost of all hired workers
    total_cost = z3.Int("total_cost")
    solver.add(total_cost == z3.Sum([z3.If(h, c, 0) for c, h in zip(cost, hired)]))

    # Every task is performed by at least one hired worker who is qualified for it.
    solver.add([z3.Or([hired[worker - 1] for worker in task_workers]) for task_workers in qualified])

    # Hire at the lowest total cost.
    solver.minimize(total_cost)

    return solver, {"total_cost": total_cost, "workers": hired}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
```

## Standalone run

Every model carries the header and the run block of the example, with `covering_opl`
replaced by the problem id, so a reader can copy it from the catalogue and run it with Z3
and numpy. Nothing else goes in either: the header is the first lines of the file, the run
block the last, and the model sits between them. The runner loads the file as module
`candidate`, so the block never runs during evaluation.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install z3-solver numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
```
