---
name: dcp-swipl
description: SWI-Prolog CLP(FD), the finite-domain constraint solver in library(clpfd) of SWI-Prolog 9.x, for constraint satisfaction and optimisation in Prolog. Use when writing, debugging or explaining clpfd models, global constraints, labelling or optimisation in SWI-Prolog, or when the user has chosen SWI-Prolog for a puzzle, scheduling, assignment or counting problem.
license: Apache-2.0
compatibility: Requires SWI-Prolog 9.2 or later with its bundled library(clpfd) and library(time); tested with 9.2.9. Free and open source; no key or account.
metadata:
  domain: constraint-programming
  solver: SWI-Prolog CLP(FD)
  paradigm: clp
  interfaces: "prolog"
---

# SWI-Prolog CLP(FD)

Constraint logic programming over finite domains. Variables get domains, constraints are ordinary Prolog goals that propagate as they are posted, and `labeling/2` is the only search. Keep one rule in mind: **give every variable a finite domain before it is labelled, and list every variable whose value you need in the labelling.**

## Pick an interface

Read this file, then the interface file for your language. Other bindings of SWI-Prolog's CLP(FD) are not covered yet.

| | Prolog |
|---|---|
| Read | [interfaces/prolog.md](interfaces/prolog.md) |
| Package | `swipl` with the bundled `library(clpfd)` and `library(time)`; SWI-Prolog 9.2 or later |
| Global constraints | `all_distinct`, `element`, `global_cardinality`, `circuit`, `cumulative`, `serialized`, `automaton` and more, as goals |
| Optimisation | `labeling([min(Expr)], Vars)` or `labeling([max(Expr)], Vars)`; a bounded descent for an answer before the proof |
| All solutions | `findall/3` over `labeling/2` |
| Time limit | `call_with_time_limit/2`, raising `time_limit_exceeded` |

## Search and optimisation

`labeling/2` is the only search, so the labelling order is part of the model. A labelled optimum is proved before it is returned, so the first answer can take minutes on a hard model. For an answer you can report before the proof ends, use a bounded descent: each round posts a bound, finds one solution under it, records it and tightens the bound, on fresh variables each round. When the descent ends normally the last recorded value is optimal; when a time limit fires it is the best found, not proven. The code is in the interface file.

## All solutions

Enumerate by backtracking into the labelling and collect ground copies. All **optimal** solutions: find the optimum, post it as a constraint, then enumerate again. If the answer is only part of the labelled variables, several labellings can give the same answer, so remove the repeats.

## Scheduling

Use a disjunctive constraint (`serialized/2`) for a machine that runs one task at a time and a cumulative one (`cumulative/2`) when a resource holds several tasks at once; a makespan bound is `Mk #>= End` for every task end, and precedences are inequalities between starts and ends.
