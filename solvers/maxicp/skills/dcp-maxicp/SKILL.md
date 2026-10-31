---
name: dcp-maxicp
description: MaxiCP, a constraint programming solver from UCLouvain with integer and Boolean variables, global constraints, interval variables for scheduling, depth-first search, optimisation and solution enumeration, used from Java (org.maxicp:maxicp) through its raw API. Use when writing, debugging or explaining MaxiCP models, or when the user has chosen MaxiCP for a constraint or scheduling problem.
license: Apache-2.0
compatibility: "Java: a JDK 21 (MaxiCP classes are compiled for release 21; tested with Eclipse Temurin 21), the MaxiCP 0.0.3 jar (MIT, Maven Central) and, for JSON input, Gson 2.11.0 (Apache-2.0). No key, account or size limits."
metadata:
  domain: constraint-programming
  solver: maxicp
  paradigm: cp
  interfaces: "java"
---

# MaxiCP

MaxiCP is a CP solver: constraints are posted on a solver object, which propagates them to shrink variable
domains, and a depth-first search branches over variables until every one is fixed. **MaxiCP has no default
search and no default time limit.** The search does only what the branching function and the limit
predicate say. This skill covers the raw API (`org.maxicp.cp.CPFactory`, `CPSolver`, `DFSearch`); the
symbolic modelling layer (`org.maxicp.modeling`, `ModelDispatcher`) is a different API.

## Pick an interface

Read this file, then the interface file for your language.

| | Java |
|---|---|
| Read | [interfaces/java/README.md](interfaces/java/README.md) |
| Package | `org.maxicp:maxicp` 0.0.3 jar (Maven Central), raw API |

Other bindings are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Java: [README](interfaces/java/README.md), [modelling](interfaces/java/modelling.md), [issues](interfaces/java/issues.md); sources in [sources.md](sources.md)

## Modelling

Variables are integer (a domain `lo..hi`), Boolean (0..1) or interval (a task with a start, an end and a
length). Constraints include all-different, linear sums, element, table, circuit, reification and logic, and
for scheduling no-overlap, cumulative resources and makespan. The calls with their exact arguments are in
[the Java modelling page](interfaces/java/modelling.md). A variable is fixed by the search only if the
branching covers it, and a view (a sum, a product, a maximum) follows the variables it is built from.

**Readable models.** Open the program with a comment that states the problem, and start each block of
constraints with a comment in the words of the problem statement, not the API call.

## Solving

| Result | Meaning |
|---|---|
| solutions > 0, completed | every solution was enumerated |
| solutions = 0, completed | no solution (infeasible) |
| completed = false | the limit predicate stopped the search; nothing is known about the rest |

There is no time limit unless a predicate is passed, and values must be read when a solution is found,
because the state is restored when the search returns. Details and names:
[the Java interface](interfaces/java/README.md#solving).

## All solutions

Every solution is reported once per assignment of every branched variable, so auxiliary variables multiply
the solutions: fix each auxiliary through a constraint, or forbid each reported assignment with a no-good and
search again. All optimal solutions: optimise, post `(objective) = optimum`, then enumerate over the
reported variables. Code: [the Java interface](interfaces/java/README.md#all-solutions).

## Common issues

Symptom to fix, with each binding's list: [Java](interfaces/java/issues.md). Two apply everywhere: a
`firstFailNary`-style heuristic bug in 0.0.3 means to branch with `firstFailBinary`, and a non-completed search
proves nothing.

## Further reading

- Source and examples at tag `v0.0.3`: [repository](https://github.com/aia-uclouvain/maxicp/tree/v0.0.3).
- User guide, search strategies and scheduling chapters: [maxicp.org](http://www.maxicp.org).
- API Javadoc: [javadoc.io](https://javadoc.io/doc/org.maxicp/maxicp/latest/org.maxicp/module-summary.html).
