# OR-Tools CP-SAT in C++ (CpModelBuilder)

The native C++ API of OR-Tools, built with CMake against the binary archive.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).
Builder API: [`cp_model.h`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), whose comments are the reference.

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Reading instance data](#reading-instance-data)
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Runnable examples](#runnable-examples)

## Install

Official guide: [OR-Tools C++ binary install](https://developers.google.com/optimization/install/cpp/binary_linux). You need `g++` with C++17 and `cmake` 3.18 or newer (Debian: `sudo apt install build-essential cmake`; ask before using `sudo`).

```bash
curl -fL -o or-tools.tar.gz https://github.com/google/or-tools/releases/download/v9.15/or-tools_amd64_debian-12_cpp_v9.15.6755.tar.gz
echo 'b2c9870c8778eeb26c98742402da17da039c058fca7eca87be5c90832b04153c  or-tools.tar.gz' | sha256sum -c -
mkdir -p "$HOME/or-tools" && tar xzf or-tools.tar.gz -C "$HOME/or-tools" --strip-components=1
export CMAKE_PREFIX_PATH="$HOME/or-tools"   # CMake reads this variable; no -D needed
```

The commands above fetch the Debian 12 x86_64 archive (the one tested). On other systems take the C++ archive for yours from the [v9.15 release page](https://github.com/google/or-tools/releases); the steps are the same, the checksum line is not.

The archive bundles its own Abseil, protobuf and Boost, so the compiler and CMake are the only tools to install. Verify with the Quick start below: it prints `Objective: 12`.

If OR-Tools is already unpacked somewhere (a container or a shared install), point `CMAKE_PREFIX_PATH` at that directory and add its `lib/` to `LD_LIBRARY_PATH`, then skip the download and go to the Quick start. Check with `echo $CMAKE_PREFIX_PATH`; if it is empty, use the commands above. Without network access the download cannot work, so the OR-Tools prefix (and nlohmann/json, found by `find_package` like OR-Tools) must already be on the machine.

## Quick start

`model.cc`:

```cpp
#include <cstdint>
#include <iostream>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  // Maximise 3x + 2y for integers 0 <= x, y <= 4 with x + y <= 4 and x + 3y <= 6.
  CpModelBuilder model;
  const IntVar x = model.NewIntVar(Domain(0, 4));
  const IntVar y = model.NewIntVar(Domain(0, 4));
  model.AddLessOrEqual(x + y, 4);
  model.AddLessOrEqual(x + 3 * y, 6);
  model.Maximize(3 * x + 2 * y);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() == CpSolverStatus::OPTIMAL) {
    std::cout << "Objective: " << static_cast<int64_t>(response.objective_value()) << "\n";
    std::cout << "x = " << SolutionIntegerValue(response, x) << ", y = "
              << SolutionIntegerValue(response, y) << "\n";
  } else {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  }
  return 0;
}
```

`CMakeLists.txt` next to it:

```cmake
cmake_minimum_required(VERSION 3.18)
project(model LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(ortools CONFIG REQUIRED)
add_executable(model model.cc)
target_link_libraries(model PRIVATE ortools::ortools)
```

```bash
cmake -S . -B build && cmake --build build && ./build/model
```

Keep the build tree outside the source folder (`-B "$HOME/build/model"` instead of `-B build`), so it never mixes with sources and can always be deleted; the binary is then `"$HOME/build/model/model"`.

Several programs in one project: list their names, and CMake builds each into `<build>/bin`. This version takes sources from `models/<name>.cpp` and links nlohmann/json (drop that line if no program reads JSON); for `<name>.cc` in the project root, change the `add_executable` path.

```cmake
find_package(nlohmann_json CONFIG REQUIRED)
set(PROGRAMS knapsack copy)
foreach(program IN LISTS PROGRAMS)
  add_executable(${program} models/${program}.cpp)
  target_link_libraries(${program} PRIVATE ortools::ortools nlohmann_json::nlohmann_json)
  set_target_properties(${program} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endforeach()
```


## Reading instance data

A program that solves a data file receives its path as `argv[1]`. This skill parses it with nlohmann/json, header `/usr/include/nlohmann/json.hpp` from the Debian package `nlohmann-json3-dev` (`sudo apt install nlohmann-json3-dev`, asking before `sudo`). Link it through CMake:

```cmake
find_package(nlohmann_json CONFIG REQUIRED)
target_link_libraries(model PRIVATE ortools::ortools nlohmann_json::nlohmann_json)
```

```cpp
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

#include <nlohmann/json.hpp>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const auto weights = instance.at("weights").get<std::vector<int64_t>>();
  const int64_t capacity = instance.at("capacity").get<int64_t>();
  // ... build the model from these values
}
```

Nested arrays convert in one call, for example `[machine, duration]` pairs per job: `instance.at("jobs").get<std::vector<std::vector<std::pair<int, int64_t>>>>()` (verified). `parse` throws on malformed JSON and `at` throws on a missing key, so a failure stops the program with an exception rather than a wrong answer. The full program is verified by building with `find_package(nlohmann_json)`; it prints `Value: 10` for weights `[3, 4, 5]`, values `[4, 5, 6]` and capacity `8`.

## Modelling

Full list: [`cp_model.h`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h).

| Need | API |
|---|---|
| Integer variable with bounds | [`NewIntVar(Domain(lo, hi))`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Domain with holes | [`Domain::FromValues({-1, 1})`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Boolean variable | [`NewBoolVar()`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); a `BoolVar` enters sums directly: `total += weight * take[i]`. Also verified: `int * IntVar` in sums, `LinearExpr - int64_t`, `AddMaxEquality(IntVar, {exprs})` |
| Constant as a variable | [`NewConstant(k)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Linear (in)equality | [`AddEquality`, `AddNotEqual`, `AddLessOrEqual`, `AddLessThan`, `AddGreaterOrEqual`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Linear value in a set | [`AddLinearConstraint(expr, Domain::FromValues({3, 4, 7}))`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| All different | [`AddAllDifferent(std::vector<LinearExpr>)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Element (array read at a variable index) | [`AddElement`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), see [Common issues](#common-issues) |
| Absolute value, min, max | [`AddAbsEquality`, `AddMinEquality`, `AddMaxEquality`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Product, division, modulo | [`AddMultiplicationEquality`, `AddDivisionEquality`, `AddModuloEquality`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); chain a product two factors at a time, each intermediate bounded; a divisor whose domain contains 0 makes the model invalid, so give it a domain without 0 |
| Boolean clauses | [`AddBoolOr`, `AddBoolAnd`, `AddImplication`, `AddAtMostOne`, `AddExactlyOne`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Reification | [`.OnlyEnforceIf(lit)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), posted in both directions; see below |
| Regular language | [`AddAutomaton(exprs, start, finals)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then [`.AddTransition(tail, head, label)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) per arc |
| Intervals and no-overlap | [`NewFixedSizeIntervalVar(start, size)`, `NewIntervalVar(start, size, end)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); [`AddNoOverlap(std::vector<IntervalVar>)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) takes the intervals of one machine per call, see [no-overlap-jobshop](../assets/cpp/no-overlap-jobshop/README.md) |
| Interval ends | `interval.StartExpr()`, `interval.EndExpr()` and `SizeExpr()` are `LinearExpr`s usable in constraints, `AddMaxEquality` and `SolutionIntegerValue` (verified); a makespan is `AddMaxEquality(makespan, ends)` |
| Cumulative resource | [`AddCumulative(capacity)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then [`.AddDemand(interval, demand)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| 2-D no-overlap | [`AddNoOverlap2D()`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then `.AddRectangle(x_interval, y_interval)` |
| Minimise / maximise | [`Minimize(expr)` / `Maximize(expr)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); at most one objective |

Reification needs both directions, or the indicator is free to take the value that suits the search:

```cpp
BoolVar hit = model.NewBoolVar();
model.AddEquality(x[i], value).OnlyEnforceIf(hit);
model.AddNotEqual(x[i], value).OnlyEnforceIf(hit.Not());
```

This counts occurrences (`sum(x == v) == k` is a sum of `hit` indicators), and a disjunction of constraints is one `AddBoolOr` over their indicators.

## Solving

Status values: [`CpSolverStatus`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto) (`CpSolverStatus::OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `UNKNOWN`, `MODEL_INVALID`; name with `CpSolverStatus_Name`). Parameters: [`sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto). Meanings: [SKILL.md](../SKILL.md#solving). For `MODEL_INVALID`, read `ValidateCpModel(model.Build())`.

Read values only after checking the status is `OPTIMAL` or `FEASIBLE`.

```cpp
SatParameters parameters;
parameters.set_max_time_in_seconds(10.0);
parameters.set_num_workers(8);
parameters.set_random_seed(42);
parameters.set_log_search_progress(true);   // the search log goes to stdout
const CpSolverResponse response = SolveWithParameters(model.Build(), parameters);
```

| Need | Call |
|---|---|
| Value of an `IntVar` or `LinearExpr` | `SolutionIntegerValue(response, expr)` |
| Value of a `BoolVar` | `SolutionBooleanValue(response, b)` |
| Objective and its bound | `response.objective_value()` (a double), `response.best_objective_bound()` |
| Why a model is invalid | `ValidateCpModel(model.Build())` (`ortools/sat/cp_model_checker.h`); empty when valid |


## All solutions

Enumerate with a solution observer and one worker. Every variable in the model is part of the solution, so enumerate over decision variables only (see [SKILL.md](../SKILL.md#all-solutions)). The snippet needs the same `using` lines as the Quick start, and these headers:

```cpp
#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

Model enumerator;
int count = 0;
enumerator.Add(NewFeasibleSolutionObserver([&] (const CpSolverResponse& r) {
  ++count;   // read the decision variables of r here
}));
SatParameters parameters;
parameters.set_enumerate_all_solutions(true);
parameters.set_num_workers(1);
enumerator.Add(NewSatParameters(parameters));
const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
```

Pattern and runnable code: [all-solutions-subset-sum](../assets/cpp/all-solutions-subset-sum/README.md). Reference: [`sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto) (`enumerate_all_solutions`), [sample programs](https://github.com/google/or-tools/tree/v9.15/ortools/sat/samples), starting with `cp_sat_example.cc` and `search_for_all_solutions_sample_sat.cc`.

**All optimal solutions:** solve once to get the optimum `z*`. Build a second model from scratch with the same constraints, `AddEquality(objective_expr, z*)` and no objective, then enumerate it as above. A model that still carries the objective is optimised, not enumerated. Pattern and code: [all-optimal-committee](../assets/cpp/all-optimal-committee/README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Compile error listing many `AddElement` candidates | `AddElement` takes a span of `LinearExpr` (or of `int64_t` constants), not of `IntVar`; a `std::vector<IntVar>` converts to neither | Convert once: `const std::vector<LinearExpr> exprs(vars.begin(), vars.end());`. `AddAllDifferent` and `AddMaxEquality` need the same conversion for expressions such as `queens[i] - i` |
| Two-dimensional table indexed by two variables | Nested element constraints, or an `AddElement` on the wrong axis | Flatten the table into one `std::vector<LinearExpr>` of width `w`, add `AddEquality(cell, w * row + col)`, then one `AddElement(cell, ...)` |
| `MODEL_INVALID` | Malformed model, for example a domain with `lo > hi` | Print `ValidateCpModel(model.Build())` and fix the named variable or constraint |
| Compile error: `Model`, `NewFeasibleSolutionObserver` or `NewSatParameters` not declared | The enumeration headers are missing | Include `ortools/sat/model.h` and `ortools/sat/sat_parameters.pb.h` with the other two headers, as in [All solutions](#all-solutions) |
| Job shop reports makespan 23 where the optimum is 11 | One `AddNoOverlap` over the intervals of all machines, which also forbids overlap between machines | One `AddNoOverlap` call per machine, each over that machine's intervals; [no-overlap-jobshop](../assets/cpp/no-overlap-jobshop/README.md) does this |
| Ambiguous overload or no match for `queens[i] + i` style arithmetic in a `LinearExpr` context | Mixed `IntVar` and integer types of different widths | `IntVar + int` and `IntVar + size_t` compile; if a compiler complains anyway, write `LinearExpr(x) + int64_t(i)` |
| `fatal error: nlohmann/json.hpp: No such file or directory` | nlohmann/json not installed, or not linked | Install `nlohmann-json3-dev`, then `find_package(nlohmann_json CONFIG REQUIRED)` and link `nlohmann_json::nlohmann_json`; see [Reading instance data](#reading-instance-data) |

## Runnable examples

- [satisfy-latin-square](../assets/cpp/satisfy-latin-square/README.md): satisfy
- [all-solutions-subset-sum](../assets/cpp/all-solutions-subset-sum/README.md): all solutions
- [all-optimal-committee](../assets/cpp/all-optimal-committee/README.md): all optimal solutions
- [maximise-production-plan](../assets/cpp/maximise-production-plan/README.md): maximise
- [minimise-assignment](../assets/cpp/minimise-assignment/README.md): minimise
- [infeasible-pigeonhole](../assets/cpp/infeasible-pigeonhole/README.md): infeasible
- [scheduling-cumulative](../assets/cpp/scheduling-cumulative/README.md): cumulative resource
- [no-overlap-jobshop](../assets/cpp/no-overlap-jobshop/README.md): one no-overlap per machine
