# session3_farmer_and_cows, jacop_java: lessons

- Modelled blind. Each cow has a son variable (0-based); Reified booleans per (cow, son) feed two LinearInt families: per-son cow count = cows_per_son[k], and per-son milk sum = N(N+1)/2 / sons (weights = cow number).
- attempt-001 (input order labelling) timed out on the example (25 cows) and json:1 (81 cows): 3 of 5, below the 80% floor.
- attempt-002 labels the largest cows first. Example and json:2 to json:4 accepted; json:1 (81 cows, 9 sons) still times out: the performance limit is recorded, 4 of 5 = 80%.
- No symmetry breaking on son labels (not asked for by the description).
