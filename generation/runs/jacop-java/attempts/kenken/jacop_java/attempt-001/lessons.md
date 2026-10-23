# kenken, attempt 001

- The brief lists `problem` under `unbindable_fields`. For jacop it binds: each cage is
  `[target, [[r, c], ...]]` with 1-based cells, read by its own length.
- The instance gives no operation per cage. The description says the operation is "yet another
  unknown", so the model accepts a cage when one option holds: sum or product for any size, and
  for two cells also the difference (either order) or the quotient (either order). This reading
  was accepted by the evaluator on all five instances (`accepted`, `instances_checked` 5 of 5).
  Record the interpretation here; the brief does not state it.
