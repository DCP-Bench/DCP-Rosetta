# docplex_cplex: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how DOcplex
(Python, CPLEX) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `docplex` and the standard library; nothing
else is installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def create_model(instance) -> tuple[docplex.mp.model.Model, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
Models retained before 2026-11-11 name it `build(instance)`, which the runner still
accepts; write `create_model`. It must return a 2-tuple
(not a list) `(model, outputs)` with `model` a `docplex.mp.model.Model`. Anything the
module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a docplex variable,
a linear expression, a Python integer or Boolean, or a nested `list`/`tuple` of these.
Integer and binary variables are rounded to the nearest integer and linear expressions
are evaluated over the rounded values. A `binary_var` is reported as `0`/`1`, not as a
Boolean. A value that is not within 1e-6 of an integer is rejected (`execution_error`).

## Objective

`model.minimize(expr)` or `model.maximize(expr)`; the runner reads
`model.has_objective()`. No call (or `minimize(0)`) is a satisfaction problem. Any other
constant (`minimize(3)`) makes `has_objective()` true, so the runner treats the model as
an optimisation with that constant as the proven optimum.

The objective reported with each solution is the objective expression evaluated on that
solution (its constant included, integer variables rounded), in the model's own direction.
The incumbents are CPLEX's incumbent objective, which already has the model's constant and
direction (CPLEX maximises natively and keeps the constant as the objective offset).

## Solving

- Forced over the submission's own parameters: `threads = 1`,
  `mip.tolerances.mipgap = 0` (CPLEX's default 1e-4 relative gap ends the search with
  status 102, "integer optimal, tolerance", short of the optimum), `timelimit` = the
  budget left, and `log_output=False`. Other parameters you set are kept.
- Status codes: 1, 101, 102 with a solution are proven (`solved`); 3, 103 `unsat`;
  2, 118 `error` (objective unbounded); 11, 107, 108 `timeout`; any other code `error`.
  On 4 or 119 (infeasible or unbounded) the runner re-solves once with
  `preprocessing.reduce = 1` (primal reductions only) and maps the new code.
  `DOcplexLimitsExceeded` is `unsupported`.
- Incumbents: during the first solve of an optimisation only, a CPLEX generic callback in
  the global-progress context (informational: same nodes and iterations as without it)
  reports each improving integer incumbent objective as an `incumbent`, with the seconds
  since `solve()` was called. A model presolve solves outright gets no call, so the proven
  optimum is reported when the solve returns if it was not the last one reported.
- Enumeration: after the first proven solve the objective is pinned by a range
  (±0.5 around the optimum for an integral objective) and removed; each next solve adds
  a no-good over the integer variables under the declared outputs (a linear term per
  binary, two indicator constraints per general integer; fixed variables skipped).
  A repeated output value is re-solved, not emitted. Infeasible after a no-good, or no
  unfixed variable left to move, is `complete`.
- Time: the deadline is set before `create_model` runs, so building spends the budget. Each solve
  gets the time left; a SIGALRM at budget + 5 s, armed over `create_model` and the whole loop,
  turns a hang in Python into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/docplex_cplex:v1`: Python 3.12.11 (`/usr/local/bin/python`), docplex
2.32.264 on the cplex 22.2.0.1 wheel, whose `cplex.__version__` reports `22.2.0.0`.
Installed: `cplex`, `docplex`, `six` and the standard library (`json` included); no NumPy.
The wheel is the CPLEX Community Edition: no licence file, and it refuses a model above
1000 variables or 1000 constraints with `DOcplexLimitsExceeded: **** Promotional version.
Problem size limits (1000 vars, 1000 consts) exceeded, model has ... CPLEX code=1016`.
No environment variables of note; the container runs without network. For an ad hoc run,
`--entrypoint sh` bypasses `/opt/runner/run.py`.

## Traps

- The Community Edition limit (see Environment) counts indicator constraints. It is
  reported as `unsupported`, which the evaluator records as `unsupported_capability`;
  size the model for the largest instance. Enumeration adds rows of its own: one range
  pinning the objective, one no-good per extra solution, and per general-integer output
  variable up to two binaries and two indicators.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
  That includes the hidden continuous variable of `model.abs`, `model.max` and
  `model.min`: tie such a value to an `integer_var` and declare that instead.
- `*_var_matrix` and `*_var_dict` return dicts. Keyed by tuples they crash serialisation
  (`execution_error`); keyed by ints they become a JSON object (`invalid_output`).
  Return lists: `[[x[i, j] for j in cols] for i in rows]`.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment
  with the same value. Declare such an output as its own integer variable.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a CPLEX (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python knapsack.py knapsack.json

from docplex.mp.model import Model


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry
    n_items = len(values)

    model = Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = model.binary_var_list(n_items, name="x")

    # The packed items weigh no more than the backpack can carry.
    model.add_constraint(model.sum(weights[i] * x[i] for i in range(n_items)) <= capacity)

    # Pack the most valuable selection.
    model.maximize(model.sum(values[i] * x[i] for i in range(n_items)))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
```

## Standalone run

Every model carries the header and the run block of the example, with `knapsack` replaced by
the problem id, so a reader can copy it from the catalogue and run it with `docplex` and
`cplex`. Nothing else goes in either: the header is the first lines of the file, the run
block the last, and the model sits between them. The runner loads the file as module
`candidate`, so the block never runs during evaluation.

The block sets the relative gap to 0 as the runner does (the default stops within 0.01% of the
optimum and still reports a solution), solves once, and when `solve()` returns a solution prints
the objective value and each output as integers, a list for a list. A model with no objective
leaves out the `mipgap` line and the objective line, and its comment reads `# a solution`.
Otherwise `solve()` returns `None` and `model.solve_details.status` says why (`infeasible`,
`infeasible or unbounded`, ...). The `value` helper reads a variable or a linear expression
through `solution_value`, and goes through lists of any depth. A model without instance data
calls `create_model({})`, takes no instances file, and has no `Download` line, no `json` and
`sys` imports and no `instances` lines:

```python
# abbots_puzzle: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python abbots_puzzle.py

from docplex.mp.model import Model


def create_model(instance):
    ...


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
```

The CPLEX that comes with `pip install cplex` is the Community Edition, and refuses a model
above 1000 variables or 1000 constraints; the header says so.
