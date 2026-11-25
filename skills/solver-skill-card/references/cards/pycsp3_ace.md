# PyCSP3 (Python, ACE) — Python, constraint modelling library compiled to XCSP3 and solved by ACE

## Minimal working example (knapsack)
```python
from pycsp3 import *
vals, weights, capacity = [6, 10, 12], [1, 2, 3], 5
x = VarArray(size=3, dom={0, 1})
satisfy(Sum(weights[i] * x[i] for i in range(3)) <= capacity)
maximize(Sum(vals[i] * x[i] for i in range(3)))
if solve() is OPTIMUM:
    print(bound(), values(x))
```

## API
- **Decision variables:** `Var(dom=range(lo, hi + 1))`; `Var(dom={1, 4, 7})`; `VarArray(size=n, dom=...)`; `VarArray(size=[n, m], dom=...)` (`x[i][j]`, column `x[:, j]`); `dom=lambda i: range(k[i])`. Never name data `values`, `value`, `bound`, `status` (library functions)
- **Logic constraints:** `&`, `|`, `~` (not Python `and`/`or`/`not`; `Not(...)` crashes; parenthesise comparisons); `imply(a, b)`; `iff(a, b)`; `And(a, b)`; `Or(a, b)`; `If(c, Then=a, Else=b)`; `b == (x > 3)`; `x in {1, 2}`; `x not in {0}`; `x.among(1, 2)`
- **Arithmetic constraints:** `==`, `!=`, `<`, `<=`, `>`, `>=`; `Sum(terms)`; `Sum(w[i] * x[i] for i in r)`; `x * y`; `x // k`; `x % k`; `abs(e)`; `Maximum(xs)`; `Minimum(xs)`; `Product(xs)`
- **Other constraints:**
  - counting: `AllDifferent(xs)`; `Count(xs, value=v)`; `Count(xs, values=vs)`; `Cardinality(xs, occurrences={v: k})`; `NValues(xs)`
  - indexing/extensional: `cp_array(row)[idx]` (constant list, 0-based); `x[idx]` (variable list); `Table(scope=xs, supports=rows)`; `Table(scope=xs, conflicts=rows)`; `Regular(scope=xs, automaton=Automaton(start="q0", transitions=[("q0", 0, "q1")], final=["q1"]))`
  - ordering: `Increasing(xs, strict=True)`; `LexIncreasing([xs, ys])`; `Channel(xs, ys)`
  - graph: `Circuit(succ)` (0-based)
  - scheduling: `Cumulative(origins=s, lengths=d, heights=h) <= cap`; `NoOverlap(origins=s, lengths=d)`
- **Objectives and solving:** `minimize(e)` / `maximize(e)` (at most one); `solve()` returns `SAT`, `OPTIMUM`, `UNSAT`; `value(x)`; `values(xs)` (flat list, also for 2-D); `bound()` (objective); unset variables print `*`

## Modelling
- **Domains:** the tightest `range(lo, hi + 1)` the data allows; a set of allowed values: `Var(dom={1, 4, 7})`
- **Structure:** tour or path: `Circuit(succ)` with each successor domain restricted to allowed neighbours (a path adds a dummy node), not a position sequence with move tests; row patterns: `Regular`; resources: `Cumulative`, `NoOverlap`; allocation counts: `Cardinality`; compatible pairs: `Table`
- **Lookups:** `cp_array(d[i])[succ[i]]` per row, not a computed flat index; a cost over a few variables: `Table(scope=[a, b, cost], supports=rows)`
- **Symmetry:** order interchangeable objects, `Increasing(xs, strict=True)` or `LexIncreasing([row1, row2])`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (`Sum(cap) >= Sum(demand)`, count bounds on prefixes of a sequence)

Docs: https://pycsp.org/documentation/
