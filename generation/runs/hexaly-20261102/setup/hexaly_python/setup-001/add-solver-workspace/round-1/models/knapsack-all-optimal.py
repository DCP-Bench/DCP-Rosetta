"""All optimal 0/1 knapsack selections: every subset of items that fits the capacity and
reaches the largest total value.

First the optimum is proven (gap limit 0). Then the objective is replaced: the total value
is pinned to the optimum and the optimal selections are enumerated with soft no-goods, where
the objective counts how many earlier selections the decisions repeat. A proven minimum of 1
or more proves that every optimal selection has been printed.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
DEADLINE = time.monotonic() + 100  # the whole run must end within 120 s

with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]
n = len(weights)


def time_left():
    return max(1, int(DEADLINE - time.monotonic()))


with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)
    param.time_limit = time_left()
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
    if status != S.OPTIMAL:
        print("optimum not proven:", status.name, file=sys.stderr)
        sys.exit(1)
    best = total.value
    print("optimum:", best, file=sys.stderr)

    # Keep only selections of optimal value, then enumerate them with soft no-goods
    model.open()
    model.remove_objective(0)
    model.constraint(total == best)
    repeats = []
    model.minimize(0)
    model.close()
    count, complete = 0, False
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
            complete = status == S.OPTIMAL  # proven: every optimal selection repeats a printed one
            break
        chosen = [t.value for t in take]
        print(json.dumps({"take": chosen}), flush=True)
        count += 1
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[t == v for t, v in zip(take, chosen)]))
        model.minimize(model.sum(repeats))
        model.close()

    print("optimal selections:", count, "complete:", complete, file=sys.stderr)
