# CPMpy (Python) — Python, constraint modelling library over numpy arrays (OR-Tools and other back-ends)

## Minimal working example (knapsack)
```python
import cpmpy as cp
import numpy as np
values, weights, capacity = np.array([6, 10, 12]), np.array([1, 2, 3]), 5
x = cp.boolvar(shape=3, name="x")
model = cp.Model()
model.add(cp.sum(weights * x) <= capacity)
model.maximize(cp.sum(values * x))
model.solve()
print(model.objective_value(), x.value())
```

## API
- **Decision variables:** `cp.intvar(lb, ub, shape=None, name=None)`; `cp.boolvar(shape=None, name=None)`; `shape=(n, m)` gives a numpy-style array: `x[i, j]`, `x[:, j]`
- **Logic constraints:** `&`, `|`, `~` (not Python `and`/`or`/`not`; parenthesise comparisons: `(x > 2) & (y < 8)`); `a.implies(b)`; `b == (x > 3)` (reification); `cp.any(bs)`; `cp.all(bs)`
- **Arithmetic constraints:** `==`, `!=`, `<`, `<=`, `>`, `>=`; `cp.sum(xs)`; `cp.sum(w * x)` (w a numpy array); `x * y`; `x // k`; `x % k`; `cp.abs(e)`; `cp.max(xs)`; `cp.min(xs)`
- **Other constraints:**
  - counting: `cp.AllDifferent(xs)`; `cp.Count(xs, v)`; `cp.GlobalCardinalityCount(xs, vals, cnts)`; `cp.NValue(xs)`
  - indexing/extensional: `cp.cpm_array(arr)[idx]` (element, 0-based); `cp.Table(xs, rows)`; `cp.Regular(xs, [(q, v, q2), ...], start, accepting)`
  - ordering: `cp.Increasing(xs)`; `cp.LexLessEq(xs, ys)`
  - graph: `cp.Circuit(succ)` (0-based)
  - scheduling: `cp.Cumulative(start, duration, demand=d, capacity=c)`; `cp.NoOverlap(start, duration)`
- **Objectives and solving:** `model.minimize(e)` / `model.maximize(e)`; `model.solve()` (True if a solution); `x.value()`; `model.objective_value()`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `cp.InDomain(x, [1, 4, 7])`
- **Structure:** tour or path: `cp.Circuit(succ)` with each successor restricted to its allowed neighbours (a path adds a dummy node that closes the cycle), not a position sequence with move tests; row patterns: `cp.Regular`; resources: `cp.Cumulative`
- **Lookups:** `cp.cpm_array(d[i])[succ[i]]` per row, not a computed flat index
- **Symmetry:** order interchangeable objects, `cp.Increasing(xs)` or `x[i] < x[i + 1]`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://cpmpy.readthedocs.io/
