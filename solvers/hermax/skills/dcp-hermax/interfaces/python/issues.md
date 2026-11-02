# hermax in Python: common issues

Entry: [README.md](README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `TypeError: obj[w] is no longer supported` | The `m.obj[w] += lit` form of hermax 1.2 | `m.obj += w * expr` minimises `w * expr`; to pay `w` when `lit` is false, `m.obj += w * ~lit` |
| `FutureWarning: add_soft() is deprecated` | A soft constraint posted with `add_soft` | Reify it, `m &= (constraint).iff(r)`, and `m.obj += w * ~r` |
| `TypeError: Non-linear arithmetic is not supported` | `x * y` between two IntVars | Loop over the smaller factor, `(p == k * y).only_if(x == k)`, or a `table` |
| Model long and slow, built from Boolean digits, adders or comparators | Integer arithmetic encoded by hand | Use `m.int` variables and write the linear constraint directly; hermax encodes it |
| Wide `m.int` over millions, very slow or out of memory | Integers are encoded per value | Keep bounds tight (each variable its own window), or express the value as a sum of small variables: `sum(10**(9-i) * d[i])` over ten 0..9 integers |
| `TypeError: bad operand type for abs()` | `abs` of an expression | Two one-sided slacks, see [The objective](modelling.md#the-objective) |
| `TypeError: Unsupported decode target` on `r[expression]` | A plain Python `int` was returned | Use `m.as_int(c)` for a constant; sums decode directly |
| `TypeError: Clause OR only supports Literal operands` | `|` between a literal and a non-literal, e.g. `(x | y) | False` | Combine only literals with `|`; post the rest as separate `m &=` lines |
| `TypeError: PBConstraint` on `|`, or `Literal == PBConstraint` | A constraint is not a literal | Reify it: `(constraint).iff(r)`, see [Combining constraints](modelling.md#combining-constraints-reify-with-iff); for `DivExpr` use `m.floor_div` |
| A constraint has no effect | `iv.all_different()`, `m.table(...)`, `x.forbid_value(v)` called without `m &=` | Post it: `m &= iv.all_different()` |
| `(consequent).only_if(condition)` has the wrong direction | The condition implies the consequent | Swap the two sides |
| Minimise-colours stalls above the optimum | Interchangeable colour labels | Add prefix symmetry breaking: `used[k+1]` implies `used[k]` |
| Hamiltonian path or tour times out at 8x8 | A position plus channel encoding | One Boolean successor per move, exactly one per square, `(x[d] == x[s] + 1).only_if(nxt)` |
| Tasks overlap or exceed the resource although `m.cumulative(...)` was called | Since 1.3.0 `cumulative` returns its constraint instead of posting it | Post it: `m &= m.cumulative(...)` |
| `ValueError` from `m.scale(x, 0)` | Only a zero factor is rejected; a negative factor flips the domain | Use a nonzero factor |
| `r.ok` is true but the answer is not proven | `interrupted_sat` counts as ok | Test `r.status == "optimum"` |
| `interrupted` with `r.cost` None | Time limit reached before any solution | Raise the limit or simplify the model |
| `r.cost` is None | No objective: a satisfaction problem | Read `r.status == "sat"` instead |
| Maximisation returns the worst selection | The minus sign was left out | `m.obj += -total`: the objective is always minimised |
| Enumeration repeats answers | Auxiliary variables left out of the block, see [All solutions](README.md#all-solutions) | Block only the variables you report, or every variable that changes the answer |
| Enumeration over integer variables finds the same answer again | Blocking only Booleans, or blocking with `==` on whole variables | Block each integer with `q[i] != value` literals OR'd together, as in [All solutions](README.md#all-solutions) |
| `all_different` cannot take `q[i] + i` or other expressions | Constraint applies to variables only | Create `d[i] == q[i] + i` as an `IntVar` and call `all_different()` on the vector, see [Derived values](modelling.md#derived-values) |
| `all_different` on a plain list of IntVars | Only containers have the method | `m.vector(items).all_different()` |
| Tasks overlap on one machine in a job-shop | No no-overlap constraint posted; precedence alone does not stop overlap | One `m &= m.cumulative(starts, durations, [1] * len(starts), 1)` per machine, or one ordering Boolean per pair with `(s[a] + d[a] <= s[b]).only_if(o)` and `(s[b] + d[b] <= s[a]).only_if(~o)` |
| Need a linear equation with a sum on both sides | Assumed to need a constant right-hand side | `m &= (sum(a) == sum(b))` works, as in the cryptarithm `SEND + MORE = MONEY` model with `10**k` weights |
| `r[matrix]` shape unclear | Result nesting is not stated | `r[matrix]` returns a list of row lists with the same shape; `r[x[j]]` reads one row, `[[r[s[j][k]] for k in range(K[j])] for j in range(J)]` builds a ragged table |
