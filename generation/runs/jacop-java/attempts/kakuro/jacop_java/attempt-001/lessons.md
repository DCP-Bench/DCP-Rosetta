# kakuro, attempt 001

- The brief lists `problem` under `unbindable_fields`. For jacop it binds: each clue is a JSON
  array `[sum, [r, c], ...]` with 1-based cells, and the runner's JSONArray walk reads the ragged
  entries by their own length. Brief gap to report.
- `blanks` is the list of cells printed as 0 (the black cells), not the white cells the name
  suggests. The 36 white cells are exactly the cells covered by the clue entries. A first attempt
  took `blanks` as the white cells and was unsatisfiable on the example (`no_solution`, status
  `unsat`, seen with `evaluation.check`). The fix was made before `evaluate` ran, so this attempt is
  the one evaluated.
