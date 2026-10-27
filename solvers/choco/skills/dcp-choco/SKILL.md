---
name: dcp-choco
description: Choco, an open-source constraint programming solver with integer, Boolean and set variables, a large catalogue of global constraints (all different, cumulative, table, circuit, regular and more), reification and optimisation, used from Java (choco-solver) or Python (pychoco, no Java install needed). Use when writing, debugging or explaining Choco models in either language, or when the user has chosen Choco for a constraint or scheduling problem.
license: Apache-2.0
compatibility: "Java: a JDK (tested with Java 21; the examples use records, so JDK 16+), the choco-solver 6.0.1 jar-with-dependencies (Maven Central, BSD-3-Clause) and, for JSON input, Gson 2.11.0 (Apache-2.0). Python: Python 3.12 (tested) and pychoco (tested 0.2.1 and 0.4.0), no other packages. No key or size limits."
metadata:
  domain: constraint-programming
  solver: choco
  paradigm: cp
  interfaces: "java, python"
---

# Choco

Choco is a propagation-based constraint solver written in Java, with a large catalogue of global
constraints. A model object is the factory for every variable and constraint, and a constraint it
returns does nothing until it is **posted** (or reified on purpose); the few calls that post at once
are listed in the interface files. **Model with the globals.**
Choco's strength is its propagators: a decomposition into pairwise relations or reified sums
throws that away.

## Pick an interface

Read this file, then the one interface file for your language.

| | Java | Python |
|---|---|---|
| Read | [interfaces/java.md](interfaces/java.md) | [interfaces/python.md](interfaces/python.md) |
| Package | `org.choco-solver:choco-solver` jar | `pychoco` wheel; Choco compiled to a native library, no Java install needed |
| Global constraints | the full catalogue, camelCase (`allDifferent`, `subCircuit`) | nearly the same catalogue on `model`, snake_case (`all_different`, `sub_circuit`; `keySort` is `keysort`) |
| Search strategies | presets, custom variable and value selectors, combined strategies | presets only (`solver.set_min_dom_lb_search(...)` and the like) |
| Restarts and no-good recording | Luby or geometric restarts | not configurable |
| Lazy clause generation | `setLCG(true)`, not safe for every constraint | not available |
| Limit hit or proof? | `getSearchState()`: `TERMINATED` (proved) or `STOPPED` (limit) | no flag: a limit hit with nothing found looks like infeasibility |
| All solutions | a `while (solver.solve())` loop | `find_all_solutions()` |
| All optimal solutions | optimise, then enumerate with the cost fixed | `find_all_optimal_solutions()` |
| Solving a model again | `solver.reset()` (not under LCG) | build a new `Model` |

Use the language of the user's project. Without one, take Java when the problem needs search
control, a proof of optimality under a time limit, or LCG; take Python for a quick model.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [Java](interfaces/java.md), [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Modelling

Full catalogue: [Choco documentation](https://choco-solver.org/docs/). Find a global for each
sentence of the problem. The calls, with their exact arguments, are in the interface files; in
Python, `help(model.<name>)` shows a signature.

| The problem says | Choco constraint (Java name) |
|---|---|
| all different, all different except 0 | `allDifferent`, `allDifferentExcept0` |
| exactly k equal to v, how many take a value in a set | `count`, `among` |
| each value occurs a given number of times | `globalCardinality` |
| number of distinct values | `nValues`, `atMostNValues`, `atLeastNValues` |
| weighted sum, how many are true | `scalar`, `sum` |
| the i-th entry of a table or array | `element` |
| allowed or forbidden combinations | `table` |
| a pattern along a sequence (shifts, nonogram row) | `regular`, `costRegular` |
| a tour, an optional tour, a path, a forest | `circuit`, `subCircuit`, `path`, `tree` |
| tasks on a machine or a resource over time | `cumulative` over tasks |
| items into bins, knapsack | `binPacking`, `knapsack` |
| rectangles do not overlap | `diffN` |
| sorted copy, permutation and inverse, one-hot channelling | `sort`, `inverseChanneling`, `boolsIntChanneling` |
| symmetry of values or rows | `intValuePrecedeChain`, `lexChainLessEq`, `lexLessEq` |
| minimum, maximum | `min`, `max` |

**Argument order.** In both interfaces the integer `element` takes the value first and the index third
(`value = table[index]`), `min` and `max` take the result first, and `count` takes the value
first. A wrong order fails at best, and can also run and give wrong answers.

**Objective.** An objective is an integer **variable**, not an expression: post an equality from
the expression onto a fresh variable whose bounds hold every attainable value, taken from the data.
Never bound the objective with a value the model does not imply (an expected or remembered best):
that silently removes solutions, and the proof then covers the cut rather than the model.

**Readable models.** Open the program with a comment that states the problem, and start each
block of constraints with a comment in the words of the problem statement, not the Choco call.
Take every size (item count, days, the length of a list) from the input data.

## Solving

| Outcome | Meaning |
|---|---|
| solution, search finished | satisfiable; for an optimisation, the last solution is optimal |
| solution, limit hit | feasible; an optimisation's best is **not** proven optimal |
| no solution, search finished | proven infeasible |
| no solution, limit hit | unknown |

How to tell these apart differs per interface: see the interface table.

Choco's default search is a black-box strategy that is good on many models. When it is not:

- Branch on the few variables that decide the structure (pass only those to the strategy).
- Scheduling: branch on start times, smallest first. Routing: branch on successors, first-fail.
- On a timeout, switch the search style first (input order against dom/wdeg), then add implied
  constraints, such as a lower bound on the objective (total demand / capacity, rounded up).
  Implied constraints usually beat a change of heuristic.

## All solutions

Enumeration returns every distinct assignment of **every** variable in the model, auxiliary ones
included: a free `aux` in 0..5 beside `x` in 1..2 gives 12 solutions, and with `aux = x` it gives 2,
in both interfaces. Make each auxiliary a function of the outputs (tie it with a constraint), or
keep the solutions distinct on the outputs as the interface file shows. All optimal solutions are
every assignment that reaches the optimum, with the same rule for duplicates.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| A constraint has no effect | It was built but not posted | Post it, or reify it on purpose |
| Duplicate solutions in an enumeration | A free auxiliary variable | Make it a function of the outputs, or deduplicate on the outputs |
| Optimisation ignores the objective | The objective is an expression, not a variable | Post the expression onto a fresh variable and pass that |
| Wrong `element`, `min`, `max` or `count` result | Arguments in the wrong order | See *Argument order* |
| An optimum is reported after a time limit | The search stopped before the proof | Java: check the search state; Python has no flag, so a run that used its whole limit is not proven (see the interface table) |
| Slow, or no first solution | Weak propagation or branching | A global instead of a decomposition, implied constraints, another search ([Solving](#solving)) |

## Further reading

- Choco documentation (modelling, search strategies, solving): <https://choco-solver.org/docs/>
- Choco source and releases: <https://github.com/chocoteam/choco-solver>
- pychoco documentation: <https://pychoco.readthedocs.io/en/latest/>, source: <https://github.com/chocoteam/pychoco>
