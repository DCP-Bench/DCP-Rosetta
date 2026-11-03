# covering_opl: an Exact (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python covering_opl.py covering_opl.json

from exact import Exact


def create_model(instance):
    """Hire a set of workers at the lowest total cost, so that every task is done by
    at least one hired worker who is qualified for it."""
    nb_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]              # cost[i] is the hiring cost of worker i
    # qualified[t] lists the workers who can do task t, numbered from 1
    qualified = instance["Qualified"]

    solver = Exact()

    # Exact identifies its variables by name.
    # workers[i] is 1 when worker i is hired, and 0 when not.
    workers = [f"workers_{i}" for i in range(nb_workers)]
    for name in workers:
        solver.addVariable(name, 0, 1)

    # total_cost is at most the cost of hiring every worker.
    solver.addVariable("total_cost", 0, sum(cost))
    # The hiring cost of each worker, with the workers who cost nothing left out.
    hiring = [(cost[i], workers[i]) for i in range(nb_workers) if cost[i]]

    # total_cost is the summed hiring cost of the hired workers.
    solver.addConstraint(hiring + [(-1, "total_cost")], True, 0, True, 0)

    # Each task needs one hired worker among those qualified for it.
    for task in qualified:
        # the workers who can do this task, numbered from 0
        able = sorted(set(q - 1 for q in task))
        solver.addConstraint([(1, workers[i]) for i in able], True, 1)

    # Minimise the total hiring cost.
    solver.setObjective(hiring, minimize=True)

    return solver, {"total_cost": "total_cost", "workers": workers}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
