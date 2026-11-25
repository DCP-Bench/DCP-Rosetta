# SWI-Prolog CLP(FD) (Prolog) — SWI-Prolog Prolog, finite-domain constraint programming with propagation and labeling

## Minimal working example (knapsack)
```prolog
:- use_module(library(clpfd)).
main :-
    Values = [6, 10, 12], Weights = [1, 2, 3], Capacity = 5,
    length(Xs, 3), Xs ins 0..1,
    scalar_product(Weights, Xs, #=<, Capacity),
    scalar_product(Values, Xs, #=, Total),
    labeling([max(Total)], Xs),
    format("~w ~w~n", [Total, Xs]).
:- initialization((main, halt)).
```

## API
- **Decision variables:** `X in L..U`; `Xs ins L..U` (list); domains join with `\/`, e.g. `X in 1..3 \/ 7..9`; `length(Xs, N)`; `numlist(1, N, L)`; `nth0(I, L, X)` / `nth1(I, L, X)`; `maplist(Goal, L1, L2)`; `foldl(G, L, S0, S)`; `transpose(Rows, Cols)`; `fd_dom(X, D)`, `fd_inf(X, Min)`, `fd_sup(X, Max)`, `fd_size(X, N)`
- **Logic constraints:** `#/\`, `#\/`, `#\ P` (not), `P #\ Q` (xor), `P #==> Q`, `P #<== Q`, `P #<==> Q`; reify with `B #<==> (X #> 2)` (`B` in `0..1`)
- **Arithmetic constraints:** `#=`, `#\=`, `#<`, `#=<`, `#>`, `#>=`; expressions `+ - *`, `//`, `div`, `mod`, `rem`, `abs(E)`, `min(A, B)`, `max(A, B)`, `A^B`
- **Other constraints:**
  - counting: `all_distinct(Xs)`; `all_different(Xs)` (weaker); `sum(Xs, #=, S)`; `scalar_product(Cs, Xs, #=<, S)` (constant `Cs`); `global_cardinality(Xs, [Val-Count, ...])`
  - indexing/extensional: `element(I, List, V)` (1-based); `tuples_in([[X, Y]], Tuples)`; `automaton(Seq, [source(a), sink(b)], [arc(a, 0, b), ...])`
  - ordering: `lex_chain([Xs, Ys])`; `chain(Xs, #=<)` (also `#<`, `#>=`, `#>`)
  - graph: `circuit(Succs)` (1-based successors, one Hamiltonian cycle)
  - scheduling: `cumulative([task(Start, Dur, End, Use, Id), ...], [limit(Cap)])`; `disjoint2([r(X, W, Y, H), ...])`
- **Objectives and solving:** `labeling(Options, Vars)`, `label(Vars)`; options `ff`, `ffc`, `min`, `max`, `leftmost` (variable selection, one of), `up`, `down`, `step`, `enum`, `bisect` (value order or branching), `min(Expr)`, `max(Expr)` (optimise: first solution found is optimal, more on backtracking); `findall(Xs, label(Xs), All)` enumerates; all labelled variables need finite domains (otherwise instantiation error)

## Modelling
- **Domains:** the tightest bounds the data allows, declared before posting constraints so propagation prunes early: `X in 1..9`; allowed values: `X in 1 \/ 4 \/ 7`
- **Structure:** tour: `circuit(Succ)` with `Succ ins 1..N` (restrict arcs with `S in 2 \/ 5`), not position sequences with move tests; permutations and all-different: `all_distinct`, not `all_different` or pairwise `#\=`; patterns: `automaton` or `tuples_in`; resources: `cumulative`; non-overlapping rectangles: `disjoint2`
- **Lookups:** `element(I, Row, V)` per constant row, not a computed flat index; a reified `B #<==> (X #= K)` links a variable to an indicator, and `scalar_product(Costs, Bs, #=, Total)` sums chosen costs
- **Symmetry:** order interchangeable variables with `chain(Xs, #=<)` or `lex_chain([Row1, Row2])`; fix the first
- **Implied constraints:** add redundant `sum(Xs, #=, S)` totals and `global_cardinality` counts the solver cannot infer
- **Search:** `labeling([ff, min(Obj)], Vars)` with the deciding variables first in `Vars`; the objective needs `Obj #= Expr` posted first

Docs: https://www.swi-prolog.org/man/clpfd.html
