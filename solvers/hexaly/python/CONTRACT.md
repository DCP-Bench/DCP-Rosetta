# hexaly_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Hexaly
(Python, `hexaly`) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `hexaly` and the standard library; nothing else
is installed, and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[hexaly.optimizer.HexalyOptimizer, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
(not a list) `(optimizer, outputs)`, with `optimizer` the `HexalyOptimizer` whose
`optimizer.model` holds the model. Create it as `optimizer = hx.HexalyOptimizer()`, not in
a `with` block: leaving the block deletes the optimizer before the runner can solve, which
fails with `Hexaly error: ERROR [function check]: Cannot call this method on an object that
is no longer valid.` (`execution_error`). Leave
the model open or close it; do not call `optimizer.solve()`. Anything the module prints
goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. To index data by a decision, wrap it: `model.array(data)[i]` or
`model.at(model.array(data), i, j)`; a Python list indexed by an expression raises
`TypeError`.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to one of:

- a Boolean or integer `HxExpression` (a decision or any integer-valued expression),
  reported as its integer value (Booleans as `0`/`1`);
- a list decision (`model.list(n)`), reported as the list of its elements in order;
- an array expression (`model.array(...)` of integer expressions, nested arrays
  included), reported as nested lists;
- a Python `int` or `bool`, or a nested `list`/`tuple` of any of these.

Refused with `execution_error` and a message naming the fix: a float expression (from
`/`, `**`, a float decision), a set, an interval (declare `model.start(t)` or
`model.end(t)`), and an expression undefined in the solution. Integers are 64-bit, so
values beyond 32 bits are carried as they are.

## Objective

`model.minimize(expr)` or `model.maximize(expr)`, with `expr` an integer expression. No
objective, or one constant objective, is a satisfaction problem (the runner adds
`minimize(0)`, which Hexaly needs to close a model). More than one objective (Hexaly's
lexicographic objectives) is `unsupported`; a float objective is `execution_error`.

## Solving

- Forced over the submission's own parameters: `verbosity = 0`, `nb_threads = 4` (Hexaly
  proves bounds in threads beside its search; with fewer the proofs stall),
  `set_gap_limit(0)` (the default 1e-4 relative gap reports `OPTIMAL` short of the
  optimum) and `time_limit` = the whole seconds left. Other parameters you set are kept.
- Status: `OPTIMAL` is proven and reported; `INCONSISTENT` is `unsat`; `FEASIBLE` (an
  unproven optimum) and `INFEASIBLE` (nothing found, which Hexaly does not prove) are
  `timeout`. An `HxError` is `error` with Hexaly's message.
- Enumeration re-solves with soft no-goods. After the first proven solve the runner
  reopens the model, removes the objective, pins an optimisation objective with
  `objective == optimum`, and minimises the number of reported solutions the declared
  outputs repeat (one `and` of equalities per solution, over the output expressions
  themselves; a list output compares its count and `index` of each element). Objective 0
  is a new solution; a proven minimum of 1 or more, or `INCONSISTENT`, is `complete`; the
  time limit is `timeout`. Outputs that are all constants are `complete` after one solution.
- Time: the deadline is set before `build` runs, so building spends the budget. Each solve
  gets the whole seconds left; with less than one second left the run is `timeout`. A
  SIGALRM at budget + 5 s turns a hang in Python into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/hexaly_python:v1`: Python 3.12.11 (`/usr/local/bin/python`), hexaly
15.0.20261026 (Hexaly Optimizer 15.0); the standard library (`json` included) and nothing
else. The image holds no licence. The evaluator binds the machine's Hexaly licence file
read-only at `/run/licence/license.dat` and sets `HX_LICENSE_PATH` to it, at run time
(`licence` in `metadata.json`). Without a licence configured, a run stops before the
container starts with `licence_unavailable`; a licence Hexaly refuses (`Cannot open file
[...]`, or an expired licence) is `licence_unavailable` too. The container has no network
and needs none. The runner keeps the protocol on its own copy of file
descriptor 1 and sends fd 1, Hexaly's log and everything the submission prints to stderr.
For an ad hoc run, `--entrypoint sh` bypasses `/opt/runner/run.py`.

## Traps

- Hexaly proves an optimum only through its bounds, and the formulation decides them. On
  a 4x4 assignment, Booleans with linear constraints or integers with pairwise `!=` were
  proven in 0.02 s, while `count(distinct(...)) == n` and a list decision found the
  optimum and stayed unproven (`timeout`). Prefer Booleans, linear sums and pairwise
  constraints for optimisation problems; keep lists and intervals for sequencing.
- A satisfaction problem with no solution is `timeout`, not `unsat`, unless presolve proves
  it (`INCONSISTENT`).
- The profile asks for two distinct solutions, or a proof that there is no second, so a
  problem with one solution needs that proof. Booleans with linear sums give it: a Boolean
  per (cell, value) proved a 12 x 12 hidato unique in 2.5 s and a quotient variable per prefix
  proved the single number divisible by 1 to 9 in 8 s, where a list or a `%` found the
  solution and timed out. Solutions that are isolated points (a season timetable, a
  quasigroup of order 9) end as one solution and `timeout`.
- An output may mix expressions and constants (`[digit_a, 5, digit_b, 0]`); a sum of Booleans
  such as `sum(k * has[p][k] for k in range(n))` is an integer expression and reports as one.
- A model that finds nothing may be unsatisfiable because of a rule the statement does not
  give (a leading zero in a cryptarithm); check a small case in plain Python first.
- Enumeration costs one solve per solution and each solve grows with the number found
  (8-queens, 92 solutions: about 100 s with an integer column per row, 4 to 48 s with a
  Boolean board, depending on the order the constraints are posted). A large
  `solution_limit` on a problem with fewer solutions ends in `timeout` when the last
  proof does not come in time.
- `//` rounds down and `%` keeps the dividend's sign, unlike each other (-7 // 2 = -4,
  -7 % 2 = -1); state the reference's division with explicit decisions when operands can
  be negative.

## Example

The pilot fixture [tests/fixtures/model_hexaly.py](../../../tests/fixtures/model_hexaly.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model
    x = model.int(0, n)
    y = model.int(0, n)
    if instance["optimize"]:
        model.constraint(x + y >= n)
        model.minimize(x + y)
    else:
        model.constraint(x + y == n)
    return optimizer, {"x": x, "y": y}
```
