# Pindakaas (Rust) — Rust, SAT-based encoder for Boolean, integer and linear constraints (CaDiCaL), satisfaction only

## Minimal working example (knapsack)
```rust
use pindakaas::{ClauseDatabaseTools, Valuation, solver::{Solver, SolveResult, cadical::Cadical}, constraint::linear::{Comparator, LinExp, Linear, LinearEncoder}};
fn main() {
    let (values, weights, capacity) = (vec![6, 10, 12], vec![1, 2, 3], 5);
    for target in (0..=values.iter().sum::<i64>()).rev() {
        let mut s = Cadical::default();
        let enc: LinearEncoder = LinearEncoder::default();
        let x: Vec<_> = (0..values.len()).map(|_| s.new_lit()).collect();
        let (mut w, mut v) = (LinExp::default(), LinExp::default());
        for i in 0..x.len() {
            w += LinExp::from(x[i]) * weights[i];
            v += LinExp::from(x[i]) * values[i];
        }
        s.encode(&Linear::new(w, Comparator::LessEq, capacity), &enc).unwrap();
        if s.encode(&Linear::new(v, Comparator::GreaterEq, target), &enc).is_err() { continue; }
        if let SolveResult::Satisfied(sol) = s.solve() {
            println!("{} {:?}", target, x.iter().map(|l| sol.value(*l)).collect::<Vec<_>>());
            break;
        }
    }
}
```

## API
Solver `s = Cadical::default()` is also the clause database; every encoding call returns a `Result` (`Err` = already unsatisfiable), so use `?` or `.unwrap()`. Needs `ClauseDatabaseTools` in scope.
- **Decision variables:** `s.new_lit()` (Lit); `!l`; `IntVar::new(lo..=hi)` (no solver needed); `x.min()`, `x.max()`, `x.card()`; `BoolVal::Lit(l)` / `BoolVal::Const(b)`
- **Logic constraints:** `s.add_clause([l1, !l2])` (items `Lit` or `BoolVal`, OR)
- **Arithmetic constraints:** `let enc: LinearEncoder = LinearEncoder::default();` `s.encode(&Linear::new(e, Comparator::LessEq, k), &enc)` (`Equal`, `LessEq`, `GreaterEq`; `e: LinExp`, constant `k: i64`); `LinExp::default()`, `e += LinExp::from(lit)`, `LinExp::from(x.clone()) * c` (Lit or IntVar term, `+`, `-`, `+=`)
- **Reified comparisons on an IntVar:** `x.equals(&mut s, v)?`, `x.at_least(&mut s, v)?`, `x.at_most(&mut s, v)?` return a `BoolVal` literal (⇔ x = v / x ≥ v / x ≤ v); usable in clauses and `!`
- **Solving:** `s.solve()` → `SolveResult::Satisfied(sol)` (borrows `s`), `Unsatisfiable(_)`, `Unknown`; values: `sol.value(lit)` (needs `Valuation`), `x.value(&sol)`

## Modelling
- **Domains:** tight `IntVar::new(lo..=hi)` from the data; a set of allowed values: `x.equals(&mut s, v)?` literals in one clause, or `!x.equals(...)` to forbid a value
- **Structure:** all-different: for each value `v`, `Σ x_i.equals(&mut s, v)` as `LinExp` `LessEq 1`; assignments and permutations are 0/1 literals with `Equal 1` rows and columns; a cardinality bound is a `Linear` over literals
- **Lookups:** index a constant row by a variable: for each `j`, `s.add_clause([!idx.equals(&mut s, j)?, r.equals(&mut s, row[j])?])`; tuples: one selector literal per row, `!sel ∨ x.equals(v)` per column, selectors `Equal 1`
- **Symmetry:** order interchangeable objects with `Linear` `x_a - x_b LessEq -1`, and fix the first one
- **Implied constraints:** add redundant totals (Σ over rows = Σ over columns) as extra `Linear` rows; keep coefficients small, products of big domains blow up (split on the small factor's values, `x.equals`)

Docs: https://docs.rs/pindakaas/0.6.0/pindakaas/
