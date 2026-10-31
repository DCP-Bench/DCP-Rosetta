Blind model. Marks as integers, one one-hot difference row per pair (values bounded by C(k+1,2)
for a span of k marks and by the greedy ruler's length), and at most one pair per difference.
Evaluated: 3 of 5 (sizes 5, 7, 8); sizes 10 (example) and 9 (json:2) end with "Optimum not
proven". A local run of size 9 with CBC's log: after 90 s the bound is 43 (optimum 44) but CBC has
no integer solution at all; the gap is in finding rulers, not in the bound.
