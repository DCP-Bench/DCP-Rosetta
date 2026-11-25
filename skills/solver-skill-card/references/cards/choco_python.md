# Choco (Python, pychoco) — Python, constraint programming solver (Choco-solver via pychoco)

## Minimal working example (knapsack)
```python
from pychoco.model import Model
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = Model()
x = [model.boolvar(name=f"x{i}") for i in range(3)]
model.scalar(x, weights, "<=", capacity).post()
total = model.intvar(0, sum(values), "total")
model.scalar(x, values, "=", total).post()
sol = model.get_solver().find_optimal_solution(total, maximize=True)
print(sol.get_int_val(total), [sol.get_int_val(v) for v in x])
```

## API
- **Decision variables:** `model.intvar(lb, ub, name)`; `model.intvar([1, 3, 5])` (enumerated domain); `model.intvar(7)` (constant); `model.boolvar(name=...)` (use `name=`; the first positional is the value); `model.intvars(n, lb, ub, name=)`; `model.boolvars(n, name=)`
- **Constraints are objects:** build one, then `.post()` it; `model.if_then` and `model.if_only_if` post themselves (no `.post()`). Operators are strings: `"="`, `"!="`, `"<"`, `"<="`, `">"`, `">="`
- **Logic constraints:** `c.reify()` (BoolVar b ⇔ c); `c.reify_with(b)`; `c.implied_by(b)`; `model.or_([c1, c2])`; `model.and_([c1, c2])` (list of constraints only or of BoolVars only, never mixed: JVM crash); `model.not_(c)`; `model.if_then(b_or_c, c)`; `model.if_only_if(b_or_c, c)`
- **Arithmetic constraints:** `model.arithm(x, "<", y_or_int)`; `model.arithm(x, "+", y, "=", z)`; `model.sum(xs, "<=", v)`; `model.scalar(xs, coeffs, "=", v)` (int coeffs); `model.times(x, y, z)` (z = x·y); `model.div(x, y, z)`; `model.mod(x, k, r)`; `model.absolute(x, y)` (x = |y|); `model.distance(x, y, "=", d)`; `model.max(m, xs)`; `model.min(m, xs)`; `model.square(x, y)` (x = y²); `model.pow(x, c, y)`
- **Other constraints:**
  - counting: `model.all_different(xs)`; `model.count(value, xs, n)`; `model.global_cardinality(xs, values, occurrences)`; `model.n_values(xs, n)`; `model.among(n, xs, values)`; `model.all_equal(xs)`
  - indexing/extensional: `model.element(v, table, idx)` (v = table[idx], 0-based, table of ints or vars); `model.table(xs, tuples)`; `model.member(x, [1, 2, 3])`; `model.regular(xs, FiniteAutomaton("0*1+0*"))` (`from pychoco.objects.automaton.finite_automaton import FiniteAutomaton`; regexp over digit symbols)
  - ordering: `model.increasing(xs)`; `model.lex_less_eq(xs, ys)`; `model.sort(xs, sorted_xs)`
  - channelling: `model.inverse_channeling(xs, ys)`; `model.bools_int_channeling(bs, i)`
  - graph: `model.circuit(succ)` (0-based); `model.sub_circuit(succ, 0, length)`
  - scheduling: `model.task(start, dur)`; `model.cumulative(tasks, heights, capacity)` (heights and capacity IntVars: `model.intvar(c)`); `model.diff_n(xs, ys, widths, heights, True)`; `model.bin_packing(item_bin, sizes, loads)`
- **Objectives and solving:** `solver = model.get_solver()`; `solver.find_solution()`; `solver.find_optimal_solution(obj, maximize=True)` (obj an IntVar; `None` if unsat); `solver.find_all_solutions(solution_limit=n)`; `sol.get_int_val(v)`

## Modelling
- **Domains:** the tightest bounds from the data; allowed values: `model.intvar([1, 4, 7])` or `model.member(x, [1, 4, 7])`
- **Structure:** a tour is successor variables plus `model.circuit(succ)` (a path adds a dummy node), not a position sequence with move tests; patterns: `model.regular`; resources: `model.cumulative`; packing: `model.bin_packing`, `model.diff_n`
- **Lookups:** `model.element(cost, d[i], succ[i])` per row, not a computed flat index; a product with a small-domain factor: `model.times`
- **Symmetry:** order interchangeable objects with `model.increasing(xs)` or `model.arithm(x[i], "<", x[i + 1])`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand); `model.sum` over the Booleans of a partition
- **Search:** one call such as `solver.set_min_dom_lb_search(*vars)` or `solver.set_input_order_lb_search(*vars)` before solving, listing all decision variables (reading a variable left out of it raises an error); the later call replaces the earlier

Docs: https://pychoco.readthedocs.io/
