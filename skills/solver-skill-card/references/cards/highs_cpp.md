# HiGHS (C++) — C++, linear and mixed-integer linear programming (branch and cut)

## Minimal working example (knapsack)
```cpp
#include <cmath>
#include <iostream>
#include <vector>
#include "Highs.h"
int main() {
  std::vector<double> values = {6, 10, 12}, weights = {1, 2, 3};
  double capacity = 5;
  Highs h;
  h.setOptionValue("output_flag", false);
  for (int i = 0; i < 3; i++) {
    h.addVar(0, 1);
    h.changeColIntegrality(i, HighsVarType::kInteger);
    h.changeColCost(i, values[i]);
  }
  h.changeObjectiveSense(ObjSense::kMaximize);
  std::vector<HighsInt> idx = {0, 1, 2};
  h.addRow(-kHighsInf, capacity, 3, idx.data(), weights.data());
  h.run();
  const std::vector<double>& x = h.getSolution().col_value;
  std::cout << std::llround(h.getInfo().objective_function_value) << " " << std::llround(x[0]) << std::llround(x[1]) << std::llround(x[2]) << std::endl;
}
```

## API
- **Decision variables:** `h.addVar(lb, ub)` appends a continuous column (index = `h.getNumCol()` before the call; `-kHighsInf`/`kHighsInf` for no bound); `h.changeColIntegrality(j, HighsVarType::kInteger)` makes it integer (binary = integer in [0,1]); `h.addVars(n, lbs.data(), ubs.data())`; `h.changeColsIntegrality(n, idx.data(), types.data())`; `h.changeColBounds(j, lb, ub)`
- **Linear constraints:** `h.addRow(lo, hi, n, idx.data(), coef.data())` adds `lo <= Σ coef[k]·x[idx[k]] <= hi` (`idx` is `std::vector<HighsInt>`, `coef` `std::vector<double>`; `==` is `lo == hi`; `<=` is `lo = -kHighsInf`; no `<`, `>`, `!=`; no products, logic, indicator or global constraints: everything is linear rows over columns)
- **Objectives and solving:** `h.changeColCost(j, c)` (sets, not adds; default 0); `h.changeObjectiveOffset(k)`; `h.changeObjectiveSense(ObjSense::kMinimize)` (default) or `kMaximize`; `h.run()`; `h.getModelStatus()` compared with `HighsModelStatus::kOptimal` (also `kInfeasible`, `kTimeLimit`); `h.modelStatusToString(s)`; `h.getSolution().col_value` (`std::vector<double>`: `std::llround` it); `h.getInfo().objective_function_value` (includes the offset)
- **Options:** `h.setOptionValue("output_flag", false)`; `"time_limit"` (double), `"threads"` (int), `"mip_rel_gap"` (double), `"random_seed"` (int); wrong option names return `HighsStatus::kError`

## Modelling
- **Domains:** the tightest `addVar(lb, ub)` the data allows (bounds set the strength of every big-M); a choice among few values: binaries `y[i][v]` with `Σ_v y[i][v] = 1` and `x[i] = Σ v·y[i][v]`
- **Structure:** all-different: one-hot assignment, `Σ_i y[i][v] <= 1` per value; strict `a < b` on integers is `a - b <= -1`; tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `o[i] - o[j] + M·go[i][j] <= M - 1`
- **Implications:** `b ⇒ e <= k` is the row `e + (emax - k)·b <= emax` with the smallest valid `emax` (upper bound of `e`); a product `z = a·b` of binaries: rows `z - a <= 0`, `z - b <= 0`, `z - a - b >= -1`
- **Costs:** weight binaries directly with `changeColCost` or in sums; pick constants in C++ loops, never as variable-indexed lookups
- **Symmetry:** order interchangeable objects (`o[i] - o[i+1] <= -1`) and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand) to tighten the relaxation

Docs: https://ergo-code.github.io/HiGHS/stable/interfaces/cpp/
