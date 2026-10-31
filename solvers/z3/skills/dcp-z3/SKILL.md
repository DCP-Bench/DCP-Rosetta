---
name: dcp-z3
description: Z3, an SMT solver with a Python API (pip package z3-solver, import z3) for integer, Boolean and array constraints, satisfiability checks, optimisation and solution enumeration. Use when writing, debugging or explaining Z3 models in Python, or when the user has chosen Z3 for a constraint or scheduling problem.
license: Apache-2.0
compatibility: "Python: Python 3 and pip, and the z3-solver package (tested with package 5.1.0.0, which reports Z3 core version 5.1.0, on Python 3.12; Z3 itself is MIT-licensed, no key or size limit)"
metadata:
  domain: constraint-programming
  solver: z3
  paradigm: smt
  interfaces: "python"
---

# Z3

Z3 is an SMT solver: it decides satisfiability of logical formulas over integers, reals,
Booleans and arrays. It has **no global constraints** (no all-different, element,
cumulative or table as built-ins), so encode them with `Distinct`, `If`, `Select` and
linear arithmetic. Integers are unbounded unless you bound them.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `z3-solver` wheel (`import z3`) |

Other bindings (the Z3 docs cover C, C++, Java, .NET, JavaScript and OCaml) are not covered yet.

## Contents
- [Solving](#solving) · [All solutions](#all-solutions) · [Further reading](#further-reading)
- Per language: [Python](interfaces/python.md); sources in [sources.md](sources.md)

## Solving

| Result of a check | Meaning |
|---|---|
| sat | a model exists |
| unsat | proven: no model exists |
| unknown | undecided, with a reason such as a timeout |

The optimum of an optimisation is proven when the best value found and the proven bound are the
same finite number; an unbounded objective has an infinite bound. The calls are in the interface files.

## All solutions

Z3 has no enumeration call: loop over `check()` and block each assignment of the
**decision** variables. Auxiliary variables (intermediate sums, makespans) must stay out
of the blocking clause, or each solution appears once per auxiliary value.
Exact calls: the interface file.

## Further reading

- Z3 guide, logic: <https://microsoft.github.io/z3guide/docs/logic/intro/>
- Z3 guide, optimisation: <https://microsoft.github.io/z3guide/docs/optimization/intro/>
- Z3 guide, arithmetic theory: <https://microsoft.github.io/z3guide/docs/theories/Arithmetic/>
- Python API reference (all functions): <https://z3prover.github.io/api/html/namespacez3py.html>
- Source and examples: <https://github.com/Z3Prover/z3> (`examples/python`)
