# OR-Tools CP-SAT in Python (ortools.sat.python.cp_model)

The Python API of OR-Tools, installed from the `ortools` wheel.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Solving](#solving)
- [All solutions](#all-solutions) · [All optimal solutions](#all-optimal-solutions)
- [Common issues](#common-issues) · [Runnable examples](#runnable-examples)

## Install

```bash
pip install ortools
python3 -c "from ortools.sat.python import cp_model; print(cp_model.__name__)"
```

The package is free and needs no licence. Details: [install guide](https://developers.google.com/optimization/install/python).

## Quick start

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = model.new_int_var(0, 10, "x")
y = model.new_int_var(0, 10, "y")
model.add(x + 2 * y == 14)
model.maximize(x + y)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status == cp_model.OPTIMAL:
    print(solver.status_name(status), solver.value(x), solver.value(y), solver.objective_value)
```

## Modelling

Full API: [CpModel reference](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html).
Each row names its method on `CpModel` unless stated otherwise.

| Need | API |
|---|---|
| integer variable (name is **required**) | `new_int_var(lb, ub, name)` |
| variable with a non-interval domain | `new_int_var_from_domain(cp_model.Domain.from_values([2, 4, 8]), name)` |
| Boolean variable | `new_bool_var(name)`; negation `b.Not()` |
| constant | `new_constant(5)` or plain Python `5` |
| linear constraint | `add(expr <= k)`; `==`, `!=`, `>=` work the same |
| sum / weighted sum | `cp_model.LinearExpr.sum(xs)`, `cp_model.LinearExpr.weighted_sum(xs, ws)`; Python `sum()` also works |
| reification (enforce a constraint when a literal holds) | `add(...).only_enforce_if(b)` |
| at least one / at most one / exactly one | `add_bool_or`, `add_at_most_one`, `add_exactly_one` |
| implication / xor | `add_implication(a, b)`, `add_bool_xor` |
| all different (items may be linear expressions) | `add_all_different(xs)`, e.g. `add_all_different([col[i] + i for i in range(n)])` for the diagonals of n-queens |
| element (`arr[i]` with variable `i`) | `add_element(index, values, target)` (`target == values[index]`) |
| allowed / forbidden tuples | `add_allowed_assignments(vars, tuples)`, `add_forbidden_assignments(vars, tuples)` |
| min / max / abs of expressions | `add_min_equality(target, exprs)`, `add_max_equality(target, exprs)`, `add_abs_equality(target, expr)`: the target comes first |
| product / division / modulo of variables | `add_multiplication_equality(target, [x, y])`, `add_division_equality(target, x, y)`, `add_modulo_equality(target, x, y)`: the target comes first; a divisor whose domain contains 0 makes the model `MODEL_INVALID`, so give it a domain without 0 |
| circuit (Hamiltonian cycle) | `add_circuit(arcs)`, `add_multiple_circuit` |
| interval for scheduling | `new_interval_var(start, size, end, name)`, `new_fixed_size_interval_var(start, size, name)`, `new_optional_interval_var` |
| no two intervals overlap (one list per machine or resource) | `add_no_overlap(intervals)`; worked example: [jobshop-no-overlap](../assets/python/jobshop-no-overlap/README.md) |
| shared resource limit | `add_cumulative(intervals, demands, capacity)`; worked example: [tasks-scheduling](../assets/python/tasks-scheduling/README.md) |
| minimise / maximise | `minimize(expr)`, `maximize(expr)`; `clear_objective()` removes it |
| check the model before solving | `model.validate()` returns `''` when valid, else a message such as `var #0 has no domain(): name: "v"` for a lower bound above the upper bound |

Reading and writing expressions:

| Writing | Result |
|---|---|
| `if x:`, `bool(x == 1)` | `NotImplementedError`: an expression has no truth value; use `add` or `only_enforce_if` |
| `x // 2`, `x / 2`, `x * y` in a constraint | `TypeError`: use `add_division_equality` / `add_multiplication_equality` with an auxiliary variable |
| `x * 0.5` in a constraint | `TypeError`: scale to integers |
| `x in list`, `list.index(x)` | compares by identity; `==` between expressions builds a constraint, it is not a Boolean |

Reading instance data: CP-SAT does not read files. Read them in plain Python and build the
model from the values: `with open(path) as f: data = json.load(f)`, where `path` is given
on the command line (for example `sys.argv[1]`). Size the variables from the data, so the same
program works for any data file. Worked example: [coins-minimise](../assets/python/coins-minimise/README.md).

Minimising the number of distinct values (for example colours): minimise the largest index
with `add_max_equality`. At an optimum the values are `0..k-1`, so the largest index is
`k - 1` and the count is exact. Worked example: [colouring-min-colours](../assets/python/colouring-min-colours/README.md).

Modelling notes: [CP-SAT primer](https://developers.google.com/optimization/cp/cp_solver)
explains the overall approach; the constraint list in the reference above is the complete set.

## Solving

Status values and parameters: [CpSolver reference](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html),
definitions in [cp_model.proto](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto).

| `status` (`cp_model.X`) | `solver.status_name(status)` | Meaning |
|---|---|---|
| `OPTIMAL` | `OPTIMAL` | Solution found and, with an objective, proven optimal. For a satisfaction model, a solution was found |
| `FEASIBLE` | `FEASIBLE` | Solution found, optimality not proven (typically a time limit) |
| `INFEASIBLE` | `INFEASIBLE` | Proven that no solution exists |
| `UNKNOWN` | `UNKNOWN` | Limit reached before anything was found |
| `MODEL_INVALID` | `MODEL_INVALID` | The model is malformed, e.g. `new_int_var(5, 1, "x")` (lower bound above upper bound) |

| Need | Call |
|---|---|
| time limit (seconds) | `solver.parameters.max_time_in_seconds = 10` |
| workers | `solver.parameters.num_workers = 8` (default `0` = automatic) |
| seed | `solver.parameters.random_seed = 7` |
| objective value / proven bound | `solver.objective_value`, `solver.best_objective_bound` |
| value of a variable or expression | `solver.value(x)`, `solver.value(x + y)`; Booleans give `0`/`1`, `solver.boolean_value(b)` gives `bool` |
| many values at once | `solver.values(list_of_vars)` (returns a pandas `Series`; use `list(...)` for a list) |
| run time | `solver.wall_time` |
| summary string | `solver.solution_info()` |

- `solver.value` before `solve` raises `RuntimeError: solve() has not been called`.
- Only read values when `status` is `OPTIMAL` or `FEASIBLE`.
- **Optimisation problems:** the answer is the optimum, so accept only `OPTIMAL`. A `FEASIBLE`
  result is a solution with no proof of optimality; do not report it as the optimum. Either
  raise `max_time_in_seconds` and solve again, or report the status and the gap
  (`objective_value` against `best_objective_bound`) as the outcome. Example:
  `if status != cp_model.OPTIMAL: raise SystemExit(solver.status_name(status))`
  (as in [ties-all-optimal](../assets/python/ties-all-optimal/README.md)).
- **Satisfaction problems:** `OPTIMAL` and `FEASIBLE` both mean a solution is available.
  `INFEASIBLE` is a proof that none exists, not an error.

## All solutions

Enumeration needs a callback; the solver calls it once per solution. Full details:
[enumerate all solutions](https://developers.google.com/optimization/cp/cp_solver#finding_all_solutions).

```python
class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append(tuple(self.value(v) for v in self.variables))

solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
collector = Collect([x, y])
status = solver.solve(model, collector)
print(len(collector.solutions))
```

- Set `solver.parameters.num_workers = 1` with `enumerate_all_solutions`; checked: 8 workers reported 4 of 7 solutions, the default (`0`) and 1 reported all 7.
- Solutions are counted **per assignment of all variables**. An auxiliary variable that takes
  several values for the same values of the variables you report makes duplicates: record
  only the variables you report (as above) and dedupe with `set(...)`, or make auxiliary
  variables fully determined by them.
- **Zero solutions:** the callback is never called and the status is `INFEASIBLE`
  (for example three Booleans with `sum == 5`). Decide "no solutions" from the status, not from
  an empty list. If the status is `UNKNOWN` or `MODEL_INVALID`, the list is not a complete
  answer: report the status instead of the count.
- A finished enumeration of a satisfiable model returns status `OPTIMAL` (checked: 20 solutions of
  `sum == 3` over six Booleans). Do not report a count that a time limit cut short.

## All optimal solutions

Enumeration with an objective still set returns **one** optimal solution, not all of them.
Solve for the optimum, post the objective as a constraint, clear the objective, then enumerate.
This takes two solver objects. `total` is the objective expression, kept in a variable:

```python
total = cp_model.LinearExpr.weighted_sum(take, values)
model.maximize(total)

solver = cp_model.CpSolver()
assert solver.solve(model) == cp_model.OPTIMAL
best = int(solver.objective_value)

model.add(total == best)
model.clear_objective()

enumerator = cp_model.CpSolver()
enumerator.parameters.enumerate_all_solutions = True
collector = Collect(reported)  # the variables you print
enumerator.solve(model, collector)
```

Check the first solve is `OPTIMAL` before using `objective_value`. Worked example:
[ties-all-optimal](../assets/python/ties-all-optimal/README.md). Several objective terms can tie; `total` must be built from the same terms
and weights as the objective, or the equality fixes the wrong value.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `TypeError: new_int_var() missing ... 'name'` | the name argument is required in this version | pass a name string |
| `NotImplementedError` on `if x` or `bool(...)` | using an expression as a Boolean | use `add`, `only_enforce_if` or `.Not()` |
| `TypeError` on `x * y`, `x // k`, `x / k` | nonlinear arithmetic in a linear expression | introduce a variable with `add_multiplication_equality` or `add_division_equality` |
| float coefficient in the objective, e.g. `maximize(z * 0.5 + y * 0.3)` | accepted: CP-SAT stores a floating-point objective and scales it to integers internally (the search log shows `[Scaling] ... worst-case absolute error`), so the proven optimum is exact only up to that error | for an exact integer optimum multiply by a common factor (`maximize(5 * z + 3 * y)`: the same solution is optimal, and the reported objective is then 10 times the original, so divide it by 10 for the true value) |
| `MODEL_INVALID` | e.g. a variable with lower bound above upper bound | `model.validate()` gives the message; fix the bound |
| `RuntimeError: solve() has not been called` | reading values before solving | call `solver.solve(model)` first |
| `FEASIBLE` instead of `OPTIMAL` on an optimisation problem | time limit reached before the proof | raise `max_time_in_seconds` and solve again, or report the status and gap; do not report the value as the optimum |
| enumeration reports nothing | the instance is infeasible: the callback is never called | read the status: `INFEASIBLE` means zero solutions; other statuses mean the list is incomplete |
| too many solutions in enumeration | auxiliary variables multiply solutions | record only the decision variables you print, and dedupe on them |
| only one optimal solution enumerated | objective still set during enumeration | post `objective == best`, then `clear_objective()` |
| enumeration hangs | unbounded variable domain | give every variable finite bounds |
| data read from a file beside the script, not the path given | the file location is chosen by whoever runs the program | open the path argument: `json.load(open(sys.argv[1]))`; see [coins-minimise](../assets/python/coins-minimise/README.md) |
| one `add_no_overlap` over all operations | operations on different machines block each other | build one interval list per machine and one `add_no_overlap` per list; see [jobshop-no-overlap](../assets/python/jobshop-no-overlap/README.md) |
| minimising "number of colours" with no counter | a count of distinct values is not a linear expression | minimise the largest index with `add_max_equality`; see [colouring-min-colours](../assets/python/colouring-min-colours/README.md) |

## Runnable examples

- [sudoku-satisfy](../assets/python/sudoku-satisfy/README.md): satisfy
- [subsets-all-solutions](../assets/python/subsets-all-solutions/README.md): all solutions
- [ties-all-optimal](../assets/python/ties-all-optimal/README.md): all optimal solutions
- [production-maximise](../assets/python/production-maximise/README.md): maximise
- [coins-minimise](../assets/python/coins-minimise/README.md): minimise, reading a JSON instance
- [pigeons-infeasible](../assets/python/pigeons-infeasible/README.md): infeasible
- [tasks-scheduling](../assets/python/tasks-scheduling/README.md): cumulative resource
- [jobshop-no-overlap](../assets/python/jobshop-no-overlap/README.md): one no-overlap per machine
- [colouring-min-colours](../assets/python/colouring-min-colours/README.md): minimise the number of distinct values
