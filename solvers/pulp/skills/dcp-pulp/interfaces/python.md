# PuLP in Python (pulp)

PuLP's own Python API; it writes the model to a file and runs the bundled CBC binary.
Shared concepts, encodings, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/python/`, one folder per pattern

## Install

```bash
pip install "pulp>=3.3,<4"
python3 -c "import pulp; print(pulp.__version__, pulp.PULP_CBC_CMD().available())"
```

The second line prints the version and the path of the bundled `cbc` binary (`3.3.2 /…/cbc`). PuLP 4.0 was published on PyPI on 2026-10-14. This skill has not been tested against PuLP 4.0, so the range stops below 4. Details: [installing PuLP](https://coin-or.github.io/pulp/main/installing_pulp_at_home.html), [migrating to 4.0](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html) (read, not run).

## Quick start

```python
import pulp

prob = pulp.LpProblem("quick", pulp.LpMaximize)
x = prob.add_variable("x", lowBound=0, upBound=4, cat="Integer")
y = prob.add_variable("y", lowBound=0, upBound=4, cat="Integer")
prob += x + 2 * y <= 7        # a constraint: the expression has a relation
prob += 3 * x + 2 * y         # the objective: a bare expression

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status == pulp.LpSolutionOptimal:
    print("Optimal:", pulp.value(x), pulp.value(y), pulp.value(prob.objective))  # Optimal: 4.0 1.0 14.0
else:
    print("Status:", pulp.LpStatus[status])
```

## Modelling

Full API: [PuLP reference](https://coin-or.github.io/pulp/technical/pulp.html).

| Need | API |
|---|---|
| variable (`cat` is `"Continuous"`, `"Integer"` or `"Binary"`) | [`prob.add_variable(name, lowBound, upBound, cat)`](https://coin-or.github.io/pulp/technical/pulp.html) |
| many variables; nested index sets give nested dicts | [`prob.add_variable_dicts(name, indices, lowBound, upBound, cat)`](https://coin-or.github.io/pulp/technical/pulp.html), then `x[i][j]` |
| sum of terms (linear time) | [`pulp.lpSum(...)`](https://coin-or.github.io/pulp/technical/pulp.html) |
| constraint (`<=`, `>=`, `==`), named | `prob += expr <= rhs, "name"` |
| objective: one bare expression | `prob += expr`, direction from `pulp.LpProblem(name, pulp.LpMaximize)` or `LpMinimize` |
| satisfaction problem | add no objective; `prob.objective` stays `None` |
| multiply by a constant, divide by a constant | `2 * x`, `x / 2` |
| value after solving | `var.varValue` (float), `pulp.value(expr)` |

A `Binary` variable is an `Integer` with bounds 0 and 1. An `Integer` without bounds has `lowBound` and `upBound` of `None`, which enumeration cannot use: bound every integer you need to enumerate.

Non-linear forms are rejected at build time: `x * y`, `x * x`, `abs(x)`, `x / y` and `x % 2` raise `TypeError`. `x != y` is not an error, but it adds nothing to the model: it returns a Python `True`.

## Solving

Solver options: [configure a solver](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html). CBC parameters are in [solvers](https://coin-or.github.io/pulp/technical/solvers.html).

`PULP_CBC_CMD(msg=True, timeLimit=None, gapRel=None, gapAbs=None, threads=None, logPath=None, timeMode="elapsed", options=None, warmStart=False, ...)`. `msg=True` (the default) prints CBC's log to stdout; `msg=False` silences it; `logPath` writes the log to a file; `timeMode="cpu"` counts CPU seconds instead of wall-clock seconds.

**Use `msg=False` whenever the script's stdout is parsed or compared** (a grader, a test, or any line-by-line reader): CBC's log lines are written to the same stream. Use `logPath="cbc.log"` if you still want the log.

Two status attributes answer two questions. Read both:

| `pulp.LpStatus[prob.status]` | `prob.status` | Meaning |
|---|---|---|
| `Optimal` | 1 | CBC stopped with a solution. It may still be unproven (see `sol_status`) |
| `Not Solved` | 0 | Not solved, or a time limit ended with no solution |
| `Infeasible` | -1 | proven: no solution |
| `Unbounded` | -2 | the objective is unbounded |

| `prob.sol_status` | Value | Meaning |
|---|---|---|
| `pulp.LpSolutionOptimal` | 1 | optimum proven (or, with no objective, a solution found and proven feasible) |
| `pulp.LpSolutionIntegerFeasible` | 2 | a feasible solution, optimality not proven (time limit) |
| `pulp.LpSolutionNoSolutionFound` | 0 | nothing found within the limits |
| `pulp.LpSolutionInfeasible` | -1 | proven infeasible |
| `pulp.LpSolutionUnbounded` | -2 | unbounded |

Check `prob.sol_status == pulp.LpSolutionOptimal` before you report an optimum. On a 200-item, 10-constraint knapsack with `timeLimit=2`, `LpStatus` read `Optimal` while `sol_status` was `2`.

**Satisfaction problems** (no objective) need three answers, and a time limit must not be reported as a proof of infeasibility:

```python
status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status == pulp.LpSolutionOptimal:           # satisfiable: a solution was found
    print("satisfiable")
