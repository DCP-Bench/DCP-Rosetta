# hermax in Python: modelling patterns

Entry: [README.md](README.md).

### Derived values

`all_different`, `increasing` and the other container constraints apply to variables, not
to expressions. Give each expression its own `IntVar` and constrain that:

```python
q = m.int_vector("q", n, 0, n - 1)                  # queen column per row
d1 = m.int_vector("d1", n, 0, 2 * n - 2)            # diagonal id q[i] + i
d2 = m.int_vector("d2", n, 0, 2 * n - 2)            # anti-diagonal id q[i] - i + (n - 1)
m &= q.all_different()
for i in range(n):
    m &= (d1[i] == q[i] + i)
    m &= (d2[i] == q[i] - i + (n - 1))
m &= d1.all_different()
m &= d2.all_different()
```

The pattern is checked by the n-queens enumeration in [All solutions](README.md#all-solutions).
No-overlap on a machine is the `cumulative` call in the table above, and
[assets/scheduling](../../assets/python/scheduling/README.md) shows `cumulative` with demands other than 1.

### Combining constraints: reify with `.iff`

`|` and `&` between two constraints, and `Literal == constraint`, do not exist. Give each
sub-constraint a Boolean with `.iff`, then combine the Booleans:

```python
r1, r2 = m.bool(), m.bool()          # unnamed auxiliaries never collide
m &= (a + b <= 1).iff(r1)            # a PB constraint
m &= (c == d).iff(r2)                # IntVar == IntVar
m &= (r1 | r2)                       # (a + b <= 1) or (c == d)
```

- `x != y` between two IntVars has no `.iff`: reify the equality and negate it,
  `(x == y).iff(~r)`.
- Half reification: `(consequent).only_if(condition)`: the condition implies the consequent,
  so `(root == s).only_if(x == c)` says `x == c` implies `root == s`. `lit.implies(pb)` has
  the same direction.
- An IntVar compared with a constant is already a `Literal`: `(x <= 3) | (y >= 2)` and
  `(x == 3) & (y == 4)` work directly.
- `m.obj[w] += (pb)` makes the constraint soft (pays `w` when violated).
- Every constraint, including `iv.all_different()`, `bv.exactly_one()` and
  `x.forbid_value(v)`, does nothing until it is posted with `m &=`; a bare call is silently
  dropped.
- Names are unique per model and `bool_vector("x", 2)` reserves `x[0]` and `x[1]`: use
  `m.bool()` with no name for auxiliaries, or unique f-string names (`m.int` needs a name).

### Lookups, min/max and products

| Need | Idiom |
|---|---|
| constant list indexed by an IntVar | `m &= ((arr @ i) == y)`; `arr[0]` pairs with `i.lb` |
| list value as an expression | `sum(arr[k] * (i == k) for k in range(i.lb, i.ub + 1))` |
| IntVector element by an IntVar | `m &= (v[k] == z)`, absolute index, `z` an int or IntVar |
| 2-D table lookup | `m &= m.table([r, c, val], allowed=[(i, j, tab[i][j]) for ...])` |
| any other container indexed by an IntVar | `for j: m &= (y == bv[j]).only_if(k == j)` |
| `b * x`, Boolean times IntVar | `p = m.int(..., 0, x.ub); m &= (p == x).only_if(b); m &= (p == 0).only_if(~b)` |
| `x * y`, two IntVars | `for k in range(x.lb, x.ub + 1): m &= (p == k * y).only_if(x == k)` |
| `x * x` | `sum(k * k * (x == k) for k in range(x.lb, x.ub + 1))` |

Plain lists, `BoolVector` and `IntMatrix` cannot be indexed by an IntVar (`TypeError`);
`m.max`/`m.min` take IntVars only, so tie expressions to IntVars first; `m.enum` takes
string choices only. Products or squares over wide domains (about 1000 and up) exhaust
memory or time: loop over the smaller factor, and write a long number as a digit-weighted
sum of small IntVars instead of one wide IntVar.

### Weighted constraints over integers: channel to bits once

`sum(c[i] * x[i]) <= T` (or `==`) over IntVars with coefficients above about 5 can take
tens of seconds to build and more than a minute with larger coefficients, and the cost
lands inside `m &= ...`, so `time_limit` does not bound it (`189*b + 180*o + 175*g == 15750`
never finished building). Tie each integer once to binary Booleans and write the weighted
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

A diet model with coefficients 10 to 400 went from over 100 s to 0.9 s, and the equality
over bits above built in 0.0005 s. Keep using `x[i]` for comparisons with constants,
`all_different` and outputs; a wide IntVar in the *objective* is still costly, so use the
bit sums there too. The cheap path needs `lb == 0` and no constant term. Put a
constraint and its objective on the same expression (`sum(w*b) <= cap`) instead of routing
through `W == sum(w*b)`; the detour doubles the solve time. An equality with coefficients
around 10^8 over several integers stays hard whichever encoding is used.

### The objective is soft clauses

| Direction | Write | Cost paid |
|---|---|---|
| minimise a total | `m.obj[c] += ~x` | `c` when `x` is true (the thing is used) |
| maximise a total | `m.obj[v] += x` | `v` when `x` is false (the thing is left out) |
| any integer expression | `m.obj += expr` | its value, e.g. `m.obj += makespan` |
| maximise an expression | `m.obj += 0 - expr` | the negated value (`-x` on a bare `IntVar` is a `TypeError`) |

For a maximisation the solver minimises the **forgone** weight, so the objective is
`sum(all weights) - r.cost`. Keep the objective as soft clauses where you can: a weighted
sum tied to an integer variable is far slower (see [Common issues](issues.md)).

`m.obj += sum(c[i] * x[i] ...)` over Booleans or IntVars is a cheap, exact linear
objective (each literal becomes one unit soft clause, negative coefficients and a constant
are allowed, and `r.cost` is the expression's value). **Never enumerate thresholds**
(`(total >= c)` for every `c`): that posts one pseudo-Boolean encoding per threshold
(29 s to build, against 0.01 s for `m.obj += sum(c*x)`, on a six-variable diet model).
For a bare `Literal` the two forms have opposite polarity: `m.obj[w] += lit` is a soft
clause and **maximises** `lit`, while `m.obj += lit` and `m.obj[w] += 1 * lit` **minimise**
it. `m.obj[w]` takes a positive integer only; put a sign in the expression.

An absolute deviation of `S = sum(c_i * x_i)` from a target `T` takes two one-sided slack
integers, not an equality (`S - T == p - n` was 17 times slower to solve):

```python
p = m.int("p", 0, S_max - T); n = m.int("n", 0, T)
m &= (p >= S - T)
m &= (n >= T - S)
m.obj += p + n
```

**Sign check:** minimise uses `~x` (pays when `x` is chosen), maximise uses plain `x`
(pays when `x` is left out). Copying `~x` from the minimise row into a maximisation makes
the solver minimise the value and return the worst selection. Example: maximum-weight independent set,
[assets/maximise](../../assets/python/maximise/README.md), uses `m.obj[w] += pick[i]`.

