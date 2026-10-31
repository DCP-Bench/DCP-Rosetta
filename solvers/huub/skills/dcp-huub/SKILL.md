---
name: dcp-huub
description: Huub, a constraint programming solver written in Rust (crate huub 100.1.0) that uses lazy clause generation, with integer and Boolean decision variables, linear, element, table, cumulative and disjunctive constraints, and proven optimisation. Use when writing, debugging or explaining a constraint or optimisation model in Rust with Huub, or when the user has chosen Huub.
license: Apache-2.0
compatibility: Requires Rust with cargo (tested with Rust 1.98.1), huub 100.1.0 from crates.io (MPL-2.0), and a C++ compiler (g++) on PATH, because huub builds the CaDiCaL SAT solver. Needs network access, or a vendored copy of the crates.
metadata:
  domain: constraint-programming
  solver: huub
  paradigm: cp
  interfaces: "rust"
---

# Huub


Huub is a constraint programming solver with lazy clause generation, written in Rust. You
create decision variables on a `Model`, post constraints with its builders, then lower the
model to a `Solver` and solve. Two rules matter most. **Every `post()` returns a `Result`**:
an ignored `Err` silently drops a constraint. **A `Bool` is a view, and so is an integer**:
a view can be a variable, a constant or a derived expression.

## Pick an interface

Read this file and the interface file below.

| | Rust |
|---|---|
| Read | [interfaces/rust.md](interfaces/rust.md) |
| Package | `huub` crate 100.1.0 (crates.io); builds CaDiCaL, so it needs a C++ compiler |

Huub's own API is Rust. Other bindings are not covered yet.

## Contents
- [Modelling](#modelling)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

Constraint list and exact calls: [interfaces/rust.md](interfaces/rust.md#modelling).

**Not available:** `circuit`, `subcircuit`, `regular`, `count`, `global_cardinality`, `lex`,
`inverse`, `nvalue`, `among`, `bin_packing`. Write them as decompositions. A count is a linear
sum of `x.eq(v)`. The circuit decomposition is in [circuit-decomposition](assets/rust/circuit-decomposition/README.md),
and modulo is `k*q + r == x` with `0 <= r <= k-1`.

## Common issues

Solver-level problems; those of the Rust API are in [interfaces/rust.md](interfaces/rust.md#common-issues).

| Symptom | Cause | Fix |
|---|---|---|
| `post()` never returns on a 2-term equality such as `a + b == 1100`, or on two 2-term equalities over the same pair | Huub aliases the variables of a 2-term `eq` and can hang, also on distinct pairs; a single small 2-term `eq` such as `x + y == 7` or `x - y == 0` posts fine | When `post()` hangs, and always for two equalities over one pair, post `le` and `ge` instead of `eq` |
| Memory explodes with `y == 3*x` on large domains | A 2-term equality with a coefficient other than 1 | Post `le` and `ge` instead of `eq` |
| `no_overlap` with `.strict(false)` misses solutions that contain zero-size objects | Huub 100.1.0 still treats a zero-size object as an obstacle | Use the pairwise disjunction and exempt a pair when one size is 0 |

## Further reading

- Crate and API reference: <https://docs.rs/huub/100.1.0/huub/>
- Project site and repository: <https://huub.solutions>, <https://github.com/huub-solver/huub>
- Runnable examples: `assets/rust/`, each folder with `README.md`, `Cargo.toml` and `src/main.rs`
