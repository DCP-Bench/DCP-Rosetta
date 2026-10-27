# PyCSP3 in Python (pycsp3)

The native binding: PyCSP3 is a Python library whose `solve()` writes XCSP3 and runs the ACE jar.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Reading data](#reading-data)
- [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues)
- Examples: [satisfy](../assets/python/satisfy-queens/README.md), [all solutions](../assets/python/all-solutions-latin/README.md),
  [all optimal](../assets/python/all-optimal-permutation/README.md), [maximise](../assets/python/maximise-knapsack/README.md),
  [minimise](../assets/python/minimise-coins/README.md), [infeasible](../assets/python/infeasible-pigeonhole/README.md),
  [scheduling](../assets/python/scheduling-jobshop/README.md), [fewest colours](../assets/python/colouring-min-colours/README.md),
  [JSON input](../assets/python/json-input-shifts/README.md)
- References: [language.md](../references/python/language.md) (every construct, limits, reserved
  words, failing forms), [examples.md](../references/python/examples.md) (tested models per global)

## Install

```bash
pip install pycsp3                 # also installs lxml; ACE-2.6.jar is inside the wheel
java -version                      # any recent JRE; ACE's classes are Java 8/11
python -c "from importlib.metadata import version; print(version('pycsp3'))"
```

`pycsp3` has no `__version__`. Importing pycsp3 in a script that declares no variables prints
`Warning: no variables in this model` at exit; harmless. Java heap: set it with
`JAVA_TOOL_OPTIONS=-Xmx2g` (Java then prints `Picked up JAVA_TOOL_OPTIONS` on stderr).
Details: [installation](http://pycsp.org/documentation/installation).

## Quick start

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4))
satisfy(AllDifferent(x), x[0] < x[1])
minimize(Sum(x[i] * (i + 1) for i in range(4)))

status = solve()                     # OPTIMUM, SAT, UNSAT or UNKNOWN
if status is OPTIMUM:
    print(values(x), bound())        # [2, 3, 1, 0] 11
```

`python model.py` writes `model.xml` and a `solver_*.log` file to the working directory.
A small model takes about 2 s wall in total (Python start, compilation, a Java start).

## Modelling

Every construct below was run; the full catalogue with failing forms is in
[language.md](../references/python/language.md), and per-global models in
[examples.md](../references/python/examples.md). API docs: [pycsp.org](https://pycsp.org/).

| Need | API |
|---|---|
| integer variable | `Var(dom=range(lo, hi))` (upper bound excluded), a list or a set; Boolean `dom={0, 1}` |
| array, matrix | `VarArray(size=n, dom=...)`, `VarArray(size=[r, c], dom=...)`; `grid[i][j]`, column `grid[:, j]` |
| post constraints | `satisfy(c1, c2, ...)`; lists and generators inside are flattened |
| arithmetic | `+ - * // % abs`, `==`, `!=`, `<`; `Sum(w[i] * x[i] for i in range(n))`; integers only |
| all different | `AllDifferent(x)`, also over expressions `AllDifferent(q[i] + i for i in range(n))` |
| counting | `Count(x, value=v)`, `NValues(x)`, `Exist(x, value=v)`, `Cardinality(x, occurrences={...})` |
| element | `v == t[idx]` with `t` a `VarArray` and `idx` a variable |
| table | `(x, y) in {(0, 1), (1, 2)}`, `x in {1, 3}`, `Table(scope=x, supports=[...])`, `conflicts=[...]`; `ANY`/`'*'` wildcard |
| min / max | `Minimum(x) == lo`, `Maximum(x) == hi`, `MaximumArg(x, rank=TypeRank.FIRST) == i` |
| scheduling | `NoOverlap(origins=s, lengths=d)`, `Cumulative(origins=s, lengths=d, heights=h) <= cap` |
| graphs, permutations | `Circuit(x)` (0-based successors), `Channel(x, y)` (inverse) |
| sequences | `Increasing(x, strict=True)`, `LexIncreasing([x, y])`, `Regular(scope=x, automaton=Automaton(...))` |
| packing | `BinPacking(b, sizes=w, limits=caps)`, `Knapsack(x, weights=w, wlimit=c, profits=p) >= k` |
| distance | `Hamming(x, y) == k` (positions where two arrays differ) |
| logic | `imply(a, b)`, `If(c, Then=..., Else=...)`, `Or`, `And`, `Xor`, `Iff`; reify `(b == 1) == (Sum(x) > 4)` |
| objective | at most one `minimize(term)` or `maximize(term)` |

