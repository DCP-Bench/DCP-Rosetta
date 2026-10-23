---
name: hermax
description: Write a DCP-Bench submission for the hermax integration - one Python file defining build(instance) against hermax.model.Model, with any objective declared as soft clauses on model.obj. Use when generating or repairing a model for solver ID hermax.
---

# hermax (MaxSAT) submissions

A submission is one Python file defining `build(instance)`, written against
hermax's own modelling layer:

```python
from hermax.model import Model


def build(instance):
    ...
    return m, outputs
```

Always two values. There is no objective in the return: hermax models carry
their objective on `m.obj`, and the runner reads it off the solve result.

```python
from hermax.model import Model


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    m = Model()
    take = m.bool_vector("take", len(values))
    m &= (sum(weights[j] * take[j] for j in range(len(values))) <= capacity)

    # Maximising the value carried means paying for what is left behind.
    for j, value in enumerate(values):
        m.obj[value] += take[j]
    return m, {"x": take}
```

## The objective is soft clauses

`m.obj[weight] += literal` adds a soft clause that **pays `weight` when the
literal is false**. That polarity is the whole trick:

- **minimise** a total: pay when the literal is *true*, so write `~lit`.
  `m.obj[cost[i][j]] += ~x[i][j]` charges `cost[i][j]` for using pairing
  `(i, j)`.
- **maximise** a total: pay when the literal is *false*, so write the literal
  itself. `m.obj[value] += take[j]` charges for every item left behind, and the
  minimum total forgone is the maximum total taken.

Either way the solver minimises the broken weight, which is what MaxSAT is.

### A linear objective over integers

`m.obj += expression` minimises a linear expression exactly. It accepts
`IntVar`, `Literal` and weighted sums, with negative coefficients and a
constant, and `result.cost` equals the expression's value:

```python
m.obj += sum(cost[i] * x[i] for i in range(n))      # minimise
m.obj += 0 - sum(profit[i] * x[i] for i in range(n))   # maximise: negate with 0 - E
```

Each literal of an `IntVar` becomes one soft unit clause, so this is cheap.
**Never enumerate thresholds** such as `(total >= c)` for every `c`: that posts
one pseudo-Boolean encoding per threshold (29 s to build against 0.01 s for
`m.obj += sum(c*x)` on a six-variable diet model).

Polarity differs between the two forms for a bare `Literal`:
`m.obj[w] += lit` is a soft clause and **maximises** `lit`; `m.obj += lit`,
`m.obj += 5 * lit` and `m.obj[w] += 1 * lit` **minimise** it. `m.obj[w]` takes
a positive integer weight only; put a sign in the expression.
Unary minus is not defined on an `IntVar` or `Literal`; write `0 - x` or
`-1 * x`.

**Absolute deviation** of `S = sum(c_i * x_i)` from a target `T`: two one-sided
slack integers and inequalities, then `m.obj += p + n`:

```python
p = m.int("p", 0, S_max - T); n = m.int("n", 0, T)
m &= (p >= S - T)
m &= (n >= T - S)
m.obj += p + n
```

Avoid the equality form `S - T == p - n` (17 times slower to solve). For one
`IntVar` `x` against a constant `t`, the deviation is a sum of `x`'s own ladder
literals: `m.obj[1] += (x >= k) if k <= t else (x < k)` for each `k` in the
domain beyond `lb`.

## Do not route the objective through an integer variable

Declaring `total = m.int(...)` and tying it with
`m &= (sum(c[j] * x[j] for j in ...) == total)` is the single most expensive
mistake available here. That equality has to be encoded as a pseudo-Boolean
constraint over the full range of the sum.

Measured on a four-by-four assignment problem with costs up to 125: the
soft-clause form builds and solves in **0.21 s**, the auxiliary-variable form
spends **43 s inside `build` alone** before solving starts. Same model, same
answer.

Only introduce an integer objective variable when the brief declares the
objective value as an output. Even then, keep the soft clauses as the objective
and let the variable be tied separately, or narrow its bounds to the values the
sum can actually reach.

## The modelling surface

Constraints are posted with `m &= constraint`. Every constraint, including
`iv.all_different()`, `bv.exactly_one()` and `x.forbid_value(v)`, does nothing
until it is posted this way; a bare call is silently dropped.

