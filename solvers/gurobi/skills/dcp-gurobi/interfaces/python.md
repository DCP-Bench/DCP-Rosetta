# Gurobi in Python (gurobipy)

gurobipy is Gurobi's Python API: the `gurobipy` wheel bundles the Gurobi Optimizer. What holds in
every interface (concepts, outcomes, parameters, the pool strategy) is in [SKILL.md](../SKILL.md).

Runnable examples: `assets/python/`, one folder per pattern; encodings in [references/python/encodings.md](../references/python/encodings.md).


## Install

```bash
pip install gurobipy numpy scipy
python3 -c "import gurobipy as gp; print(gp.gurobi.version())"   # (13, 0, 3) when tested
```

The wheel bundles a size-limited licence: no key, no network needed, and a banner
`Restricted license - for non-production use only - expires 2027-11-29` is printed to stdout
when the default environment starts, that is at the first `gp.Model(...)`. Setting
`model.Params.OutputFlag = 0` after the model exists does **not** hide it (verified). To silence
the banner, create the environment with the flag: `env = gp.Env(params={"OutputFlag": 0})`, then
`gp.Model("name", env=env)` (verified: no banner, same status). Above the limits it fails with
`Model too large for size-limited license` (see [Common issues](../SKILL.md#common-issues)).
Details: [pip package](https://pypi.org/project/gurobipy/) and
[size-limited licence](https://support.gurobi.com/hc/en-us/articles/360051597492).



## Quick start

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("quick")
x = model.addVar(lb=0, ub=10, vtype=GRB.INTEGER, name="x")
y = model.addVar(lb=0, ub=10, vtype=GRB.INTEGER, name="y")
model.addConstr(x + y >= 7, name="demand")
model.setObjective(3 * x + 2 * y, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Objective:", model.ObjVal)
    print("x =", round(x.X), "y =", round(y.X))
else:
    print("Status:", model.Status)
```

Expected output: `Objective: 14.0`, then `x = 0 y = 7`.



## Modelling

Full reference: [Python API](https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html)
([Model](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html),
[global functions](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_global.html),
[general constraint helpers](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_utility.html)).

| Need | API |
|---|---|
| one variable | [`addVar`](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html): `model.addVar(lb=0, ub=u, vtype=GRB.INTEGER, name="x")` |
| many variables | `model.addVars(n, m, ...)`, indexed `x[i, j]`; `lb` defaults to **0** |
| variables with string keys | `model.addVars(["a", "b", "c"], vtype=GRB.BINARY)`, indexed `x["a"]`; a list of strings is used as the keys directly |
| variables with mixed keys | `model.addVars([("a", 1), ("b", 2)], ...)` or `model.addVars(["r", "s"], [1, 2, 3], ...)` (tuple keys `x["r", 2]`); the keys are the tuples you pass |
| sum over one index | `x.sum(i, "*")` or `x.sum("*", j)` on a tupledict: `*` is a wildcard over that position (verified on string and integer keys); `x.sum()` sums all |
| matrix of variables | `model.addMVar((n, m), vtype=GRB.BINARY)`; `sum` and `@` need SciPy |
| a sum | [`gp.quicksum(...)`](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_global.html), faster than `sum()` on many terms |
| a constraint | `model.addConstr(expr <= rhs, name=...)`; also `>=`, `==`; `model.addConstrs(... for ...)` |
| conditional constraint | `model.addConstr((b == 1) >> (x + y <= 3))`, `b` binary: an [indicator](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html) |
| `y = abs(x)` | `model.addConstr(y == gp.abs_(v))`, where `v` is a **variable** |
| `y = max(...)`, `min(...)` | `gp.max_([a, b], constant=0)`, `gp.min_(a, b)`; variables only |
| `z = a and b`, `z = a or b` | `model.addConstr(z == gp.and_(a, b))`, `gp.or_`; binaries only |
| objective | `model.setObjective(expr, GRB.MINIMIZE)` or `GRB.MAXIMIZE`; none means satisfaction |
| negative or free domain | `lb=-5` explicitly, or `lb=-GRB.INFINITY` |
| read a result | `x.X` (value), `model.ObjVal`, `model.Status` |

Encodings for `!=`, all-different, element, disjunctions, products and `//`, `%`:
[references/encodings.md](../references/python/encodings.md).

What raises, in this exact form (gurobipy 13.0.3):

| Code | Error |
|---|---|
| `model.addConstr(x != y)` | `GurobiError: Inequality constraints not supported` |
| `x // 2`, `x % 2` | `TypeError: unsupported operand type(s) for //` |
| `if x == 1:`, `bool(x <= y)` | `GurobiError: Constraint has no bool value`; branch on data, not decisions |
| `gp.abs_(a - b)` | `TypeError: ... is not a variable`; create an auxiliary variable first |
| `x` from model A used in model B | error; each variable belongs to one `Model` |




## Solving

Status codes: [status reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html).
Parameters: [parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html).

| `model.Status` | Value | Meaning |
|---|---|---|
| `GRB.OPTIMAL` | 2 | optimal (within `MIPGap`); `ObjVal` and `X` are valid |
| `GRB.INFEASIBLE` | 3 | proven to have no solution; use `computeIIS()` to see why |
| `GRB.INF_OR_UNBD` | 4 | infeasible or unbounded; set `DualReductions = 0` and re-solve to tell |
| `GRB.UNBOUNDED` | 5 | objective unbounded; says nothing about feasibility |
| `GRB.TIME_LIMIT` | 9 | stopped at `TimeLimit`; a solution exists only if `model.SolCount > 0` |
| `GRB.SUBOPTIMAL` | 13 | tolerances not met; a suboptimal solution is available |

Errors: Python exceptions (`GurobiError`, `TypeError`) show in the traceback on stderr. A
solver problem is a status, not an exception: always test `model.Status` before reading `.X`.
Log lines go to stdout unless `OutputFlag = 0`.

Read integer variables with `round(x.X)`: values come back within `IntFeasTol` (1e-5) of an integer.


## All solutions

Strategy and settings: [SKILL.md](../SKILL.md#all-solutions).
Read each pool solution with `SolutionNumber` (set `model.Params.SolutionNumber = k`) and `Xn`
(the value in that solution; `X` is the current one). Count with `model.SolCount`.

Solving examples: [satisfy](../assets/python/satisfy/README.md), [maximise](../assets/python/maximise/README.md), [minimise](../assets/python/minimise/README.md),
[infeasible](../assets/python/infeasible/README.md), [scheduling](../assets/python/scheduling/README.md).

| You want | Example |
|---|---|
| every feasible solution (`setObjective(0)` or no objective) | [all-solutions](../assets/python/all-solutions/README.md) |
| every optimal solution | [all-optimal](../assets/python/all-optimal/README.md) |


## Readable models

Write for a student reading the model for the first time, in the words of the problem
statement, not of the API:

- a docstring that states the problem in a sentence or two;
- a comment on each input field, saying what it holds (`weights[i]: the weight of item i`);
- a comment on each decision variable, saying what it means (`x[i] is 1 when item i is packed`);
- a comment on each group of constraints and on the objective, and on a problem constant
  where it appears (`# fixed by the rules of Sudoku`);
- the plainest expression that says it: `gp.quicksum(w * xi for w, xi in zip(weights, x)) <= capacity`,
  and `holds.sum(r, c, "*")` for a sum over one index of a `tupledict` (say in a comment what
  the `"*"` adds up);
- one `model.addConstrs(... for ...)` with a generator (and `if j > i` for pairs) where a loop
  only adds one row per item; a loop stays where each group has its own clue or bound;
- a domain or bound that the statement does not give (an upper bound taken from the data or
  chosen to keep a variable finite) with a comment that says so;
- decisions kept as lists or nested lists so they print as a whole; a `tupledict` from
  `addVars` is a dict, so list its entries (`[[x[i, j] for j in cols] for i in rows]`).

An output may be a variable, a linear expression over variables or a number, and the same
`gp.LinExpr(out).getValue()` reads each. So a digit chosen through one-hot binaries can be
returned as `gp.quicksum(d * holds[r, c, d] for d in digits)`, with no integer variable and
no linking constraint added only to read it.

Build the model in one function that creates the `Model`, adds the constraints, sets the
objective when there is one, and returns the model with the variables to print:

```python
def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = gp.Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = [model.addVar(vtype=GRB.BINARY, name=f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.addConstr(gp.quicksum(w * xi for w, xi in zip(weights, x)) <= capacity)

    # Pack the most valuable selection.
    model.setObjective(gp.quicksum(v * xi for v, xi in zip(values, x)), GRB.MAXIMIZE)

    return model, {"x": x}
```

Solve with `model.Params.OutputFlag = 0` and `model.Params.MIPGap = 0` (the default gap stops
within 0.01% of the optimum), call `model.optimize()`, test `model.Status == GRB.OPTIMAL`, and
print `round(model.ObjVal)` and each output as `round(gp.LinExpr(out).getValue())`;
`numpy.vectorize` applies it to a nested list in one call. A status of 3 is infeasible, and 4
means presolve could not tell infeasible from unbounded. The licence that comes with
`pip install gurobipy` handles up to 2000 variables and 2000 linear constraints.

### Generators and `tupledict` traps

- The loop variables of an `addConstrs` generator become `tupledict` keys, so they must be
  indices (`int`, `str`, `tuple`). Looping over variables fails with `Variable has not yet been
  added to the model`, and over lists with `unhashable type: 'list'`: loop over indices and index
  the data inside the expression. Indicator constraints `(b[i] == 1) >> (...)` work in
  `addConstrs` over indices.
- `tupledict.sum` takes one argument per key position: `holds.sum(r, c, "*")` for keys
  `(r, c, d)`. A tuple passed as one argument (`sum((i, k), "*")`), or keys that contain tuples,
  silently match nothing and leave the model infeasible with no error: flatten the keys to ints,
  and look at `model.write("model.lp")` when a model is unexpectedly infeasible.
- `gp.quicksum` over a `tupledict` adds its keys, not its values: use `td.sum()` or
  `list(td.values())`.
- `addVars` takes a list or a dict for `lb` and `ub` (one per index), so per-index bounds need no
  loop afterwards.
- Regrouping constraint rows changes their order, and under one thread that alone can make a
  hard model ten times slower: keep the order when reshaping loops of a model that is hard to
  solve, and time it with `Threads = 1`.
- A bound the statement does not give needs a comment saying so and, when it has one, why it
  cannot cut off the optimum (an implied bound, a triangle inequality), not only that it comes
  from the data. State in a comment where the statement leaves a boundary open.
- An integer output that is a linear function of many binaries should be its own bounded
  integer variable with an equality link: enumeration of further solutions then moves over
  distinct output values, and stays small, instead of adding indicator constraints per binary.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
|---|---|---|
| `Inequality constraints not supported` | `addConstr(a != b)` | use the `!=` encoding in [encodings.md](../references/python/encodings.md) |
| `Constraint has no bool value` | Python `if` or `bool()` on an expression | Branch on data; express the choice with an indicator |
| `is not a variable` from `abs_`, `max_` | argument is an expression | introduce a variable equal to it, then apply the helper |
| `No module named 'scipy'` | `MVar.sum` or `@` used without SciPy | `pip install scipy` |
| licence banner still printed after `model.Params.OutputFlag = 0` | the flag was set after the environment started | `env = gp.Env(params={"OutputFlag": 0})` and `gp.Model(..., env=env)` |
| `KeyError` on `x["a"]` or `x[i, j]` | keys are not the ones you think: `addVars(n)` gives `0..n-1`, string lists give the strings, tuples stay tuples | print `list(x.keys())[:5]` and index with exactly those keys |
| `2.9999999` instead of `3` | integrality tolerance | `round(x.X)` |
| `GurobiError` about a variable from another model | variable reused across `Model`s | create variables in the model that uses them |

More in [SKILL.md](../SKILL.md#common-issues).
