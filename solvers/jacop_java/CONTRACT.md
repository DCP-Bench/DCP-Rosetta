# jacop_java: how this runner realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how JaCoP in Java
expresses it. Runner: [run.py](run.py), which compiles the submission with `javac` and starts the
driver [java/dcp/jacop/Runner.java](java/dcp/jacop/Runner.java), which owns the search, the optimum
proof, the enumeration and the protocol. The only helper class a submission sees is
[java/dcp/jacop/Model.java](java/dcp/jacop/Model.java). It wraps no JaCoP API: variables and
constraints are JaCoP's own classes, created on the `Store` the runner hands over. The solver skill
([skills/jacop-java/SKILL.md](skills/jacop-java/SKILL.md)) teaches standalone programs with their own
`main` and search; this file describes the submission form only.

## Submission file

One Java file, `model.java`, staged as `Submission.java` (javac needs a public class in a file of its
name). It declares **`public class Submission`**, has no `main`, and imports what it uses:
`org.jacop.core.*`, `org.jacop.constraints.*` (and `org.jacop.constraints.*` subpackages such as
`org.jacop.constraints.netflow`), `org.jacop.search.*`, `org.json.*` and `dcp.jacop.Model`. The class
path holds JaCoP 4.10.0, org.json 20250517 and the driver, nothing else. A submission posts
constraints; it does not create a search, read or write files, or print to the protocol.

## Entrypoint

```java
public static Model build(JSONObject instance, Store store)
```

`dcp.jacop.Model`, not an `org.jacop` class. The runner calls it once, by reflection, with a fresh
`Store`, and the method may be declared `throws Exception`. An exception thrown from it is
`execution_error` whose detail is the exception's `toString()` (a `FailException` thrown while
building, such as `new IntVar(store, "x", 3, 1)`, gets a note that JaCoP refused the model as built).
Returning anything but a `Model`, or a `Model` with no outputs, is `execution_error`.

## Instance

`instance` is an `org.json.JSONObject`: read it with `getInt`, `getLong`, `getBoolean`, `getString`,
`getJSONArray`, `getJSONObject` and `optX`; arrays are 0-based as in the JSON. Rows may be ragged or
of mixed types, since you walk the `JSONArray` yourself; `name` and `note` keys are present and can
be ignored. A value outside `int` range needs `getLong`.

## Outputs

`new Model().put("name", value)`, chained, once for each declared name and no others; a repeated name
throws. A value is an `IntVar` (a `BooleanVar` is one), an `int`, `Integer`, `long`, `Long` or
`Boolean` constant, or any nesting of Java arrays (`IntVar[]`, `IntVar[][][]`, `BooleanVar[][]`,
`int[]`) and `Collection`s of these. A number beyond the `int` range goes through
`putDigits("name", IntVar[] digits, 10)`, most significant digit first, and is reported as a 64-bit
integer. An `IntVar` is written as an integer, which the evaluator accepts for a declared Boolean; a `boolean` constant or `boolean[]` is written as `true`/`false`. Shapes follow each instance's own data: `build` runs once per instance,
so build every array from `instance` with that instance's size.

## Objective

`model.minimize(IntVar)` or `model.maximize(IntVar)`, at most once, chained on the returned `Model`.
The argument is a variable, so tie an expression to a fresh `IntVar` with a constraint
(`XplusYeqZ`, `SumInt`, `LinearInt`) and give it finite bounds wide enough for every value. Absent:
satisfaction. Do not bound the objective with a value known from elsewhere.

## Solving

- **Search:** `DepthFirstSearch` with `SimpleSelect`: smallest domain first, `IndomainMin`, over
  every integer variable in the store, so a solution fixes all of them. `model.search(IntVar[]
  order, ComparatorVariable<IntVar> comparator, Indomain<IntVar> indomain)` (`null` comparator is
  input order, `null` indomain is `IndomainMin`) puts your variables first; the rest are still
  labelled after them. The submission cannot add a search of its own. One thread.
- **Root propagation:** the runner calls `store.consistency()` before searching; a failure there is
  `unsat`.
- **Optimisation:** branch and bound with JaCoP's `labeling(store, select, cost)`; a maximised
  objective is minimised through a negated variable the runner adds. A search stopped by the deadline
  is `timeout`, with no solution emitted: the optimum was not proven. An exhausted search with no
  solution is `unsat`. After the proof the runner posts `cost == optimum` and enumerates the other
  optima (below).
