# session1_guards_and_apples, jacop_java, attempt-001

- Reading of the description: the count after the last gate is 1 (the apple given to the girl), so
  `apples[num_gates] = 1`. Each gate gives `a/2 + 1` apples, so `a[i] - 2*a[i+1] = 2`, which also
  makes `a[i]` even. The chain has a single solution (5 gates: 94 apples at the start).
- The description does not say whether the count after the last gate includes the girl's apple;
  this reading is the one that gives the usual puzzle answer. Recorded as an interpretation.
- Accepted on all 5 instances, status `complete` each time.
