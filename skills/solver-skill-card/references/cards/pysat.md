# PySAT (Python) — Python, SAT/MaxSAT modelling over Booleans and bounded integers (CNF/pseudo-Boolean encodings)

## Minimal working example (knapsack)
```python
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.examples.rc2 import RC2
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
pool = IDPool()
x = [Integer(f"x{i}", 0, 1, vpool=pool) for i in range(len(values))]
engine = IntegerEngine(vars=x, vpool=pool)
engine.add_linear(sum(w * xi for w, xi in zip(weights, x)) <= capacity)
wcnf = WCNF()
wcnf.extend(engine.clausify().clauses)
for v, xi in zip(values, x):
    wcnf.append([xi.equals(1)], weight=v)
solver = RC2(wcnf)
model = solver.compute()
print(sum(values) - solver.cost, [xi.decode(model) for xi in x])
```

## API
- **Decision variables:** `pool.id(name)` (a Boolean literal, an int; negate with `-l`); `Integer(name, lb, ub, encoding="direct"|"order"|"coupled", vpool=pool)`; every Integer must be in `IntegerEngine(vars=[...], vpool=pool)` (`engine.add_var(v)` adds one later)
- **Logic constraints:** clauses are lists of literals in `CNF()`/`WCNF()` with `f.append([a, -b])` and `f.extend(clauses)`; `x.equals(v)` (direct/coupled only), `x.ge(v)`, `x.le(v)` (order/coupled only) are literals
- **Arithmetic constraints:** `engine.add_linear(e)` with `==`, `<=`, `>=`, `!=` and `<`/`>` against another expression (not a constant) on `k*x + y - ...` (constant `k`; Integers only, no products); `sel = engine.add_linear(e, reified=True)` (sel ⇒ e); `engine.add_equal(x, y)`; `engine.add_not_equal(x, y)`
- **Other constraints:**
  - counting: `f.extend(CardEnc.atmost(lits=ls, bound=k, vpool=pool, encoding=EncType.seqcounter).clauses)`; also `CardEnc.atleast`, `CardEnc.equals`; `PBEnc.leq(lits=ls, weights=ws, bound=k, vpool=pool).clauses`; also `PBEnc.geq`, `PBEnc.equals` (positive int weights)
  - ordering: `engine.add_alldifferent(xs)` (direct/coupled only)
- **Objectives and solving:** `f = WCNF()`; `f.append([lit], weight=w)` (soft: pays `w` when false); `r = RC2(f)`; `m = r.compute()` (None when UNSAT); `r.cost`; `x.decode(m)`; `l in m` for a literal; satisfaction: `with Solver(bootstrap_with=cnf) as s: s.solve(); m = s.get_model()` (`from pysat.solvers import Solver`; `s.solve(assumptions=[l])`)

## Modelling
- **Domains:** tight bounds from the data (every value costs clauses); `"coupled"` when you need both `equals` and `ge`/`le` or `add_alldifferent`; `"order"` for large sums and totals; plain 0/1 choices as `pool.id(...)` literals, not Integers
- **Structure:** all-different values: `engine.add_alldifferent(xs)`; choose-k or capacity over Booleans: `CardEnc`/`PBEnc`; linear sums over Integers: one `engine.add_linear(...)`
- **Lookups and costs:** a table or element: `cnf.append([-i.equals(k), y.equals(t[k])])` for each `k`; a cost of an Integer: soft `[-z.ge(v)]` with weight 1 per threshold `v` (order/coupled), or `[b]` with weight `c` per Boolean
- **Symmetry:** order interchangeable items `engine.add_linear(x[i + 1] - x[i] >= 1)` and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand) as one `PBEnc` or `add_linear` over the aggregate

Docs: https://pysathq.github.io/docs/html/