elif pulp.LpStatus[status] == "Infeasible":             # unsatisfiable: proven
    print("unsatisfiable")
else:                                                   # a limit was hit: no answer
    print("unknown:", pulp.LpStatus[status])
```

Verified with PuLP's bundled CBC: a satisfiable model gives `Optimal` with `sol_status` 1; an unsatisfiable one gives `Infeasible` with `sol_status` -1; a model stopped by a time limit before any solution gives `Not Solved` with `sol_status` 0.

Read values only after a solve that found a solution (`sol_status` 1 or 2). After `Infeasible`, `varValue` and `pulp.value` return numbers that mean nothing. Integer outputs come back as floats (`4.0`), so round them.

Errors: a solver that cannot run raises `pulp.PulpSolverError` from `solve`; `PULP_CBC_CMD` refuses a `path=` argument for this reason (use `COIN_CMD(path=...)` for a custom binary). CBC's own messages appear in the stdout log (`msg=True`) or in `logPath`.

## All solutions

The strategy and the table of needs are in [SKILL.md](../SKILL.md#all-solutions). The cut, in PuLP:

```python
# bins: the decision binaries; k: the number of solutions found so far
ones = [b for b in bins if round(b.varValue) == 1]
zeros = [b for b in bins if round(b.varValue) == 0]
prob += pulp.lpSum(1 - b for b in ones) + pulp.lpSum(zeros) >= 1, f"no_good_{k}"
```

For all optimal solutions, keep the objective in a variable (`score = pulp.lpSum(...)`, then `prob += score`), require `sol_status == pulp.LpSolutionOptimal`, read `best = round(pulp.value(score))`, add the named pin `prob += score == best, "optimum"`, and run the loop.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `TypeError: Non-constant expressions cannot be multiplied` | `x * y`, `x * x` | encode the product ([table](../SKILL.md#encoding-the-constraints)) |
| `TypeError: bad operand type for abs()` | `abs(var)` | `d >= a - b`, `d >= b - a` with a minimisation |
| `TypeError` on `/` or `%` between variables | `x / y`, `x % 2` | encode, or use a constant divisor (`x / 2` is fine) |
| A `!=` constraint is missing, with no error | `p += x != y` adds nothing: `!=` returns a Python `True` | use the `!=` encoding |
| `UserWarning: Overwriting previously set objective` | two bare expressions added | build one objective expression |
| Output parser fails, or sees CBC log lines in the answer | `msg=True` is the default and prints CBC's log to stdout | pass `msg=False` whenever stdout is parsed; use `logPath` for the log |
| `Optimal` status, but the answer is not the optimum | time limit reached; `sol_status` is 2 | check `sol_status`; tighten the formulation or raise `timeLimit` |
| "Unsatisfiable" printed on a run that hit a time limit | `Not Solved` is not a proof of infeasibility | print "unsatisfiable" only for `LpStatus == "Infeasible"`; see the [satisfaction snippet](#solving) |
| `Not Solved`, no values after a time limit | no incumbent found in time | tighten the formulation, reduce big-M, or give more time |
| Garbage values after `Infeasible` | values are not defined | read values only when `sol_status` is 1 or 2 |
| `DeprecationWarning`: `LpVariable(...)`, `LpVariable.dicts`, `constraints` as dict | PuLP 3.3.2 deprecates these | use `add_variable`, `add_variable_dicts` and `prob.constraints()`, as in this skill |
| `x[i, j]` raises `KeyError` | nested index sets give nested dicts | write `x[i][j]` |
| `PulpSolverError` mentioning `cbc` with `COIN_CMD` | `COIN_CMD` looks for `cbc` on `PATH`, not the bundled binary | use `PULP_CBC_CMD()` |
| `PulpSolverError: Use COIN_CMD if you want to set a path` | `PULP_CBC_CMD(path=...)` | use `COIN_CMD(path=...)` for a custom `cbc` binary |
| `PULP_CBC_CMD` not found after upgrading to PuLP 4.0 | PuLP 4.0 removed it and no longer bundles CBC (from the migration guide, not run here) | pin `pulp<4`, or follow the [4.0 migration guide](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html) |
| Long model builds slowly | `sum(...)` over long lists is quadratic (0.28 s for 3,000 terms, against 0.001 s for `lpSum`) | use `pulp.lpSum` |

Symptoms that hold in every binding (big-M, enumeration, unbounded) are in [SKILL.md](../SKILL.md#common-issues).

## Further reading

- API reference: [PuLP technical reference](https://coin-or.github.io/pulp/technical/pulp.html), [solvers](https://coin-or.github.io/pulp/technical/solvers.html)
- Guides: [configure a solver](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html), [debug](https://coin-or.github.io/pulp/guides/how_to_debug.html), [warm start](https://coin-or.github.io/pulp/guides/how_to_mip_start.html), [migrate to 4.0](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html)
- Runnable patterns in `assets/python/`
