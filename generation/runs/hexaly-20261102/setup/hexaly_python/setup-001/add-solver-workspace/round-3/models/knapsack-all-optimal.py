"""All optimal 0/1 knapsack selections: every subset of items whose total weight fits the
capacity and whose total value is the largest possible.

First proves the optimum (gap limit 0), then pins the value to it and enumerates the
selections with soft no-goods; a proven minimum of 1 repeat proves the list complete.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
deadline = time.monotonic() + 95  # the whole run must end within 120 s

with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]
n = len(weights)


def time_left():
    return max(1, int(deadline - time.monotonic()))


with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    param.time_limit = time_left()
    model = optimizer.model
    take = [model.bool() for _ in range(n)]  # take[i]: item i is in the knapsack

    # The total weight of the chosen items does not exceed the capacity
    model.constraint(model.sum(weights[i] * take[i] for i in range(n)) <= capacity)

    # The total value is as large as possible
    value = model.sum(values[i] * take[i] for i in range(n))
    model.maximize(value)
    model.close()
    optimizer.solve()
    if optimizer.solution.status != S.OPTIMAL:
        sys.exit(f"optimum not proven: {optimizer.solution.status.name}")
    best = value.value
    print(f"optimum {best}", file=sys.stderr)

    # Keep only selections of the optimal value, then enumerate them with soft no-goods
    model.open()
    model.remove_objective(0)
    model.constraint(value == best)
    repeats = []
    model.minimize(0)
    model.close()
    found, complete = [], False
    while True:
        param.time_limit = time_left()
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break  # time limit with nothing found: no proof either way
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL  # proven: every optimal selection repeats a found one
            break
        selection = [t.value for t in take]
        found.append(selection)
        print(json.dumps({"take": selection}), flush=True)
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[t == v for t, v in zip(take, selection)]))
        model.minimize(model.sum(repeats))
        model.close()

    print(f"solutions {len(found)} complete {complete}", file=sys.stderr)
