attempt-001 with CBC's conflict graph, clique strengthening, feasibility pump and preprocessing
switched off through mip.cbc.cbc_set_parameter. Locally on json:5 that removed the setup time but
CBC then enumerated 32 nodes in 170 s without a solution (each node LP on the 455k-nonzero cover
is slow). In the evaluator json:5 and json:6 still end in memory_limit; 4 of 6 checked (67%),
below the 80% bar. Blocked.
