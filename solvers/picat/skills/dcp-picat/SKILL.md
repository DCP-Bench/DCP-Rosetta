---
name: dcp-picat
description: Picat, a logic-based language whose constraint modules cp and sat solve finite-domain and SAT-encoded problems. Use when writing, debugging or explaining Picat models with cp or sat, or when a user has chosen Picat for a constraint or optimisation problem.
license: Apache-2.0
compatibility: Requires Picat 3.9#12 (free for any use; C sources under MPL 2.0) and a Linux, macOS or Windows host. The mip and smt modules need external solvers and are not covered.
metadata:
  domain: constraint-programming
  solver: picat
  paradigm: cp
  interfaces: "picat"
---

# Picat (cp and sat)

Picat is a rule-based language with a constraint library. A model states variables, domains and constraints; `solve` searches for values. Constraint operators such as `#=` and `::` post constraints at once, while an arithmetic expression outside a constraint is computed at once. Keep that split in mind and most errors are avoided.

## Pick an interface

Read this file, then the interface file.

| | Picat |
|---|---|
| Read | [interfaces/picat.md](interfaces/picat.md) |
| Package | the `picat` executable with its library modules (`cp`, `sat`, `util`, ...); the models are written in Picat itself |

Other bindings (a host-language API for Picat) are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [Picat](interfaces/picat.md), with install, quick start, exact calls and the traps of the language; sources in [sources.md](sources.md)

## Modelling

Full list of constraints: [Picat guide, constraints chapter](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

| Need | Picat |
|---|---|
| integer variable with domain | [`X :: 1..N`](https://picat-lang.org/download/picat_guide_html/picat_guide.html), `X :: [1,3,5]`, `X notin [2,4]` |
| list of variables | `new_list(N)`, then `Xs :: 0..9`; two-dimensional: `new_array(R, C)` |
| all different | [`all_different/1`](https://picat-lang.org/download/picat_guide_html/picat_guide.html) (`all_distinct/1` propagates more in `cp`) |
| element lookup (1-based) | [`element/3`](https://picat-lang.org/download/picat_guide_html/picat_guide.html), `element0/3`, `matrix_element/4` |
| table | `table_in/2`, `table_notin/2` |
| counting | `count/4`, `global_cardinality/2`, `nvalue/2` |
| cumulative / no-overlap | `cumulative/4`, `serialized/2`, `diffn/1` |
| circuit | `circuit/1`, `subcircuit/1` |
| sequences | `regular/6`, `increasing/1`, `decreasing/1`, `lex_le/2` |
| reification / implication | `#<=>`, `#=>`, `#\/`, `#/\`, `#~` |
| conditional value | `V #= cond(C, Then, Else)` |
| minimise / maximise | `$min(Expr)` / `$max(Expr)` as an option, see [Solving](#solving) |

Write `$min` and `$max` with the `$`: without it, `min(...)` is a call to the function `min` and nothing is optimised. Arithmetic inside a constraint stays a term, so `X + Y #= N` is fine; outside one it is computed at once (see [Common issues](interfaces/picat.md#common-issues)).

Operators to get right: `**` is power (`10**2` is `100`) and works inside a `cp` constraint (`Z #= 2 ** X`); `^` is bitwise XOR (`10^2` is `8`), and inside a constraint it raises `invalid_constraint_expression`. See [Writing Picat correctly](interfaces/picat.md#writing-picat-correctly).

Each constraint row above is the library's name; the full reference is in the [guide](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

## Solving

Official: [solving options](https://picat-lang.org/download/picat_guide_html/picat_guide.html) (common options, `cp` options, `sat` options). The calls are in [interfaces/picat.md](interfaces/picat.md).

| Outcome | How it shows |
|---|---|
| Solution found | `solve` succeeds; variables are bound |
| Infeasible | `solve` fails, or posting a constraint fails. Test with `if ... then ... else ... end` |
| Optimum | `solve` with `$min`/`$max` gives the optimal values; Picat searches until the value is proven |
| Time limit | `time_out(solve(Vars), Millis, Res)`: `Res` is `success` or `time_out` ([sys module](https://picat-lang.org/modules.html)) |

Read values by printing the bound variables (`println(X)`). An unbound variable prints as a name like `_123`, which means a missing domain or label. Options for `cp` include `ff`, `ffc`, `down`, `split`, `rand`; `sat` accepts them without effect. Full lists: [solving options](https://picat-lang.org/download/picat_guide_html/picat_guide.html).


**Choosing `cp` or `sat`.** Both modules take the same constraints, so switching is the `import` line. `cp` propagates and searches; `sat` compiles the model to clauses for a SAT solver. Neither is faster in general. When one times out, the other is a fair try.

## All solutions

Enumerate only the decision variables: an auxiliary variable that differs makes two solutions look distinct. The enumeration calls are in [interfaces/picat.md](interfaces/picat.md#all-solutions).

**All optimal solutions.** Solve once with the objective to prove the optimum, rebuild the model (bindings from the first solve cannot be undone), post `Obj #= Optimum`, then enumerate. A builder predicate keeps the two copies identical. See `assets/picat/all-optimal-vertex-covers/`.

## Common issues

Solver-level ones; symptoms of the Picat syntax are in [interfaces/picat.md](interfaces/picat.md#common-issues).

| Symptom | Likely cause | Fix |
|---|---|---|
| `sat` returns assignments that break an equality with `all_different` over sums of 0/1 variables | defect in `sat` with `all_different/1` over such variables; `cp` is correct | write the pairwise form `foreach (I in 1..N-1, J in I+1..N) Z[I] #!= Z[J] end`, or use `import cp.` |
| Search takes too long | labelling order or weak propagation | try the other module, add `ff`, tighten domains, add a redundant constraint, or use a global constraint |

## Further reading

- Picat guide (HTML): https://picat-lang.org/download/picat_guide_html/picat_guide.html
- Picat guide (PDF): https://picat-lang.org/download/picat_guide.pdf
- Modules and library reference: https://picat-lang.org/modules.html
- Downloads and releases: https://picat-lang.org/download.html
