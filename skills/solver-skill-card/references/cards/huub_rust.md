# Huub (Rust) — Rust, lazy clause generation CP solver (crate `huub` 100.1.0)

## Minimal working example (knapsack)
```rust
use huub::model::{Model, expressions::IntLinearExp};
use huub::solver::{Solver, Valuation};
fn main() {
    let (values, weights, capacity) = (vec![6, 10, 12], vec![1, 2, 3], 5);
    let mut m = Model::default();
    let x = m.new_int_decisions(values.len(), 0..=1);
    let profit = m.new_int_decision(0..=values.iter().sum());
    m.linear(x.iter().zip(&weights).map(|(v, w)| IntLinearExp::from(*v * *w)).sum::<IntLinearExp>()).le(capacity).post().unwrap();
    m.linear(x.iter().zip(&values).map(|(v, c)| IntLinearExp::from(*v * *c)).sum::<IntLinearExp>()).eq(profit).post().unwrap();
    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let xs: Vec<_> = x.iter().map(|v| map.get(&mut solver, *v)).collect();
    let p = map.get(&mut solver, profit);
    let mut sol = vec![];
    let (_, best) = solver.solve().on_solution(|s| sol = xs.iter().map(|v| v.val(s)).collect::<Vec<i64>>()).maximize(p);
    println!("{} {:?}", best.unwrap(), sol);
}
```

## API
Every `.post()` returns a `Result` (`Err` = conflict, infeasible): propagate with `?` or `unwrap`, never drop it. Constraints go on `m` before `lower()`; later posts are ignored.
- **Decision variables:** `m.new_int_decision(lo..=hi)` (inclusive; empty range panics); `m.new_int_decisions(n, lo..=hi)` → `Vec<View<i64>>`; `m.new_bool_decision()`, `m.new_bool_decisions(n)` → `View<bool>`; `!b`; `let bi: View<i64> = b.into()`; `View::from(5)` (constant)
- **Logic constraints:** `m.proposition(f).post()` with `BoolFormula::Atom(b)`, `f1 | f2`, `Or(vec)`, `Not(Box::new(f))`, `Implies(Box::new(f), Box::new(g))`, `Equiv(vec)`; `c.reified_by(b)` (b ⇔ c), `c.implied_by(b)` (b ⇒ c) in place of `.post()`; `c.reify()` → `View<bool>`; `x.eq(v)` → `View<bool>` (x = v)
- **Arithmetic constraints:** `m.linear(expr).le(r)` (also `lt ge gt eq ne`; `r`: `i64` or view); `expr`: `x * 3 - y * 2 + 5` (`x * 3`, not `3 * x`; `x == y` posts nothing); sums: `it.map(|v| IntLinearExp::from(*v)).sum::<IntLinearExp>()`, Booleans: `bs.iter().copied().sum::<IntLinearExp>()`, weighted: `[b1 * 5, b2 * 2].into_iter().sum::<IntLinearExp>()`; `m.mul(x, y).define()`; `m.abs(x).define()`; `m.pow(x, 2).define()`; `m.minimum(xs).define()`; `m.maximum(xs).result(v).post()`
- **Other constraints:**
  - counting: `m.unique(xs).post()` (all different); count of `x = v`: `xs.iter().map(|x| x.eq(v)).sum::<IntLinearExp>()` in `m.linear`
  - indexing/extensional: `m.element(vec_i64).index(i).result(r).post()` (0-based, `.define()` for a new view; array may be views); `m.table(vars).values(rows).post()` (rows `Vec<Vec<i64>>`, positive); `m.contains(huub::Set::from_iter([1i64..=2, 7..=7])).member(x).define()` → `View<bool>`
  - scheduling: `m.cumulative().start_times(s).durations(d).usages(u).capacity(c).post()`; `m.disjunctive().start_times(s).durations(d).post()` (constant `Vec<i64>` d, u); `m.no_overlap().origins(o).sizes(z).post()` (`o[i]`, `z[i]`: one `Vec<View<i64>>` per object, one entry per dimension; fixed sizes)
- **Objectives and solving:** `let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();` `let v = map.get(&mut solver, view);` `v.val(sol)` (needs `Valuation`; `i64`/`bool`); `solver.solve().on_solution(|s| ..).maximize(obj)` (or `minimize`) → `(Status, Option<i64>)`, `Status::Complete` = proven, must be the first solve; satisfy: `solver.solve().on_solution(..).satisfy()` → `Status::Satisfied`/`Unsatisfiable`; all solutions over views: `.all_solutions(vec![v1, v2]).on_solution(..).satisfy()` → `Complete`

## Modelling
- **Domains:** tight `lo..=hi` from the data; allowed values: `m.table(vec![x]).values(vec![vec![1], vec![4]])` or `.contains(Set).member(x)`.
- **Structure:** `unique` for permutations and distinctness; no `circuit`, `regular`, `count`, `lex` or `inverse`: a tour is successors `nx` with `unique(nx)`, `nx[i] ≠ i`, an order `ord` with `ord[0] = 0`, `element(nx).index(ord[i]).result(ord[i+1])`; resources use `cumulative` or `disjunctive`, placement `no_overlap`; counts via `x.eq(v)` sums.
- **Lookups:** index a constant `i64` row by a variable with `m.element(row).index(i).result(r)`; a row of allowed pairs is `table(vec![a, b])`; product of two variables `m.mul(x, y).define()`.
- **Symmetry:** order interchangeable variables `m.linear(a).lt(b).post()`; fix the first of a symmetric class.
- **Implied constraints:** bound totals the solver cannot infer (Σ demand ≤ Σ capacity); post a 2-term equality as `.le(r)` and `.ge(r)` (a single `a + b = c` or `y = 3x` can hang on large domains).

Docs: https://docs.rs/huub/100.1.0/huub/
