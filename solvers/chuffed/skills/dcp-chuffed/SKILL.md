---
name: dcp-chuffed
description: Chuffed, a lazy clause generation constraint programming solver, used directly from C++ through its native API (Problem subclass, IntVar/BoolView, int_linear, all_different, cumulative, branch, optimize, engine.solve), built with CMake. Use when writing, building, debugging or explaining C++ programs that model with Chuffed, or when the user has chosen Chuffed's C++ API.
license: Apache-2.0
compatibility: "C++: a C++17 compiler, CMake 3.18+ and Chuffed built from source (tested with Chuffed 0.14.0, g++ 12.2, CMake 3.25, Debian 12); MIT licence, no key or size limit. The JSON example also needs nlohmann/json."
metadata:
  domain: constraint-programming
  solver: chuffed
  paradigm: cp
  interfaces: "cpp"
---

# Chuffed

Chuffed is a CP solver with lazy clause generation: propagators explain their inferences
as clauses, so it learns from failures like a SAT solver. Variables are integers with
bounds, or Booleans; the model is a set of constraints, mostly global ones, plus a search
specification and at most one objective.

## Pick an interface

Read this file, then the interface file for your language.

| | C++ |
|---|---|
| Read | [interfaces/cpp/README.md](interfaces/cpp/README.md) |
| Package | Chuffed built from source with CMake (no package for the C++ library), native API |
| Expressions | none: every intermediate value is its own variable with a defining constraint |
| Solving again | one solve per process |

Other bindings (the MiniZinc `fzn-chuffed` front end) are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Hard instances](#hard-instances) · [Further reading](#further-reading)
- Per language: [C++](interfaces/cpp/README.md); sources in [sources.md](sources.md)

## Modelling

Variables need finite bounds (within +-500,000,000, sums within 32-bit `int`); a Boolean
and a 0..1 integer are separate kinds of variable, tied by an explicit link constraint
(see the binding file). Prefer the global constraints (all different, element,
table, regular, circuit, inverse, lex, disjunctive, cumulative) over decompositions, and one
linear constraint over hand-built sums. Reification exists for linear and binary relations
only; a global has no reified form. An objective is a single integer variable.
Keep the domain of every auxiliary variable wide enough for every value it can take, or the
model turns infeasible. Tight domains from the data help search.

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement, not the API
call. Test on a second data set.

## Solving

| Outcome | Meaning |
|---|---|
| search complete (optimisation) | the last solution found is optimal |
| search complete (satisfaction) | all solutions were found; none means infeasible |
| stopped at the requested number of solutions | more may exist |
| time out | an optimisation's last solution is only the best found |
| failure at the root | detected while posting the model, before search; Chuffed reports it on its own output |

Search is declared on the decision variables (variable choice, value choice); variables no
branching reaches stay unfixed. How an outcome is read is in the interface file.

## All solutions

Enumeration is over the declared output variables: solutions are distinct on those, and
without them search ends after the first solution. **All optimal solutions** need two solves:
optimise, then solve again with the objective fixed to the optimum and no objective.

## Hard instances

Branch first on the structural decisions everything else follows from; try a smallest-domain or
activity-based variable choice when input order stalls; derive tight domains and objective
bounds from the data; turn on restarts for heavy-tailed search. Measured cases and the
reasoning behind each: [C++ performance notes](references/cpp/performance.md).

## Further reading

- Source, README and build notes: <https://github.com/chuffed/chuffed>
- Headers (the API reference): <https://github.com/chuffed/chuffed/tree/0.14.0/chuffed> (`primitives/`, `globals/`, `vars/`, `branching/`, `core/`)
- Official C++ examples: <https://github.com/chuffed/chuffed/tree/0.14.0/chuffed/examples> (`queens.cpp`, `golomb.cpp`, `rcpsp.cpp`, `shift.cpp`)
