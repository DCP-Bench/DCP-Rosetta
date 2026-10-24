# big_bang2, jacop_java, attempt-002

hints.md (coordinator) was used. Counting view: per die a GCC over the faces shifted to 0..11
(GCC over faces 1..12 with a counter for value 0 throws "GCC failure : join domain of x variables
doesn't cover all count variables"), below[v] prefix sums, pairs won = sum with_A[v]*below_B[v]
by XmulYeqZ, >= 19. Faces sorted non-decreasing.
Search matters most. On 40-180 s budgets: faces or counters with SmallestDomain/IndomainRandom
succeeded about 1 run in 3 (random, unreliable); input order with IndomainMin/Max and
SmallestDomain with Min/Max timed out; redundant "above" products (loser view) did not help.
What worked, deterministically (about 25 s including the second solution): label the 60 counters
only, die by die in the order Rock, Scissors, Paper, Lizard, Spock, input order, IndomainMiddle.
