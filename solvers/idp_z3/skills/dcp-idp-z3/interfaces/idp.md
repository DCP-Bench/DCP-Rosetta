# IDP-Z3 through `idp_engine` and the `idp-engine` command

What holds for every use of IDP-Z3 (the knowledge base, FO(.) syntax) is in
[SKILL.md](../SKILL.md); this page is the Python API, the command line and what goes wrong
with them.

## Contents
- [Examples](#examples) · [Install](#install) · [Quick start](#quick-start) · [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues)

## Examples

| Example | Pattern | Run |
|---|---|---|
| [queens-cli](../assets/idp/queens-cli/README.md) | satisfy and all solutions, `idp-engine` command | `idp-engine --no-timing queens.idp` |
| [subset-sum-all](../assets/idp/subset-sum-all/README.md) | all solutions, Python API, auxiliary symbol | `python model.py` |
| [assignment-all-optimal](../assets/idp/assignment-all-optimal/README.md) | all optimal solutions | `python model.py` |
| [project-selection-json](../assets/idp/project-selection-json/README.md) | maximise, data from a JSON file, ragged list | `python model.py data.json` |
| [coins-minimise](../assets/idp/coins-minimise/README.md) | minimise, `idp-engine` command | `idp-engine --no-timing coins.idp` |
| [infeasible-roster](../assets/idp/infeasible-roster/README.md) | infeasible | `python model.py` |
| [schedule-makespan](../assets/idp/schedule-makespan/README.md) | scheduling, optimum under a time limit | `python model.py` |

## Install

```bash
pip install idp-engine
idp-engine --version          # 0.12.1
```

It installs its own z3-solver (4.11.2.0 for idp-engine 0.12.1, older than the current
z3), so use a virtual environment if another package needs a newer z3. Details:
[IDP-Z3 documentation](https://docs.idp-z3.be/en/stable/IDP-Z3.html)

## Quick start

```python
from idp_engine import IDP, Theory

n = 8
kb = IDP.from_str("""
vocabulary V {
    type Row <: Int
    queen: Row -> Row                       // queen(r) = column of the queen in row r
}
theory T: V {
    // different columns and diagonals
    ! r1, r2 in Row: r1 < r2 => queen(r1) ~= queen(r2).
    ! r1, r2 in Row: r1 < r2 => queen(r1) - r1 ~= queen(r2) - r2.
    ! r1, r2 in Row: r1 < r2 => queen(r1) + r1 ~= queen(r2) + r2.
}
structure S: V {
    Row := {1..%d}.
}
""" % n)
theory = Theory(*kb.get_blocks("T, S"))
for model in theory.expand(max=1, timeout_seconds=10):
    if isinstance(model, str):
        print(model.strip())        # "No models." when infeasible
    else:
        print([int(str(model[f"queen({r})"].value)) for r in range(1, n + 1)])
```

## Solving

API: [IDP-Z3 Python API and procedures](https://docs.idp-z3.be/en/stable/IDP-Z3.html)

| Call | Does |
|---|---|
| `IDP.from_str(text)` / `IDP.from_file(path)` | parse; uninterpreted `<: Int` types are fine until `Theory()` |
| `kb.get_blocks("T, S")` | the named blocks (default names `V`, `T`, `S`) |
| `Theory(*blocks)` | ground; "Expected an interpretation for type X" if a type is unsized |
| `theory.expand(max=10, timeout_seconds=10, complete=False)` | yields models (`Assignments`), then **one message string**; `max=0`, `timeout_seconds=0` mean unlimited |
| `theory.optimize("total()", minimize=True)` | fixes `total()` to its optimum; chain `.expand()` for the models |
| `model["queen(3)"].value` | an Expression; keys look like `"cost(0, 1)"`, `"total()"` |

Messages: `"No models."` (infeasible), `"\nNo more models."` (enumeration complete),
`"\nMore models may be available.  Change the max argument to see them."`, the
`timeout_seconds` variants, and `"\nNo model found in N seconds. ..."`.

- **Read values by text**: `int(str(v.value))`; a Boolean is `str(v.value) == "true"`.
  `bool(v.value)` is always `True`, even for `false`. With `complete=False` (the default) an
  unconstrained term's value can be `None` and is not enumerated; pass `complete=True` when
  every symbol needs a value ([gotchas](../references/gotchas.md#procedures-and-the-python-side)).
- `optimize` raises `AssertionError("Optimization requires satisfiable specification")` for
  an infeasible theory **and** when z3 gives up, has **no time limit**, and returns a wrong
  optimum for an unbounded objective. Give the objective's ingredients finite types, or
  drive the z3 `Optimize` yourself ([schedule-makespan](../assets/idp/schedule-makespan/README.md),
  [references/engine.md](../references/idp/engine.md)).
- **Command line**: `idp-engine file.idp` runs `procedure main()` (without one: `KeyError:
  'main'`), with `pretty_print(model_expand(T, S, max=0, timeout_seconds=0))`,
  `pretty_print(minimize(T, S, term="total()"))` (one optimal model; `maximize` likewise),
  `model_check(T, S)` (`sat`/`unsat`), `model_propagate(T, S)`. `--no-timing` drops the
  timing line. A procedure cannot import modules, so read JSON data from Python.
- Errors are exceptions with a traceback (the CLI exits 1); the last line is the useful one.

## All solutions

`theory.expand(max=0, timeout_seconds=0)` enumerates until `"\nNo more models."`
([subset-sum-all](../assets/idp/subset-sum-all/README.md)). It blocks on **every** unknown term,
so a free auxiliary symbol multiplies the models (a free `aux: () -> V` turned 3
solutions into 9; a leading `_` does not help): fix each auxiliary symbol by an equation
or a definition. **All optimal**: `theory.optimize(...)` then `theory.expand(max=0, ...)`
enumerates only optimal models ([assignment-all-optimal](../assets/idp/assignment-all-optimal/README.md));
with the z3 route, add `term == best` to `theory.solver` and block the output terms
yourself ([references/engine.md](../references/idp/engine.md)).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Expected IDPFLOAT or INT` at a type range | `{1..n()}` or `{1..n}` | write the literal from your program ([Knowledge base](../SKILL.md#knowledge-base)) |
| `Expected '{{' ...` after `sum{` | an f-string turned `{{` into `{` | keep FO(.) in a plain string; format only the structure |
| `𝔹 value expected (ℤ found: 2)` | `x() <= 2` is reverse implication | `=<` |
| `ℤ value expected (Row found: ...)` | `type Row` with no range and no `<: Int` | `type Row <: Int`, or a literal range `type Row := {1..9}` |
| `Domain error: ¬(y() = 0) is not a tautology` | division by a symbol | guard it ([gotchas](../references/gotchas.md#arithmetic)) |
| `IndexError: list index out of range` at parse | redeclared `abs` | rename it |
| `Duplicate declaration of D` | two symbols named alike | rename one |
| `set expected at most 1 argument` | two-variable quantifier under an implication | nest the quantifiers |
| `TypeError` in annotation | `?=n` under an implication or parentheses | put it at the top of a sentence, or use `#{ }` |
| `Can't use function enumeration for predicates` | `p := {0->true}.` | `p := {0}.` |
| every Boolean reads as true | `bool(value)` | `str(value) == "true"` |
| models repeat with the same decisions | a free auxiliary symbol | fix it by an equation or definition |
| an output reads back `None`, or models differ only in an unconstrained symbol | `expand` with the default `complete=False` | `complete=True`, or constrain the symbol ([engine](../references/idp/engine.md)) |
| a sentence with `&`, `\|` and `=>` means something other than intended | precedence: `&` binds tighter than `\|`, which binds tighter than `=>` | parenthesise the parts ([FO(.) syntax](../SKILL.md#fo-syntax)) |
| slow or `unknown`, out of memory | nonlinear product, unbounded `-> Int`, huge quantifier span | [performance lessons](../references/gotchas.md#performance) |
| unlisted facts are free | ground facts written in a theory | put them in a definition `{ ... }` or a structure |
| wrong "optimum" | unbounded objective | bound it; check `lower == upper` ([engine](../references/idp/engine.md)) |
