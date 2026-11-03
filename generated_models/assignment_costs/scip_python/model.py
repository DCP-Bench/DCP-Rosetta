# assignment_costs: a SCIP (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python assignment_costs.py assignment_costs.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Assign people to tasks so that the total cost is as small as possible.

    Every task must be given exactly one person. A person can take at most one
    task, and it is not necessary to use every person. Doing task i with person j
    costs cost[i][j]; minimise the total cost of the assignment.
    """
    cost = instance["cost"]        # cost[i][j]: what person j charges for task i
    n_tasks = len(cost)            # number of tasks, from the rows of cost
    n_people = len(cost[0])        # number of people, from the columns of cost

    model = Model("assignment_costs")

    # x[i, j] is 1 when task i is assigned to person j, and 0 when not
    x = model.addMatrixVar((n_tasks, n_people), vtype="B", name="x")

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        model.addCons(quicksum(x[i, j] for j in range(n_people)) == 1,
                      name=f"task_{i}_gets_one_person")

    # Each person takes at most one task (the description says not everyone has to be used).
    for j in range(n_people):
        model.addCons(quicksum(x[i, j] for i in range(n_tasks)) <= 1,
                      name=f"person_{j}_at_most_one_task")

    # The total cost of the assignment is as small as possible.
    model.setObjective(quicksum(cost[i][j] * x[i, j]
                                for i in range(n_tasks) for j in range(n_people)),
                       "minimize")

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
