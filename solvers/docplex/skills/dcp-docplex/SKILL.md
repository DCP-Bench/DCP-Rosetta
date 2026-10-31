---
name: dcp-docplex
description: DOcplex (docplex.mp), the Python modelling API of IBM CPLEX, for mixed-integer linear models with integer, binary and continuous variables, linear, indicator and logical constraints, optimisation and enumeration of solutions. Use when writing, debugging or explaining a model with docplex or CPLEX in Python, or when a problem such as assignment, scheduling, packing or selection should be modelled with docplex.
license: Apache-2.0
compatibility: Python 3 with the docplex and cplex packages (tested with docplex 2.32.264, cplex 22.2.0.1, Python 3.12). The pip cplex package is the CPLEX Community Edition, limited to 1000 variables and 1000 constraints per model; no key or network is needed
metadata:
  domain: constraint-programming
  solver: CPLEX
  paradigm: mip
  interfaces: "python"
---

# DOcplex (CPLEX)

DOcplex is the modelling API of IBM CPLEX. You build a `docplex.mp` `Model` from
variables and constraints, then `solve()` hands it to CPLEX, which proves optimality for
mixed-integer programs. The one idea to keep: the model must be **linear**. A product of two
variables, a division or a remainder of a variable is refused by CPLEX or by Python, and
[encodings](references/python/encodings.md) show the linear forms that do the same job.

This skill covers the `docplex.mp` modelling API. It does not cover the native `cplex` Python
API, the C++ or Java APIs, or CP Optimizer (`docplex.cp`).

## Pick an interface

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `docplex` with the `cplex` wheel (Community Edition) |

Other bindings (the native `cplex` API, C++, Java) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Per language: [Python](interfaces/python/README.md); sources in [sources.md](sources.md)

## Modelling

Variables are integer, binary or continuous; constraints are linear (in)equalities, plus
indicator, equivalence, if-then and logical helpers that CPLEX linearises, and an objective to
minimise or maximise. The calls are in the interface file; patterns a table does not show
(all-different, element, counting, binary times integer, division, disjunctions) are in
[encodings](references/python/encodings.md). Each helper adds variables and constraints of its
own, which count against the Community Edition limit ([cost table](interfaces/python/speed.md)).

## Solving

| Outcome | Meaning |
|---|---|
| proven optimal | also reported for a feasible model with no objective |
| optimal within the gap | stopped at the relative gap (default 1e-4): not exact; set the gap to 0 |
| time limit, with a solution | not proven optimal |
| time limit, no solution | nothing found |
| infeasible | proven: no solution |
| unbounded | the objective is unbounded |
| infeasible or unbounded | presolve could not tell which; turn presolve off and solve again |

Accept a result as an answer only when it is proven optimal; any other outcome may be a guess.
The exact status strings, codes and parameter names are in the interface file.

## All solutions

CPLEX has no call that lists every solution, but a solution pool can be filled, and a loop of
no-good cuts (solve, forbid that assignment, repeat) works without any pool settings. Both
are complete for integer and binary decision variables. Auxiliary variables multiply solutions:
enumerate over decision variables and drop duplicates. For all optimal solutions, solve for the
optimum, fix the objective to it, then enumerate. The loop is slow for many solutions, so
prefer the pool for more than a few dozen. Calls: [interface file](interfaces/python/README.md#all-solutions).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| refusal citing a non-convex quadratic constraint | product of two variables | a binary times a bounded integer has a linear form in [encodings](references/python/encodings.md) |
| limit error, `CPLEX code=1016` | Community Edition limit of 1000 variables or constraints | reduce the formulation; enumeration adds rows of its own |

More, by symptom, in [the interface file](interfaces/python/README.md#common-issues).

## Further reading

- Documentation for agents: no `llms.txt` is published (checked: 404); start from the API reference.
- API reference: [`Model`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html), [`Solution`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.solution.html)
- Modelling guide: [docplex.mp index](https://ibmdecisionoptimization.github.io/docplex-doc/mp/index.html)
- Examples: [docplex-examples `examples/mp`](https://github.com/IBMDecisionOptimization/docplex-examples/tree/master/examples/mp)
