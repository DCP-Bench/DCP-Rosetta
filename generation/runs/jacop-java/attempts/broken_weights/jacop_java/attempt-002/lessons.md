# broken_weights, jacop_java: lessons

- attempt-001 (one signed-choice variable per piece and value, XmulYeqZ products) was
  `execution_timeout` on the example (n=4, m=40). Labelling the choice variables was
  the cost. attempt-002 replaces it with a reachability DP over Element lookups, which
  propagates; all 5 instances accepted.
- The output is ordered: pieces are increasing, so one solution per multiset. Without
  that, permutations of the same pieces are distinct solutions and the reference set
  does not contain them.
- Reference not opened: the model was written from the brief and the instance notes.
