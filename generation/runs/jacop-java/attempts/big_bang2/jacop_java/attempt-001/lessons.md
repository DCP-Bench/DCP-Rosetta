# big_bang2, attempt-001: not retained (search timeout, no solution)

Model: 5 dice x 6 faces in 1..12; each of the ten beats relations as 36 reified XgtY booleans
summed by LinearInt >= 19. Check (2 instances requested, 1 available, solution limit 2) timed out
at 180 s with no solution. Four search variants in scratch also timed out at 180 s:
dice with SmallestDomain + IndomainMiddle, dice with SmallestDomain + IndomainMax, and
reified booleans then dice with IndomainMax or IndomainMin. Not evaluated: evaluate would only
record the same timeout.

Suspected cause: the beats sums give no pruning until most face values are fixed, so the DFS
thrashes. CP-SAT's learning is not available. Not yet tested: an element/cumulative-count encoding.
