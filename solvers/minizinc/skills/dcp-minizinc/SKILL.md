---
name: dcp-minizinc
description: MiniZinc constraint modelling language solved by the Gecode constraint solver, from the command line or the minizinc-python API (package minizinc). Use when writing, running or debugging MiniZinc (.mzn) models, listing all or all optimal solutions, or using Gecode through MiniZinc.
license: Apache-2.0
compatibility: Requires MiniZinc 2.9.3 on PATH (bundles Gecode 6.3.0; free, no licence key); the Python API needs minizinc 0.10.0 and Python 3.12 (tested)
metadata:
  domain: constraint-programming
  solver: minizinc
  paradigm: cp
  interfaces: "minizinc"
---

# MiniZinc with Gecode

MiniZinc is a declarative modelling language: you state variables and constraints, and
MiniZinc flattens them to FlatZinc for a solver. Here the solver is Gecode, a
constraint-programming solver that propagates constraints and searches depth-first. Keep
one idea in mind: the model says *what* must hold, and Gecode decides *how* to search
unless you add a search annotation.

## Pick an interface

Read this file and the interface below.

| | MiniZinc (command line and Python) |
|---|---|
| Read | [interfaces/minizinc.md](interfaces/minizinc.md) |
| Package | `minizinc` executable (bundles Gecode); the optional `minizinc` Python package drives it |

Other bindings (the Julia and JavaScript packages, the C++ API) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

