# lessons: csplib_013 progressive party, jacop_java, attempt-001

- Output convention: `visits[p][b]` is the boat that boat `b` is aboard in period `p`. The brief
  does not say what a host boat's entry is. The model sets `visits[p][h] = h` for every host `h`
  (a host stays aboard itself), and `is_host[h]` is tied to that equality. The evaluator accepted
  this on every checked instance, so the reference uses the same convention.
- Encoding: a Boolean view `occ[p][b][v] <-> (visits[p][b] == v)` lets capacity, revisit and guest
  host checks be plain `LinearInt` sums. Meeting is `Reified(XeqY(...))` per pair and period, with
  `<= 1` over periods.
- Performance: instance `json:8` (12 boats, 5 periods in the data) hit `execution_timeout` at 180 s
  with optimum 5 (`reason: execution_timeout`, `runner_status: timeout`). The other eight instances
  were accepted, the slowest in 16 s. The model is evidenced on 8 of 9 instances, which meets the
  80% rule for retention as a performance limit. A stronger encoding was not tried in this
  attempt; likely candidates are a per-host capacity bound on the guest count, or redundant
  bounds on `hosts`.
