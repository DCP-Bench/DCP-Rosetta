# Lessons: coins_grid, jacop_java

- Official evaluation (attempt-004, profile instance_count 99, tolerate_inconclusive): accepted at the top level, but 2 of 5 instances skipped on execution_timeout (example, json:4). Checked 3/5 = 60%, below the 80% floor in acceptance.md, so not retained.
- Optimum proof is the bottleneck. The 10x10 example and json:4 do not prove the optimum in 180 s; json:1 to json:3 prove it in 0.1 to 57 s.
- Tried: plain Booleans with the runner's default order (no proof on the example, 180 s); cost-ordered search with IndomainMax (no proof); cost-ordered search with IndomainMin (no proof); row and column cost bounds added on top of the global sum (no proof). Last two runs were run with check, not retained.
- Not tried: a different objective encoding, or a stronger redundant bound than the per-row and per-column cheapest-c sums.
