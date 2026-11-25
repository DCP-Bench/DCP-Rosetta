# SCIP (Python, PySCIPOpt) — Python, mixed-integer (non)linear programming with constraint handlers

## Minimal working example (knapsack)
```python
from pyscipopt import Model, quicksum
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = Model()
model.hideOutput()
x = [model.addVar(vtype="B", name=f"x{i}") for i in range(3)]
model.addCons(quicksum(w * xi for w, xi in zip(weights, x)) <= capacity)
model.setObjective(quicksum(v * xi for v, xi in zip(values, x)), "maximize")
model.optimize()
print(round(model.getObjVal()), [round(model.getVal(xi)) for xi in x])
```

## API
- **Decision variables:** `model.addVar(vtype="I", lb=0, ub=9, name="v")` (`"B"` binary, `"C"` continuous; default `ub` is infinite: give tight bounds; `lb=None` for no lower bound); arrays: lists or dicts `x[i, j]`
- **Logic constraints:** `model.addConsAnd(bs, r)` (r ⇔ ∧bs); `model.addConsOr(bs, r)` (r ⇔ ∨bs); `model.addConsXor(bs, True)`; `model.addConsIndicator(e <= k, b)` (b ⇒ e ≤ k; also `>=`)
- **Arithmetic constraints:** `model.addCons(e <= k)` with `<=`, `>=`, `==` only (`<`, `>`, `!=` raise `NotImplementedError`: use `<= k - 1` or a binary); `quicksum(...)`; `x * y` (nonlinear allowed); `abs(e)`
- **Objectives and solving:** `model.setObjective(e, "minimize")` or `"maximize"` (linear); `model.optimize()`; `model.getStatus()` (`"optimal"`); `model.getVal(v)` and `model.getObjVal()` return floats: `round()` them

## Modelling
- **Domains:** the tightest `lb`/`ub` the data allows (bounds set the strength of every linearisation); a choice among few values: binaries `y[i, v]` with `Σ_v y[i, v] == 1` and `x[i] == Σ v·y[i, v]`
- **Structure:** all-different: one-hot assignment, `Σ_i y[i, v] <= 1` per value; tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `addConsIndicator(o[i] - o[j] <= -1, go[i, j])` (the start node has none); never a position-by-value grid over all pairs
- **Costs:** weight binaries directly in sums (`Σ d[i][j] · go[i, j]`); a product of two binaries: `addConsAnd([a, b], z)`; a binary times a bounded integer: `addConsIndicator`
- **Symmetry:** order interchangeable objects (`o[i] <= o[i + 1] - 1`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://pyscipopt.readthedocs.io/
