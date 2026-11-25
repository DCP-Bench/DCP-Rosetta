# cvc5 (Python, pythonic) — Python, SMT solver with a Z3-style API (integers, Booleans, arrays, bit-vectors); satisfaction only, no optimiser

## Minimal working example (knapsack)
```python
import cvc5.pythonic as c5
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
x = c5.IntVector("x", 3)
solver = c5.Solver()
for xi in x:
    solver.add(xi >= 0, xi <= 1)
solver.add(c5.Sum([w * xi for w, xi in zip(weights, x)]) <= capacity)
value = c5.Sum([v * xi for v, xi in zip(values, x)])
best, sol = None, None
while solver.check() == c5.sat:
    m = solver.model()
    best, sol = m.eval(value).as_long(), [m.eval(xi).as_long() for xi in x]
    solver.add(value > best)
print(best, sol)
```

## API
- **Decision variables:** `c5.Int(name)`; `c5.Ints("a b c")`; `c5.IntVector(name, n)`; `c5.Bool(name)`; `c5.Bools("p q")`; `c5.BoolVector(name, n)`; `c5.Real(name)`; `c5.BitVec(name, width)`; names must be unique per variable; no domains, bound them with constraints; nested lists: `[[c5.Int(f"g{i}_{j}") for j in range(m)] for i in range(n)]`
- **Logic constraints:** `c5.And(a, b)` / `c5.And(list)`; `c5.Or(...)`; `c5.Not(a)`; `c5.Implies(a, b)`; `c5.Xor(a, b)`; `a == b` on Booleans (⇔); `c5.If(cond, t, e)`; `c5.BoolVal(True)`; `c5.IntVal(3)`; Python `and`/`or`/`not` and chained `0 <= x <= 3` raise an error; `c5.Or([])` and `c5.And([])` crash (guard empty lists)
- **Arithmetic constraints:** `==`, `!=`, `<`, `<=`, `>`, `>=`; `+`, `-`, `*`, `**` (int exponent); `x / k` (integer floor division on Int, no `//`); `x % k` (≥ 0); `c5.Sum(xs)` (`c5.Sum([])` is 0); `c5.Product(xs)`; max/abs via `c5.If(a > b, a, b)`; Boolean as number: `c5.If(b, 1, 0)` (Bool + Bool is not allowed)
- **Other constraints:**
  - counting: `c5.Distinct(xs)` or `c5.Distinct(a, b, c)`; count: `c5.Sum([c5.If(x == v, 1, 0) for x in xs])`
  - indexing/extensional: array `t = c5.Array("t", c5.IntSort(), c5.IntSort())`, `c5.Select(t, i)` or `t[i]` (variable index), fix entries with `solver.add(t[k] == val)`; uninterpreted `f = c5.Function("f", c5.IntSort(), c5.IntSort())`, `f(x)`; table: `c5.Or([c5.And(a == p, b == q) for p, q in rows])`
  - bit-vectors: `c5.ULE(a, b)`, `c5.ZeroExt(k, a)` (widen by k bits), `c5.BitVecVal(v, width)`
- **Solving:** `solver = c5.Solver()` (or `c5.SolverFor("QF_LIA")` to fix the logic); `solver.add(c1, c2, ...)` or `solver.add(list)`; `solver.check()` is `c5.sat` / `c5.unsat` / `c5.unknown`; `m = solver.model()`; `m.eval(e, model_completion=True)` (needed for variables the model leaves free); `.as_long()` int, `c5.is_true(m.eval(b))` Boolean; `solver.push()` / `solver.pop()`; to maximise, re-add `obj > best` after each sat answer (see example)

## Modelling
- **Domains:** the tightest bounds from the data, added as `x >= lo, x <= hi` on every integer, or a set of allowed values: `c5.Or([x == v for v in vals])`
- **Structure:** all-different is `c5.Distinct`; a permutation or assignment is `Distinct` over bounded integers (or Booleans `placed[i][v]` linked to `x[i] == v` by `c5.Implies` both ways); `c5.SolverFor("QF_LIA")` for linear integer models
- **Lookups:** a constant row indexed by a variable: `c5.Select(t, i)` over an `Array` whose entries are fixed with `solver.add(t[k] == row[k])`, or a nested `c5.If(i == 0, row[0], c5.If(i == 1, row[1], row[2]))`
- **Symmetry:** order interchangeable objects with `x[i] < x[i + 1]` and fix the first
- **Implied constraints:** add totals the solver cannot infer, such as `c5.Sum(xs) == total`, and channel two views of the same assignment with `c5.Implies`

Docs: https://cvc5.github.io/docs/latest/api/python/pythonic/pythonic.html
