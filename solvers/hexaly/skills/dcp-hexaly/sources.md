# Sources for `hexaly`

Existing skills: none found. GitHub code search for `SKILL.md` files naming Hexaly returned
only passing mentions in skills about other topics (robust modelling, reporting
experiments); `hexaly.com` publishes no `llms.txt`. The skills.sh registry was not searched.

## Shared (SKILL.md)

Checked in Python, the only interface.

- https://www.hexaly.com/docs/last/pythonapi/optimizer/hxsolutionstatus.html: the four statuses and their definitions.
- https://www.hexaly.com/docs/last/pythonapi/optimizer/hxparam.html: `nb_threads` (0 = automatic, at least 4 threads), `gap_limit`, `time_limit`, `verbosity`, `log_writer`.
- https://www.hexaly.com/docs/last/mathematicaloperators/collectionvariables.html: list and set semantics, permutation as a full list, `distinct`, `partition`, `disjoint`.
- https://www.hexaly.com/docs/last/mathematicaloperators/intervalvariables.html: interval semantics, `a < b` as `end(a) <= start(b)`.
- https://www.hexaly.com/docs/last/modelingprinciples/modelingprinciples.html: turning constraints into objectives (`max(0, a - b)`), lexicographic objectives.
- https://www.hexaly.com/docs/last/modelingprinciples/inconsistency.html: INFEASIBLE versus INCONSISTENT, `compute_inconsistency`.
- https://www.hexaly.com/docs/last/exampletour/jobshop.html: the job shop model (intervals, one list per machine, lambda), shortened in `assets/python/scheduling`.

Verified by running (hexaly 15.0.20261026, Python 3.12, Linux container without network):

