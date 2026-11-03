# sudoku, jacop_java, attempt-002

- attempt-001 used `Alldistinct` for rows, columns and boxes. Its evaluation was `invalid_solution`
  with "Declared outputs cannot extend to a reference solution" at `--solution-limit 2`. Its first
  solution was a valid sudoku matching the clues, but the second solution the runner enumerated broke
  the rules. With `--solution-limit 1` the same model was accepted. Evidence: `attempt-001/` check
  output in the scratchpad. The cause is likely `Alldistinct` misbehaving during enumeration in
  JaCoP 4.10 (not confirmed beyond this).
- attempt-002 writes every all-different group as pairwise `XneqY`. Accepted on all 5 instances,
  status `complete`, one solution each (the puzzles are unique).
- Lesson for the integration: enumeration after the first solution can expose a global constraint
  that is wrong after restart. A pairwise decomposition avoided it here. Worth a runner-level check
  with `solution-limit 2` on a known-unique puzzle.
