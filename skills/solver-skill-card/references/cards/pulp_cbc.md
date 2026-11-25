# PuLP with CBC (Python) — Python, mixed-integer linear programming (LP/MIP modeller)

## Minimal working example (knapsack)
```python
import pulp
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
prob = pulp.LpProblem("knapsack", pulp.LpMaximize)
x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(3)]
prob += pulp.lpSum(w * xi for w, xi in zip(weights, x)) <= capacity
prob += pulp.lpSum(v * xi for v, xi in zip(values, x))
prob.solve(pulp.PULP_CBC_CMD(msg=False))
print(round(pulp.value(prob.objective)), [round(pulp.value(xi)) for xi in x])
```

## API
- **Decision variables:** `pulp.LpVariable("v", 0, 9, cat="Integer")` (`cat="Binary"` ignores bounds, `"Continuous"` is the default; bounds default to unbounded: give tight ones; keywords `lowBound=`, `upBound=`); `pulp.LpVariable.dicts("y", (range(n), range(m)), cat="Binary")` gives `y[i][j]`, one index list gives `y[i]`
- **Arithmetic constraints:** `prob += expr <= k` with `<=`, `>=`, `==` only; `prob += (expr <= k, "name")`; `prob.addConstraint(expr <= k)`; `pulp.lpSum(terms)`; `pulp.lpDot(coeffs, vars)`; linear only (no `x * y`, `abs`, `min`, `max`, `%`); `a < b` raises `TypeError` and `a != b` silently adds nothing: use `<= b - 1` or a binary
- **Objectives and solving:** `prob += expr` (a bare expression is the objective; `pulp.LpMinimize` or `pulp.LpMaximize` in `LpProblem`; none means feasibility); `prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=60))` returns the status code; `pulp.LpStatus[prob.status]` (`"Optimal"`, `"Infeasible"`); `pulp.value(expr_or_var)` or `v.varValue` return floats: `round()` them

## Modelling
- **Domains:** tightest bounds from the data (they set the big-M); a variable with a few allowed values: binaries `y[i][k]` with `lpSum(y[i][k]) == 1` and `x[i] == lpSum(k * y[i][k])`
- **Structure:** all-different: one-hot `y[i][k]`, `lpSum(y[i][k] for i) <= 1` per value; a tour or ordering: binary arcs only between allowed pairs, one out and one in per node, plus order variables with big-M, `o[i] - o[j] <= -1 + M * (1 - go[i][j])`; never a position-by-value grid over all pairs
- **Lookups:** weight binaries directly (`lpSum(d[i][j] * go[i][j] ...)`); `z = a AND b`: `z <= a`, `z <= b`, `z >= a + b - 1`; a binary times a bounded integer: big-M with the bound; `m = max(xs)`: `m >= x` for each `x` when minimising `m`
- **Symmetry:** order interchangeable objects (`x[i] <= x[i + 1] - 1`) and fix the first
- **Implied constraints:** add totals CBC cannot infer (`lpSum(capacity) >= total demand`) and the smallest valid M per constraint

Docs: https://coin-or.github.io/pulp/
