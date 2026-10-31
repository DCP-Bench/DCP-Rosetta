---
name: dcp-pumpkin
description: Pumpkin, a constraint solver written in Rust (crate pumpkin-solver 0.5.0) with lazy clause generation, integer and Boolean variables, linear and global constraints, and proven optimisation. Use when writing, debugging or explaining a constraint or optimisation model with Pumpkin, in Rust, or when the user has chosen Pumpkin.
license: Apache-2.0
compatibility: "Rust: cargo (tested with Rust 1.98.1), pumpkin-solver 0.5.0 from crates.io (MIT OR Apache-2.0), git on PATH while building, and network access or a vendored copy of the crates. Build with NO_CHECKERS=true."
metadata:
  domain: constraint-programming
  solver: pumpkin
  paradigm: cp
  interfaces: "rust"
---

# Pumpkin

Pumpkin is a constraint programming solver with lazy clause generation, written in Rust by ConSol Lab at TU Delft. You create variables on a solver object, post constraints built by Pumpkin's own constructors, then ask it to satisfy or optimise. A Boolean is a literal, not a variable, and a linear constraint takes variables with explicit coefficients.

## Pick an interface

Read this file, then the interface file for your language.

| | Rust |
|---|---|
| Read | [interfaces/rust.md](interfaces/rust.md) |
| Package | `pumpkin-solver` crate on crates.io, native API |

Other bindings of Pumpkin are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- Per language: [Rust](interfaces/rust.md); sources in [sources.md](sources.md)

## Modelling

Official: [repository](https://github.com/consol-lab/pumpkin). The constructors and their exact arguments are in the interface file.

Pumpkin offers linear (in)equalities, `all_different`, `element` (0-based), `table`, `cumulative`, `times`, `division` (truncates toward zero), `absolute`, `maximum`, `minimum`, clauses and Boolean-weighted sums, and reification of any posted constraint in both directions or one way.

There is no modulo and no cardinality (count) constraint. Write `a == k*q + r` with `0 <= r < k` for modulo, and use a Boolean-weighted sum with unit weights for "at most k of these literals".

**Counting distinct values (for example the number of colours).** Pumpkin has no count-distinct or cardinality constraint. Give each value a variable in `0..=n-1`, take the maximum of them into one variable `top`, and minimise `top`. Values start at 0, so the count is `optimum + 1`.

A zero coefficient must never reach a linear term: drop zero weights before building terms (the failure modes are in the interface file).

## Solving

The objective is a single variable. Every call needs a brancher, a conflict resolver and a time budget.

| Outcome | Meaning |
|---|---|
| satisfiable | A solution was found |
| unsatisfiable | Proven: no solution (or none left, when enumerating) |
| unknown | The time budget ran out; nothing proven |
| optimal | Proven optimal |
| satisfiable or stopped, while optimising | A solution was found but optimality is not proven |

For a larger instance, `unknown` or `stopped` means the budget ran out: raise the time limit to prove optimality. A solution from a cut-off run is valid, but its value is only a bound on the optimum. The job-shop instance ft06 (optimum 55, 6 jobs by 6 machines) solved in under 2 seconds of wall time with a release build.

## All solutions

Enumerate by solving again after each solution, with a clause that rules out the values just printed. Block only the variables you print: a clause over auxiliary variables lets the same printed answer appear twice.

**All optimal solutions.** Optimise first, then fix the objective to the best value found, and enumerate as above.

## Further reading

- Repository and changelog: <https://github.com/consol-lab/pumpkin>
- Crate API reference: <https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/>
- Per language: [Rust](interfaces/rust.md)
