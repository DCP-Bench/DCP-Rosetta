# MiniZinc with Gecode (command line and minizinc-python)

MiniZinc models are `.mzn` files run by the `minizinc` executable; the `minizinc` Python package drives that executable. The language, statuses and enumeration strategy are shared: [SKILL.md](../SKILL.md).

## Install

Gecode ships inside the MiniZinc bundle, so there is nothing else to install for the
command line. The Python package drives the `minizinc` executable, so MiniZinc must be
on `PATH` first.

```bash
minizinc --version                 # tested with MiniZinc 2.9.3
minizinc --solvers                 # lists "Gecode ... default solver"
pip install minizinc               # optional: Python API
python3 -c "from minizinc import Solver; print(Solver.lookup('gecode').version)"
```

Details: [MiniZinc installation](https://docs.minizinc.dev/en/2.9.3/installation.html) ·
[minizinc-python getting started](https://python.minizinc.dev/en/latest/getting_started.html)

## Quick start

```python
from minizinc import Instance, Model, Solver

model = Model()
model.add_string("""
include "globals.mzn";
int: n;
array[1..n] of var 1..n: x;
constraint all_different(x);
constraint x[1] < x[n];
solve satisfy;
""")
instance = Instance(Solver.lookup("gecode"), model)
instance["n"] = 4                  # data is assigned by name, not written into the model
result = instance.solve()
if result.status.has_solution():
    print("x =", result["x"])
else:
    print("no solution:", result.status.name)
```

From the command line the same model is a file, run with `minizinc --solver gecode model.mzn data.dzn`.

## Data from Python

`instance["name"] = value` binds a parameter; lists become 1-based arrays. Bind exactly the
parameters the model declares: a key the model does not declare was accepted without error
in the test, so a misspelled name is silent. Encode sets and enumerated types as integers or
booleans.

Arrays must be rectangular (a ragged list raises `TypeError`). For ragged data, flatten into
one 1-based array per field and keep the row positions in Python, as
[assets/minizinc/jobshop/model.py](../assets/minizinc/jobshop/model.py) does: `job[t]` is the job of task `t`,
`mach[t]` its machine, `dur[t]` its duration. Then `where job[t] = job[t+1]` selects the
precedences inside a job.

## Solving

Status values: [`Status`](https://python.minizinc.dev/en/latest/api.html#minizinc.result.Status)

| Python `Status` | CLI output | Meaning |
|---|---|---|
| `OPTIMAL_SOLUTION` | `==========` after the last solution | optimum proven |
| `SATISFIED` | `----------` with no `==========` | a solution was found; the search stopped early (time limit), so optimality or the rest of the space is unproven |
| `UNSATISFIABLE` | `=====UNSATISFIABLE=====` | the whole search space was explored; no solution |
| `UNKNOWN` | `=====UNKNOWN=====` | the limit was reached before any solution |
| `ALL_SOLUTIONS` | `==========` | all solutions enumerated (see [All solutions](#all-solutions)) |
| `UNBOUNDED`, `ERROR` | | rarely reported; a syntax or type error raises `minizinc.error` instead |

Options: CLI [`--time-limit <ms>`](https://docs.minizinc.dev/en/2.9.3/command_line.html),
`-s`, `-d data.dzn`, `-c`. Python: [`Instance.solve(timeout=...)`](https://python.minizinc.dev/en/latest/api.html#minizinc.instance.Instance.solve), `result.statistics`.

Reading results from Python:

| Need | How |
|---|---|
| a declared variable | `result["x"]` (declare it `var ...: x;`, see below) |
| the objective of an optimisation | `result["objective"]` (always present, whatever the variable is named; `result["value"]` for a variable called `value` raises `KeyError` when it is defined with `=`) |
| all fields of the solution | `result.solution`, an object with one attribute per variable |
| no solution | `result.solution` is `None` (`[]` with `all_solutions=True`); check `result.status.has_solution()` |

A variable defined in its declaration (`var int: t = expr;`) is **not** returned to Python.
Declare it and constrain it instead: `var int: t; constraint t = expr;`.

## All solutions

| Goal | CLI | Python (`minizinc`) |
|---|---|---|
| every solution of a satisfaction model | `minizinc --solver gecode -a model.mzn` | `instance.solve(all_solutions=True)`, status `ALL_SOLUTIONS`; `result.solution` is a list with one `Solution` per solution, `[]` when there is none (status `UNSATISFIABLE`) |
| the first k solutions | `-n k` | `instance.solve(nr_solutions=k)` |
| all optimal solutions | not by `-a` (it prints one optimum) | two passes, see [SKILL.md](../SKILL.md#all-solutions) |

Details: [enumeration in the command line](https://docs.minizinc.dev/en/2.9.3/command_line.html)

**Duplicates.** The CLI enumerates distinct values of the output, so unconstrained auxiliary
variables do not repeat a solution. Python's `all_solutions` enumerates every variable,
auxiliary ones included: a free auxiliary variable doubles the count. Either make auxiliaries
functions of the outputs, or keep only distinct values of the output variables in Python
(example: [assets/minizinc/python-all-solutions/model.py](../assets/minizinc/python-all-solutions/model.py)).

**All optimal solutions.** Gecode refuses `all_solutions` on an optimisation model
(`NotImplementedError: Solver does not support the -a-o flag`), so:

1. solve `solve minimize objective;` and check the status is `OPTIMAL_SOLUTION`;
2. add `int: best;` and `constraint objective = best;` to the model and change the solve item to `solve satisfy;`;
3. assign `best` the optimum and call `solve(all_solutions=True)`.

Full code: [assets/minizinc/all-optimal/model.py](../assets/minizinc/all-optimal/model.py).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Solver does not support the -a-o flag` (or `-n-o`) | `all_solutions` or `nr_solutions` on a minimise or maximise model | two passes, see [All optimal solutions](#all-solutions) |
| `cannot determine coercion from type array[_] of array[int] of int` | ragged list passed from Python | flatten to 1-based arrays, see [Data from Python](#data-from-python) |
| `KeyError` on `result["value"]` (or another name) | the objective is read by a name other than `objective`, or the variable is defined with `=` | read `result["objective"]`; it is present whatever the variable is called |
| `KeyError` when reading `result["t"]` | `t` is defined with `=` in its declaration | declare `var int: t;` and `constraint t = ...;` |
| `TypeError` iterating `result.solution` | a plain `solve` found no solution, so `result.solution` is `None` | check `result.status.has_solution()` first; with `all_solutions=True` the list is empty instead |
| repeated solutions from Python `all_solutions` | auxiliary variables | see [Duplicates](#all-solutions) |
