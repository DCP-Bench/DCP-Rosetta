---
name: jacop-java
description: JaCoP, a Java constraint programming (CP) solver over finite integer domains; package org.jacop (core, constraints, search). Use when writing, debugging or explaining JaCoP models in Java - scheduling, assignment, puzzles, optimisation with global constraints - or when the user has chosen JaCoP.
license: Apache-2.0
compatibility: Requires a JDK 11+ (Java 21 tested) and the org.jacop:jacop jar (AGPL-3.0, no licence key); examples read JSON with org.json
metadata:
  domain: constraint-programming
  solver: jacop
  paradigm: cp
---

# JaCoP (Java)

JaCoP is a finite-domain CP solver used as a plain Java library. A model is a
`Store` holding `IntVar`s, constraints are objects passed to `store.impose(...)`,
and solving is a separate **search** object you configure: which variables to
label, in which order, with which values. The one idea to keep in mind: *JaCoP
only reports a solution once every variable you gave the search is fixed*, so the
variables you label decide both what a solution is and how many duplicates you see.

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling)
- [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues)
- Runnable examples in `assets/`: `all-solutions` (subset sum, de-duplicated
  enumeration), `all-optimal` (maximise, then every optimal assignment),
  `scheduling` (`CumulativeUnary`, minimise makespan)

## Install

JaCoP is on Maven Central as `org.jacop:jacop` (latest release 4.10.0). Without a
build tool, download the jars and put them on the class path:

