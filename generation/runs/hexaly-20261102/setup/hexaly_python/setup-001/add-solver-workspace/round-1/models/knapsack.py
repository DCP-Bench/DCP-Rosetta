"""0/1 knapsack: choose items whose total weight fits the capacity, maximise the total value."""
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
    optimizer.param.time_limit = 60
    model = optimizer.model
    take = [model.bool() for _ in range(n)]

    # The total weight of the chosen items does not exceed the capacity
    model.constraint(model.sum(weights[i] * take[i] for i in range(n)) <= capacity)

    # The total value is as large as possible
    total = model.sum(values[i] * take[i] for i in range(n))
    model.maximize(total)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("status:", status.name, "value:", total.value if status in (S.OPTIMAL, S.FEASIBLE) else None,
          "bound:", optimizer.solution.get_objective_bound(0), file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        print(json.dumps({"take": [t.value for t in take]}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
