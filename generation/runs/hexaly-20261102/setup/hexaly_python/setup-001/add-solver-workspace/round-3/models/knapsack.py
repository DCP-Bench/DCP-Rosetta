"""0/1 knapsack: choose items whose total weight fits the capacity, maximising the total value.

Prints one optimal selection as {"take": [...]} once Hexaly proves it optimal (gap limit 0).
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
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    param.time_limit = 60
    model = optimizer.model
    take = [model.bool() for _ in range(n)]  # take[i]: item i is in the knapsack

    # The total weight of the chosen items does not exceed the capacity
    model.constraint(model.sum(weights[i] * take[i] for i in range(n)) <= capacity)

    # The total value is as large as possible
    value = model.sum(values[i] * take[i] for i in range(n))
    model.maximize(value)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: best found, optimality not proven", file=sys.stderr)
        print(json.dumps({"take": [t.value for t in take]}))
        print(f"status {status.name} value {value.value}", file=sys.stderr)
    else:
        print(f"no solution found: {status.name}", file=sys.stderr)
