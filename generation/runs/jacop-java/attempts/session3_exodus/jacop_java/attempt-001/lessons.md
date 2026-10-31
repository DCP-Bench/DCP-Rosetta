# session3_exodus, jacop_java, attempt 001

- Modelled from the brief only. Labels 1..5 are shared across the four arrays: the same
  label in two arrays is the same child. Ages come from a channel `ageOfLabel[ages[a]-1] = AGE[a]`.
- Element offset: `Element.choose(index, arr, value, offset)` with a 1-based index needs offset 0.
  Offset -1 makes the index 0-based. Probed in the image (`arr[idx]` with offset -1, `arr[idx-1]` with 0).
  With -1 and 1-based labels the first check returned `no_solution` (unsat), which the skill does not warn about.
