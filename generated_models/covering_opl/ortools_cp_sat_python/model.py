# covering_opl: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install ortools`):
#   python covering_opl.py covering_opl.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    n_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]             # cost[i]: the hiring cost of worker i
    # qualified[t]: the workers who can perform task t
    qualified = [[worker - 1 for worker in task] for task in instance["Qualified"]]

    model = cp_model.CpModel()

    # workers[i] is true when worker i is hired
    workers = [model.new_bool_var(f"workers_{i}") for i in range(n_workers)]
    # total_cost is at most the cost of hiring everyone
    total_cost = model.new_int_var(0, sum(cost), "total_cost")

    # total_cost is the sum of the costs of the hired workers.
    model.add(total_cost == sum(cost[i] * workers[i] for i in range(n_workers)))
    # Every task is performed by at least one hired worker who is qualified for it.
    for task_workers in qualified:
        model.add(sum(workers[worker] for worker in task_workers) >= 1)

    # Hire at the lowest cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "workers": workers}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
