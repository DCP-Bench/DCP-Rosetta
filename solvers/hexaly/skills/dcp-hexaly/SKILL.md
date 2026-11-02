---
name: dcp-hexaly
description: Hexaly Optimizer (formerly LocalSolver), a hybrid solver that combines local search with bounds for nonlinear models over Boolean, integer, float, list, set and interval decisions, used from Python (hexaly). Covers install and licence, modelling, proven versus found optima, infeasibility, and enumerating all or all optimal solutions. Use when writing, debugging or explaining Hexaly models, or when the user has chosen Hexaly.
license: Apache-2.0
compatibility: "Python: Python 3.8+ and pip install hexaly (tested with hexaly 15.0.20261026 on Python 3.12, Linux). Every run needs a Hexaly licence file (license.dat): a paid licence, or a free trial or academic licence after registering on hexaly.com."
metadata:
  domain: constraint-programming
  solver: hexaly
  paradigm: cp
  interfaces: "python"
---

# Hexaly

Hexaly Optimizer models a problem as **decisions** (Booleans, integers, floats, lists, sets,
intervals) and **expressions** computed from them with any arithmetic, logical or
collection operator, linear or not. Local search finds solutions; bounds computed beside it
prove optimality. Two facts to keep in mind:

- A model must have **at least one objective**. A feasibility problem minimises a constant.
- A status is a claim to check. `OPTIMAL` is only proven exactly with a zero gap limit, and
  `INFEASIBLE` means "nothing found yet", not "no solution exists".

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `hexaly` (`import hexaly.optimizer`) |

