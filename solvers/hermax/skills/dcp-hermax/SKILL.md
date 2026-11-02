---
name: dcp-hermax
description: hermax is a MaxSAT modelling library (hermax.model.Model over PySAT) with Boolean and integer variables, native linear, pseudo-Boolean, table and scheduling constraints, a minimised objective compiled to weighted soft clauses, and solution enumeration. Python binding (pip package hermax). Use when writing, debugging or explaining hermax models or MaxSAT-style optimisation, or when the user has chosen hermax.
license: Apache-2.0
compatibility: Python binding - Python 3 with pip (tested with Python 3.12.11 and hermax 1.3.0, which installs python-sat); no licence key or account needed
metadata:
  domain: constraint-programming
  solver: hermax
  paradigm: maxsat
  interfaces: "python"
---

# hermax (MaxSAT)

hermax models are built with `hermax.model.Model`. Hard constraints are posted with
`m &= constraint`. The objective is always **minimised**: `m.obj += expr` adds an expression
(a literal, an `IntVar`, a weighted sum, a `piecewise` cost) that hermax compiles to weighted
soft clauses, and `solve` minimises their total. `m.obj += w * lit` pays `w` when `lit` is
true; to maximise, minimise the negation (`m.obj += -expr`). The `m.obj[w] += lit` form of
hermax 1.2 raises `TypeError` since 1.3.0.

## Pick an interface

Read this file and the interface below.

| | Python |
|---|---|
| Read | [interfaces/python/README.md](interfaces/python/README.md) |
| Package | `hermax` (`hermax.model`) |

Other bindings are not covered yet.

## Contents
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Further reading](#further-reading)

## Modelling

Boolean and integer variables, hard constraints (linear and pseudo-Boolean sums,
cardinality, all-different, `table`, `cumulative`, half-reified `only_if`) and a minimised
objective. Exact calls, patterns and pitfalls are in the interface file. Full list:
[API reference](https://hermax.readthedocs.io/en/latest/api.html).

**Say it with hermax's own constraints.** hermax encodes integer arithmetic, weighted sums
and comparisons itself, and picks the encoding. A model is shorter, and usually faster,
when it states the arithmetic directly instead of building it from Booleans:

- integers are `m.int` variables with linear constraints over them
  (`m &= (189 * b + 225 * o == 31500)`), not hand-built binary digits, adders, comparators
  or unary counters;
- each integer gets its own tightest domain (`m.int(name, earliest[i], latest[i])`), not
  one domain shared by all and then narrowed with constraints;
- an ordering that holds only when a Boolean is true is one half-reified comparison,
  `m &= (start_a + duration_a <= start_b).only_if(a_first)`, not a loop over thresholds;
- a cost that depends on an integer's value through a formula or table is
  `x.piecewise(base_value=..., steps={t: value_from_t_on})`, and a long sum of expressions
  is `sum_expr(...)`;
- a relation that is awkward as arithmetic (products of digits, a property checked by a
  program) can be a `m.table([...], allowed=rows)` over the rows a short loop enumerates
  beforehand.

**Help the solver.** Constraints that follow from the problem but are not needed for
correctness can shorten the search a lot: a counting argument (when pieces fill a board
exactly, every row and column of the board is filled exactly), a symmetry break between
interchangeable objects, a bound on the objective. The objective may also be shifted by
a constant without changing which solutions are optimal: when every solution pays for a
fixed quantity `q_j` of item `j` (an equality, not an at-least), and `c_j` is its cheapest
unit cost, subtract `c_j` from each of `j`'s unit costs and add the constant
`sum(c_j * q_j)` back, so the soft clauses only weigh what is above the minimum. With an
at-least constraint the shift is not a constant; when extra units only add cost, an optimal
solution meets the quantity exactly, so the equality can be posted first. Report the value
computed from the original costs.

**Readable models.** Write for a student reading the model for the first time, in the
words of the problem statement, not of the API:

- a docstring or opening comment that states the problem in a sentence or two;
- a comment on each input field, saying what it holds (`weights[i]: the weight of item i`);
- a comment on each decision variable, saying what it means (`x[i] is true when item i is packed`);
- a comment on each group of constraints and on the objective;
- the plainest expression that says it: `sum(weights[i] * x[i] for i in ...)` for a
  weighted sum, `m.bool_vector`/`m.int_vector` for families of variables, and the native
  constraints above rather than encodings.

For example:

```python
values = [6, 10, 12]   # values[i]: the value of item i
weights = [1, 2, 3]    # weights[i]: the weight of item i
capacity = 5           # the most weight the backpack can carry

m = Model()
# x[i] is true when the hiker packs item i
x = m.bool_vector("x", len(values))

# The packed items weigh no more than the backpack can carry.
m &= (sum(weights[i] * x[i] for i in range(len(x))) <= capacity)
# Pack the most valuable selection.
m.obj += -sum(values[i] * x[i] for i in range(len(x)))
```

## Solving

| Status | Meaning |
|---|---|
| `sat` | satisfiable (the model has no objective) |
| `optimum` | proven optimal (the model has an objective) |
| `unsat` | proven: no solution |
| `interrupted_sat` | a solution found, optimality not proven (time limit) |
| `interrupted` | time limit reached, no solution |
| `unknown` | the backend gave no verdict |
| `error` | the solve failed |

`result.cost` is the minimised objective's value, constant included, so a maximisation
written as `m.obj += -expr` reports `-expr`'s value. `result.ok` is true for `sat`,
`optimum` and `interrupted_sat`.

## All solutions

Enumeration is by blocking clauses: solve, forbid exactly the answer found (over the
variables you report), and solve again until the status is no longer `sat`. All optimal
solutions: solve for the optimum, record the cost, then block each optimal answer and
re-solve while the status is `optimum` and the cost is unchanged. Code: the interface file.

## Further reading

- Documentation: [hermax.readthedocs.io](https://hermax.readthedocs.io/en/latest/)
- Quick start and modelling guide: [quickstart](https://hermax.readthedocs.io/en/latest/quickstart.html), [modeling](https://hermax.readthedocs.io/en/latest/modeling.html)
- API reference: [api](https://hermax.readthedocs.io/en/latest/api.html)
- Solver backends: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html), [incremental](https://hermax.readthedocs.io/en/latest/incremental.html)
- Runnable examples: [satisfy](assets/python/satisfy/README.md), [all-solutions](assets/python/all-solutions/README.md), [all-optimal](assets/python/all-optimal/README.md), [maximise](assets/python/maximise/README.md), [minimise](assets/python/minimise/README.md), [infeasible](assets/python/infeasible/README.md), [scheduling](assets/python/scheduling/README.md)
- Examples: [examples](https://hermax.readthedocs.io/en/latest/examples.html) (UWrMaxSAT, RC2, graph colouring, scheduling)
