"""0/1 knapsack: choose a subset of items whose total weight fits the capacity, maximising the total value.

Prints one optimal selection as {"take": [...]}.
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
    optimizer.param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    optimizer.param.time_limit = 90
    model = optimizer.model
    take = [model.bool() for _ in range(n)]  # take[i]: item i is in the knapsack

    # The total weight does not exceed the capacity
    model.constraint(model.sum(weights[i] * take[i] for i in range(n)) <= capacity)

    # The total value is as large as possible
    total = model.sum(values[i] * take[i] for i in range(n))
    model.maximize(total)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print(f"status {status.name} value {total.value if status in (S.OPTIMAL, S.FEASIBLE) else None} "
          f"bound {optimizer.solution.get_objective_bound(0)}", file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: optimality not proven", file=sys.stderr)
        print(json.dumps({"take": [x.value for x in take]}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no solution found within the time limit", file=sys.stderr)
        sys.exit(1)
