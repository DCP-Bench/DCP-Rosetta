---
name: dcp-idp-z3
description: IDP-Z3, a reasoning engine for FO(.) ("FO-dot") knowledge bases (vocabulary, theory, structure) built on Z3; pip package idp-engine, Python module idp_engine, command idp-engine. Use when writing, debugging or explaining FO(.) models, model expansion or optimisation with IDP-Z3, or when the user has chosen IDP-Z3 for a constraint, configuration or scheduling problem.
license: Apache-2.0
compatibility: Requires Python 3.11+ on x86_64 Linux with glibc 2.28+ (the sli-lib dependency ships only as a manylinux_2_28 wheel) and pip install idp-engine; tested with idp-engine 0.12.1, which pins z3-solver 4.11.2.0. LGPL-3.0, no licence key or size limit.
metadata:
  domain: constraint-programming
  solver: idp-z3
  paradigm: smt
  interfaces: "idp"
---

# IDP-Z3 (FO(.))

IDP-Z3 reasons over a **knowledge base** written in FO(.), typed first-order logic with
aggregates and inductive definitions: a `vocabulary` declares types and symbols, a
`theory` states sentences, a `structure` gives the data. It is not a program: you ask the
engine for models (model expansion), an optimum, or consequences, from Python
(`idp_engine`) or from a `procedure main()` run by the `idp-engine` command. The one idea
to keep in mind: **type ranges are integer literals**, so the data, sizes included, goes
into a structure that your program writes.

## Pick an interface

Read this file, then the interface file. Other bindings of IDP-Z3 are not covered yet.

| | IDP |
|---|---|
| Read | [interfaces/idp.md](interfaces/idp.md) |
| Package | `idp-engine` (Python module `idp_engine`, command `idp-engine`) |

## Contents
- [Knowledge base](#knowledge-base) · [FO(.) syntax](#fo-syntax) · [Further reading](#further-reading)
- Interface: [IDP](interfaces/idp.md) (install, quick start, solving, all solutions, common issues); sources in [sources.md](sources.md)
- References: [FO(.) gotchas and modelling lessons](references/gotchas.md), [engine behaviour, driving z3 directly, timings](references/idp/engine.md)

## Knowledge base

Language reference: [FO(.)](https://docs.idp-z3.be/en/stable/FO-dot.html) · [syntax summary](https://docs.idp-z3.be/en/stable/summary.html)

| Need | Write |
|---|---|
| index type sized by data | vocabulary `type Item <: Int`, structure `Item := {0..4}.` (`{}` when empty) |
| fixed small range | `type Digit := {0..9}` in the vocabulary: a literal range is numeric, so `d() + 1 = 3` works. Literals only: `{1..n()}` is a parse error |
| integer decision | function into a finite type, `val: Letter -> Digit` |
| yes/no decision | predicate, `queen: Row * Col -> Bool` (never `Row -> Col -> Bool`) |
| constant | `n: () -> Int`, used as `n()` (always applied) |
| 1-D / 2-D data | `w := {0->7, 1->8}.` / `cost := {(0,0)->1, (0,1)->2}.` (tuple parentheses required) |
| predicate data | the set of true tuples, `edge := {(0,1), (1,2)}.` or `{}` |
| proposition data | `p := true.` |
| definition (closed world) | `{ ! x in T: reach(x) <- start(x). ! x in T: reach(x) <- ? y in T: reach(y) & edge(y, x). }` |
| count of a defined predicate | `{ ! c in Colour: used(c) <- ? v in Node: colour(v) = c. }` then `n() = #{ c in Colour: used(c) }.` |
| objective | a nullary `total: () -> Int` fixed by `total() = sum{{ ... }}.` |

Write the knowledge base as a plain string and **append a structure generated from your
data** ([project-selection-json](assets/idp/project-selection-json/README.md)): sizes become
range literals, lists become `{i->v}` maps, ragged lists become predicates or a padded
map with a length function. Compute any constant the theory needs (a magic sum, a bound)
in the program and put it in the structure. Several structure blocks merge into one
`Theory`. Arrays you write 0-based stay 0-based; shift 1-based data in the constraint
(`r + 1 = pos(k)`). Comment each block of sentences with the requirement it encodes.

## FO(.) syntax

| Meaning | Write | Not |
|---|---|---|
| less-or-equal | `=<` | `<=` (reverse implication) |
| not equal / equal | `~=` / `=` | `!=` / `==` (parse errors) |
| and / or / not | `&` `\|` `~` (or `and` `or` `not`) | |
| implies / iff | `=>` / `<=>` | |
| for all / exists | `! a, b in T:` / `? a in T:` | `! a b in T:` (comma required) |
| exactly / at most / at least k | `?=1 v in T: p(v).` `?=<2 ...` `?>=2 ...` | |
| count | `#{ v in T: p(v) }` | |
| sum | `sum{{ e(v) \| v in T: guard(v) }}` (**double** braces) | `sum{ ... }`, `sum(v in T)(e)` |
| min / max | `max{ e(v) \| v in T: guard(v) }` | |
| conditional term | `if c then a else b` | |
| definition | `{ ! v in T: even(v) <- v % 2 = 0. }` | |

**Every sentence ends with `.`**. Declarations are `name: A * B -> Result`; there is no
`var`/`pred` keyword. The parser's useful line is the **last** one,
`Expected ... at position (l, c) => '... *token ...'`, where `*` marks where it stopped.
**Precedence**, loosest to tightest: quantifiers, `<=`, `<=>`, `=>`, `|`, `&`, comparisons,
`+ -`, `* / %`, unary `- ~`. So `a & b => c` means `(a & b) => c`, and `p | q & r` means
`p | (q & r)` (both checked). Parenthesise any sentence that mixes `&`, `|` and `=>`, and
any chain of `=>`, so the reader does not have to apply the table.

The full list of traps, each verified: [references/gotchas.md](references/gotchas.md).

## Further reading

- Documentation: <https://docs.idp-z3.be/en/stable/> (FO(.) reference, summary, Python API)
- Package: <https://pypi.org/project/idp-engine/>
- Source of truth for engine behaviour: `idp_engine/Theory.py` and the grammar `idp_engine/Idp.tx` in the installed package
