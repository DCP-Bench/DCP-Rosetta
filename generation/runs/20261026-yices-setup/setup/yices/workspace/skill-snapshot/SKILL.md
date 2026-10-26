---
name: yices
description: Yices 2, an SMT solver for quantifier-free linear and nonlinear integer, real, Boolean and bit-vector formulas, used from its native C API (libyices, yices.h) or from Python (the yices package). Use when writing, debugging or explaining Yices models in C or Python, or when the user chose Yices or an SMT solver for a constraint, scheduling or feasibility problem.
license: Apache-2.0
compatibility: "C: a C compiler and Yices 2.7.0 built from source (GPL-3.0; with --enable-mcsat for nonlinear arithmetic, which needs libpoly and CUDD); libgmp only to read big integers. Python: Python 3.12 (tested) and the yices 1.1.6 package (MIT binding, ctypes) over the same libyices; the package does not contain the solver. No key, account or size limit."
metadata:
  domain: constraint-programming
  solver: yices
  paradigm: smt
  interfaces: "c, python"
---

# Yices

Yices 2 decides satisfiability of quantifier-free formulas over integers, reals, Booleans and bit-vectors.
You build a formula as **terms**, assert it in a **context**, call check, and read a **model**.
It is a satisfiability solver, not an optimiser: there is no objective, no global constraint catalogue and no
solution iterator. Optimise by asserting a tighter bound and checking again; enumerate by asserting a no-good.
**Terms are handles** (integers) in a global table, not objects with operators, in both bindings.

## Pick an interface

Read this file, then the one interface file for your language.

| | C | Python |
|---|---|---|
| Read | [interfaces/c.md](interfaces/c.md) | [interfaces/python.md](interfaces/python.md) |
| Package | `libyices` and `yices.h`, link `-lyices` | `yices` wheel (ctypes) over an installed `libyices` |
| Start and stop | `yices_init()` first (a segfault otherwise), `yices_exit()` last | automatic on import; `Yices.exit()` optional |
| Builder failure | returns `NULL_TERM` (-1); passing it on cascades; read `yices_error_string()` | raises `YicesException` at the call |
| Model after UNSAT or interrupt | `yices_get_model` returns NULL | `Model.from_context` returns a model of zeros, no error |
| Time limit | none built in: signal timer plus `yices_stop_search` | `ctx.check_context(timeout=seconds)` |
| Integers beyond int64 | `<gmp.h>` before `yices.h`, `yices_get_mpz_value`; `yices_get_int64_value` fails | `get_value` returns a lossy float; `Terms.integer` silently wraps (use `Terms.parse_rational`) |
| Reading JSON | not in Yices: a library such as cJSON | stdlib `json` |
| Memory | free each model, context, config and parameter record | `dispose()` on the same objects |

Use the language of the user's project. Without one, take Python for a quick model, C when the program
must be a standalone native executable.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [C](interfaces/c.md), [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

Terms: [term operations](https://yices.csl.sri.com/doc/term-operations.html). The exact calls are in the interface files.

- **Variables**: an uninterpreted term of integer, real or Boolean type. A decision variable is **not** a "variable"
  term (those are quantifier binders: asserting one fails with `assertion contains a free variable`).
- **Constraints**: bounds and comparisons are atoms over arithmetic terms; combine with and, or, not, implies,
  iff, xor and if-then-else. A Boolean is 0/1 through `ite(b, 1, 0)`, which gives counting and element.
- **Only `distinct` is a global constraint.** Express table, no-overlap, cumulative and the like with or/and of atoms,
  pairwise disjunctions, or sums of `ite`.
- `div` and `mod` floor: `-7 div 2 = -4`. `distinct` of one term is trivially true; of no terms it is an error
  (each interface file gives the exact failure): skip the constraint when there is nothing to compare.
- **Nonlinear arithmetic** (a product or division of variables) builds fine but is rejected at assert time by a
  default context (`the context does not support non-linear arithmetic`). Create the context from the logic
  `QF_NIA`, which uses MCSAT and needs a library built with `--enable-mcsat`.
- **Objective**: a term that equals the cost. A compound term (a sum, a count) needs no variable of its own: the model
  evaluates it from the values of its variables when read. To minimise the number of distinct values among
  variables `x`, sum over each candidate value `k` of `ite(or(x_i == k for all i), 1, 0)`, then tighten.

**Readable models.** Open the program with a comment that states the problem, and start each block of
constraints with a comment in the words of the problem statement, not the API call. Take every size from
the input data.

## Solving

Details: [context operations](https://yices.csl.sri.com/doc/context-operations.html), [model operations](https://yices.csl.sri.com/doc/model-operations.html).

Statuses (the same numbers in both bindings: IDLE 0, SEARCHING 1, UNKNOWN 2, SAT 3, UNSAT 4, INTERRUPTED 5, ERROR 6):

| Status | Meaning |
|---|---|
| SAT | a model exists; read it |
| UNSAT | proven no solution. After a bound tightened on a found solution, the last solution is optimal |
| UNKNOWN | the solver gave up; no model to rely on |
| INTERRUPTED | stopped (time limit or stop request): no proof either way |
| ERROR | misuse, such as checking an interrupted context |

- Read values **only after SAT**. An output term that occurs in no assertion reads as 0 (false).
- After INTERRUPTED the context accepts only a reset (which drops all assertions) or is replaced by a new one.
- Assertions after a SAT check are accepted in a default context, and so are assertions after UNSAT (the status
  stays UNSAT). Terms are global, so a new context can assert the same terms again.
- **Optimise by tightening.** After each SAT, read the objective `best` and assert `objective < best` (minimise)
  or `objective > best` (maximise) in the same context; repeat until UNSAT, which proves `best` optimal. If a
  limit stops the loop, `best` is only the best found. A bound assumed in advance that the model does not imply
  silently removes solutions.

## All solutions

Details: [assert and blocking clause](https://yices.csl.sri.com/doc/context-operations.html#c.yices_assert_blocking_clause).

Assert a **no-good over the output terms only** after each model: the disjunction of "this output differs from
its value". UNSAT ends the loop and proves the list complete. `assert_blocking_clause` /
`yices_assert_blocking_clause` is **not** a substitute: it blocks the Boolean abstraction, and on integer
variables it stops early and misses solutions.
All optimal solutions: find the optimum by tightening, build a **new** context from the same terms with
`objective == best`, then run the no-good loop.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `assertion contains a free variable` | a quantifier-bound variable used as a decision variable | create an uninterpreted term |
| `the context does not support non-linear arithmetic` | product of variables in a default context | `QF_NIA` context ([Modelling](#modelling)) |
| `argument is not an arithmetic term` | a number or Boolean passed where an arithmetic term is needed | wrap numbers as terms; compare terms of one type |
| enumeration stops early or repeats | blocking clause used on integers | no-good over the outputs ([All solutions](#all-solutions)) |
| no model, or meaningless zeros | a model read after UNSAT or a limit | check the status first (interface table row "Model after UNSAT or interrupt") |
| `the context state does not allow operation` | an operation on a context after INTERRUPTED | reset the context or build a new one |
| `invalid term` | a value that is not a term handle was passed as a term | see the interface file for the binding-specific cause |
| a wrong constant at 2^63 or above | 64-bit integer constants | see the interface table row for big integers |

Per-binding symptoms are in each interface file.

## Further reading

- Yices manual: <https://yices.csl.sri.com/doc/>
- Source and releases: <https://github.com/SRI-CSL/yices2>
- Python binding: <https://github.com/SRI-CSL/yices2_python_bindings>
