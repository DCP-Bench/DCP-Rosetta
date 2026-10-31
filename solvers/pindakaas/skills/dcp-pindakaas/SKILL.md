---
name: dcp-pindakaas
description: Pindakaas, a library that encodes Boolean and integer constraints (clauses, propositional formulas, linear, pseudo-Boolean and cardinality constraints, integer variables) into CNF and solves them with the bundled CaDiCaL SAT solver, used from Rust (crate pindakaas 0.6.0). Use when writing, debugging or explaining a SAT or pseudo-Boolean model with Pindakaas, when a constraint has to be hand-encoded to clauses, or when the user has chosen Pindakaas.
license: Apache-2.0
compatibility: "Rust: Rust with cargo (tested with Rust 1.98.1), pindakaas 0.6.0 from crates.io (MPL-2.0), and a C++ compiler (g++) on PATH, because the crate builds the CaDiCaL SAT solver. Needs network access, or a vendored copy of the crates."
metadata:
  domain: sat
  solver: cadical
  paradigm: sat
  interfaces: "rust"
---

# Pindakaas

Pindakaas is a library of CNF encodings with a SAT solver attached. You create literals and
integer variables on a solver, encode constraints into it, and solve. It has **no optimiser,
no enumeration and no global constraints** (no all-different, element, table, min/max,
multiplication, reification): those are clauses and linear constraints that you write. Three
rules matter most. **Every encoding call returns a `Result`**: propagate it with `?`.
**`encode_implied` over integer terms narrows the variables for good** and gives wrong
answers: use the safe form in the interface file. **An integer variable has to have a view
before you read it** or `value()` returns the domain minimum.

## Pick an interface

Read this file and the interface file below.

| | Rust |
|---|---|
| Read | [interfaces/rust.md](interfaces/rust.md) |
| Package | `pindakaas` crate 0.6.0 (crates.io); builds CaDiCaL, so it needs a C++ compiler |

Pindakaas's own API is Rust. Other bindings are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

Constraint list and exact calls: [interfaces/rust.md](interfaces/rust.md#modelling).

Variables are Boolean literals and integer variables over a range or a set of values.
Constraints are clauses, propositional formulas (Tseitin-encoded) and linear constraints over
literals and integers; a linear constraint over literals is a cardinality or pseudo-Boolean
constraint. Every global constraint (all-different, count, element, table, min/max,
multiplication, modulo, absolute value) is a decomposition into these, built from the
integer variables' order literals (`x >= v`) and equality literals (`x = v`).

**Conditions over integers.** A condition on a linear constraint over integer terms must
not be encoded with the library's implied-constraint call: that narrows the variables for
good. Define the expression as a fresh integer variable and put only that variable's
literals behind the condition ([interfaces/rust.md](interfaces/rust.md#implication-and-reification-over-integers)).

**Wide domains.** Every linear constraint over an integer variable lists the values of its
domain, whichever encoder is used, so memory grows with the range. Give a variable that
takes few values a sparse domain, and hold a wide value as bits summed with the adder
encoder ([interfaces/rust.md](interfaces/rust.md#wide-integers-and-sparse-domains)).

## Solving

| Outcome | Meaning |
|---|---|
| satisfied | a solution; read the values before touching the solver again |
| unsatisfiable | proven no solution (also an error from an encoding call: the clauses already contradict) |
| unknown | the search was interrupted, for example by a deadline |

- **Optimise:** there is no optimiser. Define the objective as an integer variable and
  search linearly: solve under the assumption that the objective is better than the best
  so far, until that is unsatisfiable or no better value is left in the domain.
- **Deadline:** a terminate callback stops the search within about a millisecond, and the
  solve then reports unknown. **Encoding is not interruptible**: one large cardinality or
  pseudo-Boolean encoding can run for seconds past any deadline.
- **Reading values:** give every integer you will read at least one view before the first
  solve.
- **Encoders:** the default picks MixedRadix for integer sums, Totalizer for pseudo-Boolean,
  cardinality and count constraints, and Product for at-most-one. On one weighted knapsack the
  decision diagram encoder solved in 0.75 s where the default Totalizer timed out, so try
  another when a weighted constraint is the bottleneck.

## All solutions

There is no enumeration call. After each solution add a blocking clause over the variables
you care about (the negation of their current values) and solve again, until the clause
cannot be added or the solve is unsatisfiable. Projecting on a subset of variables gives
distinct rows on that subset. Code: [interfaces/rust.md](interfaces/rust.md#solving).

## Common issues

Solver-level problems; those of the Rust API are in [interfaces/rust.md](interfaces/rust.md#common-issues).

| Symptom | Cause and fix |
|---|---|
| Wrong answers or lost solutions behind a condition | the implied-constraint call over integer terms narrows the variables; define a fresh variable and put the condition on its literals |
| An integer reads as the minimum of its domain | the variable has no view; create one before solving |
| Constraints silently accept everything | an `i64` overflow in the encoder: `sum |c| * max|x|` must stay under 2^62; check it before posting |
| Wrong answers after reusing a variable in a second solver | an integer variable belongs to the first solver that encodes it; rebuild fresh variables for a new solver |
| Out of memory or a C++ `bad_alloc` abort | a wide domain: a linear constraint lists every value of an integer variable (about 1.9 GB at `10^7`, abort at `10^8`); see [Modelling](#modelling) |
| An encoding runs past the deadline | encoding does not poll the terminate callback; keep weights and domains small |
| Process aborts with "Coverage goal" using Kissat | Kissat is not incremental: a clause added after a solve aborts the process; use CaDiCaL |

## Further reading

- API reference: <https://docs.rs/pindakaas/0.6.0/pindakaas/>
- Repository and changelog: <https://github.com/pindakaashq/pindakaas>