| Need | Call |
| --- | --- |
| one Boolean | `m.bool(name)` |
| Booleans | `m.bool_vector(name, n)`, `m.bool_matrix(name, rows, cols)` |
| integers | `m.int(name, lb, ub)`, `m.int_vector(...)`, `m.int_matrix(...)` |
| named choices | `m.enum(name, choices)`, `m.enum_vector(...)` |
| cardinality | `bv.at_most_one()`, `bv.at_least_one()`, `bv.exactly_one()` |
| all-different | `iv.all_different()` |
| ordering | `iv.increasing()`, `iv.lexicographic_less_than(other)` |
| aggregates | `m.sum_var(items)`, `m.max(vec)`, `m.min(vec)`, `iv.running_sum()` |
| value tests | `x == v`, `x != v`, `x.in_range(lo, hi)`, `x.forbid_value(v)` |
| scheduling | `m.interval(...)`, `m.cumulative(starts, durations, demands, cap)` |

## Combining constraints: reify with `.iff`

`|` and `&` between two constraints, and `Literal == constraint`, do not exist.
Give each sub-constraint a Boolean with `.iff`, then combine the Booleans:

```python
r1, r2 = m.bool(), m.bool()          # unnamed auxiliaries never collide
m &= (a + b <= 1).iff(r1)            # a PB constraint
m &= (c == d).iff(r2)                # IntVar == IntVar
m &= (r1 | r2)                       # (a + b <= 1) or (c == d)
```

- `x != y` between two IntVars has no `.iff`; reify the equality and negate it:
  `(x == y).iff(~r)`.
- Half reification: `(consequent).only_if(condition)` means the condition
  implies the consequent, so `(root == s).only_if(x == c)` says `x == c`
  implies `root == s`. `lit.implies(pb)` is the same direction.
- An IntVar compared with a constant is already a `Literal`, so
  `(x <= 3) | (y >= 2)` and `(x == 3) & (y == 4)` work directly.
- `m.obj[w] += (pb)` makes the constraint soft (pays `w` when violated).
- Give auxiliaries no name (`m.bool()`), or a unique f-string name:
  every name is unique per model, and `bool_vector("x", 2)` reserves `x[0]`
  and `x[1]`. `m.int` needs a name string, so use `f"aux_{i}_{j}"`.

## Lookups, min/max and products

| Need | Idiom |
| --- | --- |
| constant list indexed by IntVar | `m &= ((arr @ i) == y)`; `arr[0]` pairs with `i.lb` |
| list value as an expression | `sum(arr[k] * (i == k) for k in range(i.lb, i.ub + 1))` |
| IntVector element by IntVar | `m &= (v[k] == z)`, absolute index, `z` an int or IntVar |
| 2-D table lookup | `m &= m.table([r, c, val], allowed=[(i, j, tab[i][j]) for ...])` |
| anything else indexed by IntVar | `for j: m &= (y == bv[j]).only_if(k == j)` |
| max / min | `m.max(intvars)`, `m.min(intvars)`; tie expressions to IntVars first |
| `x // k`, `x % k` | `m.floor_div(x, k)`, `m.modulo(x, k)` |
| `b * x`, Boolean times IntVar | `p = m.int(..., 0, x.ub); m &= (p == x).only_if(b); m &= (p == 0).only_if(~b)` |
| `x * y`, two IntVars | `for k in range(x.lb, x.ub + 1): m &= (p == k * y).only_if(x == k)` |
| `x * x` | `sum(k * k * (x == k) for k in range(x.lb, x.ub + 1))` |

Products or squares over wide domains (about 1000 and up) exhaust memory or
time: loop over the smaller factor, and write a long number as a digit-weighted
sum of small `IntVar`s instead of one wide `IntVar`.

Plain Python lists, `BoolVector` and `IntMatrix` cannot be indexed by an
IntVar (`TypeError`). `m.enum` takes string choices only; use an IntVar for
integer choices.

## Weighted constraints over integers: channel to bits once

`sum(c[i] * x[i]) <= T` over IntVars with coefficients above about 5 can take
tens of seconds to build and more than a minute with larger coefficients; the
cost lands inside `m &= ...`, before the solve, so `time_limit` does not
bound it. Tie each integer once to binary Booleans and write the weighted
constraint over the bits:

```python
x = m.int_vector("x", n, 0, U)
bits = []
for i in range(n):
    b = m.bool_vector(f"xb{i}", U.bit_length())
    expr = sum(2 ** k * b[k] for k in range(len(b)))
    m &= (x[i] == expr)               # IntVar with lb 0 == Boolean sum: cheap
    bits.append(expr)
m &= (sum(c[i] * bits[i] for i in range(n)) <= T)
```

