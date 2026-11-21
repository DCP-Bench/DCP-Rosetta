---
name: solver-skill-card
description: How to write a minimal, verified skill file (card) for a combinatorial solver or modelling library, read by an LLM before it writes models. Use when creating or revising a solver skill.
---

# Writing a solver skill card

A card gives a model what it cannot reliably guess about one solver: how a model is set up, the exact API names and argument semantics, and the real pitfalls. It contains general solver knowledge only. Harness or benchmark glue (entrypoints, input reading, output registration) belongs in the task prompt, never in the card.

Evidence (DCP-Bench, 9 unfamiliar solvers, Haiku, single shot): no card 9/180 accepted, example only 56, API list only 81, both ~86–92. The example carries setup and glue (Gecode copy constructor, MaxiCP helpers). The API list carries breadth and argument semantics (Exact `addConstraint` flags). Keep both.

## Template

````markdown
# <Solver> (<language>) — <language>, <paradigm in one phrase>

## Minimal working example (knapsack)
```<lang>
<complete runnable program>
```

## API
- **Decision variables:** ...
- **Logic constraints:** ...
- **Arithmetic constraints:** ...
- **Other constraints:**
  - counting: ...
  - indexing/extensional: ...
  - ordering: ...
  - graph: ...
  - scheduling: ...
- **Objectives and solving:** ...

Docs: <official docs URL>
````

Leave out any item or family the solver does not have. Do not write "none".

## Minimal working example
- 0/1 knapsack with values `[6, 10, 12]`, weights `[1, 2, 3]` and capacity `5`, on one line. Maximise, then print the optimum (22) and the solution in a single print.
- Follow the official docs' recommended, modern style (for example CPMpy `model = cp.Model(); model.add(...)`). Check the getting-started or tutorial page; when the docs offer several APIs, pick the one the target users will need.
- Add constraints the way a long model would: create the model empty and add one statement per constraint.
- Include the imports and setup. No comments, no blank lines that aren't needed, no file input, no unused code.
- Keep only what the solver itself requires, such as a mandatory copy constructor.

## API rows
- Write every name in `code`; prose and code must be visually distinct.
- One form per concept. Prefer the forms real models use most (count them in a corpus of accepted models when one exists). Omit rare functions; a modeller can guess them from the name or look them up.
- Don't repeat what the example already shows (imports, setup).
- Semantics only as short symbolic notes, e.g. `(h ⇔ Σ ≥ k)`, `(0-based)`, `(int c only)`.
- Pitfalls only when tested and real: a missing library load, an operator that silently does nothing, a crash, a misleading return value.
- No encoding recipes or modelling advice (how to linearise an implication, how to build alldifferent from Booleans). That is not API knowledge.
- No solving or diagnosis tutorial: no statuses beyond what reading a result needs, no time-limit tuning, no UNSAT debugging.

## Verification (mandatory)
1. Take signatures from the installed library itself: Python `dir()` and docstrings, `javap`, headers, crate source. Don't trust memory or the docs alone.
2. Run the minimal example in the solver's real environment; it must print 22.
3. Write a scratch program that uses every form listed in the API, and check that it compiles and runs.
4. Test any non-obvious semantics with a tiny model and enumerate the feasible pairs: reification direction and sign, index base, bound flags, what solve returns, whether a constraint must be posted explicitly (e.g. `m &= vec.all_different()` vs a bare call).
5. Grep the finished card for harness terms (entrypoint names, instance/outputs glue) and remove them.

## Budget
- Whole card: about 1.5–3 KB and under 60 lines. Hard limits: 200 lines and 5000 characters, since some harnesses truncate.
- If over budget, cut API forms first (least used), never the example's essential glue.

## Who writes it
Use a strong model, or write it yourself. Card writing takes judgement: what counts as general API versus a recipe, and which forms matter. Small models produce cards with wrong rows, recipes and harness leakage. Modellers that read the card can be small.

## Checklist
- [ ] Title line names the solver, language and paradigm
- [ ] Example: one-line data, one print, recommended style, prints 22 when run
- [ ] API: names in `code`, one form per concept, empty items omitted, no recipes, no harness glue
- [ ] Every listed form ran in a scratch program; non-obvious semantics tested
- [ ] Size within budget
