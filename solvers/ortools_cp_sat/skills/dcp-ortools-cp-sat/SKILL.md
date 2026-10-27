---
name: dcp-ortools-cp-sat
description: OR-Tools CP-SAT, Google's constraint programming and integer optimisation solver (propagation with clause learning), used from C++ (CpModelBuilder) or Python (ortools.sat.python.cp_model). Use when writing, debugging or explaining CP-SAT models in either language, including scheduling, assignment, packing, installing OR-Tools, or enumerating all or all optimal solutions.
license: Apache-2.0
compatibility: "C++: a C++17 compiler (tested with g++ 12.2), CMake 3.18+ and the OR-Tools 9.15 C++ binary archive (tested on Debian 12 x86_64). Python: Python 3.10+ and the ortools package (tested with 9.15, Python 3.12). Free and open source, no key or account."
metadata:
  domain: constraint-programming
  solver: ortools-cp-sat
  paradigm: cp
  interfaces: "cpp, python"
---

# OR-Tools CP-SAT

CP-SAT is a finite-domain constraint solver that combines propagation with clause learning. You declare **integer and Boolean variables**, add linear and global constraints, optionally add one objective, then solve. Two rules to keep in mind: every variable has a finite integer domain, and the objective is a linear expression over integers (scale money to whole cents; the Python binding also accepts float coefficients and scales them internally). Products of variables, division and modulo are modelled with a helper constraint; floats are not allowed in constraints.

