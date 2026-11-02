# assignment_costs: a Z3 (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python assignment_costs.py assignment_costs.json

import z3


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is
    minimized. Each task is assigned to exactly one person, but not every person
    needs a task."""
    cost = instance["cost"]  # cost[i][j]: the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    # assigned[i][j] is true when task i is assigned to person j
    assigned = [[z3.Bool(f"x_{i}_{j}") for j in range(n_people)] for i in range(n_tasks)]
    # picked[i][j] is 1 when task i is assigned to person j, else 0
    picked = [[z3.If(assigned[i][j], 1, 0) for j in range(n_people)] for i in range(n_tasks)]

    solver = z3.Optimize()
    # Each task is assigned to exactly one person.
    solver.add([z3.Sum(picked[i]) == 1 for i in range(n_tasks)])
    # A person does at most one task.
    solver.add([z3.Sum([picked[i][j] for i in range(n_tasks)]) <= 1 for j in range(n_people)])

    # The total cost of the assignment, to be minimized.
    total_cost = z3.Sum([cost[i][j] * picked[i][j] for i in range(n_tasks) for j in range(n_people)])
    solver.minimize(total_cost)

    return solver, {"x": assigned}


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
