# Exact in Python: patterns

Back to [the Python page](README.md).

## Patterns

### Indicators for "takes value v"

Exact reasons about linear constraints. Anything that talks about a variable *taking a
particular value* needs one 0/1 variable per value, linked to the integer variable.

| Want | Build |
|---|---|
| `y[v] == 1` exactly when `x == v` | `sum_v y[v] == 1` and `sum_v v*y[v] - x == 0` |
| all different over a domain | for each value, the indicators of all variables for that value sum to `<= 1` (to `== 1` when every value must be used) |
| count of variables taking `v` | linear sum of the indicators for `v` |
| "colour k is used" | a 0/1 `used_k` with `x[v][k] - used_k <= 0` for every node `v`; the objective is the sum of the `used_k` |

Build indicators only for the variables that need them, and keep their domains tight:
this is the one place where a wide domain costs.

Worked examples: [assets/assign-distinct](../../assets/python/assign-distinct/README.md) (all-different
over a small domain), [assets/graph-colouring](../../assets/python/graph-colouring/README.md) (node by
colour, used-colour objective), and [assets/cryptarithm](../../assets/python/cryptarithm/README.md)
(one digit indicator per letter, all letters different, a sum written in place values).

### No-overlap (scheduling)

Two tasks on one machine must not overlap. For each pair, one of two orders holds; each
order is a reified condition, and at least one must be true:

```python
solver.addVariable(a_first, 0, 1)
solver.addVariable(b_first, 0, 1)
# a_first <-> start_b - start_a >= duration_a
solver.addReification(a_first, True, [(1, start_b), (-1, start_a)], dur_a)
# b_first <-> start_a - start_b >= duration_b
solver.addReification(b_first, True, [(1, start_a), (-1, start_b)], dur_b)
solver.addConstraint([(1, a_first), (1, b_first)], True, 1)        # one of the orders
```

Start times get bounds `0..horizon`, with the horizon set to the sum of all durations
(a valid bound). Precedence inside a job is `start_next - start_prev >= duration_prev`. The
makespan is one variable with `makespan - start_k >= duration_k` for every task, minimised.
Full models: [assets/job-shop](../../assets/python/job-shop/README.md) (six jobs, six machines, the
ft06 benchmark) and [assets/task-schedule](../../assets/python/task-schedule/README.md) (release times).

### Encodings

`addVariable(name, lb, ub, encoding)` takes `"log"` (default), `"order"` or `"onehot"`.
Any other string raises `ValueError`. The encoding is a choice of internal representation
of the same domain; measure on your model before changing it. For a wide domain with no
per-value needs, keep the default.
