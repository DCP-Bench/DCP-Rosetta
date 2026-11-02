"""0/1 knapsack: choose items whose total weight fits the capacity, maximising the total value.

Boolean take decisions with linear sums, so Hexaly's bound can prove the optimum (gap limit 0).
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]
n = len(weights)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 90
    model = optimizer.model
    take = [model.bool() for _ in range(n)]  # take[i]: item i is chosen

    # The total weight of the chosen items does not exceed the capacity
    model.constraint(model.sum(weights[i] * take[i] for i in range(n)) <= capacity)

    # The total value is as large as possible
    total = model.sum(values[i] * take[i] for i in range(n))
    model.maximize(total)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("status:", status.name, file=sys.stderr)
    if status == S.OPTIMAL:
        print(json.dumps({"take": [t.value for t in take]}))
        print("value:", total.value, file=sys.stderr)
    elif status == S.FEASIBLE:
        # best found, not proven optimal
        print(json.dumps({"take": [t.value for t in take], "status": "feasible"}))
        print("value:", total.value, "bound:", optimizer.solution.get_objective_bound(0), file=sys.stderr)
