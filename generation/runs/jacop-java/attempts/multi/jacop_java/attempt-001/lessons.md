# multi, jacop_java, attempt-001 (retained)

- Accepted by the evaluator on 4 of 5 instances (example, json:1 optimum 279 as the note says, json:2, json:3). `json:4` (3 origins, 4 destinations, 3 products) hit `execution_timeout` at 180 s with the optimum unproven. Retained as a performance limit under the 80% rule.
- Attempt-002 splits the objective per destination and product, with a lower bound of demand times the cheapest rate. Still times out on `json:4`.
- Attempt-003 is attempt-002 with cheapest lanes labelled first at `IndomainMax`. Still times out on `json:4`. Not retained.
- Likely cause: JaCoP's branch and bound on 36 shipment variables with weak bounds; no LP relaxation.