```bash
mkdir -p lib
curl -fsSLo lib/jacop.jar https://repo1.maven.org/maven2/org/jacop/jacop/4.10.0/jacop-4.10.0.jar
curl -fsSLo lib/json.jar  https://repo1.maven.org/maven2/org/json/json/20250517/json-20250517.jar
export CLASSPATH="$PWD/lib/jacop.jar:$PWD/lib/json.jar"
java Main.java data.json          # JDK 11+: compiles and runs one source file
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

`Reified`, `Implies`, `IfThen`, `Or`, `And` and `Not` take `PrimitiveConstraint`s
(the `X...` and `LinearInt` family), never global constraints such as `Alldifferent`.
To reify a global, reify its decomposition.

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
  [assets/all-optimal](assets/all-optimal/README.md).
- **Time limit**: `search.setTimeOut(seconds)` or `setTimeOutMilliseconds(ms)`.
- **Heuristics**: `new SimpleSelect<>(vars, comparator, indomain)`; comparator `null`
  keeps input order, `SmallestDomain` is first-fail, `SmallestMin` suits start
  times; values via `IndomainMin`, `IndomainMax`, `IndomainMiddle`, `IndomainRandom`.
- **Search order and value choice decide many models.** `SimpleSelect` over every
  variable in input order, or smallest-domain over auxiliary 0/1 helpers, can fail
  where an explicit order succeeds. Label the decision variables first and the helper
  Booleans last; for a minimisation over Boolean flips label the smaller group first;
  for a 0/1 matrix try column-major order with `IndomainMax`. Test two or three orders
  on the largest instance before concluding the model is too weak.
- **No restarts, no dom/wdeg.** For a hard satisfaction instance a static order after
  ranking values by difficulty, or `SmallestDomain` with `IndomainRandom`, worked where
  the defaults did not. Cheap wins before any of that: implied sums and prefix bounds,
  equalities where the problem says exactly, a `Table` over an enumerated pattern space
  (build the tuples in Java; tens of thousands are fine), and symmetry breaking only
  where the problem allows it.
- **Check the first solution, not a later one.** A model can emit a wrong first solution
  and a right second one when a constraint loses propagation.
- **Which variables to label**: label every variable whose value you read, plus
  any auxiliary that propagation does not fix once those are fixed. When unsure,
  label all of them (decisions first) and de-duplicate, as below.
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

Every distinct assignment of the **labelled** variables counts, so labelling an
auxiliary that is not fixed by your outputs yields duplicates. Either label only
output variables that fix everything else, or print from a listener that keeps a
`Set` of output tuples: [assets/all-solutions](assets/all-solutions/README.md).

**All optimal solutions**: optimise, read the optimum, then build the model again
in a fresh `Store`, post `XeqC(obj, optimum)` and enumerate. Write the model in a
method so it can be built twice ([assets/all-optimal](assets/all-optimal/README.md)).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Labeling has finished ...` / `DFS1: ...` lines on stdout | search prints by default | `search.setPrintInfo(false)` |
| element or circuit off by one | `Element` and `Circuit` are 1-based | `Element.choose(i, a, v, -1)`; map circuit values with `- 1` |
| `ElementInteger(...) is not public` / deprecation warning on `new Element` | constructors hidden or deprecated | use `Element.choose(...)` |
| more solutions than expected, repeats in output | auxiliary variables labelled | de-duplicate on output tuples ([All solutions](#all-solutions)) |
| optimum reported after a timeout | only `found` was checked | also require `!search.timeOutOccured` ([Solving](#solving)) |
| maximisation returns the minimum | `labeling(..., cost)` always minimises | label with the negated objective |
| second search on the same `Store` gives stale or wrong results | the first solution stays assigned in the store, and constraints added afterwards are not reliably kept | build a fresh `Store` for every search |
| a constraint seems ignored; a wrong value is accepted | the constraint was built, not imposed (`Element.choose` returns an object) | `store.impose(c)` for every constraint |
| `Arrays.copyOf(w, n)` weights give an infeasible model with no error | it pads with zeros when `n` exceeds the length, so weights and variables no longer match | give `LinearInt` weight and variable arrays of equal length |
| `cannot find symbol ... setDom` | `IntVar` has no such method | give the domain in the constructor |
| `no suitable constructor found for SumInt(..., String, int)` | the sum's right side must be an `IntVar` | `new IntVar(store, n, n)` or `LinearInt` |
| `... durations must be greater than 0 violated` from `Cumulative` | a zero duration or resource need | drop those tasks from the constraint |
| `... not in the allowed range` on a large constant | `IntDomain.MaxInt` is 536870909, not 2^31-1 | split a big product into two halves and join them with a `Table` over (x, target/x) |
| a conditional step such as `x - 3 = y` fails on every branch | an unconditional `XplusCeqZ` holds on all branches | `Reified(XeqC(selector, k), b)` then `Implies(b, c)` |
| a product-of-sums objective, or squares via `XmulYeqZ`, never proves the optimum | weak propagation | use Boolean membership with linear sums, or a Table, where possible |
| `ArrayIndexOutOfBoundsException` inside `LinearInt` / `SumInt` | posted over an empty array | skip the constraint, or compare the constant 0 directly |
| `is not abstract and does not override` / generic errors with `SimpleSelect` | raw types | use `IntVar[]` and `new SimpleSelect<>(..)`, `new IndomainMin<>()` |
| global constraint passed to `Reified` / `Or` will not compile | those take `PrimitiveConstraint` only | reify a decomposition ([Modelling](#modelling)) |
| a printed value is wrong although `labeling` returned `true` | that variable was not in the search and is still unfixed: `value()` then silently returns a domain bound | add it to the labelled array; `x.singleton()` tells whether it is fixed |

## Further reading

- API reference: [javadoc.io/doc/org.jacop/jacop](https://javadoc.io/doc/org.jacop/jacop/4.10.0/index.html)
- User's guide (PDF): [guideJaCoP.pdf](https://github.com/radsz/jacop/blob/develop/doc/jacopguide/guideJaCoP.pdf)
- Examples: [src/main/java/org/jacop/examples/fd](https://github.com/radsz/jacop/tree/develop/src/main/java/org/jacop/examples/fd)
  (`ExampleFD.java` holds the shared search code; `SendMoreMoney`, `Queens`, `KnapsackExample`, `TSP` are short)
