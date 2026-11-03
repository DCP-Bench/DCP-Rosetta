# assignment_costs: a Python-MIP (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python assignment_costs.py assignment_costs.json

import mip


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is
    minimized. Each task goes to exactly one person, and each person takes at most
    one task."""
    cost = instance["cost"]  # cost[i][j] is the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][j] is 1 when task i is assigned to person j, and 0 when not
    x = [
        [model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n_people)]
        for i in range(n_tasks)
    ]

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        model += mip.xsum(x[i][j] for j in range(n_people)) == 1

    # Each person takes at most one task.
    for j in range(n_people):
        model += mip.xsum(x[i][j] for i in range(n_tasks)) <= 1

    # The total cost is the sum of the costs of the chosen pairs.
    model.objective = mip.xsum(
        cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people)
    )

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
