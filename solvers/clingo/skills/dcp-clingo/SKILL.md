---
name: dcp-clingo
description: clingo, an answer set programming (ASP) system. Writes rules, choice rules and constraints, grounds and solves them, enumerates answer sets and finds proven optimal ones; used from Python (the clingo package). Use when writing, debugging or explaining ASP programs, or when the user has chosen clingo for a combinatorial or logic problem.
license: Apache-2.0
compatibility: "Python: Python 3.10+ and the clingo package (tested with clingo 5.8.2, MIT licence); no other software, no licence key."
metadata:
  domain: constraint-programming
  solver: clingo
  paradigm: asp
  interfaces: "asp"
---

# clingo

clingo grounds a logic program first (every variable is replaced by the values it can take), then searches for answer sets, the stable models of the program. The modeller's main idea: write rules that describe what a valid answer looks like, and let the search find them. Ground size, not search, is usually the bottleneck.

## Pick an interface

Read this file and the interface below.

| | ASP (Python API) |
|---|---|
| Read | [interfaces/asp.md](interfaces/asp.md) |
| Package | `clingo` wheel (CFFI), used from Python |

Other bindings (the clingo command line, C, C++ and Lua APIs) are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [Optimisation](#optimisation)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Per interface: [ASP](interfaces/asp.md); sources in [sources.md](sources.md)

## Modelling

Full list: [language reference](https://potassco.org/guide/language/). Every `#` directive is a clingo extension to plain ASP.

| Need | Syntax |
|---|---|
| fact | `p(1).` |
| rule | `q(X) :- p(X).` |
| integrity constraint (must not hold) | `:- p(X), q(X).` |
| choice with bounds | `1 { assign(N,C) : colour(C) } 1 :- node(N).` |
| negation as failure | `not in(A)` |
| integer range | `node(1..N).` |
| arithmetic | `+ - *`, `/` (truncates: `-7/2` is `-3`), modulo `\` (`7\2` is `1`) |
| sum / count / min / max | `#sum { W,I : take(I), weight(I,W) } > C`, `#count`, `#min`, `#max` |
| minimise / maximise | `#minimize { W,I : take(I), weight(I,W) }.`, `#maximize { ... }.` |
| priority levels | `#minimize { 5@2,1 : x(1); 1@1,2 : x(2) }.` (level 2 first) |
| constant | `#const n = 5.` or `Control(["-c", "n=5"])` |
| output | `#show p/2.` shows only `p/2` atoms |

Facts and rules:

- Names starting with a capital are **variables**. Predicates and constants are lowercase. `_SHIP(1).` is a parse error, and so is `-c N=5`; use `_ship`, `n`.
- Every variable must appear in a positive body literal, or the program is unsafe (see [Common issues](#common-issues)).
- Strings are constants in double quotes. The escapes `\"`, `\\` and `\n` parse; `\t` and `\uXXXX` do not. Strings have no built-in length or character access; to inspect characters, write one fact per character.
- Uppercase data (letters, codes) works as strings: `letter("S").`, `val("S",9)`. Read them back with `atom.arguments[0].string`; `str(atom)` shows them in quotes. Strings compare with `<`, as in `L1 < L2`. The cryptarithm example uses this.
- With no `#show` directive every atom is shown. Once one `#show` appears, only the listed signatures are shown. `#show.` alone hides everything.
- Bounds of a choice go outside the braces: `L { ... } U`.

Aggregate elements are **sets of tuples**. Elements with the same tuple count once. With `b(1,5). b(2,5). b(3,7).`:

```prolog
s(S) :- S = #sum { V : b(I,V) }.    % 12: the tuple 5 is counted once, not twice
t(S) :- S = #sum { V,I : b(I,V) }.  % 17: the index makes each tuple unique
c(N) :- N = #count { V : b(I,V) }.  % 2 distinct values, not 3
```

Add a distinguishing term (an index, a position or the name) to every element whose values may repeat. The same holds for weights in `#minimize` and `#maximize`. Negative weights are fine in a sum compared with `!=`, as in the cryptarithm example: `:- #sum { W*D,L : val(L,D), weight(L,W) } != 0.`

A `#sum` or `#count` aggregate cannot be compared with another aggregate: `:- #sum{...} != #sum{...}.` is a parse error. Bind each side first:

```prolog
total_a(S) :- S = #sum { V : a(V) }.
total_b(S) :- S = #sum { V : b(V) }.
:- total_a(A), total_b(B), A != B.
```

## Solving

A run ends in one of three outcomes: a model is found (satisfiable), the search finishes with no model (unsatisfiable, proven), or it is stopped early (interrupted, a limit or a cancel). The exact result attributes, option names and calls are in the [interface file](interfaces/asp.md#solving). Options: [command-line options](https://potassco.org/guide/options).

## Optimisation

Objectives are ordinary `#minimize` or `#maximize` statements, ranked by priority level. Clingo reports the cost of each model in `model.cost`, a list with one entry per priority level. For `#maximize` the cost is the **negated** value.

Without the `optN` optimisation mode, clingo stops at the first model it finds, and that model is not proven optimal. In `optN` mode clingo keeps improving the model and proves the optimum; the last model of a run with one model requested is then the proven optimum. If the solve is interrupted by a limit, the last model may be unproven: it is only the best found so far. Calls: [interface file](interfaces/asp.md#optimisation).

## All solutions

Enumerate with every model requested and project onto the shown atoms: without projection, clingo lists every combination of auxiliary atoms separately (the subset example reports 20 models without projection and 4 with it). All **optimal** solutions: `optN`, every model, projection, keeping only the models proven optimal. Calls: [interface file](interfaces/asp.md#all-solutions). Details: [enumeration and optimisation](https://potassco.org/guide/basics/).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `RuntimeError: parsing failed` on a name or string | A name starts with a capital (for example `letter(S)` or `_SHIP`), or a string uses `\t` or `\uXXXX` | Lowercase the name (`_ship`), or write the data as a string (`letter("S")`); use a real tab, or escape only `\"`, `\\`, `\n` |
| Sum or count is smaller than expected, with no error | Aggregate elements are sets of tuples, so repeated values count once: `#sum { V : b(I,V) }` gives 12 for values 5, 5, 7 | Add a distinguishing term: `#sum { V,I : b(I,V) }` gives 17 |
| `grounding stopped because of errors`, "unsafe variables" | A variable appears only in the head, a negative literal or a comparison | Bind it with a positive body literal, for example `p(X), not q(X)` |
| parse error on `:- #sum{...} != #sum{...}` | Aggregate compared with another aggregate | Bind each aggregate to a variable first |
| `info: tuple ignored: #inf@0` on stderr | A `#max` or `#min` over an empty set, during grounding | Add an unconditional element: `#max { 0,none ; E,T : end(T,E) }`; the optimum is unchanged |
| Duplicate solutions in an enumeration | Auxiliary atoms differ between models with the same shown answer | `project = "show"` |
| Enumeration never finishes | Grounding is too large, or a rule has an unbounded domain | Constrain variables in the body; use aggregates instead of listing combinations |
| Output has extra atoms | Another `#show` line, or no `#show` at all | List only the signatures to report |

Problems that depend on the Python API are in the [interface file](interfaces/asp.md#common-issues).

## Further reading

- Python API: [clingo documentation](https://docs.potassco.org/clingo/python-api/current/)
- Language and guide: [Potassco guide](https://potassco.org/guide/) (chapters: [language](https://potassco.org/guide/language/), [basics](https://potassco.org/guide/basics/))
- Command-line options: [clingo options](https://potassco.org/guide/options)

