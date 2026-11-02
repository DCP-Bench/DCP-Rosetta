# broken_weights attempt-001

Accepted on 2 of 5 instances; on the example (m=40, n=4) and json:2, json:3 Hexaly found no
weights within 180 s (status INFEASIBLE). Attempt-002 adds the implied condition that sorted
pieces weigh every integer up to their total iff each piece is at most 2 * (sum of lighter) + 1,
verified by brute force on the host for every split of m <= 80 into at most 5 pieces
(364274 multisets, no mismatch). The reference was not read.
