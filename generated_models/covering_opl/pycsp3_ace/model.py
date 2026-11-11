# covering_opl: a PyCSP3 model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python covering_opl.py covering_opl.json

from pycsp3 import *


def create_model(instance):
    """Select a set of workers to perform all the tasks, while minimizing the cost. Each
    worker can perform certain tasks and has a hiring cost. Ensure that all tasks are
    performed."""
    n_workers = instance["nb_workers"]  # the number of workers
    n_tasks = instance["num_tasks"]  # the number of tasks to perform
    cost = instance["Cost"]  # cost[w]: the hiring cost of worker w
    qualified = instance["Qualified"]  # qualified[t]: the workers who can perform task t, numbered from 1

    # workers[w] is 1 when worker w is hired (workers[0] is worker 1 of the data)
    workers = VarArray(size=n_workers, dom={0, 1})

    # The total hiring cost. No choice of workers costs more than hiring all of them, so the
    # total is at most sum(cost).
    total_cost = Var(dom=range(sum(cost) + 1))

    satisfy(
        # Every task is performed: at least one hired worker is qualified for it. A worker
        # numbered w in qualified[t] is workers[w - 1].
        [Sum(workers[w - 1] for w in qualified[t]) >= 1 for t in range(n_tasks)],
        # The total cost is the sum of the hiring costs of the hired workers.
        total_cost == Sum(cost[w] * workers[w] for w in range(n_workers)),
    )

    # Minimise the total hiring cost.
    minimize(total_cost)

    return {"total_cost": total_cost, "workers": workers}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("total_cost =", value(outputs["total_cost"]))
        print("workers =", values(outputs["workers"]))
    else:
        print("No solution:", status())
