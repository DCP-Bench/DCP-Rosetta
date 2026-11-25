# ECLiPSe (ic) — ECLiPSe Prolog, finite-domain constraint programming with branch and bound

## Minimal working example (knapsack)
```prolog
:- lib(ic).
:- lib(branch_and_bound).
main :-
    Values = [6, 10, 12], Weights = [1, 2, 3], Capacity = 5,
    length(Xs, 3), Xs :: 0..1,
    sum(Weights * Xs) #=< Capacity,
    Total #= sum(Values * Xs),
    Cost #= -Total,
    minimize(labeling(Xs), Cost),
    printf("%w %w%n", [Total, Xs]).
```

## API
- **Decision variables:** `X :: L..U` (also on lists); `length(Xs, N)`; `nth1(I, Xs, X)` (needs `:- lib(listut).`); loops `( foreach(X, Xs), param(K) do Goal )` (outer variables only via `param`)
- **Logic constraints:** `C1, C2` (and); `C1 or C2`; `C1 => C2`; `B #= (X #= V)` (reification)
- **Arithmetic constraints:** `#=`, `#\=`, `#<`, `#=<`, `#>`, `#>=`; `sum(Xs)`; `sum(Ws * Xs)` (weighted); `*`; `abs(E)`; `min(X, Y)`; `max(X, Y)` (no `mod` on variables in `ic`)
- **Other constraints:**
  - counting: `alldifferent(Xs)`
  - indexing/extensional: `element(I, List, V)` (1-based); `table([Xs], Tuples)` (needs `:- lib(ic_mdd).`)
  - graph: `circuit(Succs)` (1-based)
  - scheduling: `cumulative(Starts, Durations, Usages, Capacity)` (needs `:- lib(ic_edge_finder).`)
- **Objectives and solving:** `minimize(labeling(Vars), Cost)` (maximise with `Cost #= -Total`); satisfaction: `labeling(Vars)`; print with `printf("%w%n", [X])`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `X :: [1, 4, 7]`
- **Structure:** tour or path: `circuit(Succ)` with each successor restricted to its allowed neighbours (`S :: Nbs`; a path adds a dummy node that closes the cycle), not a position sequence with `abs`/`or` move tests; patterns: `table`; resources: `cumulative`
- **Lookups:** `element(S, Row, Leg)` per row, not a computed flat index; a product of two variables where one has a small domain: split on its values, `(L #= K) => (C #= K * P)`
- **Symmetry:** order interchangeable objects (`X #< Y` for neighbours) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)
- **Search:** `search_goal(Vars) :- search(Vars, 0, first_fail, indomain_min, complete, []).`, with the variables that decide the rest (successors, production levels) first in `Vars`

Docs: https://eclipseclp.org/doc/
