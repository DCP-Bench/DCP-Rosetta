# cvc5_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how cvc5 (Python)
expresses it. cvc5 has no optimiser, so this integration is satisfaction-only: it is given
no problem with an objective (`optimization` is false in [metadata.json](metadata.json), and
those problems are listed in `generation/blockers.json`). Runner: [run.py](run.py), which imports `emit`, `finish`, `flatten` and
`mapped` from [runner/runtime.py](../../../runner/runtime.py) and has its own loader, solve
and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `cvc5.pythonic` (and `cvc5` itself) and the
standard library; nothing else is installed (no NumPy), and no other file of yours is
staged. The standalone run block imports `numpy`, which is fine: the runner never executes
it.

## Entrypoint

```python
def create_model(instance) -> tuple[cvc5.pythonic.Solver, dict]:
```

It must return a pair `(solver, outputs)`: `solver` a `cvc5.pythonic.Solver` with the
constraints added by `solver.add(...)`. From the Solver the runner takes its assertions, its
logic and the options set on it (see [Solving](#solving)). The runner imports the file as
module `candidate` and calls `create_model(instance)` once. Anything the module prints goes
to stderr. A third element, such as an objective, is an `error`.

Models retained before 2026-10-30 name it `build(instance)` and return
`(constraints, outputs)`, with `constraints` a `cvc5.pythonic.Solver`, a list or tuple of
Boolean expressions, or a single one. The runner still accepts that form; write
`create_model` and the form above.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to an Int- or
Bool-sorted pythonic expression, or a nested list/tuple of these with the declared shape.
The standalone run reads each leaf with `model.eval`, which fails on a plain Python integer
or Boolean, so give a fixed value as `c5.IntVal(...)` or `c5.BoolVal(...)` (the runner
itself also accepts the plain value and passes it through unchanged). After the solver finds
a model, each leaf is read with `model.eval(e)`: a Boolean comes back
as `true`/`false`, an integer as its `as_long()`. Any other sort (a `Real`, a string) raises
and is reported as `execution_error`.

## Objective

None. cvc5 has no optimiser, so this integration declares no objective: a satisfaction
problem declares none, and an optimisation problem is out of scope.

## Solving

- Solvers: the runner never checks the Solver `create_model` returns. It solves on fresh pythonic
  Solvers that carry the returned Solver's assertions, its logic (set when the native
  solver has one, `isLogicSet()`, as `SolverFor(logic)` and `solver.setLogic(...)` do)
  and every option whose `getOptionInfo(name)["setByUser"]` is true, copied with
  `set(name, getOption(name))`. The runner owns `tlimit-per`, `tlimit`, `incremental` and
  `produce-models`: values a model sets for these are not copied, `incremental` and
  `produce-models` stay on. Constraints given as a list, or a plain `Solver()` with no
  options, are solved on `c5.Solver()` under cvc5's default logic.
- Time: `execution_timeout` is measured from the start of `solve`, including `create_model`. Each
  solver check gets **all the time left** (cvc5 option `tlimit-per`, in ms, set before each
  check); a later check in the enumeration can therefore run out, which gives `timeout`.
- Enumeration: one incremental solver over the constraints. Each model is emitted, then
  `Or(leaf != value)` over every declared output leaf that is not a Python constant is
  asserted, and the solver checks again. `unsat` gives `complete` after at least one
  solution (`unsat` if there was none); `limit` once `solution_limit` is reached.
- `unknown`: cvc5 reason `TIMEOUT` maps to `timeout`. Any other reason (for example
  `INCOMPLETE`, which cvc5 gives for nonlinear arithmetic it cannot decide) maps to `error`
  with `cvc5 returned unknown: <reason>` as the detail.
- Exceptions raised while building or solving map to `error` with the exception's own
  message as the detail. This covers a logic the model does not fit: a product of two
  unknowns under `SolverFor("QF_LIA")` raises at the first check with `A non-linear term
  was asserted to arithmetic in a linear logic.`
- Backstop: a `SIGALRM` at `execution_timeout + 5` s becomes `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/cvc5_python:v1`, built `FROM python:3.12.11-slim-bookworm` (pinned by
digest, as in `solvers/z3_python`). Python 3.12.11 at `/usr/local/bin/python`, the `cvc5`
wheel 1.4.2 from PyPI (`cvc5.__version__` is `1.4.2`), and nothing else besides pip. The
shared `runner/requirements.txt` stack is not installed, so NumPy is not available (the
standalone run block imports it, but the runner never executes that block). The JSON
library is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp`, user 65534, the
submission and `request.json` under `/input`. The image's entrypoint is the runner
(`python /opt/runner/run.py`).

## Traps

- Use `cvc5.pythonic`, not the native `cvc5` API: the runner and the pythonic `Solver` are
  the only interface it supports.
- `set("timeout", ...)` is rejected (`unrecognized option: timeout.`). Use `tlimit-per`.
- A `tlimit-per`, `tlimit`, `incremental` or `produce-models` value set on the returned
  Solver is dropped without a message; the runner sets its own. Other options and the logic
  are kept, so a wrong logic fails the run: `SolverFor("QF_LIA")` with a product of two
  unknowns is `error`, and `SolverFor("QF_UF")` over integers is `error` (`The logic was
  specified as QF_UF, which doesn't include THEORY_ARITH, ...`). An option that limits work,
  such as `rlimit-per`, ends a check with `unknown` / `RESOURCEOUT`, which is `error`.
- Options and the logic must be set before the first `add`: cvc5 refuses both afterwards
  (`invalid call to 'setOption' for option '...', solver is already fully initialized`).
- The global `tlimit` option was not usable in this image: with it set, `check()` did not
  return within the budget in testing. Only `tlimit-per` is used.
- `solver.add` takes Boolean expressions as separate arguments, or one list of them as its
  only argument. A list next to other arguments, a nested list or a generator raises
  `SMTException: True, False or SMT Boolean expression expected`.
- `Sum([...])` over Boolean expressions raises `TypeError: unsupported operand type(s) for
  +: 'BoolRef' and 'BoolRef'`. Wrap each Boolean in `If(b, 1, 0)`.
- Inside arithmetic, a Boolean mixed with an Int is silently taken as 0/1 (`x + b` becomes
  `x + If(b, 1, 0)`); a Boolean compared with an Int is also not an error. Write explicit
  `If` where the meaning matters.
- `Distinct` over Python `int`s (no pythonic expression in the list) raises
  `SMTException: At least one of the arguments must be an SMT expression`.
- A string in an arithmetic position raises `RuntimeError: invalid argument 'abc' for 's',
  expected an integer`. Strings from the instance must be turned into numbers before use.
- Integers are unbounded: constrain every output and every auxiliary variable to the domain
  the problem implies. An output no constraint mentions is enumerated over its whole
  unbounded domain, so enumeration does not stop at `solution_limit` in a useful way.
- Nonlinear integer arithmetic (a product of two unknowns, for example `a * b == 7000021`
  or `c * c * d == 2 * 10**12 + 1`) returned `unknown` after the time limit in testing. It
  is reported as `timeout` or, when cvc5 gives another reason, `error`. Products with a
  constant factor are linear and were solved quickly.
- Quantifiers: not tested by this integration. Treat as unsupported until a readiness
  case covers them.

## Example

A complete submission, with the standalone run below:

```python
# bin_packing: a cvc5 (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python bin_packing.py bin_packing.json

import cvc5.pythonic as c5


def create_model(instance):
    """Assign each item to one of several bins, each of a fixed capacity, so that the total
    weight of the items in each bin does not exceed the capacity."""
    weights = instance["weights"]    # weights[k]: the weight of item k
    capacity = instance["capacity"]  # the most weight one bin can hold
    n_bins = instance["num_bins"]    # the number of bins available

    # bins[k]: the bin that item k goes into
    bins = [c5.Int(f"bin_{k}") for k in range(len(weights))]

    solver = c5.Solver()

    # Each item goes into one of the bins, numbered 0 to n_bins - 1.
    solver.add([c5.And(b >= 0, b <= n_bins - 1) for b in bins])

    # The items in each bin weigh no more than the capacity.
    for b in range(n_bins):
        solver.add(
            c5.Sum([c5.If(bin_k == b, w, 0) for bin_k, w in zip(bins, weights)]) <= capacity
        )

    return solver, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
```

## Standalone run

Every model carries the header and the run block of the example, with `covering_opl`
replaced by the problem id, so a reader can copy it from the catalogue and run it with cvc5
and numpy. Nothing else goes in either: the header is the first lines of the file, the run
block the last, and the model sits between them. The runner loads the file as module
`candidate`, so the block never runs during evaluation.

The run block checks once and prints each output read through `solver.model().eval`, or the
status when there is no solution.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install cvc5 numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
```
