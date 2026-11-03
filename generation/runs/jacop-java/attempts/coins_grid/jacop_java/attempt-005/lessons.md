hints.md (coordinator's notes) was used for this retry.

Attempt 004 timed out proving the optimum. Fix: one Table per row and per column over the n cells plus a
line-cost variable (tuples = every placement of exactly c coins with its cost), z tied to both the row-cost
sum and the column-cost sum, cells labelled by ascending cost with IndomainMax (coin first). Attempt 004
had a comment saying "coin first" but used IndomainMin. The largest instance takes about 110 s of the
180 s budget; the others take 2-7 s.
