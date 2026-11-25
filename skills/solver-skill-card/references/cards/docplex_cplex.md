# DOcplex (Python, CPLEX) — Python, mixed-integer linear programming with indicator and logical constraints

## Minimal working example (knapsack)
```python
from docplex.mp.model import Model
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = Model()
x = model.binary_var_list(3, name="x")
model.add_constraint(model.sum(w * xi for w, xi in zip(weights, x)) <= capacity)
model.maximize(model.sum(v * xi for v, xi in zip(values, x)))
sol = model.solve()
print(round(sol.objective_value), [round(sol[xi]) for xi in x])
```

## API
- **Decision variables:** `model.integer_var(lb=0, ub=9, name="v")` (also `binary_var`, `continuous_var`; default `ub` is infinite: give tight bounds); `model.binary_var_list(n, name="x")`; `model.integer_var_list(n, lb, ub, name="x")`; `model.binary_var_matrix(r, c)` and `model.integer_var_matrix(r, c, lb, ub)` (dict keyed `[i, j]`); `model.binary_var_cube(a, b, c)` (keyed `[i, j, k]`)
- **Logic constraints:** `model.add_indicator(b, e <= k, active_value=1)` (b == active_value ⇒ constraint); `model.add_equivalence(b, e >= k)` (b ⇔ constraint); `model.if_then(c1, c2)`, `model.logical_and(b1, b2)`, `model.logical_or(b1, b2)`, `model.logical_not(b)` (as expressions inside `add_constraint`)
- **Arithmetic constraints:** `model.add_constraint(e <= k, ctname="c")` with `<=`, `>=`, `==`; `model.add_constraints(generator)` (one statement for a whole family); `model.add_range(lo, e, hi)`; `model.sum(iterable)`; `model.dot(vars, coeffs)` (also `model.scal_prod`); `model.abs(e)`, `model.min(a, b)`, `model.max(a, b)` (also over a list)
- **Objectives and solving:** `model.minimize(e)` or `model.maximize(e)`; `sol = model.solve()` returns `None` when infeasible; `sol.objective_value`; `sol[v]` or `v.solution_value` (floats: `round()` them for integers); `model.parameters.timelimit = 60`

## Modelling
- **Domains:** the tightest `lb`/`ub` the data allows (bounds set the strength of every big-M and linearisation); a choice among few values: binaries `y[i, v]` with `model.sum(y[i, v] for v in V) == 1` and `x[i] == model.sum(v * y[i, v] for v in V)`
- **Structure:** all-different: one-hot `y[i, v]` with `Σ_i y[i, v] <= 1`; tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `model.add_indicator(go[i, j], o[j] >= o[i] + 1)` (the start node has none)
- **Costs:** weight binaries directly in sums (`model.sum(d[i][j] * go[i, j] ...)`); a product of two binaries: `model.add_equivalence(z, a + b == 2)` or `z <= a`, `z <= b`, `z >= a + b - 1`; a conditional equation: `add_indicator`, not big-M
- **Symmetry:** order interchangeable objects (`x[i] <= x[i + 1]`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://ibmdecisionoptimization.github.io/docplex-doc/mp/index.html
