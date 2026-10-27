# hermax in Python (hermax.model)

`hermax.model.Model` over PySAT, installed with `pip install hermax`. Shared concepts, statuses and
enumeration strategy: [SKILL.md](../../SKILL.md). Further pages: [modelling patterns](modelling.md) ·
[common issues](issues.md) · [all signatures](../../references/python/model-api.md).

## Install

```bash
pip install hermax
python3 -c "import hermax.model; print('hermax ok')"
```

Apache-2.0, no key. Details: [Quick start](https://hermax.readthedocs.io/en/latest/quickstart.html)

## Quick start

```python
from hermax.model import Model

COST = [4, 1, 3, 2]           # price of each item
m = Model()
pick = m.bool_vector("pick", len(COST))
m &= (sum(pick[i] for i in range(len(COST))) == 2)   # choose exactly two
for i, c in enumerate(COST):
    m.obj[c] += ~pick[i]      # pay c when item i is picked

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
print("picked:", [i for i in range(len(COST)) if r[pick[i]]])
print("total cost:", r.cost)  # picked: [1, 3], total cost: 3
```

## Modelling

Full list: [API reference](https://hermax.readthedocs.io/en/latest/api.html) ·
[Modelling guide](https://hermax.readthedocs.io/en/latest/modeling.html) ·
[all signatures](../../references/python/model-api.md)

| Need | API |
|---|---|
| one Boolean / vector / matrix | [`m.bool`, `m.bool_vector`, `m.bool_matrix`](https://hermax.readthedocs.io/en/latest/api.html) |
| integer / vector / matrix | [`m.int`, `m.int_vector`, `m.int_matrix`](https://hermax.readthedocs.io/en/latest/api.html) |
| at most / exactly one | [`bv.at_most_one()`, `bv.exactly_one()`](https://hermax.readthedocs.io/en/latest/api.html) |
| all different | [`iv.all_different()`](https://hermax.readthedocs.io/en/latest/api.html) |
| ordering | [`iv.increasing()`, `iv.lexicographic_less_than(other)`](https://hermax.readthedocs.io/en/latest/api.html) |
| linear constraint | `m &= (sum(w[j] * x[j] for j in range(n)) <= cap)` |
| row / column of a matrix | [`x.row(i)`, `x.col(j)`](https://hermax.readthedocs.io/en/latest/api.html) |
| min / max / sum of variables | [`m.min`, `m.max`, `m.sum_var`](https://hermax.readthedocs.io/en/latest/api.html) |
| integer quotient | [`m.floor_div(x, k)`](https://hermax.readthedocs.io/en/latest/api.html) (not `x // k`) |
| scheduling resource | [`m.cumulative(starts, durations, demands, capacity)`](https://hermax.readthedocs.io/en/latest/api.html), adds its own constraint |
| no two tasks overlap on one machine | `m.cumulative(starts, durations, [1] * len(starts), 1)`, one call per machine |
| all different over expressions | auxiliary `IntVar`s, see [Derived values](modelling.md#derived-values) |
| equality between two sums | `m &= (sum(...) == sum(...))`, both sides may be sums |
| minimise / maximise | [`m.obj[w] += literal`](https://hermax.readthedocs.io/en/latest/modeling.html), see below |
| reading values | `r[var]`; `r[vector]` is a list, `r[matrix]` a list of row lists of the same shape |

`cumulative` is not wrapped in `m &=`: it posts its constraint directly.


More patterns (derived values, reification, lookups, weighted sums, the objective): [modelling.md](modelling.md).

## Solving

Status values: [Quick start](https://hermax.readthedocs.io/en/latest/quickstart.html) ·
Portfolio and time limits: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html)

The status values and their meaning are in [SKILL.md](../../SKILL.md#solving).


`solve(time_limit=seconds)` enforces a budget through the portfolio backend, a little
slower on easy models (3.15 s against 1.81 s on a 4x4 assignment) but the only way to bound
the run. `result.backend` names the solver that ran. `sat_solver_name`, `maxsat_backend`
and `backend` select the engines; the defaults are `"g4"`, `"rc2"` and `"auto"`.

Errors: Python exceptions (`TypeError`, `ValueError`) are raised at the line that
posts or reads the offending expression, so read the traceback's last line. A solve
problem appears in `r.status`, not as an exception.


## All solutions

Enumeration is by blocking clauses. Block only the variables you want to count:

```python
solutions = []
while True:
    r = m.solve()
    if r.status != "sat":                      # "unsat": no more solutions
        break
    chosen = tuple(bool(r[v]) for v in pick)
    solutions.append(chosen)
    block = None
    for var, value in zip(pick, chosen):       # forbid exactly this assignment
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block
```

Example: [assets/all-solutions](../../assets/python/all-solutions/README.md) (subsets of 1..6 summing to 7).

For **integer** decision variables, block each value with a `!=` literal and OR the
literals together. Build the block from literals only:

```python
solutions = []
while True:
    r = m.solve()
    if r.status != "sat":
        break
    cols = [r[q[i]] for i in range(n)]
    solutions.append(cols)
    block = None
    for i in range(n):
        lit = q[i] != cols[i]          # a Literal: "q[i] differs from this value"
        block = lit if block is None else (block | lit)
    m &= block
```

Example: n-queens with `d1`/`d2` from [Derived values](modelling.md#derived-values) gives 4 solutions
for n = 6 and 92 for n = 8.

| Pitfall | Effect |
|---|---|
| Auxiliary variable left out of the block | Each answer is repeated for every value of the free auxiliary variable (two free Booleans give 4 answers for 2 real ones) |
| Blocking on a derived integer (`x // k`) | Cannot be expressed as a clause; use `floor_div` and block its `IntVar` |

## All optimal solutions

Solve for the optimum, record `cost`, then block each optimal answer and re-solve. The
solver is incremental, so each re-solve returns the next-best answer. Stop when the status
is no longer `optimum` or the cost rises above the first one:

```python
r = m.solve(); best = r.cost; optimal = []
while r.status == "optimum" and r.cost == best:
    chosen = [bool(r[t]) for t in take]
    optimal.append(chosen)
    block = None
    for var, value in zip(take, chosen):
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block
    r = m.solve()
```

Example: [assets/all-optimal](../../assets/python/all-optimal/README.md) (minimum vertex covers).


Common issues: [issues.md](issues.md).
