# equal_sized_groups, jacop_java, attempt 001

Accepted on 5 of 5 instances, first attempt. Non-obvious points:

- Target size: the brief says "round(N/K)" without saying how halves round. The model uses
  `Math.rint` (half to even, like Python's `round`). The evaluator accepted it on all instances.
- Break points: a break point is only valid where the value changes (`a[p] != a[p+1]`, 1-based).
  Posted as a unary `Table` over each break point with the valid positions as tuples.
- Groups are non-empty and in order (`XltY` chain with the fixed endpoints 0 and N). The brief
  does not say whether empty groups are allowed; strict order was accepted.
- Group error `|size - target|` is built with `LinearInt` for the deviation and `AbsXeqY` for the
  absolute value, then `SumInt` into the objective. `SumInt` takes an `IntVar` right-hand side.
