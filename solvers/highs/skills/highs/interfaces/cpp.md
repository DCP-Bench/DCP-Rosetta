# HiGHS in C++ (the `Highs` class)

The native C++ API of HiGHS, built from source. What holds in every interface (concepts,
linearisation patterns, the gap rule for proven optimality, what the model statuses mean, enumeration strategy) is in [SKILL.md](../SKILL.md).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Solving](#solving)
- [All solutions](#all-solutions) · [Common issues](#common-issues) · [Further reading](#further-reading)
- Examples: [assignment](../assets/cpp/satisfy-assignment/README.md), [all solutions](../assets/cpp/all-solutions-no-good/README.md),
  [knapsack](../assets/cpp/maximise-knapsack/README.md), [scheduling](../assets/cpp/minimise-big-m-scheduling/README.md),
  [abs, max, product](../assets/cpp/min-max-abs-product/README.md), [all different](../assets/cpp/alldifferent-binaries/README.md),
  [infeasible](../assets/cpp/infeasible-status/README.md), [JSON data](../assets/cpp/json-data/README.md)

Docs: [C++ interface](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/library.md)
(source in the repository, v1.15.1), [class declaration](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h),
[options with defaults](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h),
[status enums](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HConst.h).

## Install

Build HiGHS from source (needs git, CMake 3.15+, a C++17 compiler). Tested with v1.15.1 (commit `04024d7`), g++ 12.2:

```bash
git clone --depth 1 --branch v1.15.1 https://github.com/ERGO-Code/HiGHS.git
cmake -S HiGHS -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HOME/highs" \
      -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF -DBUILD_CXX_EXE=OFF -DZLIB=OFF
cmake --build build -j4 && cmake --install build
export HIGHS_PREFIX="$HOME/highs"
```

Build an example with `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`.
Headers are in `include/highs/`, so include them as `"Highs.h"`. The JSON example also needs `nlohmann-json3-dev`.
Verify: the Quick start prints `Objective: 3`. Docs: [installation](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/installation.md).

## Quick start

```cpp
// Minimise x + 2y over integers 0..4 with x + y >= 3.
#include <cmath>
#include <cstdio>
#include "Highs.h"

int main() {
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("mip_rel_gap", 0.0);            // both gaps 0.0: OPTIMAL then means proven
  h.setOptionValue("mip_abs_gap", 0.0);
  h.addVar(0, 4); h.addVar(0, 4);                  // columns 0 (x) and 1 (y)
  h.changeColIntegrality(0, HighsVarType::kInteger);
  h.changeColIntegrality(1, HighsVarType::kInteger);
  h.changeColCost(0, 1); h.changeColCost(1, 2);
  h.changeObjectiveSense(ObjSense::kMinimize);
  HighsInt cols[2] = {0, 1}; double coefs[2] = {1, 1};
  h.addRow(3, kHighsInf, 2, cols, coefs);          // 3 <= x + y
  h.run();
  if (h.getModelStatus() == HighsModelStatus::kOptimal)
    std::printf("Objective: %.0f\n", std::round(h.getInfo().objective_function_value));
}
```

## Modelling

Start each block of rows with a `//` comment that states the constraint in plain words, not the HiGHS call
(`// every row holds different values`).

Columns are numbered in `addVar` order: the first is 0. Rows take index and value arrays.

| Need | API |
|---|---|
| continuous column | [`addVar(lower, upper)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) (`-kHighsInf`/`kHighsInf` for no bound) |
| integer or binary column | `addVar(0, 1)` then [`changeColIntegrality(col, HighsVarType::kInteger)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| linear row `lo <= sum a_j x_j <= hi` | [`addRow(lo, hi, nnz, index, value)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h); `=` is `lo == hi`, `<=` has `lo = -kHighsInf` |
| objective coefficient | [`changeColCost(col, c)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| minimise / maximise | [`changeObjectiveSense(ObjSense::kMinimize / kMaximize)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| constant in the objective | [`changeObjectiveOffset(d)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h); `getInfo().objective_function_value` includes it |
| change a bound | [`changeColBounds(col, lo, hi)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| number of columns | [`getNumCol()`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) (the next `addVar` returns this) |
| read a column's bounds or integrality back | [`getLp()`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h): `col_lower_`, `col_upper_`, `integrality_` |

Use `kHighsInf` (infinity, `+inf` in double). A row with no entries and bounds that exclude zero makes the model infeasible.
Pass integer counts as `HighsInt` (32-bit in a default build) and bounds as `double`.

## Solving

Status and parameters: [status enum](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HConst.h),
[options](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h).

| `getModelStatus()` | Meaning |
|---|---|
| `kOptimal` | proven optimal when `mip_rel_gap` and `mip_abs_gap` are zero (their defaults are 1e-4 and 1e-6); the solution is in `getSolution().col_value` |
| `kInfeasible` | no solution |
| `kUnboundedOrInfeasible` | a MIP with an unbounded objective is reported this way; solve again with the objective cleared to decide |
| `kUnbounded` | the objective is unbounded |
| `kTimeLimit` | time limit reached before the proof; the result is not proven, so do not report it as optimal |
| `kNotset` | HiGHS stopped at a short time limit before setting a status (seen with a 0.2 s limit); treat as a time limit |
| `kModelEmpty` | the model has no columns; a feasible empty model reports this |

`run()` returns `HighsStatus::kOk` for an infeasible model; check `getModelStatus()`, not `run()`.
Read values with `getSolution().col_value` (doubles: round them, e.g. `std::lround`; a binary is `lround(v) == 1`).
`modelStatusToString(status)` (a `Highs` member, returns `std::string`) gives the status name.

A model with no objective (all costs zero, the default) is a satisfaction problem: `run()` returns any feasible
point and the status is `kOptimal`.

Options used by the examples (`setOptionValue`): `output_flag` (`false`: silent), `threads` (default 0 = automatic; use `HighsInt{1}`),
`mip_rel_gap` and `mip_abs_gap` (set both to `0.0`), `time_limit` (seconds, default infinite), `random_seed` (default 0).
Option defaults come from `HighsOptions.h`, not from the online docs.

## All solutions

The strategy (no-goods, all optimal solutions) is in [SKILL.md](../SKILL.md#all-solutions). Full C++ code in
[the example](../assets/cpp/all-solutions-no-good/README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `kOptimal` but a result is off by a fraction | `mip_rel_gap` default 1e-4 | set `mip_rel_gap` and `mip_abs_gap` to 0 |
| `run()` returns `kOk` but the model is infeasible | status is in the model, not the return value | check `getModelStatus()` |
| `kUnboundedOrInfeasible` on a MIP | HiGHS does not say which | re-solve with the objective set to zero; no solution means infeasible |
| time limit with no proof | LP relaxation weak | tighter big-M, binary formulation, stronger rows |
| a value printed as 2.99999 | solver tolerance (`mip_feasibility_tolerance` default 1e-6) | `std::lround` before printing |
| wrong sign on a maximisation objective | coefficients were set for minimisation | `changeObjectiveSense(ObjSense::kMaximize)` and check the cost signs |
| constant missing from the objective | offset not set | `changeObjectiveOffset` |
| column index out of range | columns numbered in `addVar` order from 0 | use `getNumCol()` before each `addVar` |

## Further reading

- C++ interface guide: [library.md](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/library.md) and [examples.md](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/examples.md)
- Full API: [Highs.h](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h)
- Options and defaults: [HighsOptions.h](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h)
- Example programs: [call_highs_from_cpp.cpp](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/examples/call_highs_from_cpp.cpp)
