# Python-MIP with CBC (Python) — Python, mixed-integer linear programming (CBC branch and cut)

## Minimal working example (knapsack)
```python
import mip
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
model.verbose = 0
x = [model.add_var(name=f"x{i}", var_type=mip.BINARY) for i in range(3)]
model.add_constr(mip.xsum(w * xi for w, xi in zip(weights, x)) <= capacity)
model.objective = mip.xsum(v * xi for v, xi in zip(values, x))
model.optimize()
print(round(model.objective_value), [round(xi.x) for xi in x])
```

## API
- **Decision variables:** `model.add_var(name="v", lb=0, ub=9, var_type=mip.INTEGER)` (`mip.BINARY`, `mip.CONTINUOUS` default; default `ub` is infinite: give tight bounds); arrays: lists or dicts `y[i, j]`
- **Arithmetic constraints:** `model.add_constr(e <= k, name="c")` with `<=`, `>=`, `==` only (`<`, `>`, `!=` unsupported); `mip.xsum(terms)` (use instead of `sum`); `mip.LinExpr()` with `e += 2 * v`, `e.add_const(3)`; products of variables are not allowed
- **Objectives and solving:** `model.objective = e` (direction from `mip.Model(sense=mip.MINIMIZE or mip.MAXIMIZE)`, constant included); no objective for satisfaction; `model.optimize()` returns a status, `mip.OptimizationStatus.OPTIMAL`; `v.x` and `model.objective_value` are floats: `round()` them; `model.verbose = 0`; `model.max_mip_gap = 0` (default stops within 0.01% of optimum)

## Modelling
- **Domains:** the tightest `lb`/`ub` the data allows (they set the strength of every big-M); a choice among few values: binaries `y[i, v]` with `xsum(y[i, v] for v) == 1` and `x[i] == xsum(v * y[i, v] for v)`
- **Structure:** all-different: one-hot assignment with `xsum(y[i, v] for i) <= 1` per value; tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `o[i] - o[j] + 1 <= N * (1 - go[i, j])` (the start node has none)
- **Costs:** weight binaries directly in sums (`xsum(d[i][j] * go[i, j] ...)`); product of two binaries: `z <= a`, `z <= b`, `z >= a + b - 1`; a binary times a bounded integer: big-M with the integer's bound
- **Implication:** `b => e <= k` as `e <= k + M * (1 - b)` with the smallest valid `M` from variable bounds
- **Symmetry:** order interchangeable objects (`o[i] + 1 <= o[i + 1]`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand)

Docs: https://python-mip.readthedocs.io/
