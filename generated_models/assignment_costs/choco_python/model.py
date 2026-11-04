# assignment_costs: a Choco-solver (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python assignment_costs.py assignment_costs.json

from pychoco.model import Model


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is
    minimized. Each task is assigned to exactly one person, but not every person
    needs a task."""
    cost = instance["cost"]  # cost[i][j]: the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    model = Model()

    # x[i][j] is true when task i is assigned to person j
    x = [[model.boolvar(name=f"x{i}_{j}") for j in range(n_people)] for i in range(n_tasks)]

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        model.sum(x[i], "=", 1).post()
    # A person is assigned at most one task.
    for j in range(n_people):
        model.sum([x[i][j] for i in range(n_tasks)], "<=", 1).post()

    # flat and prices pair each x[i][j] with the cost of person j doing task i.
    flat = [x[i][j] for i in range(n_tasks) for j in range(n_people)]
    prices = [cost[i][j] for i in range(n_tasks) for j in range(n_people)]
    # total_cost: the total cost of the assignment, which is minimized.
    total_cost = model.intvar(0, sum(prices), name="total_cost")
    model.scalar(flat, prices, "=", total_cost).post()

    return model, {"x": x}, {"objective": total_cost, "maximize": False}


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