- **Enumeration:** after each solution it posts a disjunction of `x != value` over the declared
  output variables that are not already constants, propagates it at the root, and searches again.
  Solutions are therefore distinct on the declared outputs. The status is `limit` when the requested
  count was emitted, `complete` when the search ended earlier (also when nothing is left to vary), and
  `unsat` when no solution exists at all.
- **Time:** the budget counts from JVM start (javac time is separate), each search gets the seconds
  left, and an expired search is `timeout`. `run.py` kills a JVM that outlives the budget by 5 s.
- **Protocol:** each solution is written as found, then one status.

## Compilation

`javac -encoding UTF-8 -nowarn` against the class path above, within the compilation timeout. Any
javac error is `compilation_error`; the messages are on stderr. A file with no top-level `Submission`
class is a `compilation_error`.

## Environment

Image `dcp-eval/jacop_java:v1`: `eclipse-temurin:21.0.8_9-jdk-noble` (digest pinned in the Dockerfile)
plus Python 3.12 for the runner. Jars at `/opt/jacop/jacop.jar` (JaCoP 4.10.0 from Maven Central,
AGPL-3.0, sha256 `4c7b5aa4…5585`), `/opt/jacop/json.jar` (org.json 20250517, sha256 `3ea61b2a…5796`)
and `/opt/jacop/dcp-jacop.jar` (the driver). JaCoP's Scala wrapper and FlatZinc front end are not on
the class path (their dependencies are not installed). The JVM runs with the serial collector, 2
compiler threads, `-Xss256m` and a heap of 75% of the container memory; an exhausted heap is an
`execution_error` with `OutOfMemoryError` in the detail. Inside the container: no network, a
read-only filesystem except `/tmp`, unprivileged. No licence key or size limits.

## Traps

- **JaCoP loses a constraint that is first found satisfied inside a search level.** The runner
  propagates the root before searching, so this does not affect submissions, but do not call `search`
  or `labeling` yourself.
- **`IntVar` is 32-bit.** A bound or product beyond `int` silently overflows or throws; keep domains
  and sums within `int`, and use `putDigits` for a larger declared output.
- **An empty domain** (`new IntVar(store, "x", 3, 1)`) throws `FailException` during `build`:
  `execution_error`, not `unsat`.
- **Unbounded variables.** `new IntVar(store)` spans about +-10^9 and propagates poorly; give every
  variable tight bounds.
- **`Alldistinct` is unsafe under enumeration; `Count` with its counter inside the list is unsound.** Use `Alldifferent` and `GCC`. `Sequence` and other decomposed constraints go through `store.imposeDecomposition(c)`.
- **Constraints must be imposed.** `Element.choose(...)` and every other constraint object does
  nothing until `store.impose(c)`; a dropped constraint shows up as `invalid_solution`.
- **Default search order.** The runner labels every integer variable, smallest domain first, so
  auxiliary 0/1 helpers are labelled before your decision variables. Pass the variables that matter to
  `model.search(order, null, null)` (it chains after `put`/`minimize`); several models timed out
  until they did. For a 0/1 matrix, column-major order with `new IndomainMax<>()` helped.
- **`Cumulative` rejects zero durations and zero needs** (`... must be greater than 0`): filter those
  tasks out.
- **The JDK standard library** (for example `java.time`) is on the class path.
- **Printing** is harmless: the driver points `System.out` at stderr.
- **A declared output not given** by the model only logs a warning; the evaluator then rejects the
  result as missing that output.

## Example

The pilot fixture [tests/fixtures/model_jacop_java.java](../../tests/fixtures/model_jacop_java.java)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```java
import org.jacop.constraints.XplusYeqC;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.constraints.XgteqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, n);
        IntVar y = new IntVar(store, "y", 0, n);
        Model m = new Model().put("x", x).put("y", y);
        if (inst.getBoolean("optimize")) {
            IntVar total = new IntVar(store, "total", 0, 2 * n);
            store.impose(new XplusYeqZ(x, y, total));
            store.impose(new XgteqC(total, n));
            return m.minimize(total);
        }
        store.impose(new XplusYeqC(x, y, n));
        return m;
    }
}
```
