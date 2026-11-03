# facility_location, jacop_java, attempt-001 (retained)

- Accepted by the evaluator on 4 of 5 instances. `json:4` (5 regions, 4 warehouses, `max_shipping` 120) hit `execution_timeout` at 180 s with the optimum not proven. Retained as a performance limit under the 80% rule (4 of 5 checked). The model is evidenced on the `example`, `json:1`, `json:2`, `json:3`.
- Attempt-002 (adds the per-lane link `ships[i][j] <= min(max_shipping, demand_j) * open[i]` and labels open decisions first) still timed out on `json:4`, with the optimum unproven.
- Attempt-003 (same plus lanes labelled cheapest-first with `IndomainMax`) timed out on `json:4` and took 168 s on `json:2`, so it is slower overall. Not retained.
- Likely cause: the bound on the total cost is weak (no LP relaxation in JaCoP), so the branch and bound must enumerate many shipment splits for 20 shipment variables of domain up to 120.
- Restrictions read from the description, by warehouse index in `warehouse_s` order: 0 New York, 1 Los Angeles, 2 Chicago, 3 Atlanta.
