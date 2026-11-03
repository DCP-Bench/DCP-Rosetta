# netasgn: a Choco-solver (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python netasgn.py netasgn.json

from pychoco.model import Model


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can contribute to project j
    n_people, n_projects = len(supply), len(demand)

    # The most hours any person can contribute to any project.
    max_hours = max(max(row) for row in limit)

    model = Model()

    # assign[i][j]: the hours person i works on project j
    assign = [[model.intvar(0, max_hours, name=f"assign_{i}_{j}") for j in range(n_projects)]
              for i in range(n_people)]

    # Each person works exactly their available hours.
    for i in range(n_people):
        model.sum(assign[i], "=", supply[i]).post()

    # Each project gets exactly the hours it requires.
    for j in range(n_projects):
        model.sum([assign[i][j] for i in range(n_people)], "=", demand[j]).post()

    # No person works more hours on a project than their limit.
    for i in range(n_people):
        for j in range(n_projects):
            model.arithm(assign[i][j], "<=", limit[i][j]).post()

    # flat_assign and flat_cost list every pair of person and project in the same order.
    flat_assign = [assign[i][j] for i in range(n_people) for j in range(n_projects)]
    flat_cost = [cost[i][j] for i in range(n_people) for j in range(n_projects)]

    # total_cost: the cost of all hours worked.
    total_cost = model.intvar(0, max_hours * sum(flat_cost), name="total_cost")
    model.scalar(flat_assign, flat_cost, "=", total_cost).post()

    # Minimise the total cost.
    return model, {"assign": assign, "total_cost": total_cost}, {"objective": total_cost, "maximize": False}


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
