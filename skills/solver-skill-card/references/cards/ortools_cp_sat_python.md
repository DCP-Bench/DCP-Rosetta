# OR-Tools CP-SAT (Python) — Python, lazy-clause-generation CP-SAT solver, integer-only

## Minimal working example (knapsack)
```python
from ortools.sat.python import cp_model
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = cp_model.CpModel()
x = [model.new_bool_var(f"x{i}") for i in range(3)]
model.add(sum(weights[i] * x[i] for i in range(3)) <= capacity)
model.maximize(sum(values[i] * x[i] for i in range(3)))
solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.objective_value, [solver.value(v) for v in x])
```

## API
- **Decision variables:** `model.new_int_var(lb, ub, name)`; `model.new_bool_var(name)`; `model.new_int_var_from_domain(cp_model.Domain.from_values([1, 4, 7]), name)`; `Domain.from_intervals([[0, 2], [5, 6]])`
- **Logic constraints:** `model.add_bool_or(lits)`; `model.add_bool_and(lits)`; `model.add_bool_xor(lits)`; `model.add_implication(a, b)`; `b.Not()` (negated literal, capital N); `ct.only_enforce_if(lit_or_list)` on a constraint returned by `model.add(...)`/`add_bool_and` (`lit ⇒ ct`, one direction only; for `⇔` add the opposite constraint `.only_enforce_if(lit.Not())`)
- **Arithmetic constraints:** `model.add(expr <op> expr)` with `==`, `!=`, `<=`, `<`, `>=`, `>`, `sum(...)` and `k * x` (linear only); `model.add_multiplication_equality(t, [x, y])`; `model.add_division_equality(q, x, k)`; `model.add_modulo_equality(r, x, k)`; `model.add_abs_equality(a, e)`; `model.add_max_equality(m, xs)`; `model.add_min_equality(m, xs)`
- **Other constraints:**
  - counting: `model.add_all_different(exprs)`; `model.add_exactly_one(lits)`; `model.add_at_most_one(lits)`
  - indexing/extensional: `model.add_element(idx, array, target)` (0-based, constants or variables); `model.add_allowed_assignments(xs, tuples)`; `model.add_forbidden_assignments(xs, tuples)`; `model.add_automaton(xs, start, finals, [(q, v, q2), ...])`; `model.add_inverse(f, g)`; `model.add_linear_expression_in_domain(e, domain)`
  - graph: `model.add_circuit([(tail, head, lit), ...])` (nodes 0-based; self-loop arc `(i, i, lit)` skips node i)
  - scheduling: `model.new_fixed_size_interval_var(start, size, name)`; `model.new_interval_var(start, size, end, name)`; `model.new_optional_fixed_size_interval_var(start, size, lit, name)`; `model.add_no_overlap(intervals)`; `model.add_cumulative(intervals, demands, capacity)`; `model.add_no_overlap_2d(x_intervals, y_intervals)`
- **Objectives and solving:** `model.minimize(e)` / `model.maximize(e)`; `solver = cp_model.CpSolver()`; `solver.parameters.max_time_in_seconds = 60`; `solver.parameters.num_workers = 8`; `status = solver.solve(model)` (compare with `cp_model.OPTIMAL`, `cp_model.FEASIBLE`, `cp_model.INFEASIBLE`); `solver.value(e)`; `solver.boolean_value(b)`; `solver.objective_value`

## Modelling
- **Domains:** the tightest `new_int_var(lb, ub)` the data allows; allowed value sets: `new_int_var_from_domain(cp_model.Domain.from_values(vs), name)`
- **Structure:** one `add_circuit` over arcs with Boolean literals for allowed neighbours only (a path adds a dummy node closing the cycle) instead of position sequences; row patterns: `add_automaton`; resources: interval variables with `add_cumulative` / `add_no_overlap`; permutations: `add_all_different`; one-of choices: `add_exactly_one`
- **Lookups:** `add_element(idx, row_i, v)` with the constant row, not a computed flat index; a product with a small-domain factor: Boolean per value, sum `value * b`; `add_allowed_assignments` for explicit tuples
- **Symmetry:** order interchangeable objects with `model.add(x[i] <= x[i + 1])` and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand); channel a second view of a permutation with `add_inverse`
- **Search:** `model.add_decision_strategy(xs, cp_model.CHOOSE_MIN_DOMAIN_SIZE, cp_model.SELECT_MIN_VALUE)` on the deciding variables first; `solver.parameters.num_workers = 8` for portfolio search

Docs: https://developers.google.com/optimization/cp
