# JuMP (Julia, HiGHS) — Julia, mixed-integer linear programming (linear constraints only)

## Minimal working example (knapsack)
```julia
using JuMP, HiGHS
values, weights, capacity = [6, 10, 12], [1, 2, 3], 5
model = Model(HiGHS.Optimizer)
set_silent(model)
@variable(model, x[1:3], Bin)
@constraint(model, sum(weights[i] * x[i] for i in 1:3) <= capacity)
@objective(model, Max, sum(values[i] * x[i] for i in 1:3))
optimize!(model)
println(round(Int, objective_value(model)), " ", round.(Int, value.(x)))
```

## API
- **Decision variables:** `@variable(model, 0 <= v[1:n, 1:m] <= 9, Int)` (`Bin` binary; omit `Int` for continuous; `@variable(model, b, Bin)` or `@variable(model, b, binary = true)` for a scalar; indices are 1-based; `v[i, :]` slices); give every integer variable finite bounds
- **Logic constraints:** `@constraint(model, b => {e <= k})` (b ⇒ e ≤ k); `@constraint(model, !b => {e >= k})`; plain linear forms over binaries (`a + b <= 1`)
- **Arithmetic constraints:** `@constraint(model, e <= k)` with `<=`, `>=`, `==` only (`<`, `>`, `!=` raise errors: use `<= k - 1`); `@constraint(model, lo <= e <= hi)`; families `@constraint(model, [i = 1:n, j = 1:m], e[i, j] <= 1)`; `sum(v[i] for i in 1:n if cond)`; `@expression(model, ex, e)`; `fix(v, 3; force = true)`; no `abs`, `min`, `max`, `x * y` or `x^2` of variables
- **Other constraints:**
  - extensional: `@constraint(model, [v[1], v[2]] in MOI.Table(rows))` (`rows` a `Float64` matrix, one allowed tuple per row; variables integer with finite bounds)
  - ordering: `@constraint(model, v in MOI.AllDifferent(n))` (v a vector of n integer variables with finite bounds); `@constraint(model, [x, y] in MOI.SOS1([1.0, 2.0]))` (at most one nonzero)
- **Objectives and solving:** `@objective(model, Min, e)` or `Max` (linear; omit for feasibility); `optimize!(model)`; `termination_status(model)` (`OPTIMAL`), `is_solved_and_feasible(model)`; `value(v)` and `value.(v)` return `Float64`: `round(Int, ...)` them; `objective_value(model)`; `set_time_limit_sec(model, 30)`; `set_attribute(model, "mip_rel_gap", 0.0)`

## Modelling
- **Domains:** the tightest integer bounds the data allows (they set the strength of every big-M and of `MOI.Table`/`MOI.AllDifferent`); a choice among few values: binaries `y[i, v]` with `sum(y[i, :]) == 1` and `x[i] == sum(v * y[i, v] for v in vals)`
- **Structure:** assignment and all-different as one-hot binaries with `sum(y[:, v]) <= 1` per value (stronger than `MOI.AllDifferent`, which is bridged to binaries); tour or path: binary arcs only between allowed pairs, one out and one in per node, plus order variables `o[i] - o[j] + n * go[i, j] <= n - 1`; scheduling and disjunctions: a binary per ordering with `s[i] + d[i] <= s[j] + M * (1 - before[i, j])`, `M` as small as the horizon allows
- **Lookups:** weight binaries directly in sums (`sum(c[i][j] * y[i, j] for ...)`); a product of two binaries: `z <= a`, `z <= b`, `z >= a + b - 1`; a binary times a bounded integer: `z <= U * b`, `z <= x`, `z >= x - U * (1 - b)`; `|x - y|` and `max`: extra variables with one inequality per case, exact only when the objective pushes the right way, otherwise a binary picks the case
- **Symmetry:** order interchangeable objects (`o[i] <= o[i + 1] - 1`) and fix the first
- **Implied constraints:** add totals the relaxation cannot infer (sum of capacities ≥ sum of demands, row and column sums of 0/1 grids)

Docs: https://jump.dev/JuMP.jl/stable/
