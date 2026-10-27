---
name: dcp-paramita
description: Paramita SAT and MaxSAT framework, used from Python (paramita 1.2.0) - Bool variables, propositional operators and pseudo-Boolean constraints from paramita.modelling, integers encoded as Booleans, satisfiability and all-solutions enumeration with CaDiCaL, and optimisation as MaxSAT with EvalMaxSAT2022. Use when writing, debugging or explaining Paramita models, or when the user has chosen Paramita for a SAT, MaxSAT or pseudo-Boolean problem.
license: Apache-2.0
compatibility: Requires Python 3.12 (tested) and paramita 1.2.0 with the Cadical300 and EvalMaxSAT2022 plugins built from paramita-plugins (CMake and a C++ compiler). No licence key, no size limit.
metadata:
  domain: constraint-programming
  solver: paramita
  paradigm: sat
  interfaces: "python"
---

# Paramita (Python)

# Paramita

Paramita is a SAT and MaxSAT framework. A model is propositional: `Bool` variables,
logical operators and pseudo-Boolean (PB) constraints `Σ wᵢ·bᵢ ⋈ k`. There are no
integer or finite-domain variables: an integer is a sum of Bools, so the modelling
work is choosing the encoding. Each expression is turned into clauses (PB encoder
`BestEncoder` by default). Satisfiable problems go to CaDiCaL; optimisation
goes to EvalMaxSAT as a weighted problem.

## Pick an interface

Read this file, then the interface file for your language.

| | Python |
|---|---|
| Read | [interfaces/python.md](interfaces/python.md) |
| Package | `paramita` wheel plus the solver plugins built from `paramita-plugins` (CMake and a C++ compiler) |

Other bindings (the docs describe a C++ core) are not covered yet.

## Modelling

Full reference: [Paramita documentation](https://ulog.udl.cat/static/doc/paramita/). Booleans, `And`/`Or`/`If`/`Iff`
and PB sums are the whole vocabulary; integers, all-different, element, table, no-overlap
and similar constraints are encoded over Booleans (one-hot, unary, binary). Exact calls
and expressions are in the interface file.

## Solving

- **Satisfaction**: a solve returns a model, proven unsatisfiable, or unknown when a conflict budget ran out.
- **All solutions**: after each model add a clause that differs from it in at least one
  answer Boolean, and solve again; unsatisfiable means the list is complete. Block only the answer
  variables: auxiliary variables make duplicates of the same answer.
- **Optimisation (MaxSAT)** maximises a linear objective; to minimise, negate it. Only an `OPTIMAL` status is a proven result.
- **All optimal solutions**: solve for the optimum, then fix the objective to it as a hard constraint on a fresh solver and enumerate.
- **Time limits**: CaDiCaL accepts only a conflict budget; EvalMaxSAT accepts none, so run it in a child process and kill it at the deadline.
- **Recursion**: the default PB encoder recurses once per term. A single sum of about 5000
  Bools segfaults on the default 8 MB stack (2000 was fine); use a larger stack or split the sum.

The code for each is in the interface file.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `TypeError` on a coefficient | outside the 32-bit range | scale the data, or split the sum |
| A sum wraps and the answer is wrong | a constraint or objective value beyond 32 bits | scale down or split; read big numbers from the model bits in Python |
| Segmentation fault on a wide sum | the recursive PB encoder overflows the stack | `ulimit -s unlimited`, or split the sum |
| EvalMaxSAT proof takes minutes on a scheduling-sized model (a 6x6 job shop took about 3 minutes to prove optimal) | MaxSAT has no budget, and a large horizon with many unary bits makes the proof long | tighten the horizon to a feasible makespan upper bound, use the unary makespan from [modelling.md](references/python/modelling.md#precedence-and-makespan), run in a child process with a deadline, and treat anything not `OPTIMAL` as unresolved |
| EvalMaxSAT run never returns | no budget exists for it | run it in a child process and kill at the deadline |
| Enumeration returns duplicates | blocking clauses cover auxiliary variables | block only the answer Booleans |

Binding-specific problems are in the interface file.

## Further reading

- Paramita 1.2.0 documentation (tutorials, Python API reference): <https://ulog.udl.cat/static/doc/paramita/>
- Plugin sources, pinned commit: <https://codeberg.org/paramita/paramita-plugins>
