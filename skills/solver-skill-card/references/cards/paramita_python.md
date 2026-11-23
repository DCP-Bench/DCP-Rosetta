# Paramita (Python) — Python, Boolean modelling compiled to CNF / weighted CNF for SAT and MaxSAT solvers

## Minimal working example (knapsack)
```python
from paramita.containers import WcnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_weighted_container, evaluate, to_cnf
from paramita.solvers import MaxSatSolver
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
x = [Bool(f"x{i}") for i in range(len(values))]
profit = sum(v * xi for v, xi in zip(values, x))
subject_to = sum(w * xi for w, xi in zip(weights, x)) <= capacity
formula, pool = WcnfFormula(), DimacsVariablePool()
add_to_weighted_container(profit, subject_to, to_cnf, formula, pool)
solver = MaxSatSolver.from_name("EvalMaxSAT2022")
solver.add_clauses(formula.hard_clauses())
for weight, clause in formula.soft_clauses():
    solver.add_clause(clause, weight)
solver.solve()
truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
print(evaluate(profit, truth), [evaluate(xi, truth) for xi in x])
```

## API
- **Decision variables:** `Bool(name)` (Booleans only; integers as weighted sums of Bools)
- **Logic constraints:** `~a`; `a & b`; `a | b`; `And(cs)`; `Or(cs)`; `If(a, c)` (a ⇒ c); `Iff(a, b)`
- **Arithmetic constraints:** `sum(w * b ...)` with `==`, `<=`, `<`, `>=`, `>` (constant `w` only)
- **Objectives and solving:** `subject_to &= c` (conjoin constraints); `add_to_weighted_container(obj, subject_to, to_cnf, formula, pool)` (maximises `obj`; minimise with `-obj`); satisfaction: `CnfFormula()`, `add_to_container(subject_to, to_cnf, formula, pool)`, `SatSolver.from_name("Cadical300")`, `solver.add_clauses(formula.clauses())`; `solver.solve()`; `evaluate(e, truth)`

## Modelling
- **Integers:** a small range as one-hot `Bool`s with `sum(bs) == 1`; a wide range as bits `sum(2 ** q * b[q] ...)` with the tightest bit count
- **Structure:** tour or path: arc `Bool`s only between allowed pairs, one out and one in per node, plus integer ranks with `If(go, r[j] == r[i] + 1)` (the start rank fixed); never a position-by-time grid over all pairs
- **Costs:** weight the Boolean choices directly in sums (`sum(d[i][j] * go[i][j] ...)`)
- **Symmetry:** order interchangeable objects (`r[a] < r[b]`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://codeberg.org/paramita/paramita-plugins
