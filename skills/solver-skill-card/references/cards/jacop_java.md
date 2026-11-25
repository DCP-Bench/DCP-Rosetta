# JaCoP (Java) — Java, finite-domain constraint propagation with depth-first search

## Minimal working example (knapsack)
```java
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.*;
import java.util.Arrays;
public class Knapsack {
  public static void main(String[] args) {
    Store store = new Store();
    int[] values = {6, 10, 12}, weights = {1, 2, 3}; int capacity = 5;
    IntVar[] x = new IntVar[3];
    for (int i = 0; i < 3; i++) x[i] = new IntVar(store, "x" + i, 0, 1);
    IntVar total = new IntVar(store, "total", 0, 28), cost = new IntVar(store, "cost", -28, 0);
    store.impose(new LinearInt(x, weights, "<=", capacity));
    store.impose(new LinearInt(x, values, "==", total));
    store.impose(new LinearInt(new IntVar[]{total, cost}, new int[]{1, 1}, "==", 0));
    DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
    search.setPrintInfo(false);
    SimpleSelect<IntVar> select = new SimpleSelect<>(x, new SmallestDomain<>(), new IndomainMax<>());
    search.labeling(store, select, cost);
    System.out.println(total.value() + " " + Arrays.stream(x).map(IntVar::value).toList());
  }
}
```

## API
- **Decision variables:** `new IntVar(store, "name", lb, ub)`; `new BooleanVar(store, "name")` (is an `IntVar`, 0/1); set of values: `v = new IntVar(store, "v", 1, 1); v.addDom(4, 4)`; read `v.value()` after a solution; `store.impose(c)` posts a constraint
- **Logic constraints:** `Reified(c, b)` (b ⇔ c); `Implies(b, c)` (b ⇒ c, b a 0/1 var); `Or(c1, c2)`, `And(c1, c2)`, `Not(c)`, `IfThen(c, t)`, `IfThenElse(c, t, e)` over primitive constraints such as `XeqC(x, 1)`, `XneqC`, `XgteqC`, `XlteqC`, `XeqY`, `XneqY`, `XltY`, `XlteqY`, `XgteqY`
- **Arithmetic constraints:** `XplusYeqZ(x, y, z)`, `XplusCeqZ(x, c, z)`, `XplusYeqC(x, y, c)`, `XmulYeqZ(x, y, z)`, `XmulCeqZ(x, c, z)`, `AbsXeqY(x, y)`, `Max(vars, m)`, `Min(vars, m)`; `LinearInt(vars, int[] coeffs, "==", rhs)` (`"<="`, `">="`, `"<"`, `">"`, `"!="`; rhs an int or an `IntVar`); `SumInt(vars, "==", total)`
- **Other constraints:**
  - counting: `Alldifferent(vars)`; `Alldistinct(vars)` (stronger propagation); `Count(vars, cnt, value)` (cnt = #vars equal to value); `GCC(vars, occ)` (`occ[i]` counts value `lb+i`)
  - indexing/extensional: `Element(idx, int[] arr, res)` (res = arr[idx], idx is 1-based; also `IntVar[]` arrays; `Element(idx, arr, res, 0)` makes idx 0-based); `Table(vars, int[][] tuples)`; `Regular(fsm, vars)` with `FSM`, `FSMState`, `FSMTransition(new IntervalDomain(lo, hi), nextState)` (`f.allStates`, `f.initState`, `f.finalStates`)
  - graph: `Circuit(succ)` (successors 1-based); `Subcircuit(succ)`
  - scheduling: `Cumulative(starts, durations, usages, limit)` (all `IntVar[]`, `limit` an `IntVar`); `Diff2(new IntVar[][]{{x, y, dx, dy}, ...})` (non-overlapping rectangles)
- **Objectives and solving:** `DepthFirstSearch<IntVar> search`; `search.labeling(store, new SimpleSelect<>(vars, varOrder, valOrder))` for satisfaction, `search.labeling(store, select, cost)` minimises the `IntVar cost` (maximise by minimising its negation); returns whether a solution was found, values are then readable; `search.setPrintInfo(false)`, `search.setTimeOut(seconds)`; var orders `SmallestDomain<>()`, `MostConstrainedStatic<>()`, `LargestDomain<>()`, `SmallestMin<>()`; value orders `IndomainMin<>()`, `IndomainMax<>()`, `IndomainMiddle<>()`, `IndomainRandom<>()`; `new InputOrderSelect<>(store, vars, new IndomainMin<>())` (input order)

## Modelling
- **Domains:** the tightest `lb`/`ub` the data allows; give the objective variable its true range
- **Structure:** a tour is successor variables with `Circuit(succ)` (1-based; a path adds a dummy node); patterns and transitions: `Table(vars, tuples)` or `Regular`; resources: `Cumulative`; packing: `Diff2`; exactly-one or at-most-one over 0/1 variables: `LinearInt(bs, ones, "==", 1)`, not pairwise `Or`s
- **Lookups:** `store.impose(new Element(succ[i], row_i, leg[i]))` per row (row_i an `int[]`, index 1-based), not a computed flat index; a product with a small-domain factor: `Reified(new XeqC(l, k), b)` per value, or `Element` over the constants
- **Symmetry:** order interchangeable variables with `XltY(a[i], a[i + 1])` (`XlteqY` if ties are allowed) and fix the first
- **Implied constraints:** redundant totals such as `SumInt(parts, "==", total)` alongside the individual sums; `Alldistinct` instead of `Alldifferent` when pruning matters
- **Search:** put the deciding variables first (build `SimpleSelect` over only those, the rest follow by propagation) with `SmallestDomain<>()` and `IndomainMin<>()`; for optimisation `IndomainMax<>()` on 0/1 choice variables often finds good solutions early

Docs: https://github.com/radsz/jacop
