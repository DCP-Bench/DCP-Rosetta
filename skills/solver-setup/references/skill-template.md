# Solver skill template

The shape / template a standalone solver skill should follow.

## Layout

```
<name>/
  SKILL.md               entry point
  assets/<example>/      one runnable example per folder: the program and its README.md
  references/            only when needed (per-interface API detail, a cheatsheet)
  sources.md
  evals/evals.json
```

No empty folders or placeholder files.

## SKILL.md

Adapt the sections to the solver; drop those that do not apply.

- **Description**: what and when, in at most ~400 characters; not a list of contents.
- **License**: always `Apache-2.0`. It licenses the skill text, not the solver; the
  solver's own licence and limits go in `compatibility`.
- **Link docs where needed**: each section links its doc page, each table row its API
  entry. Prefer `llms.txt`, `.md` or plain HTML; *Further reading* keeps entry points only.
- **Link files, not folders**: validators reject a directory link, so link an example's
  `README.md`.
- **Keep test material out**: the toy problems' output format, test results and sandbox
  quirks go in the report, not in the skill or `sources.md`.

````markdown
---
name: <skill-name>
description: <What the solver or framework is: language, paradigm, package/import names.> Use when <writing, debugging or explaining models with it; typical problem words; the user has chosen this tool>.
license: Apache-2.0
compatibility: Requires <language/runtime version> and <package>; <licence or size limits, if any>
metadata:
  domain: constraint-programming
  solver: <solver>
  paradigm: <cp | sat | maxsat | smt | mip | asp | clp>
  related-skills: "<owner>/<repo>[, ...]"   # only if a complementary skill was found and not bundled
---

# <Solver> (<Language>)

<One paragraph: what kind of solver, and the one idea a modeller must keep in mind
("every constraint must be linear", "the program is grounded first").>

<Only if related-skills is set:>
> **Related skill:** `<skill-name>` (<what it adds>) is not included here. When <the situation it helps with>, suggest the user install it: `npx skills add <owner>/<repo>`.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- <Runnable examples: [<example>](assets/<example>/README.md), …>

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

Full list: [<API reference / global constraint catalogue>](<URL>)

| Need | API |
|---|---|
| integer variable | [`<exact call>`](<URL to its API entry>) |
| all different | [`<exact call>`](<URL>) |
| element / table / cumulative / no-overlap | [`<exact call>`](<URL>) |
| reification / implication | [`<exact call>`](<URL>) |
| read data from a file (sizes from the data, extra keys ignored) | [`<exact call>`](<URL>) |
| minimise / maximise | [`<exact call>`](<URL>) |

<Short code blocks only for patterns a table cannot show.>

**Readable models.** Open the program with a comment that states the problem, and start
each block of constraints with a comment in the words of the problem statement, not the
API call. <Use this sentence, with the language's comment syntax.>

## Solving

Status values: [<status codes page>](<URL>) · Parameters: [<parameters page>](<URL>)

| Status | Meaning |
|---|---|
| `<OPTIMAL>` | <proven optimal> |
| `<FEASIBLE>` | <solution found, optimality not proven (e.g. timeout)> |
| `<INFEASIBLE>` | <proven no solution> |
| `<UNKNOWN>` | <limit hit, nothing found> |

<Reading values. Time limit / threads / seed parameter names.>

<Where errors appear (stderr, stdout, log file, verbose flag), and the solver's own solution checker if it has one.>

## All solutions

<The enumeration API, and how to avoid duplicates. All optimal solutions: solve, post `(objective) = optimum`, then enumerate over the output variables.> Details: [<enumeration / solution pool page>](<URL>)

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| <symptom an agent sees: error text or wrong result> | <cause> | <fix, or a link to the section that has it> |

## Further reading

- Documentation for agents: <llms-full.txt or .md docs URL>
- API reference: <URL>
- Examples: <URL> (<which files are worth reading>)
````

## Runnable examples

Every example beyond the Quick start is a complete program in `assets/<example>/`
(e.g. `assets/knapsack/model.py`), so it can be rerun when the solver changes.
`scripts/check_assets.py` runs it from its `README.md`:

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

Together the examples cover satisfy, all solutions, all optimal solutions, maximise,
minimise, infeasible and scheduling, as small general patterns rather than copies of the
toy problems. Prefer shortened official examples, credited in `sources.md`.

One example reads a JSON file given as its first argument (default: a bundled
`data.json`). It names the JSON library and its install (or shows a small reader when
the language has none), takes every size from the data, handles a ragged list and
ignores unused keys.

## sources.md

```markdown
# Sources for `<name>`

Tested with <solver> <version>, <language> <version>, <OS>.

Existing skills: <none found | each one: source / companion / ignored, with one line on why>

- <URL>: <what was taken from it>
- Learned from <upstream skill URL> (<licence>, <version>): <what it contributed>   ← only for a source skill

Verified by running: <claim>: <how>
```

## evals/evals.json

One entry per toy-problem family, plus 2–3 **negative** prompts where the skill should
not activate (the same problem with another solver, a non-modelling task about the
solver). `expected_skill` scores whether the right skill was picked (`null` for a
negative).

```json
{"skill_name": "<name>", "evals": [
  {"id": 1, "prompt": "Solve this 0/1 knapsack with <solver> from <language> …", "expected_skill": "<name>",
   "expected_output": "Proven-optimal selection", "assertions": ["Uses <solver>'s maximise API", "Checks the status is proven optimal"]},
  {"id": 9, "prompt": "Write a MiniZinc model for n-queens.", "expected_skill": null,
   "expected_output": "The skill is not used", "assertions": ["<name> is not loaded"]}]}
```
