# MaxiCP in Java (org.maxicp:maxicp 0.0.3)

The raw Java API of MaxiCP: `org.maxicp.cp.CPFactory`, `CPSolver`, `DFSearch`. What holds in every
interface (concepts, outcomes, enumeration strategy) is in [SKILL.md](../../SKILL.md).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](modelling.md): the API table and what each call needs
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Optimisation](#optimisation)
- [Common issues](issues.md) and [Performance](issues.md#performance)
- [Runnable examples](#runnable-examples)
- [Further reading](#further-reading)

## Install

```bash
mkdir -p lib
curl -fsSLo lib/maxicp-0.0.3.jar https://repo1.maven.org/maven2/org/maxicp/maxicp/0.0.3/maxicp-0.0.3.jar
curl -fsSLo lib/gson-2.11.0.jar https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar
export CLASSPATH="$PWD/lib/maxicp-0.0.3.jar:$PWD/lib/gson-2.11.0.jar"
java -version
```

The examples run as single files with `java File.java`, which reads `CLASSPATH`. Only the JSON example
needs Gson. The raw API needs nothing else. Name the file after its public class, so a problem named
`n-queens` goes in `NQueens.java` (the source launcher accepts a mismatch, javac does not). Details: [MaxiCP repository](https://github.com/aia-uclouvain/maxicp/tree/v0.0.3)
(tag `v0.0.3`), [Maven artifact](https://repo1.maven.org/maven2/org/maxicp/maxicp/0.0.3/).

## Quick start

```java
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

public class QuickStart {
    public static void main(String[] args) {
        CPSolver cp = makeSolver();
        CPIntVar x = makeIntVar(cp, 0, 2);
        CPIntVar y = makeIntVar(cp, 0, 2);
        // x and y add up to 2
        cp.post(eq(sum(x, y), 2));
        DFSearch search = makeDfs(cp, firstFailBinary(x, y));
        search.onSolution(() -> System.out.println("x=" + x.min() + " y=" + y.min()));
        SearchStatistics stats = search.solve();
        System.out.println("solutions: " + stats.numberOfSolutions() + ", completed: " + stats.isCompleted());
    }
}
```

Output: three lines `x=... y=...`, then `solutions: 3, completed: true`.

## Solving

- A search is `DFSearch search = makeDfs(cp, branching)`. `branching` is a `Supplier<Runnable[]>` that
  returns `EMPTY` when it has nothing to branch on (a solution), or `branch(left, right)` otherwise.
- Use `firstFailBinary(vars...)`: it picks the unfixed variable with the smallest domain, posts `x = min`
  on the left and `x != min` on the right. This is the default heuristic in this skill. Equal domain sizes
  go to the variable that comes first in the arguments (creation order does not matter), so pass the main
  decisions first.
- `search.solve()` explores the whole tree. `search.solve(stats -> ...)` stops when the predicate is true.
- `SearchStatistics`: `numberOfSolutions()`, `numberOfFailures()`, `numberOfNodes()`, `timeInMillis()`,
  `isCompleted()`. `isCompleted()` is true only when the tree was exhausted; a stopped search is not completed.

| Result | Meaning |
|---|---|
| solutions > 0, completed | every solution was enumerated |
| solutions = 0, completed | no solution (infeasible) |
| completed = false | the predicate stopped the search; nothing is known about the rest |

- **Time limit:** none is built in. Pass a predicate: `search.solve(s -> s.timeInMillis() > 10_000)`. It is
  checked when the search picks its next alternative, so one long propagation is not interrupted.
- **Read values inside `onSolution`.** `solve` returns with the state restored to the root, and every
  variable is unfixed again. `search.onSolution(() -> value = x.min())` is correct; reading `x` after
  `solve` is not.

## All solutions

`onSolution` runs once per solution. Auxiliary variables (any variable not part of the reported solution)
multiply the solutions: a free `spare` in 0..5 makes each `(x, y)` appear six times. Either fix every
auxiliary through a constraint, or forbid each assignment of the reported variables with a no-good:

```java
import org.maxicp.util.exception.InconsistencyException;

int[] values = new int[n];                                  // inside the loop, values of the variables the loop records
DFSearch search = makeDfs(cp, firstFailBinary(xs));
search.onSolution(() -> { for (int i = 0; i < n; i++) values[i] = xs[i].min(); });
SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1);
if (stats.numberOfSolutions() == 0) break;                  // no solution left
CPBoolVar[] differ = new CPBoolVar[n];
for (int i = 0; i < n; i++) differ[i] = not(isEq(xs[i], values[i]));
try { cp.post(or(differ)); } catch (InconsistencyException last) { break; }   // nothing left to forbid
```

Posting at the root, after `solve` returns, persists; posting inside a branch is undone on backtrack.
Each pass builds a new `makeDfs`. [Min-makespan](../../assets/java/min-makespan/README.md) shows the full loop.

## Optimisation

- `IntObjective o = cp.minimize(x)` or `cp.maximize(x)`, with `x` a `CPIntVar` (a view such as `sum(...)`
  or `max(...)` is fine).
- `SearchStatistics stats = search.optimize(o)` (or `optimize(o, limit)`). Each improving solution
  tightens the bound. The last value recorded in `onSolution` is optimal **only if `stats.isCompleted()`**;
  otherwise report "not proven". No solution and `isCompleted()` means infeasible.
- The objective must be fixed at every solution. If it is not, MaxiCP throws `objective not bound`: add the
  objective to the branching array.
- To enumerate every optimum: post `eq(x, optimum)` at the root after `optimize`, then run the no-good loop
  above over the variables the loop reports.
- Do not bound the objective with a value the model does not imply.
- Examples: [project-selection](../../assets/java/project-selection/README.md) (maximise),
  [min-makespan](../../assets/java/min-makespan/README.md) (minimise, all optimal),
  [single-machine](../../assets/java/single-machine/README.md) (makespan over intervals).

## Runnable examples

| Example | Shows |
|---|---|
| [magic-square](../../assets/java/magic-square/README.md) | `allDifferent`, sums over rows, columns and diagonals, counting every solution, an infeasible order |
| [project-selection](../../assets/java/project-selection/README.md) | maximise, JSON data with ragged groups and unused keys |
| [min-makespan](../../assets/java/min-makespan/README.md) | minimise a `max` of loads, proof check, every optimal assignment with no-goods |
| [single-machine](../../assets/java/single-machine/README.md) | interval variables, `noOverlap`, precedences, release times, makespan |

## Further reading

- Source and examples at tag `v0.0.3`: [repository](https://github.com/aia-uclouvain/maxicp/tree/v0.0.3); raw
  examples in `src/main/java/org/maxicp/cp/examples/raw/` (`nqueens`, `JobShop.java`).
- User guide, search strategies and scheduling chapters: [maxicp.org](http://www.maxicp.org).
- API Javadoc: [javadoc.io](https://javadoc.io/doc/org.maxicp/maxicp/latest/org.maxicp/module-summary.html).
