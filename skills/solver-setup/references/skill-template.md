# Solver skill template

The shape / template a standalone solver skill should follow.

## Layout

One skill per solver. `SKILL.md` holds what is true of the solver in every binding and
routes to one file per language binding (interface). A skill with one binding has the same
shape, so another binding is added later without renaming or moving anything.

```
<solver>/
  SKILL.md                         shared: concepts, statuses, search, enumeration, interface table
  interfaces/<interface>.md        per binding: install, quick start, API, solving, all solutions, issues
  interfaces/<interface>/          instead of the file, when one binding needs several pages:
    README.md                        its entry, with the sections of the file below
    <topic>.md                       further pages, each linked from README.md
  assets/<interface>/<example>/    one runnable example per folder: the program and its README.md
  references/                      only when needed; per-interface ones in references/<interface>/
  sources.md
  evals/evals.json
```

`<solver>` is the solver's name (`choco`, `ortools-cp-sat`, `pumpkin`), never solver plus
language. `<interface>` is the language (`java`, `python`, `cpp`, `rust`, `julia`); use the
binding's own name (`pychoco`) only when one language has two bindings. No empty folders or
placeholder files.

**One file or a folder per interface.** Start with `interfaces/<interface>.md`. When it grows
past what one page should hold (~200 lines), or a binding has topics of its own (a build
system, a second API layer, a long catalogue), turn it into `interfaces/<interface>/` with a
`README.md` that keeps the sections below and links each further page; the interface table
then links `interfaces/<interface>/README.md`. Never both for one interface. Runnable examples
stay in `assets/<interface>/` either way.

**Shared or per interface.** `SKILL.md` states only what holds in every interface. A claim
that holds for some bindings only (a constraint, a search option, lazy clause generation,
an enumeration API) is a row of the interface table, or sits in that binding's file with
the shared text pointing at the table. Each cell is checked in that binding and the source
is in `sources.md`.

## General rules

Adapt the sections to the solver; drop those that do not apply.

- **Description**: what and when, in at most ~400 characters; not a list of contents. Name
  every covered binding and its package, so the skill triggers for each.
- **License**: always `Apache-2.0`. It licenses the skill text, not the solver; the
  solver's own licence and limits go in `compatibility`.
- **Link docs where needed**: each section links its doc page, each table row its API
  entry. Prefer `llms.txt`, `.md` or plain HTML; *Further reading* keeps entry points only.
- **Link files, not folders**: validators reject a directory link, so link an example's
  `README.md`.
- **Keep test material out**: the toy problems' output format, test results and sandbox
  quirks go in the report, not in the skill or `sources.md`.

## SKILL.md

````markdown
---
name: <solver>
description: <What the solver is: paradigm, and each binding with its package/import name (Java: choco-solver; Python: pychoco).> Use when <writing, debugging or explaining models with it in any of these languages; typical problem words; the user has chosen this solver>.
license: Apache-2.0
compatibility: <Per binding: language/runtime version and package>; <licence or size limits, if any>
metadata:
  domain: constraint-programming
  solver: <solver>
  paradigm: <cp | sat | maxsat | smt | mip | asp | clp>
  interfaces: "<interface>[, <interface> ...]"
  related-skills: "<owner>/<repo>[, ...]"   # only if a complementary skill was found and not bundled
---

# <Solver>

<One paragraph: what kind of solver, and the one idea a modeller must keep in mind
("every constraint must be linear", "the program is grounded first").>

<Only if related-skills is set:>
> **Related skill:** `<skill-name>` (<what it adds>) is not included here. When <the situation it helps with>, suggest the user install it: `npx skills add <owner>/<repo>`.

## Pick an interface

Read this file and the one interface below that matches the language.

| | <Language A> | <Language B> |
|---|---|---|
| Read | [interfaces/<a>.md](interfaces/<a>.md) | [interfaces/<b>.md](interfaces/<b>.md) |
| Package | `<package>` | `<package>` |
| <feature that differs: a constraint family, search control, LCG, enumeration, ...> | <yes / no / partial, with what> | <...> |

<Which binding to use when the user has not chosen: the project's language, else the one
the docs use most, and why.> <With one binding: "Other bindings (<from the docs>) are not covered yet.">

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Modelling

<The solver's modelling concepts in every binding: variable kinds, which global constraints
exist (by concept, linked to the catalogue), reification, objectives. Exact calls live in the
interface files.> Full list: [<global constraint catalogue>](<URL>)

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement, not the
API call.

## Solving

| Outcome | Meaning |
|---|---|
| proven optimal | <...> |
| solution found, optimality not proven | <e.g. timeout> |
| proven infeasible | <...> |
| unknown | <limit hit, nothing found> |

