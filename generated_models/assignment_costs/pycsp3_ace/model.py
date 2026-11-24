# assignment_costs: a PyCSP3 model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python assignment_costs.py assignment_costs.json

from pycsp3 import *


def create_model(instance):
    """Assign people to 4 tasks with different costs, so that the total cost is minimized.
    Each task must be assigned to exactly one person, but it is not necessary to assign all
    people to a task."""
    cost = instance["cost"]          # cost[i][j]: the cost of task i done by person j
    n_tasks = len(cost)              # the number of tasks
    n_people = len(cost[0])          # the number of people

    # x[i][j] is 1 when task i is assigned to person j, and 0 otherwise.
    x = VarArray(size=[n_tasks, n_people], dom={0, 1})

    satisfy(
        # Each task must be assigned to exactly one person.
        [Sum(x[i]) == 1 for i in range(n_tasks)],
        # Each person takes at most one task. (Not stated outright in the description: the usual
        # reading of an assignment problem, and what the instances assume.)
        [Sum(x[:, j]) <= 1 for j in range(n_people)],
    )

    # Assign the tasks so that the total cost is as small as possible.
    minimize(Sum(cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people)))

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
