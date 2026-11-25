# Essence' (Savile Row, Minion) — Essence', declarative constraint modelling language translated to the Minion CP solver

## Minimal working example (knapsack)
```essence'
language ESSENCE' 1.0
letting values = [6, 10, 12]
letting weights = [1, 2, 3]
letting capacity = 5
find x : matrix indexed by [int(1..3)] of bool
find total : int(0..28)
maximising total
such that
    (sum i : int(1..3) . weights[i] * toInt(x[i])) <= capacity,
    total = sum i : int(1..3) . values[i] * toInt(x[i])
```

## API
- **Decision variables:** `find a, b : int(0..9)`; `find p : bool`; `find xs : matrix indexed by [int(1..n)] of int(0..9)`; `find g : matrix indexed by [int(1..n), int(1..m)] of bool` (`g[i,j]`, row slice `g[i,..]`, `flatten(g)`); every `find` needs a finite domain (plain `int` is an error)
- **Constants:** `letting n = 4`; `letting d = [3, 1, 4]`; `letting t = [[1, 2], [2, 3]]`; `letting ev = [ i | i : int(1..8), i % 2 = 0 ]`; `$` starts a comment
- **Logic constraints:** `/\`, `\/`, `!`, `->`, `<->`; `forAll i, j : int(1..n) . e`; `exists i : int(1..n) . e`; `and([e1, e2])`; `or([e1, e2])`; `toInt(b)` (bool to 0/1)
- **Arithmetic constraints:** `=`, `!=`, `<`, `<=`, `>`, `>=`; `sum i : int(1..n) . e`; `sum(xs)`; `*`; `/` (floor); `%`; `**`; `|e|`; `max(xs)`; `min(xs)`; `max(a, b)`; `min(a, b)`
- **Other constraints:**
  - counting: `allDiff(xs)`; `gcc(xs, vals, counts)` (exact counts); `atleast(xs, vals, counts)`; `atmost(xs, vals, counts)`
  - indexing/extensional: `d[idx]` with a variable `idx`, `d[x[1]]` (element); `table([x1, x2], t)` (rows of `t` are the allowed tuples)
  - ordering: `xs <=lex ys`; `xs <lex ys`
- **Objectives and solving:** `minimising e` / `maximising e` (one line before `such that`; none for satisfaction); `branching on [xs, y]`; `heuristic sdf` (also `conflict`); the constraints follow `such that`, comma-separated, no trailing comma

## Modelling
- **Domains:** the tightest bounds the data allows, `find x : int(lo..hi)`; a set of allowed values: `table([x], [[1], [4], [7]])`
- **Structure:** a permutation or all-distinct group: `allDiff(flatten(g))` and `forAll i : int(1..n) . allDiff(g[i,..])`; fixed value counts: `gcc(xs, vals, counts)`; a relation between variables: `table`, not a chain of `\/`
- **Lookups:** index a constant matrix by a variable directly, `cost[i, s[i]]`, and sum it; a Boolean in a sum is `toInt(b)`
- **Symmetry:** order interchangeable rows or entries, `forAll i : int(1..n-1) . g[i,..] <=lex g[i+1,..]` or `x[i] < x[i+1]`
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand); define each sum as a bounded `find` variable and constrain that variable
- **Search:** `branching on [decisions]` with the deciding variables first, then `heuristic sdf`; auxiliary variables are left out of the list

Docs: https://savilerow.cs.st-andrews.ac.uk/documentation/
