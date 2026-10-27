# Python-MIP in Python (mip)

The `mip` package: Python classes over the CBC library. Shared concepts, encodings and enumeration strategy: [SKILL.md](../SKILL.md).

## Install

```bash
pip install mip
python3 -c "import mip; print(mip.__version__)"
```

Tested with `mip` 2.0.0 (which installs `cbcbox` 2.935, the CBC solver). Pin `mip==2.0.0` when results must reproduce. `mip.Model()` picks Gurobi when Gurobi (`gurobipy`) is installed and CBC otherwise, so pass `solver_name="CBC"` explicitly. Details: [Python-MIP site](https://www.python-mip.com).

## Quick start

```python
# Tiny integer program: choose whole numbers x and y in 0..4 to maximise 3x + 2y
# under x + 2y <= 7. Prints the proven optimum.
import mip

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0                        # without this CBC's log goes to stdout
m.max_mip_gap = 0.0                  # OPTIMAL means proven, not within 0.01 %
m.max_mip_gap_abs = 0.0
x = m.add_var("x", lb=0, ub=4, var_type=mip.INTEGER)
y = m.add_var("y", lb=0, ub=4, var_type=mip.INTEGER)
# the capacity constraint
m += x + 2 * y <= 7
# the objective
m.objective = 3 * x + 2 * y
if m.optimize(max_seconds=10) == mip.OptimizationStatus.OPTIMAL:
    print("Optimal:", round(x.x), round(y.x), round(m.objective_value))
```

## Modelling

Full reference: [classes](https://python-mip.readthedocs.io/en/latest/classes.html).

| Need | API |
|---|---|
| variable; `var_type` is `mip.BINARY`, `mip.INTEGER` or `mip.CONTINUOUS` (default) | [`m.add_var(name, lb, ub, obj, var_type)`](https://python-mip.readthedocs.io/en/latest/classes.html) |
| many terms | [`mip.xsum(terms)`](https://python-mip.readthedocs.io/en/latest/classes.html) (Python's `sum` also builds an expression) |
| constraint with `<=`, `>=` or `==` | `m += expr <= rhs` or [`m.add_constr(expr, name)`](https://python-mip.readthedocs.io/en/latest/classes.html) |
| objective (a bare `m += expr` adds nothing and raises nothing; a bare variable raises `TypeError`) | `m.objective = expr`; direction from `mip.Model(sense=mip.MAXIMIZE)` (default `MINIMIZE`) |
| constant in the objective | `expr + 5`; `m.objective_const` reports it and `objective_value` includes it |
| value after solving | `v.x` and `expr.x` (float, or `None` without a solution), `m.objective_value`, `m.objective_bound`, `m.gap` |
| variable by name, bounds, type | `m.var_by_name("x")`, `v.lb`, `v.ub`, `v.var_type` |

Syntax facts, all checked by running:
- `x * y`, `x * x`, `abs(x)` raise `TypeError`. Multiply by a number only (`2 * x`, `x / 2`).
- `x == 3` gives an expression object, which is always true in an `if`. Use `==` only inside `m += ...`, and compare values with `v.x` after solving.
- `m += 2 <= 3` raises `TypeError`: a constraint needs a variable.
- `a + a + b` silently drops a coefficient (it becomes `a + b`), while `a + b + a` is correct. Write `2 * a + b`, or build sums with `mip.xsum([...])`. A constraint built from such a sum is weaker than intended.
- Inside a nested helper function, `m += expr` makes `m` a local name and raises `UnboundLocalError`. Call `m.add_constr(expr)`, or pass `m` as a parameter.

## Numbers

- Solution values are floats: `5.0`, not `5`. Round them (`round(v.x)`) before comparing or printing. A value can sit up to `m.integer_tol` (1e-6 by default) from an integer, and an expression over continuous variables can drift a little further.
- Keep an integer output an integer variable: `z = m.add_var(var_type=mip.INTEGER)` with `z == sum(w_i * b_i)` (unit or integer coefficients). The integer variable then comes back as an integral float (`11.0`).
- Coefficients up to 1e9 with integer outputs up to 2.5e10 gave exact integer values in tests (60 binaries). Larger magnitudes were not tested.

## Solving

`m.optimize(max_seconds=...)` returns an `mip.OptimizationStatus`. Read the status before any value.

| Status | Meaning |
|---|---|
| `OPTIMAL` | a solution, proven optimal when `max_mip_gap` is 0 |
| `INFEASIBLE` | proven: no solution (CBC also reports this when the relaxation is feasible but no integer point exists) |
| `UNBOUNDED` | the objective has no bound |
| `FEASIBLE` | a solution, optimality not proven (time limit reached) |
| `NO_SOLUTION_FOUND` | time limit reached with no solution: nothing is known |
| `OTHER` | the model has no variables, so nothing was solved |

Reference: [`OptimizationStatus`](https://python-mip.readthedocs.io/en/latest/classes.html). Without a solution, `v.x` is `None`.

A satisfaction model (no objective) may leave `m.objective` unset, or set it to 0. Then `m.optimize()` returns `OPTIMAL` when a feasible point exists (`m.objective_value` is 0.0) and `INFEASIBLE` when none does. Checked with CBC 2.935.

Settings that matter (defaults from the package source, `mip/model.py`):

| Setting | Default | Note |
|---|---|---|
| `m.max_mip_gap` | `1e-4` | relative gap at which CBC stops. Set `0.0`. In a test at the default, CBC returned `OPTIMAL` with value 195,360,778 and gap 4.5e-5; the same model with gap 0 found 195,369,517 |
| `m.max_mip_gap_abs` | `1e-10` | absolute gap at which CBC stops. Set `0.0` with the line above |
| `m.verbose` | `1` | CBC's log goes to stdout. Set `0` |
| `m.threads` | `0` | solver default. `1` for reproducible runs |
| `m.integer_tol`, `m.infeas_tol`, `m.opt_tol` | `1e-6` each | tolerances; leave them unless a model needs otherwise |
| `m.seed` | `0` | random seed for CBC's tie-breaks |
| `m.preprocess` | `-1` | `0` turns CBC's presolve off. Needed when a model with coefficients around 1e6 or larger returns `OPTIMAL` for a point that breaks a row (CBC prints "Postprocessed model is infeasible") |
| `m.emphasis` | `0` | `1` favours feasibility, `2` optimality. It rarely helped in tests, and `1` raised memory sharply on a model with about 11,000 binaries |
| `m.cuts`, `m.cut_passes` | `-1` | cut generation level and number of passes; `m.cuts = 2` crashed CBC on one scheduling model |
| `optimize(max_seconds=...)` | no limit | time limit in seconds for that solve |

With the default `verbose = 1` the package prints a solver banner and CBC's log to stdout. A program that prints its own answer sets `m.verbose = 0` before `optimize`; the `[cbcbox]` banner lines (binary and library paths) still print at `verbose = 0`, so a script that parses stdout must skip lines starting with `[cbcbox]`.

Errors in building the model are Python exceptions at build time. A solver failure shows as status `ERROR`, which none of the tests with CBC produced. A model with no variables returns `OTHER` and logs `Model has no variables`.

## All solutions

No solution pool to rely on: `m.num_solutions` and `v.xi(k)` exist, but on a tie of four binaries the pool held one solution. Enumerate with no-good cuts instead ([n-queens-all](../assets/python/n-queens-all/README.md)):

```python
# Count every 0/1 assignment of decision binaries that satisfies the model.
# After each solution, a no-good cut over the decision binaries forbids it.
placements = []
while m.optimize(max_seconds=60) == mip.OptimizationStatus.OPTIMAL:
    values = [round(b.x) for b in decisions]
    placements.append(values)
    m += mip.xsum((1 - b) if v == 1 else b for b, v in zip(decisions, values)) >= 1
```

The loop itself prints nothing. With zero solutions the first `optimize` returns `INFEASIBLE`, the loop body never runs and `placements` is empty, so a count of 0 is printed. With exactly one solution the count is 1. Check `placements` before indexing it. The [n-queens-all](../assets/python/n-queens-all/README.md) example prints the first placement as a plain list.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Log lines in the output, parser fails | `verbose` defaults to 1; the `[cbcbox]` banner prints even at 0 | `m.verbose = 0`, and skip `[cbcbox]` lines |
| `TypeError: Can not multiply with type Var` | `x * y` | encode the product (table above) |
| `TypeError: bad operand type for abs()` | `abs(var)` | `d >= a - b`, `d >= b - a` with minimisation |
| A branch never runs, or a constraint has no effect | `if x == 3:` is always true | use `m += x == 3`, or compare `x.x` after the solve |
| `ValueError: Invalid bounds for binary variable` | `var_type=mip.BINARY` with a bound outside 0..1 (`ub=2`, `lb=-1`); a bound inside 0..1 such as `lb=1` is accepted and fixes the variable | omit the bounds of a binary |
| `TypeError: type ... bool not supported` | `m += 2 <= 3` | write the constraint with variables |
| `TypeError: type ... Var not supported` on `m += x` | a bare variable is not a constraint | `m.objective = x` |
| `m += x + y` has no effect | a bare expression is accepted and adds no constraint | write a relation (`x + y <= 3`) or set `m.objective` |
| `5.0` where `5` is expected | solution values are floats | `round()`; keep integer outputs integer variables |
| `None` in output, or `TypeError` on `None` | no solution | check the status before reading values |
| `OTHER`, `Model has no variables` | no `add_var` before `optimize` | create the variables first |
| Solver is Gurobi, not CBC | `gurobipy` installed | `mip.Model(solver_name="CBC")` |
| `UnboundLocalError` on `m` in a helper | `m += expr` inside a nested function | `m.add_constr(expr)` |
| Solutions fail a check although every constraint was written | a sum like `a + a + b` lost a coefficient | `2 * a + b` or `mip.xsum` |
| `INFEASIBLE` on a small model built with an index loop | a row with the same variable on both sides (`x == x`) | skip the degenerate row |

More: [Common issues in SKILL.md](../SKILL.md#common-issues).

## Runnable examples

- [knapsack](../assets/python/knapsack/README.md)
- [all-optimal-committee](../assets/python/all-optimal-committee/README.md)
- [n-queens-all](../assets/python/n-queens-all/README.md)
- [latin-square](../assets/python/latin-square/README.md)
- [cryptarithm](../assets/python/cryptarithm/README.md)
- [single-machine-schedule](../assets/python/single-machine-schedule/README.md)
- [encodings](../assets/python/encodings/README.md)
- [graph-colouring](../assets/python/graph-colouring/README.md)
- [status-check](../assets/python/status-check/README.md)
