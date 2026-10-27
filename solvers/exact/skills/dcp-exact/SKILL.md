---
name: dcp-exact
description: Exact, a pseudo-Boolean and integer linear solver with Python bindings (package exact, import exact, class Exact) that builds models from named integer and 0/1 variables, linear constraints, reification and multiplication. Use when writing, debugging or explaining an integer linear or pseudo-Boolean model with Exact, or when the user asks for Exact's Python API.
license: Apache-2.0
compatibility: Requires Python 3.12 (tested) and the exact package (pip install exact; precompiled for x86_64 Linux and Windows). The package is AGPL-3.0-only.
metadata:
  domain: constraint-programming
  solver: exact
  paradigm: pb
  interfaces: "python"
---

Exact is a pseudo-Boolean solver: it encodes integer variables as binaries internally, so
a wide integer domain is cheap, but **every constraint must be linear**. A model is built
by naming variables and adding constraints; there is no expression language, and nothing
is solved until you call a solve method.
## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `exact` (`import exact`, class `Exact`) |

Other bindings (the C++ library and the command-line tool) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

Variables and constraints are addressed by **name**. Constraints are linear sums of integer
variables with integer coefficients, bounded from one or both sides; implications and
equivalences with a 0/1 head variable (reification) and products of variables exist. Exact
has **no global constraints** (all-different, element, table, cumulative, no-overlap): build
them from 0/1 indicator variables or reification. Anything that talks about a variable
*taking a particular value* needs one 0/1 variable per value, linked to the integer variable.
Patterns and code: [interfaces/python/patterns.md](interfaces/python/patterns.md).

## Solving

Nothing is solved until a solve method is called. The result is a state:

| State | Meaning |
|---|---|
| `SAT` | a solution was found; with `toOptimum`, it is proven optimal |
| `UNSAT` | no solution exists (after exhaustion, too) |
| `TIMEOUT` | the limit stopped the search; not proven, and the value is meaningless |

Infeasibility is never an exception. There is **no time limit by default**: a hard model
runs until it finishes, so pass a limit when there is a budget and report a `TIMEOUT`
answer as not proven. Exact minimises internally: a maximised objective value comes back
negated. Exact calls and parameters: [interfaces/python/README.md](interfaces/python/README.md).

## All solutions

Enumerate by solving without optimising, then blocking the solution projected onto the
decision variables, so auxiliary variables are not counted twice; stop at `UNSAT`. All
optimal solutions: solve for the optimum, pin the real objective at that value with a
constraint, then enumerate over the decision variables.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Global constraint not found (`all_different`, `element`) | Exact has none | Build from indicators or reification ([Modelling](#modelling)) |
| Run never ends, or hits an external limit with no answer | no time limit by default | Set a limit; on `TIMEOUT` report "not proven" |
| Maximum shows as a negative number | Exact minimises internally | Negate the value for a maximisation |
| Enumeration gives duplicates | Enumerated over auxiliary variables | Block solutions over the decision variables only |

Binding-specific issues: [interfaces/python/README.md](interfaces/python/README.md#common-issues).

## Further reading

- Repository and README: <https://gitlab.com/nonfiction-software/exact>
- Input formats for the command line: <https://gitlab.com/nonfiction-software/exact/-/blob/main/InputFormats.md>
- Package: <https://pypi.org/project/exact/>
