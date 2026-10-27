# Exact in Python (exact)

The `exact` package: pybind11 bindings of Exact's C++ library, one class `Exact`.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../../SKILL.md).
Reification, indicators, no-overlap and encodings: [patterns.md](patterns.md).

## Install

```bash
pip install exact
python3 -c "import exact; print(exact.Exact())"
```

Checked in a fresh virtual environment (Python 3.12, Linux x86_64): `pip install exact`
installs Exact 2.2.1. The PyPI package is precompiled for x86_64 Linux and Windows.
Elsewhere, compile the bindings from the repository (`pip install .` in its root, with
Boost installed). Details:
[README, Python interface](https://gitlab.com/nonfiction-software/exact#python-interface).
The package is AGPL-3.0-only; check that licence before redistributing it.

## Quick start

```python
from exact import Exact

solver = Exact()
solver.addVariable("x", 0, 10)
solver.addVariable("y", 0, 10)
solver.addConstraint([(1, "x"), (1, "y")], True, 5)      # x + y >= 5
solver.setObjective([(2, "x"), (3, "y")], minimize=True)

state, value = solver.toOptimum()                         # ('SAT', 10) when proven
print(state, value, solver.getLastSolutionFor(["x", "y"]))  # SAT 10 [5, 0]
```
## Reading data

When the model takes its numbers from a file (JSON, for example), read each key the
model needs by name:

```python
import json, sys

data = json.load(open(sys.argv[1]))
jobs = data["jobs"]          # bind the keys you use; leave the rest alone
```

Read only the keys the model uses. Do not loop over the whole dictionary or unpack it
into a call (`addVariable(**data)`): `addVariable` takes a name and bounds, not a data record.

## Modelling

Variables and constraints are addressed by **name** (`str`). Full signatures:
[Exact.hpp](https://gitlab.com/nonfiction-software/exact/-/blob/main/src/Exact.hpp) and
[../../references/python/exact-api.md](../../references/python/exact-api.md).

| Need | API |
|---|---|
| integer variable with bounds | `addVariable(name, lb, ub)` |
| 0/1 variable | `addVariable(name, 0, 1)` (the default bounds) |
| linear `sum >= k`, `sum <= k`, `lo <= sum <= hi` | `addConstraint(terms, use_lb, lb, use_ub, ub)`, one call with both bounds |
| `sum == k` | `addConstraint(terms, True, k, True, k)`: equal lower and upper bounds |
| `head <-> sum(terms) >= k` | `addReification(head, True, terms, k)` |
| `head -> sum >= k` / `sum >= k -> head` | `addLeftReification` / `addRightReification` |
| `z == a * b` (variable names as bounds) | `addMultiplication(["a", "b"], True, "z", True, "z")` |
| fix a variable | `fix(name, value)` |
| minimise / maximise a linear term list | `setObjective(terms, minimize=True/False, offset=0)` |

`terms` is a list of `(integer coefficient, variable name)` pairs. **Drop zero
coefficients** when you build the list from data: a `(0, name)` term is still a term, and
`[(0, "a")] >= 1` is unsatisfiable. A bound that is not used is ignored, so
`addConstraint(terms, False, 0, True, k)` is `sum <= k`.

Reification in both directions, with a switch variable:

```python
solver.addVariable("h", 0, 1)
solver.addReification("h", True, [(1, "x")], 3)   # h == 1  <->  x >= 3
solver.addConstraint([(1, "h")], True, 1, True, 1)  # force h = 1, so x >= 3
```

**No global constraints.** There is no all-different, element, table, cumulative or
no-overlap. Build them from indicators or reification (next section).
## Solving

Status values come back as strings. Method reference:
[Exact.hpp](https://gitlab.com/nonfiction-software/exact/-/blob/main/src/Exact.hpp).

| Call | Returns | Use |
|---|---|---|
| `toOptimum(timeout=0)` | `(state, value)` | objective already set; `state` is `SAT` only when the optimum is proven |
| `runFull(optimize=True, timeout=0)` | state string | solve (or enumerate with `optimize=False`) |
| `runOnce(timeout=0)` | state string | stop at the first state reached |
| `getLastSolutionFor(names)` | `list[int]` | values in the last solution, always integers (a 0..1 variable gives 0 or 1) |
| `count(names, timeout=0)` | `(state, n)` | number of distinct projections onto `names` |

| State | Meaning |
|---|---|
| `SAT` | a solution was found; with `toOptimum`, it is proven optimal |
| `UNSAT` | no solution exists (after exhaustion, too) |
| `TIMEOUT` | the limit stopped the search; not proven, and `value` is meaningless |

Behaviours to keep in mind:

- **`hasSolution()` is not the test.** It stays true after `TIMEOUT` and after an
  exhausted enumeration. Read the returned state. A 400-item knapsack stopped at 0.001 s
  still reported a solution.
- **`getLastSolutionFor` on an infeasible model returns `[]`**, not an error. Test the
  state first.
- **Maximisation comes back negated.** Exact minimises internally, so `toOptimum` with
  `minimize=False` returns `-optimum` (the offset is included in the negation). Flip the
  sign before reporting it.

Errors: a duplicate variable, an unknown name in a term, or a lower bound above the upper
bound raise `ValueError` in Python (for example `No variable zz found.`). Infeasibility is
never an exception.

## Time limits

`toOptimum(timeout=0)`, `runFull(timeout=0)` and the other solve calls have **no limit by
default** (`timeout=0`). A hard model then runs until it finishes.

- Pass `timeout` in seconds when the caller has a budget. Use the budget the task gives;
  if there is none, time the model on the largest input you expect first and allow a margin.
- On `TIMEOUT`, report that the answer is **not proven**. Do not report the value or a
  schedule as optimal. Report the time limit and the state.
- Measured in this build: the 6 x 6 job shop (ft06) proves makespan 55 in about 0.1 s,
  including Python start-up. A 60-item knapsack proves in 0.07 s and a 200-item one with
  8-digit values in 25 s (see [Common issues](#common-issues) for the table).
## All solutions

Enumerate with `runFull(optimize=False)`. After each `SAT`, block the solution
**projected onto the variables you care about** with `invalidateLastSol(names)`. Auxiliary
variables are then not counted twice. Stop when the state is `UNSAT`.

```python
solutions = []
while solver.runFull(optimize=False) == "SAT":
    solutions.append(solver.getLastSolutionFor(names))
    solver.invalidateLastSol(names)
```

For a number only, `count(names)` returns `(state, n)`. Example:
[assets/change-ways](../../assets/python/change-ways/README.md).

## All optimal solutions

1. Set the objective and call `toOptimum()`; keep the value (negate it for a maximisation).
2. Pin the objective at that value with `addConstraint(terms, True, best, True, best)`,
   using the real objective terms, not the negated ones.
3. Enumerate as above, projected onto the decision variables.

Example: [assets/pick-items](../../assets/python/pick-items/README.md).
## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Run never ends, or hits an external limit with no answer | `timeout=0` (no limit) | Pass a `timeout` in seconds; on `TIMEOUT` report "not proven" ([Time limits](#time-limits)) |
| Reported a solution after a timeout, and the value is wrong | `hasSolution()` read instead of the state | Accept only `SAT` from `toOptimum` or `runFull` as an answer |
| Reported a schedule as optimal after a timeout | Read the value without checking `toOptimum`'s state | Use the value only when the state is `SAT` |
| Maximum shows as a negative number | Exact minimises internally | Negate `toOptimum`'s value for `minimize=False` |
| Enumeration gives duplicates | Enumerated over auxiliary variables | `invalidateLastSol(names)` over the decision variables only |
| An equality is off by one side, or only half enforced | Written as a one-sided bound | `addConstraint(terms, True, k, True, k)` for `sum == k` |
| Model is unsatisfiable on a zero coefficient | A `(0, name)` term was added from data | Drop zero coefficients when building the term list |
| Two letters or two nodes share a digit or colour | Indicators per letter but no all-different across letters | For each value, sum the indicators over all variables and bound the sum by 1 |
| No-overlap model is slow or wrong at 6 x 6 | No horizon, or orders not reified in both directions | Use the reified pair pattern with the horizon set to the sum of durations ([No-overlap](patterns.md#no-overlap-scheduling)) |
| `ValueError: No variable ... found` | Term or name used before `addVariable`, or misspelt | Declare every variable first; check the spelling |
| `ValueError: Unknown encoding ...` | Encoding not in `log`, `order`, `onehot` | Use one of the three |
| `ValueError: Upper bound ... smaller than lower bound` | Bounds swapped in `addVariable` | Check the order `(name, lb, ub)` |
| Model is slow with many indicators | One-hot indicators on a wide domain | Tighten the domain; indicate only the variables that need values |
| Global constraint not found (`all_different`, `element`) | Exact has none | Build from indicators or reification ([Patterns](patterns.md)) |
| Installation fails on macOS or ARM | No precompiled wheel | Build from source, see [Install](#install) |

Timing reference (this build, Exact 2.2.1, Python 3.12): a knapsack with 60 items of 6 digits
proves its optimum in 0.07 s, 120 items of 7 digits in 2.6 s, 200 items of 8 digits in 25 s.
Pigeonhole-style infeasibility is not hard for Exact. For no-overlap, the ft06 job shop solved
in 0.1 s with the reified pair pattern, and also with a big-M order constraint with M from 100
to 10^8, so no time-out was seen for either; measure both on your own model before choosing.
Source: [sources.md](../../sources.md).
## Examples

Each folder under `assets/` is a standalone model with a README (problem, what it shows, run
command, expected output). Run one with `python3 model.py` inside its folder.

| Example | Pattern | Output |
|---|---|---|
| [assign-distinct](../../assets/python/assign-distinct/README.md) | one-hot indicators, all-different, satisfy | `status: SAT` |
| [budget-infeasible](../../assets/python/budget-infeasible/README.md) | reading `UNSAT` as the answer | `status: UNSAT` |
| [change-making](../../assets/python/change-making/README.md) | minimise a sum of variables | `Minimum coins: 5` |
| [change-ways](../../assets/python/change-ways/README.md) | enumerate, projected onto the decision variables | `Solutions: 13` |
| [cryptarithm](../../assets/python/cryptarithm/README.md) | letters as digits, all-different, place values | `9567 + 1085 = 10652` |
| [either-or](../../assets/python/either-or/README.md) | reification, disjunction, minimise | `x = 8 minimum: 8` |
| [graph-colouring](../../assets/python/graph-colouring/README.md) | node by colour, used-colour objective | `colours used: 3` |
| [job-shop](../../assets/python/job-shop/README.md) | reified no-overlap, makespan | `makespan: 55` |
| [pick-items](../../assets/python/pick-items/README.md) | all optimal solutions, pinned objective | `Optimal solutions: 3` |
| [production-plan](../../assets/python/production-plan/README.md) | maximise, sign flipped back | `Optimal profit: 20` |
| [task-schedule](../../assets/python/task-schedule/README.md) | release times, reified no-overlap | `Makespan: 11` |
## Further reading

- Python bindings, every method and its doc string: <https://gitlab.com/nonfiction-software/exact/-/blob/main/src/Exact.hpp>
- Examples: <https://gitlab.com/nonfiction-software/exact/-/blob/main/python_examples>; start with `knapsack_tutorial`, which is commented and ends with advanced features
