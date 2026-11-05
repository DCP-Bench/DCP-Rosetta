# pulp_cbc: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how PuLP with
CBC expresses it. Runner: [run.py](run.py), which imports `emit` and `finish` from
[runner/runtime.py](../../../runner/runtime.py) but has its own loader, solve and
enumeration loop.

## Submission file

One Python file, `model.py`. It may import `pulp` and the standard library; nothing else
is installed (no NumPy), and no other file of yours is staged. The standalone run block
imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[pulp.LpProblem, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return exactly a 2-tuple `(problem, outputs)` with `problem` a `pulp.LpProblem`; a
third element is rejected. Anything the module prints goes to stderr. Models retained
before 2026-11-02 name it `build(instance)`, which the runner still accepts; write
`create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to an `LpVariable`, an
`LpAffineExpression`, a Python integer or Boolean, or a nested list/tuple of these with
the declared shape. The runner reads `pulp.value(leaf)`, rounds it, and rejects a value
more than 1e-6 from an integer; values come back as integers (`0`/`1` for a `Binary`).

## Objective

On the problem itself: the direction is the `sense` given to `LpProblem(name,
pulp.LpMinimize | pulp.LpMaximize)`, the objective is a bare expression added with
`problem += expr`. A problem whose `objective` stays `None` is a satisfaction problem,
whatever its sense. The runner accepts a solve only when CBC's `sol_status` is
`LpSolutionOptimal`, then pins the objective to within 1e-6 of that value before
enumerating.

The objective reported with each solution is `pulp.value(problem.objective)` on that
solution: PuLP evaluates the expression itself, constant included, in the problem's sense.
CBC's own value is not used for it: CBC only minimises, so a maximisation shows the negated
value, and PuLP keeps the objective's constant to itself. The incumbents read from CBC's log
are converted for both: `(-V if maximising else V) + constant`.

## Solving

- Each solve is `PULP_CBC_CMD(msg=0, threads=1, timeLimit=max(1, int(seconds left)))`:
  one thread, a whole-second limit of at least 1 s; no gap or presolve option is set.
- Incumbents: the first solve of an optimisation adds `logPath=<file>`, so CBC's log goes
  to a file instead of `/dev/null` (same command line), with CBC's stdout line-buffered
  (`LD_PRELOAD` of coreutils' `libstdbuf.so`, `_STDBUF_O=L`). A thread follows the file
  and reports each `Cbc0004I`/`Cbc0012I`/`Cbc0016I Integer solution of V found` that
  improves on the last as an `incumbent`, objective `(-V if maximising else V) + the
  objective's constant` (CBC minimises internally and never sees PuLP's constant),
  seconds from the call to `solve`. When CBC logs none (its preprocessing solved the
  model) or not the optimum, the proven optimum is reported when the solve returns.
- Status: `Infeasible` gives `unsat` on the first solve and `complete` after;
  `Unbounded` on the first solve gives `error` (see Traps). Otherwise a solve counts only
  when `sol_status` is `LpSolutionOptimal`: CBC reports `Optimal` even when it stopped on
  its time limit, and `sol_status` then reads `LpSolutionIntegerFeasible`, which gives
  `timeout` ("Candidate optimum was not proven" when there is an objective).
- Enumeration (solution limit above 1): every variable under a declared output, those
  inside an output expression included, must be `Integer`/`Binary` with finite bounds,
  else `unsupported`. The objective is held within 1e-6 of the optimum.
- Next solution: a big-M no-good cut over those variables, with binaries
  `_below_<k>_<i>` and `_above_<k>_<i>`, then a fresh CBC solve. A solution whose declared
  values repeat an earlier one (the cut moved only a variable inside an expression) is
  skipped. Exhausted when the cut problem is `Infeasible`, or every such variable is
  already fixed by its bounds.
- Time: the budget runs from the start of the run (`create_model` included). A `SIGALRM` at
  `execution_timeout + 5` s becomes `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/pulp_cbc:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, PuLP 3.3.2 and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). CBC 2.10.3 is the binary the wheel
ships, at `/usr/local/lib/python3.12/site-packages/pulp/solverdir/cbc/linux/i64/cbc`;
`PULP_CBC_CMD` is the only solver PuLP finds. The pin must stay below PuLP 4, which
removes both the bundled CBC and `PULP_CBC_CMD` that the runner calls. JSON is the
standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/pulp_cbc:v1 -c '...'`.

## Traps

- Enumeration (more than one solution requested) needs every variable inside a declared
  output, including those inside an output expression, to be `Integer`/`Binary` and to
  have finite lower and upper bounds; otherwise the run is `unsupported_capability`.
- An output variable in no constraint is added through its bound; with no bound at all
  the run is an `execution_error`.
- An unbounded objective is an `execution_error` ("The objective is unbounded").
- A fractional output value (more than 1e-6 from an integer) raises in the runner and is
  reported as `execution_error`.
- The runner's no-good cuts add binaries named `_below_<i>_<j>` and `_above_<i>_<j>`; do
  not use those names.
- `import numpy` fails in this image (`execution_error`).

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a PuLP (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python knapsack.py knapsack.json

import pulp


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    problem = pulp.LpProblem("knapsack", pulp.LpMaximize)

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    problem += pulp.lpSum(w * xi for w, xi in zip(weights, x)) <= capacity

    # Pack the most valuable selection.
    problem += pulp.lpSum(v * xi for v, xi in zip(values, x))

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with PuLP and
numpy. Nothing else goes in either: the header is the first lines of the file, the run block
the last, and the model sits between them. The runner loads the file as module `candidate`,
so the block never runs during evaluation.

The run block solves once with the bundled CBC and prints each output rounded to an
integer, read with `pulp.value` through `numpy.vectorize`. It checks `problem.status`,
which is enough without a time limit; the runner, which sets one, checks `sol_status`.
`numpy.vectorize` turns a bare integer, or a list holding only integers, into numpy
integers that `pulp.value` does not accept, so give a fixed output as a variable or keep
it in a list with variables.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pulp numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
```
