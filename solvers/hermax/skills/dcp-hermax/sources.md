# Sources for `hermax`

## Shared

Documentation and package: see the links below; tested versions are under Python.

## Python

Tested with hermax 1.3.0 (with python-sat 1.9.dev17), Python 3.12.11, Linux, inside the
`python:3.12.11-slim-bookworm` image with `pip install hermax==1.3.0`. The earlier rounds
below were run on hermax 1.2.9; the 1.3.0 round lists what changed.

Documentation:

- <https://hermax.readthedocs.io/en/latest/> — documentation index: quick start, modelling,
  portfolio, incremental solvers, API reference, examples
- <https://github.com/josalhor/hermax> — repository and README (modelling example,
  `m.obj` soft-clause usage, `solve`, `result.status`/`result.cost`)
- <https://pypi.org/project/hermax/> — package metadata (Apache-2.0)
- <https://hermax.readthedocs.io/en/latest/acknowledgments.html> — backend solver credits

Verified on hermax 1.3.0 (inside the image):

- `m.obj[w] += lit` raises `TypeError: obj[w] is no longer supported`; `m.obj += 5 * l`
  leaves `l` false at cost 0, `m.obj += 5 * ~l` sets it true; `m.obj += -x`, `-1 * x` and
  `-sum(...)` maximise (cost reported negated). `add_soft` warns `FutureWarning`
  (deprecated); a reified constraint with `m.obj += w * ~r` is the soft form.
- `Model.solve` defaults: `sat_solver_name="g4"`, `maxsat_backend="coretrail"`.
- `cumulative(...)` returns a constraint ("post it with `model &=`"); called on its own line
  it is dropped (all 30 random unit-demand and 30 general instances overlapped); posted with
  `m &=` the scheduling example gives makespan 8 again (1.2.9: 8 without `m &=`).
- Native linear constraints over IntVars: `189b + 180o + 175g == 15750` (each 0..100) solved
  in 0.01 s (1.2.9 never finished building it); the four-fruit system
  `b + o + m + a == 100`, `189b + 225o + 245m + 945a == 31500` minimising `b + a` in 0.57 s;
  four constraints with coefficients 10..400 over six 0..20 IntVars in 2.2 s.
- Objective through an auxiliary `IntVar` (`tot == cost`, `m.obj += tot`) on a random 12x12
  assignment: 0.16 s, against 0.01 s with `m.obj += cost` (1.2.9: did not finish in 300 s on
  4x4).
- `x % 7` (a `ModExpr`) and `m.modulo(x, 7)` work; `abs(expr)` and `IntVar * IntVar` raise
  `TypeError`; `(x != y).iff(r)` works; `m.vector(list_of_intvars).all_different()` works.
- `x.piecewise(base_value=..., steps={t: v})`: the step value holds from `x >= t` on; with the
  objective minimised it picks the cheapest case. `sum_expr` takes a generator.
- `m.table([a, b, c, d], allowed=rows)` over 18 enumerated rows returns one of them.
- `(s1 + 5 <= s2).only_if(o)` with the converse under `~o`: two tasks never overlap, makespan
  is the sum of durations.
- 3-SAT with 400 random variables at 4.26 clauses per variable is `interrupted` after a 20 s
  limit; with 300 variables it is proven `unsat` in 17 s.
- All seven assets give their README's expected output.

Verified on hermax 1.2.9 (inside the image):

- Soft-clause polarity: `m.obj[w] += literal` pays `w` when the literal is false
  (`minimise` example chooses the cheapest assignment; `maximise` reports the forgone weight).
- `solve(time_limit=...)` returns `interrupted` after the limit (2.03 s against a 2.0 s
  limit on pigeonhole 14 into 13) and `r.backend` names `hermax.PortfolioSolver[...]`.
- `r.cost` is `None` when the model has no soft clauses.
- Blocking-clause enumeration: two free Booleans give 4 answers when auxiliary variables are
  blocked too, 2 when only the reported variable is blocked.
- Incremental re-solve after blocking returns the next-best cost; the all-optimal loop
  matched brute force (10 optimal, one solution).
- `m.scale(x, -1)` raises `ValueError`; `x % 3` raises `TypeError`; `r[sum]` raises
  `TypeError: Unsupported decode target`; `(x | y) | False` raises `TypeError`;
  `m &= m.cumulative(...)` raises `TypeError`; `DivExpr != v` is a `PBConstraint` that `|`
  rejects; `m.floor_div(x, k)` returns an `IntVar` usable in `z == 3*q + 1`.
- `result.ok` is `True` for `sat`, `optimum` and `interrupted_sat`
  (`hermax/model/core.py`, `SolveResult.ok`).
- Scheduling example: `cumulative` plus a makespan `IntVar` as `m.obj += makespan` gives the
  brute-force makespan 8.
- Soft-clause encoding of a random 4x4 assignment (costs up to 125) solved in 0.01 s; the
  encoding with `total == sum(c * x)` as objective did not finish within 300 s.
- A lone `m.int("x", 0, 5333333)` with a trivial constraint did not finish within 100 s under
  a 2 GB limit (not reproduced as a memory kill).

- Round 2 probes (inside the image): `r[matrix]` returns a list of row lists of the matrix
  shape; `m &= (a[0] + a[1] == a[2] + 1)` is feasible; three tasks of durations 3, 2, 4 under
  `cumulative(..., [1, 1, 1], 1)` give makespan 9 (no overlap); `q[0] != q[1]` posts a literal
  usable in a block.
- `interrupted_sat` was not triggered in round 2 probes (time limits 1, 2, 3 and 8 s on
  a 300-item knapsack and a random clause-plus-soft model: `interrupted` with no solution,
  or `optimum`). The status stays in the table because `SolveResult.ok` covers it.

Independent toy test (add-solver toy problems, solved by a tester from this skill only,
in the same image): 18/18 passed after one repair round. First run 13/18: all five
failures were knapsack variants with the minimise sign used for a maximisation (the Common
issues sign row was then added). Per-problem results:

| Problem | Result |
|---|---|
| cryptarithm/ab-ab-aaa | PASS (infeasibility reported) |
| cryptarithm/send-more-money | PASS (feasible solution) |
| cryptarithm/two-two-four | PASS (feasible solution) |
| graph-colouring/cycle6 | PASS (optimal, 2) |
| graph-colouring/k4-tail | PASS (optimal, 4) |
| graph-colouring/petersen | PASS (optimal, 3) |
| jobshop/ft06 | PASS (optimal, 55) |
| jobshop/small | PASS (optimal, 11) |
| knapsack/p01 | PASS (optimal, 309) |
| knapsack/small | PASS (optimal, 15) |
| knapsack-all-optimal/fourteen | PASS (all 9 optimal) |
| knapsack-all-optimal/ties | PASS (all 5 optimal) |
| knapsack-all-optimal/unique | PASS (all 1 optimal) |
| n-queens/n3 | PASS (infeasibility reported) |
| n-queens/n4 | PASS (feasible solution) |
| n-queens/n8 | PASS (feasible solution) |
| n-queens-all/n6 | PASS (all 4 solutions) |
| n-queens-all/n8 | PASS (all 92 solutions) |

Tester total: **18/18 passed** (final run, after one repair round).

The README cross-cutting failures ("only instances with name/note keys fail", "exit code with
no useful message") did not occur in the tester's runs; the tester read only the named keys.

Refactored from an earlier integration skill; examples verified inside the same image.
