# covering_opl: a Choco-solver (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python covering_opl.py covering_opl.json

from pychoco.model import Model


def create_model(instance):
    """Select a set of workers to perform all the tasks, while minimizing the cost. Each worker can perform certain tasks and has a hiring cost. Every task has to be performed."""
    n_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]             # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]   # qualified[t]: the workers who can perform task t

    model = Model()

    # workers[i] is true when worker i is hired
    workers = [model.boolvar(name=f"workers_{i}") for i in range(n_workers)]
    # The total hiring cost, at most the cost of hiring everyone.
    total_cost = model.intvar(0, sum(cost), name="total_cost")

    # The total hiring cost is the cost of the hired workers.
    model.scalar(workers, cost, "=", total_cost).post()

    # Every task is performed by at least one hired worker who is qualified for it.
    for task_workers in qualified:
        model.sum([workers[c - 1] for c in task_workers], ">=", 1).post()

    # Minimise the total hiring cost.
    return model, {"total_cost": total_cost, "workers": workers}, {"objective": total_cost, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
