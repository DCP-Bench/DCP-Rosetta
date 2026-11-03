# assignment_costs: a CPMpy model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python assignment_costs.py assignment_costs.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is
    minimized. Each task is assigned to exactly one person, but not every person
    needs a task."""
    cost = np.array(instance["cost"])  # cost[i][j]: the cost of person j doing task i
    num_tasks, num_people = cost.shape

    # x[i, j] is true when task i is assigned to person j
    x = cp.boolvar(shape=(num_tasks, num_people), name="x")

    model = cp.Model()
    # Each task is assigned to exactly one person.
    model.add(x.sum(axis=1) == 1)
    # A person does at most one task.
    model.add(x.sum(axis=0) <= 1)
    # Minimize the total cost of the assignment.
    model.minimize(cp.sum(x * cost))

    return model, {"x": x}


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
