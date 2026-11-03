# Z3 in Python (z3-solver)

The Python API of Z3, shipped in the `z3-solver` wheel. What holds in every interface (statuses,
no global constraints, enumeration strategy) is in [SKILL.md](../SKILL.md).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Program interface](#program-interface)
- [Readable models](#readable-models)
- [Common issues](#common-issues)
- Runnable examples: `../assets/python/<example>/`, one folder per pattern (table under Quick start)

## Install

```bash
pip install z3-solver
python -c "import z3; print(z3.get_version_string())"
```

Details: [Z3 guide, logic introduction](https://microsoft.github.io/z3guide/docs/logic/intro/)

## Quick start

```python
import z3

x, y = z3.Ints("x y")
solver = z3.Solver()
solver.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
if solver.check() == z3.sat:
    model = solver.model()
    print(model[x], model[y])  # 4 3
else:
    print(solver.check())
```

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](../assets/python/satisfy-magic-square/README.md) | satisfy, `Distinct`, sums | `python3 model.py` |
| [all-solutions-subset-sum](../assets/python/all-solutions-subset-sum/README.md) | all solutions, blocking clause | `python3 model.py` |
| [all-optimal-partition](../assets/python/all-optimal-partition/README.md) | all optimal solutions | `python3 model.py` |
| [maximise-workshop](../assets/python/maximise-workshop/README.md) | maximise | `python3 model.py` |
| [minimise-rental](../assets/python/minimise-rental/README.md) | minimise | `python3 model.py` |
| [infeasible-shifts](../assets/python/infeasible-shifts/README.md) | infeasible | `python3 model.py` |
| [schedule-single-machine](../assets/python/schedule-single-machine/README.md) | scheduling | `python3 model.py` |
| [minimise-colours](../assets/python/minimise-colours/README.md) | minimise the number of distinct values | `python3 model.py` |

## Modelling

Full list: [Python API reference](https://z3prover.github.io/api/html/namespacez3py.html)

| Need | API |
|---|---|
| integer variables (no domain: add bounds) | [`z3.Int`, `z3.Ints`](https://z3prover.github.io/api/html/namespacez3py.html) |
| Boolean variables | [`z3.Bool`, `z3.Bools`](https://z3prover.github.io/api/html/namespacez3py.html) |
| lists of variables | [`z3.IntVector`, `z3.BoolVector`](https://z3prover.github.io/api/html/namespacez3py.html) |
| all different | [`z3.Distinct(xs)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| sum, product, absolute value | [`z3.Sum`, `z3.Product`, `z3.Abs`](https://z3prover.github.io/api/html/namespacez3py.html) (Python `sum(xs)` also works, giving `0 + x + y`) |
| conditional value | [`z3.If(c, a, b)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| logic | [`z3.And`, `z3.Or`, `z3.Not`, `z3.Implies`, `z3.Xor`](https://z3prover.github.io/api/html/namespacez3py.html) |
| exactly / at most / at least *k* true | [`z3.PbEq(pairs, k)`, `z3.AtMost(*bs, k)`, `z3.AtLeast(*bs, k)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| weighted cardinality | [`z3.PbLe`, `z3.PbGe`, `z3.PbEq`](https://z3prover.github.io/api/html/namespacez3py.html) with `[(b, w), ...]` |
| Boolean as 0/1 in arithmetic | `z3.If(b, 1, 0)` |
| count of a value in a list | `z3.Sum([z3.If(x == v, 1, 0) for x in xs])` |
| number of distinct values used (e.g. colours) | one Boolean per candidate value `used[v] == z3.Or([x == v for x in xs])`, then minimise `z3.Sum` of the `used` flags; do not bound the largest value, because values need not be contiguous ([minimise-colours](../assets/python/minimise-colours/README.md)) |
| maximum / minimum | no built-in: `functools.reduce(lambda a, b: z3.If(a > b, a, b), xs)` (min: `<`) |
| index an array by a variable | [`z3.Array`, `z3.Select`](https://z3prover.github.io/api/html/namespacez3py.html): constrain `arr[k] == v` for each constant `k`, then `z3.Select(arr, i)`; or an `If` chain |
| index a matrix by variables | flatten: `z3.Select(flat, i * width + j)` with `flat[i*width+j]` tied to each constant cell |
| no-overlap of intervals (scheduling) | pairwise `z3.Or(end_a <= start_b, end_b <= start_a)`; no `NoOverlap` or `Cumulative` exists |

Build constraints with the Python operators (`<=`, `+`, `==`); they produce Z3 expressions,
not Python booleans. Pass them to `Solver.add` or `Optimize.add`.

**Scheduling.** Use the pairwise `z3.Or` no-overlap by default: it needs no constant. Big-M
(`start_b >= end_a - M * b` with a Boolean ordering `b`) needs an `M` above every start time;
the sum of all durations is safe, a fixed one such as `10**6` may not be. Both solved a 36-task
job-shop in under a second on one CPU; measure before using big-M at larger scale.

## Solving

Status: [`Solver.check`](https://z3prover.github.io/api/html/classz3py_1_1_solver.html) ·
[`Optimize`](https://z3prover.github.io/api/html/classz3py_1_1_optimize.html)

| Result of `check()` | Meaning |
|---|---|
| `z3.sat` | a model exists; read it with `model()` |
| `z3.unsat` | proven: no model exists |
| `z3.unknown` | undecided; `reason_unknown()` says why, e.g. `"timeout"` |

Use `Solver` for satisfiability and `Optimize` for `minimize` / `maximize`. An `Optimize`
returns a handle from `minimize(expr)`; after `check() == z3.sat`, `upper(handle)` is the
best value found and `lower(handle)` the proven bound. The optimum is proven when both are
the same finite integer; an unbounded objective shows `-1*oo` or `oo`.

`upper(handle)` and `lower(handle)` return Z3 numerals, not Python ints: print them, or
convert with `.as_long()` (an `AttributeError` on `oo` means the bound is infinite). The
model from `optimizer.model()` is the solution behind `upper` after `sat`; when `lower` equals
`upper` it is an **optimal** assignment, and the model from a run stopped by timeout is only the
best found. Check `lower == upper` before reporting the model as optimal.

Reading values: `model[x]`, or `model.eval(e, model_completion=True)` for any expression,
then `.as_long()` for integers and `z3.is_true(...)` for Booleans. `model()` raises
`Z3Exception: model is not available` unless the last `check()` returned `sat`.

Parameters: `solver.set("timeout", ms)` works on `Solver` and on `Optimize`; `solver.set("random_seed", n)`
is accepted on `Solver` ([Solver](https://z3prover.github.io/api/html/classz3py_1_1_solver.html),
[Optimize](https://z3prover.github.io/api/html/classz3py_1_1_optimize.html)).

Errors: Python-level mistakes raise `z3.Z3Exception` or `AttributeError` at the call site,
with a traceback on stderr. A wrong answer is not an error; check results against the model.

## All solutions

Z3 has no enumeration call: loop over `check()` and block each assignment of the
**decision** variables. Auxiliary variables (intermediate sums, makespans) must stay out
of the blocking clause, or each solution appears once per auxiliary value.

```python
while solver.check() == z3.sat:
    model = solver.model()
    values = [z3.is_true(model.eval(b, model_completion=True)) for b in decision]
    solutions.append(values)
    solver.add(z3.Or([b != v for b, v in zip(decision, values)]))
```

All **optimal** solutions: solve with `Optimize` and take `best = upper(handle).as_long()`,
then enumerate on a plain `Solver` with the same constraints plus `objective == best`.
Example: [all-optimal-partition](../assets/python/all-optimal-partition/README.md).

## Program interface

A model program that reads its data from a JSON file indexes the keys it needs by name, so
extra keys in the file do no harm. Report `unsat` and `unknown` as outcomes, not crashes:
Z3 signals them through `check()`, never through an exception.

```python
import json
import sys

import z3

with open(sys.argv[1]) as f:
    data = json.load(f)
n_nodes, edges = data["n_nodes"], data["edges"]  # other keys in the file are ignored

colour = [z3.Int(f"c{i}") for i in range(n_nodes)]
solver = z3.Solver()
solver.add([z3.And(c >= 0, c < 3) for c in colour])
solver.add([colour[a] != colour[b] for a, b in edges])

result = solver.check()
if result == z3.sat:
    model = solver.model()
    print([model.eval(c, model_completion=True).as_long() for c in colour])
elif result == z3.unsat:
    print("no 3-colouring exists")
else:
    sys.exit(f"undecided: {solver.reason_unknown()}")
```

Print the values from the model (`.as_long()`, `z3.is_true`), not the raw `model()`, whose
order and format are Z3's own. `sys.exit("message")` prints the message to stderr and exits
with status 1.

## Readable models

Write for a student reading the model for the first time, in the words of the problem
statement, not of the API:

- a docstring that states the problem in a sentence or two;
- a comment on each input field, saying what it holds (`weights[i]: the weight of item i`);
- a comment on each decision variable, saying what it means (`x[i] is true when item i is packed`);
- a comment on each group of constraints and on the objective;
- the plainest expression that says it (`z3.Sum([z3.If(xi, w, 0) for w, xi in zip(weights, x)])`
  over index arithmetic), and variables kept as lists or nested lists so they print as a whole.

Build the model in one function that creates the solver, adds the constraints with
`solver.add(...)` and returns the solver with the variables to print. Use a `z3.Solver` for a
satisfaction problem and a `z3.Optimize` for an optimisation problem, and set its one objective
with `solver.minimize(expr)` or `solver.maximize(expr)`. For example:

```python
def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    solver = z3.Optimize()

    # x[i] is true when the hiker packs item i
    x = [z3.Bool(f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    solver.add(z3.Sum([z3.If(xi, w, 0) for w, xi in zip(weights, x)]) <= capacity)

    # Pack the most valuable selection.
    solver.maximize(z3.Sum([z3.If(xi, v, 0) for v, xi in zip(values, x)]))

    return solver, {"x": x}
```

Print the values with `model.eval(e, model_completion=True)`; `numpy.vectorize` applies it
to a nested list in one call. It fails on a plain Python integer or Boolean, so give a fixed
value to print as `z3.IntVal(...)` or `z3.BoolVal(...)`.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Z3Exception: Symbolic expressions cannot be cast to concrete Boolean values` | Python `max`, `min`, `any` or `all` applied to Z3 expressions | `z3.Or` / `z3.And`; `If`-reduce for max and min (see [Modelling](#modelling)) |
| `AttributeError: module 'z3' has no attribute 'Max'` (also `Min`, `Element`, `AllDifferent`) | no such global in Z3 | `Distinct`; `If`-reduce; `Select` |
| `if x == 3:` takes the wrong branch, or never fires | `==` builds an expression; for a symbolic `x` it is `False` in Python | put it in a constraint (`solver.add(x == 3)`) or test a model value with `z3.is_true(model.eval(...))` |
| Result differs from Python for negative `/` or `%` | Z3 `div` and `mod` are Euclidean: `7 / -2 = -3`, `7 % -2 = 1`; Python gives `-4`, `-1` | constrain quotient and remainder explicitly (`7 == q * d + r`, `0 <= r < abs(d)`) |
| `check()` returns `unknown`, `reason_unknown()` is `timeout` | unbounded integers, products of two variables, large `Distinct` over derived expressions | add the bounds the problem implies; linearise; raise `timeout`; reformulate |
| optimum never proven: `lower` and `upper` differ or are infinite | objective unbounded, or search stopped early | bound the variables the objective depends on; raise the timeout |
| `Z3Exception: model is not available` | `model()` read after `unsat` or `unknown` | test `check() == z3.sat` first |
| enumeration repeats a solution | auxiliary variables included in the blocking clause | block only the decision variables |
| a value prints as `1/3` | `z3.Real` sort | use `z3.Int` for integer answers, or `.as_fraction()` |
| program breaks on a data file with extra keys | the code iterates over the JSON dict or passes it whole to Z3 | index the keys the model needs by name (`data["edges"]`); ignore the rest |
| program ends with no useful message | the reason is in a traceback on stderr, or was never printed | print the `check()` result and `reason_unknown()`; treat `unsat` as an answer, not an error |
| `AttributeError: 'ArithRef' object has no attribute 'as_long'` on an objective bound | `upper` or `lower` is `oo` or `-1*oo` (unbounded), not a numeral | bound the objective; report unbounded explicitly |
| minimising colours or groups counts the largest value, not the number used | `max + 1` is not the number of distinct values when values are not contiguous | one `used` flag per value, sum the flags ([Modelling](#modelling)) |
| big-M schedule gives wrong or infeasible answers | `M` too small: it cuts off valid schedules; too large: weak relaxation | use the pairwise `z3.Or` no-overlap; see [Modelling](#modelling) |

