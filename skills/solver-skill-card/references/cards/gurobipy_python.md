# Gurobi (Python, gurobipy) — Python, mixed-integer linear programming (with quadratic and general constraints)

## Minimal working example (knapsack)
```python
import gurobipy as gp
from gurobipy import GRB
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = gp.Model()
x = model.addVars(3, vtype=GRB.BINARY, name="x")
model.addConstr(gp.quicksum(weights[i] * x[i] for i in range(3)) <= capacity)
model.setObjective(gp.quicksum(values[i] * x[i] for i in range(3)), GRB.MAXIMIZE)
model.optimize()
print(round(model.ObjVal), [round(x[i].X) for i in range(3)])
```

## API
- **Decision variables:** `model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name="v")` (`GRB.BINARY`, `GRB.CONTINUOUS`; default `lb=0`, `ub=inf`: give tight bounds, `lb=-GRB.INFINITY` for negatives); `model.addVars(n, m, vtype=..., lb=..., ub=...)` returns a dict indexed `x[i, j]`; `x.sum(i, "*")` and `x.sum("*", j)` sum a slice
- **Logic constraints:** `model.addConstr((b == 1) >> (e <= k))` (b ⇒ constraint; b binary); `model.addGenConstrIndicator(b, False, e <= k)` (b = 0 ⇒); `model.addConstr(r == gp.and_(a, b))`; `gp.or_(a, b)` (r ⇔ ∧ / ∨ of binaries)
- **Arithmetic constraints:** `model.addConstr(e <= k)` with `<=`, `>=`, `==` only (`<` raises `TypeError`, `!=` raises `GurobiError`: use `<= k - 1`); `model.addConstrs((e(i) <= k for i in I), name="c")`; `gp.quicksum(...)`; `gp.LinExpr()` with `e += c * v`; `x * y` (quadratic, allowed); `/ 2` by a constant; no `%`
- **Other constraints:**
  - ordering: `model.addConstr(t == gp.max_([x, y]))`; `gp.min_([x, y])` (variables or constants only)
  - arithmetic: `model.addConstr(d == gp.abs_(z))` (`z` must be a variable, not an expression: define `z == x - y` first)
- **Objectives and solving:** `model.setObjective(e, GRB.MINIMIZE)` or `GRB.MAXIMIZE`; `model.optimize()`; `model.Status == GRB.OPTIMAL`; `model.ObjVal`; `v.X` (floats: `round()` them); `model.Params.MIPGap = 0`, `model.Params.OutputFlag = 0`

## Modelling
- **Domains:** the tightest `lb`/`ub` the data allows (they set the strength of every big-M and indicator); a choice among few values: binaries `y[i, v]` with `y.sum(i, "*") == 1` and `x[i] == gp.quicksum(v * y[i, v] for v in V)`
- **Structure:** all-different: one-hot `y[i, v]` with `y.sum("*", v) <= 1` per value; tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `(go[i, j] == 1) >> (o[j] >= o[i] + 1)` (the start node has none)
- **Lookups:** weight binaries directly in sums (`gp.quicksum(d[i][j] * go[i, j] ...)`); a binary times a bounded integer: `(b == 1) >> (p == v)` and `(b == 0) >> (p == 0)`, not `b * v`
- **Symmetry:** order interchangeable objects (`x[i] <= x[i + 1] - 1`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html
