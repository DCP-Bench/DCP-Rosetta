# hermax in Python: common issues

Entry: [README.md](README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Build takes tens of seconds; objective is a weighted sum | Objective tied to an integer through `sum(c * x) == total` | Use `m.obj[c] += ~x` soft clauses. On a random 4x4 assignment with costs up to 125 the soft form solved in 0.01 s; the tied form did not finish in five minutes |
| Wide `m.int` over millions, very slow or out of memory | Integers are encoded per value | Keep bounds tight, or express the value as a sum of small variables: `sum(10**(9-i) * d[i])` over ten 0..9 integers solved at once (an all-different ten-digit number) |
| `TypeError: unsupported operand ... for %` | No `%` on `IntVar` or `PBExpr` | `q = m.floor_div(x, k)` and `x == k * q + r` with `0 <= r < k` |
| `TypeError: Unsupported decode target` on `r[expression]` | A plain Python `int` was returned, or hermax is older than 1.2.9 (a `PBExpr` or `Term` decodes from 1.2.9) | Use `m.as_int(c)` for a constant; sums decode directly |
| `TypeError: Clause OR only supports Literal operands` | `|` between a literal and a non-literal, e.g. `(x | y) | False` | Combine only literals with `|`; post the rest as separate `m &=` lines |
| `TypeError: PBConstraint` on `|`, or `Literal == PBConstraint` | A constraint is not a literal | Reify it: `(constraint).iff(r)`, see [Combining constraints](modelling.md#combining-constraints-reify-with-iff); for `DivExpr` use `m.floor_div` |
| `DeferredClauseGroup` cannot be OR-ed with a Literal | `x != v` on an IntVar | Write `~(x == v)` |
| A constraint has no effect | `iv.all_different()`, `x.forbid_value(v)` called without `m &=` | Post it: `m &= iv.all_different()` |
| `(consequent).only_if(condition)` has the wrong direction | The condition implies the consequent | Swap the two sides |
| Minimise-colours stalls above the optimum | Interchangeable colour labels | Add prefix symmetry breaking: `used[k+1]` implies `used[k]` |
| Hamiltonian path or tour times out at 8x8 | A position plus channel encoding | One Boolean successor per move, exactly one per square, `(x[d] == x[s] + 1).only_if(nxt)` |
| `TypeError: Expected Literal, Clause, or ClauseGroup` | `m &= m.cumulative(...)` | Call `m.cumulative(...)` on its own line |
| `ValueError` from `m.scale(x, 0)` | Only a zero factor is rejected; a negative factor flips the domain | Use a nonzero factor |
| `r.ok` is true but the answer is not proven | `interrupted_sat` counts as ok | Test `r.status == "optimum"` |
| `interrupted` with `r.cost` None | Time limit reached before any solution | Raise the limit or simplify the model |
| Maximise reports a small "cost" | `cost` is the forgone weight | Report `sum(weights) - r.cost` |
| `r.cost` is None | No soft clauses: a satisfaction problem | Read `r.status == "sat"` instead |
| Enumeration repeats answers | Auxiliary variables left out of the block, see [All solutions](README.md#all-solutions) | Block only the variables you report, or every variable that changes the answer |
| Enumeration over integer variables finds the same answer again | Blocking only Booleans, or blocking with `==` on whole variables | Block each integer with `q[i] != value` literals OR'd together, as in [All solutions](README.md#all-solutions) |
| Maximisation returns the worst selection (value minimised) | `~x` copied from the minimise row into `m.obj[v] += ~x` | Maximise with the plain literal: `m.obj[v] += x` pays `v` when `x` is false |
| `all_different` cannot take `q[i] + i` or other expressions | Constraint applies to variables only | Create `d[i] == q[i] + i` as an `IntVar` and call `all_different()` on the vector, see [Derived values](modelling.md#derived-values) |
| Tasks overlap on one machine in a job-shop | No no-overlap constraint posted; precedence alone does not stop overlap | One `m.cumulative(starts, durations, [1] * len(starts), 1)` per machine (ft06 reaches optimum 55 this way) |
| Need a linear equation with a sum on both sides | Assumed to need a constant right-hand side | `m &= (sum(a) == sum(b))` works, as in the cryptarithm `SEND + MORE = MONEY` model with `10**k` weights |
| `r[matrix]` shape unclear | Result nesting is not stated | `r[matrix]` returns a list of row lists with the same shape; `r[x[j]]` reads one row, `[[r[s[j][k]] for k in range(K[j])] for j in range(J)]` builds a ragged table |

