---
name: dcp-highs
description: HiGHS, a mixed-integer linear programming solver, used from C++ through its Highs class (built from source), covering columns and rows, integrality, objective, run(), model status, and enumerating solutions with no-goods. Use when writing, debugging or explaining HiGHS C++ code for MIP or LP models, linearising logic, all-different, products, min/max or absolute values for it, or choosing big-M constants.
license: MIT
compatibility: "C++: a C++17 compiler, CMake 3.15+ and HiGHS 1.15.1 built from source (github.com/ERGO-Code/HiGHS, MIT). No key, no size limits."
metadata:
  domain: optimisation
  solver: highs
  paradigm: mip
  interfaces: "cpp"
---

# HiGHS

HiGHS solves linear programs and mixed-integer linear programs. Columns (variables) and rows
(linear constraints) are added one call at a time, then a run call solves.
Every constraint must be linear: a disjunction, an all-different, a product of two variables or
a logical condition must be written as rows with binary columns and big-M constants. HiGHS
keeps no solution pool and does not enumerate: each solution is found by a new solve.

## Pick an interface

Read this file, then the interface file for your language.

| | C++ |
|---|---|
| Read | [interfaces/cpp.md](interfaces/cpp.md) |
| Package | the `Highs` class (`Highs.h`), HiGHS built from source |

Other bindings (Python `highspy`, C, Julia, ...) are not covered yet.

## Linearising logic

Start each block of rows with a comment that states the constraint in plain words, not the HiGHS call
(`every row holds different values`).
Let `M` be a big-M constant computed from the data, not a guess (see the last row).

| Pattern | Rows |
|---|---|
| one-hot: exactly one of `b_1..b_k` | `sum b_i = 1` |
| at most one | `sum b_i <= 1` |
| `b = 1` implies `a x <= r` | `a x <= r + M (1 - b)`, i.e. `a x + M b <= r + M` |
| `b = 1` implies `a x >= r` | `a x >= r - M (1 - b)` |
| `b = (x >= r)`, integer x in `lo..hi` | `x >= r b + lo (1 - b)` and `x <= (r - 1) + (hi - r + 1) b`; exact with the bounds as M |
| disjunction `a x <= r` or `c x <= s` | binary `b`: `a x <= r + M b`, `c x <= s + M (1 - b)` |
| `x != v` for integer x in `lo..hi` | binary `b` (1 means `x > v`): `x <= v - 1 + (hi - v + 1) b`; `x >= v + 1 - (v + 1 - lo) (1 - b)` |
| all different `x_1..x_n` in `lo..hi` | `y[i][v]` binary: `x_i = sum v y[i][v]`, `sum_v y[i][v] = 1`, `sum_i y[i][v] <= 1` (see [example](assets/cpp/alldifferent-binaries/README.md)) |
| product `p = b1 b2` (binaries) | `p <= b1`, `p <= b2`, `p >= b1 + b2 - 1`, `0 <= p <= 1` |
| product `p = x y`, x integer in `lo..hi`, y binary | `p <= hi y`, `p >= lo y`, `p <= x - lo (1 - y)`, `p >= x - hi (1 - y)` (p is x when y = 1, else 0) |
| `z = max(x_1..x_k)` | `z >= x_i` for all i; to force equality under minimisation, also `z <= x_i + M (1 - b_i)` with `sum b_i = 1` |
| `z = min(x_1..x_k)` | `z <= x_i` for all i; to force equality under maximisation, `z >= x_i - M (1 - b_i)`, `sum b_i = 1` |
| `z = |x|` | `z >= x`, `z >= -x`; minimising the objective needs nothing more; to force equality under maximisation add `z <= x + M b`, `z <= -x + M (1 - b)`, `b` binary |
| strict `x < y` (integers) | `x + 1 <= y` |
| big-M from data | `M = sum_j |a_j| * max(|lo_j|, |hi_j|) + |r|`, computed in the program from the input data |

Choose M from the data: the smallest value with `a x` at its extremes over the column bounds, plus the
right-hand side. A large M ruins the LP relaxation and slows the proof. Tiny M cuts off solutions. With
a schedule, the total work `H` bounds the end of a left-shifted schedule; bound each start by `H - d_j`
so that `M = H` covers every disjunction row.

## Solving

A MIP is solved to proven optimality only when the gap options are zero; the defaults are `mip_rel_gap` 1e-4 and `mip_abs_gap` 1e-6,
so set both to `0.0`. The result is a model status: optimal, infeasible, unbounded (or unbounded-or-infeasible for a MIP), time limit. Only optimal with zero gaps is a proof; a time limit is never reported as optimal. The C++ status enum names, `run()` and option calls are in [the interface file](interfaces/cpp.md#solving).

## All solutions

HiGHS has no solution pool. To list solutions of a satisfaction problem, solve, record the values `v_i` of the
integer columns `x_i` (with bounds `lo_i..hi_i`), add a no-good, and solve again until `kInfeasible`:

- for each column with `v_i > lo_i`, a binary `below_i` with `x_i + (hi_i - v_i + 1) below_i <= hi_i`
  (`below_i = 1` forces `x_i <= v_i - 1`);
- for each column with `v_i < hi_i`, a binary `above_i` with `x_i - (v_i + 1 - lo_i) above_i >= lo_i`
  (`above_i = 1` forces `x_i >= v_i + 1`);
- one row: the sum of all these binaries `>= 1`.

A binary column (`lo = 0`, `hi = 1`) needs only one indicator: the one that flips it (`x = 1` gives `below`, `x = 0` gives `above`).
If no indicator is created, every column is fixed and the enumeration is complete. Full code in
[the example](assets/cpp/all-solutions-no-good/README.md).

For all optimal solutions: solve, record the optimum `z` from `getInfo().objective_function_value`. That value
includes the offset from `changeObjectiveOffset`, and a row holds no constant, so add the row
`sum_j c_j x_j` (the cost coefficients) with bounds `z - offset - 1e-5 <= row <= z - offset + 1e-5`. Then enumerate with the same no-goods.
Only integer columns that the printed answer depends on need no-goods; each solve costs one more round, so keep
the enumerated count small.

## Common issues

Symptom to fix tables are per binding: [interfaces/cpp.md](interfaces/cpp.md#common-issues).

## Further reading

- HiGHS documentation: <https://ergo-code.github.io/HiGHS/>
