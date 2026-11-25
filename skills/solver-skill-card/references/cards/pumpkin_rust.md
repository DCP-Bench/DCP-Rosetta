# Pumpkin (Rust) — Rust, lazy clause generation constraint solver

## Minimal working example (knapsack)
```rust
use std::ops::ControlFlow;
use pumpkin_solver::{Solver, conflict_resolvers::resolvers::ResolutionResolver, core::{DefaultBrancher, termination::Indefinite, optimisation::{OptimisationDirection, linear_sat_unsat::LinearSatUnsat}, results::{OptimisationResult, ProblemSolution, SolutionReference}}};
fn main() {
    let (values, weights, capacity) = (vec![6, 10, 12], vec![1, 2, 3], 5);
    let mut solver = Solver::default();
    let x: Vec<_> = (0..values.len()).map(|_| solver.new_literal()).collect();
    let profit = solver.new_bounded_integer(0, values.iter().sum());
    let tag = solver.new_constraint_tag();
    let _ = solver.add_constraint(pumpkin_solver::boolean_less_than_or_equals(weights, x.clone(), capacity, tag)).post();
    let _ = solver.add_constraint(pumpkin_solver::boolean_equals(values, x.clone(), profit, tag)).post();
    let (mut brancher, mut termination, mut resolver) = (solver.default_brancher(), Indefinite, ResolutionResolver::default());
    let callback = |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| -> ControlFlow<()> { ControlFlow::Continue(()) };
    if let OptimisationResult::Optimal(s) = solver.optimise(&mut brancher, &mut termination, &mut resolver, LinearSatUnsat::new(OptimisationDirection::Maximise, profit, callback)) {
        println!("{} {:?}", s.get_integer_value(profit), x.iter().map(|l| s.get_literal_value(*l)).collect::<Vec<_>>());
    };
}
```

## API
Every constraint is `solver.add_constraint(pumpkin_solver::name(args, tag)).post()`, with `tag = solver.new_constraint_tag()`.
- **Decision variables:** `solver.new_bounded_integer(lb, ub)`; `solver.new_literal()`; arrays: `(0..n).map(|_| solver.new_literal()).collect::<Vec<_>>()`; `!lit`; `v.scaled(c)` (a term; needs `use pumpkin_solver::core::variables::TransformableVariable`)
- **Logic constraints:** `clause(lits, tag)` (OR); `conjunction(lits, tag)` (AND); `.reify(lit)` (lit ⇔ c) or `.implied_by(lit)` (lit ⇒ c) instead of `.post()`
- **Arithmetic constraints:** `equals(terms, k, tag)`; `less_than_or_equals(terms, k, tag)`; `not_equals(terms, k, tag)` (`terms`: `Vec` of `v.scaled(c)`, no zero coefficients: panics); `boolean_less_than_or_equals(weights, lits, k, tag)`; `boolean_equals(weights, lits, var, tag)`; `times(x, y, z, tag)` (z = x·y); `maximum(xs, m, tag)`
- **Other constraints:**
  - counting: `all_different(xs, tag)`
  - indexing/extensional: `element(idx, xs, value, tag)` (0-based); `table(xs, rows, tag)`
  - scheduling: `cumulative(starts, durations, demands, capacity, tag)`
- **Objectives and solving:** `solver.optimise(&mut brancher, &mut termination, &mut resolver, LinearSatUnsat::new(OptimisationDirection::Minimise, obj, callback))` → `OptimisationResult::Optimal(s)`; satisfaction: `solver.satisfy(&mut brancher, &mut termination, &mut resolver)` → `SatisfactionResult::Satisfiable(r)`, `r.solution()`; values: `s.get_integer_value(v)`, `s.get_literal_value(l)` (needs `ProblemSolution`)

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `solver.new_sparse_integer(vec![1, 4, 7])`
- **Structure:** tour or path (no circuit): successor variables, each restricted to its allowed neighbours, with `all_different`, plus rank variables, `equals(vec![rank[j].scaled(1), rank[i].scaled(-1)], 1, tag)` `.implied_by(b)` where `b` reifies `succ[i] = j`; a path adds a dummy node that closes the cycle; never channel a position sequence to a grid through n⁴ literals
- **Lookups:** a constant table indexed by a variable: `table(vec![succ[i], leg[i]], rows, tag)` with rows `vec![j, d[i][j]]` (`element` needs variables)
- **Symmetry:** order interchangeable objects, `binary_less_than(a, b, tag)`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence); a redundant `all_different` on predecessors helps a tour

Docs: https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/
