# Gecode in C++ (libgecode, Gecode 6.2)

The native API: Gecode is written in C++, and every feature is available here. What holds in
every interface (concepts, outcomes, enumeration strategy) is in [SKILL.md](../../SKILL.md).

A model is a `Space` subclass: variables are members, constraints are posted in the
constructor, and search **copies** the space, so every member is updated in the copy
constructor. Docs: [Modeling and Programming with Gecode (MPG)](https://www.gecode.org/doc-latest/MPG.pdf),
the guide; [reference for 6.2.0](https://www.gecode.org/doc/6.2.0/reference/).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Constraint map](constraint-map.md)
- [Solving and statuses](#solving-and-statuses) · [All solutions](#all-solutions) · [Common issues](#common-issues)
- References: [modelling.md](../../references/cpp/modelling.md) (variables, arrays, data, MiniModel, propagation levels), [search.md](../../references/cpp/search.md) (branching, restarts, implied constraints, symmetry), [constraints.md](../../references/cpp/constraints.md) (every post function), [catalogue.cpp](../../references/cpp/catalogue.cpp) (51 globals checked against brute force)
- Examples: [satisfy](../../assets/cpp/satisfy-send-more-money/README.md), [all solutions](../../assets/cpp/all-solutions-queens/README.md), [all optimal](../../assets/cpp/all-optimal-committee/README.md), [maximise](../../assets/cpp/maximise-knapsack/README.md), [minimise](../../assets/cpp/minimise-seating/README.md), [infeasible](../../assets/cpp/infeasible-pigeonhole/README.md), [scheduling](../../assets/cpp/scheduling-machines-crew/README.md), [job shop](../../assets/cpp/jobshop-ft06/README.md), [JSON input](../../assets/cpp/json-roster/README.md)

## Install

Debian/Ubuntu ([package](https://packages.debian.org/bookworm/libgecode-dev); ask before `sudo`):

```bash
sudo apt install g++ libgecode-dev nlohmann-json3-dev   # nlohmann only for JSON input
g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset \
    -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model
```

Headers land in `/usr/include/gecode`, libraries on the system path: no `-I`, `-L` or
`LD_LIBRARY_PATH` needed. Keep the library order above (dependants before
dependencies). macOS: `brew install gecode` ([formula](https://formulae.brew.sh/formula/gecode),
not tested here; add `-I`/`-L` for the Homebrew prefix). Other systems: build from
[source](https://github.com/Gecode/gecode) ([download page](https://www.gecode.org/download.html)).
Verify with the Quick start: it prints `Profit: 12 at x = 4, y = 0`.

## Quick start

```cpp
// Maximise 3x + 2y for integers 0 <= x, y <= 4 with x + y <= 4 and x + 3y <= 6.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
using namespace Gecode;

class Plan : public IntMaximizeSpace {     // IntMinimizeSpace to minimise; Space to satisfy
 protected:
  IntVar x, y, profit;                      // everything read later is a member
 public:
  Plan() : x(*this, 0, 4), y(*this, 0, 4) {
    rel(*this, x + y <= 4);
    rel(*this, x + 3 * y <= 6);
    profit = expr(*this, 3 * x + 2 * y);    // a fresh IntVar with bounds from the expression
    branch(*this, IntVarArgs({x, y}), INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Plan(Plan& s) : IntMaximizeSpace(s) {     // update EVERY variable member
    x.update(*this, s.x); y.update(*this, s.y); profit.update(*this, s.profit);
  }
  Space* copy() override { return new Plan(*this); }
  IntVar cost() const override { return profit; }   // the objective BAB improves
  void print() const { std::cout << "Profit: " << profit.val() << " at x = " << x.val() << ", y = " << y.val() << "\n"; }
};

int main() {
  Plan* root = new Plan;
  BAB<Plan> engine(root);                   // the engine searches its own clone
  delete root;
  Plan* best = nullptr;
  while (Plan* s = engine.next()) { delete best; best = s; }  // each one strictly better
  if (!best) { std::cout << (engine.stopped() ? "Stopped before a solution\n" : "No solution\n"); return 0; }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
}
```

## Modelling

Find a row of the [constraint map](constraint-map.md) for each sentence of the description.
A decomposition is right only when no row fits.

## Solving and statuses

[Search engines](https://www.gecode.org/doc/6.2.0/reference/group__TaskSearch.html):
`DFS<T>` (satisfy, enumerate), `BAB<T>` (optimise; `T` derives from `IntMinimizeSpace`
/ `IntMaximizeSpace` and overrides `IntVar cost() const`), `RBS<T, DFS>` / `RBS<T, BAB>`
(restarts, `opts.cutoff = Search::Cutoff::luby(scale)`). The engine clones the root, so
`delete` it after constructing the engine. [Options](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Search_1_1Options.html):
`opts.threads` (1 = deterministic), `opts.stop = Search::Stop::time(ms)` (also
`Search::Stop::node(n)`, `fail(n)`, [stop objects](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelSearchStop.html)).
Gecode has no status enum; read it from these:

| What you see | Meaning |
|---|---|
| `root->status() == SS_FAILED` before search | infeasible, proven by propagation alone |
| `next()` returns a space | a solution (BAB: strictly better than the previous one); read `x.val()` |
| `next()` returns `nullptr`, `engine.stopped()` false | search exhausted: no more solutions; for BAB the last solution is **optimal**, none at all means **infeasible** |
| `next()` returns `nullptr`, `engine.stopped()` true | a stop object fired: the last BAB solution is feasible, not proven; none means unknown |

`engine.statistics()` gives `node`, `fail`, `depth`. Errors: compile errors come from
g++ (long template messages; read the first `error:`); run-time errors are C++
exceptions derived from `Gecode::Exception`, uncaught they print
`terminate called after throwing an instance of 'Gecode::Int::OutOfLimits'` plus
`what()` on stderr and abort (exit 134). Buffered `std::cout` output is lost on abort.

## All solutions

`DFS` returns each solution once per assignment of the **branched** variables: loop on
`next()` until `nullptr` ([all-solutions-queens](../../assets/cpp/all-solutions-queens/README.md)).
Branch only on the variables whose values define a solution, and make every auxiliary
functionally determined by them (otherwise see [Common issues](#common-issues)). **All
optimal solutions**: prove the optimum with `BAB`, then build a fresh space with
`rel(*this, cost == optimum)` and enumerate it with `DFS`. `BAB` keeps requiring each
solution to beat the last, so it never yields a second solution of equal cost. The fresh
space can be the same class, given the optimum through its constructor (a default of -1
means optimise), as [all-optimal-committee](../../assets/cpp/all-optimal-committee/README.md) does.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Garbage values or a crash after search; constraints silently ignored | A member missing from the copy constructor | Update every `IntVarArray`, `IntVar`, `BoolVar*`, `SetVar*` member |
| A "solution" violates a constraint, or `val()` throws `Attempt to access value of unassigned variable` | A solution is reported once every brancher is done; an auxiliary no branching and no propagation fixes stays open (a weak propagator may still be alive: `PropagatorGroup::all.size(*s) > 0`) | Branch on every decision variable, auxiliaries last ([search.md](../../references/cpp/search.md)) |
| Crash at run time right after construction | `IntVarArray(*this, n)` / `BoolVarArray(*this, n)` leave variables unset | Always give bounds: `IntVarArray(*this, n, lo, hi)` |
| `Int::OutOfLimits` (`Number out of limits`) | Bounds beyond ±(2^31 − 2) (`Int::Limits::max` = 2147483646), or overflowing products of large domains | Bound intermediates; split wide numbers into digit variables |
| Values read after copy are stale | An `IntVarArgs` kept as a member is not updated on copy | Keep an `IntVarArray` member |
| `(x == 1) + (y == 1)` does not compile | Relations are not numbers | `count`, or sum `expr(*this, x == 1)` BoolVars |
| A `BoolVar` rejected by `IntVarArgs`, `mult`, `count`'s count argument | A `BoolVar` is not an `IntVar` | `channel(*this, b, x)` with x in 0..1, or declare 0/1 `IntVar`s; MiniModel mixes them freely |
| `IntSet(v)` on a vector, `IntArgs(n, v)` do not compile | No such overloads | `IntSet(IntArgs(v))`; `IntArgs::create(n, v, 0)` for n copies of v |
| `TupleSet t;` throws on `add`; table ignored | No arity, or not finalised | `TupleSet t(arity)`, then `t.finalize()` before posting |
| `path`/`circuit` fails at once | Wrong domain | `circuit` over n nodes: domain 0..n−1; `path`: `succ[e] = n` |
| One-hot `channel(bools, v, o)` gives no "none" choice | It makes exactly one Boolean true, `v` in o..o+n−1 | Give "none" its own Boolean (index 0, offset 0) |
| gcc `count(x, cards, vals)` removes values | It forces every `x_i` into `vals` | List every value x may take, cardinality `IntSet(0, n)` for free ones |
| `rel(home, b, BOT_AND, ...)` rejects a relation | Takes Booleans only | `rel(*this, b == ((x < y) && (u < v)))`, `expr(*this, a && b)` |
| Odd compile error at `count(...)`, `sum(...)`, `element(...)` | A member or local named `count`, `sum`, `min`, `max`, `element`, `path`, `circuit`, `sequence` or `rel` hides the Gecode function | Rename it |
| Memory exhausted at posting | `IPL_DOM` on a product of two large domains (10^4 values) | Default level on arithmetic |
| All-optimal run returns one solution, never a second one of equal cost | `BAB` only reports strictly better solutions | Enumerate with `DFS` on a space with `rel(*this, cost == optimum)` ([All solutions](#all-solutions)) |
| `engine.stopped()` is true on a small problem: the answer is unknown or the list incomplete | A time, node or fail limit fired before the search ended | [Limits](../../references/cpp/search.md#limits): change the search style or raise the limit |
| Slow, or no first solution / optimum not proven | Weak propagation or branching | [search.md](../../references/cpp/search.md): implied constraints, branching order, restarts |
| `FloatVar` model slow or inexact | Floats are slow and inexact | Scale to integers |
| Values read from a failed space | — | Check `status()` before reading |

`sequence` and a few other globals stay alive at solutions; that is harmless once all
branched variables are assigned.