Official guide: [CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver) ([Markdown](https://developers.google.com/optimization/cp/cp_solver.md)).

## Pick an interface

Read this file, then the one interface file for your language.

| | C++ | Python |
|---|---|---|
| Read | [interfaces/cpp.md](interfaces/cpp.md) | [interfaces/python.md](interfaces/python.md) |
| Package | OR-Tools C++ binary archive, built with CMake (`ortools::ortools`) | `ortools` wheel (`pip install ortools`) |
| Entry point | `CpModelBuilder`, `Solve(model.Build())` | `cp_model.CpModel`, `cp_model.CpSolver` |
| Variable names | none | `new_int_var(lb, ub, name)`: the name is required |
| Reading values | `SolutionIntegerValue(response, expr)` | `solver.value(expr)` |
| Enumerating solutions | a solution observer on a `Model` | a `CpSolverSolutionCallback` subclass |
| Expression syntax | operators on `IntVar`/`LinearExpr`; `AddElement`, `AddAllDifferent` and `AddMaxEquality` need a `std::vector<LinearExpr>` | Python operators; `add(expr <= k)`; an expression has no truth value (`if x:` raises) |
| Reading instance files | no JSON reader in the standard library; nlohmann/json | `json` from the standard library |

Use the language of the user's project; without one, take Python for a quick model and C++ when the program must be compiled.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [C++](interfaces/cpp.md), [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

The calls, with their exact names, are in the interface files; the constraint catalogue is the same in both.

| The problem says | Constraint |
|---|---|
| integer / Boolean variable, domain with holes | bounded `IntVar`, `BoolVar`, a variable from a `Domain` |
| linear (in)equality, weighted sum | linear expression compared with a constant or expression |
| all different (items may be linear expressions) | all-different |
| `arr[i]` with a variable index | element |
| allowed or forbidden tuples, regular language, circuit | table, automaton, circuit constraints |
| min, max, abs, product, division, modulo | `*_equality` helper constraints with a bounded target (Python `add_min_equality`, `add_max_equality`, `add_abs_equality`, `add_multiplication_equality`, `add_division_equality`, `add_modulo_equality`; C++ `AddMinEquality`, `AddMaxEquality`, `AddAbsEquality`, `AddMultiplicationEquality`, `AddDivisionEquality`, `AddModuloEquality`) |
| at least, at most, exactly one; implication | Boolean clause constraints |
| a constraint that holds only when a literal does | reification (`only_enforce_if` / `OnlyEnforceIf`) |
| scheduling | interval variables, no-overlap (one per machine), cumulative, 2-D no-overlap |
| minimise or maximise | at most one objective |

A one-way reification (constraint enforced only when `lit` holds) leaves `lit` free when the constraint does not hold. When `lit` must be an indicator that is true exactly when the condition holds (equivalence), post the constraint under `lit` and its negation under `lit.Not()`. This counts occurrences (`sum(x == v) == k` is a sum of indicators), and a disjunction of constraints is one Boolean-or over their indicators.

Minimising the number of distinct values (for example colours): minimise the largest index with a max constraint. At an optimum the values are `0..k-1`, so the largest index is `k - 1` and the count is exact (Python example: [colouring-min-colours](assets/python/colouring-min-colours/README.md)).

## Solving

Status definitions: [cp_model.proto](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto). Parameters: [sat_parameters.proto](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto).

| Status | Meaning |
|---|---|
| `OPTIMAL` | Solution found; for an optimisation, optimality is proven. For a satisfaction model, a solution was found |
| `FEASIBLE` | Solution found but not proven optimal (typically a time limit) |
| `INFEASIBLE` | Proven: no solution exists; a proof, not an error |
| `UNKNOWN` | Limit reached before any solution or proof |
| `MODEL_INVALID` | The model is malformed, for example a variable with lower bound above upper bound |

Read values only when the status is `OPTIMAL` or `FEASIBLE`. **Optimisation problems:** the answer is the optimum, so accept only `OPTIMAL`; a `FEASIBLE` result is a solution with no proof, so raise the time limit and solve again, or report the status and the gap (objective against best bound) as the outcome. The time limit, number of workers, seed and search log are solver parameters (`max_time_in_seconds`, `num_workers`, `random_seed`, `log_search_progress`).

## All solutions

Enumeration is a solver parameter (`enumerate_all_solutions`) plus a callback that the solver calls once per solution. Use **one worker**: with 8 workers a 6-solution model returned 5 in C++ and a 7-solution model returned 4 in Python.

- Solutions are counted **per assignment of all variables**. An auxiliary variable that takes several values for the same values of the variables you report makes duplicates: enumerate over decision variables only, or make auxiliary variables fully determined by them.
- **Zero solutions:** the callback is never called and the status is `INFEASIBLE`. Decide "no solutions" from the status, not from an empty list. If the status is `UNKNOWN` or `MODEL_INVALID`, the list is not a complete answer: report the status instead of the count.
- A finished enumeration of a satisfiable model returns status `OPTIMAL`. Do not report a count that a time limit cut short.

**All optimal solutions:** an enumeration with an objective still set returns one optimal solution. Solve once for the optimum `z*` (check the status is `OPTIMAL`), then enumerate a model that has the objective expression fixed to `z*` and no objective. The fixed expression must be the same linear expression as the objective.

Details: [enumerate all solutions](https://developers.google.com/optimization/cp/cp_solver#finding_all_solutions)

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Duplicate solutions from enumeration | Auxiliary variables are not fixed by the decision variables | Enumerate decision variables only, or dedupe on them; see [All solutions](#all-solutions) |
| Enumeration returns fewer solutions than exist | More than one worker | One worker with `enumerate_all_solutions` |
| Only one optimal solution enumerated | Objective still set during enumeration | Fix `objective == best` and remove the objective |
| Enumeration reports nothing | The instance is infeasible: the callback is never called | Read the status |
| Indicator takes either value | Reification posted in one direction only | Post the constraint and its negation; see [Modelling](#modelling) |
| `MODEL_INVALID` | Malformed model, e.g. a domain with lower bound above upper bound | Validate the model (the interface file names the call) and fix the bound |
| `FEASIBLE` instead of `OPTIMAL` for an optimisation | Time limit reached; optimality not proven | Raise the limit (C++ `set_max_time_in_seconds`), or report the status and gap; do not report the value as the optimum |
| Product, division or modulo misbehaves or is rejected | Nonlinear arithmetic in a linear expression, or a target with no bounded domain | Use the `*_equality` helper with a bounded `Domain` for the target and each intermediate; chain products two factors at a time |
| Objective with decimal costs | CP-SAT works on integers; a floating-point objective is scaled internally | Multiply costs by 100 (or 1000) yourself and keep the objective integer |
| Job shop reports a far too long makespan | One no-overlap over the intervals of all machines, which also forbids overlap between machines | One no-overlap per machine, each over that machine's intervals |
| Enumeration hangs | Unbounded variable domain | Give every variable finite bounds |

Binding-specific issues: [C++](interfaces/cpp.md#common-issues), [Python](interfaces/python.md#common-issues).

## Further reading

- Solver guide: [CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver) ([Markdown](https://developers.google.com/optimization/cp/cp_solver.md))
- Statuses and parameters: [cp_model.proto](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto), [sat_parameters.proto](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto)
- Scheduling: [job shop](https://developers.google.com/optimization/scheduling/job_shop)
