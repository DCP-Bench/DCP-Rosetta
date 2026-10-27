# Sources for `choco`

Merged from two single-language skills (`choco-java`, `choco-python`). Their text and examples were
moved, not rewritten, into `interfaces/` and `assets/`; `SKILL.md` keeps what both state, each
claim checked in both bindings as listed below.

## Shared (SKILL.md)

- Choco documentation, <https://choco-solver.org/docs/>: the constraint catalogue and search.
- Free auxiliary variables: 12 enumerated solutions for `x` in 1..2 with a free `aux` in 0..5, 2 with
  `aux = x`, run in Java and in Python.
- Argument order of `element`, `min`, `max` and `count`, and the objective as an IntVar: checked in
  each binding (Java: `references/java/Catalogue.java`; Python: the list under Python below).
- The interface table, Python column, from pychoco 0.2.1 in its container (Python 3.12):
  - `dir(Model())` lists every constraint named in the Modelling table in snake_case
    (`all_different`, `sub_circuit`, `bin_packing`, `int_value_precede_chain`, `keysort`, ...).
  - `Model.__init__(self, name=None, **kwargs)` takes no settings, and no LCG option exists.
  - `dir(solver)` has preset `set_*_search(*intvars)` methods and `add_hint`, no restart policy, no
    search state and no `reset`; the `find_*` calls take `time_limit`, `node_limit`, `fail_limit`,
    `restart_limit` and `backtrack_limit`.
  - Run on 8 queens: `set_min_dom_lb_search`, `set_dom_over_w_deg_search` and
    `set_input_order_lb_search` each returned a valid placement; `add_hint(q[0], 3)` gave `q[0] = 3`;
    `find_all_solutions()` returned 92 and `find_all_solutions(fail_limit=5)` returned `[]`.

- Interface-specific claims added while merging, run in the containers: pychoco `n_values(vars, count)`
  matches brute force on every assignment of three variables in 0..2 (27 solutions); pychoco
  `if_then` and `if_then_else` post at once and return `None`; the signatures of pychoco `knapsack`,
  `n_values` and `int_value_precede_chain` from `inspect.signature`; Java `SetVar.getValue()` returns
  the solved set (`{1, 3}` for a 2-element set containing 3).

## Merge verification

Two rounds of the toy problems (cryptarithm, graph colouring, job shop, knapsack, all-optimal
knapsack, n-queens, all n-queens; 18 instances) by fresh agents given only this skill, one per
interface and round: Java 18/18 and 18/18, Python 18/18 and 18/18. Gaps they reported were fixed
in the interface files between rounds.

## Java

Tested with Choco 6.0.1 (2026-05-21) and Gson 2.11.0 on Eclipse Temurin JDK 21 (Linux container).

Existing skills: not searched in this refactor; an earlier version of this skill was written from the
Choco documentation and the jar's own sources.

- Choco 6.0.1 from Maven Central: `org.choco-solver:choco-solver:6.0.1`, the `jar-with-dependencies` artifact,
  sha256 `c1956f7688f0982c55dc12edfa5695b60085fb9c37f3fbc6cf7efc53afc0da39`. Upstream:
  <https://github.com/chocoteam/choco-solver/releases/tag/v6.0.1>. Licence: BSD-3-Clause.
- `choco-solver-6.0.1-sources.jar` from the same Maven directory: every signature in
  `references/java/constraints.md` was extracted from the factory interfaces `Model` implements
  (`IIntConstraintFactory`, `ISchedulingFactory`, `IReificationFactory`, `ISatFactory`,
  `IDecompositionFactory`, `IResultVariableFactory`, `IVariableFactory`, `IViewFactory`,
  `ISetConstraintFactory`, `IGraphConstraintFactory`), plus `Solver`, `Search`, `Tuples`,
  `FiniteAutomaton`, `ArExpression` and `ReExpression`.
- Gson 2.11.0 from Maven Central, <https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar>,
  for the JSON examples. Licence: Apache-2.0. Checked: `getAsInt()` on a JSON boolean throws
  `NumberFormatException`; `getAsBoolean()` reads it.
- Choco documentation, <https://choco-solver.org/docs/>: modelling, search strategies,
  restarts, solving.
- `references/java/Catalogue.java` checks the semantics stated in interfaces/java.md and constraints.md against
  brute force, once with default settings and once with LCG on. Its `signatures()` method compiles every
  other call these files name. All checks agreed with brute force on the tested run; the constraints that
  throw or miscount under LCG are the ones listed in interfaces/java.md.
- The examples under `assets/java/` run with `java File.java` and print the values listed in their READMEs.
  The optima were checked independently: the sudoku has one solution (checked by enumerating all
  completions of the grid); the transport cost 240, the production profit 17, the project makespan 8,
  the machine makespan 7 and the knapsack value 20 were checked by brute force; the choice of two items
  at cost 3 has two optima; the coin count 10 is the known number of ways.
