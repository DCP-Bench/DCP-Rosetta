# covering_opl: a CPMpy model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python covering_opl.py covering_opl.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    nb_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]              # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]    # qualified[t]: the workers who can perform task t, numbered from 1

    # workers[i] is true when worker i is hired
    workers = cp.boolvar(shape=nb_workers, name="workers")
    # total_cost is the hiring cost of all hired workers, at most the cost of hiring everyone
    total_cost = cp.intvar(0, sum(cost), name="total_cost")

    model = cp.Model()
    # total_cost adds up the costs of the hired workers.
    model.add(total_cost == cp.sum(workers * cost))
    # Every task is performed by at least one hired worker who is qualified for it.
    for task_workers in qualified:
        model.add(cp.sum(workers[np.array(task_workers) - 1]) >= 1)
    # Hire at the lowest cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "workers": workers}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
