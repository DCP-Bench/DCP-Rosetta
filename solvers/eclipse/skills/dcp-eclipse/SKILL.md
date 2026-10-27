---
name: dcp-eclipse
description: ECLiPSe, the ECLiPSe Constraint Logic Programming system (version 7.x), used through its native Prolog interface (eclipse launcher, .ecl files), for finite-domain constraint satisfaction and optimisation in Prolog syntax with libraries ic, ic_global, gfd (Gecode), branch_and_bound and timeout. Covers variables and domains, global constraints, reification, search, optimisation with bb_min, all solutions, timeouts and reading JSON data. Use when writing, debugging or explaining ECLiPSe models, or when the user has chosen ECLiPSe for a puzzle, scheduling, assignment or routing problem.
license: Apache-2.0
compatibility: Requires ECLiPSe 7.x from eclipseclp.org (tested with 7.2 #13, x86_64 Linux, libraries ic, ic_global, ic_edge_finder, ic_mdd, gfd, branch_and_bound, timeout, listut, json). Free and open source (MPL); no key or account.
metadata:
  domain: constraint-programming
  solver: ECLiPSe
  paradigm: clp
  interfaces: "prolog"
---

# ECLiPSe (CLP)

ECLiPSe is a Prolog system with constraint libraries. Variables get domains, constraints
propagate when posted, and search is Prolog backtracking. Rules to keep: **load the libraries
with directives at the top of the file, give every variable a finite domain, label every
variable whose value you need**, and **minimise through `bb_min/3` with a variable as cost**.
A failed goal means "no solution"; nothing is raised.

## Pick an interface

Read this file, then the interface file.

| | Prolog |
|---|---|
| Read | [interfaces/prolog/README.md](interfaces/prolog/README.md) |
| Package | the ECLiPSe 7.x distribution (`eclipse` launcher, libraries `ic`, `gfd`, `branch_and_bound`, ...) |

ECLiPSe is used through its own Prolog language. Other bindings (the embedding interfaces for C, Java and Python) are not covered yet.

## Contents
- [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions)
- [Common issues](#common-issues) · [Further reading](#further-reading)
- Per interface: [Prolog](interfaces/prolog/README.md); sources in [sources.md](sources.md)

## Modelling

Variables get finite domains, constraints propagate when posted, and search is backtracking. The
libraries (`ic`, `gfd`, `ic_global`, ...), the syntax, the global constraints and their arities are in
[the Prolog interface](interfaces/prolog/README.md). Docs: [ic library](https://eclipseclp.org/doc/bips/lib/ic/index.html), [gfd library](https://eclipseclp.org/doc/bips/lib/gfd/index.html).

## Solving

| Outcome | Meaning |
|---|---|
| goal succeeds | a solution; variables hold it once labelled |
| goal fails | no solution; nothing is raised |
| optimisation exits normally | the best solution found, proven optimal unless a time limit was set |
| optimisation cut by a time limit | best found so far, optimality not proven |

Search order often decides between seconds and a timeout; the calls are in the interface file.

## All solutions

Collect copies of labelled solutions (label inside the goal, because copies carry unlabelled
variables); for all optimal solutions find the optimum first, then enumerate under the cost fixed to it.
Calls: [Prolog interface](interfaces/prolog/README.md#all-solutions).

## Common issues

Symptom to fix table: [Prolog common issues](interfaces/prolog/common-issues.md).

## Further reading

- [ECLiPSe documentation](https://eclipseclp.org/doc/), [library index](https://eclipseclp.org/doc/bips/lib/index.html)
