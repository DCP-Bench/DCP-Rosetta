# Huub in Rust (crate `huub`)

Huub's native API: a Rust crate. Shared concepts and solver-level issues: [SKILL.md](../SKILL.md).

## Install

Official: [crate page](https://crates.io/crates/huub), [API reference](https://docs.rs/huub/100.1.0/huub/), [repository](https://github.com/huub-solver/huub), [project site](https://huub.solutions).

```bash
cargo new my-model && cd my-model
cargo add huub@=100.1.0
cargo run --release           # first build; it compiles CaDiCaL with g++, takes about 40 s
```

| Requirement | Why |
|---|---|
| `g++` (or any C++ compiler that `cc` finds) | `pindakaas-cadical` compiles CaDiCaL with the `cc` crate. Without it the build fails in that crate's build script |
| Network to crates.io, or a vendored copy | `cargo add` and the first build download huub and its dependencies |

Pin the version exactly (`=100.1.0`): the examples were tested against it. Release builds are
much faster to search with, so use `--release` for anything that is timed.

## Quick start

Put this in `src/main.rs` of the project above. It finds `x` and `y` with `x + y = 7` and `x <= y`.

```rust
use huub::model::Model;
use huub::solver::{Solver, Valuation};

fn main() {
    let mut m = Model::default();
    let x = m.new_int_decision(0..=5);
    let y = m.new_int_decision(0..=5);
    m.linear(x + y).eq(7).post().unwrap();
    m.linear(x).le(y).post().unwrap();

    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let outputs = vec![map.get(&mut solver, x), map.get(&mut solver, y)];
    solver
        .solve()
        .all_solutions(outputs.clone())
        .on_solution(|sol| println!("x = {}, y = {}", outputs[0].val(sol), outputs[1].val(sol)))
        .satisfy();
}
```

`unwrap` turns a conflict at post into a panic, which is fine for a script. In a function that
returns `Result`, propagate the error with `?` instead.

## Modelling

Crate API: [docs.rs](https://docs.rs/huub/100.1.0/huub/). Every constraint ends in `.post()?`,
or `.define()` when it returns a new view.

| Need | Call |
|---|---|
| integer in a range | `m.new_int_decision(0..=5)`, `m.new_int_decisions(n, 0..=5)`; Boolean: `m.new_bool_decision()` |
| linear `<=`, `<`, `==`, `!=`, `>=`, `>` | `m.linear(x * 3 - y * 2 + 5).le(z).post()?` (also `eq`, `ne`, `lt`, `ge`, `gt`) |
| constraint holds iff a Boolean | `.reified_by(b)` is an equivalence (`b` true iff the constraint holds, so `b` false forces the negation); one way only: `.implied_by(b)` (`b` true forces the constraint, `b` false leaves it free); the indicator: `.reify()` gives a `View<bool>` |
| all different | `m.unique(xs.clone()).post()?` |
| allowed tuples (positive table only) | `m.table(vars).values(rows).post()?` |
| `array[index] == value`, 0-based | `m.element(array).index(i).result(r).post()?`, or `.define()` for a new view |
| `\|x\|`, `x / y`, `x * y`, `x^2` | `m.abs(x).define()`, `m.div(x, y).define()` (truncates), `m.mul(x, y).define()`, `m.pow(x, 2).define()` |
| min / max of variables | `m.minimum(xs).define()`, `m.maximum(xs).result(hi).post()?` |
| membership in a set | `m.contains(huub::Set::from_iter([1i64..=2, 7..=7])).member(x).define()` |
| tasks sharing a resource | `m.cumulative().start_times(s).durations(d).usages(u).capacity(c).post()?` |
| tasks on a unary resource | `m.disjunctive().start_times(s).durations(d).post()?` (durations are constants) |
| rectangles that do not overlap | `m.no_overlap().origins(o).sizes(z).post()?` with one inner `Vec` per object: `o[i] = vec![x[i], y[i]]`, `z[i] = vec![w[i], h[i]]`. Sizes must be constants or singleton domains; keep the default `strict` |
| first occurrence order | `m.value_precede(xs).post()?` |
| Boolean formula | `m.proposition(BoolFormula::Atom(b) \| BoolFormula::Atom(d)).post()?` |
| sum of Booleans or counts | `m.linear(bs.iter().copied().sum::<IntLinearExp>()).eq(2).post()?`; a count of `x == v` is the same, with `x.eq(v)` in the sum |

`IntLinearExp::from` takes only `i64` and `View<i64>`. A `View<bool>` does not convert: a single
Boolean in a sum is `std::iter::once(b).sum::<IntLinearExp>()`, a weighted Boolean is
`x.eq(v) * w` (a `View<bool>` times an `i64` is a valid term), and a 0/1 integer view
`b.into()` (declared `let bi: View<i64> = b.into();`) can be scaled like any integer view. A
product of an integer view and a constant (`xs[i] * c`) is a `View<i64>`, so wrap each term
with `IntLinearExp::from(..)` before collecting them into a `Vec<IntLinearExp>`.



**Writing constraints.** Write `x * 3`, not `3 * x`. `x % 3` does not compile. `x == y` on two views
posts nothing: use `m.linear(x - y).eq(0)`.

Examples: [maximise-production](../assets/rust/maximise-production/README.md), [schedule-makespan](../assets/rust/schedule-makespan/README.md),
[element-table](../assets/rust/element-table/README.md), [infeasible-post](../assets/rust/infeasible-post/README.md).

## Solving

Lower the model once: `let (mut solver, map): (Solver, _) = m.lower().to_solver()?;`. Map each
`View` you need with `map.get(&mut solver, view)`. Adding constraints after lowering has no effect
on the solver.

**Optimisation.** `minimize(objective)` and `maximize(objective)` take an integer view and return
`(Status, Option<i64>)`. They must be the **first** solve on that solver: after another solve the
bound is stale and `minimize` can report a wrong value. See [schedule-makespan](../assets/rust/schedule-makespan/README.md).

| Call | Result | Meaning |
|---|---|---|
| `minimize` / `maximize` | `(Complete, Some(v))` | optimum `v`, proven |
| | `(Unsatisfiable, _)` | no solution |
| | `(Satisfied, Some(v))` | stopped with an incumbent `v`; not proven |
| | `(Unknown, _)` | stopped with nothing |
| `satisfy` after `all_solutions(views)` | `Complete` | every distinct solution over `views` was listed |
| | `Satisfied` | stopped early, with solutions |
| | `Unknown` | stopped early, with none |
| | `Unsatisfiable` | infeasible |

**Enumerating optimal solutions.** Prove the optimum first, pin it, then enumerate on a second
solve. `assuming(Some(pin))` takes an `Option`, and `None` means no pin.

```rust
let pin = objective.lit(&mut solver, IntLitMeaning::Eq(best));   // needs huub::actions::IntDecisionActions
let status = solver.solve().assuming(Some(pin)).all_solutions(outputs).on_solution(|_| rows += 1).satisfy();
```

Do not chain `minimize(..).all_solutions(..)`: it fires on improving solutions and panics when the
objective is constant. [all-optimal-solutions](../assets/rust/all-optimal-solutions/README.md) has the full program.

**Distinct solutions.** `all_solutions(views)` lists distinct assignments over `views`, so auxiliary
variables do not repeat a row. Views you do not list are not enumerated.

**Time limits.** Set a terminate callback. It is called about every ten conflicts, and the solver
stops within about a millisecond of the signal:

```rust
let deadline = std::time::Instant::now() + std::time::Duration::from_secs(10);
solver.set_terminate_callback(Some(move || {
    if std::time::Instant::now() >= deadline {
        huub::solver::TerminationSignal::Terminate
    } else {
        huub::solver::TerminationSignal::Continue
    }
}));
```

The solver does not check a count between solutions, so a callback can receive more solutions
than the count you set. Count in the callback and drop the extras
when the number matters.

**Values.** `view.val(sol)` gives `i64` for an integer view and `bool` for a Boolean view
(`use huub::solver::Valuation;`). Integer domains are 64-bit.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| A constraint has no effect; a solution violates it | `post()` returned `Err`, and the result was ignored | Write `post()?`, or `.unwrap()`. Never `let _ =` or `.ok()` on a `post()` |
| Optimum reported too low or high after another solve | `minimize` is not the first solve | Solve for the optimum on a fresh solver, first |
| `all_solutions` panics with a constant objective | Mixed `minimize` and `all_solutions` | Use `minimize`, then pin and enumerate separately |
| Maximisation climbs one value per step | A loose objective and the default search | Slow but correct. Tested on small cases: `IntBrancher::new_in(&mut s, vec![obj], DecisionSelection::InputOrder, DomainSelection::IndomainMax)` (in `huub::solver::branchers`) speeds it up. The effect on large models is not measured |
| Panic when lowering (`new_int_decision(5..=3)`) | An empty domain | Give a valid range, `lo..=hi` with `lo <= hi` |
| Panic on `element(vec![false, ...])` or a length mismatch in `table`, `cumulative` or `disjunctive` | Wrong element type or lengths | Use `i64` arrays of matching length |
| `element` accepts one index past the end | `element` over a constant `Vec<bool>` ending in `true` | Use a `Vec<i64>` of 0/1, or restrict the index domain |
| Wrong index by one | `element` is 0-based | Index with `i - 1` for 1-based data |
| `define()` returns a variable with the full `i64` range | `define` on `linear`, `minimum`, `maximum`, `mul` or `pow` | Create the variable yourself and pass it to `.result(v)` |
| Does not compile: `3 * x`, `x % 3`, `x * y` | Operator forms Huub does not provide | Write `x * 3`; decompose modulo; use `m.mul(x, y)` |
| `x == y` on views posts nothing | `==` on views is Rust equality | Use `m.linear(x - y).eq(0)` |
| `the trait bound IntLinearExp: From<View<bool>> is not satisfied`, or a sum of `View<i64>` and `View<bool>` does not compile | `IntLinearExp::from` accepts `i64` and `View<i64>` only | `std::iter::once(b).sum::<IntLinearExp>()` for one Boolean, `x.eq(v) * w` for a weighted Boolean, or a 0/1 integer view as in the table above |
| The model is infeasible although a solution exists; a constraint seems to hold in both directions | `reified_by(b)` is an equivalence, so with `b` false the negation is enforced | Use `implied_by(b)` when `b` should only switch the constraint on |
| Rectangles overlap in a solution of `no_overlap` | Origins nested per dimension (`vec![xs, ys]`) compile and mean two objects in n dimensions; or the sizes are decision variables, where Huub 100.1.0 can accept overlapping solutions | Nest per object (`(0..n).map(\|i\| vec![x[i], y[i]])`). With variable sizes (rotation) post the pairwise disjunction instead: `x_i + w_i <= x_j`, `x_j + w_j <= x_i`, `y_i + h_i <= y_j`, `y_j + h_j <= y_i`, at least one holds (reified linears and a proposition) |
| `cannot find function circuit` | Huub has no circuit builder | Use the decomposition in [circuit-decomposition](../assets/rust/circuit-decomposition/README.md) |
| Off-by-one in a 1-based array | `element` is 0-based | Index `i - 1` |