Rules pycsp3 enforces (messages in [Common issues](#common-issues)):

- **One declaration per line.** `a, b = Var(...), Var(...)` fails.
- **Declare variables at module level, preferably as one `VarArray`.** A `Var` without `id=`
  made in a loop, comprehension, helper function or dict fails. `VarArray` inside a function
  works; with `id="x"` it is safe everywhere.
- **Reserved identifiers**: `E` and 57 XCSP words (`min`, `max`, `dist`, `in`, `set`, `sin`,
  `card`, ...; full list in [language.md](../references/python/language.md#variables-and-domains)).
  ACE stops with `The id E is a keyword`.
- **Value limits**: values at or above about 2.1e9 (either sign) fail; the total number of
  domain values over all variables must stay under about 3e7 (four `range(10**7)` domains
  solved, five ran out of a 1200 MiB heap; one `range(10**9)` too).
- **A Python list indexed by a variable fails**: make it a `VarArray`, or use a `Table` of
  `(index, value)` pairs ([JSON example](../assets/python/json-input-shifts/README.md)).
- `from pycsp3 import *` replaces the builtin `min`/`max` and defines `values`, `value`,
  `Sum`, `ANY`, ...: `min(..., key=...)` fails (use `builtins.min` after `import builtins`),
  and a data list called `values` hides the function.
- `Not(c)` fails in 2.6.1: write the negated relation (`!=`, `>=`).

## Reading data

Read a JSON file with the standard library's `json` and take every size from it; extra keys
are simply never read ([example](../assets/python/json-input-shifts/README.md)):

```python
import json, sys
from pycsp3 import *
with open(sys.argv[1] if len(sys.argv) > 1 else "data.json") as f:
    d = json.load(f)
x = VarArray(size=d["n"], dom=range(d["n"]))
satisfy(AllDifferent(x))
```

PyCSP3's own `python model.py -data=file.json` (then `data.n`) breaks on keys starting
with `_` and on one-key files ([details](../references/python/language.md#reading-data)); plain `json`
avoids both.

## Solving

`solve(solver=ACE, options="", verbose=-1, sols=None)` compiles, runs ACE and returns a
`TypeStatus`; compare with `is`. Solver options: `java -jar <path>/ACE-2.6.jar` lists them,
or the [options PDF](https://github.com/xcsp3team/pycsp3/blob/master/docs/optionsSolvers.pdf).

| Status | Meaning |
|---|---|
| `OPTIMUM` | optimisation, optimum proven |
| `SAT` | a solution; for an optimisation, **not proven optimal** (time limit) |
| `UNSAT` | proven infeasible; `n_solutions()` is `None`, no values stored |
| `UNKNOWN` | nothing found: time limit, or a solver error (prints `Actually, the instance was not solved`) |

- Values: `value(v)`, `values(x)` (nested like `x`), `values(x, sol=k)` for solution k;
  objective value `bound()`. An array element no constraint mentions reads as `*` (`ANY`);
  a lone `Var` no constraint mentions makes `value(z)` raise `AssertionError`. ACE only
  sees constrained variables, so constrain everything you print.
- Time limit `options="-t=10s"` (**a bare number is milliseconds**), seed `-seed=1`.
- `verbose=1` prints the compilation and the ACE command and log; `solver().last_log` is the
  log file path. `clear()` drops the whole model so a script can build and solve another.
- Files: `solve()` writes `<script>.xml` (`model.xml` for `model.py`) and `solver_*.log` to the
  **current working directory**, not beside the script. If that directory is read-only,
  `solve()` raises `OSError: [Errno 30] Read-only file system` while compiling. Run the script
  from a writable directory.
- **Errors**: a Python modelling error raises (or pycsp3 prints `ERROR: ...` and exits). An
  ACE error gives `UNKNOWN`, with `Fatal Error: ...` in the log, or only `! ERROR (use -ev
  for more details)` for a Java exception; `options="-ev"` does not bring it into the log,
  so rerun ACE on the XML: `java -jar <path>/ACE-2.6.jar model.xml -ev` prints the
  exception (e.g. `java.lang.OutOfMemoryError: Java heap space`). The jar path:
  `os.path.join(os.path.dirname(pycsp3.__file__), "solvers", "ace", "ACE-2.6.jar")`.
- **Checking a solution**: ACE 2.6 can report wrong solutions for `Product` over four or
  more variables (see [lessons](../SKILL.md#modelling-lessons)). The XCSP3 checker in the same jar
  verifies one: write `str(solution())` to `sol.xml`, then
  `java -cp <jar> org.xcsp.parser.callbacks.SolutionChecker model.xml sol.xml` prints `OK`
  or `INVALID Solution!` with the violated constraint.

## All solutions

`solve(sols=ALL)` (or `sols=k`) enumerates; read solution k with `values(x, sol=k)`
([example](../assets/python/all-solutions-latin/README.md)). Two traps:

- `n_solutions()` misparses ACE's thousands separator (`1,500` gives 500). Count the stored
  solutions instead: `len(x[0].values)` for any variable `x[0]` of the model.
- The status is `SAT` whether or not the search finished. Only the log tells: it contains
  `d COMPLETE EXPLORATION` or `d INCOMPLETE EXPLORATION` (`solver().last_log`).
- An infeasible model enumerates to `UNSAT`, not `SAT` with zero solutions: `n_solutions()` is
  `None` and `x[0].values` is empty. Take the count as `len(x[0].values) if status is SAT else 0`;
  it is 0 with no error.

ACE enumerates assignments of all constrained variables, so an auxiliary variable that is
not fixed by the ones you print repeats them; deduplicate on the printed values or fix it.

**All optimal solutions** ([example](../assets/python/all-optimal-permutation/README.md)): solve with the
objective, require `OPTIMUM`, keep `best = bound()`; then `clear()`, rebuild the model (a
function returning the arrays, with `id=`), post `satisfy(term == best)` with no objective,
and `solve(sols=ALL)`.

## Common issues

Shared solver-side symptoms: [SKILL.md](../SKILL.md#common-issues).

| Message or symptom | Cause | Fix |
|---|---|---|
|---|---|---|
| `AssertionError: Every simple declaration must be on its own line` | two declarations on one line | one per line |
| `The identifier z is used twice. This is not possible` | `Var` without `id=` in a loop | `VarArray`, or `id=f"z{i}"` |
| `The variable identifier None is not valid` | `Var` without `id=` in a helper function | `id=name` |
| `The variable identifier [ is not valid` | `Var` without `id=` in a list comprehension | `VarArray`, or `id=` |
| `The variable identifier d[0] is not valid` | `Var` stored in a dict | `id="d0"` |
| `TypeError: list indices must be integers or slices, not VariableInteger` | Python list indexed by a variable | `VarArray` or `Table` |
| `TypeError: min() got an unexpected keyword argument 'key'` | builtin `min` replaced | `builtins.min` |
| `TypeError: bad operand type for unary ~: 'list'` | `Not(...)` | negated relation |
| `ValueError: Problem: bad form of predicate 0.5` | float in an expression | scale to integers |
| `Bad arity for node MUL. It is 1 but it should be between 2 and inf` | `Product` of one value | use the value |
| `TypeError: Wrong type for first` | `rank='first'` | `rank=TypeRank.FIRST` |
| `*` in `values(x)`; `AssertionError` from `value(z)` | variable in no constraint | constrain it |
| `n_solutions()` too small | thousands separator | [count stored values](#all-solutions) |
| `n_solutions()` is `None` after enumeration | the model is infeasible: `solve(sols=ALL)` returned `UNSAT` | count is 0; [status check](#all-solutions) |
| `OSError: [Errno 30] Read-only file system` from `solve()` | the working directory is read-only; pycsp3 writes the XML and the log there | run from a writable directory ([Solving](#solving)) |
| `ValueError: Field names cannot start with an underscore` | `-data=` with a `_key` | [plain `json`](#reading-data) |
