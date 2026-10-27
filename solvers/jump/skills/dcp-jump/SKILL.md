---
name: dcp-jump
description: JuMP, the Julia modelling language for optimisation, with HiGHS as its mixed-integer linear programming solver (Julia, packages JuMP and HiGHS.jl). Use when writing, debugging or explaining JuMP models, reading JSON instances, reformulating all-different, table, circuit or indicator constraints for HiGHS, linearising products and disjunctions, or enumerating and proving optimal solutions.
license: Apache-2.0
compatibility: "Julia: Julia (tested with 1.12.7) and the JuMP, HiGHS.jl and JSON packages (tested with JuMP 1.32.0, HiGHS.jl 1.26.0, JSON 1.10.0); all are free and open source, with no licence key or size limit"
metadata:
  domain: constraint-programming
  solver: HiGHS
  paradigm: mip
  interfaces: "julia"
---

# JuMP (HiGHS)

JuMP is an algebraic modelling language: you write variables, constraints and an objective, attach a solver, and read the results back. HiGHS solves **linear** constraints and objectives over integer and continuous variables. JuMP reformulates a few constraint sets into linear ones; everything else must be linearised by hand.

## Pick an interface

Read this file, then the interface file for your language.

| | Julia |
|---|---|
| Read | [interfaces/julia.md](interfaces/julia.md) |
| Package | `JuMP` with `HiGHS` (HiGHS.jl) |

Other bindings (JuMP is Julia-only; the Python modelling layers over HiGHS are different APIs) are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [Julia](interfaces/julia.md); sources in [sources.md](sources.md)

## Modelling

The calls for each construct are in the interface file. Everything is linear: JuMP reformulates the sets `AllDifferent`, `Table`, `Circuit`, `CountDistinct`, `CountBelongs`, `SOS1` and indicator constraints into linear ones.

These sets need **finite bounds** on their variables (see [Common issues](#common-issues)). Not available: `MOI.Reified`, a product of two variables in a constraint or the objective, and `!=` (use the linearisations below).

`AllDifferent` over expressions is enforced, not ignored: `[q[i] + i ...] in MOI.AllDifferent(n)` is OPTIMAL when the queens fit (n = 4, 8) and INFEASIBLE for n = 3.

### Linearisations

| Need | Linear form |
|---|---|
| product of binaries `z = a * b` | `z <= a`, `z <= b`, `z >= a + b - 1` |
| binary times bounded integer `z = b * x`, `0 <= x <= U` | `z <= U * b`, `z <= x`, `z >= x - U * (1 - b)`, `z >= 0` |
| `x` takes value `v` | one `Bin` per value, `sum(is) == 1`, `x == sum(v * is[v] for v in values)` |
| `x != y` | `[x, y] in MOI.AllDifferent(2)` (bounded), or binary `s` with `x - y >= 1 - M * s` and `y - x >= 1 - M * (1 - s)` |
| disjunction of linear constraints | one binary per case, an indicator per case, `sum(cases) >= 1` |
| `d = abs(x - y)` | `d >= x - y`, `d >= y - x` is exact only when `d` is minimised; otherwise binary `s` with `d <= x - y + M * s`, `d <= y - x + M * (1 - s)` |
| value picked by an index variable `c[i]` | the per-value binaries of `i`, `sum(c[v] * is[v] for v in values)` |
| "minimise the number of classes" (colouring) | `x[i, c]` binary per item and class, `sum(x[i, c] for c) == 1`, `x[i, c] + x[j, c] <= 1` per conflict, `x[i, c] <= used[c]`, minimise `sum(used)`; see [graph-colouring](assets/julia/graph-colouring/README.md) |

Keep every big-M as small as the variable bounds allow: a loose one slows HiGHS and can make the numerics wobble. The [scheduling example](assets/julia/scheduling/README.md) uses the disjunction pattern.

The colour-class model is symmetric: any permutation of colours is a solution, which slows large instances. Setting `K` to the number of colours of a greedy colouring (an upper bound) instead of the number of nodes keeps the model correct and smaller.


## Solving

Termination statuses (JuMP names): [JuMP solutions manual](https://jump.dev/JuMP.jl/stable/manual/solutions/). HiGHS options: [HiGHS documentation](https://ergo-code.github.io/HiGHS/stable/).

| Status | Meaning |
|---|---|
| `OPTIMAL` | Proven optimal; for a model without objective, a feasible point was found |
| `INFEASIBLE` | Proven that no solution exists; `has_values` is `false` |
| `INFEASIBLE_OR_UNBOUNDED` | HiGHS cannot tell which; typically an unbounded objective, so bound the variables |
| `TIME_LIMIT` | Limit reached. Check `has_values` before reading values: an incumbent may exist |


Settings, reading results and where errors appear: [Julia](interfaces/julia.md#settings-and-reading-results).

## All solutions

HiGHS returns one solution per solve. To list all solutions, solve, record the values, forbid that assignment with a **no-good cut**, and repeat until the status is `INFEASIBLE`. Cut over the **decision variables** only: two auxiliary assignments (totals, indicators) can give the same decisions, and cutting over the auxiliaries reports duplicates.

| Variables in the cut | Cut forbidding assignment `a` |
|---|---|
| binaries | `sum(v for v with a = 0) + sum(1 - v for v with a = 1) >= 1` |
| bounded integers | per variable a disjunction `v >= a + 1` or `v <= a - 1`, chosen by binaries, with `M = upper - lower + 1`; full code in [all-solutions](assets/julia/all-solutions/README.md) |

Integer variables without both bounds cannot be cut: bound them first.

**All optimal solutions:** solve, take the optimum `best`, add `obj_expr == best`, call `set_objective_sense(model, MOI.FEASIBILITY_SENSE)`, then enumerate as above. See [all-optimal](assets/julia/all-optimal/README.md).

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `Unsupported operator != cannot be interpreted as a constraint` | JuMP has no `!=` constraint | use a linearisation from [Linearisations](#linearisations) |
| `Constraints of type ScalarQuadraticFunction ... are not supported` | product of two variables | linearise `z = a * b` |
| `BridgeRequiresFiniteDomainError` | a variable in an `AllDifferent`, indicator or other set has no finite bound | add both bounds |
| `MethodError` for `MOI.Reified` | not available in JuMP | use an indicator constraint `b --> {...}` |
| `INFEASIBLE_OR_UNBOUNDED` or unexpected `TIME_LIMIT` | unbounded variables, or a loose big-M | bound the variables; shrink each M to the bounds |

Binding syntax issues (packages, scoping, indexing, printing): [Julia](interfaces/julia.md#common-issues).

## Further reading

- JuMP manual: <https://jump.dev/JuMP.jl/stable/>
- JuMP API reference: <https://jump.dev/JuMP.jl/stable/api/JuMP/>
- MathOptInterface standard sets (the `MOI.*` names above): <https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/>
- HiGHS options: <https://ergo-code.github.io/HiGHS/stable/>
- JSON.jl: <https://github.com/JuliaIO/JSON.jl>
- Julia scoping rules (the top-level loop trap): <https://docs.julialang.org/en/v1/manual/variables-and-scoping/>
