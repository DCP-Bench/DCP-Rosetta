# MiniZinc — MiniZinc, solver-independent constraint modelling language (here with Gecode)

## Minimal working example (knapsack)
```minizinc
array[1..3] of int: values = [6, 10, 12];
array[1..3] of int: weights = [1, 2, 3];
int: capacity = 5;
array[1..3] of var bool: x;
constraint sum(i in 1..3)(weights[i] * x[i]) <= capacity;
var int: total = sum(i in 1..3)(values[i] * x[i]);
solve maximize total;
output ["\(total) \(x)\n"];
```

## API
- **Decision variables:** `var 0..9: x;`; `var bool: b;`; `array[1..n] of var 0..9: xs;`; `array[1..n, 1..m] of var 0..3: g;` (`g[i, j]`, `row(g, i)`, `col(g, j)`, 1-based); parameters: `int: n;`, `array[int] of int: a;`; comprehensions: `[e | i in 1..n where c]`
- **Logic constraints:** `/\`, `\/`, `not`, `->`, `<->` (`b <-> x > 3` reifies); `forall(i in 1..n)(e)`; `exists(i in 1..n)(e)`; `bool2int(b)`; `if c then e1 else e2 endif`
- **Arithmetic constraints:** `=`, `!=`, `<`, `<=`, `>`, `>=`; `sum(i in 1..n)(e)`; `*`; `div`; `mod`; `abs(e)`; `max(xs)`; `min(xs)`
- **Other constraints:** (need `include "globals.mzn";`)
  - counting: `all_different(xs)`; `count(xs, v) = c`; `global_cardinality(xs, vals, cnts)`; `nvalue(xs)`
  - indexing/extensional: `a[idx]` with a variable `idx` (element); `table(xs, [| 1, 2 | 2, 1 |])`; `regular(xs, Q, S, d, q0, F)` (`xs` in `1..S`, `d[q, s]` next state, 0 fails, `F` a set)
  - ordering: `increasing(xs)`; `lex_lesseq(xs, ys)`
  - graph: `circuit(succ)`
  - scheduling: `cumulative(s, d, r, b)`; `disjunctive(s, d)`
- **Objectives and solving:** `solve minimize e;` / `solve maximize e;` / `solve satisfy;`; `output ["\(x)\n"];`; `show(x)`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `var {1, 4, 7}: x;`
- **Structure:** tour or path: `circuit(succ)` with each successor restricted to its allowed neighbours (a path adds a dummy node that closes the cycle), not a position sequence with move tests; row patterns: `regular`; resources: `cumulative`
- **Lookups:** index a data array with the variable directly, `d[i, succ[i]]`, not a computed flat index
- **Symmetry:** order interchangeable objects, `increasing(xs)` or `x[i] < x[i + 1]`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://docs.minizinc.dev/
