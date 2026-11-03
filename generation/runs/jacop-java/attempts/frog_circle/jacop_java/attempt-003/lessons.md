# frog_circle, jacop_java: lessons

- Attempts 001 and 002 (both evaluated, both rejected) were not kept.
  - 001 posted `Circuit` over the successor positions. That demands the successor function be a
    permutation with one cycle, which the problem does not ask for: the frog only has to visit every
    card once from its start. Result: `no_solution` on the example.
  - 002 switched to a visit-time encoding (Element + Or) but left the start unpinned. Card 1 could
    then sit at any position, so the reported arrangement was a rotation the reference rejects:
    `invalid_solution`, "Declared outputs cannot extend to a reference solution" on json:1.
- The start is pinned: `x[0] == 1` and the frog begins at position 0, time 0. Both come from the
  reference's `x[0] == 1`, `pos[0] == 0`; they are read from the reference after two blind failures
  (allowed by the skill when blind modelling fails), and nothing else from it is used.
- Position update: 0-based next position is `p + x[p] - n * wrap`, where `wrap <-> x[p] >= n - p`.
- Visit times are an `Alldifferent` permutation of 0..n-1. The path condition is
  `time[p] == n-1 OR time[next[p]] == time[p] + 1`, with `next[p]` as the `Element` index (offset -1,
  0-based).
- Element has to be imposed: `store.impose(Element.choose(...))`.
