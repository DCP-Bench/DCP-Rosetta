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

cost = [4, 1, 3, 2]     # cost[i]: the price of item i

m = Model()
# pick[i] is true when item i is bought
pick = m.bool_vector("pick", len(cost))

# Buy exactly two items.
m &= (sum(pick[i] for i in range(len(cost))) == 2)
# Spend as little as possible.
m.obj += sum(cost[i] * pick[i] for i in range(len(cost)))

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
print("picked:", [i for i in range(len(cost)) if r[pick[i]]])
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
| linear constraint, over Booleans or integers | `m &= (sum(w[j] * x[j] for j in range(n)) <= cap)`, any integer coefficients |
| constraint only when a Boolean holds | `m &= (s[a] + d[a] <= s[b]).only_if(a_first)` (half reification) |
| allowed combinations | [`m.table([x, y, z], allowed=rows)`](https://hermax.readthedocs.io/en/latest/api.html) |
| cost by cases of an integer's value | [`x.piecewise(base_value=v0, steps={t: v_t})`](https://hermax.readthedocs.io/en/latest/api.html), value `v_t` from `x >= t` on |
| long sum of expressions | `sum_expr(exprs)` (`from hermax.model import sum_expr`) |
| remainder / quotient | `x % k`, [`m.modulo(x, k)`](https://hermax.readthedocs.io/en/latest/api.html); [`m.floor_div(x, k)`](https://hermax.readthedocs.io/en/latest/api.html) |
| row / column of a matrix | [`x.row(i)`, `x.col(j)`](https://hermax.readthedocs.io/en/latest/api.html) |
| min / max / sum of variables | [`m.min`, `m.max`, `m.sum_var`](https://hermax.readthedocs.io/en/latest/api.html) |
| scheduling resource | [`m &= m.cumulative(starts, durations, demands, capacity)`](https://hermax.readthedocs.io/en/latest/api.html) |
| no two tasks overlap on one machine | `m &= m.cumulative(starts, durations, [1] * len(starts), 1)` per machine, or a Boolean per pair with `(s[a] + d[a] <= s[b]).only_if(o)` and `(s[b] + d[b] <= s[a]).only_if(~o)` |
| all different over expressions | auxiliary `IntVar`s, see [Derived values](modelling.md#derived-values) |
| equality between two sums | `m &= (sum(...) == sum(...))`, both sides may be sums |
| minimise / maximise | [`m.obj += expr`](https://hermax.readthedocs.io/en/latest/modeling.html) / `m.obj += -expr`, see [modelling.md](modelling.md#the-objective) |
| reading values | `r[var]`; `r[vector]` is a list, `r[matrix]` a list of row lists of the same shape |
| the objective's value | `r[objective]` on the problem's own expression; `r.cost` is what was minimised (the negation, for a maximisation), see [modelling.md](modelling.md#the-objective) |

`cumulative` returns its constraint like every other one (since 1.3.0): a call without
`m &=` is silently dropped.


More patterns (derived values, reification, lookups, weighted sums, the objective): [modelling.md](modelling.md).

## Solving

Status values: [Quick start](https://hermax.readthedocs.io/en/latest/quickstart.html) ·
Portfolio and time limits: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html)

The status values and their meaning are in [SKILL.md](../../SKILL.md#solving).


`solve(time_limit=seconds)` bounds the run. `result.backend` names the solver that ran.
`sat_solver_name`, `maxsat_backend` and `backend` select the engines; the defaults are
`"g4"` (Glucose 4, for a model without objective), `"coretrail"` (for a model with one)
and `"auto"`.

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
