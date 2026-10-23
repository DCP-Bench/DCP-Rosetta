# jobshop, jacop_java: lessons

- Modelled blind from the brief and the instance JSON. Ragged `jobs_data` (jobs with 2 or 3 tasks) is read by walking the JSONArray; the brief's `unbindable_fields` listing is not a limit for jacop.
- Precedence: start[j][t+1] >= start[j][t] + d, with XplusClteqZ. Machines: pairwise disjunction (one task ends before the other starts), Or of two XplusClteqZ.
- Makespan >= end of every job's last task. Horizon = sum of durations.
- Evaluated: accepted, 4 of 5 instances checked. json:2 is skipped with execution_timeout (optimum not proven in 180 s). This is a performance limit, not a reference or infrastructure limit. 4/5 = 80%, the minimum allowed.
- Tried and not kept:
  - attempt-002: SmallestMin start-time comparator. Worse: json:1 also timed out (3 of 5, below 80%).
  - attempt-003: CumulativeUnary per machine instead of pairwise disjunctions. Same 4 of 5, same json:2 timeout.
