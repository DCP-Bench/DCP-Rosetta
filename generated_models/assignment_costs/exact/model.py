# assignment_costs: an Exact (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python assignment_costs.py assignment_costs.json

from exact import Exact


def create_model(instance):
    """Assign each task to one person, where people differ in cost for each task,
    and each person does at most one task, so that the total cost is as low as possible."""
    cost = instance["cost"]  # cost[i][j] is the cost of person j doing task i
    n_tasks = len(cost)
    n_people = len(cost[0])

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i][j] is true when task i is assigned to person j
    x = [[f"x{i}_{j}" for j in range(n_people)] for i in range(n_tasks)]
    for row in x:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each task goes to exactly one person.
    for i in range(n_tasks):
        solver.addConstraint([(1, name) for name in x[i]], True, 1, True, 1)

    # Each person does at most one task.
    for j in range(n_people):
        solver.addConstraint([(1, x[i][j]) for i in range(n_tasks)], False, 0, True, 1)

    # The total cost of the assignment is as low as possible.
    terms = [(cost[i][j], x[i][j]) for i in range(n_tasks) for j in range(n_people)]
    solver.setObjective(terms, minimize=True)

    return solver, {"x": x}


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
