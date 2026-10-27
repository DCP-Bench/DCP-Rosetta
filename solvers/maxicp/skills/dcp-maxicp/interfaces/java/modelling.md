# MaxiCP in Java: modelling

Part of [the Java interface](README.md); shared concepts in [SKILL.md](../../SKILL.md).


**Readable models.** Open the program with a `//` comment stating the problem, and start each constraint
block with a `//` comment in the problem statement's words, not the MaxiCP call, for example
`// every row holds different values`. The examples below follow this.

Full list: [CPFactory](https://github.com/aia-uclouvain/maxicp/blob/v0.0.3/src/main/java/org/maxicp/cp/CPFactory.java)
(static factories and constraints; `import static org.maxicp.cp.CPFactory.*`).

| Need | API |
|---|---|
| integer variable in lo..hi | `makeIntVar(cp, lo, hi)`, `makeIntVarArray(cp, n, lo, hi)` |
| integer variables in 0..sz-1 | `makeIntVarArray(cp, n, sz)` (the two-value form is the domain size, not the upper bound) |
| Boolean variable | `makeBoolVar(cp)`, `makeBoolVarArray(cp, n)` (a `CPBoolVar` is a `CPIntVar` of 0..1) |
| all different | `allDifferent(xs)` |
| disequality | `neq(x, y)`, `neq(x, k)` |
| linear equality or bound | `eq(x, k)`, `eq(x, y)`, `le(x, k)`, `le(x, y)`, `ge(x, k)`, `ge(x, y)` |
| sum as a constraint | `sum(xs, k)`, `sum(xs, y)`: post with `cp.post(...)`, see below |
| views (no new constraint) | `sum(xs)`, `mul(x, k)`, `mul(x, y)`, `plus(x, k)`, `minus(x)` (-x), `minus(x, k)` (x - k), `max(xs)`, `minimum(xs)` |
| element and table | `element(int[], idx)`, `element(CPIntVar[], idx)`, `element(int[][], r, c)`, `table(xs, rows)`, `circuit(xs)` |
| reification and logic | `isEq(x, k)`, `isEq(x, y)`, `isLe(x, y)`, `not(b)`, `isOr(bs...)` (a `CPBoolVar`); constraints `or(bs)`, `implies(b1, b2)` |
| interval (task) | `makeIntervalVar(cp, false, len)`, `start(t)`, `end(t)`, `startAfter(t, r)`, `endBeforeStart(a, b)` |
| no overlap and makespan | `noOverlap(ts)`, `makespan(ts)` |

- `cp.post(c)` posts a constraint and propagates. If it is refuted there and then, it throws
  `InconsistencyException` (`org.maxicp.util.exception`). A refusal at a root-level post, before any search,
  means the problem is unsatisfiable: catch it and report that, with no solution. Inside a branch the search
  handles it. See [Common issues](issues.md).
- A variable is fixed by the search only if the branching array covers it. Pass every variable a solution
  must fix to `firstFailBinary`.
- A view (`sum`, `mul`, `max`, `element`, ...) follows the variables it is built from. It is fixed when they are.
- Bounds may not be `Integer.MIN_VALUE` or `Integer.MAX_VALUE`. For a number that does not fit an int, use
  digits or a smaller scale.
- `sum(xs, k)` and `sum(xs, y)` are constraints: the sum of `xs` equals `k`, or equals the variable `y`. Post
  them with `cp.post(...)`. They cannot be an argument of `eq`, `le` or `ge` (`eq(sum(xs, 2), 1)` does not
  compile). Use the view `sum(xs)` there.
- Booleans in a sum: a `CPBoolVar[]` is accepted where a `CPIntVar[]` is expected, so `cp.post(sum(bs, k))`
  counts the `true` values. `sum(bs)` is the count as a view.
- No `minus(CPIntVar, CPIntVar)`. Write `a - b` as `sum(a, minus(b))`. `minus(b, k)` is `b - k`.
- `mul(x, y)` computes its bounds in `int`. The largest product of bounds must stay below 2^31: `0..40000` times `0..40000` is fine;
  `0..50000` times `0..50000` throws `InvalidParameterException: consider reducing the domains, Integer.MIN _VALUE
  and Integer.MAX_VALUE not allowed`.
- `or(bs)` and `implies(b1, b2)` are constraints: post them, do not assign them to a `CPBoolVar` (`CPBoolVar r
  = implies(...)` does not compile). A Boolean equal to a clause is `isOr(...)`, which nests:
  `r = isOr(not(isEq(x, 1)), isEq(y, 2))`, and `eq(r, 0)` forces `x = 1` and `y != 2`.
- "`b` implies at least one of `bs`" is `cp.post(ge(sum(bs), b))`.
- `table(xs, rows)`: `rows` is `int[][]`, one tuple per row, e.g. `new int[][]{{0, 1}, {1, 2}, {2, 0}}`.
- `circuit(succ)`: `succ[i]` in `0..n-1` is the successor of node `i`, and the variables form one cycle through
  all nodes. Self-loops are excluded (4 nodes: 6 circuits; 5 nodes: 24).
- `element(CPIntVar[] xs, idx)` is a view equal to `xs[idx]`. A 2-D lookup with variable indices flattens the
  grid: `element(flat, sum(mul(r, m), c))` for an `m`-column grid.
- Cumulative resource (raw API): `CPIntervalVar t = makeIntervalVar(cp, false, len)`, then
  `CPCumulFunction f = sum(pulse(t1, h1), pulse(t2, h2), ...)` and `cp.post(le(f, cap))`. The total height of
  the active tasks is at most `cap` at every time point. Bound a start with `cp.post(le(start(t), H))`. Import
  `org.maxicp.cp.engine.constraints.scheduling.CPCumulFunction`.

