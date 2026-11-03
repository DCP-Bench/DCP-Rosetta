# assignment_costs: a PuLP (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python assignment_costs.py assignment_costs.json

import pulp


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is
    minimized. Each task is assigned to exactly one person, but not every person
    needs a task."""
    cost = instance["cost"]  # cost[i][j]: the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    problem = pulp.LpProblem("assignment_costs", pulp.LpMinimize)

    # x[i][j] is 1 when task i is assigned to person j, and 0 when not
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n_people)]
         for i in range(n_tasks)]

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        problem += pulp.lpSum(x[i]) == 1

    # A person does at most one task.
    for j in range(n_people):
        problem += pulp.lpSum(x[i][j] for i in range(n_tasks)) <= 1

    # Minimize the total cost of the assignment.
    problem += pulp.lpSum(cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people))

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
