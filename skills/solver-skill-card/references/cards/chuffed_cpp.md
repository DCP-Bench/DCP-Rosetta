# Chuffed (C++) — C++, lazy clause generation CP solver (propagation plus SAT learning)

## Minimal working example (knapsack)
```cpp
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/vars/modelling.h>
#include <iostream>
#include <sstream>
struct Knapsack : Problem { void print(std::ostream&) override {} };
int main() {
  vec<IntVar*> x;
  createVars(x, 3, 0, 1);
  IntVar* total = newIntVar(0, 28);
  vec<int> values, weights;
  values.push(6); values.push(10); values.push(12);
  weights.push(1); weights.push(2); weights.push(3);
  int_linear(weights, x, IRT_LE, 5);
  int_linear(values, x, IRT_EQ, total);
  optimize(total, OPT_MAX);
  branch(x, VAR_INORDER, VAL_MAX);
  int best = 0; int sol[3] = {0, 0, 0};
  engine.setSolutionCallback([&](Problem*) {
    best = total->getVal();
    for (int i = 0; i < 3; i++) sol[i] = x[i]->getVal();
  });
  so.print_sol = false;
  std::stringstream sink;
  engine.setOutputStream(sink);
  Knapsack p;
  engine.solve(&p);
  std::cout << best << " " << sol[0] << sol[1] << sol[2] << std::endl;
}
```

## API
- **Decision variables:** `createVars(xs, n, lo, hi)` (`vec<IntVar*>`; `createVars(m, n, k, lo, hi)` for `vec<vec<IntVar*>>`); `newIntVar(lo, hi)`; `getConstant(c)`; `BoolView b = newBoolVar()`; `createVars(bs, n)` (`vec<BoolView>`); `bool2int(b, iv)` (`iv` a 0..1 IntVar); `~b` negates; `vec<T>`: `push(e)`, `push()` (new empty row), `last()`, `size()`; `flatten(m, flat)`; `branch(xs, VAR_SIZE_MIN, VAL_MIN)` (`vec<IntVar*>` only, not BoolViews: use `bool2int` vars)
- **Logic constraints:** `int_rel_reif(x, IRT_LT, y, b)` (`b ⇔ x < y`; also `(x, t, c, b)`); `int_rel_half_reif(x, t, y, b)` (`b ⇒ x t y`); `bool_clause(pos, neg)` (∨pos ∨ ∨¬neg); `array_bool_or(bs, z)`; `array_bool_and(bs, z)`; `bool_rel(x, BRT_AND, y, z)` (`z = x ∧ y`)
- **Arithmetic constraints:** `int_rel(x, IRT_EQ, y)` or `(x, t, c)`; `int_rel(x, IRT_EQ, y, c)` (`x = y + c`); `IRT_EQ NE LE LT GE GT`; `int_linear(coefs, xs, IRT_LE, k)` (`k` an int or `IntVar*`; extra last arg `b` reifies; arguments must be lvalue `vec`s); `int_linear(xs, IRT_EQ, y)` (unit weights); `bin_linear(x, y, IRT_LE, c)` (`x + y ≤ c`); `bool_linear(bs, IRT_EQ, y)` (count of true); `int_plus(x, y, z)`, `int_minus(x, y, z)`, `int_times(x, y, z)` (`z = x∘y`); `int_div(x, y, z)` (`z` must be non-negative); `int_abs(x, z)`; `int_min(x, y, z)`; `int_max(x, y, z)`; `minimum(xs, z)`; `maximum(xs, z)`; `int_mod` aborts "Not yet supported"
- **Other constraints:**
  - counting: `all_different(xs)` (`all_different(xs, CL_DOM)` for domain consistency)
  - indexing/extensional: `array_int_element(idx, arr, res)` (`res = arr[idx]`, 0-based, `arr` a `vec<int>`; last arg offset for 1-based); `array_var_int_element_bound(idx, vars, res)`; `table(xs, tuples)` (`vec<vec<int>>`, allowed rows); `regular(xs, nstates, nsyms, d, q0, final)` (`d[state-1][sym-1]` = next state, 0 = fail; states, symbols 1-based; `final` a `vec<int>`)
  - ordering: `lex(xs, ys, false)` (`xs ≤ ys`; `true` strict); `value_precede_int(s, t, xs)`; `inverse(xs, ys)`
  - graph: `circuit(succ)` (0-based); `subcircuit(succ)` (`succ[i] == i` skips node i)
  - scheduling: `cumulative(starts, durs, uses, limit)` (`vec<int>` durs, uses); `disjunctive(starts, durs)`
- **Objectives and solving:** `optimize(obj, OPT_MIN)` or `OPT_MAX` (once, before `engine.solve(&problem)`); `branch(xs, VAR_INORDER, VAL_MAX)` (also `VAR_SIZE_MIN`, `VAL_SPLIT_MIN`); `engine.setSolutionCallback([&](Problem*) {...})` reads `x->getVal()` per solution (last improving one is optimal); satisfaction with several solutions: `output_vars(xs)` and `so.nof_solutions = n`; `so.print_sol = false`; link `-I/opt/chuffed/include -lchuffed -lchuffed_fzn -lchuffed -lpthread`

## Modelling
- **Domains:** the tightest bounds the data allows in `newIntVar(lo, hi)`; a set of allowed values: `table` over one variable with one-element rows
- **Structure:** tour or path: successor variables restricted to allowed neighbours with `table` pairs, plus `circuit(succ)` (a path adds a dummy node); patterns: `regular`; resources: `cumulative(starts, durs, uses, cap)`, non-overlap: `disjunctive`; allowed combinations: `table`
- **Lookups:** `array_int_element(succ[i], row_i, leg[i])` per row, not a computed flat index; a product with a small-domain factor: split on its values, `int_rel_reif(l, IRT_EQ, k, b)` then `int_linear(one, cv, IRT_EQ, k * p, b)`
- **Symmetry:** order interchangeable objects with `int_rel(a, IRT_LT, b)` or `lex(xs, ys, false)`; `value_precede_int(s, t, xs)` for interchangeable values
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand) with `int_linear`
- **Search:** `branch` first on the variables that decide the rest, `VAR_SIZE_MIN`; one `branch` per array, in that order

Docs: https://github.com/chuffed/chuffed
