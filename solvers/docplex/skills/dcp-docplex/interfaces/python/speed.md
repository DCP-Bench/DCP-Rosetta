# Speed and helper cost (DOcplex in Python)

Back to [README](README.md) · [SKILL.md](../../SKILL.md)

**Helper cost.** Each helper adds variables and constraints of its own, which count against
the Community Edition limit. Measured on integer variables in 0..9, counting the result
variable or indicator binary that the helper is posted with:

| Posting | Adds variables | Adds constraints |
|---|---|---|
| `m.add_constraint(a != b)` | 1 | 2 |
| `m.add(d == m.abs(a - b))` | 5 | 4 |
| `m.add(y == m.max(a, b))` | 4 | 6 |
| `m.add_equivalence(c, a == b)` | 1 | 1 |
| `m.add_indicator(c, a <= b)` | 1 | 1 |
| `m.add_if_then(a >= 3, b == 0)` | 1 | 2 |


## Speed

Measured on one CPU, wall time of the whole script (Python start-up, model build, all solves),
on small textbook instances:

| Model | Size | Time |
|---|---|---|
| cryptarithm | SEND+MORE=MONEY, TWO+TWO=FOUR, an infeasible AB+AB=AAA | 0.1 to 0.6 s each |
| minimum graph colouring | a 6-cycle, a 4-clique with a pendant vertex, the Petersen graph | 0.1 to 0.5 s each |
| 0/1 knapsack | 5 and 10 items | 0.1 s each |
| job shop, indicator encoding | 3 jobs; Fisher-Thompson ft06 (6 jobs by 6 machines) | 1.0 s, 0.5 s |
| n-queens, one solution | n = 3, 4, 8 | 0.1 s each |
| n-queens, all solutions, no-good loop | n = 8, 92 solutions | 21 s |
| n-queens, all solutions, `populate()` alone | n = 8, 92 solutions | 0.7 s |

The job shop timings are for those two instances only. The skill makes no claim about larger job
shops: time one on your data before relying on this encoding. When a time limit is set, a run that
hits it may return a solution that is not proven optimal, so check the status (see [Solving](README.md#solving)).

