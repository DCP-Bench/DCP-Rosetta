---
name: dcp-jacop
description: JaCoP, a constraint programming (CP) solver over finite integer domains, used from Java (org.jacop:jacop; packages org.jacop.core, .constraints, .search). Use when writing, debugging or explaining JaCoP models - scheduling, assignment, puzzles, optimisation with global constraints - or when the user has chosen JaCoP.
license: Apache-2.0
compatibility: "Java: a JDK 16+ (the examples use records; Java 21 tested) and the org.jacop:jacop 4.10.0 jar (AGPL-3.0, no licence key); examples read JSON with org.json"
metadata:
  domain: constraint-programming
  solver: jacop
  paradigm: cp
  interfaces: "java"
---

# JaCoP

JaCoP is a finite-domain CP solver used as a plain Java library. A model is a
`Store` holding `IntVar`s, constraints are objects passed to `store.impose(...)`,
and solving is a separate **search** object you configure: which variables to
label, in which order, with which values. The one idea to keep in mind: *JaCoP
only reports a solution once every variable you gave the search is fixed*, so the
variables you label decide both what a solution is and how many duplicates you see.

## Pick an interface

Read this file and the interface file below.

| | Java |
|---|---|
| Read | [interfaces/java.md](interfaces/java.md) |
| Package | `org.jacop:jacop` 4.10.0 (Maven Central) |

JaCoP's own API is Java. Other front ends (the Scala DSL, the FlatZinc front end) are not
covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

Constraint list and exact calls: [interfaces/java.md](interfaces/java.md#modelling).

Variables are integer variables over finite domains; a Boolean is an integer variable in
0..1. JaCoP has weighted sums, max/min, all different, element, table, cumulative,
non-overlapping rectangles, circuit, count and global cardinality, and decomposed
constraints (sliding window, stretch, among, regular). Element and circuit are
**1-based**. Reification, implication and logical connectives take only primitive
constraints: comparisons, sums, multiplication by a constant and absolute value. A product
of two variables, division, modulo, max/min and the global constraints are not primitive:
to reify one, reify its decomposition. Domain bounds stop at `IntDomain.MaxInt` =
536870909, not 2^31-1.

## Solving

| Outcome | Meaning |
|---|---|
| solution found, search not stopped | a solution; with a cost, **proven optimal** |
| solution found, time limit hit | (cost only) best solution so far, **not** proven optimal |
| nothing found, search not stopped | proven infeasible |
| nothing found, time limit hit | unknown |

The search does depth-first branch and bound and always **minimises** the cost; maximise by
minimising the negation. The exact calls and flags are in
[interfaces/java.md](interfaces/java.md#solving).

- **Search order and value choice decide many models.** Selecting over every
  variable in input order, or smallest-domain over auxiliary 0/1 helpers, can fail
  where an explicit order succeeds. Label the decision variables first and the helper
  Booleans last; for a minimisation over Boolean flips label the smaller group first;
  for a 0/1 matrix try column-major order with the largest value first. Test two or three
  orders on the hardest data you have before concluding the model is too weak.
- **No restarts, no dom/wdeg.** For a hard satisfaction instance a static order after
  ranking values by difficulty, or smallest domain with random value choice, worked where
  the defaults did not. Cheap wins before any of that: implied sums and prefix bounds,
  equalities where the problem says exactly, a table over an enumerated pattern space
  (build the tuples in code; tens of thousands are fine), and symmetry breaking only
  where the problem allows it.
- **Prefer a deterministic order to random value choice.** Random value choice without
  restarts solved a hard puzzle one run in three. Labelling the counters one group at a
  time, so each new group closes constraints against groups already fixed, was reliable.
- **Check the first solution, not a later one.** A model can emit a wrong first solution
  and a right second one when a constraint loses propagation.
- **Which variables to label**: label every variable whose value you read, plus
  any auxiliary that propagation does not fix once those are fixed. When unsure,
  label all of them (decisions first) and de-duplicate, as below.
- **Errors**: JaCoP reports nothing for an inconsistent model; the search just reports
  no solution. Bad arguments throw exceptions. A store that is inconsistent before
  search means infeasible already.

## All solutions

Every distinct assignment of the **labelled** variables counts, so labelling an
auxiliary that is not fixed by your outputs yields duplicates. Either label only
output variables that fix everything else, or keep a set of output tuples and print
each new one only.

**All optimal solutions**: optimise, read the optimum, then build the model again
in a fresh `Store`, fix the objective to the optimum and enumerate. Write the model in a
method so it can be built twice. Code: [interfaces/java.md](interfaces/java.md#all-solutions).

## Common issues

Solver-level problems; those of the Java API are in [interfaces/java.md](interfaces/java.md#common-issues).

| Problem | Likely cause | Fix |
|---|---|---|
| element or circuit off by one | element and circuit are 1-based | give element an offset of `-1`; map circuit values with `- 1` |
| a wrong second solution when enumerating, or a `NullPointerException` on a large set | `Alldistinct` in 4.10.0 | use `Alldifferent`, or pairwise `XneqY` |
| a wrong first solution with `Count` | the counter is a member of the counted list: unsound | keep the counter out of the list, or use `GCC` |
| more solutions than expected, repeats in output | auxiliary variables labelled | de-duplicate on output tuples ([All solutions](#all-solutions)) |
| optimum reported after a timeout | only the found flag was checked | also require that the time limit was not hit ([Solving](#solving)) |
| maximisation returns the minimum | the search always minimises | label with the negated objective |
| second search on the same `Store` gives stale or wrong results | the first solution stays assigned in the store, and constraints added afterwards are not reliably kept | build a fresh `Store` for every search |
| a constraint seems ignored; a wrong value is accepted | the constraint was built, not imposed | impose every constraint on the store |
| `... durations must be greater than 0 violated` from `Cumulative` | a zero duration or resource need | drop those tasks from the constraint |
| `... not in the allowed range` on a large constant | `IntDomain.MaxInt` is 536870909, not 2^31-1 | split a big product into two halves and join them with a table over (x, target/x) |
| `GCC failure : join domain of x variables doesn't cover all count variables` | `GCC` counts the values 0, 1, 2, ... in order, and a counter's value is one no `x` variable can take | shift the variables so they start at 0 and use one counter per shifted value |
| an invalid first solution with overlapping or inconsistent items, and no error | an auxiliary placement Boolean was left outside the search, so channelling from coordinates did not fix it | put the Booleans that define the model in the labelled array, not only the coordinates derived from them |
| a conditional step such as `x - 3 = y` fails on every branch | an unconditional constraint holds on all branches | reify the selector and imply the step from it |
| a product-of-sums objective, or squares via products, never proves the optimum | weak propagation | use Boolean membership with linear sums, or a table, where possible |
| a printed value is wrong although the search succeeded | that variable was not in the search and is still unfixed: its value is then silently a domain bound | add it to the labelled array; check that it is fixed |

## Further reading

- API reference: [javadoc.io/doc/org.jacop/jacop](https://javadoc.io/doc/org.jacop/jacop/4.10.0/index.html)
- User's guide (PDF): [guideJaCoP.pdf](https://github.com/radsz/jacop/blob/develop/doc/jacopguide/guideJaCoP.pdf)
- Source and build notes: [github.com/radsz/jacop](https://github.com/radsz/jacop)
