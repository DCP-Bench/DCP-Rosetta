# assignment_costs: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install ortools`):
#   python assignment_costs.py assignment_costs.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is minimized."""
    cost = instance["cost"]  # cost[i][j]: the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    model = cp_model.CpModel()

    # assigned[i][j] is true when task i is assigned to person j
    assigned = [
        [model.new_bool_var(f"x_{i}_{j}") for j in range(n_people)]
        for i in range(n_tasks)
    ]

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        model.add_exactly_one(assigned[i])
    # A person does at most one task.
    for j in range(n_people):
        model.add_at_most_one(assigned[i][j] for i in range(n_tasks))

    # Minimize the total cost of the assignment.
    model.minimize(
        sum(
            cost[i][j] * assigned[i][j]
            for i in range(n_tasks)
            for j in range(n_people)
        )
    )

    return model, {"x": assigned}


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
