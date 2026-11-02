"""All optimal 0/1 knapsack selections: every subset of items whose total weight fits the
capacity and whose total value is the largest possible.

First proves the optimum (gap limit 0), then pins the value to it and enumerates the selections
with soft no-goods; a proven minimum of 1 repeated solution means none is missing.
Prints each optimal selection as {"take": [...]} on its own line.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
DEADLINE = time.monotonic() + 95


def time_left():
    return int(DEADLINE - time.monotonic())


with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]
n = len(weights)

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    param.time_limit = max(1, time_left())
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
    if status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
        sys.exit(0)
    if status != S.OPTIMAL:
        print(f"optimum not proven: {status.name}", file=sys.stderr)
        sys.exit(1)
    best = total.value
    print(f"optimum {best}", file=sys.stderr)

    # Keep only selections reaching the optimum, then enumerate them with soft no-goods:
    # the objective counts the earlier solutions the decisions repeat.
    model.open()
    model.remove_objective(0)
    model.constraint(total == best)
    repeats = []
    model.minimize(0)
    model.close()
    found, complete = 0, False
    while True:
        left = time_left()
        if left < 1:
            break
        param.time_limit = left
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break  # time limit with nothing found: no proof either way
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL  # proven: every remaining solution repeats a found one
            break
        chosen = [x.value for x in take]
        print(json.dumps({"take": chosen}), flush=True)
        found += 1
        model.open()
        model.remove_objective(0)
        # Selections can contain one another, so the no-good fixes every item, taken or not
        repeats.append(model.and_(*[x == v for x, v in zip(take, chosen)]))
        model.minimize(model.sum(repeats))
        model.close()

    print(f"solutions {found} complete {complete}", file=sys.stderr)
