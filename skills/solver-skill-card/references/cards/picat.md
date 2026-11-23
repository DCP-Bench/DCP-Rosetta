# Picat (cp / sat) — Picat, finite-domain constraint programming (`cp`) or SAT encoding (`sat`)

## Minimal working example (knapsack)
```picat
import cp.
main =>
    Values = [6, 10, 12], Weights = [1, 2, 3], Capacity = 5,
    N = len(Values),
    X = new_list(N), X :: 0..1,
    sum([Weights[I] * X[I] : I in 1..N]) #=< Capacity,
    Total #= sum([Values[I] * X[I] : I in 1..N]),
    solve([$max(Total)], X),
    println([Total, X]).
```

## API
- **Decision variables:** `X = new_list(N)`; `A = new_array(R, C)` (`A[I, J]`, 1-based); `X :: L..U` (also on lists and arrays); lists of lists: `L[I, J]` (not `L[I][J]`); `import cp.` or `import sat.` is required for `#=` and friends
- **Logic constraints:** `#/\`; `#\/`; `#~`; `#=>`; `#<=>` (`B #<=> (X #= 3)` reifies); constraints as 0/1 terms: `sum([X[I] #= 0 : I in 1..N]) #>= 1`
- **Arithmetic constraints:** `#=`, `#!=`, `#<`, `#=<`, `#>`, `#>=`; `sum(L)`; `sum([E : I in 1..N])`; `*`; `div`; `mod`; `abs(E)`; `max(L)`; `min(L)` (`len(L)` is a plain integer)
- **Other constraints:**
  - counting: `all_different(L)` (expression lists need `$`: `[$Q[I] - I : I in 1..N]`); `count(V, L, #=, C)`
  - indexing/extensional: `element(I, L, V)` (V = L[I], 1-based); `table_in({X, Y}, [{1, 2}, {3, 4}])`
  - ordering: `increasing(L)`
  - graph: `circuit(Next)` (1-based)
  - scheduling: `cumulative(Starts, Durations, Resources, Limit)`
- **Objectives and solving:** `solve([$min(E)], Vars)`; `solve([$max(E)], Vars)` (binds `Vars`); satisfaction: `solve(Vars)`; options combine, e.g. `[ff, $min(E)]`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `X :: [1, 4, 7]`
- **Structure:** tour or path: `circuit(Next)` with `Next[I] :: Nbs` (its allowed neighbours; a path adds a dummy node that closes the cycle), not a position sequence with `abs`/`#\/` move tests; row patterns: `regular(X, Q, S, M, Q0, F)` (`X` in `1..S`, `M[Q][S]` next state, 0 fails, `F` list of final states); resources: `cumulative`
- **Lookups:** `element(Next[I], D[I], Leg[I])` per row, not a computed flat index; a product of two variables where one has a small domain: split on its values, `(L #= K) #=> (C #= K * P)`
- **Symmetry:** order interchangeable objects, `increasing(L)` or `X[I] #< X[I+1]`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)
- **Search:** `Vars` is labelled in order: put the variables that decide the rest first (successors, production levels), auxiliaries out; add `ff` to the options

Docs: https://picat-lang.org/
