# Lessons: csplib_049_number_partitioning, attempt 2

- Attempt 1 modelled the sum of squares with one `XmulYeqZ` per slot and a `LinearInt` over the
  squares. It was accepted on the example and json:1 but tolerated an `execution_timeout` on
  json:2 (n=16): 2 of 3 instances checked, below the 80% bar. Weak bounds on squares are the cause.
- Attempt 2 keeps one Boolean per value (`inA[v]`) and makes the cardinality, sum and
  sum-of-squares conditions linear over those Booleans. Slots are linked to the Booleans with
  `Reified(XeqC(slot, v))`. It solves all three instances (json:2 included) without a timeout.
- Odd n is not modelled. Every instance is even, and the brief states no solution exists for N < 8.
