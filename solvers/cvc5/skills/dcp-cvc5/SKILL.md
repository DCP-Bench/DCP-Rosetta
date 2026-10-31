---
name: dcp-cvc5
description: cvc5, an SMT solver used for finite-domain combinatorial models, from Python (pip package cvc5, module cvc5.pythonic, Z3-style). Covers integer and Boolean variables, Distinct, sums and cardinality, table, element, lexicographic, cumulative, no-overlap and routing encodings, satisfiability, enumeration and optimisation by tightening. Use when writing, debugging or explaining cvc5 models in Python, or when the user has chosen cvc5 for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Python 3.10+ and the cvc5 pip package (tested with cvc5 1.4.2 on Python 3.12, Linux x86-64; no NumPy needed). cvc5 is free with no key or size limit.
metadata:
  domain: constraint-programming
  solver: cvc5
  paradigm: smt
  interfaces: "python"
---

# cvc5

cvc5 is an SMT solver. Its Python API (`cvc5.pythonic`) builds integer, Boolean and array formulas
with the same operators as Z3. It has **no global constraints**: no cumulative, table,
element or circuit, and no `PbEq`, `AtMost` or `Max`. Encode them with `Distinct`, `If`,
`Or`, `And` and `Sum`. It has **no optimiser**: minimise or maximise by asking for a
better value until the solver answers `unsat`. Integers are unbounded unless you bound them.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `cvc5` on PyPI, module `cvc5.pythonic` (Z3-style) |

Other bindings (C++, Java, the SMT-LIB text format) are not covered yet.

## Contents
- [Pick an interface](#pick-an-interface)
- [Solving](#solving) · [All solutions](#all-solutions) · [Optimisation](#optimisation)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per language: [Python](interfaces/python/README.md); sources in [sources.md](sources.md)

## Solving

| Outcome | Meaning |
|---|---|
| sat | a model exists |
| unsat | proven: no model exists |
| unknown | undecided: a limit was hit, or the problem is nonlinear and beyond the solver; the solver gives a reason (for example a timeout) |

A time limit applies per check, not to a whole tightening or enumeration loop. Choose the
solver's logic to match the model (linear integer arithmetic is much faster than the default for
linear models; products of variables need a nonlinear logic). The option names, the
measurements behind them and how to read models are in the interface file.

## All solutions

No enumeration call exists. Loop over the check and block the assignment of the **decision**
variables only. An auxiliary variable in the no-good gives each solution once per value of
the auxiliary. Check that the last check returned `unsat`, not `unknown`, before reporting the
list as complete. Code and example: [Python](interfaces/python/README.md#all-solutions).

## Optimisation

cvc5 has no optimiser. Tighten: solve, record the value, add `objective > best` (or
`< best` for minimisation), solve again. The last `check()` returning `unsat` proves the
optimum. Returning `unknown` means the best value is only a bound. Examples:
[maximise-knapsack](assets/python/maximise-knapsack/README.md) and
[minimise-jobshop](assets/python/minimise-jobshop/README.md). For all optimal solutions, first find
the optimum, then add `objective == best` and enumerate as in [All solutions](#all-solutions).

## Common issues

Symptoms of the solver in every binding; error texts are in the interface file.

| Symptom | Likely cause | Fix |
|---|---|---|
| a bit-vector bound makes the model unsat with no error | `<=` on `BitVec` is signed, the constant's top bit is set | widen by one bit |
| `check()` returns `unknown`, `TIMEOUT` | hard search, or nonlinear terms | `QF_LIA` for linear models, redundant bounds, a stronger encoding, a larger `tlimit-per` |
| enumeration repeats a solution | auxiliary variable in the no-good | block only the decision variables |
| optimum not proven | the last `check()` returned `unknown`, not `unsat` | treat the value as a bound; raise `tlimit-per` or strengthen the model |
| `model()` gives 0 for a variable | the variable is not in the formula | create it in the formula, or ignore it |

## Further reading

- cvc5 options: <https://cvc5.github.io/docs/cvc5-1.4.2/options.html>
- cvc5 documentation: <https://cvc5.github.io/docs/cvc5-1.4.2/>
