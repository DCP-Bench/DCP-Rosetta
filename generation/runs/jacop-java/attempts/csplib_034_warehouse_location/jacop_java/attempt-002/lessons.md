# Lessons: csplib_034_warehouse_location, jacop_java

- `Element.choose(...)` returns a constraint and does not post it. attempt-001 called it bare, so the
  cost and open links were never imposed, and the evaluator rejected it with "Declared outputs cannot
  extend to a reference solution". Fix: `store.impose(Element.choose(...))`. The integration skill and
  the contract examples show `Element.choose` without `impose`.
- attempt-001 was accepted on 4 of 5 instances, with `json:3` skipped on `execution_timeout` (180 s).
  Labelling the default order (open booleans first) was slow there. attempt-002 labels the supplier
  assignment first with `Model.search(assign, null, null)`; `json:3` then solved in about 2.5 s, and all
  5 instances were checked.
- Offset -1 in `Element.choose` gives 0-based indices (checked against the example's optimum of 383 and
  against an independent brute force on the example data; the accepted run matches).
