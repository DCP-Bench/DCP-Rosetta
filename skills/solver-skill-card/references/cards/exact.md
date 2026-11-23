# Exact (Python) — Python, integer linear (pseudo-Boolean) solver with multiplication constraints

## Minimal working example (knapsack)
```python
from exact import Exact
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
solver = Exact()
x = [f"x{i}" for i in range(len(values))]
for v in x:
    solver.addVariable(v, 0, 1)
solver.addConstraint(list(zip(weights, x)), False, 0, True, capacity)
solver.setObjective(list(zip(values, x)), minimize=False)
solver.runFull()
print(solver.getBestSoFar(), solver.getLastSolutionFor(x))
```

## API
- **Decision variables:** `solver.addVariable(name, lb, ub)` (variables are string names; Boolean: `lb=0, ub=1`); arrays: lists of names, `[f"x{i}" for i in range(n)]`; `solver.fix(name, value)`
- **Logic constraints:** `solver.addReification(h, True, terms, k)` (h ⇔ Σ ≥ k; `False`: h ⇔ Σ < k); `solver.addLeftReification(h, True, terms, k)` (Σ ≥ k ⇒ h); `solver.addRightReification(h, True, terms, k)` (h ⇒ Σ ≥ k)
- **Arithmetic constraints:** `solver.addConstraint(terms, use_lb, lb, use_ub, ub)` with `terms = [(coef, name), ...]` (lb ≤ Σ ≤ ub; = when lb = ub); `solver.addMultiplication([a, b], True, z, True, z)` (z = a·b, z a variable name)
- **Objectives and solving:** `solver.setObjective(terms, minimize=True, offset=0)` (linear); `solver.runFull()`; `solver.hasSolution()` (`runFull` returns "UNSAT" also after proving the optimum); `solver.getBestSoFar()`; `solver.getLastSolutionFor(names)`

## Modelling
- **Domains:** the tightest bounds the data allows in `addVariable`; a choice among few values: one 0/1 variable per value with `Σ = 1`
- **Structure:** tour or path: 0/1 arc variables only between allowed pairs, one arc out and one in per node, plus order variables `addRightReification(go_ij, True, [(1, o_j), (-1, o_i)], 1)` (arc ⇒ o_j ≥ o_i + 1; the start node has none); never a position-by-value grid over all pairs
- **Costs:** weight the 0/1 choices directly in sums (`Σ d_ij · go_ij`) instead of lookups; a product with a small-domain factor: split on its values instead of `addMultiplication`
- **Symmetry:** order interchangeable objects (`[(1, b), (-1, a)] ≥ 1`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://gitlab.com/nonfiction-software/exact
