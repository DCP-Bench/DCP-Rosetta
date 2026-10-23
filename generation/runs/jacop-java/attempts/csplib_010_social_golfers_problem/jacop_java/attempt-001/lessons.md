# Lessons: csplib_010_social_golfers_problem, attempt-001

- The first model (no explicit search) timed out on the example (180 s, no solution). Labelling
  the assignment variables first (`Model.search(order, null, null)`, week by week) brought the
  example and json:1 to about 2 s. The pair-meeting Booleans are decided by propagation once the
  assignments are fixed, so the search does not branch on them.
- json:4 (5 groups of 3, 6 weeks) is a performance limit: no solution within 180 s. Two variants
  did not change this: labelling golfer-major, and the redundant "each golfer has group_size-1
  mates per week" constraint. Smallest-domain comparator on the assignments was worse (example
  timed out). Breaking the group-label symmetry would likely fix it but the description does not
  ask for it, so it was not added.
- Accepted with 7 of 8 instances checked (json:4 skipped, execution_timeout). Retained as a
  performance limit under the 80% rule.
