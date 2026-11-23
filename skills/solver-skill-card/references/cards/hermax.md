# hermax (Python) — Python, MaxSAT modelling over Booleans and bounded integers (CNF/pseudo-Boolean encodings)

## Minimal working example (knapsack)
```python
from hermax.model import Model
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
m = Model()
x = m.bool_vector("x", len(values))
value = sum(v * xi for v, xi in zip(values, x))
m &= sum(w * xi for w, xi in zip(weights, x)) <= capacity
m.obj += -value
r = m.solve()
print(r[value], [r[xi] for xi in x])
```

## API
- **Decision variables:** `m.int(name, lb, ub)`; `m.bool()`; `m.int_vector(name, n, lb, ub)`; `m.bool_vector(name, n)`; `m.int_matrix(name, rows, cols, lb, ub)`; `m.bool_matrix(name, rows, cols)` (`x[i][j]`, `x.row(i)`, `x.col(j)`)
- **Logic constraints:** `~a`; `a | b` (Literals only: `x == v` is a Literal, `x <= y` is not); `m &= a & b` (not nestable); `a.implies(b)`; `c.iff(b)` (b ⇔ c); `c.only_if(b)` (b ⇒ c)
- **Arithmetic constraints:** `m &= e` with `==`, `!=`, `<`, `<=`, `>`, `>=` on linear sums `sum(k * x[i] for i in ...)` (constant `k` only); `m.max(xs, name=...)`; `m.min(xs, name=...)`; `m.modulo(x, k)`
- **Other constraints:**
  - counting: `m &= xs.all_different()`; `m &= bs.exactly_one()`; `m &= bs.at_most_one()` (a bare call posts nothing)
  - indexing/extensional: `m &= m.table([x, y], allowed=rows)`
  - ordering: `m &= xs.increasing()`
  - scheduling: `m &= m.cumulative(starts, durations, demands, capacity)`
- **Objectives and solving:** `m.obj += e` (minimised; maximise with `-e`); `r = m.solve(time_limit=None)`; `r.ok`; `r.status`; `r[x]`, `r[e]`

## Modelling
- **Domains:** the tightest bounds the data allows (every integer is encoded in clauses: a wide range costs size); a choice among few values: `bool_vector` with `exactly_one()`
- **Structure:** tour or path: Boolean arcs only between allowed pairs, one out and one in per node, plus order variables `(u[j] >= u[i] + 1).only_if(x[i][j])` (the start node fixed); never a position-by-value grid over all pairs
- **Costs:** weight the Boolean choices directly in sums (`sum(d[i][j] * x[i][j] ...)`) instead of lookups or products
- **Symmetry:** order interchangeable objects, `m &= xs.increasing()`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence); a redundant `all_different` or degree constraint helps

Docs: https://hermax.readthedocs.io/en/latest/
