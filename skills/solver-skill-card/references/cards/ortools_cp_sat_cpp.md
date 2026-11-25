# OR-Tools CP-SAT (C++) — C++17, lazy-clause-generation CP-SAT solver over integer and Boolean variables

## Minimal working example (knapsack)
```cpp
#include <iostream>
#include <vector>
#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
using namespace operations_research::sat;
int main() {
  CpModelBuilder model;
  std::vector<int64_t> values = {6, 10, 12}, weights = {1, 2, 3};
  int64_t capacity = 5;
  std::vector<BoolVar> x;
  for (int i = 0; i < 3; ++i) x.push_back(model.NewBoolVar());
  model.AddLessOrEqual(LinearExpr::WeightedSum(x, weights), capacity);
  model.Maximize(LinearExpr::WeightedSum(x, values));
  const CpSolverResponse r = Solve(model.Build());
  std::cout << r.objective_value() << " " << SolutionBooleanValue(r, x[0]) << SolutionBooleanValue(r, x[1]) << SolutionBooleanValue(r, x[2]) << std::endl;
}
```

## API
- **Decision variables:** `model.NewIntVar(Domain(lb, ub))` (needs `using operations_research::Domain;`); `Domain::FromValues({1, 4, 7})` (`.Complement()`); `model.NewBoolVar()`; `model.NewConstant(c)`; `b.Not()` (negated literal, for BoolVar only); `x.index()`. Expressions: `LinearExpr e = 2 * a + b - c; e += x;` (int64 coefficients; `BoolVar`s too); `LinearExpr::Sum(vars)`; `LinearExpr::WeightedSum(vars, coeffs)`. `vars` is a `std::vector<IntVar>` or `std::vector<BoolVar>`; constraints taking `LinearExpr` spans need a `std::vector<LinearExpr>`
- **Logic constraints:** `AddBoolOr({l1, l2.Not()})`; `AddBoolAnd({...})`; `AddImplication(a, b)`; `AddExactlyOne({...})` (literals must be `BoolVar`); `AddEquality(x, 5).OnlyEnforceIf(b)` or `.OnlyEnforceIf({b, c.Not()})` (one-way `b ⇒ constraint`; `b` false leaves it free; works on any constraint)
- **Arithmetic constraints:** `AddEquality`, `AddNotEqual`, `AddLessOrEqual`, `AddLessThan`, `AddGreaterOrEqual`, `AddGreaterThan` `(expr, expr)`; `AddLinearConstraint(expr, Domain(lo, hi))`; `AddMultiplicationEquality(t, {a, b})`; `AddModuloEquality(t, a, m)`; `AddAbsEquality(t, e)`; `AddMinEquality(t, vars)`; `AddMaxEquality(t, vars)`
- **Other constraints:**
  - counting: `AddAllDifferent(vars)`
  - indexing/extensional: `AddElement(idx, std::vector<int64_t>{...}, target)` (target = values[idx], 0-based); `AddElement(idx, std::vector<LinearExpr>{...}, target)`; `AddVariableElement(idx, vars, target)`; `TableConstraint t = AddAllowedAssignments(vars); t.AddTuple({0, 1});`; `AutomatonConstraint au = AddAutomaton(vars, start, std::vector<int>{finals}); au.AddTransition(from, to, label);`
  - graph: `CircuitConstraint c = AddCircuitConstraint(); c.AddArc(tail, head, lit);` (nodes 0..n-1, one literal per allowed arc; a self-loop arc `(i, i, lit)` means node i is skipped)
  - scheduling: `NewIntervalVar(start, size, end)`; `NewFixedSizeIntervalVar(start, size)`; `NewOptionalIntervalVar(start, size, end, present)`; `AddNoOverlap(intervals)`; `CumulativeConstraint cu = AddCumulative(cap); cu.AddDemand(iv, d);`; `NoOverlap2DConstraint o = AddNoOverlap2D(); o.AddRectangle(x_iv, y_iv);`
- **Objectives and solving:** `model.Minimize(expr)` / `model.Maximize(expr)` (integer expression); `Solve(model.Build())` returns a `CpSolverResponse`: `r.status()` (`CpSolverStatus::OPTIMAL`, `FEASIBLE`, `INFEASIBLE`), `r.objective_value()`, `SolutionIntegerValue(r, x)`, `SolutionBooleanValue(r, b)`; link `ortools::ortools` (CMake `find_package(ortools CONFIG)`)

## Modelling
- **Domains:** the tightest `Domain(lo, hi)` from the data; every variable in a product, division or modulo needs finite bounds; a set of allowed values: `NewIntVar(Domain::FromValues(vals))` or `AddLinearConstraint(x, Domain::FromValues(vals))`; forbidden values: `AddLinearConstraint(x - y, Domain::FromValues({-1, 1}).Complement())`
- **Structure:** `AddAllDifferent` for distinctness; tour or path: one literal per allowed arc in `AddCircuitConstraint` (skipped nodes via self-loop arcs), not position variables with move tests; resources: intervals with `AddNoOverlap` / `AddCumulative` / `AddNoOverlap2D`; patterns: `AddAutomaton`; small allowed or forbidden relations: `AddAllowedAssignments` instead of reified disjunctions; choose one of n: Boolean per option with `AddExactlyOne` and linear sums over those Booleans
- **Lookups:** `AddElement(idx, std::vector<int64_t>{row...}, leg)` per constant row, not a computed flat index; Boolean times a bounded value: `AddEquality(y, v).OnlyEnforceIf(b)` and `AddEquality(y, 0).OnlyEnforceIf(b.Not())`, not `AddMultiplicationEquality`
- **Symmetry:** order interchangeable objects, `AddLessThan(x[i], x[i + 1])`, and fix the first
- **Implied constraints:** add totals the solver cannot infer, e.g. `AddEquality(LinearExpr::Sum(vars), total)` or `AddLessOrEqual` on capacities; a channel `b ⇔ (x == v)`: `AddEquality(x, v).OnlyEnforceIf(b)` plus `AddNotEqual(x, v).OnlyEnforceIf(b.Not())`

Docs: https://developers.google.com/optimization/cp
