---
name: solver-skill-card
description: How to write a minimal, verified skill file (card) for a combinatorial solver or modelling library, read by an LLM before it writes models. Use when creating or revising a solver skill.
---

# Writing a solver skill card

A card gives a model what it cannot reliably guess about one solver: how a model is set up, the exact API names and argument semantics, the real pitfalls, and how to model so that the solver finishes. It contains general solver knowledge only. Harness or benchmark glue (entrypoints, input reading, output registration) belongs in the task prompt, never in the card.

Evidence (DCP-Bench, 9 unfamiliar solvers, Haiku, single shot): no card 9/180 accepted, example only 56, API list only 81, both ~86–92. The example carries setup and glue (Gecode copy constructor, MaxiCP helpers). The API list carries breadth and argument semantics (Exact `addConstraint` flags). Keep both. A short modelling section then lifted 101 to 112/180 and cut timeouts from 59 to 46. The gain was largest where it pointed to a global constraint or search control the modeller was not using (ECLiPSe +5, IDP-Z3 +4), and about zero for pseudo-Boolean, MaxSAT and SAT solvers. Only the structure, symmetry and search bullets changed what modellers wrote. On well-known solvers (CPMpy, MiniZinc, SCIP) the card still helped by removing errors (no card 35/60, card 41), and the modelling section added nothing (40). A held-out check on 21 more solvers (cards written without the 20 test problems, 420 cases) gave no card 138, card 215, card with modelling section 223: the card again carried the gain (compile errors 87 to 38), and the modelling section added a little on CP and MIP solvers, none on SAT, PB and SMT.

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

## Modelling
- **Domains:** ...
- **Structure:** ...
- **Lookups:** ...
- **Symmetry:** ...
- **Implied constraints:** ...
- **Search:** ...

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
- No encoding recipes or modelling advice in API rows (how to linearise an implication, how to build alldifferent from Booleans). Modelling advice goes in the Modelling section.
- No solving or diagnosis tutorial: no statuses beyond what reading a result needs, no time-limit tuning, no UNSAT debugging.

## Modelling section
- One bullet per technique, in this order: domains, structure, lookups (costs, for linear solvers), symmetry, implied constraints, search. Each bullet names the solver's own construct in `code`, with a one-line example.
- Domains: tight bounds from the data, and the solver's form for a set of allowed values.
- Structure: the global constraint that matches a common structure, in its strongest form, and what to avoid instead. For example, a tour is successor variables restricted to allowed neighbours plus `circuit` (a path adds a dummy node), not a position sequence with move tests. Patterns use `regular` or table constraints; resources use cumulative constraints. A solver without the global gets the encoding that replaces it (Boolean arcs between allowed pairs plus order variables through reification).
- Lookups: index a constant row directly (`element(succ[i], row_i, leg[i])`), never a computed flat index. A product with a small-domain factor is split on its values. Linear solvers weight 0/1 choices directly in sums.
- Search: only when the model controls it (a branching call, a labelling list, a search goal). Put the deciding variables first and use first-fail. Leave the bullet out when the runner owns search.
- Generic only: no problem names, no problem-specific bounds. Vague hints are ignored ("count bounds on prefixes" was used 0/4 times); give the construct.
- About 700–1100 characters. Verify every form like an API row.

## Verification (mandatory)
1. Take signatures from the installed library itself: Python `dir()` and docstrings, `javap`, headers, crate source. Don't trust memory or the docs alone.
2. Run the minimal example in the solver's real environment; it must print 22.
3. Write a scratch program that uses every form listed in the API, and check that it compiles and runs.
4. Test any non-obvious semantics with a tiny model and enumerate the feasible pairs: reification direction and sign, index base, bound flags, what solve returns, whether a constraint must be posted explicitly (e.g. `m &= vec.all_different()` vs a bare call).
5. Grep the finished card for harness terms (entrypoint names, instance/outputs glue) and remove them.

## Budget
- Whole card: about 1.5–3 KB and under 60 lines. Hard limits: 200 lines and 5000 characters, since some harnesses truncate.
- If over budget, cut API forms first (least used), never the example's essential glue.
- When shrinking, cut forms whose syntax is guessable from the name. Keep a form whose syntax is not obvious, even if it is rare (e.g. a quantifier over two variables, 2-D list indexing, collecting variables into an array type).

## Reference cards
Verified cards written with this skill (every example and listed form was run in the solver's environment):
[Choco (Java)](references/cards/choco_java.md), [Choco (Python)](references/cards/choco_python.md), [Chuffed](references/cards/chuffed_cpp.md), [Clingo](references/cards/clingo_asp.md), [CPMpy](references/cards/cpmpy_python.md), [cvc5](references/cards/cvc5_python.md), [DOcplex](references/cards/docplex_cplex.md), [ECLiPSe](references/cards/eclipse_clp.md), [Essence'](references/cards/essence_prime_minion.md), [Exact](references/cards/exact.md), [Gecode](references/cards/gecode_cpp.md), [Gurobi](references/cards/gurobipy_python.md), [Hermax](references/cards/hermax.md), [HiGHS](references/cards/highs_cpp.md), [Huub](references/cards/huub_rust.md), [IDP-Z3](references/cards/idp_z3.md), [JaCoP](references/cards/jacop_java.md), [JuMP](references/cards/jump_highs.md), [MaxiCP](references/cards/maxicp_java.md), [MiniZinc](references/cards/minizinc_gecode.md), [OR-Tools CP-SAT (C++)](references/cards/ortools_cp_sat_cpp.md), [OR-Tools CP-SAT (Python)](references/cards/ortools_cp_sat_python.md), [Paramita](references/cards/paramita_python.md), [Picat](references/cards/picat.md), [Pindakaas](references/cards/pindakaas_rust.md), [PuLP](references/cards/pulp_cbc.md), [Pumpkin](references/cards/pumpkin_rust.md), [PyCSP3](references/cards/pycsp3_ace.md), [PySAT](references/cards/pysat.md), [Python-MIP](references/cards/python_mip_cbc.md), [SCIP](references/cards/scip_python.md), [SWI-Prolog CLP(FD)](references/cards/swipl_clpfd.md), [Z3](references/cards/z3_python.md).

## Who writes it
Use a strong model, or write it yourself. Card writing takes judgement: what counts as general API versus a recipe, and which forms matter. Small models produce cards with wrong rows, recipes and harness leakage. Modellers that read the card can be small.

## Checklist
- [ ] Title line names the solver, language and paradigm
- [ ] Example: one-line data, one print, recommended style, prints 22 when run
- [ ] API: names in `code`, one form per concept, empty items omitted, no recipes, no harness glue
- [ ] Modelling: the solver's own constructs for each technique, generic, search only if the model controls it
- [ ] Every listed form ran in a scratch program; non-obvious semantics tested
- [ ] Size within budget
