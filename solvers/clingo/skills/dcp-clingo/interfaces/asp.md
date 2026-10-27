# clingo in Python (clingo package)

The Python API of clingo: `clingo.Control` holds a program, grounds it and solves it. What holds in every interface (the language, aggregates, outcomes, enumeration strategy, language pitfalls) is in [SKILL.md](../SKILL.md).

## Install

```bash
pip install clingo
python3 -c "import clingo; print(clingo.__version__)"
```

Tested with clingo 5.8.2 on Python 3.12. The package is a CFFI wheel with no licence key or account. Details: [clingo installation](https://potassco.org/clingo/) and the [Python API](https://docs.potassco.org/clingo/python-api/current/).

## Quick start

```python
import clingo

ctl = clingo.Control()
ctl.add("base", [], """
colour(red;green).
node(1..3).
edge(1,2). edge(2,3).
1 { paint(N,C) : colour(C) } 1 :- node(N).
:- edge(A,B), paint(A,C), paint(B,C).
#show paint/2.
""")
ctl.ground([("base", [])])
with ctl.solve(yield_=True) as handle:
    for model in handle:
        print(sorted(str(atom) for atom in model.symbols(shown=True)))
    print("satisfiable:", handle.get().satisfiable)
```

Output: one list of `paint(...)` atoms, then `satisfiable: True`.

## Solving

Settings: [command-line options](https://potassco.org/guide/options) · [Python API](https://docs.potassco.org/clingo/python-api/current/)

| Want | Setting |
|---|---|
| one model (default) | `ctl.configuration.solve.models = 1` |
| every model | `ctl.configuration.solve.models = 0` |
| one model per shown answer | `ctl.configuration.solve.project = "show"` |
| optimisation with proof | `ctl.configuration.solve.opt_mode = "optN"` |
| threads | `clingo.Control(["-t", "4"])` |
| random seed | `ctl.configuration.solver.seed = "7"` or `Control(["--seed=7"])` |

Set options before grounding; pass them to `clingo.Control(...)` or assign them to `ctl.configuration` in a variable. Reading a value back from a temporary `Control` (`clingo.Control(...).configuration...`) crashed the interpreter (exit 139) with clingo 5.8.2 (Python module); keep the object in a variable.

Solve result, from `handle.get()` after the loop ([`SolveResult`](https://docs.potassco.org/clingo/python-api/current/)):

| Attribute | Meaning |
|---|---|
| `satisfiable` | at least one model found |
| `unsatisfiable` | no model exists (proven) |
| `exhausted` | the search finished, so no further models exist |
| `interrupted` | stopped early by `cancel()` or a time limit |
| `unknown` | neither satisfiable nor unsatisfiable (for example, interrupted before any result) |

Reading models: `model.symbols(shown=True)` returns the shown atoms; `atom.name` and `atom.arguments` split them (`atom.number` on an integer argument, `atom.string` on a string, `str(atom)` for the text). `model.contains(clingo.parse_term("q(3)"))` tests one atom. Build terms with `clingo.Function`, `clingo.Number`, `clingo.String` or `clingo.parse_term`. The constants `true` and `false` arrive as `Function` symbols with no arguments.

One model with the default `models = 1`, then check the result:

```python
with ctl.solve(yield_=True) as handle:
    digits = None
    for model in handle:            # at most one iteration with models = 1
        digits = {a.arguments[0].string: a.arguments[1].number for a in model.symbols(shown=True)}
    result = handle.get()
if not result.satisfiable:
    print("no solution")
```

Time limit, run in a background thread and cancelled after `seconds`:

```python
handle = ctl.solve(async_=True, yield_=True)
handle.wait(seconds)
handle.cancel()
result = handle.get()     # result.interrupted is True if the limit hit
```

Errors: a syntax error raises `RuntimeError: parsing failed` from `ctl.add`; an unsafe rule or a grounding error raises `RuntimeError: grounding stopped because of errors` from `ctl.ground`. The detailed message goes to stderr, for example `<block>:1:1-14: error: unsafe variables in: ...`. ASP programs written as Python strings report line and column inside that string.

## Optimisation

Without `opt_mode`, clingo stops at the first model it finds, and that model is not proven optimal (`optimality_proven` is False). Set `opt_mode = "optN"` and clingo keeps improving the model and proves the optimum. With the default `models = 1`, the last model yielded is then the proven optimum:

```python
ctl.configuration.solve.opt_mode = "optN"    # models = 1 is the default
with ctl.solve(yield_=True) as handle:
    best = None
    for model in handle:                     # improving models; the last one is optimal
        best = model
    result = handle.get()
optimal = result.exhausted and best is not None and best.optimality_proven
# model.cost is a list with one entry per priority level; best.cost[0] is the optimum.
# For #maximize the cost is the negated value, so negate it back.
```

`models = 0` with `optN` also yields every optimal model, and it has to search for all of them. On a 6x6 job shop (ft06, optimum 55) an independent run with `models = 0` timed out at 120 s, while `models = 1` with `optN` proved the optimum in about 23 s. Use `models = 0` only when every optimal model is wanted (see [All solutions](#all-solutions)); then keep the models whose `optimality_proven` is true.

If the solve is interrupted by a time limit, the last model may be unproven. Check `optimality_proven`: an unproven model is only the best found so far.

Worked, runnable examples: [assets/maximise](../assets/asp/maximise/README.md), [assets/minimise](../assets/asp/minimise/README.md), [assets/scheduling](../assets/asp/scheduling/README.md).

### Scheduling at scale

The [scheduling example](../assets/asp/scheduling/README.md) gives each task one start time in `time(0..H)` and forbids overlaps pairwise. Grounding and search both grow with the number of tasks and with `H`. Ways to keep them small:

- **Horizon.** The sum of all durations is always a valid makespan bound for one machine or a job shop, since everything can run in sequence. A smaller `H` shrinks the domains but can exclude the optimum; use it only when a feasible makespan at or below `H` is known.
- **Tighter domains.** Limit each start to times where the task still ends inside the horizon:

  ```prolog
  1 { start(T,S) : time(S), S + D <= H } 1 :- task(T), dur(T,D), h(H).
  ```

- **Models.** Use `opt_mode = "optN"` with `models = 1`, as above. In that measurement, `models = 0` was the cause of the timeout; the domain limit alone did not change the 120 s run.

Measured: the 6x6 job shop (36 tasks, optimum 55) solved to a proven optimum in about 23 s with this encoding, and grounding took about 1 s. No larger instance was measured, so expect longer solves beyond that size.
## All solutions

Set `models = 0` and `project = "show"`. Without projection, clingo lists every combination of auxiliary atoms separately: the subset example in [assets/all-solutions](../assets/asp/all-solutions/README.md) reports 20 models without projection and 4 with it.

```python
ctl.configuration.solve.models = 0
ctl.configuration.solve.project = "show"
with ctl.solve(yield_=True) as handle:
    answers = [sorted(str(a) for a in m.symbols(shown=True)) for m in handle]
    result = handle.get()        # result.exhausted is True when enumeration finished
```

All **optimal** solutions: combine `opt_mode = "optN"`, `models = 0` and `project = "show"`, and keep only the models with `optimality_proven`. See [assets/all-optimal](../assets/asp/all-optimal/README.md). Details: [enumeration and optimisation](https://potassco.org/guide/basics/).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Optimum search times out, or enumerates many models | `models = 0` with `optN` searches for every optimal model | `opt_mode = "optN"` with the default `models = 1`; use `models = 0` only for all optima |
| Last model has `optimality_proven` False | No `opt_mode`, or the run was interrupted by a time limit | Set `opt_mode = "optN"`; treat an interrupted result as a bound, not an optimum |
| Scheduling model too slow to finish | Horizon far above a feasible makespan, unrestricted start domains, or `models = 0` | Use the sum of durations as `H`, limit `S + D <= H`, and `models = 1` with `optN` |
| `python support not available` | `#script(python)` in a program | Not supported in the pip wheel; express the logic in rules |
| Interpreter exits with code 139 | Reading a configuration value from a temporary `Control` | Keep the `Control` in a variable first |

## Runnable examples

Each folder under `assets/` is a standalone program with its README.

| Example | Pattern |
|---|---|
| [satisfy](../assets/asp/satisfy/README.md) | one model: graph colouring with a bounded choice and a constraint |
| [all-solutions](../assets/asp/all-solutions/README.md) | every model, with projection |
| [all-optimal](../assets/asp/all-optimal/README.md) | every optimal model, `optN` with proof check |
| [maximise](../assets/asp/maximise/README.md) | knapsack with `#maximize` |
| [minimise](../assets/asp/minimise/README.md) | vertex cover with `#minimize` |
| [infeasible](../assets/asp/infeasible/README.md) | pigeonhole: no model, `unsatisfiable` |
| [cryptarithm](../assets/asp/cryptarithm/README.md) | uppercase letters as strings, weighted `#sum` with negative weights, one model read in a loop |
| [scheduling](../assets/asp/scheduling/README.md) | single machine: start times, non-overlap, `#max` makespan |
