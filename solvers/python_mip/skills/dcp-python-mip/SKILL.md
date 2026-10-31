---
name: dcp-python-mip
description: Python-MIP (import mip), a Python library for linear and mixed-integer programs, solved by its default solver CBC. Use when writing, debugging or explaining Python-MIP models, when a linear or integer program must be solved in Python with mip or CBC, when a logical or combinatorial constraint needs binaries and big-M encodings, or when enumerating all or all optimal solutions.
license: Apache-2.0
compatibility: Requires Python 3.10+ and mip (tested with 2.0.0, which installs cbcbox for CBC). No licence limits for CBC. Gurobi is used only if gurobipy is installed.
metadata:
  domain: constraint-programming
  solver: cbc
  paradigm: mip
  interfaces: "python"
---

# Python-MIP

Python-MIP builds a mixed-integer linear model and solves it with CBC. Keep one idea in mind: **every constraint and the objective must be linear**. Products of variables, `abs`, `min`, `max` and `!=` need the encodings in [Encoding the constraints](#encoding-the-constraints).

## Pick an interface

Read this file and the one interface below that matches the language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `mip` (Python-MIP 2.0.0; CBC from the `cbcbox` wheel) |

Other bindings (the CBC and HiGHS libraries directly, other modelling layers) are not covered yet.

## Contents
- [Encoding the constraints](#encoding-the-constraints)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Making CBC faster](#making-cbc-faster)
- [Further reading](#further-reading)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Encoding the constraints

`M` is a constant at least as large as the most the expression can exceed its bound. Compute it from the data: `M = max(L - R)` over the variable bounds. Too small an `M` cuts off solutions silently; a larger valid `M` only weakens the relaxation. Give every integer variable finite bounds from the data (`ub=`).

| Constraint | Linear form (`b`, `c`, `s`, `p`, `q` are binaries) |
|---|---|
| `x != v`, `x` integer in `lo..hi`, one binary `b` (`b = 1` means `x > v`) | `x <= v - 1 + (hi - v + 1) * b` and `x >= v + 1 - (v + 1 - lo) * (1 - b)` |
| `c = 1` implies `L <= R` | `L <= R + M * (1 - c)` |
| `c = 1` if and only if `x >= t`, `x` in `lo..hi` | `x >= t - (t - lo) * (1 - c)` and `x <= (t - 1) + (hi - t + 1) * c` ([example](assets/python/encodings/README.md)) |
| `d = abs(a - b)`, minimised | `d >= a - b`, `d >= b - a` |
| `d = abs(a - b)`, maximised | binary `s`: `d <= a - b + M * (1 - s)`, `d <= b - a + M * s` |
| `z = min(x, y)`, exact | binary `s`: `z <= x`, `z <= y`, `z >= x - M * (1 - s)`, `z >= y - M * s` |
| `z = max(x, y)`, exact | binary `s`: `z >= x`, `z >= y`, `z <= x + M * (1 - s)`, `z <= y + M * s` |
| `min` maximised, or `max` minimised (no binary needed) | `z <= x`, `z <= y` (or `z >= x`, `z >= y`) |
| `z = p * q`, binaries | `z <= p`, `z <= q`, `z >= p + q - 1` |
| `w = b * x`, `x` integer in `lo..hi` | `w <= hi * b`, `w >= lo * b`, `w <= x - lo * (1 - b)`, `w >= x - hi * (1 - b)` |
| `x` takes one value of `{v1, ..., vk}` | binaries `p[j]`: `sum p[j] == 1`, `x == sum vj * p[j]` |
| all different `x_0..x_{n-1}` with values in a set `V` (for example `range(lo, lo + k)`, or any list) | `p[i][v]` binary for `v` in `V`: `sum_v p[i][v] == 1`, `x_i == sum_v v * p[i][v]`, `sum_i p[i][v] <= 1` for each `v`. Values are the actual numbers, so an offset needs no change. Needs `k = len(V) >= n`, otherwise infeasible |
| `x < v` on integers | `x <= v - 1` (and `x > v` is `x >= v + 1`) |
| either `L1 <= R1` or `L2 <= R2` | binaries `b1 + b2 >= 1`, `L1 <= R1 + M1 * (1 - b1)`, `L2 <= R2 + M2 * (1 - b2)` |
| two jobs do not overlap on one machine | binary `o`: `s_j >= s_i + d_i - H * (1 - o)`, `s_i >= s_j + d_j - H * o`. `H` = sum of all durations, and bound each start by `s_i <= H - d_i` (valid without release dates, because some optimal schedule is left-justified). With release dates `r_i`, use `H` = latest release + sum of durations and `r_i <= s_i <= H - d_i` |
| `v = T[idx]` for a table `T` | binaries `ch[k]`: `sum ch[k] == 1`, `idx == sum k * ch[k]`, `v == sum T[k] * ch[k]` |

Worked code: [encodings](assets/python/encodings/README.md), [single-machine-schedule](assets/python/single-machine-schedule/README.md) (no overlap, big-M from data), [latin-square](assets/python/latin-square/README.md) (all different with binaries), [graph-colouring](assets/python/graph-colouring/README.md).


## All solutions

No-good cuts over the decision binaries enumerate the solutions; the loop is in the interface file.

- Cut only over the variables that define the answer. An auxiliary variable in the cut gives duplicate answers.
- Integer decisions need binaries before a cut (one-hot per value), or two binaries per variable (below and above the current value) with finite bounds.
- All **optimal** solutions: solve, require `OPTIMAL`, store `best = m.objective_value`, add `m += m.objective >= best - 1e-6` and `m += m.objective <= best + 1e-6`, then run the loop above ([all-optimal-committee](assets/python/all-optimal-committee/README.md)).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `OPTIMAL`, but a better solution exists | default `max_mip_gap` 1e-4 | set `max_mip_gap` and `max_mip_gap_abs` to 0 |
| Enumeration repeats answers or never ends | cut over auxiliary variables, or unbounded integers | cut only decision binaries; bound every integer |
| Wrong answer after a disjunction or `!=` | `M` too small | compute `M` from the bounds |
| `FEASIBLE` or `NO_SOLUTION_FOUND` on a hard model | time limit reached | the answer is not proven; say so or raise `max_seconds` |
| `OPTIMAL`, but the point breaks a row by about 1 | coefficients around 1e6 or larger and CBC's presolve | `m.preprocess = 0` |

Binding-specific issues: [Python](interfaces/python.md#common-issues).

## Making CBC faster

CBC is slow per node, so the encoding matters more than settings:

- Ordered comparisons between many values: use order (thermometer) binaries `ge[t]` (monotone, `value = lo + sum ge[t]`) instead of one-hot with big-M.
- Permutation or all-different puzzles with long ranges: pairwise order binaries (one binary per pair, big-M from the range) sometimes beat one-hot rows.
- Pair, link or product variables tied to one-hot or binary decisions (`w >= p_a + p_b - 1`) can be continuous in `[0, 1]`; only the decisions stay integer. This shrank the search tree on set-cover and labelling problems.
- Variables that stand for the same quantity under several index tuples can share one binary (for example a pair image `p[a, b, k, l]` for all four equivalent tuples).
- Digit puzzles with sums: use column addition with integer carries, not one equation with place values (the place-value relaxation is weak and the second solve takes long).
- Many resource rows over time: add clique rows `sum active_i(t) <= 1` over jobs that cannot run together; they are much tighter than pairwise big-M rows.
- Optimisation over a count of used colours or labels numbered from 1: minimise the largest number, because a set like `{1, 2, 3, 5}` uses four colours but its largest number is 5.
- Enumeration cuts: the cut over binaries is much cheaper than over wide integer outputs. Use the one-hot binaries as the cut variables and compute the integer value from them.
- A state-transition problem (water buckets, moves over a board): a time-expanded flow over an enumerated state table, one binary per state and step, solves much faster than big-M pour variables.

## Further reading

- Documentation: [Python-MIP site](https://www.python-mip.com), [user guide and API](https://python-mip.readthedocs.io/en/latest/)
- API reference: [classes, status values and parameters](https://python-mip.readthedocs.io/en/latest/classes.html)
- Source and issues: [coin-or/python-mip](https://github.com/coin-or/python-mip)
