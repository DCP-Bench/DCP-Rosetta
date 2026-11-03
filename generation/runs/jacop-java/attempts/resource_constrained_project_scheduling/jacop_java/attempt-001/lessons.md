# resource_constrained_project_scheduling, jacop_java: lessons

- Modelled blind from the brief and the instance JSON. Sink job (last index) start is the makespan; minimise it.
- Cumulative in JaCoP rejects zero durations and zero needs (CumulativePrimary condition errors). Zero-duration source and sink, and jobs needing none of a resource, are left out of that resource's Cumulative.
- Evaluated: accepted, 4 of 5 instances checked. json:3 is skipped with execution_timeout (optimum not proven in 180 s). Performance limit, 4/5 = 80%.
- Not repaired within this batch; a search or propagation change for json:3 is the next thing to try.
