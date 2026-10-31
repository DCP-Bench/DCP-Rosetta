# lessons: csplib_009 perfect square placement, jacop_java, attempt-001

- Accepted on 5 of 6 instances. `json:6` (base 30, 19 squares) hit `execution_timeout` at 180 s
  (`runner_status: timeout`). 5 of 6 is 83%, so this is retained as a performance limit.
- Attempt-002 added redundant `Cumulative` constraints along x and y (limit = base, resource = side).
  It was also accepted on the same 5 instances and still timed out on `json:6`, so it did not
  help. It was not retained: the simpler model is the one kept.
- The number of squares is the length of `sides` (4 to 21 across the instances), so the output
  shapes follow each instance.
