# csplib_002_template_design, jacop_java, attempt-002

hints.md (coordinator) was used. The failure of attempt-001 came from posting `sum layout[t] <= n_slots`.
Posting full templates (sum == n_slots, as the reference does) gives
`sum_v copies[t][v] == n_slots * production[t]`, a lower bound ceil(total demand / n_slots) on the
total, the implied bound `sum_t copies[t][v] <= n_slots*total - (totalDemand - demand[v])`, and a
non-increasing production order. Layout cells in input order with IndomainMin, then production.
Both instances (2 and 3 templates) check in about 15 s total including the optimum proof.
production lower bound is 1 (as the reference), valid because templates are full.
