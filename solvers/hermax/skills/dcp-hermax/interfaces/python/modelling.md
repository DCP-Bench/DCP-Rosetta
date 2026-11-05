# hermax in Python: modelling patterns

Entry: [README.md](README.md).

### Derived values

`all_different`, `increasing` and the other container constraints apply to variables, not
to expressions. Give each expression its own `IntVar` and constrain that:

```python
q = m.int_vector("q", n, 0, n - 1)                  # q[i]: the column of the queen in row i
d1 = m.int_vector("d1", n, 0, 2 * n - 2)            # d1[i]: its diagonal, q[i] + i
d2 = m.int_vector("d2", n, 0, 2 * n - 2)            # d2[i]: its anti-diagonal, q[i] - i + n - 1
for i in range(n):
    m &= (d1[i] == q[i] + i)
    m &= (d2[i] == q[i] - i + (n - 1))
# No two queens share a column, a diagonal or an anti-diagonal.
m &= q.all_different()
m &= d1.all_different()
m &= d2.all_different()
```

A plain Python list of `IntVar`s (each with its own domain) becomes a container with
`m.vector(items)`, so `m &= m.vector(items).all_different()` works.

The pattern is checked by the n-queens enumeration in [All solutions](README.md#all-solutions).
No-overlap on a machine is the `cumulative` call in the README table, and
[assets/scheduling](../../assets/python/scheduling/README.md) shows `cumulative` with demands other than 1.
For a machine that runs one task at a time, one ordering Boolean per pair of its tasks,
`(s[a] + d[a] <= s[b]).only_if(o)` and `(s[b] + d[b] <= s[a]).only_if(~o)`, can solve much
faster than `cumulative(..., [1] * k, 1)` (10 s against 84 s on a 10-job, 5-machine job
shop, whichever `cumulative` backend): try both on the data you will solve.

### Linear constraints over integers: write them directly

hermax encodes a weighted sum over `IntVar`s itself, with large coefficients too: write
the equation as the problem states it.

```python
# b, o, m_, a: how many of each fruit are bought, each 1..100
b, o, m_, a = (m.int(name, 1, 100) for name in ("b", "o", "m", "a"))
# A hundred fruits in all, costing exactly 315.00 (prices in hundredths of a cent).
m &= (b + o + m_ + a == 100)
m &= (189 * b + 225 * o + 245 * m_ + 945 * a == 31500)
```

This solves in under a second. Building the integers from Boolean digits, adders or
unary counters by hand is longer, and slower than hermax's own encoding.

### Combining constraints: reify with `.iff`

`|` and `&` between two constraints, and `Literal == constraint`, do not exist. Give each
sub-constraint a Boolean with `.iff`, then combine the Booleans:

```python
r1, r2 = m.bool(), m.bool()          # unnamed auxiliaries never collide
m &= (a + b <= 1).iff(r1)            # a PB constraint
m &= (c != d).iff(r2)                # IntVar != IntVar
m &= (r1 | r2)                       # (a + b <= 1) or (c != d)
```

- Half reification: `(consequent).only_if(condition)`: the condition implies the
  consequent, so `(s[a] + d[a] <= s[b]).only_if(a_first)` says that when `a_first` is true,
  task `a` ends before `b` starts. `lit.implies(pb)` has the same direction. For a
  disjunctive choice, post both sides: `(...).only_if(a_first)` and `(...).only_if(~a_first)`.
- An IntVar compared with a constant is already a `Literal`: `(x <= 3) | (y >= 2)` and
  `(x == 3) & (y == 4)` work directly.
- A soft constraint (pay `w` when it is violated): reify it, `m &= (pb).iff(r)`, and
  `m.obj += w * ~r`.
- Every constraint, including `iv.all_different()`, `bv.exactly_one()`, `m.table(...)` and
  `x.forbid_value(v)`, does nothing until it is posted with `m &=`; a bare call is silently
  dropped.
- Names are unique per model and `bool_vector("x", 2)` reserves `x[0]` and `x[1]`: use
  `m.bool()` with no name for auxiliaries, or unique f-string names (`m.int` needs a name).

### Tables of allowed combinations

`m &= m.table([x, y, z], allowed=rows)` restricts the tuple `(x, y, z)` to the listed rows.
The items may also be Boolean literals, with `True`/`False` in the rows.
When a relation is awkward as arithmetic, compute the rows that satisfy it with a short
Python loop and post them as a table:

```python
# The digits a, b, c, d (1..9, all different) with a/b + c/d == 1, found by enumeration.
rows = [(a, b, c, d) for a, b, c, d in itertools.permutations(range(1, 10), 4)
        if a * d + c * b == b * d]
m &= m.table([da, db, dc, dd], allowed=rows)
```

### Lookups, min/max and products

| Need | Idiom |
|---|---|
| constant list indexed by an IntVar | `m &= ((arr @ i) == y)`; `arr[0]` pairs with `i.lb` |
| cost given per value of an IntVar | `x.piecewise(base_value=cost[x.lb], steps={t: cost[t] for t in range(x.lb + 1, x.ub + 1)})` |
| IntVector element by an IntVar | `m &= (v[k] == z)`, absolute index, `z` an int or IntVar |
| 2-D table lookup | `m &= m.table([r, c, val], allowed=[(i, j, tab[i][j]) for ...])` |
| any other container indexed by an IntVar | `for j: m &= (y == bv[j]).only_if(k == j)` |
| `b * x`, Boolean times IntVar | `p = m.int(..., 0, x.ub); m &= (p == x).only_if(b); m &= (p == 0).only_if(~b)` |
| `x * y`, two IntVars | not supported (`TypeError`); `for k in range(x.lb, x.ub + 1): m &= (p == k * y).only_if(x == k)`, or a table; when `x` is wide, write it in binary digits `x = sum(2**b * bit[b])` and `x * y = sum(2**b * part[b])` with `(part[b] == y).only_if(bit[b])`, `(part[b] == 0).only_if(~bit[b])` |
| `x * x` | `x.piecewise(base_value=x.lb ** 2, steps={k: k * k for k in range(x.lb + 1, x.ub + 1)})` |
| remainder, quotient | `x % k` or `m.modulo(x, k)`; `m.floor_div(x, k)` |
| maximum / minimum | `m.max([a, b])`, `m.min(...)` over IntVars |

`piecewise` steps give the value from that threshold on (not an increment), and it returns a
linear expression usable in constraints and the objective. Plain lists, `BoolVector` and
`IntMatrix` cannot be indexed by an IntVar (`TypeError`); `abs(...)` is not supported (use
two one-sided slacks, below); `m.enum` takes string choices only. Products or squares over
wide domains (about 1000 and up) exhaust memory or time: loop over the smaller factor, and
write a long number as a digit-weighted sum of small IntVars instead of one wide IntVar.

### The objective

`m.obj += expr` adds `expr` to the cost that `solve` minimises; call it several times to
add several terms.

| Direction | Write | Cost |
|---|---|---|
| minimise a total over Booleans | `m.obj += sum(c[i] * x[i] ...)` | `c[i]` for each `x[i]` true |
| maximise a total | `m.obj += -sum(v[i] * x[i] ...)` | minus the total |
| minimise an integer expression | `m.obj += makespan` | its value |
| pay `w` when a literal is false | `m.obj += w * ~lit` | `w` when `lit` is false |
| a cost by cases of an integer | `m.obj += x.piecewise(...)` | the case's value |

`result.cost` is the objective's value, constants included. Give the sum to `m.obj`
directly: tying it to an auxiliary `IntVar` first (`total == sum(...)`, `m.obj += total`)
works, but its encoding costs time (0.16 s against 0.01 s on a 12-by-12 assignment); keep
such a variable only when a bound on it helps. **Never enumerate thresholds**
(`(total >= c)` for every `c`): that posts one pseudo-Boolean encoding per threshold.

A constant added to the objective does not change which solutions are optimal, and
subtracting a lower bound from each cost can make the soft clauses much smaller (see
"Help the solver" in [SKILL.md](../../SKILL.md#modelling)). Keep the reported value on the
original costs.

**Report the problem's value, not `result.cost`.** Whenever what `m.obj` minimises is not
the problem's objective itself (a maximisation, a complement, a shifted cost), keep the
objective as its own expression and read it with `result[...]`; return it beside the
model and the outputs:

```python
profit = sum(v[i] * x[i] for i in range(n)) - fixed_cost   # the problem's objective, maximised
m.obj += -profit                                           # what the solver minimises
...
return m, {"x": x}, profit                                 # result[profit] is the value
```

On every optimum `result.cost` and `result[profit]` agree up to that sign and constant.

An absolute deviation of `S = sum(c_i * x_i)` from a target `T` takes two one-sided slack
integers:

```python
p = m.int("p", 0, S_max - T); n = m.int("n", 0, T)
m &= (p >= S - T)
m &= (n >= T - S)
m.obj += p + n
```

**Sign check:** the objective is always minimised. A maximisation needs the minus sign
(`m.obj += -total`); forgetting it returns the worst selection. Example: maximum-weight
independent set, [assets/maximise](../../assets/python/maximise/README.md).
