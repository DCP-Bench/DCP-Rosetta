# Golomb rulers with Hexaly

Accepted on sizes 5 and 7; sizes 8, 9 and 10 time out with the optimum unproven (FEASIBLE at
180 s). An implied bound on every mark pair (marks[j] - marks[i] >= (j-i)(j-i+1)/2), tried
with `evaluation.check` on size 8 outside an attempt, still timed out at 180 s. Recorded as a
blocker (`optimum_unproven`): Hexaly's bounds from pairwise distinct differences do not close.
The reference was not read.
