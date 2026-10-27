---
name: dcp-pysat
description: PySAT (python-sat), a Python library for SAT and MaxSAT modelling with CNF and WCNF formulas, cardinality and pseudo-Boolean encoders, finite-domain integers (pysat.integer), SAT solvers such as Glucose, and the RC2 MaxSAT solver. Use when writing, debugging or explaining SAT, MaxSAT or pseudo-Boolean models in Python with pysat, or when a puzzle or optimisation problem should be modelled with pysat.
license: Apache-2.0
compatibility: Python - requires Python 3.10+ and python-sat with the pblib extra (pip install "python-sat[pblib]"); python-sat is MIT-licensed and free. Building pypblib from source needs a C++ compiler.
metadata:
  domain: constraint-programming
  solver: pysat (glucose42, RC2)
  paradigm: sat
  interfaces: "python"
---

# PySAT

PySAT is a Python toolkit for SAT and MaxSAT. You build a formula from clauses: a `CNF` for constraints, or a `WCNF` whose weighted soft clauses are the objective. Encoders turn cardinality, pseudo-Boolean and finite-domain integer constraints into clauses. A SAT solver or RC2 then searches. Every modelling choice is therefore an encoding choice.

The one idea to keep: **the objective is soft clauses.** Hard clauses are the constraints. RC2 finds a model that satisfies every hard clause and minimises the total weight of the soft clauses it falsifies.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `python-sat` (import `pysat`), with the `pblib` extra for pseudo-Boolean encodings |

Other bindings are not covered yet.

## Contents
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- Per language: [Python](interfaces/python/README.md); sources in [sources.md](sources.md)

## Solving

| Outcome | Meaning |
|---|---|
| satisfiable | a model is returned |
| unsatisfiable | the hard clauses have no model |
| optimal (MaxSAT) | a model with the minimum falsified soft weight, proven |
| interrupted | a time limit or interrupt stopped the search: nothing is proven |

The calls and return values are in the interface file.

## All solutions

Block exactly the variables the answer is made of. Auxiliary variables may differ between two models of the same answer, so they must not be blocked.

**All optimal solutions:** solve to the optimum, keep each model while the cost equals the first cost, block it, and stop at the first higher cost.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| Enumeration reports duplicate answers | Blocking clauses include auxiliary variables | Block only the variables the answer is made of |
| Optimal enumeration includes worse answers | Loop does not stop at the first higher cost | Stop when `rc2.cost` exceeds the optimum |

Binding-specific issues: [Python](interfaces/python/README.md#common-issues).