- `references/java/examples.md`: the roster optimum 34 and the machine makespan 8 were run as written.
- The no-good recipe in interfaces/java.md was run: the loop on `x <= y` over 0..2 counts 6.

## Python

Tested with pychoco 0.2.1 and 0.4.0 (Choco bundled in each wheel), Python 3.12.11, inside a Linux
container image. Every example passes on both versions; 0.4.0 was installed into a
scratch directory in the same image for the comparison.

Refactored from an earlier integration skill; examples verified inside the same image.

- <https://pychoco.readthedocs.io/en/latest/> — pychoco reference, accessed 2026-09-16
- <https://pypi.org/project/pychoco/> — the wheels tested (0.2.1, 0.4.0); each bundles the Choco native library, so no JVM is needed
- <https://choco-solver.org/docs/> — Choco 4 solver documentation, for the meaning of the constraints pychoco exposes
- <https://github.com/chocoteam/pychoco> — pychoco source

### Independent toy-problem test

An independent agent wrote one program per toy problem from this skill alone (no access to the
examples or the solver source), Python 3.12.11 with pychoco 0.2.1 in the image.

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | 3 (ab-ab-aaa, send-more-money, two-two-four) | 3/3 |
| graph-colouring | 3 (cycle6, k4-tail, petersen) | 3/3 |
| jobshop | 2 (ft06, small) | 2/2 |
| knapsack | 2 (p01, small) | 2/2 |
| knapsack-all-optimal | 3 (fourteen, ties, unique) | 3/3 |
| n-queens | 3 (n3, n4, n8) | 3/3 |
| n-queens-all | 2 (n6, n8) | 2/2 |
| **Total** | **18** | **18/18** |

All 18 passed on the first run, so no repair was needed. The gaps the tester reported (JSON I/O,
distinct-value counting, no-overlap, `arithm` forms, `scalar` with repeated variables, `Solution` access)
are now covered in interfaces/python.md. The tester did not execute the skill's example files; those are checked separately.

### Verified by running (inside the image)

- Method names: `sum`, `min`, `max` exist; `sum_`, `min_` do not; `and_`, `or_`, `not_` exist.
- `element(value, table, index)` gave pairs (5,0), (7,1), (9,2) for table [5, 7, 9]; `max(r, [a, b])` gives the maximum.
- `find_solution` and `find_optimal_solution` return `None` when infeasible; `find_all_solutions` and
  `find_all_optimal_solutions` return `[]`; `solve()` returns `False`.
- A second solve on one model after an infeasible result (any `get_solver()`) ends the process with a JVM
  "Fatal error", exit code 99; a new `Model` for the second solve works.
- `find_all_optimal_solutions` returns both optima of a tie (choose-two example).
- A posted vs. unposted constraint: with `x + y >= 1` posted and `arithm(x, "=", 2)` left unposted, 15
  solutions; Choco prints `ARITHM ([x = 2]) is free` on stdout.
- Free auxiliary variables multiply enumerated solutions: 12 for 2 outputs with a free `aux` in 0..5, 2 when
  `aux = x`.
- `limit_time`: `"0.5s"` honoured (0.80 s on a 10^6-solution enumeration); `"300ms"` ignored (2.87 s, full run);
  `"2s"` stopped the enumeration around 2.6 s. (Earlier measurement: a 10 million enumeration with `"300ms"`
  ran to completion, 40 s.)
- Operators: `x + y == 3` returns a BoolVar with no `post` method; `model.arithm(x + y, "=", 3)` gives 4 solutions for x, y in 0..3.
- `arithm(q, "+", 2, "=", up)` (int middle value) gives the correct pairs; `arithm(2, "<=", q)` raises
  `AttributeError` (an int on the left).
- `cumulative` with int heights or capacity raises `AttributeError`; with IntVars it works.
- No-overlap: three tasks of length 2 on one unit-capacity `cumulative` gave 6 solutions, none overlapping.
- `scalar` with a repeated variable (`[x, x]`, `[1, 2]`, `= 3`) and with mixed signs matches a brute-force count (15 solutions).
- `Solution`: `get_int_val` and `get_set_val` exist, `get_value` does not; a `Solution` keeps its values after a
  later solve; `var.get_value()` after `find_all_solutions` raises `AssertionError: ... not instantiated`.
- Scheduling: `model.task(start, duration, end)` and `model.cumulative(tasks, heights, capacity)` gave makespan 9,
  matching an independent brute force, on both 0.2.1 and 0.4.0 without any extra call.
- `ensure_bound_consistency()` exists on `Task` in 0.2.1 and is absent in 0.4.0; no example calls it.
- Transport and production optima (240, 17) checked against an independent brute force and by hand.
- Distinct-value count: the 5-node graph with a triangle gives 3 colours (distinct-count example).
- Knapsack instance in `json-io` (weights 3, 4, 2, 5; values 7, 9, 4, 8; capacity 9) gives profit 20 (items 0, 1, 2).
