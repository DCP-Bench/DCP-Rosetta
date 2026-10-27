# Chuffed in C++ (native API)

Chuffed's C++ API is raw: the global solver state **is** the model, so `createVars`, `int_linear`,
`all_different`, ... post straight into it. **There are no expressions**: every intermediate value (a sum,
a difference, a count, the objective) is its own `IntVar` with a defining constraint, and **one process
solves once** (the globals cannot be reset). Shared concepts, outcomes and enumeration strategy:
[SKILL.md](../../SKILL.md).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Program shape](#program-shape)
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Hard instances](#hard-instances) · [Common issues](common-issues.md) · [Further reading](#further-reading)
- Every call, signature and recipe: [references/cpp/api-cheatsheet.md](../../references/cpp/api-cheatsheet.md);
  search and performance lessons: [references/cpp/performance.md](../../references/cpp/performance.md)
- Runnable examples: [queens](../../assets/cpp/queens/README.md) (satisfy, all solutions, none),
  [knapsack-maximise](../../assets/cpp/knapsack-maximise/README.md),
  [make-change-all-optimal](../../assets/cpp/make-change-all-optimal/README.md),
  [project-schedule](../../assets/cpp/project-schedule/README.md) (scheduling, minimise),
  [graph-colouring-json](../../assets/cpp/graph-colouring-json/README.md) (JSON input, minimise),
  [pigeonhole-infeasible](../../assets/cpp/pigeonhole-infeasible/README.md),
  [derived-quantities](../../assets/cpp/derived-quantities/README.md), [globals-tour](../../assets/cpp/globals-tour/README.md)

## Install

Chuffed has no package for its C++ library (the `fzn-chuffed` binary shipped with
MiniZinc is not it): build it from source with CMake, which installs a CMake package.
Needs a C++17 compiler, CMake and make. Source and build notes: [github.com/chuffed/chuffed](https://github.com/chuffed/chuffed#readme)

```bash
git clone --depth 1 https://github.com/chuffed/chuffed.git   # or a release tag: --branch <tag>
cmake -S chuffed -B chuffed/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HOME/.local/chuffed"
cmake --build chuffed/build -j"$(nproc)" && cmake --install chuffed/build
export CMAKE_PREFIX_PATH="$HOME/.local/chuffed"               # where find_package looks
ls "$CMAKE_PREFIX_PATH/lib/cmake/chuffed/chuffed-config.cmake" # verify
```

`CMakeLists.txt` for a program `model.cpp` (every example has one):

```cmake
cmake_minimum_required(VERSION 3.18)
project(model LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(chuffed CONFIG REQUIRED)
find_package(Threads REQUIRED)
add_executable(model model.cpp)
target_include_directories(model PRIVATE ${CHUFFED_INCLUDE_DIRS})
target_link_libraries(model PRIVATE chuffed chuffed_fzn chuffed Threads::Threads)
```

`chuffed` is listed twice on purpose (static library cycle). Build Release:
`cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build`.

## Quick start

```cpp
// Two numbers x < y in 0..10 that sum to 10.
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>
#include <iostream>

class Pair : public Problem {
 public:
  vec<IntVar*> xy;
  Pair() {
    createVars(xy, 2, 0, 10);
    int_linear(xy, IRT_EQ, 10);         // x + y = 10
    int_rel(xy[0], IRT_LT, xy[1]);      // x < y
    branch(xy, VAR_INORDER, VAL_MIN);   // always branch on the decisions
  }
  void print(std::ostream& os) override {  // variables are fixed only here
    os << "x = " << xy[0]->getVal() << ", y = " << xy[1]->getVal() << "\n";
  }
};

int main() {
  so.print_sol = true;                  // call print() per solution
  engine.solve(new Pair());
  std::cout << (engine.solutions > 0 ? "solved" : "no solution") << std::endl;
}
```

Prints `x = 0, y = 10`, then Chuffed's own `----------`, then `solved`.

## Program shape

- Headers: `<chuffed/{branching/branching,core/engine,core/options,globals/globals,primitives/primitives,support/vec,vars/int-var,vars/modelling}.h>`; everything is in the global namespace. Template: [examples/template.cpp](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/examples/template.cpp).
- Subclass `Problem`, post the model in the constructor (order: variables, constraint blocks, `branch`, `optimize`), and **always** override `void print(std::ostream&)`: it is pure virtual, so a subclass without it does not compile, even when the output comes from a callback. Use an empty body if `print` is unused.
- `main`: set options on the global `so`, then `engine.solve(new P(...))`; afterwards read `engine.status`, `engine.solutions`, `engine.best_sol`.
- Values: `x->getVal()` (IntVar), `b.getVal()` (BoolView, 0/1) only inside `print` or the solution callback, where all branched variables are fixed.
- `engine.setSolutionCallback(f)`, `f` a `std::function<void(Problem*)>` (a lambda), runs per solution, also with `so.print_sol = false`, and per improving solution during `optimize`.
- One solve per process. To solve twice (all optimal solutions), `fork()` or run the program twice: [make-change-all-optimal](../../assets/cpp/make-change-all-optimal/README.md).
- Log to stderr: Chuffed prints solutions and its markers to stdout.


## Modelling

Signatures, semantics and recipes: [references/api-cheatsheet.md](../../references/cpp/api-cheatsheet.md);
headers: [primitives.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/primitives/primitives.h), [globals.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/globals/globals.h).

| Need | API |
|---|---|
| integer variables (bounds required) | `createVars(vec, n, lo, hi[, eager])`, `newIntVar(lo, hi)`, `createVar(v, lo, hi, true)` |
| Booleans | `newBoolVar()`, `createVars(vecBool, n)`; to integers `bool2int(b, x01)` |
| constant as a variable | `getConstant(k)` |
| `x rel y + c`, `x rel c` | `int_rel(x, IRT_LE, y, c)`, `int_rel(x, IRT_NE, c)` |
| (weighted) sum | `int_linear(coefs, xs, IRT_EQ, result)`; count of BoolViews `bool_linear(bs, rel, y)` |
| arithmetic | `int_plus`, `int_minus`, `int_times`, `int_div`, `int_abs`, `int_min`, `int_max`, `minimum`, `maximum` |
| reification / implication | `int_rel_reif(x, rel, y, b[, c])`, `int_rel_half_reif`, `int_linear(..., b)`, `bool_clause(pos, neg)`, `array_bool_and/or` |
| all different (with offsets) | `all_different(xs)`, `all_different_offset(offsets, xs)` |
| element | `array_int_element(i, table, y, offset)`, `array_var_int_element_bound` |
| table / regular | `table(xs, tuples)`, `regular(xs, q, s, dfa, q0, accepting)` |
| circuit / inverse / lex | `circuit(succ)`, `inverse(x, y, o1, o2)`, `lex(a, b, strict)` |
| scheduling | `disjunctive(start, dur)`, `cumulative(start, dur, demand, cap)`, `cumulative2` |
| read data from a file | nlohmann/json, copied into `vec` with `push`: [graph-colouring-json](../../assets/cpp/graph-colouring-json/README.md) |
| search | `branch(vecIntVar, VAR_..., VAL_...)` on the decisions |
| minimise / maximise | `optimize(obj, OPT_MIN)` / `OPT_MAX`, once, on one integer `IntVar` |

Rules that keep models compiling and correct (symptoms in [Common issues](common-issues.md)):

- Constraints take `vec<...>&` non-const lvalues: no `std::vector`, initializer list or temporary. Declare `vec<IntVar*> t; t.push(a); t.push(b);` first; same for `vec<int>`. Build rows of a `vec<vec<>>` in place: `m.push(); m.last().push(x);` or `createVars(m.last(), ...)`.
- No operators on `IntVar*`: one `IntVar` per intermediate, posted with `int_linear`/`int_plus`/`int_times`. Its domain must hold every value it can take, or the model turns infeasible.
- Tight domains from the data. Domains within ±500,000,000 and sums within 32-bit `int`; a value that can exceed this (a 10-digit number) must be split into digits or blocks.
- Prefer globals (`all_different`, `table`, `circuit`, `cumulative`) over decompositions and one `int_linear`/`bool_linear` over hand-built sums or chains of `int_plus`.
- Eager variables (`true` last in `createVars`/`createVar`) for 0/1 and small domains you reify or read with `getLit`; they cost memory on large domains.
- Style: open the file with a line stating the problem, comment each constraint block with the problem's own words (`// all rows must have different values`), name variables in its vocabulary, and say where a bound comes from or where an encoding works around a Chuffed limit. Test on a second data set.


## Solving

Header: [core/engine.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/core/engine.h), options: [core/options.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/core/options.h).

| After `engine.solve` | Meaning |
|---|---|
| `RES_SAT` | stopped at `so.nof_solutions`; more solutions may exist |
| `RES_GUN` | search complete (satisfaction): `engine.solutions` is all of them, 0 = infeasible |
| `RES_LUN` | optimisation complete: the last solution is optimal, `engine.best_sol` is its objective |
| `RES_UNK` | time out (`so.time_out`): an optimisation's last solution is only the best found |
| no return | failure at the root (while posting or before search): Chuffed prints `=====UNSATISFIABLE=====`, `% Top level failure!` and calls `exit(0)`; catch it with `std::atexit` and a flag, see [pigeonhole-infeasible](../../assets/cpp/pigeonhole-infeasible/README.md) |

- Stdout markers: `----------` after each printed solution, `==========` when the search is complete, `=====UNSATISFIABLE=====` when none exists. They are printed even with `so.print_sol = false`.
- Optimisation keeps improving until proven, whatever `so.nof_solutions`; with `so.print_sol` each improving solution is printed, the last one is the optimum.
- Options (fields of `so`, set before `engine.solve`): `nof_solutions` (default 1, 0 = all), `time_out = std::chrono::milliseconds(ms)`, `print_sol`, `vsids`, restarts (`restart_type`, `restart_scale`, `toggle_vsids`, `sat_polarity`, `branch_random`; see [references/performance.md](../../references/cpp/performance.md)). `parseOptions(argc, argv)` reads Chuffed's own CLI flags and can exit on unknown ones: do not use it on your program's arguments.
- A process exit code of 0 says nothing about the result: check the status or the flag.


## All solutions

Declare `output_vars(vec)` on the variables that tell solutions apart and set
`so.nof_solutions = 0`; without `output_vars` search ends after the first solution.
Solutions are distinct on those variables. Example: [queens](../../assets/cpp/queens/README.md).

**All optimal solutions** need two solves, so two processes: minimise or maximise in a
`fork()`ed child that sends `engine.best_sol` back through a pipe; then build the model
again with `int_rel(obj, IRT_EQ, best)`, **no** `optimize`, `output_vars` on the
decisions, and enumerate: [make-change-all-optimal](../../assets/cpp/make-change-all-optimal/README.md).
Flush `std::cout` before `fork()`.

**One printed optimum**: `print` runs for every improving solution, so the output shows
several. To print only the optimum, keep `so.print_sol = false`, copy the values in the solution
callback (it runs for each improving solution) and print once after the solve: the recipe is in
[the cheat sheet](../../references/cpp/api-cheatsheet.md#recipes).


## Hard instances

Branch first on the structural decisions everything else follows from; try `VAR_SIZE_MIN`
or `VAR_ACTIVITY` when `VAR_INORDER` stalls; derive tight domains and objective bounds from
the data; turn on Luby restarts for heavy-tailed search (`so.restart_type = LUBY;
so.restart_scale = 1000; so.toggle_vsids = true; so.sat_polarity = 2;`). Measured cases
and the reasoning behind each: [references/performance.md](../../references/cpp/performance.md).


## Further reading

- Source, README and build notes: <https://github.com/chuffed/chuffed>
- Headers (the API reference): <https://github.com/chuffed/chuffed/tree/0.14.0/chuffed> (`primitives/`, `globals/`, `vars/`, `branching/`, `core/`)
- Official C++ examples: <https://github.com/chuffed/chuffed/tree/0.14.0/chuffed/examples> (`queens.cpp`, `golomb.cpp`, `rcpsp.cpp`, `shift.cpp`)

