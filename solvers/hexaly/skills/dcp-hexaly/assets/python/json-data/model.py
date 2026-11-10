"""Pick one item from each group so the total size fits the capacity; maximise the total size.

Reads a JSON file (first argument, default data.json) with the standard library's json module.
The groups have different lengths, and keys the model does not use are ignored.
"""
import json
import sys

import hexaly.optimizer as hx

with open(sys.argv[1] if len(sys.argv) > 1 else "data.json") as f:
    data = json.load(f)
groups, capacity = data["groups"], data["capacity"]

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 10
    model = optimizer.model
    # choice[g] is the position of the item taken from group g; one array per group
    choice = [model.int(0, len(g) - 1) for g in groups]
    size = [model.at(model.array(g), c) for g, c in zip(groups, choice)]

    # The chosen items fit the capacity
    total = model.sum(size)
    model.constraint(total <= capacity)
    model.maximize(total)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print("Total size:", total.value)
        print("Chosen sizes:", [s.value for s in size])
