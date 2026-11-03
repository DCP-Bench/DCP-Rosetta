# knights_tour, jacop_java, attempt-001

- Model: move numbers `x` plus the inverse `cellAt` (square per move), linked by `Element.choose`
  (offset -1 for 0-based) and a `Table` of knight-move pairs between consecutive moves. Labelling
  `cellAt` in move order with `IndomainMin` finds a path quickly.
- `Element.choose(...)` only returns a constraint: it must be imposed with `store.impose(...)`.
- Evaluation: 4 of 5 instances checked. `json:2` (10x10) hit `execution_timeout` at 180 s with no
  solution. Two repairs were tried on that instance and both still timed out: first-fail
  (`SmallestDomain`) on `cellAt`, random values on `cellAt`, and a redundant `Circuit` over the
  path closed through a dummy node. Warnsdorff-style value ordering would need a custom
  `Indomain`, which this submission cannot supply. Retained as a performance limit under the
  80% rule (acceptance.md); the 10x10 instance is not evidenced.
