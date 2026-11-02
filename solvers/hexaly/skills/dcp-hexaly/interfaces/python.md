# Hexaly in Python (hexaly)

The `hexaly` wheel is Hexaly's native Python API over the optimizer library. What holds in
every interface (statuses, gap limit, threads, infeasibility, enumeration strategy) is in
[SKILL.md](../SKILL.md).

## Install

```bash
pip install hexaly
python -c "import hexaly.optimizer as hx; print(hx.HxVersion.get_major_version_number(), hx.HxVersion.get_minor_version_number())"   # 15 0 when tested
```

Creating an optimizer needs a licence file, `license.dat`. Hexaly looks for it in this
order: the file named by `HX_LICENSE_PATH` (the file itself, not its folder), the working
directory, then `/opt/hexaly_15_0/license.dat` (Linux, macOS) or `C:\hexaly_15_0\license.dat`
(Windows); the folder name follows the major and minor version. From Python,
`hx.HxVersion.set_license_path(path)` or `hx.HxVersion.set_license_content(text)` before the
first optimizer does the same. Without a licence the first `HexalyOptimizer()` raises
`HxError: ... Cannot open file [/opt/hexaly_15_0/license.dat]`. Trial and academic licences
are free after [registration](https://www.hexaly.com/registration) and exclude commercial use.
Details: [PyPI](https://pypi.org/project/hexaly/), [installation](https://www.hexaly.com/docs/last/installation/index.html).

## Quick start

```python
import hexaly.optimizer as hx

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0      # the log is printed to stdout otherwise
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)   # OPTIMAL means proven exactly
    optimizer.param.time_limit = 10    # whole seconds
    model = optimizer.model
    x = model.int(0, 10)
    y = model.int(0, 10)
    model.constraint(x + y == 7)
    model.constraint(x - y >= 1)
    model.maximize(x * y)
    model.close()
    optimizer.solve()

    solution = optimizer.solution
    if solution.status in (hx.HxSolutionStatus.OPTIMAL, hx.HxSolutionStatus.FEASIBLE):
        print(solution.status.name, x.value, y.value)   # OPTIMAL 4 3
    else:
        print(solution.status.name)
```

## Modelling

API reference: [HxModel](https://www.hexaly.com/docs/last/pythonapi/optimizer/hxmodel.html),
[HxExpression](https://www.hexaly.com/docs/last/pythonapi/optimizer/hxexpression.html).
Every decision and expression is an `HxExpression` owned by `optimizer.model`.

| Need | API |
|---|---|
| Boolean, integer, float decision | `model.bool()`, `model.int(lo, hi)`, `model.float(lo, hi)` |
| list, set decision | `model.list(n)`, `model.set(n)`; `model.count(l) == n` makes a list a permutation |
| interval decision | `model.interval(lo, hi)`; `model.start(t)`, `model.end(t)`, `model.length(t)`; `a < b` is `end(a) <= start(b)` |
| constraint | `model.constraint(expr)`, `expr` any Boolean expression |
| arithmetic, comparison | `+ - * / // % == != < <= > >=` on expressions; `model.abs`, `model.min`, `model.max`, `model.sum`, `model.prod` |
| logic | `a & b`, `a \| b`, `model.and_(...)`, `model.or_(...)`, `model.not_(a)`, `model.xor(...)` |
| if-then-else | `model.iif(cond, a, b)` |
| element: array indexed by a decision | `arr = model.array(data)` then `arr[i]` or `model.at(arr, i)`; 2D: `model.at(arr, i, j)` |
| all different | pairwise `!=`, or `model.count(model.distinct(model.array(xs))) == len(xs)` |
| set membership, size | `model.contains(s, v)`, `model.count(s)` |
| sets that split, avoid or cover `0..n-1` | `model.partition(a, b, c)`, `model.disjoint(a, b)`, `model.cover(a, b, c)` |
| a violation to minimise | `model.not_(c)` for a Boolean condition, `model.max(0, a - b)` for `a <= b`, `model.abs(a - b)` for `a == b` |
| a constraint over a range | `model.and_(model.range(0, n), model.lambda_function(lambda i: ...))` |
| objective | `model.minimize(expr)`, `model.maximize(expr)`; several are lexicographic |
| feasibility only | `model.minimize(0)` (an objective is required) |
| read data from a file | `json.load` (standard library); see [json-data](../assets/python/json-data/README.md) |

`sum(xs)` (Python's) and `model.sum(xs)` both work; `model.sum` takes a list, a generator or
several arguments, and an empty list or generator sums to 0. `model.and_` over an empty `model.range(0, 0)`
is true. Wrap a Python list in `model.array(...)` to index it with a decision and to pass it
to `model.distinct`, which rejects a plain list with a `TypeError`.

What raises, in this exact form (hexaly 15.0):

| Code | Error |
|---|---|
| `if x > 1:`, `min(x, y)`, an expression as a dict key | `TypeError: Cannot transform an HxExpression to a Python boolean ...`; use `model.iif`, `model.min`, `model.max` |
| `model.constraint(0 <= r < b)` | the same `TypeError`: Python evaluates a chained comparison with `and`; post `r >= 0` and `r < b` as two constraints |
| `model.int(5, 1)` | `HxError: ... Int boundaries are inconsistent (5 > 1).` |
| `model.close()` with no objective | `HxError: ... At least one objective is required in the model.` |
| `optimizer.solve()` before `model.close()` | `HxError: ... This method is only allowed in state Stopped ...` |
| adding a constraint after `close()` | `HxError: ... This method is only allowed in state Modeling (the model must not be closed).`; call `model.open()` first |
| `[5, 6, 7][i]`, `i` a decision | `TypeError: list indices must be integers or slices, not HxExpression`; use `model.array([5, 6, 7])[i]` |
| `optimizer.param.time_limit = 2.5` | `ArgumentError: ... 'float' object cannot be interpreted as an integer` |

## Solving

[HxSolution](https://www.hexaly.com/docs/last/pythonapi/optimizer/hxsolution.html),
[HxParam](https://www.hexaly.com/docs/last/pythonapi/optimizer/hxparam.html).

| `optimizer.solution.status` | Meaning |
|---|---|
| `hx.HxSolutionStatus.OPTIMAL` | bound reached within the gap limit |
| `hx.HxSolutionStatus.FEASIBLE` | solution found, optimality not proven |
| `hx.HxSolutionStatus.INFEASIBLE` | nothing found; no proof |
| `hx.HxSolutionStatus.INCONSISTENT` | proven: no solution |

Read values after `solve()` with `.value`: an `int` for Boolean and integer expressions, a
`float` for floats, `/` and `**`. A list or set decision gives an `HxCollection` (`list(l.value)`),
an array an `HxArray` (`list(a.value)`), an interval an `HxInterval` (`t.value.start()`,
`t.value.end()`). `solution.get_objective_bound(0)` is the proven bound of the first objective.

| Parameter | Use |
|---|---|
| `param.time_limit` | whole seconds; the default is effectively no limit |
| `param.nb_threads` | 4 or more for proofs (0, the default, picks at least 4) |
| `param.set_gap_limit(0)` | exact optimality; the default is 1e-4 |
| `param.seed` | reproducible runs |
| `param.verbosity` | 0 silences the log, which goes to `sys.stdout` as it was when the optimizer was created |

Parameters may be set again between solves, so a loop can give each `solve()` the time
left from an overall deadline: `optimizer.param.time_limit = max(1, int(deadline - time.monotonic()))`.

Errors from the library are `hx.HxError` exceptions with the message above; solver outcomes
are statuses, never exceptions. Using `with hx.HexalyOptimizer() as optimizer:` frees the
optimizer at the end of the block. One program may create several optimizers one after
another: the [infeasible](../assets/python/infeasible/README.md) example solves a model with
hard constraints and then a violation-minimising one.

## All solutions

Strategy: [SKILL.md](../SKILL.md#all-solutions). The loop, with `xs` the decisions that
identify a solution (the fewer, the faster the final proof):

```python
S = hx.HxSolutionStatus
repeats, solutions, complete = [], [], False
model.minimize(0)
model.close()
while True:
    optimizer.solve()
    status = optimizer.solution.status
    if status == S.INCONSISTENT:
        complete = True
        break
    if status not in (S.FEASIBLE, S.OPTIMAL):
        break                                    # time limit: no proof either way
    if model.get_objective(0).value >= 1:
        complete = status == S.OPTIMAL           # proven: every solution repeats a found one
        break
    values = [x.value for x in xs]
    solutions.append(values)
    model.open()
    model.remove_objective(0)
    repeats.append(model.and_(*[x == v for x, v in zip(xs, values)]))
    model.minimize(model.sum(repeats))
    model.close()
```

When every solution has the same number of true Booleans, `model.and_(*[x for x, v in
zip(xs, values) if v])` is a shorter no-good (see SKILL.md for when it is wrong). When the
problem may have no solution, first solve its violation model once and run the loop only if
the minimum is 0. For all optimal solutions, first solve with the real objective, then
`model.open()`, `model.remove_objective(0)`, `model.constraint(objective_expr == best)` and
run the loop.
Runnable: [all-solutions](../assets/python/all-solutions/README.md),
[all-optimal](../assets/python/all-optimal/README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Property 'LICENSE_KEY' is missing` | `HX_LICENSE_PATH` names a folder | point it at the file |
| log lines mixed into your output | default `verbosity` 1 writes to stdout | `optimizer.param.verbosity = 0` |
| `TypeError: Cannot transform an HxExpression to a Python boolean` | Python `if`, `and`, `min`, `max` on expressions | `model.iif`, `model.and_`, `model.min`, `model.max` |
| a float where an integer was expected | `/` or `**` | `//` or `x * x`, or keep the expression integer |
| `HxError ... only allowed in state Modeling` | changing a closed model | `model.open()`, change, `model.close()` |

## Runnable examples

- [satisfy](../assets/python/satisfy/README.md): Latin square, all-different with `distinct`, constant objective
- [maximise](../assets/python/maximise/README.md): integer production plan, objective bound
- [minimise](../assets/python/minimise/README.md): Boolean assignment proven optimal
- [infeasible](../assets/python/infeasible/README.md): proving infeasibility by minimising violations
- [all-solutions](../assets/python/all-solutions/README.md): soft no-goods with a proof of completeness
- [all-optimal](../assets/python/all-optimal/README.md): pin the optimum, then enumerate
- [scheduling](../assets/python/scheduling/README.md): job shop with intervals and one list per machine
- [json-data](../assets/python/json-data/README.md): reading a JSON file with ragged lists
