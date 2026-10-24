# tsp / jacop_java, attempt 002

Other integrations' accepted tsp models (choco_java, maxicp_java) were read for this attempt,
as the task allowed. The attempt-001 model (Circuit + Element cost, input-order labelling of the
successor array) timed out on json:2 and json:3.

What made the proof fast: label a rank variable per city (k-th nearest other city) instead of
the successor itself. Next and cost are tied to the rank by two Element constraints over arrays
sorted by distance, so IndomainMin tries the nearest successor first, and the cost lower bound
grows with the rank. Smallest-domain variable order over the ranks. Redundant Alldifferent on
the successors. Result: json:2 in about 24 s, json:3 in about 3 s, the rest under 1 s.
