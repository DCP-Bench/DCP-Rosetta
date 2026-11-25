# Z3 (Python) — Python, SMT solver over integers, Booleans and arrays (z3py)

## Minimal working example (knapsack)
```python
import z3
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
x = [z3.Bool(f"x{i}") for i in range(3)]
opt = z3.Optimize()
opt.add(z3.Sum([z3.If(x[i], weights[i], 0) for i in range(3)]) <= capacity)
obj = opt.maximize(z3.Sum([z3.If(x[i], values[i], 0) for i in range(3)]))
opt.check()
m = opt.model()
print(obj.value(), [z3.is_true(m.eval(v, model_completion=True)) for v in x])
```

## API
- **Decision variables:** `z3.Int("a")`; `z3.Ints("a b c")`; `z3.IntVector("x", n)`; `z3.Bool("p")`; `z3.Bools("p q")`; `z3.BoolVector("b", n)`; nested lists by comprehension; bounds are ordinary constraints (`a >= 0`), Int is unbounded
- **Logic constraints:** `z3.And(a, b)` / `z3.And(list)`; `z3.Or(...)`; `z3.Not(p)`; `z3.Implies(p, q)`; `z3.Xor(p, q)`; `p == (a > 3)` (reification); `z3.If(c, t, e)` (also Bool/Int-valued expression)
- **Arithmetic constraints:** `==`, `!=`, `<`, `<=`, `>`, `>=`; `+`, `-`, `*`; `a / k` and `a % k` (Int: integer division, modulo); `z3.Abs(e)`; `z3.Sum(xs)`; `z3.Product(xs)`; max as `z3.If(a > b, a, b)`
- **Other constraints:**
  - counting: `z3.Distinct(xs)`; `z3.PbEq([(b, w), ...], k)` (Σ w·b = k); `z3.PbLe`; `z3.PbGe`; `z3.AtMost(b1, b2, ..., k)` and `z3.AtLeast(...)` (Booleans, then constant k last); counting by `z3.Sum([z3.If(x == v, 1, 0) for x in xs])`
  - indexing/extensional: `arr = z3.Array("arr", z3.IntSort(), z3.IntSort())`; `z3.Select(arr, i)` or `arr[i]`; `z3.Store(arr, i, v)`; `f = z3.Function("f", z3.IntSort(), z3.IntSort())`, `f(a)`; a Python list cannot be indexed by a Z3 expression
- **Objectives and solving:** `s = z3.Solver()` (satisfaction) or `z3.Optimize()` (`s.minimize(e)` / `s.maximize(e)`, returns a handle: `h.value()`); `s.add(c1, c2, ...)` or `s.add(list)`; `s.check()` is `z3.sat` / `z3.unsat` / `z3.unknown`; `m = s.model()`; `m.eval(e, model_completion=True)`; `.as_long()`; `z3.is_true(v)`; `s.set("timeout", ms)`
- A Bool cannot be added or multiplied as a number; Python `and`/`or`/`not` do not build constraints.

## Modelling
- **Domains:** state tight bounds for every Int (`z3.And(a >= 1, a <= n)`); a set of allowed values: `z3.Or([a == v for v in vals])`
- **Structure:** `z3.Distinct(xs)` for all-different; 0/1 choices as Bools with `z3.PbEq` / `z3.AtMost` for cardinality, `z3.If(b, w, 0)` inside `z3.Sum` for weighted totals; scheduling: pairwise disjunctions `z3.Or(s1 + d1 <= s2, s2 + d2 <= s1)`
- **Lookups:** variable index into a constant row: `arr = z3.Array(...)` with `s.add(arr[i] == v)` per entry, then `arr[idx]`; or `z3.Sum([z3.If(idx == j, row[j], 0) for j in range(len(row))])`
- **Symmetry:** order interchangeable objects, `x[i] < x[i + 1]`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, bounds on a sum)

Docs: https://z3prover.github.io/api/html/namespacez3py.html
