# Gecode (C++) — C++, constraint propagation with branching search

## Minimal working example (knapsack)
```cpp
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;
class Knapsack : public IntMaximizeSpace {
public:
  BoolVarArray x;
  IntVar total;
  Knapsack() : x(*this, 3, 0, 1), total(*this, 0, 28) {
    IntArgs values({6, 10, 12}), weights({1, 2, 3}); int capacity = 5;
    linear(*this, weights, x, IRT_LQ, capacity);
    linear(*this, values, x, IRT_EQ, total);
    branch(*this, x, BOOL_VAR_NONE(), BOOL_VAL_MAX());
  }
  Knapsack(Knapsack& s) : IntMaximizeSpace(s) {
    x.update(*this, s.x);
    total.update(*this, s.total);
  }
  Space* copy() override { return new Knapsack(*this); }
  IntVar cost() const override { return total; }
};
int main() {
  BAB<Knapsack> e(new Knapsack);
  Knapsack* best = nullptr;
  while (Knapsack* s = e.next()) { delete best; best = s; }
  std::cout << best->total << " " << best->x << std::endl;
}
```

## API
- **Decision variables:** `IntVar(*this, lb, ub)`; `BoolVar(*this, 0, 1)`; `IntVarArray(*this, n, lb, ub)`; `BoolVarArray(*this, n, 0, 1)` (class members, each `update`d in the copy constructor; `IntVarArgs` has no `update`, so build it locally; matrix: flat `xs[i*m+j]`; `BoolVar` is not an `IntVar`: collect them in `BoolVarArgs`, which `linear` also accepts); `branch(*this, xs, INT_VAR_SIZE_MIN(), INT_VAL_MIN())` (every decision array needs a branching)
- **Logic constraints:** `rel(*this, e)` with `&&`, `||`, `!`, `>>` (implication) over Boolean expressions, e.g. `rel(*this, (x == 1) >> (y != 2))`; `BoolVar b = expr(*this, x <= y)` (reification); `clause(*this, BOT_OR, pos, neg, 1)`
- **Arithmetic constraints:** `rel(*this, e1 == e2)` with `==`, `!=`, `<`, `<=`, `>`, `>=` over `+ - * / %`, `abs()`, `min()`, `max()`, `sum()`; `linear(*this, IntArgs(c), xs, IRT_LQ, k)` (weighted sum; `IRT_EQ`, `IRT_NQ`, `IRT_LE`, `IRT_GQ`, `IRT_GR`)
- **Other constraints:**
  - counting: `distinct(*this, xs)`; `count(*this, xs, v, IRT_EQ, c)`
  - indexing/extensional: `element(*this, IntArgs(arr), idx, res)` (res = arr[idx], 0-based); `TupleSet ts(arity); ts.add(IntArgs({...})); ts.finalize(); extensional(*this, xs, ts)`
  - ordering: `rel(*this, xs, IRT_LQ)` (non-decreasing); `lex(*this, xs, IRT_LQ, ys)`
  - graph: `circuit(*this, succ)`
  - scheduling: `cumulative(*this, cap, starts, IntArgs(dur), IntArgs(use))`; `unary(*this, starts, IntArgs(dur))`
- **Objectives and solving:** derive from `IntMaximizeSpace` / `IntMinimizeSpace` with `IntVar cost() const override`; `BAB<M> e(new M)` (last `e.next()` is optimal); satisfaction: derive from `Space`, `DFS<M> e(new M); M* s = e.next();`; values: `s->x.val()`, `std::cout << s->xs`; link `-lgecodesearch -lgecodeminimodel -lgecodeint -lgecodekernel -lgecodesupport`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `IntVar(*this, IntSet(IntArgs({1, 4, 7})))` or `dom(*this, x, IntSet(...))`
- **Structure:** tour or path: successor variables, each restricted to its allowed neighbours, with `circuit(*this, IntArgs(cost), succ, total)` (cost flat n×n; a path adds a dummy node that closes the cycle), not a position sequence with `abs`/`||` move tests; row patterns: `REG z(0), o(1); extensional(*this, xs, DFA(*z + o + +z + o + *z))`; resources: `cumulative`
- **Lookups:** `element(*this, IntArgs(row_i), succ[i], leg[i])` per row, not a computed flat index; a product of two variables where one has a small domain: split on its values, `rel(*this, (l == k) >> (c == k * p))`
- **Symmetry:** order interchangeable objects, `rel(*this, xs, IRT_LE)`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)
- **Search:** branch first on the variables that decide the rest (successors, production levels), `INT_VAR_SIZE_MIN()`; one `branch` per array, in that order

Docs: https://www.gecode.org/doc-latest/reference/