Other bindings (C++, C#, Java, and the Hexaly Modeler language) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [Infeasibility](#infeasibility)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

Reference: [operators](https://www.hexaly.com/docs/last/mathematicaloperators/operatorsreference.html),
[modelling principles](https://www.hexaly.com/docs/last/modelingprinciples/modelingprinciples.html).

| Decision | Values |
|---|---|
| Boolean | 0 or 1 |
| integer | a closed range `[lo, hi]`; values are 64-bit |
| float | a closed real range |
| [list(n)](https://www.hexaly.com/docs/last/mathematicaloperators/collectionvariables.html) | an ordered selection of distinct values from `0..n-1`; with `count == n` it is a permutation |
| [set(n)](https://www.hexaly.com/docs/last/mathematicaloperators/collectionvariables.html) | an unordered subset of `0..n-1` |
| [interval(lo, hi)](https://www.hexaly.com/docs/last/mathematicaloperators/intervalvariables.html) | an integer interval `[start, end)` inside `[lo, hi)` |

Everything else is an expression: sums, products, minimum, maximum, absolute value,
comparisons, logical and, or and not, if-then-else, [element access](https://www.hexaly.com/docs/last/mathematicaloperators/atoperator.html)
(an array indexed by a decision, the element constraint), `count`, `contains`, `distinct`,
`partition`, `disjoint`, and [lambdas](https://www.hexaly.com/docs/last/mathematicaloperators/delegates.html)
over a range. A constraint is any Boolean expression posted as a constraint. The exact calls
are in the interface files.

There is no all-different constraint. Use pairwise `!=`, or `count(distinct(array)) == n`,
or a full list decision. Scheduling uses interval decisions: `a < b` between intervals means
`end(a) <= start(b)`, and a machine's tasks are ordered by a list decision (see the
scheduling example of each interface).

**The formulation decides what can be proven.** Hexaly finds good solutions on set-based
models, but its bounds come from the linear structure. Observed on a 4x4 assignment, 10
second limit, 4 threads: Boolean assignment variables with linear constraints, or integers
with pairwise `!=`, were proven optimal in 0.02 s; the same problem with
`count(distinct(...)) == n` or a list decision found the optimum (13) and stayed unproven
(bounds 10 and 4). Prefer Booleans, linear sums and pairwise constraints when the optimum
must be proven; keep lists and intervals for sequencing and scheduling.

**Arithmetic.** `/` is real division. Integer division `//` rounds down (-7 // 2 is -4), while
`%` keeps the sign of the dividend (-7 % 2 is -1), so `(a // b) * b + a % b == a` fails for a
negative `a`. `**` returns a float; write `x * x` for an integer square.

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement.

## Solving

[Statuses](https://www.hexaly.com/docs/last/pythonapi/optimizer/hxsolutionstatus.html):

| Status | Meaning |
|---|---|
| `OPTIMAL` | the objective reached its bound **within the gap limit** (default 1e-4, relative) |
| `FEASIBLE` | a solution that satisfies every constraint; optimality not proven, so report it as the best found, never as optimal |
| `INFEASIBLE` | no feasible solution found; **not** a proof that none exists |
| `INCONSISTENT` | proven: the model has no feasible solution |

**Set the gap limit to 0** when the exact optimum matters. Observed: a 40-item strongly
correlated knapsack reports `OPTIMAL` with value 12168772 and bound 12169975 under the
default gap; with the gap limit 0 the bound closes at 12168772.

**Use at least 4 threads.** Hexaly runs its search and its bounding in different threads.
Observed on the 6x6 job shop ft06 (optimum 55), one CPU, 30 s: with 1 or 2 threads the
bound stayed at 54; with 4 threads the optimum was proven in 0.4 s. The default (0,
automatic) creates at least 4.

The time limit is in whole seconds and is the only stopping rule besides the proof (and an
iteration limit). Without one, a model whose optimum cannot be proven runs indefinitely.

## Infeasibility

Hexaly proves infeasibility only when presolve or its bounds find it; search alone never
does. Observed (10 s, 1 or 4 threads): 3-queens and 6 pigeons in 5 holes stayed
`INFEASIBLE`. Presolve catches some cases and misses similar ones: AB + AB = AAA was
`INCONSISTENT` at once, CCEE + GGCB = DHACI stayed `INFEASIBLE` for 10 s.

To prove that no solution exists, move the constraints into the objective: minimise the
number (or amount) of violations. A proven minimum above 0 (`OPTIMAL`, gap limit 0) is the
proof. Each kind of constraint has its violation (the calls are in the interface files):

| Constraint | Violation to minimise |
|---|---|
| a Boolean condition | 1 when it is false, 0 when it holds |
| `a <= b` | the excess `a - b` when positive, else 0 |
| `a == b` | the absolute difference of `a` and `b` |

Keep hard the constraints that are easy to satisfy (one queen per row and column) and
soften the others. The same model also finds solutions: a minimum of 0 meets its trivial
bound, so a solvable instance ends `OPTIMAL` at once, and one soft solve answers whether a
solution exists. Observed: SEND + MORE = MONEY with the sum as an absolute difference was
`OPTIMAL` 0 in 0.01 s; CCEE + GGCB = DHACI was proven to miss by 1 in 0.4 s, where the hard
model had stayed `INFEASIBLE`; 3-queens with each diagonal's excess over 1 minimised was
proven to need one attack in 0.02 s. Solving the hard model first spends its whole time
limit on every instance presolve cannot settle. After an
`INCONSISTENT` status, [compute_inconsistency](https://www.hexaly.com/docs/last/modelingprinciples/inconsistency.html)
returns a minimal set of conflicting expressions.

## All solutions

Hexaly has no enumeration mode. Re-solve in a loop: read the solution, reopen the model,
exclude what was found, close it, solve again.

Exclude found solutions with **soft no-goods**: replace the objective by the number of
earlier solutions the decisions repeat (one `and` of equalities per solution) and minimise
it. Objective 0 is a new solution. A proven minimum of 1 or more (`OPTIMAL`, gap limit 0)
proves that no unseen solution exists. Hard no-goods (`or` of `!=`) also find new solutions,
but the last step ends `INFEASIBLE` at the time limit, without a proof: on 5 Booleans with
exactly 2 true, the 11th solve stayed `INFEASIBLE` until its 5 s limit, while the soft version
proved all 10 solutions in 0.15 s.

Write each no-good over the decisions that identify a solution, and as few as do. Solutions
differing only in auxiliary decisions are then not listed twice, and the final proof is
cheaper. The general form is the `and` of `x == value` over those decisions. When every
solution has the same number of true Booleans (one queen per row), the `and` of only the
Booleans that are true is enough: on n-queens it is 1 only for that placement. It is wrong
when one solution's true Booleans can include another's: a knapsack selection {1} would then
also exclude {0, 1}.

Most of the time goes into the final proof. 8-queens, all 92 solutions with soft no-goods,
4 threads on one CPU, a Boolean per square with linear row, column and diagonal sums: each
new solution took under 0.1 s, and the proof that none was left took the rest. It took 4
to 8 s in total with no-goods over the 8 queen squares, 31 s with no-goods over all 64
squares, and 33 to 48 s when each row's and column's constraints were posted together
instead of all rows first. An integer column per row with pairwise `!=` took 89 to 103 s.

The loop shows that a problem has **no** solution only when presolve proves it
(`INCONSISTENT`); otherwise its first solve ends `INFEASIBLE` at the time limit, which proves
nothing. Settle feasibility first with one solve of the violation model
([Infeasibility](#infeasibility)), and enumerate only when its minimum is 0.

All optimal solutions: solve with the objective and gap limit 0, check `OPTIMAL`, then
remove the objective, constrain the objective expression to equal the optimum, and enumerate
as above.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `At least one objective is required in the model` | no objective on a feasibility problem | minimise a constant: `minimize(0)` |
| `OPTIMAL` but a better solution exists | default gap limit 1e-4 | set the gap limit to 0 |
| `INFEASIBLE` and you need to know whether a solution exists | search found none, which proves nothing | minimise the violations ([Infeasibility](#infeasibility)) |
| `FEASIBLE` at the time limit, bound far from the objective | weak bound from set-based or `distinct` formulation, or fewer than 4 threads | Boolean or pairwise formulation ([Modelling](#modelling)); 4 threads |
| enumeration never ends with a proof | hard no-goods | soft no-goods ([All solutions](#all-solutions)) |
| enumeration ends with a long last solve | the proof that no solution is left: wide no-goods, an integer formulation | no-goods over the fewest decisions, a Boolean formulation with linear sums ([All solutions](#all-solutions)) |
| enumeration of a problem with no solution ends without a proof | the first solve is `INFEASIBLE` | prove infeasibility first by minimising violations |
| a negative remainder or quotient differs from your formula | `//` floors, `%` truncates | write the division with explicit decisions `q`, `r` and three constraints: `a == b * q + r`, `r >= 0`, `r <= b - 1` |
| licence error at the first optimizer | no `license.dat` where Hexaly looks | see the install section of the interface file |

Binding-specific issues are in the interface files.

## Further reading

- Documentation: https://www.hexaly.com/docs/last/
- Python API: https://www.hexaly.com/docs/last/pythonapi/index.html
- Operators: https://www.hexaly.com/docs/last/mathematicaloperators/operatorsreference.html
- Modelling principles: https://www.hexaly.com/docs/last/modelingprinciples/modelingprinciples.html
- Example tour (job shop and others): https://www.hexaly.com/docs/last/exampletour/index.html
- Licences and installation: https://www.hexaly.com/docs/last/installation/index.html
