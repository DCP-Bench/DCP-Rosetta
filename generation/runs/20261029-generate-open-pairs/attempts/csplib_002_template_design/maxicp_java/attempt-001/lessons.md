Blind model, after reading the lessons of 20261016-maxicp-java-models (json:2: the root bound
ceil(3665/9) = 408 is the optimum, but DFS never reached a 408 plan). Templates hold exactly
n_slots copies, coverage is sum_t production*layout >= demand, with the implied identity
"items printed = n_slots * sheets" and the derived bounds sheets >= ceil(total demand / n_slots)
and production[t] <= largest demand (cutting a template's sheets to that keeps every demand met).
The search guide that made it work: registered Booleans b_k = not(total <= LB + k), k = 0.., so
firstFailBinary (0 first) explores "at most LB sheets" before LB + 1, and so on; no value of the
objective is excluded. Both instances prove the optimum and find two plans in under 1 s.