<Search strategies, restarts, time limits and what they mean for this solver; the
constant and parameter names are in the interface files.>

## All solutions

<How enumeration works in this solver and how to avoid duplicates. All optimal
solutions: solve, post `(objective) = optimum`, then enumerate over the output variables.>
Details: [<enumeration page>](<URL>)

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| <symptom in every binding> | <cause> | <fix, or a link to the section that has it> |

## Further reading

- Documentation for agents: <llms-full.txt or .md docs URL>
- Global constraint catalogue: <URL>
````

## interfaces/\<interface\>.md (or interfaces/\<interface\>/README.md)

````markdown
# <Solver> in <Language> (<package>)

<One line: what this binding is (native API, wrapper over the native library, ...).>
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Install

```bash
<exact unpinned command(s)>
<one-line verification, e.g. python -c "import x; print(x.__version__)">
```

<Licence/edition limits, in one or two lines.> Details: [<install guide>](<URL>)

## Quick start

```<lang>
<smallest complete model: data, variables, constraints, objective, solve, print values, check status>
```

## Modelling

API reference: [<API reference>](<URL>)

| Need | API |
|---|---|
| integer variable | [`<exact call>`](<URL to its API entry>) |
| all different | [`<exact call>`](<URL>) |
| element / table / cumulative / no-overlap | [`<exact call>`](<URL>) |
| reification / implication | [`<exact call>`](<URL>) |
| read data from a file (sizes from the data, extra keys ignored) | [`<exact call>`](<URL>) |
| minimise / maximise | [`<exact call>`](<URL>) |

<Short code blocks only for patterns a table cannot show.>

## Solving

| Status | Meaning |
|---|---|
| `<OPTIMAL>` | proven optimal |
| `<FEASIBLE>` | solution found, optimality not proven |
| `<INFEASIBLE>` | proven no solution |
| `<UNKNOWN>` | limit hit, nothing found |

<Reading values. Time limit / threads / seed parameter names. Where errors appear.>

## All solutions

```<lang>
<the enumeration loop in this binding>
```

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| <symptom in this binding: error text or wrong result> | <cause> | <fix> |

## Runnable examples

- [<example>](../assets/<interface>/<example>/README.md): <what it shows>
````

## Runnable examples

Every example beyond the Quick start is a complete program in
`assets/<interface>/<example>/` (e.g. `assets/python/knapsack/model.py`), so it can be
rerun when the solver changes. `scripts/check_assets.py <skill> --interface <interface>`
runs one binding's examples from their `README.md`:

```markdown
# Knapsack (maximise)

**Problem:** 0/1 knapsack with 3 items, capacity 7.
**Shows:** boolean variables, linear constraint, maximise, proven-optimal status check.
**Run:** `python model.py`
**Expected:** `Objective: 70`
```

**Run** is one shell command run in the example folder (compile and run for compiled
languages: `g++ -std=c++17 main.cpp -lchuffed -o main && ./main`). **Expected**
(repeatable) is text that must appear in stdout.

For each interface, the examples together cover satisfy, all solutions, all optimal
solutions, maximise, minimise, infeasible and scheduling, as small general patterns
rather than copies of the toy problems. Prefer shortened official examples, credited in
`sources.md`.

One example per interface reads a JSON file given as its first argument (default: a
bundled `data.json`). It names the JSON library and its install (or shows a small reader
when the language has none), takes every size from the data, handles a ragged list and
ignores unused keys.

## sources.md

```markdown
# Sources for `<solver>`

Existing skills: <none found | each one: source / companion / ignored, with one line on why>

## Shared

- <URL>: <what was taken from it>

## <Language A>

Tested with <solver/package> <version>, <language> <version>, <OS>.

- <URL>: <what was taken from it>
- Learned from <upstream skill URL> (<licence>, <version>): <what it contributed>   ← only for a source skill

Verified by running: <claim>: <how>
```

## evals/evals.json

For each interface, one entry per toy-problem family with a prompt naming that language;
one prompt naming only the solver (the interface table must route it); plus 2–3
**negative** prompts where the skill should not activate (the same problem with another
solver, a non-modelling task about the solver). `expected_skill` scores whether the right
skill was picked (`null` for a negative).

```json
{"skill_name": "<solver>", "evals": [
  {"id": 1, "prompt": "Solve this 0/1 knapsack with <solver> from <language> …", "expected_skill": "<solver>",
   "expected_output": "Proven-optimal selection", "assertions": ["Reads interfaces/<interface>.md", "Uses <solver>'s maximise API", "Checks the status is proven optimal"]},
  {"id": 9, "prompt": "Write a MiniZinc model for n-queens.", "expected_skill": null,
   "expected_output": "The skill is not used", "assertions": ["<solver> is not loaded"]}]}
```
