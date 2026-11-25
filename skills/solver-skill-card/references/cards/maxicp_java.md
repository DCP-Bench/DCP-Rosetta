# MaxiCP (Java) — Java, constraint programming with propagation and depth-first search

## Minimal working example (knapsack)
```java
import org.maxicp.cp.engine.core.*;
import org.maxicp.search.*;
import static org.maxicp.cp.CPFactory.*;
public class Knapsack {
    public static void main(String[] args) {
        int[] values = {6, 10, 12}, weights = {1, 2, 3}; int capacity = 5, n = values.length;
        CPSolver cp = makeSolver();
        CPBoolVar[] x = makeBoolVarArray(cp, n);
        CPIntVar[] w = new CPIntVar[n], v = new CPIntVar[n];
        for (int i = 0; i < n; i++) { w[i] = mul(x[i], weights[i]); v[i] = mul(x[i], values[i]); }
        cp.post(le(sum(w), capacity));
        CPIntVar total = sum(v);
        DFSearch search = makeDfs(cp, Searches.firstFailBinary(x));
        search.onSolution(() -> System.out.println(total.min() + " " + java.util.Arrays.toString(x)));
        search.optimize(cp.maximize(total));
    }
}
```

## API
- **Decision variables:** `makeIntVar(cp, lb, ub)`; `makeBoolVar(cp)`; `makeIntVarArray(cp, n, lb, ub)`; `makeBoolVarArray(cp, n)` (`CPBoolVar` is a `CPIntVar`)
- **Logic constraints:** `cp.post(or(bs))`; `not(b)`; `cp.post(implies(a, b))`; `isEq(x, v)`, `isLe(x, y)`, `isLt(x, c)`, `isOr(bs)` → `CPBoolVar` (reification)
- **Arithmetic constraints:** `cp.post(eq(x, y))` (also `neq`, `le`, `lt`, `ge`, `gt`; `y` a variable or `int`); `sum(xs)`; `mul(x, c)`; `mul(x, y)`; `plus(x, c)`, `minus(x, c)` (`int c` only; x + y: `sum(x, y)`); `minus(x)`; `max(xs)`; `minimum(xs)`
- **Other constraints:**
  - counting: `cp.post(allDifferent(xs))`
  - indexing/extensional: `element(arr, idx)` → `CPIntVar` (0-based; `arr` is `int[]` or `CPIntVar[]`); `cp.post(table(xs, rows))`
  - graph: `cp.post(circuit(succ))`
  - scheduling: `makeIntervalVar(cp, false, d)`; `start(iv)`; `end(iv)`; `cp.post(endBeforeStart(a, b))`; `cp.post(noOverlap(ivs))`; `makespan(ivs)`; `cp.post(le(sum(pulse(iv, h), ...), cap))` (cumulative)
- **Objectives and solving:** `DFSearch s = makeDfs(cp, Searches.firstFailBinary(xs))`; `s.onSolution(() -> ...)` (read `x.min()` there; the last call is the optimum); `s.optimize(cp.minimize(obj))` or `cp.maximize(obj)`; satisfaction: `s.solve(st -> st.numberOfSolutions() >= 1)`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `makeIntVar(cp, Set.of(1, 4, 7))`
- **Structure:** tour or path: `circuit(succ)` with each successor restricted to its allowed neighbours (a path adds a dummy node that closes the cycle), not a position sequence with move tests; resources: `noOverlap` / `pulse` sums
- **Lookups:** `element(row_i, succ[i])` per row, not a computed flat index; a product of two variables where one has a small domain: split on its values `cp.post(implies(isEq(l, k), isEq(c, mul(p, k))))`
- **Symmetry:** order interchangeable objects, `cp.post(lt(x[i], x[i + 1]))`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence); a redundant `allDifferent` helps

Docs: http://www.maxicp.org
