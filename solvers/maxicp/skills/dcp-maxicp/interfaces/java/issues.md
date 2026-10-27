# MaxiCP in Java: common issues and performance

Part of [the Java interface](README.md); shared concepts in [SKILL.md](../../SKILL.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `firstFailNary(...)` gives one "solution" with variables unfixed | Bug in 0.0.3: it passes no variables to its selector | Use `firstFailBinary`; a branching that returns `EMPTY` early declares a solution |
| `heuristicNary` misses the largest domain value (8-queens: 13 solutions, not 92) | Bug in 0.0.3: its loop runs `v < max` | Use `firstFailBinary` |
| `objective not bound` | The objective is not fixed by the branching array | Add the objective variable to the array passed to `firstFailBinary` |
| Tasks ignored: `noOverlap` does nothing, `makespan` is 0 | `makeIntervalVar(cp, len)` is optional (presence unknown) | `makeIntervalVar(cp, false, len)` for a task that must run |
| `InvalidParameterException: at least one setValue in the domain` | Empty domain, `lo > hi` | Check the bounds |
| `InvalidParameterException ... MIN_VALUE and MAX_VALUE not allowed` | A bound at the int limit | Use tighter bounds from the data |
| `InconsistencyException` from `cp.post` | Refuted at the root, outside the search | Catch it where the post is outside a search; inside a branch the search handles it |
| Values read after `solve` are the root's | State is restored on return | Read values in `onSolution` |
| Solutions repeat with different auxiliaries | Auxiliaries are branched on | Fix them, or use the no-good loop |
| `solve` returns 0 solutions and `completed` is false | The predicate stopped the search (often a time limit) | Raise the limit; a non-completed search proves nothing |
| `no suitable method found for eq(CPConstraint,int)` | `sum(xs, k)` is a constraint, not a view | `cp.post(sum(xs, k))` |
| `CPConstraint cannot be converted to CPBoolVar` | `or`, `implies` are constraints | Post them; use `isOr` for a Boolean |
| `no suitable method found for minus(CPIntVar,CPIntVar)` | No variable-minus-variable | `sum(a, minus(b))` |
| `OutOfMemoryError: Java heap space` at `Equal.post` | Domains are allocated in full: 300 variables on `0..1000000000` linked by `eq` exhausted the heap (2 did not) | Use bounds from the data; keep domains small |
| `InvalidParameterException: consider reducing the domains` | A `mul` bound product does not fit in `int` | Smaller domains |

## Performance

Plain DFS has no learning and no restarts, so the encoding decides whether a search finishes. Patterns that
worked in practice:

- One-hot Booleans with an exactly-one sum per item (`cp.post(sum(bs, 1))`) instead of channelling with reified `isEq`.
- A position variable per item with `allDifferent`, and a binary `table` over consecutive positions, for paths
  and tours (knight's tour, Hidato-like puzzles).
- `table` for small arithmetic relations such as `|x - y|`, instead of `max` views.
- Implied constraints taken from the problem statement, such as lower bounds on sums, to speed up optimality proofs.