The same holds for an equality: `189*b + 180*o + 175*g == 15750` over IntVars
never finished building, and over the bits it built in 0.0005 s.
A diet model with coefficients 10 to 400 went from more than 100 s to 0.9 s.
Keep using `x[i]` for the objective, comparisons with constants,
`all_different` and outputs. The cheap `IntVar == weighted Boolean sum` path
needs `lb == 0` and no constant term. An equality with coefficients around
10^8 over several integers stays hard whichever encoding is used.

When the same sum has a constraint and an objective, put the constraint on the
expression (`sum(w*b) <= cap`) and the objective on the expression too; routing
through `W == sum(w*b)` followed by `W <= cap` doubles the solve time, and
adding `W <= value` on top of the fast path is much slower than the inequality
on the expression itself.

A matrix gives `.row(i)`, `.col(j)` and `.flatten()`; the row and column views
carry the cardinality helpers, so `m &= x.row(i).exactly_one()` is the direct
way to say "exactly one per row".

Linear constraints accept ordinary Python sums over variables:
`m &= (sum(w[j] * x[j] for j in range(n)) <= cap)`.

## Outputs

`outputs` maps each name the brief declares to variables of this model. A
vector or matrix can be handed over whole — the runner reads
`result[container]` and gets back nested lists of `bool` or `int`, matching
whichever the brief asked for. Leaves must be `IntVar`, `Literal`, or a sum of them
(`PBExpr`, decoded by `result[...]` since 1.2.9); for a constant use
`m.as_int(c)`, never a plain Python value.

**Take every size from the instance.** The brief shows the shapes of the
*example* instance only. Build the outputs as Python lists sized from the
instance argument (`n = len(instance["durations"])`, then
`m.int_vector("start", n, 0, H)`); other instances have other sizes. A count the problem itself fixes
(for example four traffic roads) stays a constant, even when a list in the
instance varies in length.

Booleans render as `true`/`false`. If the brief declares 0/1 integers, use
`m.int(name, 0, 1)` instead of `m.bool(name)`.

### Outputs too wide for one IntVar

hermax encodes an `IntVar` with literals per value, so an `IntVar` over a
range in the millions is killed at the 2048 MB memory limit before any
constraint is posted. Declare such an output as a **linear expression** of
small variables instead, and return the expression itself:

```python
from hermax.model import Model


def build(instance):
    m = Model()
    digits = m.int_vector("digit", 10, 0, 9)
    number = sum(10 ** (9 - i) * digits[i] for i in range(10))
    m &= digits.all_different()
    m &= (digits[0] >= 1)
    return m, {"number": number}       # a ten-digit int in the output
```

`sum(2 ** k * bits[k] for k in range(K))` over `m.bool_vector("bit", K)` does
the same in binary. The ten-digit model above imports, builds and solves in
0.25 s; a lone `m.int` over the ten-digit range does not fit in 2048 MB.

Such a sum is hermax's own `PBExpr` (a single `c * literal` is a `Term`).
`result[...]` decodes both, so declare the sum as the output. Rules:

- Sum only Booleans, `IntVar`s, and integers derived as `IntVar`s (`m.max`,
  `m.min`, `m.sum_var`). `x // k` stays a `DivExpr` inside the sum, which the
  runner can decode but cannot block when enumerating, so the model fails with
  `solution_limit` above 1. Tie it to an `IntVar` first.
- Coefficients must be integers.
- Constrain the expression with linear comparisons. hermax has no `%` on a
  `PBExpr` or an `IntVar` (`TypeError`), so state divisibility as
  `number == 7 * q` with `q` itself a sum of small variables.

When enumerating, the runner blocks the assignment of every literal and
variable the expression sums. A different combination can give the same total;
the runner skips that repeat rather than reporting it twice, so no symmetry
breaking is needed for correctness.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. Calls `model.solve(time_limit=...)` with whatever budget is left.
3. Treats only `optimum` (with an objective) and `sat` (without one) as an
   answer. `interrupted_sat` means a solution was found without proving it
   best, and is reported as a timeout, never as a result.
4. Emits the solution, then posts a blocking clause over the **declared
   outputs** and solves again. A solution whose declared outputs equal one
   already emitted is skipped, not emitted twice.
5. Stops with `complete` when the cost rises above the first one, which is when
   the optimal solutions are exhausted, or when the model goes `unsat`.

So enumeration covers optimal solutions only, and two submissions that declare
different outputs are blocked differently even for the same problem.

## Reasoning to record

Say which way the soft-clause polarity runs and why, in one line. If an integer
variable appears anywhere near the objective, say what its bounds are and why
they are narrow enough to encode.
