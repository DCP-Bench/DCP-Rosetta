# covering_opl: a Z3 (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python covering_opl.py covering_opl.json

import z3


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    nb_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]              # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]    # qualified[t]: the workers who can perform task t, numbered from 1

    solver = z3.Optimize()

    # hired[i] is true when worker i is hired
    hired = [z3.Bool(f"hired_{i}") for i in range(nb_workers)]
    # total_cost is the hiring cost of all hired workers
    total_cost = z3.Int("total_cost")
    solver.add(total_cost == z3.Sum([z3.If(h, c, 0) for c, h in zip(cost, hired)]))

    # Every task is performed by at least one hired worker who is qualified for it.
    solver.add([z3.Or([hired[worker - 1] for worker in task_workers]) for task_workers in qualified])

    # Hire at the lowest total cost.
    solver.minimize(total_cost)

    return solver, {"total_cost": total_cost, "workers": hired}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
