# flip_rows_cols, jacop_java, attempt-001

- Labelling the row flips first (27 booleans, then 9) timed out at 180 s on the example with no optimum proven.
  Labelling the 9 column flips first, then the row flips, proves the optimum in about 1 s on the example.
  Fixing the columns makes each row's sign independent, so the row constraints and the objective prune early.
- The cell flags are `y[i][j] = (f[i] != g[j])`, reified with `XneqY`. The total is `plainTotal - 2 * sum(v * y)`.