Full list: [language specification](https://docs.minizinc.dev/en/2.9.3/spec.html) ·
[global constraints](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) ·
[scheduling globals](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html)

| Need | Syntax |
|---|---|
| integer variable with domain | [`var 1..10: x;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| boolean variable | [`var bool: b;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| array of variables | [`array[1..n] of var 1..n: x;`](https://docs.minizinc.dev/en/2.9.3/spec.html), 2-D: `array[1..n, 1..m] of var 0..5: g;` |
| data parameter | [`int: n;`](https://docs.minizinc.dev/en/2.9.3/spec.html), value from a `.dzn` file or from Python |
| all different | [`all_different(x)`](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) after `include "globals.mzn";` |
| index an array by a variable | `c[x] = 7`, where `c` is a constant array (element) |
| allowed tuples | [`table([x, y], [\| 1, 2 \| 2, 3 \|])`](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) |
| shared resource over time | [`cumulative(s, d, r, cap)`](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html) |
| no overlap of tasks | [`disjunctive(s, d)`](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html); one machine's tasks: `disjunctive([s[t] \| t in 1..T where mach[t] = m], [dur[t] \| t in 1..T where mach[t] = m])` ([jobshop](assets/minizinc/jobshop/model.py)) |
| minimise a maximum | bound each term by a variable (`s[t] + dur[t] <= makespan`), then `solve minimize makespan;` |
| reification | [`b <-> (x < y);`](https://docs.minizinc.dev/en/2.9.3/spec.html) (also `b -> c`, `/\`, `\/`) |
| count of true booleans | [`sum(i in 1..n)(bool2int(b[i]))`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| integer division, modulo | `div`, `mod`; `/` yields a float and is refused in integer context |
| minimise / maximise | [`solve minimize expr;`](https://docs.minizinc.dev/en/2.9.3/spec.html), `solve maximize expr;` |
| satisfaction | [`solve satisfy;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| print values | [`output ["x = ", show(x), "\n"];`](https://docs.minizinc.dev/en/2.9.3/spec.html); 2-D: `showJSON(g)` |

Bound every `var`; an unbounded `var int` gets the solver's 32-bit range.

### One-sided bounds

MiniZinc 2.9.3 can flatten a model in which an auxiliary variable is bounded from one side
only, so that the variable doing the bounding drops out of another constraint. Shape:
`bool2int(covered[j]) <= sum(i)(delta[i, j] * bool2int(build[i]))` together with a budget
on `build`. The flattened model then lets `build[i]` take any value, and the solver reports
a solution that breaks the budget. The fix is to state the relation as an equivalence:

```minizinc
constraint forall(j in Regions)(covered[j] <-> exists(i in Sites)(delta[i, j] = 1 /\ build[i]));
```

Use the equivalence whenever the one-sided bound is tight at every solution you may report.
To confirm, compile with `minizinc --solver gecode -c model.mzn` and check that each variable
appears in some constraint.

### Implied constraints

When Gecode runs out of time, the cause is often weak propagation. Add constraints that every
solution satisfies but Gecode cannot derive. Example: if `x ++ y` is a permutation of `1..n`
and `sum(x) = sum(y)`, then `4 * sum(x) = n * (n + 1)` holds in every solution. Never add a
constraint that removes solutions to gain speed: a narrower model can be fast and still wrong.

## Solving

| Outcome | CLI output | Meaning |
|---|---|---|
| optimum proven, or all solutions enumerated | `==========` after the last solution | optimal for an optimisation model; with `-a` (see [All solutions](#all-solutions)) the complete enumeration of a satisfaction model |
| solution found, search stopped early | `----------` with no `==========` | time limit hit; optimality or the rest of the space is unproven |
| proven infeasible | `=====UNSATISFIABLE=====` | the whole search space was explored; no solution |
| unknown | `=====UNKNOWN=====` | the limit was reached before any solution |

Options: CLI [`--time-limit <ms>`](https://docs.minizinc.dev/en/2.9.3/command_line.html),
`-s`, `-d data.dzn`, `-c`. The Python statuses and result reading are in [interfaces/minizinc.md](interfaces/minizinc.md#solving).

Search annotations, for example `solve :: int_search(x, input_order, indomain_min, complete) satisfy;`,
override Gecode's default search: [search annotations](https://docs.minizinc.dev/en/2.9.3/mzn_search.html).

## All solutions

`minizinc --solver gecode -a model.mzn` lists every solution of a satisfaction model, `-n k` the
first k. On a minimise or maximise model `-a` prints one optimum, not all optimal solutions.

**All optimal solutions.** The command line prints one optimum under `-a`, and the Python binding
refuses `all_solutions` on an optimisation model, so in both:
solve `solve minimize objective;` and confirm optimality; add `int: best;` and
`constraint objective = best;` and change the solve item to `solve satisfy;`; assign `best` the
optimum and enumerate. Code and the duplicate-solution caveat: [interfaces/minizinc.md](interfaces/minizinc.md#all-solutions).

Details: [enumeration in the command line](https://docs.minizinc.dev/en/2.9.3/command_line.html)

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `syntax error, unexpected opt, expecting identifier` | `opt` is a reserved word | rename the variable (`best`); other keywords fail the same way |
| `no function or predicate with name 'all_different'` | `include "globals.mzn";` missing | add the include |
| `cannot determine coercion from type float to type var int` | `/` on integers | use `div` |
| `lower bound of empty array undefined` | a `where` comprehension selects no element, e.g. a machine count `M` above the machines in use | use `M = max(mach)`, or guard the loop with `where exists(t in 1..T)(mach[t] = m)` |
| `TypeError` iterating `result.solution` | a plain `solve` found no solution, so `result.solution` is `None` | check `result.status.has_solution()` first; with `all_solutions=True` the list is empty instead |
| `Warning: model inconsistency detected` then `UNSATISFIABLE` | the domains and constraints contradict each other directly, e.g. `x > 5` with `var 0..3` | fix the model; it is not a solver fault |
| objective reported as `2147483646` | a variable without bounds, so the solver used the 32-bit range | bound every variable |
| `=====UNKNOWN=====` on a larger instance | propagation too weak | see [Implied constraints](#implied-constraints) |
| a solution that breaks a constraint you wrote | one-sided bound flattened away | see [One-sided bounds](#one-sided-bounds) |

## Further reading

- MiniZinc handbook, 2.9.3: [docs.minizinc.dev/en/2.9.3](https://docs.minizinc.dev/en/2.9.3/) (start with [Tutorial](https://docs.minizinc.dev/en/2.9.3/part_2_tutorial.html) and [Efficiency](https://docs.minizinc.dev/en/2.9.3/efficient.html))
- Global constraint catalogue: [lib-globals](https://docs.minizinc.dev/en/2.9.3/lib-globals.html)
- minizinc-python API: [python.minizinc.dev/en/latest/api.html](https://python.minizinc.dev/en/latest/api.html)
- Gecode documentation and reference: [gecode.org/doc-latest](https://www.gecode.org/doc-latest/) ([Modeling and Programming with Gecode](https://www.gecode.org/doc-latest/MPG.pdf))
- Examples: the `assets/` folder; each subfolder is one pattern, runnable on its own.