- An objective is required: `close()` without one raises `At least one objective is required in the model`; `minimize(0)` solves a feasibility model and reports `OPTIMAL` once a solution is found.
- Default gap limit 1e-4 (`get_gap_limit()`); on a 40-item strongly correlated knapsack the default reports `OPTIMAL` with value 12168772 and bound 12169975, gap limit 0 closes the bound at 12168772.
- Threads: ft06 (Fisher and Thompson 6x6, optimum 55) as intervals and lists, one CPU, 30 s: 1 and 2 threads stop `FEASIBLE` with bound 54; 4 threads prove 55 in 0.4 s; the default in 1.8 s. As integers with pairwise disjunctions, 1 thread proves it in 0.1 s.
- Proofs by formulation, 4x4 assignment, 4 threads, 10 s: Boolean matrix and pairwise `!=` prove 13 in 0.01 to 0.02 s; `count(distinct(...)) == n` and a list decision end `FEASIBLE` 13 with bounds 10 and 4.
- Infeasibility: 3-queens, 6 pigeons in 5 holes (integers or Booleans) stay `INFEASIBLE` for 10 s with 1 or 4 threads; AB + AB = AAA is `INCONSISTENT` at once; 3-queens with the attacks minimised is `OPTIMAL` 1 in 0.01 s.
- Enumeration: hard no-goods (`or` of `!=`) on 5 Booleans with 2 true find 10 solutions and the 11th solve ends `INFEASIBLE` at its 5 s limit (1 and 4 threads). Soft no-goods prove exhaustion: x + y = 2 (3 solutions), 5 Booleans (10, 0.15 s), permutations of 3 (6), 6-queens (4, 1.2 s), 8-queens with integer columns (92; 89 s with 1 thread, 103 s with 4 threads on one CPU).
- 8-queens on a Boolean board (linear row, column and diagonal sums, soft no-goods, 4 threads, one CPU), all rows posted before the columns: no-goods over the 8 queen squares took 4.4 to 7.8 s over five runs, no-goods over all 64 squares 31 s over two runs; each solve that found a solution took at most 0.09 s (8 squares) or 1.1 s (64 squares), the final proof 5.2 to 6.6 s and 28 to 29 s. With each row's and column's constraints posted together and 8-square no-goods: 33 to 48 s over ten runs. Parameters were reset between solves (`time_limit` 30 and 31 alternately) without effect on the result.
- Violation forms: AB + AB = AAA minimising `abs(2 * AB - AAA)` is `OPTIMAL` 73 in 0.01 s; 3-queens with diagonals as `max(0, sum - 1)` is `OPTIMAL` 1 in 0.02 s; SEND + MORE = MONEY minimising the absolute difference is `OPTIMAL` 0 in 0.01 s; CCEE + GGCB = DHACI is `INFEASIBLE` after 10 s as hard constraints and `OPTIMAL` 1 in 0.4 s as an absolute difference.
- `model.partition(a, b, c)`, `model.disjoint(a, b)` and `model.cover(a, b, c)` on three `set(4)` decisions solve to a partition of 0..3; `model.sum` over an empty generator is 0.
- `model.constraint(0 <= r < b)` raises the `Cannot transform an HxExpression to a Python boolean` `TypeError`; `model.distinct` on a Python list raises `TypeError`; `model.sum([])` is 0; `model.and_` over `model.range(0, 0)` is 1.
- Several optimizers created one after another in one process (`assets/python/infeasible`).
- Arithmetic: -7 / 2 = -3.5, -7 // 2 = -4, -7 % 2 = -1, (-7) ** 2 = 49.0 (a float).
- Licence lookup: `HX_LICENSE_PATH` set to the file works, set to its folder raises `Property 'LICENSE_KEY' is missing`; the working directory works; `HxVersion.set_license_path` works; without a licence the first optimizer raises `Cannot open file [/opt/hexaly_15_0/license.dat]`.
- Values: Boolean and integer `.value` is an `int` (64-bit: 5000000000 read back), a list gives `HxCollection`, an array `HxArray`, both iterable.
- The log writer is the `sys.stdout` of the moment the optimizer is created; replacing `sys.stdout` later does not capture the log.
- One-hot, tour and candidate lists (`assets/python/one-hot`, `tsp`, `candidates`): SEND + MORE = MONEY with a Boolean per (letter, digit) and column carries is `OPTIMAL` in 1.2 s with the solution S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2; the 6-place tour with Boolean arcs and order variables is `OPTIMAL` 22 in 1.3 s, and a brute force over the 120 tours on the host also gives 22; two prices adding to 120 and multiplying to 3200 chosen from the divisors is `OPTIMAL` [40, 80] in 1.2 s (all with the image's `docker run`, 4 threads).
- `references/formulations.md`: times are the wall-clock seconds of the model on each instance as an evaluator measured them (one CPU, 4 threads, 180 s limit), and every "timed out" or "solved N of M" is the evaluator's record of the first formulation of that problem: magic hexagon (list, 180 s; one-hot, 66 s), crypta (list with carries, 180 s; one-hot, 1.2 s), water jug (integer amounts, 180 s; state Booleans, 2.4 s), n fractions (free integers, 180 s; digit triples, 20 s), age changing (integers and an order list, 180 s; a table of orders, 4.6 s), contracting costs (six free integers, 180 s; a chain, 1.0 s), initials queue (list with `at`, 179 s; one-hot, 1.2 s), social golfers (integer labels, 6 of 8; sets, 8 of 8), hidato (list: a path on 3 of 5, none on the 12 x 12, no proof of a single solution; one-hot: 5 of 5, at most 2.5 s each), frog circle (list: 1 of 5; one-hot: 4 of 5), handshaking (edge Booleans: 2 of 5; one-hot counts: 4 of 5) and divisible by 1 to 9 (list with `%`: found, no proof in 180 s; quotients: proof in 8.2 s). The sixteen-word sum was checked by a numpy brute force over the 10! digit assignments of the ten letters: the sum holds for one assignment, which has a zero in a leading place.
- Every error message quoted in `interfaces/python.md` was produced by the code beside it.

## Python (interfaces/python.md)

Tested with hexaly 15.0.20261026 (pip wheel), Python 3.12.11, Debian 12 (Linux x86-64), an
academic licence.

- https://pypi.org/project/hexaly/: install command, licence requirement and file locations.
- https://www.hexaly.com/docs/last/pythonapi/index.html: `HexalyOptimizer`, `HxModel`, `HxExpression`, `HxSolution`, `HxParam`, `HxCollection`, `HxArray`, `HxInterval`, `HxVersion`.
- https://www.hexaly.com/registration: free trial and academic licences.
