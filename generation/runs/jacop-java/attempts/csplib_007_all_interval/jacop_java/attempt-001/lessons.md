# csplib_007_all_interval, jacop_java: lessons

- Evaluated (attempt-001, default search, Alldistinct on x and diffs): accepted on
  4 of 5 instances. json:4 (n=20) is `execution_timeout` (tolerated). 4/5 = 80%
  checked, so retained as a performance limit, not as full coverage.
- attempt-002 labels the diffs first (SmallestDomain, IndomainMin). It still times out
  on n=20 in `check` (180 s), so it was not evaluated or retained.
- Not tried: a stronger encoding for n=20 or a different search. The n=20 case is the
  reason to revisit this pair.
