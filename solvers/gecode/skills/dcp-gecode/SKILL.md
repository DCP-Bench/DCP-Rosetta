---
name: dcp-gecode
description: Gecode, a propagation-based constraint programming solver with a large library of global constraints, propagation levels and DFS/BAB search, used from C++ (gecode/int.hh, minimodel.hh, search.hh) with Space subclasses. Use when writing, debugging or explaining Gecode models in C++, choosing a global constraint or branching for one, or enumerating all (optimal) solutions with it.
license: Apache-2.0
compatibility: "C++: a C++17 compiler and Gecode 6.2 (Debian/Ubuntu libgecode-dev; tested with 6.2.0, g++ 12.2); nlohmann/json (nlohmann-json3-dev) to read JSON data. MIT-licensed, no key or size limits."
metadata:
  domain: constraint-programming
  solver: gecode
  paradigm: cp
  interfaces: "cpp"
---

# Gecode

Gecode is a propagation-based CP solver with a large library of global constraints.
A model is a `Space`: variables and constraints live in it, and search **copies** the
space, so everything the solution needs is carried through the copy. **Model with the
globals.** Gecode's strength is its propagators; a decomposition into pairwise `rel` or
reified sums throws that away.

## Pick an interface

Read this file, then the interface file for your language.

| | C++ |
|---|---|
| Read | [interfaces/cpp/README.md](interfaces/cpp/README.md) |
| Package | `libgecode-dev` (Gecode 6.2) with headers `gecode/int.hh`, `minimodel.hh`, `search.hh` |
| Global constraints | the full catalogue ([constraint map](interfaces/cpp/constraint-map.md)) |
| Search control | branching selectors, restarts (`RBS`), stop objects, LDSB symmetry breaking |
| All solutions / all optimal | `DFS` loop on `next()`; `BAB` for the optimum, then `DFS` with the cost fixed |

Other bindings (Gecode is also reachable through MiniZinc and language wrappers) are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [C++](interfaces/cpp/README.md); sources in [sources.md](sources.md)

## Modelling

Write the model clause by clause: for each sentence of the description find the global
that states it, and start each block with a comment in the description's words. Full list:
[Gecode integer constraints](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelInt.html);
the calls, with exact arguments, are in the interface files.

A decomposition is right only when no global fits. Two globals on the same variables are
fine (a `distinct` beside a `linear`); redundant globals often pay (`count` cards that
sum to n, a `cumulative` beside `nooverlap` on each axis). Use the strong propagation
level (`IPL_DOM`) for `distinct` on permutations and puzzles; keep the default on
arithmetic, where it can exhaust memory.

**Branch on every decision variable.** A solution is reported once every brancher is done;
an auxiliary that neither branching nor propagation fixes stays open.

## Solving

[Search engines](https://www.gecode.org/doc/6.2.0/reference/group__TaskSearch.html):
depth-first (satisfy, enumerate), branch-and-bound (optimise: each solution strictly better
than the last) and the restart-based variants of both. The engine searches a clone of the
root space.

| Outcome | Meaning |
|---|---|
| the root space fails before search | infeasible, proven by propagation alone |
| the engine returns a space | a solution (branch and bound: strictly better than the previous one) |
| the engine returns nothing, not stopped | search exhausted: no more solutions; for branch and bound the last solution is **optimal**, none at all means **infeasible** |
| the engine returns nothing, stopped | a time, node or fail limit fired: the last solution is feasible, not proven; none means unknown |

Gecode has no status enum: the outcome is read from these. The constants and option names
are in the interface file.

## All solutions

Depth-first search returns each solution once per assignment of the **branched** variables.
Branch only on the variables whose values define a solution, and make every auxiliary
functionally determined by them. **All optimal solutions**: prove the optimum with branch
and bound, then build a fresh space that constrains the cost to the optimum and enumerate
it depth-first. Branch and bound keeps requiring each solution to beat the last, so it
never yields a second solution of equal cost.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Garbage values or a crash after search; constraints silently ignored | A variable missing from the space's copy | Update every variable member in the copy |
| A "solution" violates a constraint, or reading a value fails as unassigned | An auxiliary no branching fixes | Branch on every decision variable, auxiliaries last |
| All-optimal run returns one solution | Branch and bound only reports strictly better solutions | Enumerate depth-first on a space with the cost fixed ([All solutions](#all-solutions)) |
| Search stopped on a small problem: unknown answer or incomplete list | A limit fired before the search ended | Change the search style or raise the limit (interface file) |
| Slow, or no first solution / optimum not proven | Weak propagation or branching | Implied constraints, branching order, restarts (interface file) |
| Float model slow or inexact | Floats are slow and inexact | Scale to integers |

More, with the exact calls: [C++ common issues](interfaces/cpp/README.md#common-issues).

## Further reading

- MPG (the guide, with Space, cloning, MiniModel, branching, search engines, LDSB): <https://www.gecode.org/doc-latest/MPG.pdf>
- API reference 6.2.0: <https://www.gecode.org/doc/6.2.0/reference/> ([Space](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1Space.html), [MiniModel](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModel.html), [branching](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntBranch.html))
- Examples shipped with Gecode: <https://github.com/Gecode/gecode/tree/release-6.2.0/examples> (`queens.cpp`, `money.cpp`, `golomb-ruler.cpp`, `job-shop.cpp`)
