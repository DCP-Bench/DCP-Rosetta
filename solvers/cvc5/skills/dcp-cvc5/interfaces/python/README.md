# cvc5 in Python (cvc5.pythonic)

The pip package `cvc5` ships a Z3-style API, `cvc5.pythonic`, over the native solver.
Shared concepts, statuses and strategies: [SKILL.md](../../SKILL.md).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling)
- [Solving](#solving) · [All solutions](#all-solutions) · [Optimisation](#optimisation)
- [Common issues](#common-issues) · [Encodings and performance](encodings.md) · [Further reading](#further-reading)

## Install

```bash
pip install cvc5
python -c "import cvc5; from cvc5 import pythonic; print(cvc5.__version__)"
```

The package is [cvc5 on PyPI](https://pypi.org/project/cvc5/). API details:
[cvc5 Python API, pythonic](https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html).

## Quick start

```python
from cvc5.pythonic import *

x, y = Ints("x y")
s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
if s.check() == sat:
    m = s.model()
    print(m.eval(x, model_completion=True).as_long(), m.eval(y, model_completion=True).as_long())  # 4 3
```

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](../../assets/python/satisfy-magic-square/README.md) | satisfy, `Distinct`, sums | `python model.py` |
| [all-solutions-queens](../../assets/python/all-solutions-queens/README.md) | all solutions, no-goods | `python model.py` |
| [maximise-knapsack](../../assets/python/maximise-knapsack/README.md) | maximise by tightening, JSON data | `python model.py` |
| [minimise-jobshop](../../assets/python/minimise-jobshop/README.md) | no-overlap, minimise | `python model.py` |
| [cumulative-schedule](../../assets/python/cumulative-schedule/README.md) | cumulative by time point | `python model.py` |
| [table-element-lex](../../assets/python/table-element-lex/README.md) | table, element, lex order | `python model.py` |
| [routing-tour](../../assets/python/routing-tour/README.md) | permutation, subtour elimination | `python model.py` |
| [infeasible-pigeonhole](../../assets/python/infeasible-pigeonhole/README.md) | infeasible | `python model.py` |

## Modelling

Full list: [cvc5 pythonic API](https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html)

| Need | API |
|---|---|
| integer variables (no domain: add bounds) | `Int("x")`, `Ints("x y")` or `Ints(["x", "y"])` |
| Boolean variables | `Bool("b")`, `Bools(["b0", "b1"])` |
| all different | `Distinct(xs)`: needs at least two arguments |
| linear sum over integers | `Sum([...])`, Python `sum(...)` also works |
| cardinality, weighted count | `Sum([If(b, w, 0) for b, w in ...]) <= k` (`Sum` over Booleans raises `TypeError`) |
| conditional value | `If(c, a, b)` |
| logic | `And`, `Or`, `Not`, `Implies`, `Xor`; `And`/`Or` need at least two arguments |
| Boolean as an equivalence | `b == (x > 3)` (tested: reifies both ways) |
| maximum / minimum | no `Max`: fold with `If(a > b, a, b)` |
| table (allowed tuples) | `Or([And(x == a, y == b) for a, b in allowed])` |
| element `row[i]` with variable `i` | `If` chain: `If(i == 0, row[0], If(i == 1, row[1], row[2]))` |
| lexicographic `xs <= ys` | recursive: `Or(x0 < y0, And(x0 == y0, lex_le(rest)))` ([table-element-lex](../../assets/python/table-element-lex/README.md)) |
| no-overlap of intervals | pairwise `Or(end_a <= start_b, end_b <= start_a)` ([minimise-jobshop](../../assets/python/minimise-jobshop/README.md)) |
| cumulative resource | per time point `Sum([If(And(s <= t, t < s + d), r, 0), ...]) <= cap` ([cumulative-schedule](../../assets/python/cumulative-schedule/README.md)) |
| circuit / tour | successor variables with `Distinct`, positions with `Implies(succ[i] == j, pos[j] == pos[i] + 1)` ([routing-tour](../../assets/python/routing-tour/README.md)) |
| quantifiers | `ForAll([i], body)`, `Exists([i], body)`; tested on small bounded cases only |

Build constraints with the Python operators; they produce cvc5 terms, not Python booleans.
Pass them to `Solver.add`, as separate arguments: `s.add(c1, c2)` or `s.add(*constraints)`.
A Python list in `add` raises `SMTException` (see [Common issues](#common-issues)).

## Solving

Status: `Solver.check()` returns `sat`, `unsat` or `unknown` (compare with the names `sat`,
`unsat`, `unknown` from the module). `s.reason_unknown()` gives an `UnknownExplanation`,
for example `UnknownExplanation.TIMEOUT`.

| `check()` | Meaning |
|---|---|
| `sat` | a model exists; read it with `s.model()` |
| `unsat` | proven: no model exists |
| `unknown` | undecided; `reason_unknown()` says why (tested: `TIMEOUT`) |

Reading values: `m.eval(x, model_completion=True).as_long()` for integers and
`is_true(m.eval(b, model_completion=True))` for Booleans. `m[x]` also works. `s.model()`
raises `RuntimeError: cannot get value unless after a SAT or UNKNOWN response.` after `unsat`,
so test the status first.

Options: [cvc5 options](https://cvc5.github.io/docs/cvc5-1.4.2/options.html). Set them with `s.set(name, value)`.

| Setting | Effect, as measured |
|---|---|
| `SolverFor("QF_LIA")` | linear integer logic. Faster than a plain `Solver()` on the models in [Performance](encodings.md#performance). Use it for linear models |
| `SolverFor("QF_NIA")` | nonlinear integer logic, needed for products of variables |
| `s.set("tlimit-per", ms)` | time limit per `check()`, in milliseconds; a run stopped by it returns `unknown` / `TIMEOUT` (measured: 60 s limit ended at 60.00 s) |
| `s.set("arith-prop", "none")` | slower on n-queens n=40 (33 s against 13 s); keep the default |
| `s.set("arith-brab", False)` | no measurable change on the tested models |
| `s.set("sat-random-seed", n)` | accepted; effect on speed not measured |
| `incremental`, `produce-models` | accepted; `model()` worked without `produce-models` in testing |

`s.set("timeout", ms)` is rejected (see [Common issues](#common-issues)). Do not set the global
`tlimit` option: it hung in testing. Use `tlimit-per`.

## All solutions

No enumeration call exists. Loop over `check()` and block the assignment of the **decision**
variables only. An auxiliary variable in the no-good gives each solution once per value of
the auxiliary. Example: [all-solutions-queens](../../assets/python/all-solutions-queens/README.md).

```python
solutions = []
while s.check() == sat:
    m = s.model()
    values = [m.eval(v, model_completion=True).as_long() for v in q]
    solutions.append(values)
    s.add(Or([v != x for v, x in zip(q, values)]))
```

Check that the last `check()` returned `unsat`, not `unknown`, before reporting the list as complete.

## Optimisation

Tighten the objective as described in [SKILL.md](../../SKILL.md#optimisation); examples: [maximise-knapsack](../../assets/python/maximise-knapsack/README.md) and [minimise-jobshop](../../assets/python/minimise-jobshop/README.md).

## Common issues

See also the shared table in [SKILL.md](../../SKILL.md#common-issues).

| Symptom | Likely cause | Fix |
|---|---|---|
| `RuntimeError: unrecognized option: timeout.` | `s.set("timeout", ...)` is not a cvc5 option | `s.set("tlimit-per", ms)` |
| `RuntimeError: unrecognized option: <name>.` | misspelt option name | list them with `cvc5.Solver().getOptionNames()` |
| `TypeError: unsupported operand type(s) for +: 'BoolRef' and 'BoolRef'` | `Sum` over Boolean terms | `Sum([If(b, 1, 0) for b in bs])` |
| `NameError: name 'PbEq' is not defined` (also `AtMost`, `AtLeast`, `PbLe`) | no pseudo-Boolean helpers in `cvc5.pythonic` | `Sum([If(b, w, 0) ...]) == k` |
| `NameError: name 'Max' is not defined` | no `Max` | `If`-fold |
| `SMTException: True, False or SMT Boolean expression expected. Received [...] of type <class 'list'>` | a Python list passed to `add` | `s.add(*constraints)` |
| `RuntimeError: invalid kind 'AND', expected Terms with kind AND must have at least 2 children` (`'OR'` likewise) | `And` or `Or` with one argument | pass the constraint directly; `Or([...])` needs two or more |
| `RuntimeError: invalid kind 'DISTINCT', ... must have at least 2 children` | `Distinct` with one argument | skip the constraint when there are fewer than two terms |
| `SMTException: At least one of the arguments must be an SMT expression` | `Distinct([])` | skip the constraint |
| `RuntimeError: LogicInfo::setLogicString(): cannot parse logic string: NOTALOGIC` | unknown logic name in `SolverFor` | use a standard name, e.g. `QF_LIA`, `QF_NIA` |
| `RuntimeError: cannot get value unless after a SAT or UNKNOWN response.` | `model()` read after `unsat` | test `check() == sat` first |
| `RuntimeError: ... solver is already fully initialized` | `s.set(...)` or a logic change after the first `add` | set options and the logic before the first `add` |
| `RuntimeError: A non-linear term was asserted to arithmetic in a linear logic.` | `x * y` under `SolverFor("QF_LIA")` | use `QF_NIA` or the default `Solver()`, or case-split the product |
| `if x == 3:` takes the wrong branch | `==` builds a term; `bool()` on it returned `False` with no error | `s.add(x == 3)`, or test a model value with `is_true(m.eval(...))` |

## Further reading

- cvc5 Python API (pythonic): <https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html>
- cvc5 options: <https://cvc5.github.io/docs/cvc5-1.4.2/options.html>
- cvc5 on PyPI: <https://pypi.org/project/cvc5/>
