# Choco (Java) — Java, constraint propagation with branching search

## Minimal working example (knapsack)
```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solution;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import java.util.Arrays;
public class Knapsack {
  public static void main(String[] args) {
    int[] values = {6, 10, 12}, weights = {1, 2, 3};
    int capacity = 5;
    Model model = new Model("knapsack");
    BoolVar[] x = model.boolVarArray("x", 3);
    IntVar total = model.intVar("total", 0, 28);
    model.scalar(x, weights, "<=", capacity).post();
    model.scalar(x, values, "=", total).post();
    Solution best = model.getSolver().findOptimalSolution(total, Model.MAXIMIZE);
    System.out.println(best.getIntVal(total) + " " + Arrays.toString(Arrays.stream(x).mapToInt(best::getIntVal).toArray()));
  }
}
```

## API
- **Decision variables:** `model.intVar("x", lb, ub)`; `model.intVar("y", new int[]{1, 4, 7})` (set of values); `model.intVar(c)` (constant); `model.boolVar("b")`; `model.intVarArray("xs", n, lb, ub)`; `model.boolVarArray("bs", n)`; `model.intVarMatrix("m", r, c, lb, ub)`; `model.boolVarMatrix("bm", r, c)`; `BoolVar` is an `IntVar` (0/1)
- **Logic constraints:** every constraint must end with `.post()`; `c.reify()` returns a `BoolVar` equivalent to `c`; `c.reifyWith(b)` (`b` ⇔ `c`); `model.ifThen(b, c)` / `model.ifThen(c1, c2)` (⇒); `model.ifThenElse(b, c1, c2)`; `model.or(c1, c2)`, `model.and(c1, c2)`, `model.not(c)`; `model.reifyXeqY(x, y, b)`; `model.addClauses(posBools, negBools)` (one clause)
- **Arithmetic constraints:** `model.arithm(x, "<=", y)` (also `"="`, `"!="`, `"<"`, `">"`, `">="`; `y` may be an `int`); `model.arithm(x, "+", y, "=", z)` (also `"-"`; `z` may be an `int`); `model.sum(xs, "<=", k)` (`k` int or `IntVar`; also `BoolVar[]`); `model.scalar(xs, coeffs, "=", total)` (`int[]` coefficients); `model.times(x, y, z)`; `model.absolute(y, x)` (y = |x|); `model.max(m, xs)`, `model.min(m, xs)`; `model.member(x, new int[]{..})`; expressions: `x.add(y).mul(2).le(z).post()` (`add sub mul div mod abs`; `eq ne lt le gt ge`)
- **Other constraints:**
  - counting: `model.allDifferent(xs)`; `model.allDifferent(xs, "AC")`; `model.count(v, xs, n)` (`v` int or `IntVar`); `model.globalCardinality(xs, values, occurrences, closed)`; `model.nValues(xs, n)`
  - indexing/extensional: `model.element(res, int[] row, idx, 0)` (res = row[idx - offset]; also `IntVar[]`); `Tuples t = new Tuples(true); t.add(1, 2); model.table(new IntVar[]{x, y}, t)` (`true` = allowed, `false` = forbidden); `model.regular(xs, new FiniteAutomaton("(0|1)*2"))` (symbols are digits 0-9)
  - ordering: `model.increasing(xs, 0)` (non-strict, distance 0); `model.lexLessEq(xs, ys)`; `model.inverseChanneling(xs, ys, 0, 0)` (index offsets)
  - graph: `model.circuit(succ)` (0-based); `model.subCircuit(succ, 0, size)`
  - scheduling: `model.cumulative(starts, int[] durations, int[] heights, int capacity)`; `model.diffN(xs, ys, widths, heights, true)`; `model.binPacking(binOf, int[] sizes, loads, 0)`
- **Objectives and solving:** `Solution s = model.getSolver().findOptimalSolution(obj, Model.MAXIMIZE)` (or `Model.MINIMIZE`; `null` if infeasible); satisfaction: `Solution s = model.getSolver().findSolution()`; `s.getIntVal(v)`; `model.getSolver().solve()` then `v.getValue()`; `model.getSolver().limitTime("10s")`

## Modelling
- **Domains:** the tightest bounds the data allows; a set of allowed values: `model.intVar("x", new int[]{1, 4, 7})`
- **Structure:** a tour is successor variables `succ[i]` restricted to allowed neighbours with `model.circuit(succ)` (a path adds a dummy node), not position sequences with move tests; sequence patterns: `model.regular(...)` or `model.table(...)`; resources: `model.cumulative(...)`; packing: `model.binPacking(...)`; rectangles: `model.diffN(...)`
- **Lookups:** index a constant row directly, `model.element(leg[i], row_i, succ[i], 0)`, not a computed flat index; weight 0/1 choices straight in `model.scalar(bools, coeffs, "<=", cap)`; a product with a small-domain factor: `model.ifThen(model.arithm(l, "=", k), model.arithm(c, "=", k * p))` per value `k`
- **Symmetry:** order interchangeable objects, `model.increasing(xs, 1)` (strict), and `model.lexLessEq(row_i, row_j)` between interchangeable rows
- **Implied constraints:** add totals the solver cannot infer, e.g. `model.sum(xs, "=", total)` with bounds on `total`, or a redundant `model.cumulative` per axis
- **Search:** `model.getSolver().setSearch(Search.inputOrderLBSearch(decisions), Search.domOverWDegSearch(rest))` with the deciding variables first; `Search.minDomLBSearch(xs)` is first-fail with smallest value; `Search.intVarSearch(new FirstFail(model), new IntDomainMin(), xs)`; `Search.lastConflict(strategy)`; `model.getSolver().setLubyRestart(50, new FailCounter(model, 1), 10000)`

Docs: https://choco-solver.org/docs/
