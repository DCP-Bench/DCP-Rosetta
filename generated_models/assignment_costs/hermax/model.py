# assignment_costs: a hermax (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install hermax`):
#   python assignment_costs.py assignment_costs.json

from hermax.model import Model


def create_model(instance):
    """Assign each of the tasks to exactly one of the people, with each person taking at
    most one task (not every person has to be given a task), so that the total cost of
    the assignment is as small as possible."""
    cost = instance["cost"]      # cost[i][j]: the cost of giving task i to person j
    n_tasks = len(cost)          # the number of tasks: rows of the cost matrix
    n_people = len(cost[0])      # the number of people: columns of the cost matrix

    m = Model()

    # x[i][j] is true when task i is assigned to person j
    x = m.bool_matrix("x", n_tasks, n_people)

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        m &= x.row(i).exactly_one()

    # Each person is assigned at most one task.
    for j in range(n_people):
        m &= x.col(j).at_most_one()

    # Minimise the total cost of all the assignments made.
    m.obj += sum(cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people))

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
