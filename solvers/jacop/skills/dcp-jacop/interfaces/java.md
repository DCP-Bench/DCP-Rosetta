# JaCoP in Java (org.jacop:jacop)

JaCoP's native API: a Java library. Shared concepts, outcomes and enumeration strategy: [SKILL.md](../SKILL.md).

## Install

JaCoP is on Maven Central as `org.jacop:jacop` (latest release 4.10.0). Without a
build tool, download the jars and put them on the class path:

```bash
mkdir -p lib
curl -fsSLo lib/jacop.jar https://repo1.maven.org/maven2/org/jacop/jacop/4.10.0/jacop-4.10.0.jar
curl -fsSLo lib/json.jar  https://repo1.maven.org/maven2/org/json/json/20250517/json-20250517.jar
export CLASSPATH="$PWD/lib/jacop.jar:$PWD/lib/json.jar"
java Main.java data.json          # JDK 11+ runs one source file; the examples need 16+ (records)
```

The Java API needs no other dependency (Scala and slf4j in its POM serve the
Scala DSL and FlatZinc front end). JaCoP has no JSON reader; org.json
(`org.json:json`) is the small one used here. Licence: AGPL-3.0. Source and
build notes: [github.com/radsz/jacop](https://github.com/radsz/jacop).

## Quick start

```java
import java.nio.file.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class Main {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));  // {"n": 4}
        int n = data.getInt("n");                // read only the keys you need
        Store store = new Store();
        IntVar x = new IntVar(store, "x", 0, n), y = new IntVar(store, "y", 0, n);
        store.impose(new XplusYeqC(x, y, n));
        store.impose(new XneqY(x, y));

        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);              // otherwise it prints to stdout
        search.setTimeOut(10);                   // seconds
        SelectChoicePoint<IntVar> select =
            new SimpleSelect<>(new IntVar[]{x, y}, new SmallestDomain<>(), new IndomainMin<>());
        boolean found = search.labeling(store, select);
        if (found) System.out.println("x=" + x.value() + " y=" + y.value());
        else System.out.println(search.timeOutOccured ? "timeout" : "infeasible");
    }
}
```

## Modelling

Javadoc: [javadoc.io/doc/org.jacop/jacop](https://javadoc.io/doc/org.jacop/jacop/4.10.0/index.html)
(constraints in `org.jacop.constraints`, `.table`, `.cumulative`, `.regular`).
Comparison strings are `"=="`, `"!="`, `"<"`, `"<="`, `">"`, `">="`.

| Need | API |
|---|---|
| integer / Boolean / constant variable | `new IntVar(store, "x", min, max)`, `new BooleanVar(store, "b")` (an `IntVar` in 0..1), `new IntVar(store, c, c)` |
| `x = c`, `x != y`, `x < y`, ... | `XeqC`, `XneqY`, `XltY`, `XlteqC`, `XgtC`, `XgteqY` |
| `x + y = z`, `x + c = z`, `x + c <= z` | `XplusYeqZ`, `XplusCeqZ`, `XplusClteqZ` |
| `x * y = z`, `x * c = z`, `x / y = z`, `x mod y = z`, `abs(x) = y` | `XmulYeqZ`, `XmulCeqZ`, `XdivYeqZ`, `XmodYeqZ`, `AbsXeqY` |
| weighted sum `Σ w·x rel c` (or rel a variable) | `new LinearInt(IntVar[] x, int[] w, "<=", c)` |
| plain sum into a variable | `new SumInt(IntVar[] x, "==", total)`; the right side is an `IntVar`, never an `int` (use `new IntVar(store, n, n)`, or `LinearInt` with unit weights for a constant) |
| max / min of an array | `new Max(IntVar[] x, max)`, `new Min(IntVar[] x, min)` |
| all different | `Alldifferent` (bounds); use it, or pairwise `XneqY`, and avoid `Alldistinct`: in 4.10.0 it threw a `NullPointerException` on a 45-variable set and produced a wrong second solution when enumerating, twice |
| `a[i] = v` (array indexed by a variable) | [`Element.choose(i, int[] or IntVar[] a, v, offset)`](https://javadoc.io/doc/org.jacop/jacop/4.10.0/org/jacop/constraints/Element.html): **1-based**, pass `-1` for 0-based (an index already 1-based takes offset `0`; `-1` then prunes the index domain and the model is infeasible). It only returns the constraint: `store.impose(Element.choose(...))` |
| allowed tuples | `new org.jacop.constraints.table.Table(IntVar[] x, int[][] tuples)` |
| no overlap on one machine / resource limit | `cumulative.CumulativeUnary(starts, durations, resources, limit)`, `cumulative.Cumulative(...)` (all `IntVar[]`; import `org.jacop.constraints.cumulative.Cumulative`). Durations and resource needs must be above 0, so leave zero-duration or zero-need tasks out |
| non-overlapping rectangles | `Diff2(IntVar[][] rects)`, each row `{x, y, w, h}` |
| Hamiltonian circuit (successor array) | `Circuit(IntVar[] next)`: values are **1-based** |
| count occurrences | `Count(IntVar[] x, counter, value)` (the counter must not be a member of `x`: that is unsound), `GCC(IntVar[] x, IntVar[] counters)` (counts the values 0, 1, ... in order, so it covers self-describing sequences) |
| sliding window, stretch, among, regular | `Sequence(list, IntervalDomain set, q, min, max)` and kin are decomposed constraints: post with `store.imposeDecomposition(c)`, not `store.impose` |
| reification `b <-> c` | `new Reified(PrimitiveConstraint c, IntVar b)` |
| implication, if-then, logic | `Implies(b, c)`, `IfThen(c1, c2)`, `Or(c1, c2)` / `Or(c[])`, `And(...)`, `Not(c)` |

`Reified`, `Implies`, `IfThen`, `Or`, `And` and `Not` take `PrimitiveConstraint`s: the
comparison classes (`XeqC`, `XltY`, ...), `XplusYeqZ`, `XmulCeqZ`, `AbsXeqY`, `LinearInt`
and `SumInt`. `XmulYeqZ`, `XdivYeqZ`, `XmodYeqZ`, `Max`, `Min` and global constraints such
as `Alldifferent` are not; to reify one, reify its decomposition.

## Solving

Search API: [`DepthFirstSearch`](https://javadoc.io/doc/org.jacop/jacop/4.10.0/org/jacop/search/DepthFirstSearch.html),
[`SimpleSelect`](https://javadoc.io/doc/org.jacop/jacop/4.10.0/org/jacop/search/SimpleSelect.html).

`labeling(store, select)` searches for one solution; `labeling(store, select, cost)`
does branch and bound and **minimises** `cost`. On success the solution is left
assigned in the variables: read it with `x.value()`. Outcomes:

| `labeling` returns | `timeOutOccured` | Meaning |
|---|---|---|
| `true` | `false` | solution found; with a cost, **proven optimal** |
| `true` | `true` | (cost only) best solution so far, **not** proven optimal |
| `false` | `false` | proven infeasible |
| `false` | `true` | time limit hit, nothing found |

- **Maximise** by minimising the negation: `IntVar neg = new IntVar(store, -hi, -lo);
  store.impose(new XmulCeqZ(obj, -1, neg));` then label with cost `neg`. See
  [assets/java/all-optimal](../assets/java/all-optimal/README.md).
- **Time limit**: `search.setTimeOut(seconds)` or `setTimeOutMilliseconds(ms)`.
- **Heuristics**: `new SimpleSelect<>(vars, comparator, indomain)`; comparator `null`
  keeps input order, `SmallestDomain` is first-fail, `SmallestMin` suits start
  times; values via `IndomainMin`, `IndomainMax`, `IndomainMiddle`, `IndomainRandom`.
  For a 0/1 matrix, column-major order with `IndomainMax` is the order to try first
  ([SKILL.md](../SKILL.md#solving) has the rest of the search advice).
- **Errors**: JaCoP reports nothing on stderr for an inconsistent model; it just
  returns `false`. Bad arguments throw Java exceptions (stack trace on stderr).
  `store.consistency()` returning `false` before search means infeasible already.

## All solutions

```java
search.getSolutionListener().searchAll(true);
search.getSolutionListener().recordSolutions(true);   // keep them for getSolution(i)
search.labeling(store, select);
int count = search.getSolutionListener().solutionsNo();
Domain[] first = search.getSolutionListener().getSolution(1);   // 1-based; order of the select's variables
```

To avoid duplicates from labelled auxiliaries, print from a listener that keeps a
`Set` of output tuples: [assets/java/all-solutions](../assets/java/all-solutions/README.md).

**All optimal solutions**: after optimising, build the model again in a fresh `Store`,
post `XeqC(obj, optimum)` and enumerate
([assets/java/all-optimal](../assets/java/all-optimal/README.md)).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Labeling has finished ...` / `DFS1: ...` lines on stdout | search prints by default | `search.setPrintInfo(false)` |
| element or circuit off by one | `Element` and `Circuit` are 1-based | `Element.choose(i, a, v, -1)`; map circuit values with `- 1` |
| `ElementInteger(...) is not public` / deprecation warning on `new Element` | constructors hidden or deprecated | use `Element.choose(...)` |
| optimum reported after a timeout | only `found` was checked | also require `!search.timeOutOccured` ([Solving](#solving)) |
| a constraint seems ignored; a wrong value is accepted | the constraint was built, not imposed (`Element.choose` returns an object) | `store.impose(c)` for every constraint |
| `Arrays.copyOf(w, n)` weights give an infeasible model with no error | it pads with zeros when `n` exceeds the length, so weights and variables no longer match | give `LinearInt` weight and variable arrays of equal length |
| `cannot find symbol ... setDom` | `IntVar` has no such method | give the domain in the constructor |
| `no suitable constructor found for SumInt(..., String, int)` | the sum's right side must be an `IntVar` | `new IntVar(store, n, n)` or `LinearInt` |
| `... not in the allowed range` on a large constant | `IntDomain.MaxInt` is 536870909, not 2^31-1 | split a big product into two halves and join them with a `Table` over (x, target/x) |
| `GCC failure : join domain of x variables doesn't cover all count variables` | `GCC` counts the values 0, 1, 2, ... in order | shift the variables so they start at 0 (`XplusCeqZ`) and use one counter per shifted value |
| a conditional step such as `x - 3 = y` fails on every branch | an unconditional `XplusCeqZ` holds on all branches | `Reified(XeqC(selector, k), b)` then `Implies(b, c)` |
| a product-of-sums objective, or squares via `XmulYeqZ`, never proves the optimum | weak propagation | use Boolean membership with linear sums, or a `Table`, where possible |
| `ArrayIndexOutOfBoundsException` inside `LinearInt` / `SumInt` | posted over an empty array | skip the constraint, or compare the constant 0 directly |
| `is not abstract and does not override` / generic errors with `SimpleSelect` | raw types | use `IntVar[]` and `new SimpleSelect<>(..)`, `new IndomainMin<>()` |
| global constraint passed to `Reified` / `Or` will not compile | those take `PrimitiveConstraint` only | reify a decomposition ([Modelling](#modelling)) |
| a printed value is wrong although `labeling` returned `true` | that variable was not in the search and is still unfixed: `value()` then silently returns a domain bound | add it to the labelled array; `x.singleton()` tells whether it is fixed |

## Runnable examples

In `assets/java/`, each folder with its `README.md`, the program and `data.json`:
[all-solutions](../assets/java/all-solutions/README.md) (subset sum, de-duplicated
enumeration), [all-optimal](../assets/java/all-optimal/README.md) (maximise, then every
optimal assignment), [scheduling](../assets/java/scheduling/README.md) (`CumulativeUnary`,
minimise makespan).

## Further reading

- API reference: [javadoc.io/doc/org.jacop/jacop](https://javadoc.io/doc/org.jacop/jacop/4.10.0/index.html)
- User's guide (PDF): [guideJaCoP.pdf](https://github.com/radsz/jacop/blob/develop/doc/jacopguide/guideJaCoP.pdf)
- Examples: [src/main/java/org/jacop/examples/fd](https://github.com/radsz/jacop/tree/develop/src/main/java/org/jacop/examples/fd)
  (`ExampleFD.java` holds the shared search code; `SendMoreMoney`, `Queens`, `KnapsackExample`, `TSP` are short)
